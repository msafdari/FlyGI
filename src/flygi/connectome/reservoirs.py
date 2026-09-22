"""Matched generic reservoirs, including the positive control.

Two distinct roles, deliberately kept separate.

**The matched generic reservoir** is a negative control in the specification's
sense: a graph with the real graph's node count, edge count and weight
multiset, but with edges placed uniformly at random. It answers "does almost
any large sparse reservoir work as well as the fly?" It is normalized exactly
like the real condition.

**The positive control** is not a null. Every other condition is built to be no
better than the fly, so a set of near-zero results cannot distinguish "the
biological graph confers no advantage" from "this interface and operating point
cannot express an advantage that *any* graph could confer." The positive
control is a reservoir deliberately placed in the regime reservoir computing
says is good, so that it *should* outperform if the harness can register an
advantage at all. If it does not, the failure is in the harness, not in the
biology.

Placing it there takes two changes, not one, and the second is easy to miss.
Scaling to a spectral radius near one is not sufficient, because incoming-L1
normalization of non-negative weights already produces a row-stochastic matrix
whose spectral radius is exactly one for *any* topology. Such a matrix is an
averaging operator: repeated application diffuses and destroys information, and
its memory is confined to a single global mode. A reservoir needs **signed**
weights so excitation and inhibition can sustain non-diffusive dynamics. The
positive control therefore assigns symmetric random signs before scaling to its
target radius, which is the standard echo-state construction.

This is also why the real graph's measured separation from its degree-preserving
nulls appears only in the signed condition: under unsigned incoming-L1 the
radius is pinned near one regardless of wiring.

Because its whole purpose is to differ, the positive control departs from the
declared normalization and from the declared sign mode. Both departures are
recorded in its statistics. It must never be reported as a matched null.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

from .normalize import estimate_spectral_radius, incoming_l1_normalize

ReservoirKind = Literal["matched_random", "edge_of_chaos"]


class ReservoirError(ValueError):
    """Raised when a reservoir cannot satisfy its declared contract."""


@dataclass(frozen=True)
class ReservoirOptions:
    """Declared, recorded choices that change a generated reservoir."""

    kind: ReservoirKind = "matched_random"
    allow_self_edges: bool = False
    spectral_radius: float = 0.95
    weight_source: Literal["real_multiset", "lognormal"] = "real_multiset"

    def __post_init__(self) -> None:
        if self.kind not in ("matched_random", "edge_of_chaos"):
            raise ReservoirError(f"Unknown reservoir kind: {self.kind!r}")
        if not np.isfinite(self.spectral_radius) or self.spectral_radius <= 0:
            raise ReservoirError("spectral_radius must be finite and positive")
        if self.weight_source not in ("real_multiset", "lognormal"):
            raise ReservoirError(f"Unknown weight source: {self.weight_source!r}")


def _sample_unique_edges(
    node_count: int,
    edge_count: int,
    *,
    generator: np.random.Generator,
    allow_self_edges: bool,
) -> tuple[NDArray[np.int64], NDArray[np.int64]]:
    """Draw ``edge_count`` distinct directed edges uniformly at random."""

    capacity = node_count * node_count - (0 if allow_self_edges else node_count)
    if edge_count > capacity:
        raise ReservoirError(
            f"cannot place {edge_count} distinct edges in a {node_count}-node graph"
        )

    keys = np.empty(0, dtype=np.int64)
    # Rejection sampling with top-up. At the real graph's density of roughly
    # 9e-4 the collision rate is negligible, so this converges immediately.
    while len(keys) < edge_count:
        shortfall = edge_count - len(keys)
        draw = generator.integers(
            0, node_count * node_count, size=int(shortfall * 1.05) + 16, dtype=np.int64
        )
        if not allow_self_edges:
            draw = draw[draw // node_count != draw % node_count]
        keys = np.unique(np.concatenate([keys, draw]))
    keys = generator.permutation(keys)[:edge_count]
    keys.sort()
    pre = keys // node_count
    post = keys % node_count
    return pre, post


def build_matched_reservoir(
    node_count: int,
    edge_count: int,
    weights: NDArray[np.floating],
    *,
    seed: int,
    options: ReservoirOptions | None = None,
) -> tuple[sparse.csr_matrix, dict[str, Any]]:
    """Create a reservoir matched to the real graph's size and weight multiset.

    Returns the normalized matrix in the ``W[post, pre]`` convention and a
    statistics record. ``weights`` supplies the multiset to reuse; it is
    permuted, never resampled, so the global weight distribution is exact.
    """

    settings = options or ReservoirOptions()
    if node_count <= 1:
        raise ReservoirError("reservoir requires at least two nodes")
    if edge_count < 1:
        raise ReservoirError("reservoir requires at least one edge")
    source_weights = np.asarray(weights, dtype=np.float32)
    if source_weights.ndim != 1 or len(source_weights) != edge_count:
        raise ReservoirError(
            f"expected {edge_count} weights to match the edge count, "
            f"observed {source_weights.shape}"
        )

    generator = np.random.default_rng(seed)
    pre, post = _sample_unique_edges(
        node_count,
        edge_count,
        generator=generator,
        allow_self_edges=settings.allow_self_edges,
    )
    assigned = generator.permutation(source_weights)

    matrix = sparse.csr_matrix(
        (assigned, (post, pre)), shape=(node_count, node_count), dtype=np.float32
    )
    matrix.sort_indices()
    matrix.sum_duplicates()
    if matrix.nnz != edge_count:
        raise ReservoirError(
            f"reservoir edge count drifted: expected {edge_count}, observed {matrix.nnz}"
        )

    unnormalized_radius = float(estimate_spectral_radius(matrix, max_iterations=200))
    if settings.kind == "matched_random":
        # Negative control: identical treatment to the real condition.
        normalized = incoming_l1_normalize(matrix)
        normalization = "incoming_l1"
    else:
        # Positive control: symmetric random signs, then scale to the target
        # radius. Both steps are required. Without the signs the matrix stays a
        # non-negative averaging operator whose repeated application diffuses,
        # and scaling alone would place it *below* the matched null, whose
        # row-stochastic radius is already one.
        signed = matrix.copy()
        signed.data = signed.data.astype(np.float32, copy=False)
        signs = generator.integers(0, 2, size=signed.nnz).astype(np.float32) * 2.0 - 1.0
        signed.data *= signs
        signed_radius = float(estimate_spectral_radius(signed, max_iterations=200))
        if signed_radius == 0.0:
            raise ReservoirError("cannot scale a zero-spectral-radius reservoir")
        signed.data *= np.float32(settings.spectral_radius / signed_radius)
        normalized = signed
        normalization = f"signed, spectral_radius={settings.spectral_radius}"
    normalized.sort_indices()

    achieved = float(estimate_spectral_radius(normalized, max_iterations=200))
    statistics = {
        "kind": settings.kind,
        "seed": int(seed),
        "nodes": int(node_count),
        "edges": int(matrix.nnz),
        "allow_self_edges": bool(settings.allow_self_edges),
        "weight_source": settings.weight_source,
        "weight_multiset_preserved": True,
        "normalization": normalization,
        "signs_randomized": settings.kind == "edge_of_chaos",
        "spectral_radius_before_normalization": unnormalized_radius,
        "spectral_radius_after_normalization": achieved,
        "is_matched_null": settings.kind == "matched_random",
        "is_positive_control": settings.kind == "edge_of_chaos",
        "departs_from_declared_normalization": settings.kind == "edge_of_chaos",
        "departs_from_declared_sign_mode": settings.kind == "edge_of_chaos",
    }
    return normalized, statistics


def reservoir_invariants(
    real: sparse.spmatrix,
    reservoir: sparse.spmatrix,
    *,
    expect_weight_multiset_match: bool,
) -> dict[str, Any]:
    """Check what a matched reservoir promises against the real graph."""

    source = real.tocsr(copy=False)
    target = reservoir.tocsr(copy=False)
    record: dict[str, Any] = {
        "node_count_matches": source.shape == target.shape,
        "edge_count_matches": int(source.nnz) == int(target.nnz),
        "self_edges": int(np.count_nonzero(np.asarray(target.diagonal()))),
    }
    if expect_weight_multiset_match:
        record["weight_multiset_matches"] = bool(
            np.allclose(np.sort(source.data), np.sort(target.data))
        )
    failures = [name for name in ("node_count_matches", "edge_count_matches") if not record[name]]
    if record.get("weight_multiset_matches") is False:
        failures.append("weight multiset changed")
    record["failures"] = failures
    record["valid"] = not failures
    return record
