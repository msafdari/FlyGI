# FlyGI arena program synthesis — 2026-09-29 to 2026-10-07

What eight days of preregistered kill tests across two sensory
modalities established, stated at tier. Every number below traces to
EXPERIMENTS.yaml, WORKLOG.md, or the task factsheet; nothing here is
new measurement. Tier words follow the repository convention:
MEASURED (this number, this protocol), ESTABLISHED (literature or the
connectome's own annotations, with source), INFERRED (measurement plus
a stated untested bridge), EXPECTED (prediction; base rate 0 for 16).

## 1. The program and its instrument

Six arenas from the 2026-09-30 survey were run in rank order, each
under the same discipline: a frozen registration (premise, named
trivial alternative, mechanical pass/kill bars, BLOCKED floors)
committed before any instrument code; degree-preserving rewires as
the standing null; one declared encoder convention per test, no
sweeps; instruments built in the cloud, measurements run locally by
the user; closes recorded either way. Tasks 2-6 each produced a
verdict. Task 1 (the ARC paper) carries the record outward and waits
on its calendar. Tasks 7-8 are calendar-gated into 2027.

## 2. The central measured result

Seven times since 2026-09-29, under six frozen registrations, a
degree-preserving rewire of the circuit under test met or beat the
real wiring on the registered metric. No registered test went the
other way. (The WORKLOG's running "six consecutive" count covers the
arena program proper — the DSEC record contributing its real arm and
its uniform-tau context arm — with the MB association arm preceding
the program by one day.)

| Date | Circuit, task (hypothesis) | Real | Rewire | Also measured |
| --- | --- | --- | --- | --- |
| 09-29 | MB, one-shot ARC association (H-MB-CLASS2-ASSOCIATION) | 0.600 | **0.800** (p=0.996) | shuffled-credit 0.400; engineered perceptron 0.917 |
| 09-30 | T4/T5, ARC motion decoding (H-T4T5-CLASS25-MOTION) | 0.3875 | **0.4306** (p=0.97) | twin 0.3917; engineered matcher 1.0000 |
| 10-02 | T4/T5, DSEC flow direction (H-T4T5-DSEC-DIRECTION) | 81.36° AE | **78.85°** | uniform-tau 78.09°; trivial 81.88°; GT-median 65.36° |
| 10-03 | T4/T5, DVS gesture (H-T4T5-DVS-GESTURE) | .410/.389/.427 | **.441/.424/.465** (p=0.985) | event-count .472/.444/.504 (p=0.989); twin below real every seed |
| 10-04 | Early filters, Brain-Score V1 (H-EARLYFILTER-BRAINSCORE-V1) | 0.0690 | **.083/.076/.073** | passthrough 0.0330; twin 0.0697 |
| 10-06 | MB, UCI gas drift (H-ALMB-GASDRIFT) | 0.4257 | **.434/.485/.465** | raw features 0.5022; chance p 5.2e-26 |

MEASURED, in one sentence: at validated class-2/2.5 fidelity, on
every external task tried, everything these benchmarks' metrics
reward survives a degree-preserving shuffle of the connectome's
specific wiring.

## 3. The measured positives

The kills were not nulls-about-everything. Each test's decomposition
also localized what DOES earn:

- **Anatomy as spatial index** (ARC, deployed): the compiled
  retinotopic eye map at 2.59x human action-cost baseline vs its
  scrambled twin at 11.59x — a 4.5x separation from retinotopy alone,
  identical machinery otherwise (0.3064/0.3058 replicated vs 0.1875
  permuted). The program's strongest surviving fly-positive, and it
  is static metadata, not dynamics.
- **Dynamics over their own input** (Brain-Score V1): the
  early-filter population roughly doubles the predictivity of its own
  input (0.0690 vs passthrough 0.0330) — the first arm in the program
  where a simulated circuit added anything over what the encoder
  handed it.
- **A working plasticity mechanism** (MB association): real beats
  shuffled-credit 0.600 vs 0.400 (p=0.019) — DAN-gated KC->MBON
  depression genuinely carries stimulus-specific credit. The
  mechanism works; the specific wiring under it is what added
  nothing.
- **Temporal heterogeneity contributes** (DVS): the uniform-tau twin
  sat below real in every seed — the per-type time constants do
  something. The rewire just does it better.
