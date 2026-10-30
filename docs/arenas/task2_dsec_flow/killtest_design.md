# Task 2 (DSEC-Flow) — kill test registration

Registered 2026-10-01, before any instrument code and before any event or
ground-truth data was seen by anyone on this project. Per the arena
program's operating rules: the trivial alternatives are named here, the
bars are fixed here, and a failed kill test ends the task with a recorded
verdict.

RECONCILIATION NOTE (provenance): a first draft of this registration,
`docs/arenas/task2_dsec/KILL_TEST.md`, was written in the paused session
and swept into the pause commit TRUNCATED mid-sentence in the Arms list
(an interrupted turn whose file write completed anyway; flagged in
HANDOFF.md). This file supersedes it. Sections "Premise under test",
"Claim tier", "Data" and "Pipeline" carry the draft's content; the Arms
list is completed and the pass/kill rule frozen here, still before any
data. The old file and directory are removed in the same commit; the
Task-2 directory is `docs/arenas/task2_dsec_flow/` from here on.

## Premise under test

AD-3 (docs/arenas/ASSUMPTIONS.md): the class-2.5 T4/T5 configuration that
passed its direction-selectivity band (DSI 0.3216, trained flyvis ensemble
parameters, scripts/benchmarks/fc25_visual_ds.py — reused verbatim, no
re-tuning) can recover motion direction from REAL event-camera data better
than trivial alternatives and better than its own degree-preserving rewire.

The repo's nearest measured precedent cuts AGAINST the premise and is
stated up front: on ARC frame-pair displacement (H-T4T5-CLASS25-MOTION,
2026-09-30) the same patch carried real direction signal but its
degree-preserving rewire scored HIGHER (0.4306 vs 0.3875) — the specific
wiring added nothing on that task's statistics. Event-camera input is the
circuit's native statistics in a way ARC frames are not; whether that
changes the null comparison is exactly what this test measures.

## Claim tier available if it passes

Connectome-constrained + physiology-fitted (class 2.5), zero task-trained
parameters on the benchmark. NOT "innate untrained" — frozen-count T4/T5
measured DSI 0.042 and that is pre-declared as unusable for this task.
Expected-tier base rate, stated per the program rule: expected-to-help
claims in this repository are 0 for 12.

## Data (one sequence, not the benchmark)

Primary: one DSEC training sequence with ground-truth forward flow
(train_optical_flow.zip subset + that sequence's events_left). Fallback if
DSEC hosts stay unreachable everywhere: MVSEC indoor_flying1. Either way:
ONE sequence, kill-test only; no benchmark submission artifacts are built
unless every bar passes.

Declared selection and split (fixed before download):

- Sequence: `thun_00_a` if its GT + events are among what the user
  downloads; otherwise the alphabetically first train sequence with both
  forward-flow GT and left-camera events. The choice is logged by the
  harness; it is a convenience, not a knob — no sequence shopping.
- Window cap: the first 250 ground-truth flow windows of the sequence in
  timestamp order (fewer if the sequence is shorter).
- CALIBRATION split: the first 20% of those windows (temporal prefix).
  EVALUATION split: the remainder. Nothing chosen on EVAL ever feeds back.
- Blocked-vs-killed rule: if fewer than 30 EVAL windows survive the
  validity filters below, the run is BLOCKED (instrument/data problem to
  fix and re-run), not a verdict. A verdict requires >= 30 evaluable EVAL
  windows.

## Pipeline under test (plumbing declared)

1. Events -> ON/OFF signed counts at fixed sub-window dt per flow window
   (declared plumbing; dt swept only over the declared set
   {10, 20, 50, 100} ms, same grid for every arm; each arm with any dt
   dependence picks its own dt on the CALIBRATION split by its own mean
   angular error — matched freedom, frozen rule).
2. ASSUMPTION AD-6 (polarity/luminance bridge): the running sum of signed
   event polarities per pixel within a flow window approximates
   log-luminance change (the event-camera generative relation,
   ESTABLISHED qualitatively; using the raw sum as the drive luminance,
   with no contrast threshold constant, is OUR choice). Drive presented
   to the patch = fc2.INPUT_DRIVE * normalized pseudo-luminance on the
   driven types (L1/L2/L3), exactly the fc2/fc25 drive path.
3. ASSUMPTION AD-7 (spatial binning): the CENTRAL SQUARE CROP of the
   frame (480x480 of 640x480) is mapped isotropically onto the patch's
   13x13 input-column lattice (the eye-map-style downsampling; isotropic
   so image direction maps to lattice direction without distortion).
   Per-column pseudo-luminance = mean over the column's pixel block.
   Normalization: divide by the 95th-percentile absolute per-column value
   measured on the CALIBRATION split (one scalar, same for all simulated
   arms; declared plumbing). Evaluation happens at column resolution on
   the 9x9 scored window — this kill test never builds the dense 640x480
   decoder (AD-4 territory, reached only on a pass).
4. Temporal protocol (fc2/fc25 machinery verbatim): settle 2500 ms at
   zero drive (fc2.SETTLE_MS), then stream the window's sub-window drives
   (each held dt_sub), then 750 ms zero-drive tail (fc2.WINDOW_AFTER_S —
   the crossing-window analog for streamed input: the transient is
   allowed to complete; same degeneration rule as the ARC motion arm).
   Evoked per scored T4/T5 cell = max(output - settled output, 0)
   integrated from stream start to tail end. Dynamics:
   fc2.GradedFlyvisNetwork verbatim, dt = 2 ms; fc25 trained_subset
   weights/taus/V_rest and its recorded chosen_gain, no re-tuning
   (asserted from results/benchmarks/fc25_visual_ds.json at run time).
5. ASSUMPTION AD-8 (readout, fixed vector vote — no fitted parameters):
   each T4/T5 subtype votes the preferred direction fc25's own passing
   tiling result measured for it on this patch (read verbatim from the
   results JSON per_subtype table; +x/-x/+y/-y mapped to plane unit
   vectors by fc2.DIR_VECTORS). Per evaluation column: vote vector = sum
   over scored cells of that column of (evoked integral x subtype
   preferred unit vector); direction estimate = atan2 of the vote.
   Design note, stated in advance: any direction-independent DC
   component of the evoked integrals cancels in the vector sum wherever
   opposed subtypes are both present; per-column subtype coverage is
   recorded.
6. Direction, not magnitude (AD-5): driving-scene flow magnitude is not
   claimed. At this binning, typical driving flows (order 10 px per
   100 ms window, 480/13 ~ 37 px per column) land at ~0.3-1.5 columns
   per window ~ 3-15 columns/s — INFERRED to bracket the fc25 passing
   speed band (2.5-10 col/s); the inference is recorded, not relied on.
   The kill metric is 2D ANGULAR ERROR between estimated and
   ground-truth direction. For EPE context only, every direction-only
   arm is scaled by the window's median GT magnitude (identical
   plumbing for all arms, labelled context).

