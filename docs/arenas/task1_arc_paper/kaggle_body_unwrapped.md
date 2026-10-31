**One measured pair carries the paper.** Our local ARC-AGI-3 gateway ladder climbed from 0.551859 (an engineering baseline) through 3.044167 (two game-specific action grammars) to 28.742260 (thirteen grammars; 73 levels and four full game wins in a matched 35-minute competition-mode window)—and the three Kaggle submissions (56620463, 56650224, 56683298) scored 0.15, 0.15, 0.15: the abstention floor. Game-specific grammar transfer to the hidden set measured zero, three times. Meanwhile the one fly component those agents deployed—a static retinotopic eye map compiled from the MaleCNS *Drosophila* connectome—completed level-1 tasks at 2.59x the human action baseline vs 11.59x for its scrambled-map twin—a measured 4.5x efficiency separation attributable to retinotopy. The scaffold scored locally and carried nothing across; the anatomy carried little score but is the only deployed component that survived its own control.

Our leaderboard accuracy is 0.15, near the floor; we own it. The contribution is a submission-verified public measurement of zero grammar transfer at this scaffold scale, plus the attribution instrument separating what the engineering did from what the fly's anatomy did.

## Prior work

A September-2026 survey of 50+ public connectome game demos finds one dominant shape—frozen graph, hand-written readout; none ran validation, input gates and controls together, none had entered any ARC version. Published lines cut against innate-wiring usefulness: a worm connectome plus trained mapping walks a fly body realistically; fly-hero's trained readout hits 100% on a random network; connectome-reservoir benchmarks report randomized nulls often matching or beating real wiring. Our rewired-null discipline answers exactly these. Among ARC methods, CompressARC placed third in 2025 (~20%, ARC-AGI-1); biologically-flavored entries (ARC-NCA, vector-symbolic) have placed; no pure negative-results paper has (2024–2025 winner lists).

## The system and the instrument

FlyGI asks what a fly's innate wiring computes for free on ARC-AGI-3. Substrate: MaleCNS v1.0, 166,700 retained neurons; the deployed graph is the 24,994,595-edge modulator-preserving runtime. Circuits run on a fidelity ladder—class 1: full-graph float32 leaky-tanh rate dynamics; class 2: per-type LIF/graded dynamics on extracted subcircuits; class 2.5: provenance-verified flyvis ensemble parameters for T4/T5; class 3: literature-pinned spiking physiology (CX; T4/T5 attempt blocked).

Every module faces the same three stages, preregistered with bands and kill rules (EXPERIMENTS.yaml):

1. **Validate**—reproduce the circuit's known biology at a declared fidelity class.
2. **Gate the input**—prove the circuit receives usable drive. This rule was paid for: the mushroom body had been "taught" at 0.00% driven sensory input, the motion detectors evaluated on spatially scrambled input; both nulls were about our plumbing, not the fly.
3. **Test against controls**—exact degree-preserving rewires, scrambled-encoder twins, interface-matched bypasses, shuffled credit and time, and a matched engineered equivalent.

Any claim of the form "connectome X does Y" can be run through this instrument unchanged; the instrument is what transfers.

## Result 1 (measured): local ladder up, hidden set flat

Each rung shipped and scored 0.15—the pure-abstention floor—while the local score grew ~52-fold. The ladder ended honestly: an online-search layer failed its preregistered gate (28.459550 vs 28.742260) and did not ship. Before these three: six 0.00s from a construction crash, diagnosed from the empty scorecard, not exit codes.

## Result 2 (measured): the fly component is small, real, and bounded

**The fly content of all three scored submissions is the compiled anatomical eye map only, deployed as static retinotopy metadata; neuronal dynamics were OFF (`neuronal_dynamics_active=false` in the preflight) in every scored run.**

Locally, against its scrambled-map twin, real retinotopy won where the offline premise predicted: r11l completions ran 0.27–0.68x human baseline (league 0.3064, replicated 0.3058, vs 0.1875 permuted). The boundary travels with the win: the same ladder failed its breadth bar, 17 levels vs the champion's 21. The eye map's hidden-set contribution was never isolated—no scrambled-map control ever ran on Kaggle.

## The verdict matrix: controls firing both ways

**Against the fly.** With input gates passed (PN share of KC drive 62–87% vs a 5% bar), the class-2 mushroom body scored 0.600 on one-shot held-out visual association—while its exact rewire scored 0.800 (sign test p=0.996); shuffled-credit 0.400 (real beats it, p=0.019—the depression mechanism carries credit); a matched perceptron 0.917. T4/T5 motion decoding at validated class-2.5 fidelity (pooled median DSI 0.3216, band >=0.30) scored 0.3875 on the held-out test (660 verified events; 4 held-out games x 3 seeds)—above chance on every seed, while the rewire reached 0.4306 (p=0.97) and an engineered shift-matcher 1.0000. These circuits' specializations are real, and on these ARC tasks, at these fidelities, they point the wrong way. Two more circuits died earlier: the ellipsoid-body ring holds activity, not position, at every unfitted fidelity through class-3 spiking (155/155 class-2 configs delocalized; the validated class-3 bump persists but slides to one region from every heading), and the LC object-position code was sign-inverted at all 21 class-1 grid points (best Spearman -0.203 vs a +0.50 band).

