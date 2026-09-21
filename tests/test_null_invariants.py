"""Invariants of the preregistered directed degree-preserving null."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from flygi.connectome.nulls import (
    NullOptions,
    NullValidationError,
    degree_preserving_rewire,
    directed_degrees,
    null_invariants,
)


def _random_graph(node_count: int = 240, density: float = 0.05, seed: int = 0) -> sparse.csr_matrix:
    """A directed graph with no self-edges, in the ``W[post, pre]`` convention."""

    generator = np.random.default_rng(seed)
    dense = generator.random((node_count, node_count)) < density
    np.fill_diagonal(dense, False)
    weights = (generator.random((node_count, node_count)) + 0.1).astype(np.float32)
    matrix = sparse.csr_matrix(np.where(dense, weights, 0.0).astype(np.float32))
    matrix.sort_indices()
    return matrix


def test_rewiring_preserves_both_degree_sequences_exactly() -> None:
    original = _random_graph()
    rewired, stats = degree_preserving_rewire(
        original, seed=11, options=NullOptions(swaps_per_edge=5.0, batch_pairs=500)
    )

    source_in, source_out = directed_degrees(original)
    target_in, target_out = directed_degrees(rewired)

    assert np.array_equal(source_in, target_in)
    assert np.array_equal(source_out, target_out)
    assert stats["reached_target"]
    assert stats["accepted_swaps"] >= stats["target_swaps"]


def test_rewiring_preserves_the_global_weight_multiset() -> None:
    original = _random_graph(seed=2)
    rewired, _ = degree_preserving_rewire(
        original, seed=3, options=NullOptions(swaps_per_edge=5.0, batch_pairs=500)
    )
    assert np.array_equal(np.sort(original.data), np.sort(rewired.data))


def test_rewiring_preserves_each_presynaptic_outgoing_weight_multiset() -> None:
    """The declared weight rule: a weight travels with its presynaptic slot."""

    original = _random_graph(seed=4)
    rewired, _ = degree_preserving_rewire(
        original, seed=5, options=NullOptions(swaps_per_edge=5.0, batch_pairs=500)
    )

    def outgoing(matrix: sparse.csr_matrix) -> dict[int, np.ndarray]:
        coo = matrix.tocoo(copy=False)
        order = np.argsort(coo.col, kind="stable")
        columns = coo.col[order]
        data = coo.data[order]
        boundaries = np.flatnonzero(np.diff(columns)) + 1
        return {
            int(columns[block[0]]): np.sort(data[block])
            for block in np.split(np.arange(len(columns)), boundaries)
            if len(block)
        }

    source, target = outgoing(original), outgoing(rewired)
    assert source.keys() == target.keys()
    for node, values in source.items():
        assert np.allclose(values, target[node])


def test_rewiring_creates_no_self_edges_or_duplicates() -> None:
    original = _random_graph(seed=6)
    rewired, _ = degree_preserving_rewire(
        original, seed=7, options=NullOptions(swaps_per_edge=8.0, batch_pairs=500)
    )

    assert int(np.count_nonzero(rewired.diagonal())) == 0
    assert rewired.nnz == original.nnz
    assert rewired.has_canonical_format


def test_rewiring_actually_destroys_topology() -> None:
    """A null that mostly reproduces the real edge set is not a null."""

    original = _random_graph(seed=8)
    rewired, _ = degree_preserving_rewire(
        original, seed=9, options=NullOptions(swaps_per_edge=10.0, batch_pairs=500)
    )
    report = null_invariants(original, rewired)

    assert report["valid"], report["failures"]
    assert report["fraction_shared_with_real_graph"] < 0.2


def test_rewiring_is_deterministic_for_a_fixed_seed() -> None:
    original = _random_graph(seed=10)
    options = NullOptions(swaps_per_edge=4.0, batch_pairs=500)
    first, first_stats = degree_preserving_rewire(original, seed=123, options=options)
    second, second_stats = degree_preserving_rewire(original, seed=123, options=options)
    other, _ = degree_preserving_rewire(original, seed=124, options=options)

    assert np.array_equal(first.indices, second.indices)
    assert np.array_equal(first.data, second.data)
    assert first_stats["accepted_swaps"] == second_stats["accepted_swaps"]
    assert not np.array_equal(first.indices, other.indices)


def test_independent_seeds_produce_different_nulls() -> None:
    """One null can be unusually good or bad by chance; seeds must differ."""

    original = _random_graph(seed=12)
    options = NullOptions(swaps_per_edge=4.0, batch_pairs=500)
    signatures = set()
    for seed in range(5):
        rewired, _ = degree_preserving_rewire(original, seed=seed, options=options)
        signatures.add(rewired.indices.tobytes())
    assert len(signatures) == 5


def test_declared_groups_keep_their_degrees() -> None:
    original = _random_graph(seed=14)
    rewired, _ = degree_preserving_rewire(
        original, seed=15, options=NullOptions(swaps_per_edge=5.0, batch_pairs=500)
    )
    groups = {"readout": np.arange(0, 20, dtype=np.int64)}
    report = null_invariants(original, rewired, preserved_groups=groups)

    assert report["groups"]["readout"]["in_degree_matches"]
    assert report["groups"]["readout"]["out_degree_matches"]
    assert report["groups"]["readout"]["size"] == 20


def test_null_invariants_detects_a_degree_violating_graph() -> None:
    original = _random_graph(seed=16)
    broken = original.copy().tolil()
    row = int(np.flatnonzero(np.diff(original.indptr) > 0)[0])
    column = int(original.indices[original.indptr[row]])
    broken[row, column] = 0.0
    broken = broken.tocsr()
    broken.eliminate_zeros()

    report = null_invariants(original, broken)

    assert not report["valid"]
    assert "edge count changed" in report["failures"]


def test_rewiring_rejects_a_graph_with_duplicate_edges() -> None:
    duplicated = sparse.coo_matrix(
        (
            np.array([1.0, 2.0], dtype=np.float32),
            (np.array([1, 1]), np.array([0, 0])),
        ),
        shape=(3, 3),
    ).tocsr()
    duplicated.sum_duplicates()
    # A canonical CSR cannot hold duplicates, so build the failure explicitly.
    raw = sparse.csr_matrix((3, 3), dtype=np.float32)
    raw.data = np.array([1.0, 2.0], dtype=np.float32)
    raw.indices = np.array([0, 0], dtype=np.int32)
    raw.indptr = np.array([0, 0, 2, 2], dtype=np.int32)
    with pytest.raises(NullValidationError):
        degree_preserving_rewire(raw, seed=0, options=NullOptions(swaps_per_edge=1.0))


def test_rewiring_refuses_a_nonsquare_matrix() -> None:
    with pytest.raises(NullValidationError):
        degree_preserving_rewire(sparse.csr_matrix(np.ones((3, 4), dtype=np.float32)), seed=0)


def test_rewiring_refuses_a_graph_that_is_too_small() -> None:
    tiny = sparse.csr_matrix(
        (np.array([1.0], dtype=np.float32), (np.array([1]), np.array([0]))), shape=(2, 2)
    )
    with pytest.raises(NullValidationError):
        degree_preserving_rewire(tiny, seed=0)


def test_null_options_reject_unusable_settings() -> None:
    for kwargs in (
        {"kind": "bogus"},
        {"swaps_per_edge": 0.0},
        {"swaps_per_edge": float("inf")},
        {"batch_pairs": 0},
        {"max_batches": 0},
    ):
        with pytest.raises(ValueError):
            NullOptions(**kwargs)  # type: ignore[arg-type]


def test_self_edges_are_permitted_only_when_declared() -> None:
    original = _random_graph(node_count=120, density=0.08, seed=18)
    strict, _ = degree_preserving_rewire(
        original,
        seed=19,
        options=NullOptions(swaps_per_edge=10.0, batch_pairs=500, allow_self_edges=False),
    )
    assert int(np.count_nonzero(strict.diagonal())) == 0

    _permissive, stats = degree_preserving_rewire(
        original,
        seed=19,
        options=NullOptions(swaps_per_edge=10.0, batch_pairs=500, allow_self_edges=True),
    )
    assert stats["allow_self_edges"] is True
    assert stats["rejected"]["self_edge"] == 0
