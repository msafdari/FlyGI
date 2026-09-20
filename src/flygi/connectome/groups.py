"""Resolve declared annotation groups into compact dense-index arrays."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .schema import SchemaMismatchError, coerce_body_ids


@dataclass(frozen=True)
class GroupDefinition:
    """A named conjunction of exact annotation-column filters."""

    name: str
    filters: Mapping[str, object]


# Population labels are data-dependent modeling choices. The default is empty
# until a user declares filters after inspecting the downloaded annotations.
DEFAULT_GROUPS: tuple[GroupDefinition, ...] = ()


def _matches(series: pd.Series, expected: object) -> pd.Series:
    if isinstance(expected, (list, tuple, set, frozenset)):
        return series.isin(list(expected))
    if expected is None:
        return series.isna()
    return series == expected


def normalize_group_definitions(
    definitions: (Iterable[GroupDefinition] | Mapping[str, Mapping[str, object]] | None),
) -> tuple[GroupDefinition, ...]:
    if definitions is None:
        return DEFAULT_GROUPS
    if isinstance(definitions, Mapping):
        normalized = tuple(
            GroupDefinition(str(name), dict(filters)) for name, filters in definitions.items()
        )
    else:
        normalized = tuple(definitions)
    names = [definition.name for definition in normalized]
    if len(set(names)) != len(names):
        raise ValueError("group names must be unique")
    if any(not name for name in names):
        raise ValueError("group names must be non-empty")
    return normalized


def resolve_groups(
    annotations: pd.DataFrame,
    body_ids_by_index: np.ndarray,
    definitions: (Iterable[GroupDefinition] | Mapping[str, Mapping[str, object]] | None) = None,
) -> dict[str, np.ndarray]:
    """Resolve annotation filters to sorted, unique dense node indices."""

    if "bodyId" not in annotations:
        raise SchemaMismatchError("annotations are missing required column 'bodyId'")
    annotation_ids = coerce_body_ids(annotations["bodyId"], column="bodyId")
    if len(np.unique(annotation_ids)) != len(annotation_ids):
        raise SchemaMismatchError("annotations contain duplicate bodyId values")

    node_ids = np.asarray(body_ids_by_index)
    if node_ids.dtype != np.uint64 or node_ids.ndim != 1:
        raise TypeError("body_ids_by_index must be a one-dimensional uint64 array")
    if len(node_ids) and np.any(node_ids[1:] <= node_ids[:-1]):
        raise ValueError("body_ids_by_index must be strictly increasing")

    resolved: dict[str, np.ndarray] = {}
    for definition in normalize_group_definitions(definitions):
        mask = pd.Series(True, index=annotations.index, dtype=bool)
        for column, expected in definition.filters.items():
            if column not in annotations:
                raise SchemaMismatchError(
                    f"group {definition.name!r} requires missing annotation column {column!r}"
                )
            mask &= _matches(annotations[column], expected)
        selected = annotation_ids[mask.to_numpy()]
        positions = np.searchsorted(node_ids, selected)
        valid = positions < len(node_ids)
        if valid.any():
            candidates = positions[valid]
            selected_valid = selected[valid]
            exact = node_ids[candidates] == selected_valid
            indices = candidates[exact]
        else:
            indices = np.empty(0, dtype=np.int64)
        resolved[definition.name] = np.unique(indices).astype(np.int32, copy=False)
    return resolved


def pack_groups(
    groups: Mapping[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pack groups as names, offsets, values without object-pickled arrays."""

    names = list(groups)
    width = max((len(name) for name in names), default=1)
    name_array = np.asarray(names, dtype=f"<U{width}")
    offsets = np.zeros(len(names) + 1, dtype=np.int64)
    values: list[np.ndarray] = []
    for position, name in enumerate(names):
        indices = np.asarray(groups[name])
        if indices.ndim != 1 or not np.issubdtype(indices.dtype, np.integer):
            raise TypeError(f"group {name!r} indices must be a 1-D integer array")
        indices = np.unique(indices.astype(np.int32, copy=False))
        if len(indices) and int(indices[0]) < 0:
            raise ValueError(f"group {name!r} contains a negative node index")
        values.append(indices)
        offsets[position + 1] = offsets[position] + len(indices)
    packed = np.concatenate(values) if values else np.empty(0, dtype=np.int32)
    return name_array, offsets, packed


def save_groups(path: str | Path, groups: Mapping[str, np.ndarray]) -> Path:
    """Write compressed group arrays that are safe to load with allow_pickle=False."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    names, offsets, values = pack_groups(groups)
    with destination.open("wb") as stream:
        np.savez_compressed(
            stream,
            format_version=np.asarray([1], dtype=np.int16),
            names=names,
            offsets=offsets,
            indices=values,
        )
    return destination


def load_groups(path: str | Path) -> dict[str, np.ndarray]:
    """Load and validate a packed group asset."""

    with np.load(Path(path), allow_pickle=False) as archive:
        version = np.asarray(archive["format_version"])
        names = np.asarray(archive["names"])
        offsets = np.asarray(archive["offsets"], dtype=np.int64)
        indices = np.asarray(archive["indices"], dtype=np.int32)
    if version.tolist() != [1]:
        raise ValueError(f"Unsupported group format version: {version.tolist()}")
    if offsets.shape != (len(names) + 1,) or offsets[0] != 0:
        raise ValueError("invalid group offsets")
    if np.any(offsets[1:] < offsets[:-1]) or offsets[-1] != len(indices):
        raise ValueError("invalid group offset bounds")
    return {
        str(name): indices[int(offsets[i]) : int(offsets[i + 1])].copy()
        for i, name in enumerate(names)
    }