**For the fly, off-score.** Given fitted per-type physiology, Biswas et al.'s published derivation recipe applied once to our counts, the fitted EPG-Delta7 realization holds a heading bump dead on target: 8 of 8 angles, 0.0° error, both valid configurations. All three degree-preserving rewires fail outright; their attractor conditions have no solution on shuffled counts. The first verdict in our record where the fly's wiring, given fitted per-type physiology, beat its own shuffle (one earlier FlyBench bar beat the same null inside a mechanism test). Not a reproduction of their parameters; our r_a differs, flagged.

**Against ourselves.** A coordinate head shipped in two early submissions with six passing tests explored 3.29x less than clicking at random (72 vs 236 unique observations, six click-only games). A 520-parameter trained head was genuinely connectome-dependent (trace ablation 0.2835 -> exactly 0.0000) yet generalized zero: 0.0000 on all 17 held-out games against 0.8858 on its own training games. Connectome-dependent and useless are compatible; so are well-tested and worse than random.

**What survives, and what bounds it.** The deployed graph is measurably non-random—spectral radius 0.8289 vs 0.2219–0.2360 across three exact rewires (3.59x)—and still carried no ARC outcome advantage. The registered harness-sensitivity control (run before release) bounds that reading: a reservoir validated into the long-memory regime (rho 0.9924) also moved no score, both decision CIs spanning zero at a ~+0.1 detection floor. The class-1 zeros bound this interface's tested graphs, not the fly; the arena rewires each carried their own positive control.

## Theory: why it fails where it fails

**(1) A fidelity wall, located exactly:** at class 1, no delay lines, no sparse-coding regime, and no movable bump exist anywhere in the swept gain x leak space—0/21 pass maps across four circuit capabilities. That wall is a statement about the model class as swept, not about the fly. **(2) A statistics mismatch, isolated by the rewire:** at class 2/2.5 the circuits do work as circuits (held-out KC active fraction 0.0741 inside the [0.03, 0.15] band; both trivial alternatives saturate at 1.0000), and what then loses to the shuffle is the specific wiring. Inferred, bridge stated: assuming the rewire advantage reflects stimulus-statistics fit, the fly's wiring is tuned to fly inputs, and that tuning is anti-transfer on ARC grids. **(3) Generality predicted survival; sophistication did not.** The grammars, maximally game-specific, bought ~52x locally and zero hidden. The trained head, specific to its training games, generalized zero held-out. Retinotopy, a game-agnostic spatial prior, is the one deployed effect that survived its control and replicated, locally. Inferred, bridge stated: three abstention-floor scores imply no archetype latched onto a hidden game, assuming structurally similar hidden games would have triggered at least one.

## Claim boundaries

- Deployed fly content = the static compiled eye map; dynamics OFF in all three 0.15 submissions.
- A leaderboard score establishes engineering, not fly computation.
- The connectome is anatomy, not a brain emulation. Nulls indict the model class at its fidelity, not the living fly—except the two earned NOT-USEFUL verdicts, both behind passed input gates, scoped: the MB for one-shot visual association on ARC at class-2 fidelity; T4/T5 for ARC motion decoding at validated class-2.5 fidelity. At class 1 the standing verdict is NOT USEFUL: NONE—no prior null may be stated as a fact about the fly.

## What this buys anyone chasing 85%

1. **Measure transfer, not local score.** A ~52-fold local gain can be worth exactly zero. Matched-window gateways plus the abstention floor make transfer-zero a measurable, publishable outcome for any scaffold.
2. **Public-set grammar libraries are worth the abstention floor.** Key scaffolds to structure, not game identity.
3. **Run the trivial alternative first.** Degree-preserving rewires beat the real wiring twice here; random clicking beat our tested coordinate head. The control belongs in the same commit as the component.
4. **The attribution stack is substrate-agnostic:** fidelity ladder, input gates, rewired nulls, scrambled twins, preregistered kill rules—portable to any structured prior.

Expected—carried with our 0-for-16 base rate on score-adjacent predictions (the measurements held): a scaffold triggered by structure rather than game identity moves off the abstention floor. Everything needed to test it—worklog, preregistrations, league harness, submission 56683298—is in the open repository, where the deployed graph self-reports machine-readably: 166,700 nodes, 24,994,595 edges, neuronal_dynamics_active=false.
