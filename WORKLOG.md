# FlyGI durable worklog

This is the compact operational record for FlyGI. The detailed chronological
diary from repository creation through the second Kaggle submission remains
recoverable from Git history at commit `c3774e2`; it was deliberately pruned on
2026-09-22 so future sessions can recover the actual project state quickly.

Read this file before planning or editing. Reconcile it with `git status`, the
latest commits, active processes, and immutable result artifacts after every
handoff or context reset. Update it after each meaningful result, decision,
blocker, submission, or change in ordered next work. Never record secrets.

## Why FlyGI exists

FlyGI puts the complete MaleCNS v1.0 fruit-fly central-nervous-system graph into
the decision loop of ARC-AGI-3:

```text
ARC frame + action history
        -> sensory interface
        -> 166,700-neuron MaleCNS graph
        -> persistent dynamics / local learning
        -> neural-population readout
        -> legal ARC action
```

The engineering goal is a valid, reproducible leaderboard agent that genuinely
executes the full connectome on every decision. The scientific question is
narrower and more demanding:

> With the interface, dynamics, training budget, parameter count, action budget,
> and seeds held fixed, does evolved MaleCNS wiring make any ARC-relevant
> computation more accessible than a degree-matched rewire, matched artificial
> reservoir, or no-recurrent-graph bypass?

The tracks remain distinct:

- **Track A — Literal Fly:** fixed interface, zero ARC-trained parameters.
- **Track B — Frozen Fly:** frozen graph plus a small trained interface/readout.
- **Track C — Plastic Fly:** constrained local plasticity at a declared
  biological site.

A high score proves only that the whole engineered agent performs well. Credit
goes to the fly only when the real graph beats controller-only, bypass, and
matched graph controls. A zero score does not show that a biological fly lacks
intelligence: a connectome is anatomy, not a complete brain emulation.

## Current snapshot — 2026-09-22

- Private repository: <https://github.com/msafdari/FlyGI>.
- Branch: `main`, tracking `origin/main`.
- Current source checkpoint at the last recovery audit: `505a9eb`.
- Fast verification before that checkpoint: 284 tests passed and Ruff passed.
- No raw connectome, compiled arrays, ARC game packages, result traces, model
  checkpoints, credentials, virtual environments, or generated notebooks belong
  in normal Git history.
- Submission `56459984` completed with public score **0.00**. A read-only Kaggle
  CLI poll confirmed the result at `2026-09-22T09:46:10Z`.
- A Track B CEM job is active; do not launch another memory-bandwidth-heavy run
  until it ends or is deliberately stopped.

### Active Track B training

The current process trains the 520-parameter action head on eight public games:

```bash
caffeinate -ims uv run python scripts/train_head.py \
  --config configs/literal_rate_signed_loop_escape.yaml \
  --games ar25 bp35 cd82 cn04 lf52 ls20 r11l sp80 \
  --action-budget 150 --population 16 --elites 4 \
  --generations 60 --workers 4 --sigma 0.5 --sigma-floor 0.15 \
  --level-bonus 500
```

Checkpoint path: `results/head_training/head_training_checkpoint.json`.
Final reviewed parameters, if the run succeeds, belong in
`results/manifests/trained_head_parameters.json`.

Two smoke-discovered defects were fixed in `505a9eb` before launch:

1. trace ablation now evaluates inside a worker with initialized graph/game
   globals instead of silently returning negative infinity in the parent;
2. CEM sigma has a declared floor at 15% of its initial value instead of
   collapsing to a point after one generation.

The smoke winner scored objective 271 versus 21 with its descending trace
ablated. That is evidence the head can use graph output in the smoke protocol,
not an ARC score and not evidence that real topology beats controls.

Generation 0 completed at `2026-09-22T09:48Z`. Its best candidate had training
objective 185.625, one level completion, and 123.125 mean unique observations;
the population mean was 136.59375, the elite mean was 181.59375, and no
candidates failed. These are eight-game training-objective values, not held-out
ARC scores. The checkpoint's `next_generation` is 1 of 60.

