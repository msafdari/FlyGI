# Fidelity class 2 — Domain 3: KC sparse coding and EB ring-attractor regimes

Research pass, 2026-09-29. Sources verified against paper text via web fetch on
this date unless a row says otherwise. Labels follow the repository convention:
**ESTABLISHED** = taken from the literature with the source; **ASSUMED** =
chosen by us because something had to be chosen (best range + reasoning given).
Class-1 context: the frozen uniform tanh rate model produced a dense-or-silent
KC code (never 5–10% sparse) and an EB bump that was a static fixed point
(never movable). Both failures are regime failures this document parameterizes
away, not wiring failures.

---

## Part A — Kenyon cell sparseness

### What makes KCs sparse (mechanisms, each with its source)

1. **High spike threshold relative to synaptic drive.** KCs are tiny,
   high-input-resistance cells; single-claw input does not fire them
   (Turner et al. 2008 J Neurophysiol; Gruntman & Turner 2013 Nat Neurosci).
2. **Claw-count coincidence integration.** A KC has ~6–8 dendritic claws, each
   from one PN bouton; **more than half must be coactive** to elicit spikes
   (Gruntman & Turner 2013, optogenetic single-claw stimulation).
3. **APL feedback inhibition.** KCs excite APL; APL inhibits KCs via the
   GABA-A receptor RDL. Blocking APL output (shibire^ts) greatly boosts KC
   odor responses, densifies the code, and raises inter-odor correlations
   (Lin et al. 2014 Nat Neurosci, verified in PMC4000970).
4. **Fast EPSP decay curtailing temporal integration** (Turner et al. 2008,
   stated in abstract; primary full text paywalled — see row A9 note).

The class-1 diagnosis in these terms: a uniform tanh unit has no threshold
separate from its gain and the class-1 network has no functional APL loop, so
mechanisms 1–3 were all absent. Dense-or-silent is what remains.

### APL: verified non-spiking, model as a graded unit

**Verified.** "Like its locust homolog, the giant GABAergic neuron (GGN), APL
is non-spiking" (Amin et al. 2020 eLife 9:e56954, citing Papadopoulou et al.
2011 Science for GGN). Supporting: APL expresses the lowest voltage-gated
Na+/Ca2+ channel levels of all MB neuron types (Amin 2020, transcriptomics).
APL activity is also strongly **localized**: signal spread fit by space
constant **λ ≈ 50 µm**; activity decays to undetectable within ~100 µm, so one
APL acts as many local inhibitors (Amin 2020). Prisco et al. 2021 (eLife
10:e74172) show APL implements **divisive normalization** of KC responses in
the calyx.

**Class-2 treatment:** APL is a single graded (non-spiking) unit per
hemisphere: a leaky integrator with no threshold, reading connectome-weighted
KC activity, feeding back inhibition onto KCs with connectome weights.
**ASSUMPTION (labelled):** we collapse APL's λ≈50 µm locality to one global
unit for the first pass. This is the standard modeling simplification
(Litwin-Kumar 2017 does the same) but it is anatomically wrong in detail; if a
benchmark probes compartment-specific inhibition it will fail and the fix is
2–5 spatial APL segments, not a spiking APL.

### Parameter table A

