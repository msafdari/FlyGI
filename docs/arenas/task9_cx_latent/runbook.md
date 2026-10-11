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

## Reopening — run these two, PROBE FIRST (instruments of 2026-10-11)

Both registrations were frozen jointly (killtest_design_reopening.md)
before either instrument existed. Run the seeding probe first: its
outcome shapes what the class-3 result means (a probe PASS revives the
class-1 protocol question; a probe KILL makes class-3 the last stand
for CX computation in this program). Nothing to download, no new
packages: the probe uses the compiled graph + cx_ring config you have,
the class-3 test ships its own 2.4 KB validation fixture in-repo.

### 1. H-CX-SEEDING-PROTOCOL (the class-1 seeding probe)

```bash
cd <FlyGI repo root>
git pull
PYTHONPATH=src python -m pytest tests/test_cx_seeding_killtest.py -q   # 13 passed
python scripts/arenas/cx_seeding_killtest.py       # the one command
```

What it does, in order: (1) real arm on all 8 cells — 2 operating
points (gain 1.5 and 2.0, leak 0.3) x 4 protocols (P1 cx_ring-verbatim
reproduction control, P2 100-step write, P3 scale-3.0 write, P4 direct
EPG state injection), each at the calibration angle + 3 held-out
angles with 200-step darkness; (2) the 3 CX-block rewires, only at
real-passing cells; (3) tracking context (Stage-B sequences) at
decisive cells, reported, non-decisional. Cost: the real arms are 8
cells x 4 angles x ~250-350 full-graph steps — on the cx_ring
precedent well under an hour; rewires only add cost if something
passes.

Exit 0 PASS / 1 KILL / 3 BLOCKED, all frozen. Report back
`results/arenas/cx_seeding_killtest.json` (gitignored — paste it)
plus the printed per-cell lines and the branch tip.

### 2. H-CX-CLASS3-COMPASS (the spiking-fidelity kill test)

Run AFTER the probe reports (either outcome).

```bash
cd <FlyGI repo root>
PYTHONPATH=src python -m pytest tests/test_cx_class3_killtest.py -q   # 22 passed (~20 s; includes the Pisokas gate)
python scripts/arenas/cx_class3_killtest.py        # the one command
```

What it does, in order: (1) the in-cloud-validated Pisokas gate runs
again on your machine (the engine must reproduce the published
60-neuron fly bump — mean width 99.0 deg over the declared seeds was
measured in-cloud; a mismatch on your machine is BLOCKED, not a
verdict); (2) extracts the standalone 148-neuron MaleCNS CX, maps
synapse counts through the AC-6 per-class scales (nothing fitted);
(3) per grid point (global scale x {0.5,1,2} crossed with inhibitory
x {1,2}): G1 8-angle continuum/persistence at spiking fidelity (1 s
von Mises write, 2 s darkness) and G2 opposite-signed PEN_a steering;
(4) the 3 degree-preserving rewires of the standalone matrix at every
real-passing point. Cost: 6 grid points x 8 angles x 3 s simulated at
dt 1e-4 on 148 neurons — the in-cloud 60-neuron trials ran ~3.4 s per
simulated 3 s, so expect very roughly 15-40 min for the real arms;
rewires add cost only at passing points.

Exit 0 PASS / 1 KILL / 3 BLOCKED, all frozen. Report back
`results/arenas/cx_class3_killtest.json` (gitignored — paste it) plus
the printed validation-gate lines, per-grid-point lines, and the
branch tip. Interpretation is preregistered: a PASS is the program's
first computation-level wiring win at published-physiology fidelity;
a KILL at the model class where idealized fly topology is published
to work is the strongest statement yet that the compiled counts do
not carry the compass.
