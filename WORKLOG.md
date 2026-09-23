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
- 320 tests pass; Ruff clean for FlyGI-owned files.
- Both official submissions scored **0.00**. No submission remains today.
- A parallel session is implementing the Phase 1 state/effect controller in the
  same working tree (`src/flygi/controller/`, uncommitted). Stage files by name;
  `git add -A` here would sweep in half-finished work.
- No raw connectome, compiled arrays, ARC game packages, result traces, model
  checkpoints, credentials, virtual environments, or generated notebooks belong
  in normal Git history.

### Experiments closed on this date

| Experiment | Outcome | Score change |
| --- | --- | --- |
| Budget 80 → 600 → 1600 | Saturated at 600 | none beyond 600 |
| Plasticity, real vs rewired mushroom body | Falsification inconclusive | none |
| Track B trained head | Uses the connectome; **zero held-out generalization** | none held out |
| Phase 0 retinotopic encoder | **Worse on every axis** | 0.190476 → 0.003156 |

Four experiments, zero score improvements. The single actionable defect found is
the coordinate head, which explores 3.29x less than random clicking in the six
games where clicking is the only legal action.

### The coordinate-head defect, diagnosed

**Temperature is not the problem.** Six click-only games, three seeds, 600
actions:

| Condition | Mean score | Mean unique observations |
| --- | ---: | ---: |
| Coordinate temperature 0.2 (submitted) | 0.000000 | 71.7 |
| Coordinate temperature 1.0 | 0.000000 | 67.0 |
| Coordinate temperature 4.0 | 0.000000 | 67.0 |
| **Random clicking** | **0.009425** | **235.6** |

1.0 and 4.0 produced **identical** results, which is the clue. At a near-uniform
temperature of 4.0 the agent still touches only 1-2% of the grid:

| Game | Unique coordinates used | Share of 4,096 cells |
| --- | ---: | ---: |
| `r11l` | 96 | 2.3% |
| `s5i5` | 52 | 1.3% |
| `tn36` | 63 | 1.5% |
| `vc33` | 52 | 1.3% |
| `lp85` | 1,434 | 35.0% |

**The cause is the branch order, not the distribution.** The head selects by:

```
if explore_unchanged_click: seeded uniform
elif centroid is not None:  novelty_centroid   <- deterministic
else:                       factorized_sample  <- the only temperature-controlled path
```

When a click *does* change the frame, `centroid` is not None, so the agent
deterministically clicks the centroid of the changed cells and the
temperature-controlled sample is never reached. That collapses it onto a handful
of self-reinforcing locations in exactly the games that respond to clicking.

`lp85` is the proof: it has a 2.5% effect rate, so clicks almost never change
anything, the unchanged-click branch fires instead, and coverage jumps to 35%.
**The heuristic explores widely precisely when the game ignores it, and collapses
precisely when the game responds.**

`decoder.coordinate_fallback: factorized` now disables the centroid branch. A
test of it is running over the same six games and seeds. This is a defect fix
with a measured mechanism behind it, not a tuning pass.

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

### Track B: the head uses the connectome, and generalizes nothing

CEM trained the 520-parameter action head on eight public games, stopped early
at generation 25 of 60: the objective peaked at **320.25 at generation 16**,
nothing after improved, and sigma sat at its 0.075 floor from generation 8. The
remaining 35 generations would have re-sampled a converged distribution.

All 25 public games, seed 0, 600 actions, split by whether the game was in the
eight-game training set:

| Condition | All 25 | Training (8) | **Held out (17)** |
| --- | ---: | ---: | ---: |
| Untrained (the submitted policy) | 0.190476 | 0.595238 | **0.000000** |
| **Trained head** | **0.283458** | **0.885805** | **0.000000** |
| Trained head, descending trace zeroed | 0.000000 | 0.000000 | 0.000000 |
| Random legal, 600 actions, seeds 0-2 | 0.097568 | — | — |

