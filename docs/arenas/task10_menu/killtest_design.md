# Task 10 kill tests — FROZEN 2026-10-23 (the science menu, jointly)

All seven registrations frozen in ONE commit, BEFORE any instrument
code, so none can be tuned on another's outcome. Changes after first
data contact require a recorded instrument-bug finding and a full
re-run; pre-data-contact amendments are allowed if dated and recorded
(the Stage-A and class-3 precedents). Due diligence:
due_diligence.md beside this file (7-agent sweep, 2026-10-23).
None of these is score-adjacent; every Expected-tier statement
inherits the CURRENT base rate (0 for 16 score-adjacent,
docs/arenas/SYNTHESIS.md).

Shared conventions unless a section overrides them: rewire null =
flygi.connectome.nulls.degree_preserving_rewire, seeds 4242+k;
exit 0 PASS / 1 KILL / 3 BLOCKED; BLOCKED is an instrument statement,
never a verdict; every arm x condition run is reported in full.

---

## 1. H-ARC-HARNESS-SENSITIVITY — the reservoir positive control (run FIRST, before the 2026-11-01 release)

### Premise

INSTRUMENT VALIDITY, never a fly claim: the Track A class-1 ARC
harness (literal interface: sparse-projection encoder -> frozen
166,700-node graph -> adaptive DN readout -> seeded sampler, at
K=4 / leak 0.3 / gain 0.9) can register a graph-identity difference
in official score at all. The probe graph is the already-built,
already-validated edge-of-chaos reservoir (rho 0.9924, memory
half-life 3 actions vs the real graph's 1, retention-after-12-silent
0.07686 vs 0.00019; manifest
results/manifests/positive_control_regime_20260922.json). Its bundle
carries departs_from_declared_normalization=true and
departs_from_declared_sign_mode=true — it is a positive control, not
a matched null.

### Frozen protocol

- Command (local): `uv run python scripts/evaluate_connectome.py
  --config configs/literal_rate_signed.yaml --runtime-dir
  data/processed/male-cns-v1.0/literal-rate-signed/reservoirs/edge_of_chaos/seed-20260922
  --condition reservoir-positive-control --seeds 0 1 2 --games all
  --action-budget 500`, then `uv run python scripts/league.py
  --write-md LEAGUE.md`.
- Protocol identical to the eff- rows: 25 public games x seeds 0-2 x
  500 actions = 75 rows; comparisons on complete matched (game, seed)
  pairs only, clustered-bootstrap CI at 5000 resamples
  (flygi.evaluation.compare — the league's frozen verdict machine).
- SECONDARY ARM (context, reported): the matched_random reservoir
  bundle (same seed-20260922 build, rho 0.1608, half-life 1) as
  condition reservoir-matched-random — the positive control's own
  dumb twin.
- Registry mechanics: both conditions register under regime
  gain0.9-dead with baseline eff-real-signed and a prose note that
  the reservoir's dynamics are measured alive there (league.py
  refuses cross-regime comparison; this is the recorded trap).
- Comparators, already measured, NOT re-run: eff-real-signed 0.0648;
  eff-null-degree-preserving 0.0079; eff-no-graph-bypass 0.0008;
  random-500 0.097568.

### Frozen reading

- CERTIFIED (PASS): reservoir-positive-control is HELPS vs
  eff-real-signed AND vs eff-null-degree-preserving (both CIs exclude
  0, favorable side). Reading: the harness can express a graph
  advantage; the fly's class-1 ARC nulls are informative about the
  fly graph under this interface; exhaustion-audit standing
  criticism 1 discharged in the certifying direction.
- DETECTS-BUT-HURTS (partial): CI vs eff-real-signed entirely below
  0. The harness registers graph identity (sensitivity shown) but an
  expressed ADVANTAGE remains undemonstrated; partial certification
  only, stated as such.
- FLAT (KILL for the certification claim): both CIs span 0. The
  published class-1 ARC nulls DOWNGRADE from "the real wiring
  conferred no advantage under this interface" to "under an interface
  in which no tested graph — including one tuned into the known-good
  long-memory reservoir regime — moved official score, the real
  wiring also did not." That caveat MUST propagate to
  docs/experiment.md, docs/controls.md, LEAGUE.md's
  real-vs-null/bypass prose, and the task1_arc_paper
  factsheet/writeup BEFORE the 2026-11-01 release. It does NOT touch
  the arena program's seven rewire-parity instances (each of those
  harnesses carried its own measured positive), the retinotopy
  positive, or the structural separations.
- POWER FLOOR, stated now: measured comparator CI half-widths are
  +/-0.07-0.19 score at 75 rows, so certification covers advantages
  of roughly >= +0.1; FLAT means "no detected advantage at this
  resolution". The standing prose "cannot register an advantage that
  ANY graph could confer" is an INFERRED bridge and is hereby
  weakened to the measured form regardless of outcome.

