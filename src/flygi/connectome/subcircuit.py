"""Anatomical subcircuit extraction for fidelity-class-2 simulation.

Class-2 (temporal/spiking) dynamics run on SUBCIRCUITS -- the field's
standard practice (whole-brain LIF aside, every validated circuit model of
record simulates the relevant neuropil: Lappalainen 2024 the optic lobe,
Kakaria & de Bivort 2017 the EB-PB ring, Litwin-Kumar 2017 the MB). A
subcircuit here is the induced subgraph over a node selection, with weights
as SIGNED RAW SYNAPSE COUNTS rebuilt from the source pair table: the
compiled runtime's weights are log1p-transformed and incoming-l1 normalized
for the rate model, which destroys the count scale a conductance/LIF model
needs. Signs use the same measured-NT convention as the compiled graph
(ACh +, GABA/Glu/His -, per presynaptic consensus_nt; modulators default to
zero weight and are reported, not silently kept).
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

EXCITATORY = frozenset({"acetylcholine"})
INHIBITORY = frozenset({"gaba", "glutamate", "histamine"})
MODULATORY = frozenset({"dopamine", "octopamine", "serotonin"})


class SubcircuitError(RuntimeError):
    pass


@dataclass(frozen=True)
class Subcircuit:
    """An induced subgraph with signed synapse-count weights, W[post, pre]."""

    matrix: sparse.csr_matrix
    body_ids: NDArray[np.uint64]
    types: NDArray[np.str_]
    instances: NDArray[np.str_]
    superclasses: NDArray[np.str_]
    consensus_nt: NDArray[np.str_]
    dense_indices: NDArray[np.int64]  # positions in the full compiled graph
    dropped_modulatory_edges: int
    unsigned_edges: int

    @property
    def node_count(self) -> int:
        return int(self.matrix.shape[0])

    def indices_where(self, pattern: str, field: str = "types") -> NDArray[np.int64]:
        values = getattr(self, field).astype("U")
        mask = np.array([fnmatch.fnmatchcase(v, pattern) for v in values])
        return np.flatnonzero(mask)


def _load_metadata(runtime_dir: Path) -> dict[str, np.ndarray]:
    with np.load(runtime_dir / "node_metadata.npz", allow_pickle=False) as archive:
        return {
            "body_ids": np.asarray(archive["body_ids"]),
            "type": archive["type"].astype("U"),
            "instance": archive["instance"].astype("U"),
            "superclass": archive["superclass"].astype("U"),
            "consensus_nt": archive["consensus_nt"].astype("U"),
        }


def select_nodes(
    runtime_dir: str | Path,
    *,
    type_patterns: tuple[str, ...] = (),
    superclasses: tuple[str, ...] = (),
    instance_patterns: tuple[str, ...] = (),
) -> NDArray[np.int64]:
    """Dense indices of nodes matching ANY given pattern (fnmatch, case-sensitive)."""

    metadata = _load_metadata(Path(runtime_dir))
    count = metadata["type"].shape[0]
    mask = np.zeros(count, dtype=bool)
    for pattern in type_patterns:
        mask |= np.array([fnmatch.fnmatchcase(v, pattern) for v in metadata["type"]])
    for superclass in superclasses:
        mask |= metadata["superclass"] == superclass
    for pattern in instance_patterns:
        mask |= np.array(
            [fnmatch.fnmatchcase(v, pattern) for v in metadata["instance"]]
        )
    if not mask.any():
        raise SubcircuitError("node selection is empty")
    return np.flatnonzero(mask).astype(np.int64)


def extract_subcircuit(
    runtime_dir: str | Path,
    dense_indices: NDArray[np.integer],
    *,
    weights_feather: str | Path | None = None,
    modulator_treatment: str = "zero",
) -> Subcircuit:
    """Build the induced subgraph with signed raw synapse counts.

    ``weights_feather`` is the source pair table (body_pre, body_post,
    weight=synapse count). The default resolves the repository's raw
    MaleCNS download. Pairs outside the selection are never materialized:
    the table is scanned in record batches and filtered by body-id set.
    """

    runtime_dir = Path(runtime_dir)
    metadata = _load_metadata(runtime_dir)
    dense = np.unique(np.asarray(dense_indices, dtype=np.int64))
    if dense.size == 0:
        raise SubcircuitError("empty selection")
    if dense.max() >= metadata["type"].shape[0]:
        raise SubcircuitError("dense index out of range")

    body_ids = metadata["body_ids"][dense].astype(np.uint64)
    position_of_body = {int(b): i for i, b in enumerate(body_ids)}
    nts = metadata["consensus_nt"][dense]

    if weights_feather is None:
        weights_feather = (
            Path(runtime_dir).parents[2]
            / "raw"
            / "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
        )
    weights_feather = Path(weights_feather)
    if not weights_feather.is_file():
        raise SubcircuitError(f"pair table not found: {weights_feather}")

    import pyarrow as pa
    import pyarrow.ipc as ipc

    body_set = np.sort(body_ids.astype(np.int64))
    rows_post: list[np.ndarray] = []
    cols_pre: list[np.ndarray] = []
    counts: list[np.ndarray] = []

    def _batches():
        # Feather v2 is Arrow IPC: memory-map and stream record batches so a
        # 151.8M-row scan costs O(batch), not O(file), in resident memory.
        with pa.memory_map(str(weights_feather), "r") as source:
            reader = ipc.open_file(source)
            for i in range(reader.num_record_batches):
                yield reader.get_batch(i).select(["body_pre", "body_post", "weight"])

    for batch in _batches():
        pre = batch.column(0).to_numpy(zero_copy_only=False).astype(np.int64)
        post = batch.column(1).to_numpy(zero_copy_only=False).astype(np.int64)
        weight = batch.column(2).to_numpy(zero_copy_only=False).astype(np.float32)
        keep = (
            (np.searchsorted(body_set, pre) < body_set.size)
            & (body_set[np.minimum(np.searchsorted(body_set, pre), body_set.size - 1)] == pre)
            & (np.searchsorted(body_set, post) < body_set.size)
            & (body_set[np.minimum(np.searchsorted(body_set, post), body_set.size - 1)] == post)
        )
        if not keep.any():
            continue
        rows_post.append(post[keep])
        cols_pre.append(pre[keep])
        counts.append(weight[keep])

    if not rows_post:
        matrix = sparse.csr_matrix((dense.size, dense.size), dtype=np.float32)
        return Subcircuit(
            matrix=matrix,
            body_ids=body_ids,
            types=metadata["type"][dense],
            instances=metadata["instance"][dense],
            superclasses=metadata["superclass"][dense],
            consensus_nt=nts,
            dense_indices=dense,
            dropped_modulatory_edges=0,
            unsigned_edges=0,
        )

    post_bodies = np.concatenate(rows_post)
    pre_bodies = np.concatenate(cols_pre)
    edge_counts = np.concatenate(counts)
    post_index = np.array([position_of_body[int(b)] for b in post_bodies])
    pre_index = np.array([position_of_body[int(b)] for b in pre_bodies])

    signs = np.zeros(pre_index.size, dtype=np.float32)
    pre_nt = nts[pre_index]
    signs[np.isin(pre_nt, list(EXCITATORY))] = 1.0
    signs[np.isin(pre_nt, list(INHIBITORY))] = -1.0
    modulatory_mask = np.isin(pre_nt, list(MODULATORY))
    unsigned_mask = signs == 0.0
    if modulator_treatment == "zero":
        pass  # modulatory and unknown stay zero-weight and are dropped below
    elif modulator_treatment == "excitatory":
        signs[modulatory_mask] = 1.0
    else:
        raise SubcircuitError(f"unknown modulator_treatment: {modulator_treatment}")

    signed = edge_counts * signs
    keep = signed != 0.0
    matrix = sparse.csr_matrix(
        (signed[keep], (post_index[keep], pre_index[keep])),
        shape=(dense.size, dense.size),
        dtype=np.float32,
    )
    matrix.sum_duplicates()
    return Subcircuit(
        matrix=matrix,
        body_ids=body_ids,
        types=metadata["type"][dense],
        instances=metadata["instance"][dense],
        superclasses=metadata["superclass"][dense],
        consensus_nt=nts,
        dense_indices=dense,
        dropped_modulatory_edges=int(modulatory_mask.sum()),
        unsigned_edges=int((unsigned_mask & ~modulatory_mask).sum()),
    )