**Two findings, pulling opposite ways.**

*The head genuinely uses the connectome.* Zeroing the descending trace before
the head sees it drops the score from 0.283458 to **exactly 0.000000**, and mean
unique observations from 263.4 to 169.5. The head did not learn to route around
the graph; without the graph it does nothing. That is the cleanest
connectome-dependence result the project has produced.

*It generalizes nothing.* Every point of its advantage is on games it trained
on: 0.885805 there against the untrained 0.595238. On the seventeen held-out
games it scores **0.000000**, exactly like the untrained policy. The two games
it solved, `ar25` and `sp80`, are both in the training set.

This predicts the hidden-set outcome directly: a trained head would also score
0.00, because the hidden set is held out by construction. **Track B is not a
submission candidate**, and training harder would only deepen the in-sample fit.

### 3. The coordinate head is worse than random clicking

A diagnostic over the 20 games no condition has ever solved found that the
obvious explanation is wrong. **Effect rate is not the problem.** Actions change
the frame at a similar rate whether or not a game is ever solved:

| Group | Fly effect rate | Random effect rate |
| --- | ---: | ---: |
| Solved (5 games) | 84.7% | 91.2% |
| **Never solved (20 games)** | **76.3%** | **81.1%** |

The agent is not stuck. Its actions do things. It simply gets nowhere, which
rules out exploration volume as the core failure and points at what it does with
the effects it causes.

**Six games expose `ACTION6` as their only legal action**, so coordinates are
the *only* thing that can differ between conditions there. Isolating them:

| Game | Fly unique observations | Random unique observations | Ratio |
| --- | ---: | ---: | ---: |
| `ft09` | 130 | 81 | 0.63x |
| `lp85` | 15 | 14 | 0.91x |
| `r11l` | 121 | 576 | **4.76x** |
| `s5i5` | 51 | 276 | **5.42x** |
| `tn36` | 62 | 339 | **5.47x** |
| `vc33` | 51 | 126 | 2.48x |
| **mean** | **72** | **236** | **3.29x** |

With the identical single action available, **uniform random clicking explores
3.29 times more than the coordinate head**, and random solved `r11l` while the
fly never has. The novelty-centroid and untried-grid logic is not merely
unhelpful in these games; it is actively worse than clicking at random, and it
accounts for roughly 63% of all clicks the agent makes.

`lp85` is separately pathological: a 2.5% effect rate and 15 unique observations
for the fly, 2.2% and 14 for random. Almost nothing either agent clicks changes
the frame at all, so that game needs targeted rather than broader clicking.

A coordinate-temperature test is running over those six games at three seeds:
the frozen 0.2 against 1.0 and 4.0. This is a component that is demonstrably
worse than chance at its one job, so raising its temperature is a defect fix
rather than a tuning pass -- though it is still public-set development and is
recorded as such.

### 4. A retinotopic interface made things worse, not better

Phase 0 existed to test the standing excuse that the connectome has never had a
fair interface. All 25 public games, seed 0, 600 actions, identical to the
submitted configuration except the encoder.

| Measurement | Sparse projection (submitted) | **Retinotopic** |
| --- | ---: | ---: |
| Mean score | **0.190476** | **0.003156** |
| Games with a level | 1 (`cd82`) | 1 (`sp80`) |
| Mean unique observations | 280.3 | 238.0 |
| Mean action entropy (bits) | 1.703 | 1.398 |

Preserving retinotopy made the agent **worse on every axis measured**: sixty
times lower score, less exploration, less varied behaviour. Both conditions
completed one level, but the retinotopic one's was worth 0.0789 against the
sparse condition's 4.76.

**The most likely cause is a trade I did not notice making.** The sparse encoder
feeds a 16-channel one-hot of the frame, so colour identity is preserved
exactly. The retinotopic encoder collapses those 16 categorical colours onto a
scalar luminance ramp before injecting them, because a column has to receive a
number. ARC is a game about categorical colour, and two unrelated colours with
adjacent indices become nearly identical under that mapping.

