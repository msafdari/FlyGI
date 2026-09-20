"""Schema contracts for the MaleCNS v1.0 source tables.

The column names below were checked against the Arrow metadata embedded in the
three files published at https://male-cns.janelia.org/download/.  Import code
uses these names literally: it never tries aliases or guesses a replacement
column when a source schema changes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pandas.api import types as ptypes


class SchemaMismatchError(ValueError):
    """Raised when a source table does not satisfy its declared contract."""


WEIGHTS_COLUMNS = ("body_pre", "body_post", "weight")

ANNOTATIONS_COLUMNS = (
    "assignedOlHex1",
    "assignedOlHex2",
    "bodyId",
    "flywireType",
    "group",
    "instance",
    "somaSide",
    "statusLabel",
    "superclass",
    "type",
    "vfbId",
    "hemibrainType",
    "itoleeHl",
    "supertype",
    "birthtime",
    "mancBodyid",
    "mancGroup",
    "mancType",
    "subclass",
    "synonyms",
    "class",
    "rootSide",
    "somaNeuromere",
    "trumanHl",
    "dimorphism",
    "matchingNotes",
    "entryNerve",
    "mancSerial",
    "mcnsSerial",
    "serialMotif",
    "fruDsx",
    "exitNerve",
    "receptorType",
    "somaLocation",
    "tosomaLocation",
    "status",
)

NEUROTRANSMITTER_COLUMNS = (
    "body",
    "cell_type",
    "total_nt_predictions",
    "predicted_nt_confidence",
    "predicted_nt",
    "ground_truth",
    "celltype_total_nt_predictions",
    "celltype_predicted_nt",
    "celltype_predicted_nt_confidence",
    "consensus_nt",
)


@dataclass(frozen=True)
class TableContract:
    """Expected names and semantic dtypes for one source table."""

    name: str
    columns: tuple[str, ...]
    required_kinds: Mapping[str, str]


WEIGHTS_CONTRACT = TableContract(
    "weights",
    WEIGHTS_COLUMNS,
    {"body_pre": "integer", "body_post": "integer", "weight": "integer"},
)
ANNOTATIONS_CONTRACT = TableContract("annotations", ANNOTATIONS_COLUMNS, {"bodyId": "integer"})
NEUROTRANSMITTERS_CONTRACT = TableContract(
    "neurotransmitters",
    NEUROTRANSMITTER_COLUMNS,
    {"body": "integer", "consensus_nt": "string"},
)


def _dtype_kind(dtype: Any) -> str:
    """Return a small, stable semantic kind for pandas or Arrow dtype text."""

    # pandas' helpers cover numpy, extension, and categorical dtypes.
    try:
        if ptypes.is_integer_dtype(dtype):
            return "integer"
        if ptypes.is_float_dtype(dtype) or ptypes.is_numeric_dtype(dtype):
            return "numeric"
        if ptypes.is_string_dtype(dtype) or ptypes.is_object_dtype(dtype):
            return "string"
    except (TypeError, ValueError):
        pass

    # Arrow schemas are intentionally accepted without importing pyarrow here.
    label = str(dtype).lower()
    if label.startswith(("int", "uint")):
        return "integer"
    if label.startswith(("float", "double", "decimal")):
        return "numeric"
    if any(token in label for token in ("string", "utf8", "dictionary")):
        return "string"
    return label


def validate_observed_schema(
    columns: Iterable[str],
    dtypes: Mapping[str, Any],
    contract: TableContract,
    *,
    strict: bool = True,
) -> None:
    """Validate names and critical dtypes, with a diagnostic mismatch error.

    ``strict=False`` is useful only for deliberately minimal synthetic fixtures.
    Production import keeps strict mode enabled so an upstream schema change is
    visible rather than being interpreted through guessed aliases.
    """

    observed = tuple(str(column) for column in columns)
    observed_set = set(observed)
    expected_set = set(contract.columns)
    required = set(contract.required_kinds)
    missing = sorted((expected_set if strict else required) - observed_set)
    unexpected = sorted(observed_set - expected_set) if strict else []

    type_errors: list[str] = []
    for column, expected_kind in contract.required_kinds.items():
        if column not in observed_set:
            continue
        actual_kind = _dtype_kind(dtypes[column])
        if expected_kind == "numeric":
            matches = actual_kind in {"integer", "numeric"}
        else:
            matches = actual_kind == expected_kind
        if not matches:
            type_errors.append(f"{column}: expected {expected_kind}, observed {dtypes[column]!s}")

    if missing or unexpected or type_errors:
        details = [f"MaleCNS {contract.name} schema mismatch."]
        if missing:
            details.append(f"missing columns={missing}")
        if unexpected:
            details.append(f"unexpected columns={unexpected}")
        if type_errors:
            details.append(f"dtype mismatches={type_errors}")
        details.append(f"observed columns={list(observed)}")
        raise SchemaMismatchError(" ".join(details))


def _validate_dataframe(
    frame: pd.DataFrame, contract: TableContract, *, strict: bool
) -> pd.DataFrame:
    validate_observed_schema(
        frame.columns,
        {name: dtype for name, dtype in frame.dtypes.items()},
        contract,
        strict=strict,
    )
    return frame


def validate_weights_table(frame: pd.DataFrame, *, strict: bool = True) -> pd.DataFrame:
    """Validate the directed edge table and reject invalid contact counts."""

    _validate_dataframe(frame, WEIGHTS_CONTRACT, strict=strict)
    if frame.loc[:, WEIGHTS_COLUMNS].isna().any(axis=None):
        raise SchemaMismatchError("MaleCNS weights table contains null values")
    weights = frame["weight"]
    if (weights < 0).any():
        raise SchemaMismatchError("MaleCNS weights must be non-negative synapse counts")
    return frame


def validate_annotations_table(frame: pd.DataFrame, *, strict: bool = True) -> pd.DataFrame:
    """Validate the curated body-annotation table."""

    _validate_dataframe(frame, ANNOTATIONS_CONTRACT, strict=strict)
    if frame["bodyId"].isna().any():
        raise SchemaMismatchError("MaleCNS annotations contain null bodyId values")
    return frame


def validate_neurotransmitters_table(frame: pd.DataFrame, *, strict: bool = True) -> pd.DataFrame:
    """Validate the per-body neurotransmitter prediction table."""

    _validate_dataframe(frame, NEUROTRANSMITTERS_CONTRACT, strict=strict)
    if frame["body"].isna().any():
        raise SchemaMismatchError("MaleCNS neurotransmitters contain null body values")
    return frame


def coerce_body_ids(values: Any, *, column: str) -> np.ndarray:
    """Return validated body IDs as uint64 without accepting lossy floats.

    MaleCNS currently publishes signed ``int64`` IDs, but the runtime format is
    deliberately ``uint64``.  The explicit range and round-trip checks guard
    against the common accidental ``int32`` conversion.
    """

    series = values if isinstance(values, pd.Series) else pd.Series(values)
    if series.isna().any():
        raise SchemaMismatchError(f"{column} contains null body IDs")
    if not ptypes.is_integer_dtype(series.dtype):
        raise SchemaMismatchError(f"{column} must have an integer dtype; observed {series.dtype}")

    python_values = [int(value) for value in series.array]
    maximum = int(np.iinfo(np.uint64).max)
    if any(value < 0 or value > maximum for value in python_values):
        raise SchemaMismatchError(f"{column} contains an ID outside the uint64 range")
    result = np.asarray(python_values, dtype=np.uint64)
    if [int(value) for value in result] != python_values:
        raise SchemaMismatchError(f"{column} failed the uint64 round-trip check")
    return result


def dataframe_schema(frame: pd.DataFrame) -> dict[str, Any]:
    """Return a JSON-compatible record of column order and observed dtypes."""

    return {
        "columns": [str(column) for column in frame.columns],
        "dtypes": {str(column): str(dtype) for column, dtype in frame.dtypes.items()},
        "rows": len(frame),
    }


def inspect_table_schema(path: str | Path) -> dict[str, Any]:
    """Inspect a table's schema without silently renaming any columns."""

    source = Path(path)
    suffix = source.suffix.lower()
    if suffix in {".feather", ".arrow", ".ipc"}:
        try:
            import pyarrow as pa
            import pyarrow.ipc as ipc
        except ImportError as exc:  # pragma: no cover - dependency error path
            raise RuntimeError("pyarrow is required to inspect Feather files") from exc
        with pa.memory_map(str(source), "r") as memory:
            schema = ipc.open_file(memory).schema
            return {
                "columns": list(schema.names),
                "dtypes": {field.name: str(field.type) for field in schema},
                "rows": None,
            }

    frame = read_table(source)
    return dataframe_schema(frame)


def read_table(
    table: str | Path | pd.DataFrame, *, columns: Iterable[str] | None = None
) -> pd.DataFrame:
    """Read a supported source table or copy an in-memory synthetic fixture."""

    selected = list(columns) if columns is not None else None
    if isinstance(table, pd.DataFrame):
        return table.loc[:, selected].copy() if selected is not None else table.copy()

    path = Path(table)
    suffix = path.suffix.lower()
    if suffix in {".feather", ".arrow", ".ipc"}:
        return pd.read_feather(path, columns=selected)
    if suffix == ".parquet":
        return pd.read_parquet(path, columns=selected)
    if suffix == ".csv":
        frame = pd.read_csv(path, usecols=selected)
        return frame
    if suffix == ".tsv":
        frame = pd.read_csv(path, sep="\t", usecols=selected)
        return frame
    raise ValueError(f"Unsupported table format for {path}")
