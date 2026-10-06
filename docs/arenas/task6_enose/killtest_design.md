# Task 6 kill test — FROZEN 2026-10-06 (H-ALMB-GASDRIFT)

Registered BEFORE any instrument code, per the operating directive.
Everything here is fixed from this commit on: changes after first data
contact require a recorded instrument-bug finding and a full re-run,
both in the WORKLOG.

## Premise under test

The class-2-validated mushroom body — the real MaleCNS PN/KC/APL
subcircuit at the fc2_kc_sparse-passing configuration (tau_m 20 /
tau_syn 5 / beta 1.0), thresholds and APL balance recalibrated for
this input by the circuit's own Litwin-Kumar procedure — given UCI
gas-drift samples through ONE declared seeded encoder, yields KC
sparse-code features whose linear-probe gas classification on
DRIFT-HELD-OUT batches beats BOTH the identical probe on the raw
sensor features AND the subcircuit's degree-preserving rewire: the
fly's gold-standard modality earning the specific wiring its keep
where vision five times did not.

Scope words: this measures the class-2 MB model on one corpus under
one declared encoder. It is not "the fly's olfaction", and a KILL on
the rewire bar is the ESTABLISHED literature's own expectation for
this circuit (Caron 2013 random convergence; Litwin-Kumar 2017 random
expansion suffices) — stated here so the result cannot be dressed as a
surprise in either direction. The informative content either way: the
circuit-vs-raw bar (which no prior settles) and the per-batch drift
curves (AE-3).

## The dual close (binding, pre-stated)

On KILL: Task 6 closes with no benchmark/community entry, AND the
Task 4 Keyword-FSCIL/MB limb closes as NOT PURSUED (tier INFERRED,
bridge: same AL->KC machinery, native modality, native-form input,
strictly smaller encoder invention — if this fails, the audio limb
has no remaining support; its own hypothesis stays unmeasured, the
limb is closed as not worth its build). On PASS: the limb reopens for
a go/no-go with this result as its prior.

## Data and split

- UCI Gas Sensor Array Drift Dataset (archive.ics.uci.edu dataset
  224; Vergara et al. 2012): batch1.dat..batch10.dat, libsvm-style
  lines, 128 features (16 MOX sensors x 8), gas labels 1-6. Local
  acquisition; the host is egress-blocked in-cloud.
- TRAIN = batch 1 only; TEST = batches 2-10 (drift-held-out by
  construction). Trainable classes = labels with >= 10 TRAIN samples
  in batch 1; evaluation is restricted to those classes everywhere;
  chance = 1/n_trainable.
- Seeded caps, for cost: TRAIN_PER_CLASS = 15; TEST_PER_CLASS_PER_
  BATCH = 6 (SPLIT_SEED = 20261006). All arms see the identical
  sample sets.

## Frozen encoder (AE-1/AE-4, the ONE declared choice, no sweep)

- Per-feature rank-CDF normalization fit on the TRAIN batch only
  (value -> fraction of TRAIN values <= it), applied frozen to every
  batch, clipped to [0, 1]. Drift beyond the train range reaches the
  circuit as saturation — that is the phenomenon under test, not a
  bug.
- ENCODER_SEED = 20261006: one seeded permutation assigns each of the
  128 features to a distinct glomerular type (of the 162); the
  remaining 34 stay at background. Per-glomerulus drive level = the
  feature's normalized value.
- PN rates: rate = RATE_BG + (RATE_ACTIVE - RATE_BG) * level, with the
  fc2_kc_sparse endpoints (5 Hz / 100 Hz) — the binary odor mask is
  the level in {0,1} special case, so the validated drive regime is
  the endpoints of this one.
- Poisson realizations are PAIRED across arms: drive seed =
  (DRIVE_SEED_BASE = 20261008, global sample id), identical for every
  arm.

## Frozen pipeline

