# Task 9 — CX latent-state runbooks (user-executed)

> **Task 9 CLOSED at every registered level (2026-10-11).** Stage A
> SUPPORTED (H-CX-RING-TOPOLOGY, the series' first PASS); Stage B
> H-CX-HEADING-LATENT closed "null" (BLOCKED at the AC-2 precheck);
> the reopening probe and the class-3 test below were both run
> locally the same day and both KILLED (H-CX-SEEDING-PROTOCOL and
> H-CX-CLASS3-COMPASS refuted; the class-3 validation gate passed on
> the verdict machine first). Every command below was executed.
> Records: EXPERIMENTS.yaml, WORKLOG eeb75b5 + the close entry,
> SYNTHESIS second Task-9 addendum, HANDOFF row 9. This file is a
> historical record; nothing in it is awaiting a run.
>
> 2026-11-21: every outcome above was measured on a label map that
> reflected the left half-ring, so "the series' first PASS" is the
> history of the series. Under the corrected map Stage A passed again on
> 2026-11-21 (bandedness 0.8505 vs a null maximum of 0.3342), Stage B
> was BLOCKED again, and the probe and class 3 were KILLED again (see the
> RE-RUN section at the end and the amendment).

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

## RE-RUN under the amended label map (2026-11-21)

> The banner at the top of this file is the 2026-10-11 state. Every
> outcome it lists was measured with the AC-1 label map, which
> reflected the left half-ring (instrument-bug finding of 2026-11-21,
> `docs/arenas/compass_map_amendment_20261121.md`). Stage A is re-run
> once, in full, with only the label map changed. Stage B, the probe
> and class 3 are re-run the same way ONLY if Stage A is PASS under
> the amended map. The registered-map outcomes stay in the record as
> history.

Unit tests first, then the instruments in the registered order, each
through the once-only wrapper. The default map is the amended one.
Each run writes `results/arenas/<name>.amended_map.json` and its log,
plus a console record under `results/arenas/amended_runs_20261121/`,
and leaves the 2026-10-10 and 2026-10-11 result files alone.

```bash
PYTHONPATH=src python -m pytest tests/test_compass_map.py \
    tests/test_cx_topology_killtest.py tests/test_cx_heading_killtest.py \
    tests/test_cx_seeding_killtest.py tests/test_cx_class3_killtest.py \
    tests/test_run_amended_once.py -q
scripts/arenas/run_amended_once.sh scripts/arenas/cx_topology_killtest.py
# the next three ONLY on a Stage-A PASS (the wrapper refuses them otherwise)
scripts/arenas/run_amended_once.sh scripts/arenas/cx_heading_killtest.py
scripts/arenas/run_amended_once.sh scripts/arenas/cx_seeding_killtest.py
scripts/arenas/run_amended_once.sh scripts/arenas/cx_class3_killtest.py
```

Launch each run detached, in a session of its own, for example as

```bash
nohup perl -MPOSIX -e 'fork and exit; POSIX::setsid() > 0 or die "setsid: $!"; exec @ARGV or die "exec: $!"' \
    <command> >/dev/null 2>&1 &
```

and check `results/arenas/amended_runs_20261121/launch.log` for its start:
a refusal is written there with its reason. Start the next only after
this one's record ends in its `# CLASSIFICATION` line or, if its wrapper
died, after its instrument has exited and the record has been classified
by decision 7's ordered tests (then remove the stale lock by hand). The
wrapper holds a lock for the whole run. Stopping a run before the
instrument finishes, by TERM to the wrapper or to the instrument, by INT
to the wrapper or by HUP (INT and HUP only where the launch does not
ignore them), is recorded as abandoned; a SIGKILL or any other signal
that kills the instrument is recorded as a failure to finish. The
instrument itself ignores INT and QUIT, and HUP under this launch. The probe takes about 7.5 minutes and
class 3 about 16.5 on this machine (the registered-path reproductions
of amendment section 11).

To reproduce a registered run instead, call the script directly with
`--ring-map registered` (writes `<name>.registered_map.json`). All
four were run that way before the freeze of 2026-11-21 and compared
with their registered records (amendment section 11).

Between runs: hash the run's console record, JSON and log (each where it
exists) into WORKLOG.md with the printed result lines, and commit that
file alone (`[skip ci]`) before the next run. The wrapper refuses to start
if any other tracked file differs from the tag
`compass-map-freeze-20261121`. It accepts only the amendment's eleven
commands, with no other argument, and names each record after its
instrument. A failure to finish (a crash, a watchdog kill or a resource
stop) earns one re-run of the same command, with `--rerun` before the
script, as the next launch: the wrapper refuses any other first attempt
until it is made, and a failure that is not re-run is read as two.
Stopping a run before the instrument finishes, as above, is recorded as
abandoned, with no re-run (a SIGKILL of the instrument is a failure to
finish); anything more is refused. It also refuses to start unless
the compiled runtime, the raw MaleCNS pair table and the capture file
match the SHA-256 values pinned in
`scripts/arenas/run_amended_once.inputs.sha256` (amendment section 7,
decision 7).

Read the printed VERDICT or BLOCKED line and the JSON where one is
written, not the exit status alone: an uncaught exception also exits 1.
The pre-stated reading of every outcome is in section 10 of the
amendment. If Stage B passes its
precheck it builds three rewired full networks: `cx_block_rewire` was
measured on the real graph on 2026-11-21 at 3.9 s and 2.38 GB peak per
call.
