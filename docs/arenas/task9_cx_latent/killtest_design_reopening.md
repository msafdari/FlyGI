# Task 9 reopening kill tests — FROZEN 2026-10-11 (H-CX-SEEDING-PROTOCOL, H-CX-CLASS3-COMPASS)

Both registered BEFORE any instrument code, in one commit, so neither
can be tuned on the other or on the probe's outcome. Changes after
first data contact require a recorded instrument-bug finding and a
full re-run. The literature table below was assembled by a registered
research sweep BEFORE this freeze (reopening_delta.md; WORKLOG
2026-10-11); its sources are code-verified where stated.

---

## Probe — H-CX-SEEDING-PROTOCOL (class-1; instrument now)

### Premise

Stage B's failure was PROTOCOL-bound, not regime-bound: at an
operating point with measured steering, some declared seeding
protocol yields darkness persistence of a localized, POSITION-
FAITHFUL bump in the real CX that the CX-block rewires lack.

### Frozen design

- Machinery: cx_heading_killtest.py's loading/drive/read verbatim
  (class-1 rate dynamics, full compiled graph, INTERNAL_STEPS 4).
- OPERATING POINTS (2, frozen): (gain 1.5, leak 0.3) and
  (gain 2.0, leak 0.3) — the two points with measured C2 steering
  passes in the tracked cx_ring grid (git 09a998a).
- PROTOCOLS (4, frozen; P1 is the built-in reproduction control,
  measured dead): P1 wedge-write, 20 steps, scale 1.0 (cx_ring
  verbatim). P2 wedge-write, 100 steps, scale 1.0 (sustained write).
  P3 wedge-write, 20 steps, scale 3.0 (the fc2_eb_ring declared
  STIM_AMP_FACTOR). P4 direct state injection: EPG state set to 1.0
  inside the 90-deg wedge, 0.0 outside, all other nodes at
  initial_state; release (the cx_scratchpad write style; at gain 2.0
  its outcome is already measured — two fixed points — and is
  expected to reproduce).
- Angles: 22.5 (calibration) + 112.5/202.5/292.5 (held out).
  Darkness: 200 steps. Read: PVA/mass/circvar on the EPG positive
  lobe (circular_stats verbatim).
- CELL PASS RULE (real arm, per point x protocol cell): at >= 2 of 3
  held-out angles — retention >= 0.05 AND circvar <= 0.6 AND PVA
  within 45 deg of the seed angle (the position-faithfulness clause
  is what the gain-2.0 fixed-point mode fails).
- WIRING BAR: at every real-passing cell, run the 3 CX-block rewires
  (seeds 4242+0..2, the Stage-B cx_block_rewire); ALL must fail the
  same cell rule. Evaluation order frozen for cost honesty: real arms
  on all 8 cells first; rewires only at real-passing cells (decision-
  identical: the wiring bar is defined only there).
- PASS iff >= 1 cell passes both. Every cell x arm run is reported in
  full (no silent truncation). CONTEXT, non-decisional: at passing
  cells, the Stage-B tracking sequences are run and reported — the
  heading-latent VERDICT stays with a re-registered Stage B; this
  probe only decides whether such a re-registration is licensed and
  with which declared protocol.
- BLOCKED: runtime absent; CX composition != 46/20/22/42/18;
  instability (non-finite states) in > 20% of runs in any arm.

### Tier

Exploratory reconciliation with pre-stated pass rules; not
score-adjacent. Priors both ways (reopening_delta.md): steering
measured at both points; wedge-write persistence measured dead at
every grid point (twice at 1.5/0.3); the one persistence-positive run
used the unreproducible arc protocol.

---

## Class-3 — H-CX-CLASS3-COMPASS (instrument now; runs after the probe reports)

### What "class 3 (CX)" means here (definition, fixed)

Literature-pinned spiking physiology on connectome-count weights:
the Kakaria/Pisokas LIF-with-templates neuron and synapse model (the
model class in which fly-TOPOLOGY ring attractors are published to
work), applied to the REAL MaleCNS CX synapse counts with declared
per-connection-class scale factors. Above class 2 (uniform Shiu
conversion, all 155 configs delocalized), distinct from class 2.5
(flyvis-fitted, optic lobe only). The precedent gap this targets,
established by the registered sweep: connectome-weighted fly CX bumps
exist ONLY at rate tier with fitted per-type parameters (Biswas et
al. 2024 bioRxiv 2024.11.01.621596 — exact threshold-linear ring
attractors for all four connectomes INCLUDING MaleCNS; Duan, Dong &
Fiete, NeurIPS 2025 — hemibrain with learned per-type parameters,
which they show are NECESSARY); no spiking or conductance
connectome-weighted bump is published anywhere (absence finding,
sweep of 2026-10-11).

### Premise

At literature-pinned spiking physiology with declared per-class
scales, the real MaleCNS CX (standalone 148-neuron subcircuit)
passes the compass gate — localized persistent bump, position
CONTINUUM, opposite-signed steering — and its degree-preserving
rewires do not: the specific wiring computing, at a fidelity where
sibling topologies are published to work.

### Pinned physiology (ESTABLISHED; code-verified by the sweep)