So Phase 0 bought spatial structure and paid for it in colour structure, and the
exchange was bad. That is a specific, testable explanation rather than a
mystery, and per the standing rule it will be *tested cheaply before* any
colour-preserving encoder is built.

**This also weakens the project's standing excuse.** "The connectome has never
had a fair interface" has been the explanation for every null result so far. One
dimension of fairness has now been restored, and performance fell. That is
evidence, not proof -- the colour trade confounds it -- but it is the first
direct test of the excuse, and the excuse did not survive it cleanly.

### 5. Disabling the novelty centroid: the first real improvement

**The defect.** The coordinate head selects by branch order:

```
if explore_unchanged_click: seeded uniform
elif centroid is not None:  novelty_centroid   <- deterministic
else:                       factorized_sample  <- the only temperature-controlled path
```

When a click changes the frame, `centroid` is not None and the agent
deterministically clicks the centroid of the changed cells, never reaching the
sampler. Temperature is therefore irrelevant: 1.0 and 4.0 produced **identical**
results. `lp85` proves the mechanism -- its 2.5% effect rate means clicks rarely
change anything, the unchanged-click branch fires instead, and coverage jumps to
35% of the grid. The heuristic explores widely precisely when the game ignores
it and collapses precisely when the game responds.

**Six click-only games, three seeds, 600 actions:**

| Condition | Mean score | Unique obs | Levels | Games solved |
| --- | ---: | ---: | ---: | --- |
| Centroid ON, T=0.2 (submitted) | 0.000000 | 71.7 | 0 | none |
| Centroid ON, T=4.0 | 0.000000 | 67.0 | 0 | none |
| **Centroid OFF** | **0.010120** | **247.4** | **3** | `r11l`, `vc33` |
| Random clicking | 0.009425 | 235.6 | 3 | `r11l` |

Coordinate coverage recovered roughly fourteen-fold: `r11l` 96 to 1,383, `s5i5`
52 to 1,352, `tn36` 63 to 1,391, `vc33` 52 to 1,367 distinct cells of 4,096.

**All 25 games, seed 0, 600 actions:**

| Condition | Mean | Click-only (6) | Other (19) | Unique obs | Games solved |
| --- | ---: | ---: | ---: | ---: | --- |
| Submitted | 0.190476 | 0.000000 | 0.250627 | 280.3 | `cd82` |
| **Centroid OFF** | **0.195388** | **0.020466** | 0.250627 | **322.6** | `cd82`, `r11l` |

**Strictly dominant: 1 game better, 0 worse, 24 unchanged.** The nineteen games
where clicking is not the only action are **identical to six decimal places**, so
the change does no harm where it does not apply, and all of the gain is where
the defect was.

**Status: adopted as the default, not a submission on its own.** The overall
margin is +2.6%, far short of the 2x bar for spending a daily slot, and both
prior submissions scored 0.00 on games this class of fix does not reach. It
should be carried into whatever the Phase 1 controller produces rather than
spent alone.

**What it cost.** The defect shipped in both competition submissions. It had six
passing tests, none comparing it against clicking at random. It is the exact
failure the standing rule in `AGENTS.md` was written for, found four days late.

### 6. The Phase 1 state-graph controller: 3.5x the games reached

All 25 games, **three seeds**, 600 actions, same strict-offline harness, action
ceiling, legality and replay contracts as every other condition.

| Condition | Rows | Mean score | Levels | **Games with progress** | Games solved |
| --- | ---: | ---: | ---: | ---: | --- |
| Random legal | 75 | 0.097568 | 6 | 2 / 25 (8%) | `r11l`, `sp80` |
| Centroid-OFF connectome | 25 | 0.195388 | 2 | 2 / 25 (8%) | `cd82`, `r11l` |
| **State-graph controller** | 75 | 0.194691 | **20** | **7 / 25 (28%)** | `ar25`, `g50t`, `lp85`, `m0r0`, `r11l`, `tn36`, `vc33` |

