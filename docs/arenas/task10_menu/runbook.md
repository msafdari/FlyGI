# Task 10 runbook — the science menu (user-executed, local)

> **STATUS 2026-10-30.** Sections 1, 2, 4, 6 and 7 EXECUTED 2026-10-28/29
> (reservoir FLAT — downgrade executed; decomposition readings complete;
> FB PASS; t4t5 class-3 BLOCKED-closed "null"; SFA KILL + terminal PASS;
> records in EXPERIMENTS.yaml + WORKLOG). Section 5 ran once and BLOCKED at
> its G0 gate; the instrument bug is FIXED (587b40d) and **section 5b is the
> one command still to run**. Section 3 (Biswas) completed its fetch; the
> instrument awaits the Methods extraction. Everything below is otherwise a
> historical record.

Registrations: killtest_design.md (frozen 2026-10-23, one commit,
before any instrument code). Run order matters only for item 1:
**run the reservoir control FIRST, before the 2026-11-01 release**,
because its FLAT outcome changes release prose. Everything else can
run in any order, any time. Every instrument BLOCKS (exit 3) rather
than guessing when something it needs is missing. Paste back each
JSON (all are gitignored) plus the printed lines and the branch tip.

## 0. Once per machine

```bash
cd <FlyGI repo root>
git pull
PYTHONPATH=src python -m pytest tests/test_stagea_nulls2.py -q   # 11 passed
```

## 1. H-ARC-HARNESS-SENSITIVITY — reservoir positive control (BEFORE the release)

No new instrument: this launches machinery you already have. The
bundle was built 2026-09-22; if `data/processed/male-cns-v1.0/
literal-rate-signed/reservoirs/edge_of_chaos/seed-20260922` is
missing, rebuild with `uv run flygi graph reservoirs` (~2 min).

```bash
uv run python scripts/evaluate_connectome.py \
  --config configs/literal_rate_signed.yaml \
  --runtime-dir data/processed/male-cns-v1.0/literal-rate-signed/reservoirs/edge_of_chaos/seed-20260922 \
  --condition reservoir-positive-control \
  --seeds 0 1 2 --games all --action-budget 500
# context arm (the control's dumb twin):
uv run python scripts/evaluate_connectome.py \
  --config configs/literal_rate_signed.yaml \
  --runtime-dir data/processed/male-cns-v1.0/literal-rate-signed/reservoirs/matched_random/seed-20260922 \
  --condition reservoir-matched-random \
  --seeds 0 1 2 --games all --action-budget 500
uv run python scripts/league.py --write-md LEAGUE.md
```

Cost: the real graph ran ~0.148 s/action; 75 rows x 500 actions is
roughly a long afternoon per arm (A-RES-3: untimed assumption — if it
is much slower, say so and we re-plan). Both conditions are already
registered in EXPERIMENTS.yaml (regime gain0.9-dead for the league's
cross-regime rule; the note records the reservoir is dynamically
ALIVE there). Report: the two new LEAGUE.md rows and their CIs vs
eff-real-signed and eff-null-degree-preserving. The frozen readings
(CERTIFIED / DETECTS-BUT-HURTS / FLAT) are in killtest_design.md §1 —
on FLAT, the release prose edits listed there happen BEFORE 11-01.

## 2. H-STAGEA-NULL-DECOMPOSITION — second null family on Stage A

```bash
PYTHONPATH=src python -m pytest tests/test_stagea_nulls2.py -q   # 11 passed
python scripts/arenas/cx_topology_nulls2.py       # the one command
```

Cost: Stage A ran 30.6 s at 200 rewires; the shuffles are cheaper
generators on the same 148-neuron subcircuit — expect ~1-3 min for
all three families (600 nulls total). Exit 0 = readings complete
(this instrument has no KILL: refinement, never a reopening). Report
results/arenas/cx_topology_nulls2.json — the decomposition readings
per family.

## 3. H-CX-BISWAS-FITTED — fetch first (cloud cannot reach the hosts)

Fetch these three locally (do NOT commit the PDFs; we extract a small
reviewed provenance file of the parameter tables afterwards):

1. bioRxiv 10.1101/2024.11.01.621596 — full PDF + supplementary
   material (check for a published 2026 version; alternate:
   par.nsf.gov/servlets/purl/10609135).
2. bioRxiv 10.64898/2026.05.18.725766 (the 2026 follow-up — the
   MaleCNS realizations may live here).