- **The engine and wiring run competitively on a community
  instrument** (flybench, Task 3 uniform row): MaleCNS rows above the
  reference configuration on all four summary rows (core 1.000 vs
  0.5667, hard 0.6044 vs 0.5366, graded 0.711 vs 0.639, specificity
  +0.282 vs +0.184; paired-check diff CI [-0.112, -0.030] excluding
  zero). An adapter-engineering result, scoped as such in its record.
- **Far-above-chance circuit codes everywhere**: every killed arm
  cleared its chance bar decisively (gas drift p 5.2e-26; DVS worst
  p 2.6e-42) — these circuits compute; the question the kills answer
  is whether the specific wiring is where the computation lives.

## 4. The synthesis, at tier

MEASURED: the regularity in section 2, plus the positives in
section 3.

INFERRED (bridge stated): what external benchmark metrics reward in
these circuits is the population transformation — sparse expansion,
temporal filtering, rectifying nonlinearity, spatial indexing — and
that transformation is a property of the degree sequences, weight
distributions, and cell-type parameters, which the rewire preserves
by construction. The specific synaptic permutation on top of them
contributes nothing that a linear readout of these tasks can see. The
positives fit the same reading: the surviving wins are a spatial
index (anatomy), a mechanism (plasticity rule), a parameter set
(time constants), and a transformation-over-input — none of them the
permutation.

Boundaries that are part of the claim, not decoration:

- Every null is about THE MODEL CLASS AT ITS FIDELITY, not the living
  fly. For PN->KC the null result is the ESTABLISHED literature's own
  prediction (Caron et al. 2013: approximately random convergence;
  Litwin-Kumar et al. 2017: random-like expansion suffices). For
  T4/T5 it is NOT — direction selectivity is wiring-specific in the
  fly (Maisak et al. 2013) — so the three T4/T5 kills are statements
  about class-2.5 graded dynamics plus linear probes, and a class-3
  reversal on that circuit would break this synthesis (the recorded
  falsifier).
- One declared encoder per test, with map noise now measured: two
  equally-arbitrary encoder permutations differ by 4.4 accuracy
  points on the same circuit (Task 6 scram arm). Single-map effect
  sizes carry that bound; every decisive comparison in section 2 was
  map-matched.
- The gas-drift test ran with the LK alpha-balance near zero in every
  arm — the gain-control bridge (AE-3) was tested with the knob
  effectively off, equally across arms. Not claimed either way for an
  active-gain configuration.

## 5. Open alternative explanations

Three explanations for the regularity remain live, none tested:

1. **Fidelity ceiling** — class-2/2.5 dynamics may be too coarse to
   express what the specific wiring does. Untested above class 2.5
   everywhere; the single most informative next measurement.
2. **Readout mismatch** — linear probes on spike counts and evoked
   integrals may not read what the wiring computes. Evidence against,
   for the MB: the association arm used the circuit's NATIVE readout
   (MBON valence through the real KC->MBON mask and the biological
   depression rule) and still lost to its rewire. Untested for the
   visual circuits.
3. **Task-statistics mismatch** — ARC frames, benchmark gestures and
   MOX drift are not the fly's ecological input statistics. Nothing
   in the record tests a naturalistic-statistics task.

## 6. The method record

