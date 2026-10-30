# Task 4 (NeuroBench) — due-diligence delta check, 2026-10-03

Opened per operating rule 1, immediately after Task 3 closed with its
verdict. Base: the 2026-09-30 survey (due_diligence_20260930.md,
`neurobench`) and PLAN.md's Task-4 section. Everything below is MEASURED
in this session unless tiered otherwise.

## Measured environment deltas

1. **neurobench IS on PyPI** (unlike flybench): v2.3.0, requires
   Python >=3.10. Its dependency set is heavy and torch-shaped
   (pytorch-lightning <2.0, snntorch, numba/llvmlite, jitcdde, gdown) —
   an install is a real environment commitment, and `gdown` implies
   Google-Drive-hosted assets.
2. **neurobench.ai is egress-blocked** from this container (HTTP 000;
   consistent with P-2).
3. **Dataset hosts look blocked too**: research.ibm.com and dropbox.com
   HTTP 000 (DVS Gesture's usual homes); drive.google.com was already
   measured 000 (2026-10-01), which also covers gdown. One S3 endpoint
   answered 403 at the bucket root (normal for S3; object-level access
   untested). Expectation, stated at tier (inferred): dataset
   acquisition is local-side, as it was for DSEC and MaleCNS.
4. Third-party-execution note: the user's in-container authorization
   was given in the flybench context (AF-6). Installing/running the
   neurobench harness in-cloud is a NEW third-party execution and waits
   on the same explicit nod (or runs local). Reading sources needs no
   authorization.

## The moved priors (the important delta — measured in THIS repo since the survey)

The 2026-09-30 survey ranked Task 4's DVS Gesture angle as a "native
T4/T5 fit". Since then, this program measured:

- **H-T4T5-CLASS25-MOTION refuted** (2026-09-30): on real ARC frame
  pairs, the degree-preserving rewire beat the real wiring (0.4306 vs
  0.3875); the uniform-tau twin matched it.
- **H-T4T5-DSEC-DIRECTION refuted** (2026-10-02): on REAL EVENT-CAMERA
  input — the same input modality DVS Gesture uses — every arm sat near
  chance for per-column direction, and the rewire again beat the real
  wiring (78.85° vs 81.36° median AE).
- **H-FLYGI-FLYBENCH-CALIBRATED refuted** (2026-10-03): biological
  calibration moved the activation checks +0.0002 against a +0.02 bar.
- The rewire-beats-real pattern now has THREE consecutive datapoints,
  and the expected-tier base rate is 0 for 13.

Consequence, stated plainly: Task 4's headline premise ("T4/T5
population + linear readout classifies DVS gestures above its controls",
AN-2) is a close cousin of two freshly killed hypotheses on the same
circuit, one of them on the same input modality. The survey's ranking
predates all three results. This does NOT pre-decide the kill test —
gesture classification is a different computation from per-column
direction regression (population dynamics over seconds, 11-way
classification, large coherent motions closer to the fc25-validated
speed band) — but the expected-tier prior is now materially worse than
when the task was ranked, and the kill test must be run (cheaply)
before ANY harness/integration build, exactly as operating rule 3
requires.

## Sharpened kill-test plan (to be registered before any build)

Reuse the measured pattern from the DSEC/ARC instruments: one DVS
Gesture split, features = T4/T5 population responses under the
fc25-passing configuration driven by binned events (the Task-2 drive
plumbing, AD-6/AD-7 analogs), one linear probe per arm; arms = real /
uniform-tau twin / degree-preserving rewire / raw event-count features
(the circuit-free comparator); bars frozen in the registration, with
real > rewire AND real > event-count as the kill line. Data and
probably the run are local-side. If the kill test dies the way its two
cousins died, Task 4 closes as a recorded verdict without a NeuroBench
harness integration ever being built; the Keyword-FSCIL/MB angle would
then be the only remaining Task-4 limb, and its prior (MB refuted on
one-shot association; LK calibration carries sparseness, not task
gains) should be weighed by the user before any effort goes there.

## Register updates in this commit

AN-2 annotated with the moved priors; new AN-3 (PyPI availability,
measured) and AN-4 (dataset egress, measured/inferred). Next concrete
step: register the DVS kill test, then build its data-gated instrument
— unless the user, reading the moved priors, chooses to skip or
re-rank Task 4 (their call under the standing directive).