3. Duan, Dong & Fiete — bioRxiv 10.1101/2025.05.26.655406 + NeurIPS
   2025 poster 115017 page (for the necessity claim and any code
   link).

Then either paste the MaleCNS parameter tables (or the derivation
recipe) into the session, or drop the files somewhere local and tell
me the paths — the numeric completion of the registration lands as a
dated addendum, and only then does the instrument get built.

## 4-7. Remaining instruments

Sections appended when each instrument lands (FB structural probe,
class-3 T4/T5, naturalistic statistics, FlyBench SFA/terminal). The
naturalistic-statistics run additionally needs a small natural-image
corpus fetched locally (van Hateren subset; the instrument's BLOCKED
message names exactly what and where).

## 4. H-FB-COLUMNAR-TOPOLOGY — the fan-shaped-body structural probe

```bash
PYTHONPATH=src python -m pytest tests/test_fb_topology_killtest.py -q   # 14 passed
python scripts/arenas/fb_topology_killtest.py      # the one command
```

What it does, in order: (1) re-runs the synthetic Hulse-motif gate at
the frozen 200 nulls on your machine (ideal must PASS both bars at the
floor, its rewire must KILL both — a gate failure is BLOCKED, nothing
runs); (2) extracts the ~1,399-neuron FB columnar subcircuit and
checks the frozen composition table + 0.90 column/glomerulus coverage;
(3) Bar 1 (hDelta antipode mass) and Bar 2 (PFN L/R mirror via the
verbatim Stage-A mirror_peak) against 200 degree-preserving rewires,
seeds 4242+0..199. Cost: Stage A's 148-node run took 30.6 s; this
subcircuit is ~9x larger, so expect minutes to a few tens of minutes
(the in-cloud gate at 200 nulls also runs first and is included).
Exit 0 PASS / 1 KILL / 3 BLOCKED. Report
results/arenas/fb_topology_killtest.json + the printed real/floor
lines; on first contact also eyeball the reported column_counts
against FC 9 / hDelta 12 / vDelta 10 (AC-FB1).

## 5. H-T4T5-NATSTAT-DIRECTION — naturalistic statistics (needs a tiny corpus)

One-time corpus fetch (keep OUTSIDE the repo tree; nothing gets
committed or redistributed): the van Hateren IML set, files
imk00001.iml .. imk00060.iml (the frozen OP-1 list), into some
directory <CORPUS>. The instrument sha256-pins what it reads and
BLOCKS on any mismatch; --sintel-root is the declared fallback.
It also needs your local results/benchmarks/fc25_visual_ds.json
(the Task-4-era fc25 run) for the G0 gate and the AD-8 readout.

```bash
PYTHONPATH=src python -m pytest tests/test_natstat_killtest.py -q   # 32 passed at first run; 36 after the 5b fix
python scripts/arenas/natstat_killtest.py --image-root <CORPUS>
```

What it does, in order: (1) run-time scramble-integrity selftest;
(2) G0 — fc25's own moving-edge result must reproduce through the new
stimulus path (DSI within +/-0.02 of 0.3216, exact subtype tiling) —
BLOCKED otherwise; (3) G1 — real wiring on natural movies must beat
the 90-deg chance floor (usable input) — BLOCKED otherwise; (4) the
2x2: {real, 3 rewires} x {natural, phase-scrambled}, 8 directions x 3
speeds, AD-8 vector vote, bars B1 (real beats rewires on natural) and
B2 (the gap needs the natural statistics). Cost: 8 simulated
arm-conditions x 60 images x 24 (direction,speed) items at fc25's
dt 2 ms — this is the heaviest run of the menu; expect hours (the
fc25 precedent and your machine decide; the JSON reports per-arm
timing). Exit 0 PASS / 1 KILL / 3 BLOCKED. Report
results/arenas/natstat_killtest.json.

## 6. H-T4T5-CLASS3-DS — class-3 spiking physiology on T4/T5

```bash
PYTHONPATH=src python -m pytest tests/test_t4t5_class3_killtest.py -q   # 27 passed (~100 s; gate A runs inside)
python scripts/arenas/t4t5_class3_killtest.py      # the one command
```

