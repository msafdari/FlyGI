"""Threaded sparse matrix-vector product, bit-identical to SciPy's.

The whole agent is one sparse matvec in a loop. Measured on the deployed graph
(166,700 nodes, 24,994,595 edges, float32) on an Apple M4:

    scipy csr, single thread     54.0 ms     3.7 GB/s
    5 threads, nnz-balanced      14.4 ms    13.9 GB/s     3.76x

At K=4 internal steps and 600 actions that is 112 s per evaluation row against
33 s, and roughly 140 minutes of a 75-row matrix against 37.

SciPy's `csr_matvec` is a single-threaded C kernel. Apple's Accelerate, which
NumPy already links for dense BLAS, does not touch it. The operation is
memory-bandwidth-bound -- it streams 200 MB of matrix per call and does two
flops per eight bytes -- so the fix is to use more of the machine's bandwidth,
not to compute differently.

WHY THIS IS EXACT, WHICH IS THE POINT
-------------------------------------
Every output element `y[i]` is the dot product of row `i` with `x`. Splitting
the matrix **by rows** gives each thread a disjoint set of output elements, and
each one is computed by SciPy's own kernel in SciPy's own order. Float32
addition is not associative, so order is the whole ballgame -- and this
preserves it exactly. `np.array_equal(threaded, scipy)` holds, and the test
suite asserts it.

This is why the obvious alternatives were rejected after measurement:

- **Numba `prange`**: 18.7 ms (2.88x), and **not** bit-identical -- max
  absolute difference 1.19e-07, one float32 ulp, because LLVM restructures the
  reduction. Slower than threading *and* it changes results, which would have
  forced every baseline in the worklog to be re-measured. Rejected, and the
  dependency removed again.
- **GPU / segmented reduction**: splitting *within* a row across lanes changes
  accumulation order by construction. Not attempted for that reason.

GOTCHAS, ALL OF WHICH BIT SOMETHING HERE
----------------------------------------
1. **Split on cumulative nnz, never on row count.** Neuron degrees are heavily
   skewed, so equal row counts leave threads idle: measured 2.17x versus 1.73x
   at two threads, 3.76x versus 2.76x at five. `np.searchsorted` on `indptr`
   costs nothing and recovers most of the gap.
2. **The blocks are views, not copies.** They slice `data`, `indices` and
   `indptr` directly, so the 200 MB matrix is not duplicated. Building blocks
   with `W[a:b]` instead would copy it.
3. **`csr_matrix(..., copy=False)` copies anyway.** Measured: the block does
   not share memory with the parent even when every dtype matches. Using it
   would double the 200 MB matrix and silently sever in-place plasticity -- the
   mushroom body writes weights through the parent, and a copied block never
   sees them, so learning would appear to run while changing nothing. The
   blocks are therefore built as empty shells with the arrays assigned
   afterwards, and `rebuild` raises if they ever stop sharing memory.
4. **Do not change topology after building blocks.** The views alias the
   parent arrays, so a weight edit is visible to the blocks -- which is correct
   and intended for plasticity -- but a *structural* change (different indptr,
   re-sorted indices, a rewire) invalidates them. `SpmvPlan.rebuild()` exists
   for that; the rate network calls it when topology changes.
5. **More threads is not better across processes.** The plateau is ~5-6 threads
   on ten cores, and several evaluation arms usually run at once. Each process
   taking ten threads oversubscribes and makes every arm slower. The default is
   deliberately modest; `FLYGI_SPMV_THREADS` overrides it for a single run that
   wants the machine to itself.
6. **Threads help only because SciPy releases the GIL.** Verified here: four
   Python threads give 2.76x on the real matrix. If a future SciPy stopped
   releasing it this file would silently serialize, so the benchmark in
   `scripts/benchmark_runtime.py` is the canary.
7. **One thread is not zero threads.** With `threads=1` the plan calls SciPy
   directly and allocates no pool, so nothing regresses on a small matrix or a
   single-core box.
"""

from __future__ import annotations

import itertools
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

ENVIRONMENT_VARIABLE = "FLYGI_SPMV_THREADS"

# ASSUMPTION: four threads is the right default. Measured speedup at four is
# 3.20x against a plateau of 3.76-3.90x, so it buys most of the available gain
# while leaving six of ten cores for the other evaluation arms that are
# routinely running at the same time. A single run that owns the machine should
# set FLYGI_SPMV_THREADS=6. This is a throughput choice, not a physics one.
DEFAULT_THREADS = 4

# Below this, threading costs more than it saves: the pool dispatch is tens of
# microseconds and a small matvec is faster than that.
MINIMUM_NNZ_FOR_THREADS = 2_000_000