### BLOCKED floors

(1) Reservoir bundle missing or graph hash-mismatched vs its manifest
and rebuild (`uv run flygi graph reservoirs`, measured 120.7 s) fails.
(2) environment_files/ game cache absent or not the same 25 games.
(3) Any comparator bundle (results/connectome_agent/*.json[.gz])
missing — no complete matched pairs, no certification verdict.
(4) Harness engineering-gate failure (exception, illegal action,
budget violation, replay-hash mismatch). (5) Degenerate dynamics:
non-finite state, zero per-row readout variance, or tanh saturation
to a constant under the adaptive standardizer. (6) Operating-point
drift from K=4 / leak 0.3 / gain 0.9 (the gain-2.0 modulators config
is unvalidated for this bundle).

### Assumptions (register rows A-RES-1..4, ASSUMPTIONS.md)

A-RES-1 certification scope = Track A literal harness at this
operating point only. A-RES-2 the ESTABLISHED reservoir-computing
bridge ("long memory is good") does NOT establish that long memory is
the kind of advantage ARC score pays for — if level-1 completion
needs no cross-action neural memory, even a perfect reservoir is
flat; hence the FLAT reading above. A-RES-3 per-action wall time
assumed ~= real graph's 0.148 s/action (same edge count; untimed).
A-RES-4 the 2026-09-22 dynamical validation still describes the
bundle (hash check at run time).

### Tier

Expected-tier prediction: none offered beyond the base rate (0 for
16). Priors both ways: the reservoir regime is the one reservoir
computing says helps; the tie seat is measured score-inert and the
real-vs-bypass delta is measured ~0, which cuts the other way.

---

## 2. H-T4T5-CLASS3-DS — class-3 spiking physiology on T4/T5 (SYNTHESIS §7 item 1)

### Premise

At spiking class-3 physiology, the specific MaleCNS T4/T5 wiring
produces its native computation — Maisak-band direction selectivity
(ESTABLISHED wiring-specific in the fly: Maisak et al. 2013) — where
its degree-preserving rewires do not. This is the FIRST direct
real-vs-rewire comparison on the DS statistic at ANY fidelity (fc2/
fc25 ran no rewire arm; the three T4/T5 KILLs were external-task
decodes). A reversal breaks SYNTHESIS §4; a KILL with a valid gate
extends the class-3 failure record to the circuit where the
literature disagrees with our null.

### Model-class decision (recorded, mirrors the AC-8/Duan-Fiete decline)

"Class 3" = the CX ladder's template-LIF spiking tier (TemplateLIF
descendant), chosen for continuity with the validated engine. The
ESTABLISHED higher-fidelity tier for THIS circuit is graded/
conductance (Gruntman 2018/2019; Borst 2025; flyvis itself) — that
rung is explicitly NOT climbed here and reopening it needs its own
registration. Scope: every close sentence is about the spiking model
class under the declared mapping, never "the fly's T4/T5" (AT-1).

### Frozen design

- SUBSTRATE: the fc2/fc25 patch verbatim — 2,701 nodes / 507 driven
  (L1/L2/L3 at histaminergic sign) / 498 scored T4-T5 / 169 columns;
  13x13 input window centered on the right-eye Mi1 median column
  (19,20); scored on the inner 9x9.
- ENGINE: TemplateLIF extended three ways (declared engineering, not
  tuning): per-type membrane tau (trained taus from
  docs/fidelity2/flyvis_trained_params.json; e.g. Mi1 19.8 ms, Tm2
  133.2 ms, Tm9 46.7 ms), two-state exponential synapses per kernel
  class in place of the ring-buffer PSC (a 133-300 ms kernel at dt
  1e-4 makes the template buffer ~450 MB/class — O(N) exponential
  states are the honest implementation), signed external drive.
  Everything else (V_rest, threshold, AP template, dt, background)
  carried verbatim from cx_class3_killtest.py's pinned physiology.
- WEIGHT MAPPING (AT-2, the AC-6 analog): W_ij = curated_sign(pre) x
  alpha_trained(pre->post) x N_ij x g with ONE global calibrated g
  (fc2's held-out calibration: +45-deg diagonal at 5 col/s, both
  polarities, log grid, target median peak response; scoring never
  feeds back). Secondary declared config, reported: Shiu uniform
  conversion |w| = N x 0.275 mV with NT signs (class-blind; Shiu
  never tested vision — carried as context).
- STIMULUS + STATISTIC, fc2/fc25 verbatim: moving ON and OFF edges,
  4 directions (+x/-x/+y/-y hex), speeds {2.5, 5, 10} col/s; evoked =
  spike count in the v2 crossing-locked window (opens 2.0 columns
  before the edge front reaches the cell; closes 0.75 s after it
  passes) minus the background-rate expectation; DSI per cell =
  (R_pref - R_anti)/(R_pref + R_anti), pref = argmax over directions
  of speed-pooled response.
- MAISAK BAND (asserted equal to fc2.BAND_TEXT): pooled per-cell
  median DSI >= 0.30 (T4 on ON edges, T5 on OFF), >= 3 distinct
  preferred directions among T4a-d AND among T5a-d, defined-DSI
  fraction >= 0.5.
- VARIANT GRID (declared, all reported): calibrated g* x global scale
  {0.5, 1.0, 2.0} — 3 points, CX-grid style.
- NULL BAR: at every real-passing grid point, all 3 rewires of the
  patch (seeds 4242+0..2) fail the band. Cost-honest order: real arms
  first, rewires only at real-passing points.
- ATTRIBUTION CONTEXT (reported, non-decisional): uniform-tau (50 ms)
  spiking twin at the same strengths (class-2.5 precedent measured
  taus not load-bearing: 0.3365 vs 0.3216).
- PASS iff >= 1 grid point clears the band on real with all 3 rewires
  failing there; KILL otherwise (given valid gates).

### Validation gates (in-cloud, BEFORE data contact; asserted by unit test)

ABSENCE FINDING (recorded): no published spiking/LIF motion detector
with code or exact parameters exists to reproduce — there is no
Pisokas analog for T4/T5 (Shiu never tested vision; the lit clones
are CX papers; published higher-fidelity T4/T5 models are graded/
conductance; the FAFB spiking adjacency is recorded
parameters-not-verifiable). The honest fallback:

- GATE A (engine capacity; idealized circuit ASSUMED, anchors
  ESTABLISHED): an idealized 2-3-arm delay-line correlator at the
  pinned spiking physiology (~1-column offset arms; hand-set fast
  10-40 ms vs slow 100-300 ms kernels per the ESTABLISHED fast/slow
  classification: Behnia 2014, Arenz 2017, Borst 2025) must reach
  DSI >= 0.30 under the same edge protocol, with its
  temporal-frequency optimum inside 0.5-2 Hz (correlator anchor
  ~1 Hz), AND collapse to DSI < 0.05 with arm taus equalized (the
  gate's own trivial alternative — otherwise the statistic is not
  measuring the delay line). Gate A failing = BLOCKED, recorded as a
  measured absence result about the spiking model class ("spiking
  discretization destroys the delay code"), never a fly verdict.
- GATE B (continuity): patch extraction reproduces the frozen dims
  (2,701/507/498/169) and the declared fc25-reference values
  reproduce on the verdict machine before any class-3 arm runs.

### BLOCKED floors

(1) Runtime or annotations feather absent. (2) Patch composition
deviates from 2,701/507/498/169. (3) Run-time sign audit disagrees
with the curated I6 table (Mi9 -Glu, Mi4 -GABA, Mi1/Tm1/Tm2/Tm3/Tm4/
Tm9/T4*/T5* +ACh) — fc2 measured agreement; mismatch now is an
instrument fault. (4) Non-finite membrane in > 20% of runs in any
arm. (5) Gate A fail. (6) Gate B fail.

