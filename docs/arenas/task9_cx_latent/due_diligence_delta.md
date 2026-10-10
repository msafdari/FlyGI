# Task 9 (off-survey, user-directed 2026-10-10) — CX latent state

Does the central complex of the compiled MaleCNS graph carry a latent
representation of spatial state — a heading "world model" — that its
specific wiring, and not a degree-preserving shuffle of it, supports?
User go 2026-10-10 ("Go. Do them all."), staged per the operating
directive: structural kill test first, dynamics only on a structural
PASS. Scope fixed at the outset: the testable claim is a HEADING
LATENT (maintain + update a heading estimate without visual input),
which is the fly's established world-model machinery — not "a world
model of the physical environment," which no experiment here can
license.

## What is already measured (the richest prior record in the program)

The CX is not untested — it is the ONE circuit where the real wiring
has ever beaten its rewire dynamically, and the record localizes
exactly what works and what fails:

- **H-CX-RING-ATTRACTOR (2026-09-25, class-1 rate dynamics, full
  graph, gain 2.0):** the real graph sustains persistent EPG activity
  120+ darkness steps (mass stable at 0.27, drift < 2 deg) while the
  degree-preserving null DIES by t=40 (mass 0.00) — the project's
  first anatomy-specific dynamical separation. But at that operating
  point the bump is broad (circvar 0.83) and PEN steering is
  same-signed from both hemispheres (broken).
- **The regime sweep (same record):** at WHOLE-network gain 1.5 the
  ring WORKS — circvar 0.52 and opposite-signed rotation under PEN
  left/right drive (+0.07/−0.33 and +0.34/−0.05 deg/step). The
  compiled transmitter signs match compass biology exactly (Delta7
  100% inhibitory; EPG/PEN/PEG 100% excitatory) — the regime, not the
  sign heuristic, is what breaks gain 2.0.
- **H-CX-CALIBRATION (refuted, 2026-09-25):** steerability is a
  global-regime property — circuit-local scaling (intra-CX 0.4-0.75,
  even plus all 29k external->CX edges at 0.75) cannot transplant it
  into the gain-2.0 network. The compass functions only when the
  whole brain runs near gain 1.5.
- **H-CX-SCRATCHPAD (refuted, 2026-09-27, AT GAIN 2.0):** position is
  not stored at the deployed point — eight write angles settle onto
  TWO fixed points (one robust ~222 deg, one vestigial), half the
  ring dies outright; the persistence is fixed-point attraction, not
  a ring continuum. SCOPE: measured at gain 2.0 only.
- **fc2_eb_ring (class-2 LIF):** all 155 alive configurations
  delocalized — the class-2 model holds activity, not position.
- **ESTABLISHED:** EPG instance labels carry PB wedge ids L1-L8/R1-R8
  (the 16-wedge, 22.5-deg mapping used by cx_ring/cx_scratchpad,
  correct up to a fixed rotation — AC-1); heading persistence in
  darkness and self-motion updating are measured fly biology (Seelig
  & Jayaraman 2015); the CX wiring is highly structured, not random
  (Hulse et al. 2021, hemibrain) — the OPPOSITE prior from PN->KC.

## The two genuinely unmeasured questions

1. **Structural (Stage A):** does the MaleCNS CX carry the
   ring-compass TOPOLOGY — circularly banded EPG<->EPG coupling
   through PEN under the anatomical wedge ordering, and
   opposite-signed left/right PEN offsets (the shifter) — at a level
   its degree-preserving rewires cannot produce? Hulse established
   this qualitatively on hemibrain; it has never been run here, on
   this dataset, as a preregistered null comparison. Pure linear
   algebra on the subcircuit matrix; no dynamics.
2. **Dynamical latent (Stage B, gated on A):** at the MEASURED
   working regime (whole-network gain 1.5 — where steering works but
   position storage was NEVER tested; the scratchpad settle map ran
   only at 2.0), is the persistence a CONTINUUM (many stable angles,
   not two fixed points), and does the bump TRACK integrated PEN
   self-motion commands — and does the CX-rewired control fail where
   the real wiring succeeds (the null comparison also never ran at
   1.5)?

## Why this is the synthesis's best-shot experiment

Every rewire-over-real result so far came from circuits the
literature calls near-random (PN->KC) or where fidelity may be too
coarse (T4/T5). The CX is the maximally-structured counterpoint, and
it already owns the program's one measured wiring-specific
separation. A Stage-A/B PASS yields the program's first positive
wiring result and a scoped heading-latent claim; a KILL on the
circuit most favorable to wiring is the strongest confirmation the
transformation-not-permutation synthesis can get. Informative in
both directions, which is the shape of question this program exists
to ask.

## Trivial alternatives (named before anything is built)

- Stage A (structural claim): the null IS the trivial alternative —
  200 degree-preserving rewires of the extracted CX subcircuit.
- Stage B (functional claim): the engineered equivalent is a
  2-variable Python integrator, which performs perfect path
  integration by construction. Stated as the ceiling context, not a
  bar (the motion-arm precedent): the fly claim is real-vs-rewire,
  never real-vs-integrator.

## Tier discipline for these registrations

Neither stage predicts a benchmark score, so the 0-for-16
score-adjacent counter is NOT incremented by them and no score
improvement is expected or implied (any such claim would carry that
base rate). As expected-tier circuit-function predictions they carry
their own priors honestly: Stage A is the program's FIRST
registration whose priors favor PASS (the measured persistence
separation + Hulse-established structure); Stage B's priors are mixed
(steering measured to work at 1.5; position storage unmeasured there;
class-2 delocalized everywhere; regime-transplant risk AC-2).

## Cost

Stage A: seconds-to-minutes locally (a 148-neuron induced subgraph,
two-hop products, 200 rewires). Stage B: full-graph class-1 rate runs
(the cx_ring machinery, ~166,700 nodes) across 4 seed angles x
(1 real + 3 rewired) arms + 3 tracking sequences — order an hour
locally on the cx_ring precedent. Both data-gated (compiled runtime
is local-only); instruments' pure parts unit-tested in-cloud,
Stage A's pipeline validated on synthetic rings before any data
contact.