## Immutable data and runtime identity

MaleCNS source release: `male-cns:v1.0`.

| Runtime property | Signed deployed graph |
| --- | ---: |
| Retained neurons | 166,700 |
| Directed nonzero edges | 24,559,055 |
| Descending-neuron readout population | 1,314 |
| Graph SHA-256 | `45e332d90ea4e881ece5d4d72216955bd53eec922aa60955a69db510272eff61` |
| Node metadata SHA-256 | `2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c` |
| Groups SHA-256 | `09736379ce989268080f57b64f357e800cf446972007c1af2287a86b9985a89d` |

The unsigned graph contains 25,582,837 edges. The heuristic-signed build zeros
1,023,782 outgoing edges from modulatory or unknown-transmitter neurons. A
separate modulator-preserving runtime contains 24,994,595 edges for the Track C
learning experiment.

Detailed source hashes, acquisition provenance, preprocessing choices, and
runtime records live in `data/manifests/` and the tracked result manifests.

## What is implemented

### Core and deployment

- Strict Python 3.12 config, provenance, graph-build, validation, and CLI paths.
- Full sparse MaleCNS compilation without a dense adjacency matrix.
- Persistent float32 leaky-tanh dynamics on CPU/SciPy CSR.
- Fixed sparse frame encoder, adaptive DN standardizer, legal-action sampler,
  coordinate head, per-environment state, and loop-escape memory.
- Strict-offline public-game evaluator with immutable traces, deterministic
  replay, action/coordinate validation, timing, hashes, and resumable rows.
- Offline Kaggle Dataset/notebook packaging, graph preflight, fail-closed
  competition behavior, 600-action deployment ceiling, and seven-hour guard.

### Controls and analysis

- Three exact directed degree-preserving rewires.
- Interface-matched no-recurrent-graph bypass.
- Matched random reservoir and an edge-of-chaos positive control.
- Paired analysis clustered on games, trace-diversity audit, game-clustered
  bootstrap, within-pair permutation, and correct right-censoring.
- Retrospective recovery of the actual action index of every level completion.

### Learning experiments

- Track B: a fixed 48-dimensional compression plus an eight-action linear head,
  520 trainable parameters total, integrated before legal masking and sampling.
- Resumable CEM trainer with dense exploration objective, sparse level bonus,
  worker-local graph reuse, and mandatory descending-trace ablation.
- Track C: local dopamine-gated KC->MBON depression with bounded normalized
  updates, writable weights but immutable topology, a modulator-preserving
  runtime, and a degree-preserving mushroom-body partner rewire.

## Decisive results

### 1. The graph is structurally non-random

At the deployed `K=4`, `leak=0.3`, `gain=0.9` operating point:

| Measurement | Real signed graph | Three exact degree nulls |
| --- | ---: | ---: |
| Spectral radius | **0.8289** | 0.2360 / 0.2348 / 0.2219 |
| Hops for visual input to reach every DN | 3 | 2 / 2 / 2 |
| DN participation ratio | 5.39 | 18.54 / 14.33 / 16.00 |

The 3.59x spectral-radius separation survives exact in- and out-degree
preservation. This is the strongest reproducible connectome result. It has not
yet produced an ARC outcome advantage.

### 2. The literal interface is the main failure

The original encoder random-projects ARC features into 6,098 visual sensory
neurons. The decoder partitions 1,314 DNs into ARC action blocks by sorted body
ID. Those mappings preserve neither retinotopy nor motor semantics. The graph
causally changes actions, but an interface-matched bypass matched its ARC score.

Gate 2, 25 games x five seeds x 80 actions:

| Condition | Mean score | Levels | Games with a level |
| --- | ---: | ---: | --- |
| Real signed MaleCNS | 0.190476 | 5 duplicate-seed rows | `sp80` |
| No-graph bypass | 0.190476 | 5 duplicate-seed rows | `r11l` |
| Degree-preserving null | 0.000000 | 0 | none |
| Random legal | 0.050626 | 2 | `sp80` |