- Score-adjacent expected-tier predictions: 0 for 16, the program's
  running counter, incremented by each registration's own
  pre-statement and propagated at each close. (Older registrations
  also cite a broader expected-tier counter that once read ~2 for 15;
  the two count different things, and the outward carriers all use
  the score-adjacent one.) Measured-tier statements ("I measured X
  under protocol Y") held throughout, including through two
  outside-the-program reversals recorded in the register (AP-4
  twice).
- The kill tests cost minutes to ~1 hour of compute each (DVS 453.5 s;
  Brain-Score 75.9 s; gas drift 76 min at 8 workers) and prevented
  five builds on dead premises: no DSEC dense-flow pipeline, no
  flybench calibrated submission, no NeuroBench integration, no
  BrainModel submission, and the Keyword-FSCIL/MB limb closed
  unbuilt via a pre-stated dual close.
- Four instrument bugs were caught by the instruments' own unit tests
  or review BEFORE any data contact (calibrated-adapter CSC axis;
  hex-window boundary epsilon; per-arm APL block in the alpha probe;
  the DVS memory layout, fixed with equivalence tests). Two API-drift
  BLOCKEDs (vendored brainio, 0-d time_bins) were fixed pre-verdict
  under the registered allowance, decision rules untouched.

## 7. What remains, and what would change the picture

Calendar-gated: Task 7 (MLPerf Tiny, ~early 2027, working-group
membership required) and Task 8 (community venues: the IJCNN 2027
competition proposal, due 2026-11-30, was analyzed NO-GO on
2026-10-07 — task8_venues/ijcnn2027_go_no_go.md; the nearest live
Task-8 vehicle is the IJCNN regular paper, due 2027-01-31, decidable
after the 2026-12-04 ARC results; the user has not yet decided), plus
the Task 1 release and submission dates (2026-11-01 / 2026-11-08).

Measurements that would move this synthesis, in information order:

1. Class-3 fidelity on ONE killed circuit (T4/T5 is the one where the
   literature disagrees with our null) — a reversal breaks section 4;
   a confirmation hardens it from "at this fidelity" toward the
   circuit.
2. A native-statistics task for one circuit (naturalistic motion or
   plume statistics) — tests explanation 3 directly.
3. An active-gain-control MB configuration on the drift corpus —
   discharges the AE-3 caveat.
4. Any future encoder-mediated test: multi-map designs, since map
   noise is now measured at ~4 points.

## 8. Record map

| Hypothesis | Verdict | Record |
| --- | --- | --- |
| H-MB-CLASS2-ASSOCIATION | refuted 09-29 | EXPERIMENTS.yaml; mb_association.py |
| H-T4T5-CLASS25-MOTION | refuted 09-30 | EXPERIMENTS.yaml; t4t5_motion_arm.py |
| H-T4T5-DSEC-DIRECTION | refuted 10-02 | EXPERIMENTS.yaml; task2_dsec_flow/ |
| H-FLYGI-FLYBENCH-ADAPTER | supported 10-01 | EXPERIMENTS.yaml; task3_flybench/ |
| H-FLYGI-FLYBENCH-CALIBRATED | refuted 10-03 | EXPERIMENTS.yaml; task3_flybench/ |
| H-T4T5-DVS-GESTURE | refuted 10-03 | EXPERIMENTS.yaml; task4_neurobench/ |
| H-EARLYFILTER-BRAINSCORE-V1 | refuted 10-04 | EXPERIMENTS.yaml; task5_brainscore/ |
| H-ALMB-GASDRIFT | refuted 10-06 | EXPERIMENTS.yaml; task6_enose/ |

Assumption register: docs/arenas/ASSUMPTIONS.md (AP/AD/AF/AN/AB/AE
rows, annotated in place, never deleted). Durable narrative:
WORKLOG.md. Outward fact base: docs/arenas/task1_arc_paper/
factsheet.md.

## Addendum 2026-10-11 — Task 9 (CX latent state, off-survey)

A user-directed ninth task asked whether the compiled CX carries a
heading latent — the fly's established world-model fragment. Outcome,
both halves measured, full record in EXPERIMENTS.yaml and
docs/arenas/task9_cx_latent/:

- **Stage A (H-CX-RING-TOPOLOGY): SUPPORTED — the series' first
  PASS.** The real CX wiring carries ring-compass topology its
  degree-preserving rewires cannot produce: bandedness 0.5881 vs null
  max 0.3376, PEN_a mirror-peak 0.01445 vs 0.00792, each at the
  empirical floor over 200 rewires. The first measured property of
  the real wiring that its own null cannot reproduce.
- **Stage B (H-CX-HEADING-LATENT): closed "null" — untestable at
  classes 1-2 under the registered protocol.** The premise's two
  required properties exist in the record only in disjoint
  regime x protocol combinations: persistence at gain 2.0 wedge-write
  (fixed-point, not a continuum), opposite-signed steering at
  gain 1.5 under visual-arc seeding, and NO persistence at gain 1.5
  wedge-write (the class-1 grid and the Stage-B precheck, two
  independent runs concurring); class-2 delocalized everywhere.

What this does to the synthesis: it REFINES rather than breaks it.
Section 4's reading said the surviving wins are an index, a
mechanism, a parameter set, and a transformation — never the
permutation. Stage A adds a second anatomy-tier positive: the
permutation IS detectably special in the CX, structurally. What still
has no measured win is the permutation DOING anything at simulable
fidelity: even where the structure is real and null-detectable, no
class-1/2 regime runs it as the compass it anatomically resembles.
That sharpens the fidelity-ceiling explanation (section 5, option 1)
and moves the CX ahead of T4/T5 as the class-3 candidate: it now
holds the structural PASS, the gain-2.0 persistence separation, AND a
concrete protocol question (visual-arc vs wedge-write seeding at
gain 1.5) that a cheap registered probe could settle. Neither runs
without an explicit go.