Kakaria & de Bivort 2017 / Pisokas, Heinze & Webb 2020 (eLife
9:e53985), CODE values (the sweep measured a paper-vs-code
discrepancy: paper says Cm 2 nF / Rm 10 MOhm; the code that produced
the published results uses Cm 20 nF / Rm 1 MOhm — same tau_m 20 ms,
10x current-to-voltage gain; we pin the CODE values WITH the code's
weight conventions, as the sweep recommends): V_rest -52 mV,
threshold -45 mV, AP template 2 ms ending at -72 mV undershoot
(acts as refractory), unitary PSC = quarter-sine rise 2 ms +
exponential decay half-life 5 ms, peak 5 nA, truncated at 7
half-lives; excitatory/inhibitory PSCs equal magnitude, opposite
sign; forward Euler dt = 1e-4 s; background drive Poisson 5 Hz;
heading drive von Mises kappa = 3*pi/4 (FWHM ~90 deg) onto EPG,
peak 190 Hz; rotation drive Poisson onto one hemisphere's PEN_a.
Pisokas's optimized FLY class weights (unitary-PSC equivalents per
spike; from their published code, collect_stats_long_run.m:397):
E-PG->P-EN = E-PG->P-EG = 99.968; E-PG->Delta7 = 47.917;
P-EN->E-PG = P-EG->E-PG = 6.072; Delta7->P-EN = Delta7->P-EG =
-35.677; Delta7->Delta7 = -19.336.

### Weight mapping (AC-6, the declared invention)

Per-edge weight = MaleCNS synapse count x s_c, where s_c is one
scale per connection class (pre-type -> post-type), chosen so the
class's MEAN total drive per postsynaptic neuron per presynaptic
spike equals the Pisokas class weight:
s_c = W_c_Pisokas / mean_over_postsynaptic_cells(sum of class-c
counts onto that cell). Count heterogeneity — the connectome
structure under test — is preserved; only the class-level unit is
literature-pinned. Signs from the compiled consensus NT (measured
100% consistent with compass biology). Connection classes absent
from Pisokas's 4-type circuit (anything involving PEG beyond the
P-EG roles above, PEN_b, and any unlisted pairing) inherit the scale
of their nearest Pisokas class by role (PEN_b as P-EN; PEG as P-EG;
all remaining classes get the smallest excitatory scale) — declared,
not tuned.

### Frozen gate and bars

- VARIANT GRID (declared, 6 points, ALL reported): global synaptic
  scale x {0.5, 1.0, 2.0} crossed with inhibitory-class scale
  x {1.0, 2.0}. No other knob exists or is searched.
- G1 (continuum + persistence), per grid point, real wiring: 8 write
  angles every 45 deg (von Mises heading drive, 1 s), then 2 s
  darkness (background only); read = EPG spike counts in the final
  250 ms vs the 250 ms at release; pass at an angle iff retention
  >= 0.05, circvar <= 0.6, PVA within 45 deg of the write angle.
  G1 passes iff >= 6 of 8 angles pass (kills the fixed-point mode).
- G2 (steering): from two settled states, one-hemisphere PEN_a drive
  left vs right for 1 s -> opposite-signed PVA rotation, both
  |rate| >= 9 deg/s (0.05 deg per 100 ms window x the cx_ring floor
  convention, stated here once as deg/s).
- NULL BAR: at every grid point where real passes G1+G2, all 3
  rewires of the standalone matrix (degree_preserving_rewire, seeds
  4242+0..2) fail G1. Rewires are evaluated only at real-passing
  points (decision-identical, cost-honest).
- PASS iff >= 1 grid point passes G1+G2 with all rewires failing G1
  there. KILL otherwise — and a KILL here, at the model class where
  idealized fly topology is PUBLISHED to work, is the program's
  strongest possible statement that the compiled counts do not carry
  the compass at physiological fidelity.
- BLOCKED: runtime absent; composition mismatch; instability
  (non-finite membrane) in > 20% of runs in any arm; AND the
  in-cloud validation gate below failing — an invalid instrument,
  never a verdict.

### Instrument validation gate (in-cloud, BEFORE any data contact)

The engine must reproduce the PUBLISHED Pisokas fly result on their
OWN 60-neuron idealized circuit (16 P-EN + 18 P-EG + 18 E-PG +
8 Delta7, their class weights above, global Delta7 inhibition):
bump forms under the von Mises drive, persists 2 s of darkness with
PVA within 45 deg of the stimulus and circvar <= 0.6, and E-PG bump
FWHM in 60-120 deg (their Table 1: 88.3 deg). Asserted by unit test.
If the engine cannot reproduce the literature circuit, there is no
instrument and nothing about MaleCNS is claimed.

### Tier

Not score-adjacent. Expected-tier function prediction with priors
stated: FOR — Stage A's structural PASS (topology present), the
published fly-topology successes in exactly this model class, and
Biswas's rate-tier MaleCNS realizations; AGAINST — Duan & Fiete's
finding that per-type tuning is necessary at rate tier (our per-class
scales are pinned, not fitted), and this program's six-of-seven
rewire record on dynamics. Either outcome publishes; the
structure-without-computation split sharpens or breaks here.