| # | Parameter | Value / range | Units | Source (where) | Label |
|---|---|---|---|---|---|
| A1 | KC active fraction per stimulus (target) | 0.05–0.10 (reliable responders) | fraction | Turner 2008 (6±5% of 71 KCs, whole-cell, Results); Honegger 2011 J Neurosci 31:11772 (~5% of ~2500 KCs/hemisphere, ≥half-of-trials reliability criterion); Lin 2014 (intro: "~5–10%") | ESTABLISHED |
| A2 | KC count per hemisphere | ~2000–2500 | cells | Litwin-Kumar 2017 Neuron (M=2000, model spec); Honegger 2011 (~2500). Use the actual MaleCNS KC count | ESTABLISHED |
| A3 | PN inputs (claws) per KC | 6–8, mean ~7 | inputs | Gruntman & Turner 2013 (6–8 claws); Litwin-Kumar 2017 (K\*=7 optimal, "equal to the average observed number of PN inputs", verified in PMC5379477). Use MaleCNS in-degree; do not prune to 7 | ESTABLISHED |
| A4 | Coincidence requirement for KC spike | > half of claws coactive | — | Gruntman & Turner 2013 (optogenetics: "more than half of the 6–8 PN inputs need to be coactive") | ESTABLISHED |
| A5 | KC input resistance | > 10 | GΩ | Turner et al. 2008, as quoted verbatim by Ahmed et al. 2023 Curr Biol ("input resistance >10 GΩ (Turner et al., 2008)"); primary PDF is image-scanned/paywalled, number verified only through this citing text | ESTABLISHED (via citing paper) |
| A6 | KC membrane time constant | 8–20 (αβ-core longer than α′β′; per-type heterogeneity exists: Groschner 2018 Cell) | ms | No verified primary number obtained this pass; range from Rin ~10 GΩ × few-pF capacitance, discounted for in-vivo conductance load | ASSUMED |
| A7 | KC resting potential | −55 to −60 | mV | Not verified from primary text this pass; typical insect KC values (cockroach KC: threshold −47±6 mV, Rin 2.5±1 GΩ, C 2.7±0.8 pF — different species, context only) | ASSUMED |
| A8 | KC spike threshold | calibrated, not copied: set so (a) 1 claw-EPSP subthreshold, (b) >half claws coactive suprathreshold, (c) realized coding level hits A1 on the real input panel | mV | Procedure from Litwin-Kumar 2017 ("thresholds chosen so neurons activate with probability f"); constraint (a),(b) from Gruntman & Turner 2013 | ESTABLISHED (procedure); values ASSUMED |
| A9 | Model coding level f | 0.10 | fraction | Litwin-Kumar 2017 (f=0.1, "conclusions do not depend strongly on this parameter") | ESTABLISHED (model spec) |
| A10 | APL physiology | non-spiking, graded; GABAergic | — | Amin 2020 eLife (quote above; Papadopoulou 2011 for GGN homolog) | ESTABLISHED |
| A11 | APL locality | λ ≈ 50 µm space constant; decay to undetectable ≤ ~100 µm | µm | Amin 2020 (ATP-stimulation mapping + fit) | ESTABLISHED |
| A12 | APL feedback form | subtractive-balancing (J⁻=−α tuned to cancel mean excitation) or divisive normalization; loop gain is the free knob | — | Litwin-Kumar 2017 (subtractive, Methods); Prisco 2021 (divisive, calyx). Either satisfies class 2; declare which | ESTABLISHED (that feedback sparsens: Lin 2014); form choice ASSUMED |
| A13 | KC GABA receptor kinetics | RDL (GABA-A, fast Cl⁻); IPSP τ 5–10 | ms | Receptor identity: Lin 2014 ("Kenyon cells express the GABA-A receptor RDL"). Kinetic value not verified this pass | receptor ESTABLISHED; τ ASSUMED |
| A14 | PN drive statistics | calibrate on the engine's actual PN input distribution, not an odor panel | — | Consequence of A8/A9; and of the 2026-09-23 repo lesson (circuit must receive usable input before claims) | ASSUMED (procedure) |

### The knobs that move active fraction into 5–10%

Three, in order of leverage; sweep them in this order and freeze:

1. **Threshold offset θ** (global, or per-KC as θ_i = mean_i + z·std_i over the
   input panel): the direct coding-level control. Litwin-Kumar's procedure —
   pick θ to hit f — is the calibration, not a fit to be ashamed of.
2. **APL loop gain α**: raises effective threshold with population activity;
   controls dense-stimulus robustness and inter-stimulus decorrelation
   (Lin 2014). With α=0 you must reproduce the Lin 2014 phenotype
   (denser, more correlated code) — that is Part A's built-in control arm.
