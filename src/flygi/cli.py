"""Command-line interface for FlyGI data, graph, and validation workflows."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import sparse

from . import __version__
from .config import ConfigError, FlyGIConfig, load_config
from .connectome.build import (
    BuildOptions,
    NodeIndex,
    build_connectome,
    build_sparse_counts,
    load_runtime_graph,
)
from .connectome.download import SourceFile, fetch_source, write_download_manifest
from .connectome.groups import load_groups
from .connectome.manifest import (
    HashMismatchError,
    create_connectome_manifest,
    file_record,
    load_manifest,
    sha256_file,
    verify_manifest_hashes,
    write_manifest,
)
from .connectome.normalize import normalize_matrix
from .connectome.nulls import (
    NullOptions,
    degree_preserving_rewire,
    null_invariants,
)
from .connectome.schema import (
    ANNOTATIONS_CONTRACT,
    NEUROTRANSMITTERS_CONTRACT,
    WEIGHTS_CONTRACT,
    SchemaMismatchError,
    inspect_table_schema,
    validate_observed_schema,
)
from .dynamics.rate import RateParameters, ScipyRateNetwork

DEFAULT_CONFIG = Path("configs/literal_rate.yaml")
_SOURCE_PATH_ATTRIBUTES = {
    "weights": "weights_path",
    "annotations": "annotations_path",
    "neurotransmitters": "neurotransmitters_path",
}


class CLIError(RuntimeError):
    """A user-facing command failure without an internal traceback."""


def _add_config(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flygi",
        description="Build and validate reproducible MaleCNS runtime assets for ARC-AGI-3.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    data = commands.add_parser("data", help="acquire MaleCNS source tables")
    data_commands = data.add_subparsers(dest="data_command", required=True)
    fetch = data_commands.add_parser("fetch", help="download and hash official source tables")
    _add_config(fetch)
    fetch.add_argument("--release", default=None)
    fetch.add_argument("--overwrite", action="store_true")
    fetch.add_argument("--timeout", type=float, default=60.0)

    graph = commands.add_parser("graph", help="compile or inspect sparse graph assets")
    graph_commands = graph.add_subparsers(dest="graph_command", required=True)
    build = graph_commands.add_parser("build", help="compile a sparse runtime asset")
    _add_config(build)
    nulls = graph_commands.add_parser(
        "nulls", help="build seeded directed degree-preserving control graphs"
    )
    _add_config(nulls)
    nulls.add_argument("--k", type=int, default=10, help="number of independently seeded nulls")
    nulls.add_argument("--seed", type=int, default=20260919)
    nulls.add_argument(
        "--swaps-per-edge",
        type=float,
        default=10.0,
        help="double-edge swaps attempted per edge; higher mixes more thoroughly",
    )
    nulls.add_argument(
        "--batch-pairs", type=int, default=2_000_000, help="edge pairs proposed per batch"
    )

    validate = commands.add_parser("validate", help="validate configuration and assets")
    validate_commands = validate.add_subparsers(dest="validate_command", required=True)
    validate_all = validate_commands.add_parser("all", help="run all available checks")
    _add_config(validate_all)
    validate_all.add_argument(
        "--require-data",
        action="store_true",
        help="fail if the three large source tables have not been downloaded",
    )

    commands.add_parser("smoke-test", help="run fast offline configuration checks")
    return parser


def _configured_sources(config: FlyGIConfig) -> list[tuple[str, Path, SourceFile]]:
    configured: list[tuple[str, Path, SourceFile]] = []
    for logical_name, path_attribute in _SOURCE_PATH_ATTRIBUTES.items():
        path = Path(getattr(config.data, path_attribute))
        source_config = config.data.sources.get(logical_name)
        if source_config is None:
            raise CLIError(
                f"configuration is missing the canonical source declaration for {logical_name}"
            )
        configured.append(
            (
                logical_name,
                path,
                SourceFile(path.name, source_config.url, source_config.sha256),
            )
        )
    return configured


def _fetch(config: FlyGIConfig, args: argparse.Namespace) -> int:
    release = args.release or config.data.release
    if release != config.data.release:
        raise CLIError(
            f"requested release {release!r} does not match config release {config.data.release!r}"
        )
    if release != "male-cns:v1.0":
        raise CLIError(f"unsupported release {release!r}; only male-cns:v1.0 is declared")

    records = []
    for _, target, source in _configured_sources(config):
        record = fetch_source(
            source,
            target.parent,
            overwrite=bool(args.overwrite),
            timeout=float(args.timeout),
        )
        if Path(record.path) != target:
            raise CLIError(f"download destination mismatch: expected {target}, got {record.path}")
        records.append(record)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    manifest_path = config.data.manifest_dir / f"download-{stamp}.json"
    write_download_manifest(manifest_path, records)
    summary = {
        "release": release,
        "manifest": str(manifest_path),
        "files": [record.to_manifest_record() for record in records],
        "all_hashes_preverified": all(record.hash_verified for record in records),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["all_hashes_preverified"]:
        print(
            "warning: one or more config digests are null; observed SHA-256 values were "
            "recorded but were not independently preverified",
            file=sys.stderr,
        )
    return 0


def _download_timestamps(config: FlyGIConfig) -> dict[str, str]:
    """Read the newest matching download manifest, if one is present."""

    manifests = sorted(config.data.manifest_dir.glob("download-*.json"), reverse=True)
    names_to_logical = {
        Path(getattr(config.data, attribute)).name: logical
        for logical, attribute in _SOURCE_PATH_ATTRIBUTES.items()
    }
    for path in manifests:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if document.get("format") != "flygi.download-manifest/v1":
            continue
        timestamps: dict[str, str] = {}
        for record in document.get("files", []):
            logical = names_to_logical.get(str(record.get("name")))
            downloaded_at = record.get("downloaded_at")
            if logical is not None and isinstance(downloaded_at, str):
                timestamps[logical] = downloaded_at
        if len(timestamps) == len(_SOURCE_PATH_ATTRIBUTES):
            return timestamps
    return {}


def _build_graph(config: FlyGIConfig) -> int:
    inputs = [path for _, path, _ in _configured_sources(config)]
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise CLIError(
            "required MaleCNS source files are missing; run `flygi data fetch` first: "
            + ", ".join(missing)
        )
    if config.data.output_dir != config.graph.output_dir:
        raise CLIError(
            "data.output_dir and graph.output_dir must identify the same immutable asset"
        )

    spectral_radius = 0.9 if config.graph.spectral_radius is None else config.graph.spectral_radius
    options = BuildOptions(
        weight_transform=config.graph.weight_transform,  # type: ignore[arg-type]
        sign_mode=config.graph.sign_mode,  # type: ignore[arg-type]
        normalization=config.graph.normalization,  # type: ignore[arg-type]
        epsilon=config.graph.epsilon,
        spectral_radius=spectral_radius,
        allow_self_edges=config.graph.allow_self_edges,
        node_filter_column=config.graph.node_filter_column,
        node_filter_values=config.graph.node_filter_values,
        modulator_treatment=config.graph.modulator_treatment,  # type: ignore[arg-type]
        unknown_transmitter_treatment=(
            config.graph.unknown_transmitter_treatment  # type: ignore[arg-type]
        ),
        overwrite=False,
    )
    urls = {name: source.url for name, _, source in _configured_sources(config)}
    expected_hashes = {name: source.sha256 for name, _, source in _configured_sources(config)}
    manifest = build_connectome(
        config.data.weights_path,
        config.data.annotations_path,
        config.data.neurotransmitters_path,
        config.graph.output_dir,
        release=config.data.release,
        options=options,
        source_urls=urls,
        group_definitions=config.groups,
        source_download_timestamps=_download_timestamps(config),
        source_expected_hashes=expected_hashes,
    )
    print(
        json.dumps(
            {
                "output_dir": str(config.graph.output_dir),
                "manifest": str(config.graph.output_dir / "manifest.json"),
                "counts": manifest["counts"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _null_output_root(config: FlyGIConfig) -> Path:
    return config.graph.output_dir / "nulls" / "degree_preserving"


def _write_null_runtime(
    destination: Path,
    matrix: sparse.csr_matrix,
    source_dir: Path,
    *,
    config: FlyGIConfig,
    release: str,
    source_manifest: dict[str, Any],
    statistics: dict[str, Any],
    invariants: dict[str, Any],
) -> dict[str, Any]:
    """Serialize one null as a self-contained, hash-verified runtime bundle."""

    if destination.exists():
        raise FileExistsError(f"null runtime {destination} already exists; results are immutable")
    destination.mkdir(parents=True)

    with np.load(source_dir / "graph.npz", allow_pickle=False) as archive:
        node_ids = np.asarray(archive["node_ids"])
    arrays = {
        "format_version": np.asarray([1], dtype=np.int16),
        "indptr": matrix.indptr.astype(np.int64, copy=False),
        "indices": matrix.indices.astype(np.int32, copy=False),
        "weights": matrix.data.astype(np.float32, copy=False),
        "node_ids": node_ids,
        "body_to_index_ids": node_ids,
        "body_to_index_values": np.arange(len(node_ids), dtype=np.int32),
    }
    np.savez_compressed(destination / "graph.npz", **arrays)

    # The node set and declared groups are shared with the real graph by
    # construction; copying keeps each null independently loadable and hashed.
    for name in ("node_metadata.npz", "groups.npz"):
        shutil.copyfile(source_dir / name, destination / name)

    counts = dict(source_manifest["counts"])
    counts["runtime_nonzero_edges"] = int(matrix.nnz)
    counts["aggregated_directed_edges"] = int(matrix.nnz)
    counts["self_edges"] = int(invariants["self_edges"])
    preprocessing = dict(source_manifest["preprocessing"])
    preprocessing["null"] = {
        **statistics,
        "source_runtime": str(source_dir),
        "source_graph_sha256": sha256_file(source_dir / "graph.npz"),
        "normalization_reapplied": config.graph.normalization,
        "invariants": invariants,
    }
    manifest = create_connectome_manifest(
        release=release,
        sources=source_manifest.get("sources", []),
        dataframe_schemas=source_manifest.get("dataframe_schemas", {}),
        counts=counts,
        preprocessing=preprocessing,
        # ``path`` must be the bare filename, matching the real build, because
        # runtime loading resolves output hashes relative to the bundle root.
        outputs=[
            {**file_record(destination / name, name=name), "path": name}
            for name in ("graph.npz", "node_metadata.npz", "groups.npz")
        ],
    )
    write_manifest(destination / "manifest.json", manifest)
    return manifest


def _build_nulls(config: FlyGIConfig, args: argparse.Namespace) -> int:
    """Generate k independently seeded directed degree-preserving controls."""

    if args.k <= 0:
        raise CLIError("--k must be positive")
    source_dir = config.graph.output_dir
    if not (source_dir / "graph.npz").is_file():
        raise CLIError(f"no compiled runtime at {source_dir}; run `flygi graph build` first")
    source_manifest = load_manifest(source_dir / "manifest.json")
    matrix, _ = load_runtime_graph(source_dir / "graph.npz")
    groups = load_groups(source_dir / "groups.npz")

    options = NullOptions(
        kind="degree_preserving",
        swaps_per_edge=float(args.swaps_per_edge),
        allow_self_edges=bool(config.graph.allow_self_edges),
        batch_pairs=int(args.batch_pairs),
    )
    root = _null_output_root(config)
    written: list[dict[str, Any]] = []
    for offset in range(int(args.k)):
        seed = int(args.seed) + offset
        started = time.perf_counter()
        rewired, statistics = degree_preserving_rewire(matrix, seed=seed, options=options)
        invariants = null_invariants(
            matrix,
            rewired,
            expect_identical_weight_multiset=True,
            preserved_groups=groups,
        )
        if not invariants["valid"]:
            raise CLIError(f"null seed {seed} violated its invariants: {invariants['failures']}")
        # The real condition's normalization must be re-applied, because moving
        # edges between postsynaptic rows changes those rows' incoming sums.
        normalized = normalize_matrix(
            rewired,
            config.graph.normalization,  # type: ignore[arg-type]
            epsilon=config.graph.epsilon,
            spectral_radius=(
                0.9 if config.graph.spectral_radius is None else config.graph.spectral_radius
            ),
        )
        normalized.sort_indices()
        statistics["normalization_applied"] = True
        statistics["seconds"] = time.perf_counter() - started
        manifest = _write_null_runtime(
            root / f"seed-{seed}",
            normalized,
            source_dir,
            config=config,
            release=config.data.release,
            source_manifest=source_manifest,
            statistics=statistics,
            invariants=invariants,
        )
        written.append(
            {
                "seed": seed,
                "output_dir": str(root / f"seed-{seed}"),
                "edges": int(normalized.nnz),
                "accepted_swaps": statistics["accepted_swaps"],
                "acceptance_rate": statistics["acceptance_rate"],
                "fraction_shared_with_real_graph": invariants["fraction_shared_with_real_graph"],
                "seconds": statistics["seconds"],
                "graph_sha256": next(
                    record["sha256"]
                    for record in manifest["outputs"]
                    if record["name"] == "graph.npz"
                ),
            }
        )
        print(json.dumps(written[-1], indent=2, sort_keys=True), flush=True)

    print(
        json.dumps(
            {"source_runtime": str(source_dir), "nulls": written},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _validate_source_schemas(config: FlyGIConfig) -> dict[str, Any]:
    contracts = {
        "weights": WEIGHTS_CONTRACT,
        "annotations": ANNOTATIONS_CONTRACT,
        "neurotransmitters": NEUROTRANSMITTERS_CONTRACT,
    }
    result: dict[str, Any] = {}
    for logical_name, path, _ in _configured_sources(config):
        observed = inspect_table_schema(path)
        validate_observed_schema(
            observed["columns"], observed["dtypes"], contracts[logical_name], strict=True
        )
        result[logical_name] = observed
    return result


def _validate_edge_convention() -> None:
    edges = pd.DataFrame(
        {
            "body_pre": pd.Series([11, 22], dtype="int64"),
            "body_post": pd.Series([22, 33], dtype="int64"),
            "weight": pd.Series([2, 3], dtype="int64"),
        }
    )
    matrix = build_sparse_counts(edges, NodeIndex.from_body_ids([11, 22, 33]))
    if not np.array_equal(matrix @ np.asarray([1, 0, 0]), np.asarray([0, 2, 0])):
        raise CLIError("three-neuron direction self-check failed")


def _validate_all(config: FlyGIConfig, *, require_data: bool) -> int:
    _validate_edge_convention()
    configured = _configured_sources(config)
    present = [path.is_file() for _, path, _ in configured]
    if any(present) and not all(present):
        missing = [
            str(path)
            for (_, path, _), exists in zip(configured, present, strict=True)
            if not exists
        ]
        raise CLIError("source download is incomplete; missing: " + ", ".join(missing))
    if require_data and not all(present):
        raise CLIError("source data are absent; run `flygi data fetch` first")

    source_status: Any = "absent (large downloads are optional for offline validation)"
    if all(present):
        source_status = _validate_source_schemas(config)

    manifest_path = config.graph.output_dir / "manifest.json"
    runtime_status: Any = "absent (run `flygi graph build` after fetching data)"
    if manifest_path.is_file():
        manifest = load_manifest(manifest_path)
        verified = verify_manifest_hashes(
            manifest,
            root=config.graph.output_dir,
            include_sources=all(present),
        )
        matrix, node_index = load_runtime_graph(config.graph.output_dir / "graph.npz")
        counts = manifest["counts"]
        if matrix.shape != (counts["retained_neurons"], counts["retained_neurons"]):
            raise CLIError("runtime graph shape disagrees with manifest retained_neurons")
        if matrix.nnz != counts.get("runtime_nonzero_edges", counts["aggregated_directed_edges"]):
            raise CLIError("runtime graph nnz disagrees with manifest edge count")
        groups = load_groups(config.graph.output_dir / "groups.npz")
        for group_name, indices in groups.items():
            if len(indices) and int(indices[-1]) >= len(node_index):
                raise CLIError(f"group {group_name!r} contains an out-of-range node index")
        with np.load(config.graph.output_dir / "node_metadata.npz", allow_pickle=False) as metadata:
            metadata_ids = np.asarray(metadata["body_ids"], dtype=np.uint64)
        if not np.array_equal(metadata_ids, node_index.body_ids):
            raise CLIError("node metadata body IDs disagree with the runtime graph")
        parameters = RateParameters(
            internal_steps=config.dynamics.internal_steps,
            leak=config.dynamics.leak,
            recurrent_gain=config.dynamics.recurrent_gain,
            bias=config.dynamics.bias,
        )
        dynamics = ScipyRateNetwork(matrix, parameters, copy_connectivity=False)
        diagnostic_state = dynamics.initial_state(seed=config.seed, scale=0.01)
        first = dynamics.step(diagnostic_state)
        repeated = dynamics.step(diagnostic_state)
        if not np.array_equal(first, repeated):
            raise CLIError("CPU rate update was not deterministic for an identical state")
        runtime_status = {
            "manifest": str(manifest_path),
            "verified_files": len(verified),
            "source_hashes_reverified": all(present),
            "groups": {name: len(indices) for name, indices in groups.items()},
            "counts": counts,
            "dynamics": {
                "backend": dynamics.backend_name,
                "configured_internal_steps": parameters.internal_steps,
                "one_step_shape": list(first.shape),
                "state_dtype": str(first.dtype),
                "same_backend_exact_repeat": True,
                "finite": bool(np.isfinite(first).all()),
            },
        }
    elif config.graph.output_dir.exists() and any(config.graph.output_dir.iterdir()):
        raise CLIError(f"runtime asset is incomplete: {config.graph.output_dir}")

    print(
        json.dumps(
            {
                "config": "valid",
                "edge_convention": "W[post_index, pre_index]",
                "sources": source_status,
                "runtime": runtime_status,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "smoke-test":
            return _validate_all(load_config(DEFAULT_CONFIG), require_data=False)
        config = load_config(args.config)
        if args.command == "data" and args.data_command == "fetch":
            return _fetch(config, args)
        if args.command == "graph" and args.graph_command == "build":
            return _build_graph(config)
        if args.command == "graph" and args.graph_command == "nulls":
            return _build_nulls(config, args)
        if args.command == "validate" and args.validate_command == "all":
            return _validate_all(config, require_data=bool(args.require_data))
        parser.error("unhandled command")
    except (
        CLIError,
        ConfigError,
        FileNotFoundError,
        FileExistsError,
        HashMismatchError,
        SchemaMismatchError,
        ValueError,
    ) as exc:
        print(f"flygi: error: {exc}", file=sys.stderr)
        return 2
    return 2


def entrypoint() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    entrypoint()
