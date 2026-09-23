"""The threaded matvec must be exactly SciPy, only faster.

Every score in the worklog was measured with SciPy's single-threaded kernel. If
threading changed even one float32 ulp, every one of those baselines would have
to be re-measured. Bit-identity is therefore not a nicety here, it is the
precondition for the optimisation being usable at all, and it is what these
tests are mostly about.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from flygi.dynamics.spmv import (
    DEFAULT_THREADS,
    ENVIRONMENT_VARIABLE,
    MINIMUM_NNZ_FOR_THREADS,
    SpmvPlan,
    configured_threads,
)


def _skewed_matrix(rows: int = 4000, seed: int = 0) -> sparse.csr_matrix:
    """A matrix with the heavy degree skew the real connectome has."""

    generator = np.random.default_rng(seed)
    degrees = (generator.pareto(1.2, rows) * 12 + 1).astype(int).clip(1, rows // 2)
    indptr = np.zeros(rows + 1, dtype=np.int32)
    indptr[1:] = np.cumsum(degrees)
    total = int(indptr[-1])
    indices = generator.integers(0, rows, total).astype(np.int32)
    data = generator.standard_normal(total).astype(np.float32)
    matrix = sparse.csr_matrix((data, indices, indptr), shape=(rows, rows))
    matrix.sort_indices()
    return matrix


def _force_threads(plan: SpmvPlan) -> SpmvPlan:
    """Partition regardless of the nnz threshold, so small test matrices split."""

    import flygi.dynamics.spmv as module

    original = module.MINIMUM_NNZ_FOR_THREADS
    module.MINIMUM_NNZ_FOR_THREADS = 0
    try:
        plan.rebuild()
    finally:
        module.MINIMUM_NNZ_FOR_THREADS = original
    return plan


def test_threaded_result_is_bit_identical_to_scipy() -> None:
    matrix = _skewed_matrix()
    vector = np.random.default_rng(1).standard_normal(matrix.shape[0]).astype(np.float32)
    expected = np.asarray(matrix @ vector, dtype=np.float32)
    with _force_threads(SpmvPlan(matrix, threads=6)) as plan:
        assert plan.threads > 1, "the test did not actually exercise threading"
        observed = plan.matvec(vector)
    assert np.array_equal(observed, expected), (
        "threading changed the result; float32 addition is not associative and "
        "every baseline in the worklog was measured without it"
    )


@pytest.mark.parametrize("threads", [1, 2, 3, 5, 8, 13])
def test_every_thread_count_gives_the_same_answer(threads: int) -> None:
    matrix = _skewed_matrix(rows=2500, seed=threads)
    vector = np.random.default_rng(2).standard_normal(matrix.shape[0]).astype(np.float32)
    expected = np.asarray(matrix @ vector, dtype=np.float32)
    with _force_threads(SpmvPlan(matrix, threads=threads)) as plan:
        assert np.array_equal(plan.matvec(vector), expected)


def test_blocks_are_views_not_copies() -> None:
    """Copying would duplicate 200 MB of connectome per plan."""

    matrix = _skewed_matrix()
    with _force_threads(SpmvPlan(matrix, threads=4)) as plan:
        assert plan.threads > 1
        vector = np.ones(matrix.shape[0], dtype=np.float32)
        before = plan.matvec(vector).copy()
        # A weight edit through the parent must be visible to the blocks, which
        # is what in-place plasticity depends on.
        matrix.data *= np.float32(2.0)
        after = plan.matvec(vector)
    assert np.allclose(after, before * 2.0), "blocks copied the matrix instead of viewing it"


def test_a_single_thread_allocates_no_pool() -> None:
    matrix = _skewed_matrix(rows=500)
    with SpmvPlan(matrix, threads=1) as plan:
        assert plan.threads == 1
        assert plan.describe()["blocks"] == 0
        vector = np.ones(matrix.shape[0], dtype=np.float32)
        assert np.array_equal(plan.matvec(vector), np.asarray(matrix @ vector, dtype=np.float32))


def test_small_matrices_stay_serial() -> None:
    """Below the threshold, pool dispatch costs more than the matvec saves."""

    matrix = _skewed_matrix(rows=300)
    assert matrix.nnz < MINIMUM_NNZ_FOR_THREADS
    with SpmvPlan(matrix, threads=8) as plan:
        assert plan.threads == 1


def test_rebuild_survives_a_structural_change() -> None:
    matrix = _skewed_matrix()
    vector = np.random.default_rng(3).standard_normal(matrix.shape[0]).astype(np.float32)
    with _force_threads(SpmvPlan(matrix, threads=4)) as plan:
        matrix.indices[:] = matrix.indices[::-1].copy()
        matrix.sort_indices()
        _force_threads(plan)
        assert np.array_equal(plan.matvec(vector), np.asarray(matrix @ vector, dtype=np.float32))


def test_thread_count_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENVIRONMENT_VARIABLE, raising=False)
    assert configured_threads() == DEFAULT_THREADS
    assert configured_threads(7) == 7
    monkeypatch.setenv(ENVIRONMENT_VARIABLE, "6")
    assert configured_threads() == 6
    monkeypatch.setenv(ENVIRONMENT_VARIABLE, "not-a-number")
    assert configured_threads() == DEFAULT_THREADS, "a bad value must not crash a six-hour run"
    monkeypatch.setenv(ENVIRONMENT_VARIABLE, "0")
    assert configured_threads() == 1


def test_a_worker_exception_surfaces_rather_than_corrupting_output() -> None:
    matrix = _skewed_matrix()
    with _force_threads(SpmvPlan(matrix, threads=4)) as plan, pytest.raises(ValueError):
        plan.matvec(np.ones(matrix.shape[0] + 1, dtype=np.float32))