The graph policies were deterministic, so five identical seeds were not five
replicates. Effective n was 25 games.

### 3. Exploration, not raw entropy, was deficient

At 500 actions x 25 games x three seeds:

| Condition | Mean score | Levels | Unique observations |
| --- | ---: | ---: | ---: |
| Real signed | 0.064751 | 2 | 15,996 |
| Degree null | 0.007872 | 3 | 16,262 |
| Bypass | 0.000754 | 1 | 16,339 |
| Random legal | **0.097568** | **6** | **25,140** |

Formal paired analysis found no condition distinguishable on ARC outcome.
Recovered completion times also retracted an earlier apparent fly-efficiency
claim: completer-only means were 143 actions for the fly and 144 for random,
while random completed three times as often.

### 4. Loop escape helps, but budget alone saturates quickly

- 600 actions, seed 0, loop escape off: score 0.000000.
- 600 actions, seed 0, loop escape on: score 0.190476, `cd82` level 1.
- 500 actions x three seeds, loop escape on: mean 0.126984, two levels
  (`cd82` seed 0 and `sp80` seed 1). This beat the old real mean but failed the
  preregistered requirement of more than two levels.
- 1,600 actions, seed 0: mean **0.191289**, first levels in `cd82`, `sk48`, and
  `sp80`. The last two required 1,033 and 825 actions and contributed only
  0.009686 and 0.010641 game score. They raised the mean by just 0.000813 over
  600 actions while multiplying worst-case work by 2.67.

Thus a larger budget finds more states, but breadth-only exploration cannot
approach a score of 10 efficiently.

### 5. Plasticity changes exploration, not outcome

At 600 actions over 25 games, seed 0:

| Condition | Mean score | Levels | Mean unique observations |
| --- | ---: | ---: | ---: |
| Frozen modulator runtime | 0.001418 | 1 | 256.96 |
| Real plastic mushroom body | 0.005337 | 1 | **270.96** |
| Rewired plastic mushroom body | 0.000892 | 1 | 261.80 |

Real plastic minus frozen unique observations was +14.0 with a bootstrap
interval excluding zero. The required direct comparison, real plastic minus
rewired plastic, was +9.16 with 95% interval `[-1.24, +21.72]`, p=0.1539.
Plasticity unlocked no level. The result is interesting but inconclusive and is
not a connectome-advantage claim.

## Official submissions

| Ref | Configuration | Status | Public score |
| --- | --- | --- | ---: |
| `56444435` | signed graph, 80 actions, seeded literal policy | complete | **0.00** |
| `56459984` | signed graph, 600 actions, mild loop escape | complete | **0.00** |

The version-3 notebook preflighted the exact 166,700-node / 24,559,055-edge
runtime, `K=4`, loop escape 0.25/0.50, zero trainable parameters, and the three
expected array hashes. No fallback policy was used.

## Why a living connectome can score 0.00

This is not paradoxical. Natural selection shaped fly nervous systems over
millions of years for embodied survival, not symbolic program induction. More
importantly, FlyGI currently supplies only a wiring diagram and substitutes or
omits much of what makes that wiring compute:

1. **The retina is scrambled.** A random projection destroys eye columns,
   color channels, optic flow, and spatial neighborhood.
2. **The motor semantics are scrambled.** Body-ID DN blocks have no principled
   relationship to ARC arrows, click, interact, or undo.
3. **Physiology is flattened.** Every neuron receives the same leaky-tanh rule,
   leak, gain, and time scale. Real cell types, receptors, spikes, adaptation,
   delays, and oscillations are absent.
4. **Embodiment is missing.** The fly's loops expect proprioception, efference
   copy, self-motion, and muscles. ARC supplies none of those unless engineered.
5. **Learning was initially amputated.** The deployed signed runtime zeroed all
   modulatory output, deleting 129,132 DAN->KC and 3,195 DAN->MBON edges.
6. **The task is alien.** ARC-AGI-3 needs goal inference, compositional rule
   learning, counterfactual prediction, and planning. A fly has useful
   perception, memory, valuation, and control circuits, not a ready-made ARC
   executive.

