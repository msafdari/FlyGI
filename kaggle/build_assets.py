"""Build the small, offline FlyGI Python bundle used by Kaggle.

Milestone 0 packages only repository-owned Python source.  Later milestones
will place compiled connectome arrays and their provenance manifest beside
this zip; this script intentionally never downloads or preprocesses data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
DEFAULT_OUTPUT = REPOSITORY_ROOT / "kaggle" / "dist" / "flygi_runtime.zip"
FIXED_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)

UPSTREAM_REVISIONS = {
    "arc_agi_3_kaggle_starter": {
        "commit": "eeb1535404f321d280a8f9194bbc1d7aca5f05fc",
        "url": "https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter",
    },
    "arc_agi_3_agents": {
        "commit": "4743e7d0aaae0ded0d98a89a7e282e63564cd58b",
        "url": "https://github.com/arcprize/ARC-AGI-3-Agents",
    },
    "arcengine": {
        "commit": "b495c6acaf253c9681cd7b75c4299d352e9ce6f8",
        "url": "https://github.com/arcprize/ARCEngine",
    },
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_member(archive: ZipFile, name: str, data: bytes) -> None:
    info = ZipInfo(name, date_time=FIXED_ZIP_TIMESTAMP)
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def build_runtime_bundle(output: Path, *, force: bool = False) -> dict[str, Any]:
    """Write a deterministic source zip and return its embedded manifest."""

    package_root = SOURCE_ROOT / "flygi"
    if not (package_root / "__init__.py").is_file():
        raise FileNotFoundError(
            f"expected an importable FlyGI package at {package_root}; "
            "run this command from a complete repository checkout"
        )
    if output.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing bundle: {output}")

    source_files = sorted(package_root.rglob("*.py"))
    file_entries: list[dict[str, str]] = []
    members: list[tuple[str, bytes]] = []
    for source_file in source_files:
        data = source_file.read_bytes()
        member_name = source_file.relative_to(SOURCE_ROOT).as_posix()
        members.append((member_name, data))
        file_entries.append({"path": member_name, "sha256": _sha256(data)})

    manifest: dict[str, Any] = {
        "format": "flygi-kaggle-runtime-v1",
        "contains_connectome_assets": False,
        "files": file_entries,
        "upstream_revisions": UPSTREAM_REVISIONS,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()

    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, mode="w") as archive:
        for member_name, data in members:
            _write_member(archive, member_name, data)
        _write_member(archive, "flygi_kaggle_manifest.json", manifest_bytes)
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="replace an existing output bundle")
    return parser


def main() -> None:
    args = _parser().parse_args()
    manifest = build_runtime_bundle(args.output.resolve(), force=args.force)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "python_files": len(manifest["files"]),
                "contains_connectome_assets": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