**Mean score is a tie. Breadth is not.** The controller completes **20 levels
against the connectome's 2**, and reaches progress in **3.5x as many games**. Its
promotion gate passed: mean above the 0.097568 random baseline, with seven
progress games against a required minimum of three.

Per-game means, and note the consistency across seeds:

| Game | Mean | Seeds |
| --- | ---: | --- |
| `tn36` | 2.304995 | 1.978 / 2.533 / 2.404 |
| `lp85` | 1.693618 | 2.224 / 2.478 / 0.379 |
| `r11l` | 0.626983 | 1.190 / 0.662 / 0.028 |
| `g50t` | 0.169976 | 0.094 / 0.082 / 0.334 |

**Five of these games had never been completed by anything in this project**:
`ar25`, `g50t`, `lp85`, `m0r0`, `tn36`. `lp85` is the one with a 2.5% effect
rate, where nothing either agent clicked used to change the frame. `tn36`'s mean
of 2.30 is the highest per-game score recorded here.

The mean parity is a scoring artifact rather than equivalence: the connectome's
0.195 comes almost entirely from `cd82`, a single game whose first level happens
to be worth 4.76, while the controller earns its number across seven games. On a
hidden set, breadth of progress is the property that transfers; a single lucky
game is not.

**The tension this creates.** The controller uses **no connectome at all**. Its
own evaluator states that no connectome assets or game identities are available
to it. Submitting it would put the best score on the board under a project named
for a fly brain that had nothing to do with it. That is the Path A / Path B fork
recorded earlier, now with numbers attached, and it is the user's decision rather
than a technical one.

### Phase 0 — retinotopic optic-lobe encoder

`encoder.kind: retinotopic` injects the 64x64 grid into the fly's own columnar
lattice, replacing the random projection that destroys spatial structure.

Where it injects was decided by measurement, not by the plan. Photoreceptors
(`ol_sensory`) carry **no** column assignment -- 0 of 6,098 -- so they cannot be
targeted retinotopically at all. The coordinates live on **23,720
`ol_intrinsic`** lamina and medulla interneurons (L1, L2, L3, L5, Mi1, Mi4, Mi9,
T1, C2, C3) spanning hex1 1..36 and hex2 1..39 over **892 occupied columns**.

`scripts/build_retinotopy.py` compiles that map into a hashed asset beside the
graph (`retinotopy.npz`, SHA-256 `ebc2b699e541330097a257003c2346f367d4beda1f04e88b2aaa1e1542db1a8d`)
so a deployed bundle needs no annotation table.

Verified on the real graph: 15,582 neurons driven, and a 6x6 corner edit changes
only **43** of them. Under the random projection any local edit perturbs the
whole sensory population; here it stays local, which is the property the optic
lobe exists to exploit.

Channel assignment (ON: L1/Mi1/Mi4/Tm3, OFF: L2/L3/Tm1/Tm2/Tm4/Tm9, change:
T1/C2/C3/L5/Mi9) and the mapping of 16 categorical ARC colours to a scalar
luminance are **declared heuristics, not physiological claims**, and live in
config so they can be ablated. The bypass is refused a retinotopic projection,
because its projection must address the readout population.

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
expected array hashes. No fallback policy was used. The published dataset's
`config.yaml` was downloaded back and hashed before submitting
(`63b50521c324ecd1c2d39e1498dd8113b9d6838731ea7f31b3fb8a94317e5c7c`,
byte-identical to the intended config); the preflight verifies the three array
hashes but **not** the config, so serving the previous version would otherwise
have silently submitted the 0.000000 condition.

Both submissions establish the same thing: **configuration tuning does not move
the hidden-set score.** Budget is saturated (1600 actions bought nothing over
600 locally; 600 bought nothing over 80 on the hidden set), and the held-out
split above shows why -- every local gain so far lives on specific known games.

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
