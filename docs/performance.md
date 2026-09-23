# Performance: how to make this repository fast, and how not to

Read `src/flygi/dynamics/spmv.py` before changing anything here. Its module
docstring carries the numbered gotchas; this file is the decision record and the
operating instructions.

## Where the time goes

The agent is one sparse matvec in a loop. Measured on the deployed graph
(166,700 nodes, 24,994,595 edges, float32) on an Apple M4, 10 cores, 16 GB:

| Implementation | ms/matvec | GB/s | Speedup | Bit-identical |
| --- | ---: | ---: | ---: | --- |
| SciPy CSR, single thread | 54.0 | 3.7 | 1.00x | reference |
| Numba `njit(parallel=True)` | 18.7 | 10.7 | 2.88x | **no** (1.19e-07) |
| **SciPy + threaded row split** | **14.4** | **13.9** | **3.76x** | **yes** |

End to end on a real 120-action game, measured by replay hash:

| `FLYGI_SPMV_THREADS` | wall | speedup | replay hash |
| ---: | ---: | ---: | --- |
| 1 | 24.2 s | 1.00x | `dbf6c507f444cd91` |
| 4 (default) | 10.5 s | 2.31x | `dbf6c507f444cd91` |
| 6 | 10.2 s | 2.37x | `dbf6c507f444cd91` |

End-to-end gain is below the matvec gain because encoding, decoding and the ARC
environment step are serial. That is Amdahl, not a defect.

## The rule that matters

**Bit-identity is a precondition, not a bonus.** Every score in `WORKLOG.md` was
measured with SciPy's single-threaded kernel. An optimisation that changes one
float32 ulp invalidates all of them. Splitting by *rows* keeps each output
element inside SciPy's own kernel in SciPy's own order, so it is exact.
Splitting *within* a row -- which is what a GPU segmented reduction does, and
what Numba's restructured reduction effectively did -- is not.

Any future optimisation must show `np.array_equal` against SciPy on the real
graph, or state loudly in the worklog that baselines need re-measuring.

## Operating instructions

- Default is 4 threads. It buys 3.20x of an available 3.76-3.90x and leaves six
  of ten cores for the other evaluation arms that usually run at the same time.
- `FLYGI_SPMV_THREADS=6` for a single run that owns the machine.
- `FLYGI_SPMV_THREADS=1` to reproduce a pre-optimisation measurement exactly, or
  to debug.
- Running N arms at once, set threads so that `N x threads <= 10`. Oversubscribing
  makes every arm slower; the plateau is shallow past 5, so there is no reason to.

## What was tried and rejected, with the reason

- **Numba.** Slower than threading (2.88x vs 3.76x) *and* not bit-identical.
  Installed, measured, removed. Adding a dependency that is worse on both axes
  would have been indefensible.
- **`csr_matrix(..., copy=False)` for the blocks.** It copies anyway -- measured,
  the block does not share memory with the parent even when every dtype matches.
  This is the dangerous one: it doubles memory and **silently severs in-place
  plasticity**, because the mushroom body writes weights through the parent and
  a copied block never sees them. Learning would appear to run while changing
  nothing. The blocks are built as shells with arrays assigned afterwards, and
  `SpmvPlan.rebuild` raises if they ever stop sharing memory.
- **Splitting on row count.** Neuron degrees are heavily skewed, so equal row
  counts idle most threads: 1.73x versus 2.17x at two threads. Split on
  cumulative nnz.
- **GPU (MPS/Metal).** Not attempted. The operation is bandwidth-bound on a
  unified-memory machine, so the ceiling is similar, and segmented reduction
  would break bit-identity by construction.

## Canaries

- `tests/test_spmv.py` asserts bit-identity across thread counts, that blocks
  are views, and that a bad `FLYGI_SPMV_THREADS` cannot crash a six-hour run.
- The `spmv.plan` telemetry event records thread count and block count on every
  run, so a run that silently fell back to one thread is visible in its log.
- Threading works only because SciPy releases the GIL during `csr_matvec`
  (verified: 2.76x with four Python threads). If a future SciPy stops, this
  file silently serialises and the telemetry event is how you would notice.
