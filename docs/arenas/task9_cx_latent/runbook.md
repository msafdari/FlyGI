# Task 9 — CX latent-state runbooks (user-executed)

Stage A is ready to run; Stage B's instrument builds only after a
Stage-A PASS (both registrations are already frozen in
killtest_design.md, including the dated pre-data-contact amendment of
the Stage-A shifter statistic, which the synthetic validation forced
and measured).

## Stage A — H-CX-RING-TOPOLOGY (structural; ready now)

Nothing to download and no new packages: the probe needs only the
compiled runtime your machine already has.

```bash
cd <FlyGI repo root>
git pull
python scripts/arenas/cx_topology_killtest.py     # expect BLOCKED in a
                                                  # container without the
                                                  # runtime; runs locally
PYTHONPATH=src python -m pytest tests/test_cx_topology_killtest.py -q  # 8 passed
python scripts/arenas/cx_topology_killtest.py     # the one command
```

Expected cost: seconds for the real metrics, a few minutes for the
200 rewired nulls of the 148-neuron subcircuit. Exit 0 PASS / 1 KILL
/ 3 BLOCKED, all frozen; no retries, no tuning.

Report back `results/arenas/cx_topology_killtest.json` (gitignored —
paste it), plus the one "real:" line the run prints (bandedness,
argmax offsets, mirror-peaks, spectral residual) and the wedge
coverage numbers.

## Stage B — H-CX-HEADING-LATENT (gated)

On a Stage-A PASS, the Stage-B instrument is built against the frozen
registration (continuum + tracking at gain 1.5 / leak 0.3, full
graph, CX-block rewires x3) and this runbook gains its Stage-B
section. On a Stage-A KILL, Task 9 ends with no dynamics built and
H-CX-HEADING-LATENT closes not-pursued.