The fair conclusion is not “166,700 neurons are useless.” It is “our current
interface and dynamics fail to express the functions that those circuits evolved
to perform.”

## Goal: a credible route to score 10.0

### What 10.0 means

The live Kaggle leaderboard read on 2026-09-22 had a leader at 18.81 and seven
teams at or above 10.0. A score of 10 is therefore a top-eight-class system, not
a parameter-tuning milestone.

Breadth alone cannot get there. In a six-level game, level 1 is capped at
`100 / (1+2+3+4+5+6) = 4.76`. Even reaching only level 1 in every such game
would average 4.76. Score 10 requires efficient multi-level depth across many
unseen games. The missing capabilities are action-effect learning, goal
inference, executable world models, planning, and cross-level transfer.

### Target architecture

```text
frame/history
   -> stable UI-masked object scene + learned visual features
   -> candidate actions / component-grounded clicks
   -> online action-effect and uncertainty model
   -> state-transition graph + executable rule hypotheses
   -> information-gain probe OR shortest verified plan
   -> legal action

parallel FlyGI branch
   -> retinotopic optic-lobe drive
   -> motion / salience / CX context / MB novelty / DN prior
   -> guarded residual features and tie-breaks inside the controller
```

The outer controller supplies functions the connectome does not automatically
provide: object tracking, controllability, goal hypotheses, search, and plan
verification. The fly supplies structured perception, memory, novelty/value,
and action priors. Hard legality, death bans, and verified replay paths remain
controller-owned.

### Phase 0 — finish the current head experiment

**Build:** allow the active 60-generation CEM run to finish; validate its
artifact, deterministic loading, trace ablation, and held-out-game result.

**Promotion gate:** the trained head must beat the frozen loop-escape policy on
held-out games, retain a material objective gap when compared with trace
ablation, and pass a parameter-matched bypass run. Otherwise keep it as a named
negative result and do not spend a submission.

**Purpose:** close the experiment already consuming compute. This head alone is
not expected to reach 10.

### Phase 1 — competent generic exploration kernel

Implement or adapt a permissively licensed state-graph controller with:

- frozen HUD/UI masking and stable state hashes;
- 4-connected component click candidates on actual foreground pixels;
- action/click effect statistics and calibrated novelty;
- hard bans for known terminal/dead actions;
- BFS return to the nearest reachable frontier;
- exact replay paths and cross-level retention of mechanics.

Start with controller-only. Then let graph logits break equal controller
priorities and rank valid component clicks; never let the graph resurrect an
illegal, failed, or fatal action.

**Gate:** 25 public games x three diverse seeds x 500 actions; zero protocol
violations; progress in at least three distinct games; controller-only must beat
the 0.097568 random benchmark. The hybrid must retain at least 95% of controller
score. A fly claim additionally requires hybrid > controller-only and bypass.

**Expected effort:** 3-5 focused engineering days. **Score target, not forecast:**
0.3-1.0 hidden.

### Phase 2 — replay-pretrained affordance and value model

Acquire the official 342 human replays for all 25 public games and combine them
with counterexamples generated by our local random/graph runs. Split by whole
game, never by transition, so validation measures cross-game transfer.

Train one small offline model with four heads:

1. probability each legal action or component click changes the state;
2. object-level next-state delta and avatar displacement;
3. click-affordance heatmap;
4. novelty/progress value used to rank frontiers.

Use augmentation that preserves mechanics: translation, palette permutation,
component permutation, UI-strip perturbation, and trajectory truncation. Do not
feed game IDs or source code. Initialize online learning from this prior, then
update from each new environment's actual transitions.

**Gate:** leave-five-games-out cross-validation; effect calibration and
next-object-delta accuracy must beat frequency/identity baselines; the complete
controller must improve score and level depth on every held-out fold, not only
memorized training games.

**Expected effort:** 1-2 weeks. **Score target:** 1-3.

### Phase 3 — online executable world model and planning