### Assumptions (register rows AT-1, AT-2)

AT-1 spiking-tier scope (ASSUMED scope choice; the graded/conductance
rung declined, recorded). AT-2 the weight mapping (ASSUMED invention:
trained GRADED alphas imported across a dynamics tier, bridge stated;
no published per-class spiking weight set exists for this circuit).

### Tier

Expected: none beyond the base rate. Priors FOR a real-vs-rewire
separation: Maisak's wiring-specificity is ESTABLISHED in the animal;
the class-2.5 instrument measured the band on the real patch.
AGAINST: seven-of-seven rewire parity on dynamics tasks; the CX
class-3 KILL; the tau-not-load-bearing twin result.

---

## 3. H-CX-BISWAS-FITTED — fitted per-type physiology on the CX (PARTIAL FREEZE; completion pending user fetch)

### Status

needs-fetch. The Biswas et al. 2024 paper, supplement, parameters and
any code exist nowhere in the container, no GitHub repo exists, and
cloud egress denies every serving host (MEASURED proxy 403:
www.biorxiv.org, api.biorxiv.org, par.nsf.gov, neurips.cc,
europepmc). What follows is frozen NOW, before anyone on this project
has seen their parameter values, so the later completion cannot be
tuned on them. The numeric bars that depend on their published
realization are completed in a dated addendum AFTER the fetch and
BEFORE any instrument code.

### Frozen pre-commitments

- PREMISE SCOPE (frozen verbatim): "GIVEN literature-fitted per-type
  physiology — Biswas et al.'s exact threshold-linear model form with
  their published MaleCNS realization parameters (or their published
  derivation recipe applied once to our counts) — the standalone
  compiled MaleCNS CX (AC-8: EPG 46 / PEN_a 20 / PEN_b 22 / Delta7 42
  / PEG 18) sustains a position-faithful heading bump that its
  degree-preserving rewires do not." A PASS is NEVER reported as an
  unfitted-counts result: the close sentence must carry "given
  fitted per-type physiology" in the same sentence.
