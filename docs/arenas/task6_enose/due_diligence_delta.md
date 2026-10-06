# Task 6 (e-nose / gas drift) — due diligence delta, 2026-10-06

What has changed since the 2026-09-30 survey ranked this arena sixth,
what the user's option-1 go covers (the MB's last stand, one kill test
designed to settle BOTH open MB premises), and what the registration
must state before any instrument code exists.

## What the survey said (2026-09-30)

"Olfaction: UCI gas-sensor drift corpus (standing) / DREAM Olfaction 3
(watch). The one modality where the fly is the acknowledged gold
standard and where AL->KC association is native. Encoder risk (16 MOX
channels -> ORN classes) is exactly where the intelligence could leak;
declared-assumption + scrambled-encoder control mandatory. FlyBench's
PN-broadcast finding says plain LIF won't sparse-code — our calibrated
MB is the differentiator or it fails the same way (either is a
result)."

## What exists in-repo to build on (verified 2026-10-06, this session)

- **A validated class-2 MB model with a passing configuration.**
  scripts/benchmarks/fc2_kc_sparse.py: the real MaleCNS PN/KC/APL/MBON
  subcircuit (627 PNs across 162 glomerular types, 4,064 KCs, 2 graded
  APL — counts asserted in the script), LIF KCs at Shiu canonical
  params, subtractive LK APL feedback, and the full Litwin-Kumar
  calibration recipe (free-potential theta0 -> open-loop alpha-balance
  probe -> closed-loop theta bisection to coding level 0.10). Its
  passing config (tau_m 20 / tau_syn 5 / beta 1.0, held-out band pass
  + Lin densification control) is recorded in
  results/benchmarks/fc2_kc_sparse.json (local-only) and was the fixed
  configuration of the mb_association arm.
- **run_trial returns `kc_odor_spikes`** — the per-KC spike-count
  vector over the odor window. That is the feature vector a gas kill
  test needs; the only new plumbing is a continuous per-glomerulus
  drive in place of the binary 24-glomerulus odor mask.
- **Container reachability (measured):** archive.ics.uci.edu HTTP 000
  — dataset acquisition is local-side, as for every arena so far.

## Moved priors since the survey

1. **Base rate 0 for 15** (survey said 0 for 12).
2. **Five consecutive rewire-over-real** on fc25-class visual
   circuits, with Task 5 adding the first measured case where the
   dynamics beat their own input — the transformation earns, the
   specific wiring doesn't.
3. **The MB's own record is the weakest in the program:** the
   mb_association rewire control beat the real wiring, and the
   LK-calibrated flybench arm was refuted on its frozen activation
   bar. These are the priors that parked the Task 4 Keyword-FSCIL/MB
   limb.

## The honesty point the registration must carry on its face

For THIS circuit, a rewire-beats-real outcome is not even against the
literature: Caron et al. 2013 (Nature 497:113) measured PN->KC
convergence as approximately random, and Litwin-Kumar et al. 2017 —
the same paper whose calibration we run — argues random-like expansion
achieves good coding. ESTABLISHED prior: the specific PN->KC wiring
should NOT beat its degree-preserving rewire. The program's first
principle still makes beating the null the definition of the
connectome earning its keep, so the bar stays; but the registration
must say plainly that a KILL on that bar is the literature's own
expectation, and that the test's informative content either way is
(a) whether the calibrated sparse expansion beats the raw sensor
features under drift at all (the circuit-vs-encoder question no prior
settles), and (b) the per-batch drift curves (AE-3: "this IS the
experiment").

## The dual close (pre-stated, so the later close is not ad hoc)

Both open MB premises rest on the same AL->KC association machinery:

- Task 6's premise: the calibrated sparse code transfers across
  sensor drift better than the raw features and better than the
  rewired circuit.
- Task 4's parked Keyword-FSCIL/MB limb: the same machinery, on audio,
  behind a larger encoder invention.

On a Task 6 KILL, the Keyword-FSCIL/MB limb CLOSES AS NOT PURSUED — a
program decision, tier INFERRED, bridge stated: if the MB cannot earn
its keep in its native chemical modality with native-form input (rates
on glomeruli), the audio limb — same circuit, a strictly larger
mapping invention — has no remaining support. Its hypothesis is not
thereby refuted (nothing was measured on audio); the limb is closed as
not worth its build. On a PASS, the limb reopens for a go/no-go with
the measured result as its new prior.

## Trivial alternatives (named before anything is built)

1. **Raw-feature probe** — the identical linear probe on the identical
   rank-normalized 128 features the encoder hands the circuit. The
   standard baseline family for this corpus, and the input-passthrough
   analog of Task 5's control.
2. **Degree-preserving rewire** of the subcircuit, per seed, each
   calibrated fresh by the circuit's own LK procedure (the
   flybench-calibrated precedent: rewired controls calibrate fresh).

Context arm (non-decisional, AE-1's mandated control): the scrambled
encoder — a second seeded feature->glomerulus permutation on the REAL
circuit. The base assignment is already an invention; if results move
materially under a different invention, any single-map result is
noise, and that gets reported.

## Known dataset caveats, stated now

- UCI drift corpus facts (SOURCED from literature; the host is
  egress-blocked in-cloud, so byte-level verification happens at run
  time): Vergara et al. 2012; 13,910 measurements, 16 MOX sensors x 8
  features = 128 features, 6 gases, 10 batches over 36 months;
  files batch1.dat..batch10.dat in libsvm-style format. Batch/class
  coverage is uneven — the instrument derives the trainable-class set
  from batch 1 and BLOCKs below floors rather than assuming coverage.
- AE-2 (class-correlated batch artifacts, Dennler 2022) affects all
  arms identically, so the kill decision — an internal comparison —
  stands on UCI alone; no outward headline is built from UCI alone
  either way.

## Cost, measured against the resource rule

Each sample is a 200 ms settle + 500 ms odor spiking trial at
dt 0.1 ms (~10 s single-process, extrapolated from the fc2_kc_sparse
sweep's observed rate). The frozen caps (90 train, <= 324 test, 5
simulated arms + per-arm calibration) put the single-process total at
roughly 7-8 hours; the instrument therefore takes --workers N
(process pool over samples — trials are independent given the
calibrated network and per-sample seeds are fixed, so parallelism is
decision-neutral), bringing a typical 8-worker run to ~1 hour. The
runbook states both numbers.