Represent frames as tracked objects and learn a small library of composable
transition primitives: translate, rotate, recolor, toggle, select, carry,
collide, spawn/delete, counter/cycle, and conditional interaction. Maintain
multiple rule hypotheses rather than committing after one example.

At each frontier:

- choose the cheapest action that maximally separates competing hypotheses;
- verify every predicted transition against reality;
- turn mismatches into counterexamples immediately;
- plan with BFS/A*/beam search only through transitions whose predictions are
  calibrated; stop a plan at the first mismatch and repair the model.

When a level completes, back-label its shortest successful path, train the value
head, infer which object relation constituted progress, and transfer both the
mechanics and goal schema to later levels.

**Gate:** on held-out games, at least 65% exact prediction for never-taken legal
actions on visited states; probes below 20% of executed actions; multi-level
progress in at least five distinct public games; every planned action carries a
prediction that is checked afterward.

**Expected effort:** 2-4 weeks. **Score target:** 3-6.

### Phase 4 — depth, skill transfer, and compute allocation

- Store successful plans as abstract object-relation skills, not pixel scripts.
- Retrieve by scene/mechanic similarity and adapt using the learned world model.
- Route click-only, movement, orchestration, and mixed games to specialized
  candidate generators while sharing one transition/value model.
- Run a small ensemble of rule hypotheses and learned dynamics; allocate actions
  and wall time by uncertainty and observed progress.
- Use later levels' higher score weight deliberately: once mechanics are known,
  minimize redundant probing and prioritize efficient plan execution.
- Keep a seven-hour global guard and benchmark CPU/GPU parity before submission.

**Gate:** leave-game-out evaluation must show broad multi-level depth rather
than one-game spikes; no game-specific identifiers or source-derived rules; at
least two independent seeds with verified trace diversity; staged Kaggle
preflight must reproduce local model hashes.

**Expected effort:** 3-6 additional weeks. **Score target:** 6-10+.

### Phase 5 — make the fly contribution biologically meaningful

This proceeds beside Phases 2-4 but never blocks the competent controller:

1. map 64x64 ARC space to the 36x39 optic-lobe hex layout;
2. send luminance/change to R1-R6-like channels and fixed color-opponent codes
   to R7/R8-like channels;
3. expose named T4/T5 motion, LC/LPLC salience, central-complex context,
   KC/MBON novelty/value, and DN/VNC action-prior summaries;
4. route previous action and observed consequence through ascending/efference
   channels instead of the eye;
5. learn only small, parameter-matched pooling/residual heads first; add local
   KC->MBON plasticity only after generic delayed-cue and novelty probes pass.

Required comparisons are controller-only, controller + real graph, identical
bypass, degree-preserving null, shuffled retinotopy, and named-module lesions.
The real graph earns credit only by beating them on the same candidate set,
training budget, and seeds.

## Promotion and submission discipline

- One frozen intervention, one exact local gate; no edit/revert tuning loops.
- A daily submission must test a material capability change, not a larger
  action budget or cosmetic variation.
- Public-game development is allowed but always labelled; game-held-out results
  choose architectures, while Kaggle hidden score chooses submissions.
- Keep controller performance and fly attribution separate. We may submit a
  high-scoring hybrid before full controls, but we do not claim that the fly
  caused its score until the controls support that statement.
- Checkpoint source, WORKLOG, model/data provenance, validation, and next work
  before each push. Never commit generated traces or large assets.

## Ordered next actions

1. Monitor the active CEM run without competing for memory bandwidth; record
   each completed-generation checkpoint and the final trace-ablation result.
2. Treat submission 56459984's 0.00 as the stop result for budget/loop-escape
   tuning; do not spend another slot on variants of the same capability.
3. Audit and pin a permissively licensed state-graph donor; reproduce it
   standalone before hybridizing it.
4. Implement Phase 1 behind a new config without changing frozen baselines.
5. Download and schema-audit the official human replay dataset for Phase 2;
   keep it outside Git and commit only hashes/provenance.
