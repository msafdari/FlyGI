"""Hash verification and strict source-schema behavior."""

from __future__ import annotations

import hashlib

import pandas as pd
import pytest

from flygi.connectome.download import SourceFile, fetch_source
from flygi.connectome.manifest import HashMismatchError, file_record, sha256_file
from flygi.connectome.schema import SchemaMismatchError, validate_weights_table


def test_existing_download_is_rehashed_and_verified(tmp_path) -> None:
    payload = b"small deterministic fixture\n"
    target = tmp_path / "weights.feather"
    target.write_bytes(payload)
    expected = hashlib.sha256(payload).hexdigest()
    source = SourceFile("weights.feather", "https://example.invalid/weights", expected)

    record = fetch_source(source, tmp_path)

    assert record.reused_existing is True
    assert record.hash_verified is True
    assert record.sha256 == expected == sha256_file(target)


def test_hash_mismatch_fails_before_network_access(tmp_path) -> None:
    target = tmp_path / "weights.feather"
    target.write_bytes(b"wrong")
    source = SourceFile("weights.feather", "https://example.invalid/weights", "0" * 64)

    with pytest.raises(HashMismatchError, match="SHA-256 mismatch"):
        fetch_source(source, tmp_path)


def test_schema_mismatch_is_reported_without_alias_guessing() -> None:
    wrong = pd.DataFrame(
        {
            "source": pd.Series([1], dtype="int64"),
            "target": pd.Series([2], dtype="int64"),
            "weight": pd.Series([3], dtype="int64"),
        }
    )

    with pytest.raises(SchemaMismatchError, match="missing columns"):
        validate_weights_table(wrong)


def test_source_digest_must_be_sha256() -> None:
    with pytest.raises(ValueError, match="invalid SHA-256"):
        SourceFile("weights.feather", "https://example.invalid/weights", "abc")


def test_provenance_record_reverifies_expected_digest(tmp_path) -> None:
    source = tmp_path / "source.feather"
    source.write_bytes(b"changed after download")

    with pytest.raises(HashMismatchError, match="SHA-256 mismatch"):
        file_record(source, expected_sha256="0" * 64)
