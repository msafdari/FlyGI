# Task 10 — the exhaustion audit and the science menu

Provenance: a 9-agent audit (five map lenses: tested record, code
inventory, data ceiling, fly-capability literature, ARC-AGI-3 demand
profile; four adversarial gap lenses: fidelity, circuits,
interfaces/learning/tasks, hostile completeness critic) run 2026-10-15
against the repository record at commit c1505c0, answering the user's
question "are we absolutely sure we're using everything possible from
the fly?". User go on the full menu: 2026-10-23 ("Go for all items on
science menu"). This document is the condensed, tiered record of the
audit; the registrations it licenses live in killtest_design.md beside
it and in EXPERIMENTS.yaml.

## The three-part answer

1. **The named candidates are measured-closed.** "Latent world models":
   H-JEPA-SPONTANEOUS (null; the shuffled-time control scored the real
   arm's own number) and the whole of Task 9 (structure PASS p 0.005;
   computation KILL at classes 1 and 3). "ODEs": the fidelity ladder
   reached class 3 (Kakaria/Pisokas spiking, dt 1e-4 s) on the CX, with
   the engine reproducing the PUBLISHED idealized fly compass and the
   real counts still failing (H-CX-CLASS3-COMPASS).

2. **What was exhausted is not "the fly".** It is one male's
   chemical-synapse counts plus heuristic transmitter signs, at
   declared unfitted mappings, read out through rates and linear
   probes, against one null family. The data categorically lacks —
   and every published connectome lacks — gap junctions, neuromodulator
   receptors, neuropeptides, glia, per-neuron biophysics, and the
   animal's learned synaptic state (docs/modeling_assumptions.md
   states this ceiling as the first modeling sentence).

3. **The ARC mismatch is measured, not asserted.** Crossing
   ARC-AGI-3's demand profile (symbolic goal reading, discrete rule
   induction, 3-15-deep planning, 31:1 punishment-dominated signal,
   zero cross-game transfer measured three times) against the fly's
   published computational repertoire (continuous egocentric control)
   yields exactly ONE overlapping primitive — retinotopic spatial
   indexing — which is precisely the one fly component measured useful
   and deployed (2.59x vs 11.59x scrambled-twin click cost). INFERRED,
   bridge stated: the games pay for computations no fly circuit
   performs at any fidelity; even a perfect simulation of the animal
   carries no Expected-tier score claim (base rate 0 for 16,
   docs/arenas/SYNTHESIS.md §6).

## The menu (user go 2026-10-23, all items)

Ranked as delivered; none is score-adjacent; every Expected-tier
prior below inherits the 0-for-16 base rate.

| # | Item | Why | Status at audit |
| --- | --- | --- | --- |
| 1 | Edge-of-chaos reservoir positive control on ARC | Instrument validity: the one built control that can certify the harness detects ANY graph's advantage; built, validated (rho 0.9924), never fired | exists-untested |
| 2 | Class-3 physiology on T4/T5 | SYNTHESIS §7 item 1: the killed circuit where literature disagrees with our null; a reversal breaks §4; the CX class-3 run measured that fidelity CHANGES failure modes | never-tried |
| 3 | Fitted per-type physiology on the CX (Biswas 2024 / Duan & Fiete configuration) | The rung the class-3 registration explicitly declined; published rate-tier successes on these connectomes all fit per-type params; strongest open reversal candidate | never-tried (declined, recorded) |
| 4 | Fan-shaped-body structural probe | The literature's actual "latent world model" substrate (PFN/hDelta/FC/PFL vector system); "PFN" appears nowhere in the repo; excluded from the 148-neuron CX; functionally premise-blocked upstream, structurally testable at Stage-A cost | never-tried |
| 5 | Naturalistic-statistics task | SYNTHESIS §5 explanation 3 (task-statistics mismatch) is live with zero tests | never-tried |
| 6 | FlyBench's two measured mechanisms: terminal-aware synapse placement (core tier 0.57->0.90) and spike-frequency adaptation | No-free-parameter fidelity mechanisms our own survey flagged (next_arenas_survey_20260930.md Part B.4) and never imported; synapse positions are discarded at import (schema keeps body_pre/body_post/weight) | never-tried |
| 7 | Second null family (weight and sign shuffles) | The pre-release audit's own listed gap; decomposes WHAT the degree-preserving rewire destroys; refines (never reopens) closed verdicts | exists-untested |

## The hard ceiling (not a to-do list)

Unreachable from MaleCNS or any current connectome, recorded so the
menu is never confused with it: gap junctions / electrical synapses;
receptor-level neuromodulation (volume transmission, the fly's own
regime controller — ironic, as the record's central dynamical lesson
is that regime decides whether a circuit computes); neuropeptides;
glia; channel composition and compartmental biophysics beyond
type-level imports; the learned synaptic-weight state of a behaving
animal; the body and sensory periphery.

## The critic's three strongest standing criticisms (kept verbatim in spirit)

1. The seven rewire-parity instances rest on a harness never shown
   able to detect a positive — the tuned reservoir control never ran
   (menu item 1 discharges this).
2. The fidelity ladder stopped one rung below where the field says
   computation appears (fitted per-type parameters), on the wrong
   circuit for the literature disagreement (T4/T5), blind to two
   externally measured mechanisms (items 2, 3, 6 discharge this).
3. "Exhaustive" is itself an Inferred-tier bridge of exactly the class
   this repository measures at zero — asserted over a dataset it left
   substantially unread (birthtime/hemilineage/serialMotif/receptorType
   columns ingested and never queried). This document is the standing
   correction: the claim the record supports is "every registered
   bridge tested so far has failed", never "nothing remains".
