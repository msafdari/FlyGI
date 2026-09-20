"""Hashing and provenance manifests for source and runtime graph assets."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import tempfile
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

MANIFEST_FORMAT = "flygi.connectome-manifest/v1"


class HashMismatchError(RuntimeError):
    """Raised when a file does not match its recorded SHA-256."""


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256_file(path: str | Path, *, chunk_size: int = 8 * 1024 * 1024) -> str:
    """Compute a lowercase SHA-256 digest without loading the file at once."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(
    path: str | Path,
    *,
    name: str | None = None,
    url: str | None = None,
    expected_sha256: str | None = None,
    downloaded_at: str | None = None,
) -> dict[str, Any]:
    """Create a complete source/output file provenance record."""

    source = Path(path)
    observed = sha256_file(source)
    normalized_expected = expected_sha256.lower() if expected_sha256 is not None else None
    if normalized_expected is not None and observed != normalized_expected:
        raise HashMismatchError(
            f"SHA-256 mismatch for {source}: expected {normalized_expected}, observed {observed}"
        )
    return {
        "name": name or source.name,
        "path": str(source),
        "url": url,
        "bytes": int(source.stat().st_size),
        "sha256": observed,
        "expected_sha256": normalized_expected,
        "hash_verified": normalized_expected is not None,
        "downloaded_at": downloaded_at,
    }


def software_versions(
    packages: Iterable[str] = ("flygi", "numpy", "scipy", "pandas", "pyarrow"),
) -> dict[str, Any]:
    versions: dict[str, str | None] = {}
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "packages": versions,
    }


def create_connectome_manifest(
    *,
    release: str,
    sources: Iterable[Mapping[str, Any]],
    dataframe_schemas: Mapping[str, Any],
    counts: Mapping[str, int],
    preprocessing: Mapping[str, Any],
    outputs: Iterable[Mapping[str, Any]],
    created_at: str | None = None,
) -> dict[str, Any]:
    """Create the versioned Milestone-1 provenance document."""

    required_counts = {
        "annotated_neurons",
        "retained_neurons",
        "aggregated_directed_edges",
        "synaptic_contact_weight_sum",
        "self_edges",
        "disconnected_nodes",
        "unknown_transmitters",
        "missing_annotations",
    }
    missing = sorted(required_counts - set(counts))
    if missing:
        raise ValueError(f"manifest is missing required counts: {missing}")
    return {
        "format": MANIFEST_FORMAT,
        "created_at": created_at or utc_timestamp(),
        "release": release,
        "matrix_convention": "W[post_index, pre_index]",
        "propagation": "W @ activity",
        "sources": [dict(record) for record in sources],
        "dataframe_schemas": dict(dataframe_schemas),
        "counts": {key: int(value) for key, value in counts.items()},
        "preprocessing": dict(preprocessing),
        "software": software_versions(),
        "outputs": [dict(record) for record in outputs],
    }


def write_manifest(path: str | Path, manifest: Mapping[str, Any]) -> Path:
    """Atomically write a deterministic, human-readable JSON manifest."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(
                manifest,
                stream,
                indent=2,
                sort_keys=True,
                default=_json_default,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, destination)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise
    return destination


def load_manifest(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as stream:
        manifest = json.load(stream)
    if manifest.get("format") != MANIFEST_FORMAT:
        raise ValueError(f"Unsupported manifest format: {manifest.get('format')!r}")
    return manifest


def verify_manifest_hashes(
    manifest: Mapping[str, Any] | str | Path,
    *,
    root: str | Path | None = None,
    include_sources: bool = True,
) -> dict[str, str]:
    """Re-hash every recorded asset and fail closed on the first mismatch."""

    document = load_manifest(manifest) if isinstance(manifest, (str, Path)) else manifest
    base = Path(root) if root is not None else None
    verified: dict[str, str] = {}
    sections = ["outputs"]
    if include_sources:
        sections.insert(0, "sources")
    for section in sections:
        for record in document.get(section, []):
            if record.get("path") is None or record.get("sha256") is None:
                continue
            recorded_path = Path(record["path"])
            path = (
                base / recorded_path
                if base is not None and not recorded_path.is_absolute()
                else recorded_path
            )
            expected = str(record["sha256"]).lower()
            observed = sha256_file(path)
            if observed != expected:
                raise HashMismatchError(
                    f"SHA-256 mismatch for {path}: expected {expected}, observed {observed}"
                )
            verified[str(path)] = observed
    return verified


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
