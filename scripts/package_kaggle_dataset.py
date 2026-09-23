#!/usr/bin/env python3
"""Assemble the offline Kaggle Dataset that carries the compiled connectome.

The competition notebook runs with internet disabled, so every array, config
and manifest the agent needs must be attached in advance. This script stages
them into one directory with a Kaggle dataset-metadata.json and an independent
digest record, and verifies that the staged copy loads and hash-checks exactly
as the local runtime does.

It uploads nothing. Uploading is a separate, explicit action.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

DEFAULT_CONFIG = ROOT / "configs/literal_rate_signed.yaml"
DEFAULT_STAGE = ROOT / "kaggle" / "dist" / "dataset"
# retinotopy.npz is required by the retinotopic_colour encoder and the
# retinotopic saliency decoders; a bundle without it fails closed at assembly
# rather than silently degrading, but it must ship for those configs to run.
RUNTIME_FILES = (
    "graph.npz",
    "node_metadata.npz",
    "groups.npz",
    "manifest.json",
    "retinotopy.npz",
)
# Kaggle rejects single files above this size on the standard dataset path.
MAX_FILE_BYTES = 20 * 1024 * 1024 * 1024


def _relative(path: Path) -> str:
    """Record a repository-relative path when possible, absolute otherwise."""

    resolved = Path(path).resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def _stage(
    config_path: Path,
    runtime_dir: Path,
    stage: Path,
    slug: str,
    controller_path: Path | None = None,
) -> dict[str, Any]:
    from flygi.connectome.manifest import sha256_file
    from flygi.dynamics.runtime import load_runtime_connectome

    for name in RUNTIME_FILES:
        if not (runtime_dir / name).is_file():
            raise SystemExit(f"missing runtime file {runtime_dir / name}")

    if stage.exists():
        shutil.rmtree(stage)
    (stage / "runtime").mkdir(parents=True)

    records: list[dict[str, Any]] = []
    total = 0
    for name in RUNTIME_FILES:
        source = runtime_dir / name
        destination = stage / "runtime" / name
        shutil.copyfile(source, destination)
        size = destination.stat().st_size
        digest = sha256_file(destination)
        if digest != sha256_file(source):
            raise SystemExit(f"staged copy of {name} does not match its source")
        if size > MAX_FILE_BYTES:
            raise SystemExit(f"{name} is {size} bytes, above the Kaggle per-file limit")
        total += size
        records.append({"path": f"runtime/{name}", "bytes": size, "sha256": digest})

    shutil.copyfile(config_path, stage / "config.yaml")
    records.append(
        {
            "path": "config.yaml",
            "bytes": (stage / "config.yaml").stat().st_size,
            "sha256": sha256_file(stage / "config.yaml"),
        }
    )

    # A controller declaration is optional. Without it the adapter builds the
    # pure connectome policy exactly as before; with it the connectome moves
    # into the controller's tie position. There is no controller-only package:
    # the submission gate requires the fly to stay load-bearing.
    if controller_path is not None:
        shutil.copyfile(controller_path, stage / "controller.yaml")
        records.append(
            {
                "path": "controller.yaml",
                "bytes": (stage / "controller.yaml").stat().st_size,
                "sha256": sha256_file(stage / "controller.yaml"),
            }
        )

    # The staged bundle must load and hash-check on its own, exactly as the
    # notebook will load it with no network and no source tables present.
    verified = load_runtime_connectome(stage / "runtime", required_groups=("descending_neurons",))
    provenance = {
        "format": "flygi-kaggle-dataset-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "contains_connectome_assets": True,
        "slug": slug,
        "source_runtime_dir": _relative(runtime_dir),
        "config_path": _relative(config_path),
        "controller_path": None if controller_path is None else _relative(controller_path),
        "agent_mode": "controller-fly" if controller_path is not None else "connectome",
        "release": verified.manifest.get("release"),
        "nodes": verified.node_count,
        "edges": verified.edge_count,
        "descending_neurons": len(verified.groups["descending_neurons"]),
        "preprocessing": dict(verified.manifest.get("preprocessing", {})),
        "files": records,
        "total_bytes": total,
        "attribution": (
            "MaleCNS v1.0 (FlyEM/HHMI Janelia, University of Cambridge Department of "
            "Zoology, MRC Laboratory of Molecular Biology, Google Research), CC BY 4.0. "
            "These are modified derivative arrays, not an official release."
        ),
    }
    (stage / "flygi_dataset_manifest.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (stage / "dataset-metadata.json").write_text(
        json.dumps(
            {
                "title": "FlyGI MaleCNS runtime",
                "id": slug,
                "licenses": [{"name": "CC-BY-4.0"}],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return provenance


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--runtime-dir", type=Path, default=None)
    parser.add_argument(
        "--controller-config",
        type=Path,
        default=None,
        help=(
            "stage this controller declaration beside the graph; the packaged agent "
            "then runs the connectome in the controller's tie position"
        ),
    )
    parser.add_argument("--stage", type=Path, default=DEFAULT_STAGE)
    parser.add_argument("--slug", default=None, help="owner/dataset-name")
    args = parser.parse_args(argv)

    from flygi.config import load_config

    config = load_config(args.config)
    runtime_dir = (
        args.runtime_dir.resolve()
        if args.runtime_dir is not None
        else Path(config.graph.output_dir)
    )
    slug = args.slug
    if slug is None:
        metadata = ROOT / "notebooks" / "kernel-metadata.json"
        owner = json.loads(metadata.read_text())["id"].split("/")[0]
        slug = f"{owner}/flygi-malecns-runtime"

    controller_path = None
    if args.controller_config is not None:
        controller_path = args.controller_config.resolve()
        controller = load_config(controller_path)
        if not controller.controller.enabled:
            raise SystemExit(
                f"{controller_path} has controller.enabled=false; refusing to stage it"
            )

    provenance = _stage(
        args.config, runtime_dir, args.stage.resolve(), slug, controller_path=controller_path
    )
    print(json.dumps({"stage": str(args.stage.resolve()), **provenance}, indent=2, sort_keys=True))
    print(
        "\nStaged only. To publish privately, review the contents and then run:\n"
        f"  KAGGLE_API_TOKEN=$(cat .kaggle/access_token) uv run kaggle datasets create "
        f"-p {args.stage} --dir-mode zip\n"
        "Subsequent updates use `kaggle datasets version -p ... -m '<message>'`.",
    )
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("package_kaggle_dataset", main))