What it does, in order: (1) GATE A on your machine — the idealized
spiking delay-line correlator must express DS (median DSI >= 0.30,
TF optimum at the interior 1 Hz point) and collapse (< 0.05) with
equalized arms; failure = BLOCKED, a measured absence statement about
the spiking model class, never a fly verdict (in-cloud it passed:
DSI 1.0000, optimum 1.0 Hz, collapse 0.0000). (2) GATE B — patch dims
(2,701/507/498/169) + the fc25 reference reproducing within +/-0.02
of 0.3216. (3) Calibration (18 gains x 2 polarities — the dominant
cost), then the 3-point grid on the real patch, Maisak band per
point; (4) the 3 rewires at real-passing points only; (5) uniform-tau
twin + Shiu-mapping context arms (non-decisional). Expect roughly
1-2 h locally. Exit 0 PASS / 1 KILL / 3 BLOCKED. Report
results/arenas/t4t5_class3_killtest.json + the printed gate and
per-grid-point lines. The build-time operationalizations R1-R6 are
recorded as a dated pre-data-contact note in killtest_design.md.

## 7. H-FLYGI-FLYBENCH-SFA and -TERMINAL — the two FlyBench mechanisms

```bash
PYTHONPATH=src python -m pytest tests/test_flybench_mechanisms.py -q   # 19 passed (~150 s; toy-suite gates run inside)
# SFA arm:
PYTHONPATH=src:scripts/arenas flybench run -c malecns_minecraft \
  --simulator flygi_flybench_adapter:FlyGISFAAdapter
python scripts/arenas/flybench_mechanisms_verdict.py --mechanism sfa \
  results/arenas/<your stored uniform baseline>.json <the new SFA run>.json
# Terminal arm (point the env var at flybench's shipped table):
export FLYGI_TERMINAL_TABLE=<flybench clone>/data/terminal/malecns_terminal.csv.gz
PYTHONPATH=src:scripts/arenas flybench run -c malecns_minecraft \
  --simulator flygi_flybench_adapter:FlyGITerminalAdapter
python scripts/arenas/flybench_mechanisms_verdict.py --mechanism terminal \
  results/arenas/<uniform baseline>.json <the new terminal run>.json
```

Notes: the verdict script blocks unless the stored uniform baseline
records n_neurons 176,422 (like-for-like floor); each adapter writes a
mechanism sidecar the verdict script reads (its --list-checks prints
every bar and floor); mechanisms are evaluated ONE AT A TIME (a
combined arm, if you want it afterwards, is reported non-decisionally
only if both singles pass). Cost per arm ~ the Task-3 uniform run you
already did (3 seeds + rewired control). Report both verdict-script
outputs verbatim.

## Suggested overall order

1 (reservoir, BEFORE the release) -> 2 (nulls2, minutes) -> 4 (FB,
minutes-to-tens) -> 7 (SFA then terminal) -> 6 (t4t5 class 3, 1-2 h)
-> 5 (natstat, heaviest, needs the corpus) -> 3 (Biswas, after you
fetch the papers). Any order after item 1 is fine; nothing depends on
anything else's outcome.

## 5b. Natstat RE-RUN (after the 2026-10-29 OFF-edge fix)

The first run's G0 block is explained and fixed (instrument-bug
finding in killtest_design.md; drive boundary now reconstructs
absolute luminance). Pull, then repeat section 5 verbatim:

```bash
git pull
PYTHONPATH=src python -m pytest tests/test_natstat_killtest.py -q   # 36 passed
python scripts/arenas/natstat_killtest.py --image-root <CORPUS>
```

Everything else (corpus, checksums, flags) is unchanged; the frozen
full-re-run rule applies, so the whole protocol runs fresh.

## 5c. Natstat THIRD run (after the 2026-10-31 tie-aware G0 amendment)

Second run confirmed the luminance fix (0.1763 -> 0.3355, in band);
the residual G0 failure was a 0.2% argmax tie on T5a, ruled a gate-
operationalization defect and amended (tie-aware tiling, margin 0.98
from the measured residual bound; killtest_design.md). Same single
command:

```bash
git pull
PYTHONPATH=src python -m pytest tests/test_natstat_killtest.py -q   # 36 passed
python scripts/arenas/natstat_killtest.py --image-root <CORPUS>
```

Include the JSON's g1 block in the report either way: if G0 passes
and G1 still fails, the pre-stated close applies (AB-4 convention
limit, BLOCKED, ANS-5 negative) and no further natstat run follows.