def configured_threads(requested: int | None = None) -> int:
    """Resolve the thread count from the argument, the environment, or the default."""

    if requested is not None:
        return max(1, int(requested))
    raw = os.environ.get(ENVIRONMENT_VARIABLE)
    if raw:
        try:
            return max(1, int(raw))
        except ValueError:
            return DEFAULT_THREADS
    return DEFAULT_THREADS


class SpmvPlan:
    """A reusable row partition of one CSR matrix, and its thread pool."""

    def __init__(self, matrix: sparse.csr_matrix, *, threads: int | None = None) -> None:
        if not sparse.isspmatrix_csr(matrix):
            raise TypeError("SpmvPlan requires a CSR matrix")
        self._matrix = matrix
        self._threads = configured_threads(threads)
        self._executor: ThreadPoolExecutor | None = None
        self._blocks: list[sparse.csr_matrix] = []
        self._bounds: NDArray[np.int64] = np.asarray([0, matrix.shape[0]], dtype=np.int64)
        self.rebuild()

    # -- structure ---------------------------------------------------------
    def rebuild(self) -> None:
        """Rebuild the row partition. Call after any change to topology."""

        self.close()
        matrix = self._matrix
        rows = int(matrix.shape[0])
        if self._threads <= 1 or matrix.nnz < MINIMUM_NNZ_FOR_THREADS or rows < 2:
            self._blocks = []
            self._bounds = np.asarray([0, rows], dtype=np.int64)
            return

        # Balance on cumulative nonzeros, not on row count: see gotcha 1.
        indptr = matrix.indptr
        targets = np.linspace(0, matrix.nnz, self._threads + 1)
        bounds = np.searchsorted(indptr, targets).astype(np.int64)
        bounds[0], bounds[-1] = 0, rows
        bounds = np.unique(np.clip(bounds, 0, rows))
        if bounds.size < 3:
            self._blocks = []
            self._bounds = np.asarray([0, rows], dtype=np.int64)
            return

        blocks = []
        for start, stop in itertools.pairwise(bounds):
            first, last = int(indptr[start]), int(indptr[stop])
            # Views into the parent arrays: see gotcha 2.
            #
            # The obvious construction -- csr_matrix((data, indices, indptr),
            # copy=False) -- COPIES ANYWAY. Measured: the resulting block does
            # not share memory with the parent even though every dtype already
            # matches. That would double the 200 MB matrix and, far worse,
            # silently sever in-place plasticity: the mushroom body writes
            # weights through the parent, and a copied block would never see
            # them, so learning would appear to run while changing nothing.
            #
            # Building an empty shell and assigning the arrays skips the
            # validation path that copies. `indptr` is necessarily a fresh array
            # because it must be rebased, but it is small; `data` and `indices`
            # are the large ones and they stay views.
            block = sparse.csr_matrix((int(stop - start), int(matrix.shape[1])), dtype=matrix.dtype)
            block.data = matrix.data[first:last]
            block.indices = matrix.indices[first:last]
            block.indptr = indptr[start : stop + 1] - first
            if not np.shares_memory(block.data, matrix.data):
                # Fail loudly rather than silently disabling plasticity. If a
                # future SciPy copies here too, this is the canary.
                raise RuntimeError(
                    "SpmvPlan blocks no longer share memory with the parent matrix; "
                    "in-place weight updates would not reach the matvec. Refusing to "
                    "run rather than silently breaking plasticity."
                )
            blocks.append(block)
        self._blocks = blocks
        self._bounds = bounds
        self._executor = ThreadPoolExecutor(
            max_workers=len(blocks), thread_name_prefix="flygi-spmv"
        )

    def close(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=False)
            self._executor = None

    # -- use ---------------------------------------------------------------
    @property
    def threads(self) -> int:
        return len(self._blocks) if self._blocks else 1

    def matvec(self, vector: NDArray[np.floating]) -> NDArray[np.float32]:
        """Compute ``matrix @ vector``, bit-identically to SciPy."""

        if not self._blocks or self._executor is None:
            return np.asarray(self._matrix @ vector, dtype=np.float32)
        out = np.empty(self._matrix.shape[0], dtype=np.float32)
        blocks, bounds = self._blocks, self._bounds

        def run(index: int) -> None:
            out[bounds[index] : bounds[index + 1]] = blocks[index] @ vector

        # list() forces every future, so an exception in a worker surfaces here
        # rather than being swallowed and leaving `out` partly written.
        list(self._executor.map(run, range(len(blocks))))
        return out

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "threaded_row_split_csr",
            "threads": self.threads,
            "requested_threads": self._threads,
            "blocks": len(self._blocks),
            "nnz": int(self._matrix.nnz),
            "rows": int(self._matrix.shape[0]),
            "balanced_on": "cumulative_nnz",
            "bit_identical_to_scipy": True,
            "threshold_nnz": MINIMUM_NNZ_FOR_THREADS,
            "environment_variable": ENVIRONMENT_VARIABLE,
        }

    def __enter__(self) -> SpmvPlan:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