- G1 bars carried verbatim from H-CX-CLASS3-COMPASS for
  comparability: 8 write angles every 45 deg; per-angle pass iff
  retention >= 0.05 AND circvar <= 0.6 AND PVA within 45 deg; G1
  passes iff >= 6 of 8 (kills the fixed-point mode measured at
  classes 1 and 3: finals clustering ~177-221 deg).
- G2 (steering) is CONDITIONAL on the fetched realization defining a
  rotation-input convention; if their model has none, G2 is reported
  non-decisionally and the verdict rests on G1 + the null bar
  (declared now).
- NULL BAR: 3 rewires (seeds 4242+0..2) fail G1 at every real-passing
  configuration. No new variant knobs beyond what their paper itself
  declares; their published configuration(s) only, all reported.
- VALIDATION GATE (Pisokas-gate pattern): implement their
  threshold-linear form and reproduce ONE of their own published
  realizations on their own published matrix in-cloud before any
  MaleCNS contact; assert the exact-attractor property they prove.
- BLOCKED floors: runtime absent; composition mismatch; gate fail;
  fetched materials lack both the MaleCNS parameters AND a complete
  derivation recipe (then this item closes "blocked-data, recorded",
  not run).

### USER FETCH LIST (local machine; never commit the PDFs — a small
reviewed provenance extract of the parameter tables enters the repo)

1. Biswas, Stanoev, Romani, Fitzgerald — "From the fly connectome to
   exact ring attractor dynamics", bioRxiv 10.1101/2024.11.01.621596
   (full PDF + supplementary material; check for a v2 / published
   2026 version; alternate copy: par.nsf.gov/servlets/purl/10609135).
2. The 2026 follow-up, bioRxiv 10.64898/2026.05.18.725766 ("Hidden
   symmetries...") — possibly where the four-connectome/MaleCNS
   realizations live.
3. Duan, Dong & Fiete — bioRxiv 10.1101/2025.05.26.655406 + the
   NeurIPS 2025 record (poster 115017) for the necessity claim's
   exact statement and any code link.

---

## 4. H-FB-COLUMNAR-TOPOLOGY — the fan-shaped-body structural probe (Stage-A analog)

### Premise

The MaleCNS v1.0 FB columnar wiring structurally encodes the
published vector-computation geometry: (i) coupling routed through
hDelta concentrates at half-width (~180 deg) FB-column offsets, and
(ii) left-PB vs right-PB PFN populations project into FB columns at
OPPOSITE-signed angular offsets — and degree-preserving rewires
destroy both. Structure only (the Stage-A scope rule): no computation
claim at any outcome. This is the first contact of the program with
the literature's actual vector-navigation substrate ("PFN"/"hDelta"
appear nowhere in the repo before this task).

### Frozen design (Stage-A constants reused, not retuned)

- POPULATIONS + frozen composition table (MEASURED in-cloud from the
  raw release annotations, due_diligence.md): PFNa 58, PFNd 40,
  PFNm_a 21, PFNm_b 26, PFNp_a 64, PFNp_b 136, PFNp_c 40, PFNp_d 28,
  PFNp_e 23, PFNv 20, hDelta 189, vDelta 430, FC 274, PFL1 14,
  PFL2 12, PFL3 24 (noduli context: 4/2/2/4/2/2).
