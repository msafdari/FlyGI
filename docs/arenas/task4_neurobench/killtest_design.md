# Task 4 (NeuroBench) — DVS Gesture kill test registration

Registered 2026-10-03, BEFORE any instrument code, with the moved priors
stated in due_diligence_delta.md on the table: T4/T5 has been refuted on
ARC frames and on event-camera driving input since this task was ranked,
with the degree-preserving rewire beating the real wiring three
consecutive times. This test is the cheap decider the program's rules
require before any NeuroBench harness integration is built.

## Premise under test (AN-2, sharpened)

The class-2.5 T4/T5 patch at its fc25-passing configuration (verbatim,
zero re-tuning), driven by binned DVS128 gesture events through the
SAME declared plumbing the DSEC test used, yields population features
from which a linear probe classifies 11 gestures on HELD-OUT SUBJECTS
better than (a) its own degree-preserving rewire and (b) circuit-free
raw event-count features. Differences from the two killed cousins,
stated so the test is not a straw man: classification not per-column
regression; features integrate population dynamics over 250 ms windows;
gesture motions are large and coherent, nearer the fc25-validated speed
band than driving flow was at the DSEC binning.

This test deliberately does NOT use the neurobench package — no new
third-party execution is needed for the kill decision. The harness
integration (their package, their metrics) is built ONLY on a PASS.

## Data (one dataset, its own split; kill-test only)

IBM DVS128 Gesture (DvsGesture.tar.gz, ~2.4 GB; the user downloads from
IBM's official page and accepts their terms — local-side, hosts are
egress-blocked in-cloud). The dataset's OWN subject split files are
used verbatim: trials_to_train.txt / trials_to_test.txt (subjects are
disjoint, so the probe is subject-held-out by construction). The
11-class task includes the "other gestures" class, as shipped.

Frozen scale caps (cost control, seeded, declared now): TRAIN is
subsampled to 40 trials per class (seeded, from the train split only);
TEST is the full test split. BLOCKED (not a verdict) if fewer than 600
train or 150 test trials parse.

## Pipeline (plumbing declared; DSEC machinery reused verbatim where it exists)

1. AEDAT 3.1 polarity events parsed by our own reader (validated
   in-cloud on synthetic packed bytes; coordinate/timestamp sanity
   checks on real data, stats printed). Trial = a labelled
   [startTime, endTime] window from the dataset's label CSVs.
2. Per trial: 6 windows of 250 ms, evenly spaced across the trial
   (frozen; trials shorter than 1.5 s use as many full windows as fit).
   Events binned exactly as the DSEC test binned them
   (dsec_killtest.bin_window_events on the 13x13 lattice; DVS128 is
   128x128 and already square, so the central-crop map is the identity
   crop at 128). Pseudo-luminance = cumulative signed polarity sums at
   a FIXED 10 ms sub-window (the DSEC grid's finest; no dt sweep — one
   fewer knob). Drive normalization: 95th-percentile |end-of-window
   column sum| over a seeded 50-trial calibration subset of TRAIN,
   one scalar shared by every simulated arm.
3. fc2 settle-stream-tail protocol, batched windows as columns: settle
   2500 ms at zero drive once per arm, stream 250 ms, 250 ms zero tail
   (shorter than DSEC's 750 ms — declared; the slowest calibrated tau
   is 200 ms). Features per trial = the 498 scored T4/T5 cells' evoked
   integrals, averaged over the trial's windows.
4. Probe (identical for every arm, the t4t5_motion_arm pattern):
   z-score on TRAIN, multinomial logistic (L2, lbfgs), C from
   (0.01, 0.1, 1.0, 10.0) by 3-fold CV on TRAIN; fit on TRAIN, scored
   on the held-out TEST subjects.

## Arms

- REAL: fc25 trained_subset weights/taus/V_rest, verbatim chosen gain.
- TWIN: uniform-tau with trained strengths, its own fc25 gain.
- NULL: degree-preserving rewire of REAL (flygi.connectome.nulls,
  default options), one instance per seed (4242+seed), REAL table/gain.
- EVENT-COUNT (circuit-free comparator): per window, per lattice
  column, total |event| count and net signed sum (2 x 169 dims),
  averaged over windows — same binning, no circuit. Same probe.
- Seeds 0,1,2: seed the train subsample, the calibration subset, and
  the rewire instance; REAL/TWIN features are recomputed per seed only
  through the (seeded) train subsample — the dynamics are
  deterministic.

## PASS / KILL (frozen now, before any data)

Per seed, per arm: pooled TEST accuracy and per-test-subject accuracy
cells (subjects x seeds = the paired cells). PASS iff ALL THREE:

1. REAL above chance (1/11): one-sided binomial on pooled TEST trials,
   p < 0.05, in ALL three seeds.
2. REAL beats NULL: one-sided paired sign test over subject x seed
   cells, p < 0.05, AND pooled accuracy strictly higher in at least 2
   of 3 seeds (vs that seed's rewire instance).
3. REAL beats EVENT-COUNT: same operationalization.

TWIN is reported as the attribution context (if REAL passes but TWIN
matches it, the pass is not about temporal heterogeneity — reported,
exactly as fc25 framed it). KILL if any bar fails: Task 4's T4/T5 limb
closes as a recorded verdict with no NeuroBench integration built; the
Keyword-FSCIL/MB limb then needs the user's explicit go given ITS moved
priors (delta doc). BLOCKED on the parse floors above or instability in
>20% of any arm's windows. No amendments after data contact; an
instrument bug is fixed and the whole test re-run, both runs recorded.

Expected tier, base rate stated: 0 for 14 would be the count if this
fails; the base rate stands at 0 for 13 and the three nearest
precedents on this circuit are all kills.

## Registration and command

Hypothesis: EXPERIMENTS.yaml `H-T4T5-DVS-GESTURE` (this commit).
Instrument: `scripts/arenas/dvs_killtest.py` (data-gated; pure parts
unit-tested in-cloud). The one command, where the data lives:

    python scripts/arenas/dvs_killtest.py --data-root <DvsGesture dir>
