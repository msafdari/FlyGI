# Fidelity class 2 — Domain 2: temporal heterogeneity for direction selectivity

Research pass, 2026-09-29. Anchor: Lappalainen et al. 2024, *Nature* 634:1132
("Connectome-constrained networks predict neural activity across the fly visual
system", "flyvision"/flyvis). All statements below were verified against the
open-access PMC full text (PMC11525180), the flyvis source code
(`flyvis/network/dynamics.py`, `flyvis/config/network/*` on GitHub main), or the
cited primary physiology papers, except where a row is explicitly labelled
**ASSUMED**. Class-1 failure this domain addresses: frozen uniform tanh rate
model produced **no direction selectivity — no delay lines** (measured,
benchmark grid commit 6a74edf).

## 1. Verified model form (what reproduced T4/T5 DS from the connectome)

Lappalainen et al.'s dynamics, verified against both the Methods and the actual
implementation (`PPNeuronIGRSynapses`, "passive point neurons with
instantaneous graded release synapses"):

```
tau_ti * dV_i/dt = -V_i + V_ti^rest + sum_j( sign_titj * alpha_titj * N_ij * relu(V_j) ) + x_i(t)
```

- `V_i` — graded voltage (a.u., not mV). **No spikes, no threshold/reset, no
  refractory.** Rectification `relu(V_j)` is applied to the **presynaptic**
  voltage at the synapse (graded release), not to the neuron's own state. The
  task decoder additionally rectified voltages, but that is plumbing.
- `tau_ti` — **one time constant per cell type** (shared by all neurons of the
  type). Trainable. Initialized 50 ms (`time_const.yaml: value: 0.05`,
  groupby type), clamped `tau >= dt` at every use (verified in code:
  `torch.max(time_const, dt)`).
- `V_ti^rest` — **one resting potential per cell type**, enters as additive
  bias and as the initial state. Init sampled N(mean 0.5, std 0.05) a.u.
  (`bias.yaml`). Trainable. This is what places each type near or far from the
  release threshold (relu at 0) and thereby sets tonic drive.
- `sign_titj` — **fixed** ±1 per (source type, target type), from
  neurotransmitter/receptor annotation (`sign.yaml: requires_grad: false`).
  ACh → +1; GABA, Glu → −1 (Glu inhibitory via GluClα; critical for Mi9→T4).
- `alpha_titj` — unitary synapse strength, **one per connected type pair**,
  init `0.01 * <N_titj>`, clamped non-negative (`syn_strength.yaml`,
  `clamp: non_negative`). Trainable.
- `N_ij` — synapse count between neurons i,j, **fixed from the connectome**
  (FIB-25/FAFB-derived hexlattice; for us: MaleCNS).
- Scale of freedom: 734 free parameters total = 65 types × (tau + rest) + 604
  type-pair strengths; 45,669 neurons, 721 columns, 1,513,231 synapses. CT1 is
  split into **CT1(M10) and CT1(Lo1) as two separate "types"**, i.e. the giant
  cell is compartmentalized (see §4, Risk R1).
- Integration: forward Euler; training stimuli at 50 Hz (Sintel, dt = 20 ms);
  flash/moving-edge evaluation at **dt = 5 ms**. tau clamp ties resolution to dt.

All of the above: **ESTABLISHED** (paper + code).

What training found (ESTABLISHED, paper): task-optimal models reproduced T4/T5
direction selectivity and, for the models with correct T4 tuning, the correct
contrast selectivity of Mi4 and Mi9. Mechanism in the task-optimal cluster:
**fast central excitation plus spatially offset, delayed (slow) inhibition** —
Mi4 (trailing side) for T4; delayed CT1(Lo1) inhibition plus offset Tm9
excitation for T5. That is the connectome + per-type-temporal-parameter recipe
this class-2 model must copy.

**Trained per-type tau values are NOT published as a table** in the paper or
supplement. They exist in the released ensemble checkpoints
(github.com/TuragaLab/flyvis, 50 task-trained models; docs: "derived arrays
contain connectivity indices, trained weights, biases and time constants").
Retrieval requires downloading the pretrained ensemble (not done in this
research pass — heavyweight download; flagged as implementation step I5).
Section 3 therefore gives the fast/slow classification per type with ranges,
per the physiology, each row labelled.

## 2. Verified physiology anchors (what the taus must reproduce)

| Fact | Value | Source | Label |
|---|---|---|---|
| Mi1 filter time-to-peak (in vivo whole-cell, white noise) | 71 ± 3.8 ms | Behnia et al. 2014 Nature (PMC4243710), Results | ESTABLISHED |
| Tm3 filter time-to-peak | 53 ± 5.2 ms | same | ESTABLISHED |
| Tm1 filter time-to-peak | 56 ± 3.8 ms | same | ESTABLISHED |
| Tm2 filter time-to-peak | 43 ± 2.7 ms | same | ESTABLISHED |
| Mi1−Tm3 peak-time difference (ON delay pair) | 18 ms (p<0.01) | same | ESTABLISHED |
| Tm1−Tm2 peak-time difference (OFF delay pair) | 13 ms (p<0.002) | same | ESTABLISHED |
| Correlator built from those filters peaks at | ~1 Hz temporal frequency | same; also T4/T5 measured optimum ~1 Hz, Arenz et al. 2017 Curr Biol 27:929 | ESTABLISHED |
| Band-pass (transient) types | L1, L2, L4, Mi1, Tm3, Tm1, Tm2, Tm4, CT1 | Arenz 2017; Borst–Haag–Mauss 2020 review (PMC7069908 Fig 5c); Borst 2025 J Comput Neurosci (10.1007/s10827-025-00914-5) | ESTABLISHED |
| Low-pass (sustained) types | L3, Mi4, Mi9, Tm9 | same three sources | ESTABLISHED |
| T4 excitation/inhibition RF lobes spatially offset by | ~6° (≈1 column) | Gruntman, Romani, Reiser 2018 Nat Neurosci (PMC5967973) | ESTABLISHED |
| T4 hyperpolarizing input side | trailing side only (relative to PD) | same | ESTABLISHED |
| T4 conductance-model kinetics | excit. tau ~5–10 ms; inhib. tau ~50–100+ ms; membrane tau negligible–50 ms | same, Methods/Supp Fig 6b | ESTABLISHED (their fitted model, not direct measurement) |
| T4 voltage DS mechanism in whole-cell data | null-direction suppression only ("arises solely from ND suppression") | same | ESTABLISHED |
| T5 leading side depolarizing, slower rise; trailing side mixed with hyperpolarization, faster decay; no PD-enhancing nonlinearity found | — | Gruntman, Romani, Reiser 2019 eLife (PMC6917495) | ESTABLISHED |
| PD-enhancement also exists (calcium/apparent motion; leading side) | enhancement on preferred side, suppression on null side | Haag et al. 2017 eLife (PMC5582866); Fisher 2015 | ESTABLISHED (note tension with Gruntman voltage data — protocol-dependent) |
| T4 dendrite input arrangement | Mi9 distal tip (leading/PD side); Mi1, Tm3 central; Mi4, C3, CT1(M10) proximal base (trailing/ND side); CT1 ~15 syn/column to T4 | Shinomiya et al. 2019 eLife (PMC6338461) | ESTABLISHED |
| T5 dendrite input arrangement | Tm9 distal tip (leading side); Tm1, Tm2, Tm4 central; CT1(Lo1) proximal base (trailing side); CT1 ~60 syn/column to T5 | same | ESTABLISHED |
| Input signs | Mi1, Tm3, Tm1, Tm2, Tm4, Tm9 cholinergic (+); Mi4, C3, CT1, TmY15 GABAergic (−); Mi9 glutamatergic (−, GluClα) | same; Borst 2020 review | ESTABLISHED |
| CT1 is one giant cell whose per-column terminals act as independent functional units (ON in medulla M10, OFF in lobula Lo1) | — | Meier & Borst 2019 Curr Biol, via Borst 2020 review (PMC7069908) | ESTABLISHED |
| Uniform passive membrane (40 ms) + connectome alone does NOT give the transient class; an intrinsic H-current in L1/L2/L5 is required ("turning off the H-current ... leaving only sustained responses") | — | Borst 2025 J Comput Neurosci | ESTABLISHED |
| Modeling anchor for the slow arm | single low-pass tau = 150 ms tuned to put PD optimum at ~1 Hz | Zavatone-Veth, Badwan, Clark 2020 J Vision (PMC7343402) | ESTABLISHED (a model's choice, not a measurement) |
| T4/T5 subtypes a,b,c,d prefer front-to-back, back-to-front, up, down; project to lobula-plate layers 1–4 | — | Maisak et al. 2013 Nature | ESTABLISHED (not re-verified this pass; textbook-level) |

Caution on conventions: Behnia 2014 (two-arm HRC framing) makes **Mi1 the
delayed arm vs Tm3** and **Tm1 delayed vs Tm2**; the current three-arm view
(Arenz 2017, flyvision) puts the large delay in the flanking slow types
(Mi9/Mi4 for T4, Tm9/CT1 for T5) with Mi1/Tm3 (and Tm1/Tm2/Tm4) together as the
fast center. Both delays are real; the 13–18 ms center-pair asymmetry is a
second-order refinement on top of the ~100 ms flank-vs-center asymmetry.

## 3. Deliverable: minimal per-type temporal parameter table

Model form assumed for class 2: the verified equation of §1 (graded leaky
integrator, per-type tau, per-type rest, rectified release), run on MaleCNS
counts. "Effective tau" means the single first-order constant standing in for
the cell's full filter; the mapping from measured time-to-peak / sustainedness
to a first-order tau is itself **ASSUMED** (stated per row). Ranges are the
recommended search window; the single value is the recommended starting point.

| Cell type | Role in DS circuit | Class | tau start (ms) | tau range (ms) | Sign of output | Source for class | Value label |
|---|---|---|---|---|---|---|---|
| R1–R6 (R7/R8 if driven) | luminance input | fast | 10 | 5–20 | histaminergic (−) onto L1–L3 | Juusola & Hardie 2001 (photoreceptor kinetics); not re-verified | ASSUMED |
| L1 | ON relay, sign-inverting | fast band-pass | 15 | 5–30 (+ high-pass, see I3) | − in, relay + | Arenz 2017; Borst 2025 (transient; H-current) | ASSUMED value, ESTABLISHED class |
| L2 | OFF relay | fast band-pass | 15 | 5–30 (+ high-pass) | as L1 | same | ASSUMED value, ESTABLISHED class |
| L3 | sustained luminance to both pathways | slow low-pass | 150 | 100–300 | − (histamine in), sustained out | Silies 2013; Borst 2025 (sustained) | ASSUMED value, ESTABLISHED class |
| L4 | OFF-pathway lateral | fast | 20 | 10–40 | — | Borst 2025 (transient) | ASSUMED value, ESTABLISHED class |
| L5 | ON-pathway relay | fast (weakly characterized) | 25 | 10–60 | — | Borst 2025 gave L5 an H-current | ASSUMED (both) |
| **Mi1** | T4 center, fast excitation | fast band-pass | 20 | 10–40 | + (ACh) | Behnia 2014: peak 71 ms; Arenz 2017 band-pass | ASSUMED value, ESTABLISHED class |
| **Tm3** | T4 center, fast excitation, ~18 ms faster than Mi1 | fastest ON | 12 | 5–25 (keep tau_Tm3 < tau_Mi1) | + (ACh) | Behnia 2014: peak 53 ms | ASSUMED value, ESTABLISHED class + ordering |
| **Mi4** | T4 trailing/ND arm, delayed inhibition | slow low-pass | 150 | 100–300 | − (GABA) | Arenz 2017; Strother 2017; flyvision mechanism | ASSUMED value, ESTABLISHED class |
| **Mi9** | T4 leading/PD arm, slow OFF-center disinhibition | slow low-pass | 150 | 100–300 | − (Glu/GluClα) | Arenz 2017; flyvision (predicts OFF-selective Mi9) | ASSUMED value, ESTABLISHED class |
| **CT1(M10)** | T4 trailing inhibition (per-column unit) | band-pass, medium | 50 | 20–100 | − (GABA) | Meier & Borst 2019; Borst 2020 Fig 5c | ASSUMED value, ESTABLISHED class |
| **Tm1** | T5 center excitation | fast band-pass | 20 | 10–40 | + (ACh) | Behnia 2014: peak 56 ms | ASSUMED value, ESTABLISHED class |
| **Tm2** | T5 center excitation, fastest OFF | fast band-pass | 12 | 5–25 (keep tau_Tm2 < tau_Tm1) | + (ACh) | Behnia 2014: peak 43 ms | ASSUMED value, ESTABLISHED class + ordering |
| **Tm4** | T5 center excitation | fast band-pass | 20 | 10–40 | + (ACh) | Serbe 2016; Borst 2025 (transient) | ASSUMED value, ESTABLISHED class |
| **Tm9** | T5 leading/PD arm, slow sustained excitation | slow low-pass | 200 | 100–500 | + (ACh) | Serbe 2016; Arenz 2017 (sustained) | ASSUMED value, ESTABLISHED class |
| **CT1(Lo1)** | T5 trailing/ND arm, delayed inhibition (per-column unit) | slow-ish band-pass | 80 | 50–150 | − (GABA) | flyvision mechanism ("delayed CT1 inhibition"); Meier & Borst 2019 | ASSUMED value, ESTABLISHED role |
| C2, C3, TmY15 | additional GABAergic feedback onto T4/T5 base | medium | 50 | 20–100 | − (GABA) | Shinomiya 2019 (anatomy, sign) | ASSUMED value, ESTABLISHED sign |
| **T4a–d** | ON DS output; DS from inputs, not intrinsic | fast membrane | 20 | 10–50 | + (ACh) | Gruntman 2018 model: membrane negligible–50 ms | ASSUMED value, ESTABLISHED range |
| **T5a–d** | OFF DS output | fast membrane | 20 | 10–50 | + (ACh) | Gruntman 2019 | ASSUMED value, ESTABLISHED range |

Resting potentials (all a.u., flyvision convention): start every type at
V_rest = 0.5 ± 0.05 (ESTABLISHED as flyvision's init, `bias.yaml`; using it
untrained is ASSUMED), except Mi9 and Tm9, whose tonic release is what the
leading-side mechanism rides on — they must sit clearly above the relu
threshold at rest (ASSUMED; check: nonzero baseline Mi9→T4 current before
stimulus). Unitary strength: alpha init = 0.01 × mean synapse count per pair,
clamped ≥ 0 (ESTABLISHED as flyvision's init; keeping it untrained is ASSUMED
and is Risk R4).

The delay-line asymmetry this table encodes (the actual mechanism):

- **T4 (ON)**: leading side = slow **Mi9 disinhibition** (OFF-center: ON edge
  crossing its column shuts off its inhibition, slowly), center = fast
  **Mi1+Tm3 excitation**, trailing side = slow **Mi4 + CT1(M10) (+C3)
  inhibition** → PD motion collects release-then-excitation in phase; ND motion
  runs into standing inhibition. Slow arm(s): Mi9, Mi4. Fast arm: Mi1/Tm3.
- **T5 (OFF)**: leading side = slow sustained **Tm9 excitation**, center = fast
  **Tm1/Tm2/Tm4 excitation**, trailing side = delayed **CT1(Lo1)** (+TmY15)
  inhibition. Slow arm: Tm9 (excitatory! — unlike T4), CT1(Lo1). Fast arm:
  Tm1/Tm2/Tm4.
- Voltage-clamp ground truth to test against: ND suppression is the dominant
  measured mechanism in T4/T5 membrane potential (Gruntman 2018, 2019); PD
  enhancement appears in calcium and apparent-motion protocols (Haag 2017).
  A class-2 pass does not require PD enhancement; it requires DSI > 0 with the
  right preferred direction per subtype and a ~1 Hz temporal-frequency optimum.

## 4. Implementation guidance (what the engine must support)

- **I1 — Per-type tau and per-type rest.** One tau and one V_rest per cell
  type, table-driven, not global. This is the single change that most directly
  targets the class-1 DS null. Graded leaky integration with rectified release
  (the §1 equation) is the verified-sufficient dynamics; a spiking LIF layer on
  top is optional and riskier (R2), so the engine must support running these
  populations in **graded mode** (no threshold/reset), with relu applied to
  presynaptic state at the synapse.
- **I2 — dt ≤ 5 ms.** The delays being modeled are 13–18 ms (center pairs) and
  ~100 ms (flanks); flyvision evaluated at 5 ms and clamps tau ≥ dt. Use dt =
  1–2 ms if cheap, 5 ms otherwise.
- **I3 — A transience source in the lamina.** Borst 2025: connectome + uniform
  membranes leaves everything sustained; flyvision gets transience from
  trained taus + recurrence; physiology says L1/L2 carry an H-current. Minimal
  engine support: allow a per-type **high-pass/adaptation stage** (subtract a
  slow-filtered copy: y = relu(V − LP_tau_a(V)), tau_a ≈ 100–500 ms, ASSUMED)
  on L1/L2 (optionally L5). If the engine cannot afford it, the band-pass
  classes' short taus partially substitute, but flash responses will be
  sustained-only and the flash benchmark will show it.
- **I4 — CT1 (and any wide-field/amacrine cell) must be compartmentalized
  per column**, minimum split CT1(M10) vs CT1(Lo1), correct split = one unit
  per column terminal. flyvision did this (65 types from 64). A point-LIF CT1
  in the MaleCNS graph sums the whole visual field and turns local trailing
  inhibition into global gain — silently. Same check for other optic-lobe-wide
  cells (Am1, Dm/Pm families, Mt/LPi wide-field types) before trusting them.
- **I5 — Pull exact taus from the released ensemble at implementation time.**
  `pip install flyvis`, download pretrained models, average `time_const` per
  type over the task-optimal cluster; replace column "tau start" above and
  re-label those rows ESTABLISHED(model-derived). Until then the table's
  ranges are the spec, and the DS benchmark must be robust to anywhere in the
  ranges (sweep tau_slow ∈ {100, 150, 200, 300} ms first — it is the
  load-bearing constant).
- **I6 — Signs from curated table, not raw NT predictions.** Enforce the sign
  table in §2; in particular Mi9→T4 negative (Glu/GluClα) and photoreceptor→
  L1/L2/L3 negative (histamine). Grep the MaleCNS NT annotations for
  disagreements and record each override with provenance.
- **I7 — Retinotopy is a precondition.** The spatial offset (~1 column,
  Gruntman) comes from which-column-feeds-which-dendrite-zone. The subcircuit
  extraction must preserve per-column identity of Mi9/Mi4/Tm9/CT1 inputs to
  each T4/T5 (MaleCNS synapse positions/column assignments), and the stimulus
  encoder must drive photoreceptors in true retinotopic layout (the class-1
  scrambled-input null is the standing warning here).
- **I8 — Benchmark protocol** (preregister before running, per repo practice):
  ON and OFF edges/gratings, 8 directions, 3 speeds bracketing 1 Hz temporal
  frequency; measure per-subtype DSI on T4a–d (ON) and T5a–d (OFF); pass =
  correct preferred direction per subtype (a: front-to-back, b: back-to-front,
  c: up, d: down), DSI significantly > degree-preserving-null DSI, and TF
  optimum in 0.5–2 Hz. Trivial alternative to name in the plan: same anatomy
  with **uniform tau** (class-1 conditions) must stay at DSI ≈ 0, or the taus
  were not the cause.

## 5. Risks (what most likely blocks the benchmark even at class 2)

- **R1 — CT1 as a point neuron.** Highest-confidence blocker; see I4. In the
  MaleCNS graph this is one cell; unsplit, it globally couples all columns.
- **R2 — Spiking discretization destroys the delay code.** The circuit is
  graded; 13–18 ms center asymmetries are sub-spike-interval at realistic
  rates. If class 2 insists on thresholded spiking LIF everywhere, DS may fail
  for engine reasons, not fly reasons — and the null would be mislabelled. Run
  graded mode first; add spiking only downstream of T4/T5.
- **R3 — Untrained gain balance.** flyvision's DS is with *trained* alpha and
  V_rest; we freeze them at init. With count-proportional weights, one global
  gain either saturates the relu or silences T4. Expect a 1-D gain calibration
  (target: all types' baseline activity finite and nonzero, as flyvision's
  activity penalty enforced) before any DS claim. This is calibration
  plumbing, not intelligence, but label it.
- **R4 — Slow-arm tau wrong by 2×** moves the TF optimum off 1 Hz and can
  halve DSI; hence the I5/I8 sweep. The fast/slow *classification* is solid;
  every specific millisecond in §3 is ASSUMED until the ensemble values are in.
- **R5 — Sign/NT mislabels in MaleCNS** (especially glutamate) flip an arm's
  polarity; one flipped Mi9 or Mi4 inverts or abolishes DS. I6 is the control.
- **R6 — Missing or collapsed retinotopy in the extracted subcircuit** (I7):
  without the ~1-column input offset there is no direction axis at all; no tau
  setting can rescue it.
- **R7 — Base rate.** Prior expected-to-help changes in this repo: 0 for 11.
  This domain's claim is only "the verified recipe (anatomy + per-type
  temporal parameters + signs) is the minimal known-sufficient set for DS";
  whether our frozen-parameter variant of it passes on MaleCNS is **Expected**,
  not Measured, until I8 runs.

## Sources

- Lappalainen et al. 2024, Nature 634:1132. PMC11525180; code
  github.com/TuragaLab/flyvis (dynamics + config verified from source).
- Behnia, Clark, Carter, Clandinin, Desplan 2014, Nature 512:427. PMC4243710.
- Arenz, Drews, Richter, Ammer, Borst 2017, Curr Biol 27:929 (paywalled;
  classification corroborated via PMC7069908 and Borst 2025).
- Gruntman, Romani, Reiser 2018, Nat Neurosci 21:250. PMC5967973.
- Gruntman, Romani, Reiser 2019, eLife 8:e50706. PMC6917495.
- Shinomiya et al. 2019, eLife 8:e40025. PMC6338461.
- Haag, Arenz, Serbe, Gabbiani, Borst 2017, eLife 6:e29044. PMC5582866.
- Borst, Haag, Mauss 2020, J Comp Physiol A (review). PMC7069908.
- Borst 2025, J Comput Neurosci, doi 10.1007/s10827-025-00914-5.
- Zavatone-Veth, Badwan, Clark 2020, J Vision. PMC7343402.
- Maisak et al. 2013, Nature 500:212 (subtype directions; not re-verified).