- Subcircuit, dynamics, dt (0.1 ms), settle (200 ms), odor window
  (500 ms), w_scale convention, and the run_trial loop: fc2_kc_sparse
  verbatim, with the single generalization from binary member mask to
  continuous per-PN drive levels (equivalence at levels in {0,1}
  asserted by unit test).
- Configuration: tau_m_kc 20 / tau_syn_kc 5 / beta 1.0 (the passing
  config, fixed, not tuned — the mb_association precedent). theta and
  alpha are NOT carried over: both are recalibrated PER ARM on this
  input by the fc2_kc_sparse recipe verbatim (free-potential theta0
  on 2 calibration drives -> open-loop alpha-balance probe ->
  closed-loop theta bisection to TARGET_F = 0.10, CAL_TOL 0.015,
  MAX_BISECT 8), on a seeded CAL_N = 8 subset of TRAIN samples
  (CAL_SEED = 20261009; calibration samples stay in TRAIN for the
  probe — they are input-statistics fodder, not held out). Rewired
  arms calibrate fresh (the flybench-calibrated precedent).
- Features per sample: the 4,064-dim KC spike-count vector over the
  odor window (run_trial's kc_odor_spikes).
- Probe (identical for every arm, the program standard): z-score on
  TRAIN, multinomial logistic L2 (lbfgs), C from (0.01, 0.1, 1, 10)
  by 3-fold CV on TRAIN (CV_SEED = seed of the arm, 0 for
  deterministic arms).
- Primary score per arm = the mean over test batches of per-batch
  accuracy (macro over batches, so late batches weigh equally);
  per-batch accuracies recorded (the drift curve).

## Arms

1. REAL — real subcircuit, own calibration.
2. NULL x3 — degree_preserving_rewire of the full subcircuit matrix,
   seeds REWIRE_SEED_BASE = 4242 + (0, 1, 2), each with its own fresh
   calibration, real config otherwise.
3. RAW (no circuit) — the identical probe on the identical
   rank-normalized 128-feature vectors.
4. SCRAM (context, non-decisional) — the REAL circuit and calibration
   procedure under a second encoder permutation
   (ENCODER_SEED_SCRAM = 20261007). Reported as encoder-invention
   variance; decides nothing.

## Frozen bars — PASS iff ALL hold, else KILL

1. **Above chance**: REAL pooled test accuracy beats 1/n_trainable,
   one-sided exact binomial p < 0.05.
2. **Beats the rewire**: REAL mean-over-batches accuracy > NULL's for
   ALL THREE rewire seeds.
3. **Beats raw features**: REAL mean-over-batches accuracy > RAW's.

No retries, no tuning on a KILL, no second corpus, no second encoder
(SCRAM is context). AE-2 batch artifacts hit all arms identically, so
the internal comparison stands on UCI alone; no outward headline is
built from UCI alone either way.

## BLOCKED (exit 3) — not a verdict

- Any batch file missing/unparseable, a feature count other than 128,
  or fewer than 4 trainable classes / fewer than 150 total test
  samples after caps.
- Calibration misses TARGET_F beyond CAL_TOL (hit_target false) in
  ANY arm — the circuit never received usable input, so no premise
  was tested.
- Simulation exceptions in > 5% of samples in any arm.
- Plumbing fixes before any verdict-relevant quantity are allowed and
  recorded (DVS/Task-5 precedent); bars, arms, caps and the encoder
  are not plumbing.

## Cost declaration

~10 s per sample single-process (extrapolated from the fc2_kc_sparse
sweep rate): ~7-8 h single-process across the 5 simulated arms, ~1 h
at --workers 8. The pool parallelism is decision-neutral: per-sample
drive seeds are fixed and trials are independent given the calibrated
network.

## Expected-tier statement

The base rate is 0 for 15; 0 for 16 would be the count if this fails.
Bar 2's failure is additionally the ESTABLISHED literature's own
prediction for this circuit. The measurements — the drift curves, the
circuit-vs-raw comparison, the calibration facts — publish either way.
