"""Reproducible, atomic downloads for the three required MaleCNS tables."""

from __future__ import annotations

import re
import urllib.request
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from .manifest import HashMismatchError, sha256_file, utc_timestamp, write_manifest

OFFICIAL_BASE_URL = (
    "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome"
)
OFFICIAL_FILENAMES = {
    "weights": "connectome-weights-male-cns-v1.0-minconf-0.5.feather",
    "annotations": "body-annotations-male-cns-v1.0-minconf-0.5.feather",
    "neurotransmitters": "body-neurotransmitters-male-cns-v1.0.feather",
}

_SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


@dataclass(frozen=True)
class SourceFile:
    """One source URL and an optional externally recorded digest.

    The official download page does not currently publish SHA-256 values.  A
    missing expected digest is therefore recorded as unverified, while the
    observed digest is always calculated and written for subsequent rebuilds.
    """

    name: str
    url: str
    sha256: str | None = None

    def __post_init__(self) -> None:
        if not self.name or Path(self.name).name != self.name:
            raise ValueError("source name must be a plain filename")
        if not self.url:
            raise ValueError("source URL must be non-empty")
        if self.sha256 is not None and not _SHA256_PATTERN.fullmatch(self.sha256):
            raise ValueError(f"invalid SHA-256 for {self.name!r}")


@dataclass(frozen=True)
class DownloadRecord:
    name: str
    path: str
    url: str
    bytes: int
    sha256: str
    expected_sha256: str | None
    hash_verified: bool
    downloaded_at: str
    timestamp_source: str
    reused_existing: bool

    def to_manifest_record(self) -> dict[str, object]:
        return asdict(self)


def official_sources(
    expected_hashes: Mapping[str, str | None] | None = None,
) -> tuple[SourceFile, ...]:
    """Return canonical sources, optionally pinned by filename or logical key."""

    hashes = expected_hashes or {}
    result = []
    for logical_name, filename in OFFICIAL_FILENAMES.items():
        expected = hashes.get(filename, hashes.get(logical_name))
        result.append(
            SourceFile(
                name=filename,
                url=f"{OFFICIAL_BASE_URL}/{filename}",
                sha256=expected,
            )
        )
    return tuple(result)


def fetch_source(
    source: SourceFile,
    destination: str | Path,
    *,
    overwrite: bool = False,
    timeout: float = 60.0,
) -> DownloadRecord:
    """Download one file atomically, always hashing and optionally verifying it."""

    if timeout <= 0:
        raise ValueError("timeout must be positive")
    directory = Path(destination)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / source.name
    expected = source.sha256.lower() if source.sha256 is not None else None

    if target.exists() and not overwrite:
        observed = sha256_file(target)
        if expected is not None and observed != expected:
            raise HashMismatchError(
                f"SHA-256 mismatch for existing {target}: expected {expected}, observed {observed}"
            )
        timestamp = (
            datetime.fromtimestamp(target.stat().st_mtime, UTC).isoformat().replace("+00:00", "Z")
        )
        return DownloadRecord(
            name=source.name,
            path=str(target),
            url=source.url,
            bytes=int(target.stat().st_size),
            sha256=observed,
            expected_sha256=expected,
            hash_verified=expected is not None,
            downloaded_at=timestamp,
            timestamp_source="file_mtime",
            reused_existing=True,
        )

    temporary = directory / f".{source.name}.partial"
    temporary.unlink(missing_ok=True)
    downloaded_at = utc_timestamp()
    request = urllib.request.Request(
        source.url, headers={"User-Agent": "FlyGI/0.1 connectome-ingestion"}
    )
    try:
        with (
            urllib.request.urlopen(request, timeout=timeout) as response,
            temporary.open("wb") as output,
        ):
            while chunk := response.read(8 * 1024 * 1024):
                output.write(chunk)
        observed = sha256_file(temporary)
        if expected is not None and observed != expected:
            raise HashMismatchError(
                f"SHA-256 mismatch for downloaded {source.name}: expected "
                f"{expected}, observed {observed}"
            )
        temporary.replace(target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise

    return DownloadRecord(
        name=source.name,
        path=str(target),
        url=source.url,
        bytes=int(target.stat().st_size),
        sha256=observed,
        expected_sha256=expected,
        hash_verified=expected is not None,
        downloaded_at=downloaded_at,
        timestamp_source="download",
        reused_existing=False,
    )


def fetch_sources(
    sources: Iterable[SourceFile],
    destination: str | Path,
    *,
    overwrite: bool = False,
    timeout: float = 60.0,
) -> list[DownloadRecord]:
    """Fetch all declared source files and return their provenance records."""

    declared = tuple(sources)
    names = [source.name for source in declared]
    if len(set(names)) != len(names):
        raise ValueError("source filenames must be unique")
    return [
        fetch_source(
            source,
            destination,
            overwrite=overwrite,
            timeout=timeout,
        )
        for source in declared
    ]


def write_download_manifest(path: str | Path, records: Iterable[DownloadRecord]) -> Path:
    """Persist observed source hashes for pinning future fetches."""

    return write_manifest(
        path,
        {
            "format": "flygi.download-manifest/v1",
            "created_at": utc_timestamp(),
            "files": [record.to_manifest_record() for record in records],
        },
    )