- COORDINATES (AC-FB1..4): _C column labels on a common azimuthal
  frame, angle = 2*pi*(c-0.5)/N_type with N_type the type's own
  observed column count (FC 9, hDelta 12, vDelta 10 incl. C0);
  PFN instance glomerulus digits 2-9 + L/R in the Stage-A PB frame
  (each side's 8 glomeruli span 360 deg, mirrored); hDelta a/b
  sub-column suffixes collapse to the numeric column; _irreg cells
  kept and flagged.
- BAR 1 (hDelta antipode; the bandedness analog at 180 deg):
  W2 = relu(W[FC<-hDelta]) @ relu(W[hDelta<-labelled-PFN]), aggregated
  by (FC column angle, PFN column angle); statistic A = mass fraction
  at circular angular distance within ONE 40-deg sector of 180 deg.
  IN = the five labelled PFN types (163 column-labelled cells), OUT =
  FC (274) — pinned from Hulse (eLife 66039, in the clone): "the
  majority of PFN synapses are to vDelta, hDelta, and FC"; "hDelta
  and vDelta are the main downstream target of FB columnar types".
- BAR 2 (PFN mirror; mirror_peak VERBATIM from
  cx_topology_killtest.py): per hemisphere, one-hop W[FC<-PFN_side]
  aggregated into (FC column angle - PB glomerulus angle) offset
  profiles q_L, q_R; S = max_d max(q_L(d) q_R(-d), q_L(-d) q_R(d)).
- NULLS: 200 degree-preserving rewires of the full extracted FB
  subcircuit, seeds 4242+0..199, one-sided empirical
  p = (1+k)/201 (floor 0.00498), alpha 0.05.
- PASS iff BOTH bars beat the nulls at p < 0.05; KILL otherwise.
  CONTEXT, non-decisional: PFL and vDelta offset profiles, reported.
- COVERAGE floor 0.90 on every bar-coordinate population (in-cloud
  raw baselines: FC 100%, vDelta 100%, hDelta 98.9%, labelled-PFN
  98.8%, PFL 100%).

### Validation gate (in-cloud, pre-data; the AC-4 pattern that fired twice in Stage A)

Idealized FB vector circuit encoding the ESTABLISHED Hulse motifs
(9-column FC frame; per side 8 PFN glomeruli projecting at
opposite-signed one-sector offsets; hDelta half-width connectivity):
both bars must PASS on the ideal at the empirical floor AND its own
degree-preserving rewire must KILL both. Asserted by unit test before
any data contact.

### BLOCKED floors

(1) Runtime absent (cloud always blocks). (2) Compiled per-type
counts deviate from the frozen composition table. (3) Column/
glomerulus coverage < 0.90 on any bar population (AC-FB6: instance
strings did not survive the compile). (4) Degenerate zero-mass
two-hop/one-hop for any bar statistic. (5) Synthetic gate failing
either direction.

### Assumptions (register rows AC-FB1..6)

AC-FB1 common azimuthal column frame (Stage-A AC-1 analog). AC-FB2
PB-glomerulus/EPG-wedge frame concordance. AC-FB3 hDelta sub-column
collapse. AC-FB4 _irreg handling. AC-FB5 (MEASURED) bar populations
are consensus-ACh, so relu(W) keeps them. AC-FB6 instance-label
survival through the compile (coverage floor is its check).

### Tier

Structural claim only. Priors FOR: Stage A passed on the sibling
system at the p-floor; the Hulse motifs are ESTABLISHED anatomy in
hemibrain. AGAINST: MaleCNS column annotation conventions are AC-FB1
assumptions until the coverage checks bite.

---

## 5. H-T4T5-NATSTAT-DIRECTION — naturalistic statistics (SYNTHESIS §5 explanation 3's first test)

### Premise

The T4/T5 rewire-parity measured three times (ARC 0.3875 vs 0.4306;
DSEC 81.36 vs 78.85 deg; DVS 0.410/0.389/0.427 vs 0.441/0.424/0.465)
is caused by non-ecological input statistics: on translating NATURAL
scenes at validated class-2.5 physiology, the real wiring beats its
rewires at direction estimation, and the advantage disappears when
the natural statistics are destroyed (phase-scrambled) with the
power spectrum preserved.

### Frozen design

- 2x2: {REAL, 3x REWIRE (seeds 4242+0..2)} x {NATURAL,
  PHASE-SCRAMBLED}; identical fc25 class-2.5 machinery (13x13 hex
  patch, dt 2 ms, settle 2500 ms, trained params from
  docs/fidelity2/flyvis_trained_params.json), identical AB-4 encoder
  (ONE instance across all arms and conditions — the AE-1 dodge: the
  manipulated variable lives in stimulus space, upstream of any map).
- STIMULI: rigid constant-velocity translation of static natural
  images; 8 directions (4 cardinals + 4 diagonals); speeds
  {2.5, 5, 10} col/s (the fc25 passing band). Scrambled condition:
  per-image phase randomization with one declared seed per image,
  amplitude spectrum preserved (rel 1e-6, asserted at run time),
  identical translation applied.
- CORPUS: van Hateren natural-image subset, FROZEN ID list +
  checksums in the instrument (user-fetched locally; SOURCED caveat
  carried — the mirror is unverifiable from the cloud); declared
  calibration/evaluation split by index list (calibration touches a
  contrast scalar only); Sintel-via-local-flyvis is the declared
  fallback corpus. Corpus stays outside the repo tree.
- READOUT (AD-8, no fitted parameters): vector vote — per-subtype
  preferred directions read verbatim from the fc25 results JSON,
  DIR_VECTORS unit vectors; per-item estimate vs imposed direction =
  2D angular error. Item = (image, direction, speed).
- BARS: B1 — REAL beats the per-item mean of the 3 rewires on
  NATURAL items (one-sided paired sign test p < 0.05 AND median
  per-item error strictly lower; the Task-2 bar verbatim). B2 — the
  gap is statistics-dependent: d_i = err_NULL - err_REAL per item;
  one-sided paired sign test d_natural > d_scrambled on matched
  items, p < 0.05, AND median(d_nat - d_scr) > 0. PASS iff B1 AND
  B2; KILL otherwise — B2 failing refutes explanation 3 in its
  sharpest available form.
- FLOOR CONTEXT (reported): circuit-free frame-difference-centroid
  estimator on the identical lattice input; uniform-tau TWIN
  attribution arm.

### Validation gates (in-cloud, numpy-only, pre-data)

(i) Scramble integrity: amplitude spectrum preserved to rel 1e-6,
phases decorrelated. (ii) Translation exactness: imposed shift
recovered by lattice cross-correlation to sub-column precision.
(iii) AD-8 vote recovers direction exactly on a synthetic
ideal-correlator response table. (iv) Verdict-logic unit tests
covering PASS, both KILL paths, every BLOCKED floor. On the verdict
machine before eval: G0 — fc25's own moving-edge stimulus pushed
through the NEW stimulus code path reproduces the recorded
per-subtype preferred-direction tiling (argmax exact) and DSI within
+/-0.02 of the measured 0.3216 (tolerance declared here). G1 —
usable-input gate (the 0.00%-input MB rule): REAL-natural median
per-item error below the 90-deg chance floor, one-sided sign test
p < 0.05; failure = BLOCKED (a measured convention limit of the
AB-4-class drive), never a statistics verdict. Literature anchor
(non-decisional, SOURCED, unverifiable from the cloud): correlator
velocity estimation on translating van Hateren scenes (Dror,
O'Carroll & Laughlin ~2001).

### BLOCKED floors

(1) < 30 evaluable eval items in any arm-condition (Task-2 rule).
(2) G0 fail. (3) G1 fail. (4) Scramble-integrity selftest fail at run
time. (5) Instability: an unstable item is dropped from EVERY arm and
counted; > 20% dropped = BLOCKED. (6) Corpus absent: exit BLOCKED
listing exactly the missing corpus (dsec precondition pattern).

### Assumptions (register rows ANS-1..5)

ANS-1 encoder reuse (AB-4 verbatim, one instance; the AE-1 dodge).
ANS-2 "naturalistic motion" = rigid translation inside the fc25 band
(saccades/3D flow out of scope). ANS-3 "natural statistics" = what
phase-scrambling destroys; power spectrum explicitly outside the
claim. ANS-4 the frozen van Hateren subset is representative (ID list
frozen before any run). ANS-5 the fc25 operating point (chosen_gain)
transfers from edges to natural movies (checked by G1, not assumed
silently).

### Tier

Expected: none beyond the base rate. Priors FOR: flyvis params were
TRAINED on naturalistic motion (Sintel), so the circuit meets its
ecology here if anywhere. AGAINST: three T4/T5 rewire parities;
AE-1's lesson that interface inventions dominate small effects.

---

## 6. H-FLYGI-FLYBENCH-SFA and H-FLYGI-FLYBENCH-TERMINAL — the two externally measured mechanisms

Two hypotheses, one shared machinery (the Task-3 adapter + a frozen
verdict script per the flybench_calibrated_verdict.py precedent),
both compared against our own MEASURED uniform row (core 1.000 /
hard 0.6044 / graded 0.7113 / specificity +0.282; local unpinned
MaleCNS build, AF-7, 176,422 neurons, 3 seeds, rewired control).
Mechanisms are default-OFF engine extensions, evaluated ONE AT A
TIME; a combined arm is reported non-decisionally only if both
singles pass.

### H-FLYGI-FLYBENCH-SFA

- MECHANISM (ESTABLISHED source, FlyBench adaptive_lif.py): one
  adaptation state per neuron; on spike a += b, tau_a decay,
  subtracted from membrane drive. PINNED b = 2.0 mV, tau_a = 200 ms,
  uniform (their best open-division row; their measurement on
  flywire783: hard 0.512->0.647, graded 0.644->0.754, spec
  +0.200->+0.311, core untouched). UNIT BRIDGE (derived, not fitted):
  sfa_b = b_mv / tau_m_ms = 0.1 at Shiu tau_m 20 ms (the registered
  w_scale bridge pattern).
- BARS (PASS iff ALL): (1) hard-tier graded >= uniform hard-graded
  + 0.02; (2) overall graded >= 0.701 (= uniform 0.7113 - 0.01);
  (3) specificity vs rewired >= +0.252 (= +0.282 - 0.03);
  (4) activation-subset mean graded >= uniform - 0.01 (SFA is
  suppressive; it must not buy the hard tier by selling activation —
  AF-8's failure axis).
- GATES (in-cloud): bit-identity off-switch (sfa_b=0 byte-identical
  to uniform engine); single-neuron constant-drive unit test against
  the closed-form adaptive-LIF rate/ISI lengthening (Benda & Herz
  2003, their model card's reference); interface-matched toy
  equivalence — FlyBench's own AdaptiveLIFSimulator vs our
  engine+SFA behind the adapter, deltas moving the same direction as
  their adaptive-vs-reference delta.

### H-FLYGI-FLYBENCH-TERMINAL

- MECHANISM (ESTABLISHED source, FlyBench terminal.py +
  terminal_lif.py): terminal-aware synapse placement — NOT
  3D-position-based; synapses classified by their theta convention;
  input table = FlyBench's shipped
  data/terminal/malecns_terminal.csv.gz (2.4 MB, MIT; 3,782,429
  terminal synapses = 4.2%, matching their FINDINGS M1b; ID alignment
  vs official annotations MEASURED 99.98%). Their measured headline:
  core tier 0.57 -> 0.90 on their reference engine — stated openly as
  headroom that does NOT exist on our engine (our core is already
  1.000), so the honest primary bar is the hard tier.
- BARS (PASS iff ALL): (1) hard-tier graded >= uniform + 0.02;
  (2) core stays 1.000 (regression guard); (3) overall graded
  >= 0.701; (4) specificity >= +0.252 (rewired control runs
  terminal=None per FlyBench's own convention — declared; a
  terminal-preserving rewire belongs to item 7's family, not here).
- GATES (in-cloud): toy equivalence with a SYNTHETIC injected
  terminal matrix vs their TerminalLIFSimulator (matching spike
  trains within the declared dt/no-delay-line differences);
  shipped-table magnitude gate (T sums to 3,782,429); alignment gate
  (>= 95% body-ID coverage vs the LOCAL build at run time; in-cloud
  expectation 99.98%); >= 90% of published synapses survive clipping
  to |W|.

### Shared BLOCKED floors

(i) Off-switch bit-identity fails — invalid instrument. (ii) Any
in-cloud gate fails. (iii) Stored uniform baseline JSON absent/
unreadable, or local build composition != the baseline's recorded
176,422 neurons. (iv) Terminal only: coverage < 95% or synapse
survival < 90%. (v) Non-finite membrane in any arm, or
`flybench verify-adapter` nonzero on either new adapter class.

### Assumptions (register rows AF-9..13)

AF-9 SFA point values + uniformity (ASSUMED; the literature RANGE
tau_a 100-500 ms is ESTABLISHED, the point is their best row). AF-10
the unit bridge (DERIVED; Euler-vs-exponential decay a declared
scheme choice). AF-11 the load-bearing INFERRED bridge: mechanisms
measured on FlyBench's reference LIF move OUR class-2 engine — this
is exactly what the test measures. AF-12 SFA transfer from flywire783
to MaleCNS (their SFA number does not exist on MaleCNS). AF-13
terminal defined by THEIR convention and THEIR shipped table
(provenance imported, not re-derived; re-derivation from upstream
synapse tables recorded as the costlier alternative).

### Tier

Expected: none beyond the base rate. Priors FOR: both mechanisms are
externally MEASURED to move a sibling engine on this benchmark
family, with zero free parameters. AGAINST: the Task-3 calibrated arm
(the last "externally-motivated physiology knob" we imported) was
KILLED at +0.0002 vs its +0.02 bar; AF-11 is untested by
construction.

---

## 7. H-STAGEA-NULL-DECOMPOSITION — the second null family (REFINEMENT, never a reopening)

### Premise

The degree-preserving rewire destroys edge placement and magnitude
assignment simultaneously. A |weight|-magnitude shuffle holding
topology+signs fixed, and a per-presynaptic-neuron sign shuffle
holding topology+magnitudes fixed, decompose the program's single
structural PASS (H-CX-RING-TOPOLOGY: bandedness 0.5881 vs rewire max
0.3376; mirror-peak 0.01445 vs 0.00792; both p 0.00498) into
"carried by edge placement" vs "carried by magnitude/sign
assignment". No closed verdict changes at any outcome; the readings
are decomposition sentences. This also closes docs/controls.md's
recorded "Not implemented" rows by existence + validation + one
Stage-A application (ARC-scope application deferred, recorded).

### Frozen design

- GENERATORS (src/flygi/connectome/nulls.py, whose NullKind literal
  already declares both): weight_shuffle in TWO variants — global
  |w| permutation over existing edges, and within-presynaptic-column
  permutation (the clean complement of the rewire's
  weight-travels-with-pre rule) — within-pre is PRIMARY for the
  decomposition sentence (AC-N1); sign_shuffle = permute the
  per-presynaptic-neuron sign assignment over sign-bearing columns,
  Dale-consistent (AC-N2; per-edge sign permutation rejected as
  non-biological).
- INVARIANTS per generated null (extending null_invariants): edge set
  identical to real (fraction_shared == 1.0 vs the rewire's measured
  0.51%); in/out degrees identical; weight family: |w| multiset
  identical (within-pre variant: per-column multisets identical),
  per-edge signs identical; sign family: per-edge |w| identical,
  column sign-constancy preserved, column-sign multiset identical.
  Any violation = BLOCKED.
- APPLICATION: the Stage-A statistics (bandedness, mirror-peak) on
  the SAME 148-neuron CX subcircuit, 200 nulls per family, seeds
  4242+0..199, one-sided empirical p = (1+k)/201 — same seeds,
  different generator, for comparability (AC-N3).
- READINGS (all reported; none reopens anything): per statistic x
  family, "separates at p < 0.05" or not. AC-N4 bridge, said aloud:
  "p >= 0.05 under the weight family => the property is
  topology-carried" is an inference whose bridge is the invariant
  set, not a new verdict.

### Validation gate (in-cloud, pre-data, both directions; the AC-4 pattern)

On a magnitude-tuned synthetic (banding lives only in |w| on
dense/uniform topology): weight-shuffle p_banded must hit the
empirical floor (<= 0.0099 at 100 nulls). On a topology-banded
uniform-weight synthetic (the _ring builder): weight-shuffle must
NOT separate (p >= 0.2, declared) while the rewire on the same graph
separates (the existing precedent test). Identity-shuffle degeneracy
floor: >= 0.5 of edges must change |w| under the weight family, else
BLOCKED-degenerate. Sign family: if the sign multiset over
sign-bearing columns is constant, report NA, never a p.

### BLOCKED floors

(a) Runtime or raw pair table absent. (b) Inherited Stage-A floors
(composition, wedge coverage >= 0.90, degenerate two-hop). (c) Any
invariant violation. (d) Weight-family degeneracy (< 0.5 changed).
(e) Sign-family constant-multiset (NA). (f) Real subcircuit violates
column sign-constancy. (g) Gate failing either direction.

### Assumptions (register rows AC-N1..4)

As stated inline above.

### Tier

Methodological refinement. Prior: the bandedness statistic is
plausibly topology-carried (built from relu'd two-hop structure), so
the informative outcome space is asymmetric — the mirror-peak and the
magnitude question carry the news. Either way the decomposition
sentence is new, measured information about what the program's one
PASS consists of.

---

## Build-time operationalization notes (dated 2026-10-23, PRE-DATA-CONTACT; frozen text above untouched)

Recorded when the instruments were built, before any of them touched
MaleCNS data. These resolve details the frozen sections left unstated;
no frozen constant, bar, floor or gate changed. Full code-site
comments carry the same content.

### Section 2 (H-T4T5-CLASS3-DS), R1-R6

- R1 calibration target: fc2's 0.5 a.u. has no spiking unit; the
  calibrated global gain targets median evoked rate in the v2 window
  = sqrt(BG_HZ x DRIVE_PEAK_HZ) ~= 30.8 Hz (geometric midpoint of the
  pinned input-rate band), log-grid argmin over fc25's extended gain
  grid; scoring never feeds back.
- R2 kernel assignment: each synapse's kernel class = its presynaptic
  type, decay tau = that type's trained tau, rise = the pinned 2 ms.
  INTERPRETIVE RISK, stated: the trained tau then filters twice
  (membrane and outgoing kernel); this is arm-symmetric, so the
  real-vs-rewire comparison is unaffected, and the uniform-tau twin
  (which ablates kernel decays to 50 ms as well) carries the
  attribution check.
- R3 the correlator-optimum anchor is read strictly: the TF argmax
  over the three speeds must be the interior 1 Hz point.
- R4 gate-A detectors are T4-analogs scored on ON edges; "arm taus
  equalized" = both arms carry the fast kernel.
- R5 gate-B reference tolerance +/-0.02 borrowed from section 5's G0
  declaration for the same 0.3216 number; the 0.3365 twin value is
  recorded, not re-run.
- R6 evoked clamped at 0 (fc2 convention); baseline = final 1 s of
  settle; Shiu context arm varies the weight mapping only (0.275 mV
  bridged to unitary-PSC equivalents numerically, ~1.19 mV unitary
  PSP); no-stable-calibration-gain exits BLOCKED. Gate A's hand-set
  idealized-circuit values were engineered against the frozen gate
  bars only, in-cloud, before any data contact, and are recorded in
  the gate report.

### Section 6 (FlyBench mechanisms)

- The SFA adapter's forced-event pulse is STATE-DEPENDENT
  ((v_th - v_i)/dt + 1 + sfa_a_i) rather than the Task-3 uniform
  adapter's fixed pulse: MEASURED at build time, the fixed pulse under
  adaptation left driven neurons ~40 mV below rest and silenced them
  through flybench's forced path (a verify-adapter defect = shared
  floor v). The compensation restores the registered forced-spike
  semantics through the engine's own threshold; Task-3's declared
  uncompensated-inhibition limit stands.
- The verdict script carries instrument-level guards beyond the
  frozen floors (calibrated-verdict precedent, labelled in its
  header): empty shared activation set, missing report fields,
  missing/off mechanism sidecar, terminal-source mismatch -- each
  makes an otherwise silently-fake bar impossible; none is a new bar.

### Section 5 (natstat)

- The Dror/O'Carroll/Laughlin anchor is recorded in the output JSON
  as SOURCED and NON-DECISIONAL (unverifiable from the cloud).