6. Build game-held-out evaluation before training the affordance/value model.
7. Begin the retinotopic/module compiler as a parallel, separately gated fly
   contribution; do not make it the critical path to the next score gain.

## Durable limitations and claim boundary

- Heuristic transmitter signs and uniform rate dynamics are not biological
  physiology.
- The public 25 games are development data; the Kaggle public leaderboard uses
  55 unseen games and the final private leaderboard another 55.
- Existing result distributions are extremely sparse and game-clustered.
- The current best local scores come from first-level completions and do not
  predict a hidden score reliably.
- Structural non-randomness is established; behavioral advantage is not.
- Score 10 is a credible engineering objective because current teams exceed it,
  but it requires a new world-model-and-planning system. It is not a credible
  outcome of more loop-escape tuning, a larger budget, or the 520-parameter head
  alone.

## 2026-09-22 — Second submission scored: 0.00 again

Submission **56459984** completed with a **public score of 0.00**, unchanged
from the first submission's 0.00.

| Submission | Config | Public score |
| --- | --- | ---: |
| 56444435 | 80-action ceiling, no loop escape | 0.00 |
| **56459984** | **600-action ceiling, loop escape mild** | **0.00** |

### Reading it honestly

The configuration change was real and was verified end to end: the served
config.yaml hash matched the loop-escape config byte for byte, and the
server-side preflight confirmed `mode=connectome` with all three array digests
matching. This was not a packaging failure. The agent that ran on the hidden set
was the one intended.

It simply did not find anything. The local 0.190476 came from a single public
game, `cd82`, out of 25. The hidden set evidently contains nothing the agent can
reach within 600 actions, which was recorded as a plausible outcome before
submitting.

**The budget and exploration levers are now exhausted as score levers.** 1600
actions bought nothing over 600 locally, and 600 bought nothing over 80 on the
hidden set. What separates 0.00 from a score is not how long the agent flails or
how widely it wanders; it is whether it can work out what a game wants. Nothing
built so far does that.

### Consequence for the plan

Two submissions have now been spent establishing that configuration tuning does
not move the hidden-set score. The remaining untried lever is a learned policy,
which is what Track B is training now. If a trained head also returns 0.00, the
honest conclusion is that a frozen connectome with a small readout cannot reach
the first level of an unseen ARC-AGI-3 game, and the project's contribution is
the controlled negative result plus the structural finding, not a leaderboard
position.

## 2026-09-22 — Phase 0: retinotopic optic-lobe encoder

### Why this comes before the planner, not after

The plan placed "make the fly useful" last, after a competent state/effect
controller and planner. That ordering makes the fly's contribution
**unmeasurable**: once a planner is solving games, ceiling effects hide whatever
the interface does, and the question this project exists to ask can no longer be
answered. The encoder is roughly a day of work and every control needed to
evaluate it -- degree-preserving nulls, the interface-matched bypass, the
positive control, the rewired mushroom body -- is already built and tested.

### The measurement that shaped the design

The plan proposed a "36x39 retinotopic optic-lobe mapping". Checking the data
first changed where it has to go:

| Population | Count | Carries `assignedOlHex1/2` |
| --- | ---: | --- |
| `ol_sensory` (photoreceptors) | 6,098 | **0 of 6,098** |
| `ol_intrinsic` | 23,720 | **all 23,720** |

**Photoreceptors carry no column assignment at all**, so they cannot be targeted
retinotopically. The coordinates live on the lamina and medulla interneurons --
L1, L2, L3, L5, Mi1, Mi4, Mi9, T1, C2, C3 -- spanning hex1 1..36 and hex2 1..39
across **892 occupied columns**. Those are one synapse downstream of the
photoreceptors and are the only population the data lets us address spatially.

### What was built

- `scripts/build_retinotopy.py` compiles the column map into a small hashed
  asset beside the graph (`retinotopy.npz`, SHA-256
  `ebc2b699e541330097a257003c2346f367d4beda1f04e88b2aaa1e1542db1a8d`), so a
  deployed bundle carries it without the 14 MB annotation table.