Ground truth per evaluation column: mean GT flow over the column's valid
GT pixels. A column is evaluable iff >= 50% of its pixels carry valid GT
AND the median GT magnitude in the block is >= 2.0 px (direction is
ill-defined near zero flow; threshold declared now). A window is
evaluable iff >= 10 evaluable columns. A window numerically unstable in
ANY simulated arm is dropped from EVERY arm and counted (pairing
preserved, fc2.V_ABORT rule).

## Arms (completed list — the draft truncated here)

- REAL: trained-ensemble class-2.5 patch (fc25 trained_subset passing
  config, verbatim gain), pipeline above.
- TWIN (uniform-tau): trained alphas + trained V_rest, tau 50 ms for
  every type — fc25's own attribution twin, at its own fc25-recorded
  gain. Measures whether temporal heterogeneity does the work.
- NULL (degree-preserving rewire): flygi.connectome.nulls.
  degree_preserving_rewire of the REAL weight matrix, default
  NullOptions, three independent instances (seeds 4242+0,1,2), REAL
  arm's table and gain. Measures whether the specific wiring does the
  work.
- TRIVIAL-1 (zero flow): predicts zero everywhere. No direction exists,
  so it appears in the EPE context table only (the classic base-rate
  entry), not in the angular-error comparison.
- TRIVIAL-2 (GT-median global translation): one direction per window =
  the direction of the median GT flow vector of that window. An oracle
  summary statistic (it reads GT), reported as context for how far a
  single global direction gets; NOT a kill comparator.
- TRIVIAL-3 (EVENT-ARGMAX — kill comparator): circuit-free direction
  from the identical binned input. Per evaluation column: centroid of
  absolute event counts over the 3x3 column neighborhood in the first
  third of the flow window, likewise in the last third; direction
  estimate = the displacement of the centroid. dt-free by construction
  (thirds of the window). This is "event-count argmax" from the
  due-diligence plan, pinned down before any data.
- ENGINEERED (ceiling context): per-window global translation by
  argmax cross-correlation of the first-third vs last-third count
  frames on the lattice (shift range +/-3 columns); ceiling context
  like the ARC taxis matcher, NOT a required beat.
- MultiCM reference: NOT implemented. Its published board EPE (3.472)
  is quoted as external context only.

## PASS / KILL rule (frozen now, before any data)

On the EVALUATION split, per-window mean 2D angular error over evaluable
columns, paired across windows. The fly arm PASSES iff BOTH:

1. REAL beats TRIVIAL-3 (event-argmax): one-sided paired sign test
   across EVAL windows, p < 0.05, AND median per-window mean angular
   error strictly lower.
2. REAL beats NULL: same test against the per-window mean angular error
   of the three rewired instances (averaged per window before pairing),
   p < 0.05, AND median strictly lower.

TWIN, TRIVIAL-2 and ENGINEERED are reported alongside with the same
statistics as attribution/context. If either bar fails, the kill test
FAILS: the recorded verdict is a measured limit of the class-2.5 circuit
on this input (stated at its tier, with the ARC-arm precedent), the task
ends as COMPLETE-with-verdict, and no dense pipeline, no benchmark
account, and no submission artifacts are built. There are no amendments
after data contact; an instrument bug discovered mid-run is fixed and
the full test re-run from scratch, with both runs recorded.

## What this test does NOT decide

- AD-4 (whether a trivial dense decoder suffices for a benchmark entry)
  is reached only on a pass, as its own registered step.
- Benchmark logistics (institutional-email account AD-1, 6-month report
  rule AD-2) are user decisions reached only on a pass.

## Registration and single command

Hypothesis: EXPERIMENTS.yaml `H-T4T5-DSEC-DIRECTION` (registered in the
same commit as this file). Instrument: `scripts/arenas/dsec_killtest.py`
(data-gated; connectome-independent metrics in
`scripts/arenas/dsec_metrics.py`). The one command, run where the data
and the compiled runtime live (the cloud container has neither —
measured, WORKLOG 2026-10-01):

    python scripts/arenas/dsec_killtest.py --data-root <DSEC root>

Runbook for the user's local machine: `runbook.md` in this directory.
