"""Verified loading of immutable connectome assets for neural dynamics."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

from flygi.connectome.build import NodeIndex, load_runtime_graph
from flygi.connectome.groups import load_groups
from flygi.connectome.manifest import load_manifest, verify_manifest_hashes

MATRIX_CONVENTION = "W[post_index, pre_index]"
PROPAGATION = "W @ activity"
_RUNTIME_OUTPUTS = frozenset({"graph.npz", "groups.npz"})


@dataclass(frozen=True, slots=True)
class RuntimeConnectome:
    """A verified graph bundle whose sparse storage and group arrays are frozen."""

    matrix: sparse.csr_matrix
    node_index: NodeIndex
    groups: Mapping[str, NDArray[np.int32]]
    manifest: Mapping[str, Any]
    verified_hashes: Mapping[str, str]

    @property
    def node_count(self) -> int:
        """Number of neurons represented by the runtime graph."""

        return int(self.matrix.shape[0])

    @property
    def edge_count(self) -> int:
        """Number of stored nonzero directed edges."""

        return int(self.matrix.nnz)


def _manifest_count(manifest: Mapping[str, Any], name: str) -> int:
    counts = manifest.get("counts")
    if not isinstance(counts, Mapping):
        raise ValueError("connectome manifest counts must be a mapping")
    value = counts.get(name)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"connectome manifest count {name!r} must be a non-negative integer")
    return value


def _validate_hashed_outputs(manifest: Mapping[str, Any]) -> None:
    outputs = manifest.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("connectome manifest must declare hashed runtime outputs")

    declared_paths: set[str] = set()
    for record in outputs:
        if not isinstance(record, Mapping):
            raise ValueError("connectome manifest output records must be mappings")
        path = record.get("path")
        digest = record.get("sha256")
        if not isinstance(path, str) or not path:
            raise ValueError("connectome manifest output path must be a non-empty string")
        if path in declared_paths:
            raise ValueError(f"connectome manifest declares output {path!r} more than once")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdefABCDEF" for character in digest)
        ):
            raise ValueError(f"connectome manifest output {path!r} has an invalid SHA-256")
        declared_paths.add(path)

    missing = sorted(_RUNTIME_OUTPUTS - declared_paths)
    if missing:
        raise ValueError(f"connectome manifest is missing runtime outputs: {missing}")


def _normalize_required_groups(required_groups: Iterable[str]) -> tuple[str, ...]:
    if isinstance(required_groups, str):
        raise TypeError("required_groups must be an iterable of names, not a string")
    try:
        names = tuple(required_groups)
    except TypeError as exc:
        raise TypeError("required_groups must be an iterable of group names") from exc
    if any(not isinstance(name, str) or not name for name in names):
        raise ValueError("required group names must be non-empty strings")
    if len(set(names)) != len(names):
        raise ValueError("required group names must be unique")
    return names


def _validate_groups(
    groups: Mapping[str, NDArray[np.int32]],
    *,
    node_count: int,
    required: tuple[str, ...],
) -> Mapping[str, NDArray[np.int32]]:
    frozen: dict[str, NDArray[np.int32]] = {}
    for name, raw_indices in groups.items():
        indices = np.asarray(raw_indices)
        if indices.ndim != 1 or indices.dtype != np.int32:
            raise ValueError(f"group {name!r} must contain a one-dimensional int32 array")
        if len(indices) > 1 and np.any(indices[1:] <= indices[:-1]):
            raise ValueError(f"group {name!r} indices must be sorted and unique")
        if len(indices) and ((indices < 0).any() or (indices >= node_count).any()):
            raise ValueError(f"group {name!r} contains a node index outside [0, {node_count})")
        indices.flags.writeable = False
        frozen[name] = indices

    for name in required:
        if name not in frozen:
            raise ValueError(f"required connectome group {name!r} is missing")
        if len(frozen[name]) == 0:
            raise ValueError(f"required connectome group {name!r} is empty")
    return MappingProxyType(frozen)


def load_runtime_connectome(
    directory: str | Path,
    *,
    verify_hashes: bool = True,
    required_groups: Iterable[str] = ("descending_neurons",),
) -> RuntimeConnectome:
    """Load and cross-check one compiled connectome directory.

    Output hashes are verified once during construction. Source-table hashes are
    deliberately excluded because deployment bundles do not include the large raw
    MaleCNS tables.
    """

    root = Path(directory).resolve()
    required = _normalize_required_groups(required_groups)
    manifest = load_manifest(root / "manifest.json")
    if manifest.get("matrix_convention") != MATRIX_CONVENTION:
        raise ValueError(f"connectome manifest matrix convention must be {MATRIX_CONVENTION!r}")
    if manifest.get("propagation") != PROPAGATION:
        raise ValueError(f"connectome manifest propagation must be {PROPAGATION!r}")

    expected_nodes = _manifest_count(manifest, "retained_neurons")
    expected_edges = _manifest_count(manifest, "runtime_nonzero_edges")
    verified: Mapping[str, str] = {}
    if verify_hashes:
        _validate_hashed_outputs(manifest)
        verified = verify_manifest_hashes(manifest, root=root, include_sources=False)

    matrix, node_index = load_runtime_graph(root / "graph.npz")
    if not sparse.isspmatrix_csr(matrix):
        raise ValueError("runtime connectivity must be a SciPy CSR matrix")
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("runtime connectivity must be square")
    if matrix.dtype != np.dtype(np.float32):
        raise ValueError("runtime connectivity must have float32 weights")
    if matrix.shape != (expected_nodes, expected_nodes) or len(node_index) != expected_nodes:
        raise ValueError(
            "runtime graph node count disagrees with manifest retained_neurons: "
            f"expected {expected_nodes}, observed {matrix.shape[0]}"
        )
    if matrix.nnz != expected_edges:
        raise ValueError(
            "runtime graph edge count disagrees with manifest runtime_nonzero_edges: "
            f"expected {expected_edges}, observed {matrix.nnz}"
        )
    if not matrix.has_canonical_format:
        raise ValueError("runtime connectivity must have sorted, duplicate-free CSR indices")
    if not np.isfinite(matrix.data).all():
        raise ValueError("runtime connectivity contains NaN or infinity")
    if np.count_nonzero(matrix.data == 0.0):
        raise ValueError("runtime connectivity must not store explicit zero weights")

    groups = _validate_groups(
        load_groups(root / "groups.npz"),
        node_count=expected_nodes,
        required=required,
    )
    matrix.data.flags.writeable = False
    matrix.indices.flags.writeable = False
    matrix.indptr.flags.writeable = False

    return RuntimeConnectome(
        matrix=matrix,
        node_index=node_index,
        groups=groups,
        manifest=MappingProxyType(manifest),
        verified_hashes=MappingProxyType(dict(verified)),
    )