- `src/flygi/encoding/retinotopic.py` maps the 64x64 ARC grid onto the column
  lattice by a fixed affine assignment, so cells adjacent on screen drive
  columns adjacent in the eye.

### Verified on the real graph

| Check | Result |
| --- | --- |
| Neurons driven | 15,582 of 166,700 |
| Drive range | [-1.0000, 1.0000] |
| A spatially shifted image changes the drive | yes |
| **A 6x6 corner edit changes only 43 of 15,582 driven neurons** | **locality preserved** |

That last row is the whole point. Under the random sparse projection a local
edit perturbs the entire sensory population indiscriminately; here it stays
local, which is the property the optic lobe is built to exploit.

### Declared, and not claimed

Channel assignment is a **heuristic, not a physiological claim**. Luminance is
injected with positive sign to declared ON types (L1, Mi1, Mi4, Tm3), negative
sign to declared OFF types (L2, L3, Tm1, Tm2, Tm4, Tm9), and the changed-cell
signal goes to declared change types (T1, C2, C3, L5, Mi9). Mapping ARC's 16
categorical colours to a scalar luminance is likewise a declared ordering
choice. Both live in configuration so they can be varied and ablated rather than
assumed.

### Concurrent work in the same tree

A parallel session is implementing the Phase 1 state/effect controller:
`src/flygi/controller/` with `policy.py`, `scene.py` and `state_graph.py`, plus
`configs/state_graph_controller.yaml`, `scripts/evaluate_state_graph.py` and
three test modules, together with additive `ControllerConfig` changes to
`config.py`. That work is **uncommitted** in the shared working tree.

This entry and its commit therefore stage **only** the two Phase 0 files by
name. `git add -A` in this tree would sweep half-finished controller work into
an unrelated commit. All 320 tests pass with both sets of changes present, and
the plasticity and loop-escape configs verify unchanged.

### Next

Wire the encoder behind `encoder.kind: retinotopic`, then evaluate it against
the sparse projection on identical games, seeds and budget, and against the
existing controls. That comparison is the point of Phase 0.

## 2026-09-22 — Track B stopped early at generation 25: the objective plateaued

### Why it was stopped

| Generation | Best objective | Levels (8 training games) | Unique obs | Sigma |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 185.62 | 1 | 123.12 | 0.3688 |
| 4 | 300.62 | 3 | 113.12 | 0.1342 |
| 10 | 315.75 | 3 | 128.25 | 0.0845 |
| **16** | **320.25** | **3** | **132.75** | 0.0797 |
| 20 | 319.12 | 3 | 131.62 | 0.0807 |
| 24 | 256.12 | 2 | 131.12 | 0.0805 |

Every gain arrived in the first ten generations. The peak was **320.25 at
generation 16**, and nothing after it improved; generations 22 and 24 sampled
worse points and fell back to two levels. Sigma sat at **0.080** against its
declared floor of 0.075 from generation 8 onward, so the search had already
contracted as far as it was allowed to.

Running the remaining 35 generations would have cost roughly six hours to
re-sample a converged distribution. The run was stopped, the checkpoint retained,
and the best parameters extracted from generation 16.

### What did move

Level completions across the eight training games went from **1 to 3**, and
unique observations from 123.1 to 132.8. That is the first time anything in this
project learned its way to more levels rather than stumbling onto one.

**It is in-sample.** Those eight games are the training set, chosen to include
`cd82`, `sp80` and `r11l` precisely because they are the only games ever solved,
so the level term would not be identically zero. Three levels there says nothing
about held-out games, which is what the two runs now in flight measure.

### The two runs that decide what this means

Both over all 25 public games, seed 0, 600 actions, identical in every respect
except the named variable:

- `head-trained` — the generation-16 parameters, against the untrained
  `probe600-loopescape` baseline of **0.190476**;
- `head-trained-blind` — the same parameters with the descending trace **zeroed
  before the head sees it**.

The second is the one that matters for the project's question. If blinding the
head to the connectome barely changes the result, the head learned to ignore the
fly and this is an interface result, not a connectome result.
