# Fidelity class 2, domain 1: the canonical whole-brain LIF baseline (Shiu et al. 2024)

Research pass, 2026-09-29. Anchor: Shiu, Sterne, Spiller et al., "A Drosophila
computational brain model reveals sensorimotor processing", **Nature 634,
210-219 (2024)** (preprint: bioRxiv 2023.05.02.539144, "A leaky
integrate-and-fire computational model based on the connectome of the entire
adult Drosophila brain..."). Verified against three primary sources this pass:

- the Nature version-of-record PDF (CC-BY copy, Oxford Research Archive,
  `ora.ox.ac.uk/objects/uuid:9422e222-dc23-4182-b183-19b92505a7db`), Methods
  read in full;
- the preprint full text (PMC10187186), Methods read in full;
- the authors' released code, `github.com/philshiu/Drosophila_brain_model`
  `model.py` (`default_params` dict read verbatim).

Paper text and code agree on every number below. Labels: **ESTABLISHED** =
verified in paper and/or code this pass; **ASSUMED** = not stated in any
verified source, our reading; **DERIVED** = computed here from ESTABLISHED
values (the computation is shown).

## 1. Canonical parameter table

| Parameter | Value | Units | Source (where) | Label |
|---|---|---|---|---|
| Resting potential `v_0` | -52 | mV | Nature Methods "Computational model"; `model.py` `default_params`; provenance Kakaria & de Bivort 2017 (their ref. 18) | ESTABLISHED |
| Reset potential `v_rst` | -52 (= rest) | mV | same block | ESTABLISHED |
| Spike threshold `v_th` | -45 | mV | same block | ESTABLISHED |
| Membrane resistance | 10 kOhm cm^2 (code comment: 10 MOhm) | — | Nature Methods (specific units); `model.py` comment (absolute) | ESTABLISHED |
| Membrane capacitance | 2 uF cm^-2 (code comment: 0.002 uF) | — | same | ESTABLISHED |
| Membrane time constant `t_mbr` | 20 (= R x C) | ms | Nature Methods defines T_mbr = C x R; `model.py` `t_mbr = 20*ms` | ESTABLISHED |
| Synaptic decay `tau` | 5 | ms | Nature Methods (their ref. 61 = Juergensen et al. 2021); `model.py` | ESTABLISHED |
| Synaptic delay `t_dly` (spike -> PSP onset) | 1.8 | ms | Nature Methods (their ref. 62 = Paul et al. 2015, NMJ electrophysiology); `model.py` | ESTABLISHED |
| Refractory period `t_rfc` | 2.2 | ms | Nature Methods (refs 18, 59 = Kakaria & de Bivort; Lazar et al. 2021); `model.py` | ESTABLISHED |
| Weight per synapse `w_syn` | 0.275 | mV | Nature Methods: "free parameter", the model's **only** one | ESTABLISHED |
| `w_syn` calibration criterion | sugar GRNs at 100 Hz -> ~80% of maximal MN9 rate | — | Nature Methods, stated with refs 64-65 | ESTABLISHED |
| Connection weight `w(j,i)` | (synapse count j->i) x (+1 excitatory / -1 inhibitory) x `w_syn` | mV | Nature Methods; code: `syn.w = df_con['Excitatory x Connectivity'] * w_syn` | ESTABLISHED |
| Weight cap / saturation | none | — | no cap appears in Methods or `model.py` | ESTABLISHED (absence) |
| Integration timestep | 0.1 | ms | not stated in paper; `model.py` never sets `defaultclock`, so Brian2's documented default 0.1 ms applies, with `method='linear'` (exact update of the linear ODEs per step; dt only quantizes threshold checks, spikes, delays) | ESTABLISHED (code + Brian2 docs) |
| Trial protocol | 30 trials x 1000 ms | — | Nature Methods; `t_run`, `n_run` in code | ESTABLISHED |
| Neuron count / connectome | all 127,400 proofread neurons, FlyWire materialization **v630** (female brain) | — | Nature Methods verbatim; repo README (v783 optional, not used in paper) | ESTABLISHED |
| Initial conditions | v = v_0, g = 0 | — | `model.py` `create_model` | ESTABLISHED |
| Per-type deviations | **none — every neuron identical** | — | Nature Discussion: "we treat each neuron identically" | ESTABLISHED |
| Compute cost | ~5 min per 1,000 ms trial per CPU thread (sugar activation) | — | Nature Methods verbatim | ESTABLISHED |

### Model equations (Nature Methods; identical in code)

```
dv/dt = (v_0 - v + g) / t_mbr      : volt  (unless refractory)
dg/dt = -g / tau                   : volt  (unless refractory)
on presynaptic spike (after t_dly):  g += w(j,i)
spike when v > v_th; reset: v = v_rst, g = 0; frozen for t_rfc
```

Three code-level mechanics worth reproducing exactly (all ESTABLISHED from
`model.py`, first two also in Methods prose):

1. **g is zeroed at spike** ("g ... after firing of the neuron, starts at
   0 mV"): a spiking neuron discards all accumulated synaptic drive.
2. **Both v and g are frozen during the refractory period** (the
   `(unless refractory)` flag is on *both* equations): input arriving in the
   2.2 ms after a spike is lost, not integrated.
3. The reset string also contains `w = 0`, which references no neuron
   variable; treat as vestigial. Do not port it.

Despite the paper's "alpha-synapse" label, the equations are a
single-exponential (instantaneous-jump, tau-decay) drive in voltage units —
there is no conductance reversal potential, so inhibition can hyperpolarize
without bound. Label the "alpha" wording, not the equations.

## 2. Neurotransmitter -> sign mapping (ESTABLISHED, Nature Methods)

| Item | Rule |
|---|---|
| Predictions | per-synapse NT predictions from Eckstein et al. (their ref. 3), synapse cleft-score cutoff **>= 50** (as in their ref. 67), highest-probability NT per presynaptic site |
| Neuron-level sign | **majority vote across all of the neuron's presynaptic sites**; each neuron is exclusively E or I |
| Inhibitory | GABA, glutamate (glutamate inhibitory per Liu & Wilson 2013, GluCl) |
| Excitatory | acetylcholine **and dopamine, octopamine, serotonin** ("assigned to the excitatory category" — verbatim) |
| Population fractions (whole FlyWire volume) | ~55% cholinergic, 24% glutamatergic, 14% GABAergic, ~7% monoaminergic |
| E vs I magnitude | identical (`|w_syn|` same for E and I) |
| Min synapse count per connection | none stated in Methods or code; the parquet appears unthresholded beyond the cleft-score filter | ASSUMED (absence not explicitly stated) |

## 3. Stimulation, silencing, spontaneous activity (ESTABLISHED)

- **Spontaneous activity: none.** Baseline firing of every neuron is 0 Hz;
  activity exists only downstream of externally driven neurons. Stated
  consequence (verbatim in both versions): "inhibitory connections to an
  inactive neuron have no effect", and "absolute firing rates of the model
  are unlikely to be accurate" — the authors interpret only *changes*.
- **Activation** = Brian2 `PoissonInput` per driven neuron: rate 10-200 Hz
  (sugar GRNs; 20-260 Hz water), event weight `w_syn * f_poi` with
  `f_poi = 250` (= 68.75 mV per event, deliberately supra-threshold so the
  driven neuron fires ~1:1 with the Poisson train), and the driven neuron's
  refractory set to 0 ms (code).
- **Silencing** = zeroing all *output* weights of the silenced neuron (code:
  `syn.w[...] = 0`); the neuron still integrates input.
- Readout = trial-averaged firing rate over 30 x 1000 ms; "activated" means
  rate > 0 Hz in any trial's union (45 neurons respond at 10 Hz sugar drive,
  455 at 200 Hz — out of 127,400).

## 4. Derived activation-threshold numbers (DERIVED here, from the table above)

Threshold gap = 7 mV; unitary event = 0.275 mV jump in g. Numerically
integrating the model ODEs (tau_m 20 ms, tau_s 5 ms): a g-jump reaches a peak
depolarization of **0.1575 x** the jump, 9.2 ms later. Hence:

- peak unitary "EPSP" ~ **0.043 mV**;
- one presynaptic spike fires a resting neuron only through a connection of
  **>= 162 synapses** (7 / (0.275 x 0.1575));
- sustained presynaptic drive at rate r through N synapses gives steady-state
  g ~ N x 0.275 mV x r x 5 ms, so firing a resting neuron needs
  N x r >= ~5,100 syn x Hz (e.g. ~51 synapses at 100 Hz).

These are the numbers to sanity-check any reimplementation against before
trusting benchmark results (a unit test: one 162-synapse connection fires the
target once; a 161-synapse one does not).

## 5. What the canonical model CAN and CANNOT reproduce (ESTABLISHED, from the paper)

**Can (validated):** 91% of 164 empirically tested predictions consistent
(84% excluding the split-GAL4 optogenetic screen); all 10 known
sugar-responsive cell types predicted to respond, 8/10 predicted sufficient
for MN9; dose-dependent MN9 firing with sugar/water GRN rate; bitter and
Ir94e ("low salt") suppression of MN9 including the novel, then-verified
prediction that Ir94e is aversive but cannot suppress extension to 1 M
sucrose; antennal grooming: JO-CE robustly drives aBN1 while JO-F does not
(verified by calcium imaging); connectivity is load-bearing — with
distribution-preserving shuffled weights, sugar drive activates MN9 in
**1/100** simulations vs 100% with the real connectome. Follow-on use: Sapkal
et al. (Nature 2024, their ref. 49) used the model to identify
halting/foraging neurons.

**Cannot (authors' own list):** no spontaneous/basal activity, so circuits
with standing inhibition are "poorly simulated" (their words — their own
failure cases Tentacular, Phantom, Usnea are inhibitory/neuromodulatory); no
gap junctions, no neuropeptides/neuromodulation, no internal state, no
non-spiking/graded neurons, no morphology, no receptor dynamics, no
plasticity; absolute rates untrustworthy; monoaminergic neurons "modelled
less well" (forced excitatory).

**Never tested by the paper (open, not established either way):** vision
(T4/T5 direction selectivity), mushroom-body sparse coding, central-complex
bump dynamics — exactly FlyGI's three class-1 failure benchmarks. A 2026
preprint (arXiv 2609.01330) reports orientation maps emerging in the medulla
from a connectome-constrained spiking model of FAFB, which is precedent that
visual structure can emerge at this fidelity, but its parameters were not
verifiable this pass — treat as secondary.

## 6. Follow-on literature: corrections and portability

- **No verified follow-on paper replaces the canonical parameter set.** The
  robustness analysis is the paper's own: w_syn +/- 30% changes prediction
  agreement to 90-95% of default (accuracy 85-88% vs 91%); I:E weight ratio
  +/- 50% keeps 95-96% agreement; flipping glutamate to excitatory breaks the
  bitter/Ir94e inhibition result and raises the activation screen's
  false-positive rate from 1% to 16% (ESTABLISHED, Nature Methods). So: keep
  glutamate inhibitory; expect parameter slop of tens of percent to be
  survivable; expect the E/I sign map to be the fragile part.
- **Portability to male connectomes is precedented:** Cheong et al. 2024
  (eLife, MANC premotor paper) ran Shiu-style LIF units on the male adult
  nerve cord (ESTABLISHED existence; parameter deltas not verified this
  pass). A neuromorphic port to Loihi 2 exists (2025, secondary).
- **Recalibration on a different connectome is expected to move w_syn.**
  `w_syn = 0.275 mV` was fitted on FlyWire v630 *female* synapse counts via
  the MN9 criterion; a secondary source this pass reports that on another
  connectome 0.275 gives only ~68% of maximal MN9 and 0.30-0.32 restores the
  80% criterion. ASSUMED (blog-tier, unverified) — but the *procedure* is
  ESTABLISHED: refit w_syn on MaleCNS by the published criterion (sugar GRN
  100 Hz -> ~80% max MN9) rather than copying 0.275, and record the refit as
  a measured FlyGI number.

## 7. Implementation guidance (what the class-2 engine must support)

1. Per-neuron state (v, g) with the exact update above; either `dt = 0.1 ms`
   with exact (linear) per-step updates, or an event-driven equivalent.
   Uniform synaptic delay 1.8 ms (quantized to dt).
2. Signed integer-synapse weights: `w = +/- N_syn * w_syn`, neuron-level sign
   from the NT majority rule, glutamate inhibitory, monoamines excitatory
   **as the labelled default with a per-neuron override hook** (the sign map
   is the fragile assumption; make it a config, not a constant).
3. The two Shiu quirks as explicit, toggleable flags: g zeroed at spike;
   v *and* g frozen during refractory. Class-2 experiments will want them
   off; reproducing Shiu wants them on. An unlabelled divergence here is
   invisible and changes high-rate behaviour.
4. Poisson drive attachment per neuron (rate, weight multiplier `f_poi`,
   refractory override) and silencing as output-weight zeroing — these are
   the published perturbation API and the benchmarks should speak it.
5. Trial machinery: n independent stochastic trials, union/mean rate
   readouts, and the shuffled-weight null as a built-in control.
6. Hooks for per-type overrides of `t_mbr`, `tau`, threshold and a graded
   (non-spiking) unit type. The canonical model has none of these — that
   uniformity is what class 1 already showed to fail the physiology — so
   class 2's *deltas from Shiu* (per-type tau, APL as graded unit, tonic
   drive) must each be a labelled config change from this verified baseline,
   not a fork.
7. Unit tests pinned to Section 4's derived numbers, plus one integration
   test pinned to a published behaviour (e.g. shuffled weights kill
   propagation) before any benchmark is scored.

## 8. Risks for the class-2 benchmarks (this domain's view)

- **Zero-baseline silence is the structural risk.** With no spontaneous
  activity, inhibition onto silent neurons does nothing (authors' own
  statement) — an EB bump cannot persist and KC sparsening-by-APL cannot
  operate at rest. Canonical Shiu parameters alone will likely still fail
  the CX-bump and possibly the KC-sparseness benchmarks; a tonic-drive or
  spontaneous-input extension is where those benchmarks will be won or lost,
  and it is *not* part of the canonical set (any tonic drive we add is
  ASSUMED until calibrated).
- **Uniform kinetics vs direction selectivity.** One global 1.8 ms delay and
  one 5 ms synaptic tau supply no per-pathway temporal asymmetry; T4/T5 DS
  in the fly rests on tens-of-ms lag differences between input arms. DS may
  emerge weakly from synapse-count asymmetries or not at all — the paper
  never tested vision, so class 2 has no established precedent to lean on
  (the 2026 orientation-map preprint is encouraging but secondary).
- **Absolute rates are explicitly untrustworthy** — benchmarks must be
  ordinal/relative (as Shiu's own were), or they test the calibration, not
  the fly.
- **w_syn does not transfer across connectomes** (synapse-detection and
  proofreading differences shift counts); an unrefit 0.275 on MaleCNS is an
  unlabelled assumption sitting under every downstream number.
- **Compute:** ~5 CPU-minutes per simulated second for the whole brain in
  Brian2; 30-trial protocols on subcircuits are fine, whole-brain sweeps are
  not free — measure before launching (see resource-check memory rule).
