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
RUNTIME_FILES = ("graph.npz", "node_metadata.npz", "groups.npz", "manifest.json")
# Kaggle rejects single files above this size on the standard dataset path.
MAX_FILE_BYTES = 20 * 1024 * 1024 * 1024


def _stage(config_path: Path, runtime_dir: Path, stage: Path, slug: str) -> dict[str, Any]:
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

    # The staged bundle must load and hash-check on its own, exactly as the
    # notebook will load it with no network and no source tables present.
    verified = load_runtime_connectome(stage / "runtime", required_groups=("descending_neurons",))
    provenance = {
        "format": "flygi-kaggle-dataset-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "contains_connectome_assets": True,
        "slug": slug,
        "source_runtime_dir": str(runtime_dir.relative_to(ROOT)),
        "config_path": str(config_path.relative_to(ROOT)),
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

    provenance = _stage(args.config, runtime_dir, args.stage.resolve(), slug)
    print(json.dumps({"stage": str(args.stage.resolve()), **provenance}, indent=2, sort_keys=True))
    print(
        "\nStaged only. To publish privately, review the contents and then run:\n"
        f"  KAGGLE_API_TOKEN=$(cat .kaggle/access_token) uv run kaggle datasets create "
        f"-p {args.stage} --dir-mode zip\n"
        "Subsequent updates use `kaggle datasets version -p ... -m '<message>'`.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
