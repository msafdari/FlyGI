# Task 5 kill test — FROZEN 2026-10-04 (H-EARLYFILTER-BRAINSCORE-V1)

Registered BEFORE any instrument code, per the operating directive.
Everything in this file is fixed from here on: changes after first
data contact require a recorded instrument-bug finding and a full
re-run, both in the WORKLOG.

## Premise under test

The fc25 class-2.5 patch's EARLY-FILTER population — the 13
INPUT_TYPES (L1–L5, Mi1, Mi4, Mi9, Tm1, Tm2, Tm3, Tm4, Tm9), the one
dynamics-bearing circuit family in this program never yet tested
against its own rewire — driven by static benchmark images through
ONE declared flash-onset convention at the fc25-passing
configuration, yields per-cell evoked-integral features whose V1
neural predictivity (FreemanZiemba2013public.V1-pls, Brain-Score's
own public metric code run verbatim, locally) beats BOTH named
trivial alternatives.

Scope words: this measures the fc25 patch's early-filter population
on one public V1 benchmark under one declared drive convention. It is
not "the fly's early vision", not the full 892-column eye, and not
Brain-Score rank.

## Trivial alternatives (both must lose for a PASS)

1. **Input passthrough** — the per-column driven contrast vector
   itself (the circuit's own input, n_cols dims) fed to the identical
   metric. If the dynamics add nothing to what the encoder already
   hands them, the circuit earns nothing.
2. **Degree-preserving rewire** of the patch weight matrix
   (flygi.connectome.nulls.degree_preserving_rewire), one instance
   per seed, real parameter table and real gain — the control that
   has beaten the real wiring four consecutive times on T4/T5.

Context arm (non-decisional): the uniform-tau TWIN at its own fc25
gain, for the same attribution question DVS answered (does temporal
heterogeneity contribute at all?).

## Frozen pipeline

- **Patch**: fc2.build_patch() verbatim (fc2_visual_ds machinery).
  Config: fc25 trained_subset passing entry read verbatim from
  results/benchmarks/fc25_visual_ds.json (local-only), exactly as the
  DVS test did — real gain, trained table; twin table + twin gain
  from the same file.
- **Scored population**: INPUT_TYPES cells within the central 9x9
  hex window (|h1-19| <= 4 and |h2-20| <= 4, SCORE_HALF = 4 around
  PATCH_CENTER; hex coords inverted from the patch's embedded x, y).
  T4/T5 are excluded from features — they have their four results.
- **Benchmark**: FreemanZiemba2013public.V1-pls, loaded through
  brainscore-vision's public pool ON THE USER'S MACHINE (the package
  install there is the user's own call; AF-6's in-container
  authorization covered flybench only). Their stimuli, their PLS
  metric, their ceiling, their cross-validation — no reimplementation.
- **Drive convention (AB-4, the ONE declared choice, no sweep)**:
  each stimulus image -> grayscale (Rec. 601 luma if RGB) -> resized
  to 128x128 -> per-column mean luminance over the DSEC identity-crop
  pixel assignment (build_lattice / crop_mapping / assign_crop_pixels
  verbatim on the driven cells' coordinates) -> drive value =
  (column mean luma - 0.5), constant for STIM_MS, applied to the
  DRIVEN_TYPES (L1/L2/L3) through INPUT_DRIVE (-1.0, the established
  histaminergic sign). Settle at zero drive (fc2 SETTLE_MS), then
  STIM_MS = 250 ms stimulus, then TAIL_MS = 250 ms zero drive.
  Features = rectified evoked integrals of scored cells over
  stimulus + tail relative to the settled baseline — the DVS feature
  definition with a single constant sub-window.
- **BrainModel adapter (plumbing, declared)**: a minimal precomputed
  wrapper that returns the per-stimulus feature assembly. Two ASSUMED
  choices stated here because something had to be chosen: (a) the
  model declares visual_degrees equal to the benchmark's stimulus
  presentation degrees, so each image fills the patch window exactly;
  (b) whatever time_bins the benchmark requests, the model returns
  the same evoked-integral features for each bin (our integrals are
  not primate-latency-resolved). Neither is swept. The early-filter
  population is hard-assigned to V1 — one mapping, no region search
  (AB-1's auto-select is explicitly NOT used: a search over regions
  is a free parameter).
- **Seeds**: SEEDS = (0, 1, 2); REWIRE_SEED_BASE = 4242 (program
  convention). Real, twin and passthrough are deterministic given the
  benchmark's own CV; the three seeds index rewire instances.

## Frozen bars — PASS iff ALL hold, else KILL

Scores are the benchmark's ceiled center values as their code
reports them (with its error estimate where provided).

1. **Above floor**: real center > 0 AND (center - reported error) > 0
   — nonzero V1 predictivity distinguishable from zero.
2. **Beats the rewire**: real center > rewire center for ALL THREE
   rewire seeds.
3. **Beats passthrough**: real center > input-passthrough center.

The twin decides nothing. No retries, no tuning on a KILL, no second
benchmark. A sub-passthrough or sub-rewire score is a recordable
connectome limit, not an entry: KILL closes the arena with no
BrainModel submission, no website account, and no further Brain-Score
work.

## BLOCKED (exit 3) — not a verdict

- brainscore-vision cannot be installed or imported on the local
  host, or the public benchmark cannot be loaded / its data cannot
  be downloaded there.
- Fewer than MIN_STIMULI = 100 stimuli load from the benchmark.
- More than MAX_UNSTABLE_FRACTION = 20% of simulated presentations
  trip the V_ABORT instability guard in any arm.
- A benchmark/model API mismatch that prevents the metric call.
  Plumbing fixes before any verdict-relevant quantity is computed are
  allowed and recorded (the DVS memory fix is the precedent); the
  bars and arms above are not plumbing.

## Expected-tier statement

PASS would be the program's first dynamics-bearing circuit to beat
its own rewire on an external task, and the first positive on a
cross-phylum mapping. The base rate for expected-tier predictions is
0 for 14; 0 for 15 would be the count if this fails. The measurements
publish either way.
