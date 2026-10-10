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

## Stage B — H-CX-HEADING-LATENT (ready; Stage A PASSED 2026-10-10)

Stage A passed (bandedness 0.588 vs null max 0.338; mirror-peak
0.0145 vs 0.0079; both p 0.005 at 200 nulls — the arena series' first
PASS), so the Stage-B instrument is built against its registration,
which was frozen in the same commit as Stage A's and was not touched
after the PASS. Again nothing to download and no new packages — the
full compiled graph and cx_ring's config are what your machine
already has.

```bash
cd <FlyGI repo root>
git pull
PYTHONPATH=src python -m pytest tests/test_cx_heading_killtest.py -q  # 7 passed
python scripts/arenas/cx_heading_killtest.py      # the one command
```

What it does, in order: (1) PRECHECK — seeds the calibration angle
(22.5 deg) at gain 1.5 / leak 0.3 and requires the measured
persistence to reproduce (retention >= 0.05, circvar <= 0.6 after the
200-step darkness); BLOCKED if not (AC-2), and BLOCKED too if the
calibrated left/right rotation rates come back same-signed or below
0.05 deg/step (an instrument-level guard, labeled in the docstring:
no signed rate basis = no defined command integral). (2) Builds the
three CX-block rewired graphs (the 148x148 block only, rest intact).
(3) Per arm: darkness continuum on the three held-out angles, then
the three preregistered command sequences, decoded against the
command integral under the real arm's calibrated rates. Order an
hour on the cx_ring precedent (full-graph advances; the three rewired
networks dominate the cost).

Exit 0 PASS / 1 KILL / 3 BLOCKED, all frozen. Report back
`results/arenas/cx_heading_killtest.json` (gitignored — paste it),
plus the printed precheck, calibrated-rates, per-arm continuum and
tracking lines, and the branch tip if you committed a fix. On PASS,
the program has its scoped heading-latent claim (AC-3: never "a world
model of the physical environment"); on KILL, the structure exists
but does not compute a heading latent at this fidelity and regime —
either way the close propagates to the registry, HANDOFF, and
SYNTHESIS.