3. **Input scale** (PN→KC weight normalization): interacts with θ;
   fix it first from claw-EPSP constraint A8(a,b), then leave it alone.

Failure signature to watch: threshold alone with no APL gives sparseness that
collapses for strong/broad stimuli (dense) and silence for weak ones — i.e.,
class 1's dense-or-silent, reproduced at spiking fidelity. The APL loop is what
makes 5–10% hold *across* stimuli.

---

## Part B — EB ring attractor on real anatomy

### The regime that worked (Kakaria & de Bivort 2017, Front Behav Neurosci 11:8)

Spiking LIF on the full hand-traced PB–EB circuit: **60 neurons** — 18 E-PG,
16 P-EN, 16 P-EG, 10 PB-intrinsic (Δ7). All parameters below verified against
the article text.

| # | Parameter | Value | Units | Source (where) | Label |
|---|---|---|---|---|---|
| B1 | Neuron model | LIF, current-based synapses | — | K&dB 2017 Methods | ESTABLISHED |
| B2 | C_m | 0.002 (surface area 10⁻³ cm² assumed) | µF | K&dB 2017 Methods | ESTABLISHED |
| B3 | R_m | 10 | MΩ | K&dB 2017 Methods | ESTABLISHED |
| B4 | τ_m = R_m·C_m | 20 | ms | derived from B2×B3 | ESTABLISHED (derived) |
| B5 | V_rest | −52 | mV | K&dB 2017 Methods | ESTABLISHED |
| B6 | V_threshold | −45 | mV | K&dB 2017 Methods | ESTABLISHED |
| B7 | Spike shape / refractory | AP duration 2 ms, peak +20 mV, undershoot −72 mV (≈2 ms effective refractory) | ms, mV | K&dB 2017 Methods | ESTABLISHED |
| B8 | PSC amplitude I_PSC | 5 nA *as printed* — see consistency caution below | nA | K&dB 2017 Methods | ESTABLISHED (as printed) |
| B9 | PSC decay half-life | 5 | ms | K&dB 2017 Methods | ESTABLISHED |
| B10 | Synaptic strength | 20 PSC-equivalents/AP (excitatory); 15 (Δ7→P-EN, Δ7→P-EG inhibitory) → **inhibition ≈ 75% of excitation** | PSC equiv. | K&dB 2017 Methods + stability analysis | ESTABLISHED |
| B11 | Per-step noise | Gaussian, sd 3×10⁻¹⁰ V *as printed* | V | K&dB 2017 Methods | ESTABLISHED (as printed) |
| B12 | Timestep dt | 10⁻⁴ (0.1 ms) | s | K&dB 2017 Methods | ESTABLISHED |
| B13 | Trial duration | 2–4 | s | K&dB 2017 | ESTABLISHED |
| B14 | Background / stimulus drive | 5 Hz Poisson background; stimulus peaks 120 Hz | Hz | K&dB 2017 | ESTABLISHED |
| B15 | Transmitter signs | all excitatory unless evidence otherwise; Δ7 (Pintr) inhibitory | — | K&dB 2017 assumption; Δ7 inhibition since confirmed — B18 | ESTABLISHED |
| B16 | Robustness of regime | ~1.5% of 24,000 random ±100% weight perturbations kept full function | — | K&dB 2017 sensitivity analysis | ESTABLISHED |
| B17 | Motif required | local (wedge) excitation + long-range inhibition | — | K&dB 2017; Kim et al. 2017 Science 356:849 (winner-take-all + bump jumps ⇒ global-inhibition model fit their data best) | ESTABLISHED |
| B18 | Δ7 sign on real anatomy | glutamatergic (VGlut), inhibits E-PG via GluClα (GluClα mRNA in E-PG) | — | Turner-Evans et al. 2020 Neuron (hemibrain ultrastructure paper, PMC8356802) | ESTABLISHED |
| B19 | P-EN function | conjunctive heading × angular velocity; mirror-symmetric L/R; rate modulation ≈5.6±3.7 Hz between turn directions (n=12) | Hz | Turner-Evans et al. 2017 eLife 6:e23496 (PMC5440168) | ESTABLISHED |
| B20 | P-EN/E-PG phase offsets | EB: P-EN bump leads E-PG by ~20.7±11.7° at 150–180°/s (indicator-dependent; 7.3±7.2° reversed dyes); PB: lags by ~1 glomerulus (≈45° EB equivalent) at 120–150°/s | deg | Turner-Evans 2017 two-color imaging | ESTABLISHED |
| B21 | Rate-model integration quality | quasi-linear bump velocity vs input; ~30 ms model lag; heading error diffuses, D=1.82×10⁻³ rad²/s | — | Turner-Evans 2017 model section | ESTABLISHED |
| B22 | Uniform inhibition in rate model | "a pre-requisite to obtain a stationary bump ... and near-linear integration" | — | Turner-Evans 2017 model | ESTABLISHED |
| B23 | Low-velocity sticking | bump sticks below ~15°/s with discrete (9/side P-EN, 54 E-PG) populations | deg/s | Turner-Evans 2017 model | ESTABLISHED (model artifact) |
| B24 | MaleCNS weight mapping | replace 20/15 hand-set PSC-equivalents with connectome synapse counts, preserving the **ratio** Δ7-inhibition/E-PG-excitation ≈ 0.7–0.8 as the sweep center, gain as one global scalar per sign class | — | our mapping; ratio anchor from B10 | ASSUMED |

