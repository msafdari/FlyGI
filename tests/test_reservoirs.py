"""Matched generic reservoirs and the positive control."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from flygi.connectome.normalize import estimate_spectral_radius, incoming_l1_normalize
from flygi.connectome.reservoirs import (
    ReservoirError,
    ReservoirOptions,
    build_matched_reservoir,
    reservoir_invariants,
)

NODES = 400
EDGES = 6_000


def _weights(seed: int = 0) -> np.ndarray:
    generator = np.random.default_rng(seed)
    return (generator.lognormal(0.0, 1.0, size=EDGES) + 0.01).astype(np.float32)


def _real_graph(seed: int = 5) -> sparse.csr_matrix:
    generator = np.random.default_rng(seed)
    matrix, _ = build_matched_reservoir(
        NODES, EDGES, _weights(seed), seed=int(generator.integers(0, 10_000))
    )
    return matrix


def test_matched_reservoir_matches_size_and_weight_multiset() -> None:
    weights = _weights()
    matrix, stats = build_matched_reservoir(NODES, EDGES, weights, seed=1)

    assert matrix.shape == (NODES, NODES)
    assert matrix.nnz == EDGES
    assert stats["weight_multiset_preserved"]
    # The multiset is preserved before normalization; incoming-L1 rescales rows,
    # so compare the pre-normalization promise through the statistics instead.
    assert stats["normalization"] == "incoming_l1"
    assert stats["is_matched_null"]
    assert not stats["is_positive_control"]


def test_matched_reservoir_places_no_self_edges_by_default() -> None:
    matrix, _ = build_matched_reservoir(NODES, EDGES, _weights(), seed=2)
    assert int(np.count_nonzero(np.asarray(matrix.diagonal()))) == 0


def test_matched_reservoir_is_deterministic_and_seed_sensitive() -> None:
    weights = _weights()
    first, _ = build_matched_reservoir(NODES, EDGES, weights, seed=3)
    second, _ = build_matched_reservoir(NODES, EDGES, weights, seed=3)
    other, _ = build_matched_reservoir(NODES, EDGES, weights, seed=4)

    assert np.array_equal(first.indices, second.indices)
    assert np.array_equal(first.data, second.data)
    assert not np.array_equal(first.indices, other.indices)


def test_positive_control_sits_at_the_declared_spectral_radius() -> None:
    """The whole point of the positive control is that it is in a good regime."""

    matrix, stats = build_matched_reservoir(
        NODES,
        EDGES,
        _weights(),
        seed=6,
        options=ReservoirOptions(kind="edge_of_chaos", spectral_radius=0.95),
    )
    assert stats["is_positive_control"]
    assert not stats["is_matched_null"]
    assert stats["departs_from_declared_normalization"]
    observed = estimate_spectral_radius(matrix, max_iterations=400)
    assert observed == pytest.approx(0.95, rel=0.05)


def test_positive_control_uses_signed_weights() -> None:
    """Scaling alone is not enough; a non-negative matrix diffuses."""

    matrix, stats = build_matched_reservoir(
        NODES,
        EDGES,
        _weights(),
        seed=7,
        options=ReservoirOptions(kind="edge_of_chaos", spectral_radius=0.95),
    )
    assert stats["signs_randomized"]
    assert stats["departs_from_declared_sign_mode"]
    assert float(np.mean(matrix.data < 0)) == pytest.approx(0.5, abs=0.05)


def test_matched_null_radius_is_pinned_by_its_normalization() -> None:
    """Recorded so the positive control is never targeted below the null."""

    null_matrix, _ = build_matched_reservoir(NODES, EDGES, _weights(), seed=7)
    assert estimate_spectral_radius(null_matrix, max_iterations=400) == pytest.approx(1.0, abs=0.02)


def test_positive_control_retains_state_longer_than_the_matched_null() -> None:
    """The behavioral reason the positive control exists: it should remember."""

    from flygi.dynamics.rate import RateParameters, ScipyRateNetwork

    weights = _weights()
    null_matrix, _ = build_matched_reservoir(NODES, EDGES, weights, seed=8)
    positive, _ = build_matched_reservoir(
        NODES,
        EDGES,
        weights,
        seed=8,
        options=ReservoirOptions(kind="edge_of_chaos", spectral_radius=0.98),
    )

    def remaining(matrix: sparse.csr_matrix) -> float:
        network = ScipyRateNetwork(
            matrix, RateParameters(internal_steps=4, leak=0.3, recurrent_gain=0.9)
        )
        generator = np.random.default_rng(0)
        left = np.zeros(NODES, dtype=np.float32)
        right = np.zeros(NODES, dtype=np.float32)
        a = (generator.standard_normal(NODES) * 0.5).astype(np.float32)
        b = (generator.standard_normal(NODES) * 0.5).astype(np.float32)
        for _ in range(6):
            left = network.advance(left, a, internal_steps=4)
            right = network.advance(right, b, internal_steps=4)
        base = float(np.linalg.norm(left - right))
        for _ in range(8):
            left = network.advance(left, None, internal_steps=4)
            right = network.advance(right, None, internal_steps=4)
        return float(np.linalg.norm(left - right) / base)

    assert remaining(positive) > remaining(null_matrix)


def test_reservoir_invariants_report_size_mismatch() -> None:
    real = incoming_l1_normalize(_real_graph())
    reservoir, _ = build_matched_reservoir(NODES, EDGES, _weights(), seed=9)
    record = reservoir_invariants(real, reservoir, expect_weight_multiset_match=False)
    assert record["valid"], record["failures"]

    smaller, _ = build_matched_reservoir(NODES, EDGES // 2, _weights()[: EDGES // 2], seed=9)
    broken = reservoir_invariants(real, smaller, expect_weight_multiset_match=False)
    assert not broken["valid"]
    assert "edge_count_matches" in broken["failures"]


def test_reservoir_options_reject_unusable_settings() -> None:
    for kwargs in (
        {"kind": "bogus"},
        {"spectral_radius": 0.0},
        {"spectral_radius": float("nan")},
        {"weight_source": "bogus"},
    ):
        with pytest.raises(ReservoirError):
            ReservoirOptions(**kwargs)  # type: ignore[arg-type]


def test_reservoir_refuses_an_impossible_edge_count() -> None:
    with pytest.raises(ReservoirError):
        build_matched_reservoir(4, 100, np.ones(100, dtype=np.float32), seed=0)


def test_reservoir_requires_a_weight_per_edge() -> None:
    with pytest.raises(ReservoirError):
        build_matched_reservoir(NODES, EDGES, np.ones(7, dtype=np.float32), seed=0)
