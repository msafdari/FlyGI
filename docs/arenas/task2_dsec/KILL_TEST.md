# Task 2 (DSEC-Flow) — kill test registration

Registered 2026-10-01, before any instrument code. Per the arena program's
operating rules: the trivial alternatives are named here, the bars are fixed
here, and a failed kill test ends the task with a recorded verdict.

## Premise under test

AD-3 (docs/arenas/ASSUMPTIONS.md): the class-2.5 T4/T5 configuration that
passed its direction-selectivity band (DSI 0.3216, trained flyvis ensemble
parameters, scripts/benchmarks/fc25_visual_ds.py — reused verbatim, no
re-tuning) can recover motion direction from REAL event-camera data better
than trivial alternatives and better than its own degree-preserving rewire.

Claim tier available if it passes: connectome-constrained +
physiology-fitted, zero task-trained parameters on the benchmark. NOT
"innate untrained" — frozen-count T4/T5 measured DSI 0.042 and that is
pre-declared as unusable for this task.

## Data (one sequence, not the benchmark)

Primary: one DSEC training sequence with ground-truth forward flow
(train_optical_flow.zip subset + that sequence's events_left). Fallback if
DSEC hosts stay unreachable everywhere: MVSEC indoor_flying1. Either way:
ONE sequence, kill-test only; no benchmark submission artifacts are built
unless every bar passes.

## Pipeline under test (plumbing declared)

1. Events -> ON/OFF count frames at fixed dt per flow window (declared
   plumbing; dt swept only over a small declared set, same for all arms).
2. Spatial binning onto the patch's columnar lattice (the eye-map-style
   downsampling; declared plumbing — AD-4 says the decoder must stay
   trivial, and the null arm measures whether it carries the result).
3. fc25 passing configuration, unchanged, produces T4a-d/T5a-d responses
   in the crossing-window readout.
4. Fixed vector readout: each subtype votes its preferred direction
   (as measured in fc25's own tiling result); population vector sum per
   column -> direction estimate. No fitted parameters.

## Arms

- REAL: trained-ensemble class-2.5 patch (fc25 passing config).
- NULL: degree-preserving rewired patch, identical pipeline.
- TRIVIAL-1: zero-motion (predicts no direction; scores the base rate).
- TRIVIAL-2: global-translation fit of consecutive ON/OF