**Consistency caution on B8/B11 (flagged, do not silently "fix"):** 5 nA into
R_m=10 MΩ/C_m=2 nF implies tens of mV per PSC against a 7 mV rest-to-threshold
gap, and noise sd 3×10⁻¹⁰ V is physically negligible; the printed absolute
scales look internally inconsistent, though the published model demonstrably
worked as a system. Treat the **dimensionless structure** as the finding —
τ_m 20 ms, PSC decay 5 ms, 7 mV gap, inhibition/excitation ≈ 0.75, local-E /
global-I motif — and recalibrate absolute synaptic gain on our engine (one
scalar sweep until the 5 Hz background produces ~1–10 Hz spontaneous rates).
This is a labelled reimplementation ASSUMPTION.

### Known failure modes and what fixes each

| Failure (measured signature) | Cause | Fix |
|---|---|---|
| **Static fixed point / frozen bump — exactly the class-1 measurement** | No functional P-EN velocity loop (or zero L/R asymmetric drive), and/or zero noise: a bump with global inhibition and no rotation input *is* a fixed point | Wire E-PG→P-EN (PB, local) and P-EN→E-PG (EB, ±1 wedge shifted) from the connectome; drive L/R P-EN populations differentially for rotation; add noise (B11 intent). Pass criterion is bump *motion under asymmetric drive*, not mere bump existence |
| Seizure (everything fires) | Inhibition too weak vs excitation (K&dB failure modes 11–15) | Raise Δ7 gain toward inhibition/excitation ≈ 0.75 |
| Silence | Inhibition too strong or drive too weak (K&dB modes 1–3); also produced when PB→EB excitation sign is wrong | Lower Δ7 gain / check sign map (B18) |
| Multiple simultaneous bumps | Inhibition too local | Keep Δ7's anatomically broad (all-PB) projection; do not truncate its arbor |
| Bump too wide / poor competitor selectivity | Excitation/inhibition ratio marginal (K&dB modes 8–10) | Sweep the single global gain scalar; selectivity test = Kim 2017 winner-take-all: a second, stronger cue must *extinguish* the old bump (jump), not coexist |
| Bump sticks at low rotation speed | Population discreteness (16–18 wedges) | Expected artifact (B23); benchmark rotation at ≥30–60°/s, do not tune it away |

Note the trap for the benchmark: **winner-take-all is the correct dynamics**
(Kim 2017) — class 1 failed not by having WTA but by having *static* WTA. The
pass test must separate "unique bump that re-selects and moves" from "fixed
point": (1) unique bump forms; (2) persists ≥2 s after cue removal (Kim 2017
persistence in darkness, qualitative); (3) jumps to a stronger distant cue;
(4) rotates monotonically under sustained L/R P-EN asymmetry.

### Timestep and duration guidance

- Spiking (LIF) runs: **dt = 0.1 ms** (B12; resolves 2 ms AP and 5 ms PSC
  against τ_m 20 ms). Trials **2–4 s** for formation/competition (B13);
  **10–30 s** for persistence/drift tests.
- Rate-model variant (acceptable fallback for the CX benchmark only): dt = 1 ms
  is adequate; Turner-Evans 2017's rate model integrated velocity with ~30 ms
  lag. K&dB's own leaky-integrator (tanh(20·Σ)) variant kept bump formation but
  had *weaker competitor selectivity* than spiking — i.e., a rate class-2 CX
  may pass bump-persistence yet fail the WTA-jump test. Budget for spiking.

---

## Engine requirements implied by this domain

1. Per-type LIF parameters (τ_m, V_rest, V_thr, reset/undershoot, refractory);
   per-type is enough, per-cell not required at class 2.
2. Current-based exponential synapses (amplitude × decay τ ≈ 5 ms), weight =
   connectome synapse count × one global scalar per sign class.
3. Sign map with **receptor-level overrides**: glutamate→inhibitory via GluCl
   for Δ7→E-PG (B18); GABA(RDL)→fast inhibitory for APL→KC. A
   transmitter-only heuristic will get Δ7 wrong if it maps glutamate
   excitatory.
4. **APL as a graded non-spiking unit**: leaky integrator, no threshold, no
   spikes, reads connectome-weighted KC drive, returns subtractive or divisive
   inhibition (declare which; A12).
5. Threshold-calibration loop: set KC θ (global or per-cell) to hit coding
   level 5–10% on the engine's real input distribution (A8/A14).
6. Poisson background input and per-step Gaussian noise.
7. dt = 0.1 ms simulation core; runs up to 30 s (3×10⁵ steps on ~10³ neurons
   for CX; MB KC population ~2×10³ — cost is modest).

## Sources

- Kakaria KS, de Bivort BL (2017) Front Behav Neurosci 11:8. doi:10.3389/fnbeh.2017.00008 (params verified from article text)
- Kim SS, Rouault H, Druckmann S, Jayaraman V (2017) Science 356:849–853. doi:10.1126/science.aal4835 (verified from open PDF)
- Turner-Evans D et al. (2017) eLife 6:e23496 (verified via PMC5440168)
- Turner-Evans D et al. (2020) Neuron 108:145–163 (Δ7 sign; verified via PMC8356802 search result)
- Turner GC, Bazhenov M, Laurent G (2008) J Neurophysiol 99:734–746 (6±5% verified; membrane numbers only via citing text — Ahmed et al. 2023 Curr Biol)
- Honegger KS, Campbell RAA, Turner GC (2011) J Neurosci 31:11772–11785 (~5% of ~2500 KCs; ≥half-trials criterion)
- Gruntman E, Turner GC (2013) Nat Neurosci 16:1821–1829 (claw coincidence)
- Lin AC, Bygrave AM, de Calignon A, Lee T, Miesenböck G (2014) Nat Neurosci 17:559–568 (verified via PMC4000970)
- Litwin-Kumar A, Harris KD, Axel R, Sompolinsky H, Abbott LF (2017) Neuron 93:1153–1164 (verified via PMC5379477)
- Amin H et al. (2020) eLife 9:e56954 (APL non-spiking, λ≈50 µm; verified via PMC7541083)
- Prisco L et al. (2021) eLife 10:e74172 (APL divisive normalization, calyx)
- Papadopoulou M et al. (2011) Science 332:721–725 (GGN non-spiking; cited through Amin 2020)
