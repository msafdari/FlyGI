# FlyGI durable worklog

This is the compact operational record for FlyGI. The detailed chronological
diary from repository creation through the second Kaggle submission remains
recoverable from Git history at commit `c3774e2`; it was deliberately pruned on
2026-09-22 so future sessions can recover the actual project state quickly.

Read this file before planning or editing. Reconcile it with `git status`, the
latest commits, active processes, and immutable result artifacts after every
handoff or context reset. Update it after each meaningful result, decision,
blocker, submission, or change in ordered next work. Never record secrets.

## Parallel Experiment 000 draft checkpoint — 2026-09-23 15:17 PDT

Experiment 000 planning is paused at a clean documentation-only checkpoint on
the isolated branch `codex/experiment-000`. No implementation code was added,
no experiment was launched, and the shared FlyARC checkout was not edited.

The checkpoint adds a detailed mushroom-body associative-learning protocol at
`experiments/000_mb_sanity/SPEC.md`, a scope/resume guide at
`experiments/000_mb_sanity/README.md`, and the experiment's durable record at
`experiments/000_mb_sanity/WORKLOG.md`. The draft now freezes the intended
MaleCNS populations and runtime blocks, trial state machine, paired-world task
battery, conservative exact-degree Curveball null family, primary controls,
statistical reductions, evidence labels, analytic kill tests, and additive
migration boundary. Independent audits covered equations/state transitions,
nulls/statistics, repository migration, biological sources, and internal
contradictions.

This is deliberately marked **PAUSED / DRAFT**, not preregistered or ready to
run. Resume from the experiment worklog's pause checkpoint. Before any code or
data work, close its four remaining specification items: recovery-only
semantics, exact Curveball sweep/telemetry and fresh-replication wording, the
remaining scalar/golden-test ledger, and a final clean contradiction audit.

## Everything goes through the fly, or nothing goes at all

This is the project's first principle and it outranks every other consideration
in this repository, including the score.

FlyGI exists to find out what the fly's innate wiring computes for free. A
component that produces a result *without* the connectome carrying it is not a
smaller version of that finding -- it is a different project wearing this one's
name. So:

1. **Every computation the agent depends on must be performed by fly neurons.**
   If a capability can be obtained by writing Python instead, writing the Python
   is a failure, not a shortcut. The controller diffing grids in Python while
   13,585 T4/T5 motion detectors sit unread is the canonical example of the
   mistake.
2. **Encoders, decoders and transformations exist only to make fly modules
   usable.** They are plumbing, and their job is to hand a fly circuit the kind
   of input it evolved to read and to take from it the kind of output it evolved
   to produce. They are not where the intelligence is allowed to live. Any
   parameter in the plumbing that starts doing real work is a bug.
3. **A circuit must be given input it can actually use before any claim is made
   about it.** Measured on 2026-09-23: the mushroom body was taught while
   receiving 0.00% of its input from any driven sensory population, and the
   motion and object detectors were evaluated on spatially scrambled input. Both
   produced nulls. Neither null was about the fly.
4. **When a fly module cannot do the job, say so plainly and stop** -- do not
   quietly substitute an engineered component and keep the name. A recorded
   limit of the connectome is a real result. A scaffold that scores while the
   connectome idles is not.

The test to apply before adding anything: *if the connectome were replaced by a
degree-preserving null tomorrow, would this component still work?* If yes, it is
not part of this project.

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

**The essence of the project, stated plainly: what computation does the fly's
innate wiring give us for free?** Not a network trained on the fly's shape, not
a network initialized from the connectome and then fitted -- the measured
synaptic graph itself, frozen, with its evolved modules doing whatever they
already do. The mushroom body's 4,064 Kenyon cells and 97 MBONs, the central
complex's ring attractor, the optic lobe's 892 retinotopic columns: these
circuits were shaped over roughly 400 million years for foraging, navigation and
learning in a real world. The question is how much of that transfers, unpaid, to
a benchmark nobody evolved for.

This is why every engineered component in this repository is on probation. A
scaffold that scores well while the connectome sits inert is a negative result
about the fly, however good it looks on a leaderboard. Whatever the agent scores,
the number that matters is the gap between the real graph and a degree-preserving
rewiring of it, because that gap is the only part that anatomy can claim.

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

## Coordination checkpoint — 2026-09-23 13:21 PDT

Created `CLAUDE_CODE_REFACTOR_HANDOFF.md` at Mustafa's request as the explicit
boundary between the live FlyARC queue and the incoming Experiment 000
mushroom-body refactor. No process, config, source module, result artifact,
commit, or remote was changed as part of this checkpoint.

Measured locally while preparing the handoff: `sg-bioeye-lc-permuted` and
`sg-bioeye-t4t5` were healthy and checkpointed; the two decoder arms had an
armed waiter; no launcher existed for the four registered `sg-mbdr-*` arms.
The operational decision is to finish and close the four already-running/armed
bio-eye/decoder arms, then **not launch the legacy MBdr battery**. Experiment 000
supersedes its PN/DAN selectors, dynamics, plasticity scope, and non-degree-exact
rewire, so deferral is a priority decision rather than a falsification of
H-MB-LEARNING. The handoff records exact config hashes, recovery behavior,
closure checks, ownership, and the staged logical-first refactor plan.

### Handoff adopted — Claude Code, 2026-09-23

The handoff above is adopted as the operating contract for the remainder of the
ARC queue. Confirmed at adoption: all four config SHA-256 values match the
handoff's frozen table; HEAD is the inspected `96353dd`; the decoder waiter is
armed; both active arms were at 68/75 and advancing. Until all four bundles
exist: monitor-only on the read-locked surfaces, no tuning from partials, no
duplicate launches, and the `sg-mbdr-*` battery is not launched -- reversing
this session's earlier plan to queue it, as a priority decision. Closure work
(artifact validation, declared comparisons with the preregistered 19/9/25
endpoints, the smallest endpoint analyzer if still needed, provenance and
source-equivalence audit including the git_dirty=2cf2098 mixed-launch caveat,
closure report, one tested closure commit) begins only after the fourth bundle
lands.

### Incident: repo-wide format touched the foreign workspace — 2026-09-23

A `ruff format .` during closure descended into the untracked
`.fly-or-fake-work/` directory and reformatted 7 Python files there, violating
the do-not-touch instruction. Formatting is semantics-preserving and the two
tracked modifications in that repo's own git predate the incident (ruff does
not format JSON), but its owner should review with their own `git diff`. No
revert was attempted -- most touched files are untracked there, and a revert
could destroy real in-progress work. Recurrence prevented: `.fly-or-fake-work`
is now in ruff's `extend-exclude`, and repo-wide format invocations are
avoided in favour of explicit paths. Disclosed to Mustafa immediately.

### ARC queue closed — 2026-09-23 evening

All four bio-eye/decoder arms are resolved: permuted (null, as preregistered),
bioeye-t4t5 (**the league's first HELPS**, +0.0717 CI [+0.005,+0.156] p=0.070,
22 v 13 levels, survived the hash-grade source audit), retdec (HURTS on score
at every preregistered endpoint while completing +5 levels everywhere — the
breadth/depth trade at its sharpest), surprise (killed 18/75, priority).
Submission 3 scored 0.00, consistent with both priors. MBdr deferred, not
falsified. Full detail, provenance, audit, and deviations:
`docs/arc_agi/ARC_CLOSURE_2026-09-23.md`. Registry, league, and this log agree.
Next step: hand the closure SHA to Codex; the Experiment 000 refactor starts
from it.

### Submission 3 assembled and shipped — 2026-09-23 14:0x PDT

On Mustafa's explicit instruction ("whatever improvements we have planned and
that we think will help that are crucial -- like efference copy -- make those
and submit all of those to kaggle asap"), which by the handoff's own authority
clause overrides its no-submit-during-closure provision. Deviation recorded
here; the running decoder arms are untouched (their code was imported at
launch).

**Shipped stack** (`configs/kaggle_bioeye_t4t5_efference.yaml`), tiers stated:
retinotopic-colour encoder + T4/T5 readout (measured HELPS, borderline, audit
pending), retinotopic-surprise coordinates (measured 3.5-cell localization;
behavioural arm still running), Johnston's-organ efference copy at 0.05
(measured separation/cancellation; behaviourally untested by design).
**Excluded**: MB learning -- 31:1 punishment-dominated teaching signal, unknown
sign, unevaluated; a deliberate omission, not an oversight.

**Verified before shipping**: packaging now carries `retinotopy.npz` (it did
not before -- the encoder would have failed closed on Kaggle); staged config and
controller byte-identical to intent; the exact config played locally (tn36
level completed at 80 actions); server file list confirmed all 8 files with the
modulators graph at 93,348,402 bytes; the SERVED config downloaded back and
hash-matched (`edb956eb...`), per the submission-2 precedent. Instrumentation:
`FLYGI_AGENT=` identity line per game, `FLYGI_DIAG=` every 100 turns
(decisive rate, states, outcomes), `FLYGI_ERROR=` with turn and game on any
exception before fail-closed propagation.

Dataset version pushed; kernel version 4 pushed. Submission to the competition
follows kernel completion.

## Current snapshot — 2026-09-22

- Private repository: <https://github.com/msafdari/FlyGI>.
- Branch: `main`, tracking `origin/main`.
- 325 tests pass; Ruff clean for FlyGI-owned files.
- Both official submissions scored **0.00**. No submission remains today.
- The Phase 1 state/effect controller and the Phase 5 fly tiebreaker are
  committed (`8ad3863`). 325 tests pass; Ruff clean across `src/` and the
  evaluator.
- A parallel session works in the same tree. Stage files by name; `git add -A`
  here would sweep in half-finished work.
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

### 7. Phase 5 — the fly returned to the decision loop (in progress)

The Phase 1 state-graph controller reached 7 of 25 games with progress against
the connectome policy's 2, which raised the objection that makes or breaks this
project: the fly had stopped doing anything. Phase 5 puts it back, at exactly
one place.

The controller ranks candidates by

```text
(retry_prefix, attempts, -(priority + exploration), TIEBREAK, bytes)
```

`TIEBREAK` was `_tie_digest`, a deterministic hash: reproducible, carrying no
information. `src/flygi/controller/fly_tiebreak.py` puts the connectome there and
nowhere else, so it cannot override legality, a known death state, a verified
plan, or a learned effect estimate. It speaks only where the controller is
genuinely indifferent. That placement is also what makes the experiment clean:
real graph, degree-preserving rewiring, and hash differ in one thing only.

Measured before the full run, per the `AGENTS.md` rule:

| Check | Trivial alternative | Result |
| --- | --- | --- |
| Does the fly discriminate? | a constant | 6/6 distinct action preferences after warmup; click scores span 1.8-4.5 |
| Does it change decisions? | the hash | diverges at step 1; 63% of 200 steps differ |
| Does it stay in its slot? | unconfined | action totals byte-identical with and without |

Turn 0 is exactly zero for every candidate, because the adaptive standardizer's
EMA mean equals its first sample. `preference()` returns 0.0 there, so an
unobserved turn degrades to the controller's own ordering rather than to noise.

Cost: the connectome advance is ~0.148 s/action, roughly 16x the controller
alone. Caching the per-turn decode was necessary first -- the trace changes once
per observation, but one turn ranks hundreds of candidate clicks, and
recomputing the readout reduction for each cost ~10x on click-heavy games
(ar25: ~15 min -> 98.8 s per 600-action row). Verified bit-identical by replay
hash before adoption.

The three-way ablation is running against the matched baseline below. Nulls
already exist at
`data/processed/male-cns-v1.0/literal-rate-signed/nulls/degree_preserving/seed-20260921`
and load as a tiebreaker (166,700 nodes / 24,559,055 edges, identical to real).

| Condition (3 seeds x 25 games x 600 actions) | Mean score | Levels | Games w/ progress |
| --- | ---: | ---: | ---: |
| Controller alone | 0.194691 | 20 | 7/25 |
| Controller + real fly | 0.216301 | **20** | 10/25 |
| Controller + grid-hash (state-dependent, no anatomy) | 0.179650 | 9 | 3/25 |

**Result: the fly does not beat the controller.** Level count is *exactly*
tied, 20 against 20. Score is `+0.021610`, 95% CI `[-0.166096, +0.186871]`,
`p=0.8350`. Row-level: 15 better, 10 worse, 50 tied. The connectome is
mechanically load-bearing -- decisive on 25-37% of turns -- and that influence
does not convert into levels.

What the fly does do is **trade depth for breadth**. It reaches a first level in
four games the controller never cracked (cd82, lf52, s5i5, sp80) and loses one
it had (ar25), for 10 games with progress against 7. With five discordant games
split 4-1 that is not significant either. Both conditions still complete twenty
levels in total; the fly spreads them differently.

**Against the anatomy-free control the fly does separate.** Real minus
grid-hash: levels `+0.146667`, 95% CI `[+0.013333, +0.293333]` (excludes zero),
`p=0.0822`; score `+0.036651`, `p=0.5028`. Injecting a *random* state-dependent
tiebreaker into the same seam costs the controller more than half its levels
(20 -> 9) and most of its coverage (7 -> 3 games), while injecting the
connectome costs it nothing. So the fly's signal is structured rather than
noise-like. Suggestive, not significant at 0.05, and confounded by scale: the
grid hash draws uniformly on [0,1) while the readout is smooth and standardized.
Do not report this as the connectome beating a matched control.

**Discipline note.** At 41 of 75 rows this comparison read `+10.6%` on score and
`+3` on levels, and was reported as partial. Seeds 1 and 2 erased it entirely.
The 41-row snapshot was seed-0-heavy, and seed 0 is where the fly's wins
concentrate. Partial matrices from a seed-ordered run are not small versions of
the result; they are a biased sample of it. Wait for the full matrix.

**Submission gate: not cleared.** The user's condition is that the fly be
load-bearing *and* the agent beat both 0.00 submissions. The fly is load-bearing
in the mechanical sense and produces no demonstrable improvement, so this agent
is not a submission candidate. The budget arm below is the live route to an
actual gain.

**How often is the fly actually decisive?** `fly_decisive_rate` in
`policy_diagnostics` counts turns where removing the connectome would have
chosen a different candidate: 24.7% on ar25, 28.5-37.2% on ls20. It is neither
inert nor saturated -- on roughly three turns in four the controller's own
learning already picks a unique winner and the fly is silent, which is the
guardrail working.

**The action budget is NOT binding. This inference was wrong and is retracted.**
All 125 rows at 600 actions ended `budget_exhausted` with zero wins, completions
landed as late as action 599, and exploration had not plateaued -- 72.9-74.6 new
observations in the last 100 actions against 91.5-91.7 in the first. That looked
like a binding budget and it was recorded as the cheapest score gain available.

The 1800-action arm settles it: **tripling the budget bought exactly nothing.**
21 matched seed-0 rows, all running the full 1800 actions, all
`budget_exhausted`: 7 levels at 600 and 7 levels at 1800, mean score identical
to six decimal places, and **zero level completions after action 600**. The
agent is still finding 62.3 novel observations per 100 actions at action 1800.

The lesson is that **novel-state discovery is not progress**. The agent wanders
into genuinely new states indefinitely and converts none of them into level
completions. Continued exploration was read as evidence of unfinished business;
it is evidence of an agent that cannot tell which states matter. The bottleneck
is credit assignment, not action count. `MAX_ACTIONS` stays at 600 -- raising it
costs wall-clock on Kaggle and buys nothing.

**Submission gate: not cleared.** The user's condition is that the fly be
load-bearing *and* the agent beat both 0.00 submissions. The fly is load-bearing
in the mechanical sense and produces no demonstrable improvement, so this agent
is not a submission candidate. The budget arm below is the live route to an
actual gain.

**How often is the fly actually decisive?** `fly_decisive_rate` in
`policy_diagnostics` counts turns where removing the connectome would have
chosen a different candidate: 24.7% on ar25, 28.5-37.2% on ls20. It is neither
inert nor saturated -- on roughly three turns in four the controller's own
learning already picks a unique winner and the fly is silent, which is the
guardrail working.

**The action budget is binding, and this is the cheapest score gain available.**
All 125 completed rows across both conditions ended by `budget_exhausted`; not
one ended in a win. Level completions run as late as action 514 (controller) and
599 (fly) -- the literal last action of the budget. Exploration has not
plateaued: rows still find 72.9 (controller) and 74.6 (fly) new observations in
their last 100 actions against 91.5/91.7 in their first 100, an 80-81%
retention, with only 3 of 75 rows finding 5 or fewer. A 1800-action arm is
running to measure the gain. Kaggle allows nine hours; at 0.148 s/action the fly
costs 266 s/game at 1800 actions, so the budget is not the constraint there.

Baseline games with progress: ar25, g50t, lp85, m0r0, r11l, tn36, vc33. The
75-row controller-only matrix is in
`results/connectome_agent/sg-full.rows.jsonl`; its final JSON write was lost
when the process exited, but every row is on disk.

**Reading the result in advance, so it cannot be read motivatedly later.** Real
above null is the first evidence in this project that anatomy buys ARC-relevant
computation. Real equal to null means the fly is acting as a seeded hash and the
honest report is that the scaffold scores, not the fly. Real below null is a
real finding too, and gets recorded.

### 8. The operating point is dead, and that outranks the mushroom body

Research before building, per the user's instruction. Three independent sources
converge on how connectome-based MB learning is actually done, and two of their
documented failure modes are ones this repository can be checked for in minutes.

**Established practice for KC->MBON learning:**

- Plasticity is **depression only**, never potentiation. Dopamine coincident
  with KC activity depresses the KC->MBON synapse (LTD). Published
  implementations use learning rate ~0.06 with a **weight floor** (~0.25 of
  baseline) so synapses cannot be driven to zero, plus slow recovery toward
  baseline as a forgetting term.
- Credit assignment uses an **eligibility trace**, decaying ~0.55 per step so
  roughly six steps stay eligible. Reward arrives after the action; without a
  trace there is nothing to assign credit to.
- Valence is anatomical: **PAM** neurons carry reward, **PPL1** punishment, and
  they innervate distinct MBON compartments. Punishment depresses the channel
  taken; reward depresses the channels not taken.
- KC->DAN synapses stay **fixed**; only KC->MBON is plastic.
- The code must be **sparse**, a few percent of KCs per stimulus, maintained by
  APL feedback inhibition.

**The two failure modes worth checking first, both documented:**

1. *Saturation.* If every KC fires every step the eligibility trace is a
   constant and the rule degenerates to a per-compartment scalar. One project
   traced this to KC->KC recurrence being 56% of KC input against 9.3% from APL,
   pushing loop gain above unity. **Ours is worse: KC->KC is 85.3% of KC input
   (642,932 edges) against 2.4% from APL.**
2. *No reach.* A published MB-lesion control found that cutting MB output left
   behaviour unchanged -- the MB never reached the readout, so no plasticity
   could have mattered.

**What the checks found here is a third thing, and it is worse.**

`modulator_treatment: zero` in the deployed config deletes the entire
dopaminergic pathway: **0 DAN->KC and 0 DAN->MBON edges**. There is no teaching
signal to gate anything. The `-modulators` build (`modulator_treatment:
positive`) restores 129,099 DAN->KC and 3,159 DAN->MBON edges and is the graph
any learning work must use.

But the blocking problem is the operating point. At the deployed `gain=0.9`:

| Group | mean abs activity | vs sensory drive |
| --- | ---: | ---: |
| `ol_sensory` (drive) | 2.295e-01 | 1x |
| `ol_intrinsic` (1 hop) | 2.332e-03 | 100x weaker |
| **descending neurons (the readout)** | **2.611e-06** | **87,906x weaker** |
| KC / MBON / DAN | 1.6-3.4e-06 | comparable to DN |

Float32 epsilon is 1.19e-7, so the readout carries roughly one significant digit
above quantization. **The whole post-sensory network is silent, not just the
mushroom body.** Incoming-L1 normalization makes rows sum to one, and with
signed weights a row of mixed signs averages to near zero, so amplitude is lost
at ~100x per hop rather than the ~0.9x the gain suggests.

This retroactively explains a great deal: why the connectome policy never beat
an interface-matched bypass, why the trained head generalized nothing, and why
the fly ties the controller while still beating a random tiebreaker -- its
readout is structured, but at an amplitude barely above the numerical floor.

**A gain sweep finds a narrow biological window.** KC active fraction against
recurrent gain, ten turns, biological target 0.05-0.11:

| gain | mean abs DN | KC frac >0.1 | mean KC |
| ---: | ---: | ---: | ---: |
| 0.9 (deployed) | 2.6e-06 | 0.000 | 0.0000 |
| 2.4 | 5.9e-05 | 0.000 | 0.0119 |
| **2.6** | 9.5e-05 | **0.031** | 0.0327 |
| **2.8** | 1.6e-04 | **0.188** | 0.0774 |
| 3.0 | 2.7e-04 | 0.800 | 0.1813 |
| 3.4 | 1.2e-03 | 0.991 | 0.6381 |
| 4.0+ | -- | 1.000 | ~0.97 (latched) |

Between silence and latching there is roughly `gain in [2.6, 2.9]`. There the
KC code is biologically sparse and DN amplitude sits ~40-100x above the current
value and ~1000x above float32 epsilon.

**A sharp prediction falls out of this.** At `gain~2.7` the real graph
(spectral radius 0.8289) sits at effective radius ~2.2 and comes alive, while a
degree-preserving null (radius ~0.23) sits at ~0.63 and stays silent. The 3.59x
structural separation, which has never produced a behavioural difference, would
for the first time be placed at an operating point where it *should* produce
one. That is preregistered here before the run.

**Execution directive for this plan (set by the user, 2026-09-23).**

Follow all five steps to completion before running the test and validation
batteries. Do **not** abort the implementation partway because an intermediate
check looks unfavourable, and do not revert work already built in this plan.
Measure twice, cut once: the measuring has been done -- operating point, KC
sparsity, DAN edge counts and the gain window are all recorded above -- so the
remaining work is the cut.

This deliberately suspends the `AGENTS.md` habit of killing a build at the first
bad intermediate signal, and it is not a licence to skip validation. Validation
happens at the end, in full, and its results are reported whatever they say. The
rule being replaced was aimed at *speculative* builds; this build's premises
were checked first, which is precisely why it earns a straight run. If a step
turns out to be impossible rather than merely discouraging, record it, finish
every other step, and report what was left out.

**Ordered plan.**

1. Re-tune the operating point on the `-modulators` graph: pick the gain where
   KC sparsity lands in 0.05-0.11, and confirm DN amplitude clears the float32
   floor by a wide margin. Nothing else can be trusted until this is done.
2. Run the MB reach test at that operating point: zero every MBON outgoing edge
   and check whether the action sequence changes at all. If it does not, MB
   plasticity cannot affect behaviour and the plan stops here.
3. Re-measure the existing three arms at the new operating point. Changing gain
   invalidates every score in this worklog; those scores are of a dead network,
   so this is a cost worth paying, but it must be paid explicitly and not
   quietly.
4. Only then implement KC->MBON depression: depression-only, floor at 0.25 of
   baseline, learning rate ~0.06, eligibility trace decaying ~0.55 per turn,
   PAM-gated on level advance and PPL1-gated on death, with the controller
   supplying the reinforcement signal the connectome has never had.
5. Control it with the rewired mushroom body already implemented in
   `rewire_mushroom_body`, and with reinforcement shuffled in time.

### 9. Validation battery for the mushroom-body build

Implementation complete and committed before any of this ran, per the user's
execution directive. Results recorded as measured.

**1. MB reach test -- PASSES, decisively.** Zeroing every outgoing MBON edge
changes the descending-neuron readout by **22.286% of its own magnitude** and
touches **92.2% of readout entries** (20 turns, `results/mb_reach_gain2.7.json`).
The published failure mode -- an MB that never reaches the readout, where a
lesion changes nothing and no plasticity could matter -- is absent here.
KC->MBON plasticity can affect actions. The per-turn effect decays across the
episode (0.316 at turn 1 to 0.151 at turn 20), which is worth watching but does
not threaten the result.

**2. Operating point -- the dead-network defect is fixed; sparsity is a declared
compromise.** The first gain sweep used uncorrelated random frames and picked
2.7. That was wrong. Real ARC frames are highly correlated -- a persistent grid
with small edits -- and correlated drive sustains the Kenyon-cell population far
more effectively. Re-swept with correlated input:

| gain | KC active frac (mean / max) | mean abs DN | x float32 eps |
| ---: | ---: | ---: | ---: |
| 0.9 (deployed) | 0.000 / 0.000 | 2.61e-06 | **22** |
| 1.5 | 0.000 / 0.000 | 1.09e-05 | 92 |
| 1.8 | 0.002 / 0.037 | 5.47e-05 | 460 |
| **2.0 (adopted)** | **0.123 / 0.555** | **5.95e-04** | **4998** |
| 2.2 | 0.265 / 1.000 | 1.36e-03 | 11448 |
| 2.7 | 0.496 / 1.000 | 8.96e-03 | 75292 |

Adopted 2.0. The readout now sits ~5000x above float32 epsilon against the
deployed 22x, which is the defect that matters most. Mean KC activity of 0.123
is **above** the biological 0.05-0.11 band and the population still latches on
individual turns (max 0.555), so the eligibility trace is not as sharp as the
literature's. Measured spread is 2.09, well clear of the degenerate zero, so the
trace still carries structure.

There is **no gain that delivers both** biological sparsity and a readout clear
of the numerical floor. The anatomy says why: KC->KC is 85.3% of Kenyon-cell
input against 2.4% from APL, which makes the transition from silent to latched
abrupt. The principled fix is to strengthen APL feedback rather than scale the
global gain -- a separate change with its own controls, not folded in here.

**3-4. Waking the network did not help, and neither did learning.** 3 seeds x 25
games x 600 actions, matched rows, clustered on games.

| Condition | Mean score | Levels/row | Levels | vs controller (score) |
| --- | ---: | ---: | ---: | --- |
| Controller alone | 0.194691 | 0.2667 | 20 | reference |
| Fly at gain 2.0, frozen | 0.203443 | 0.2800 | 21 | `+0.008752`, p=0.8625 |
| Fly at gain 2.0, **learning** | 0.203451 | 0.2400 | **18** | `+0.008760`, p=0.8675 |

Learning against no-learning is the comparison that matters and it is flat:
score identical to five decimal places, and the learning arm completes *fewer*
levels (18 against 21). Nothing here is significant; every confidence interval
spans zero comfortably.

**The learning rule is not inert.** Instrumented over three games: 29
`reinforce()` calls moving a total absolute weight change of 95.21. It fires, it
moves real weight at the right site, and it changes behaviour -- the learning and
frozen arms are not bit-identical. It simply does not help.

**The teaching signal is pathologically imbalanced, and this is the finding
worth keeping.** In that instrumented sample: **2 rewards against 27
punishments**. Across all 75 rows: 18 level advances against 569 game-over
frames, a ratio of about 31 to 1. Mushroom-body plasticity is depression-only,
so an agent that is punished thirty times for every reward spends nearly all of
its learning depressing PPL1-gated compartments. The PAM reward channel -- 316
of the 340 dopaminergic neurons -- fires almost never. The circuit is being
taught almost exclusively what not to do, by an agent that dies constantly and
succeeds rarely, and depression-only plasticity has no mechanism to recover from
that except slow decay toward baseline.

That is a property of the *task signal*, not of the fly. ARC-AGI-3 gives an
agent this bad no usable reward statistics, and no associative learning rule can
extract a curriculum from 2 positive examples.

**5. Falsification controls running** (`--fly-rewire-mb`, `--fly-shuffle-credit`).
With a null main effect they cannot explain anything away, but they are run
because the plan preregistered them and because a control that *did* show a
difference would indicate something wrong with the harness.

**Standing conclusion after this battery.** Three separate interventions --
tiebreaking, operating point, associative learning -- have each been implemented
correctly, verified to fire, and produced no score gain. The bottleneck is not
any of them. What remains untried is the fly's perceptual machinery: 13,585
T4/T5 motion detectors at 54.5x the readout's activity and 4,257 LC object
detectors at 16.1x, all firing on every frame, all upstream of the 1,314
descending neurons this agent actually reads. See section 10.


**The controller-only reference survives the operating-point change.** It never
touches the connectome, so gain does not affect it: 0.194691, 20 levels, 7/25
games stands as the comparison point. Every *connectome* score recorded before
this section was measured at gain 0.9 and describes a dead network, including
the degree-preserving null arm that completed during this build. Those are
retained as a record of the dead regime and are not comparable to what follows.

### 10. Reading the fly's perception instead of its motor output

Every intervention so far changed what the agent does with the signal. This one
changes which signal is read. Measured at gain 2.0 on the `-modulators` graph,
mean absolute activity relative to the descending neurons this project has
always decoded, with each population's response to a changed scene:

| Circuit | Neurons | Types | Activity vs DN | Change response |
| --- | ---: | ---: | ---: | ---: |
| T4/T5 motion detectors | 13,585 | 10 | **54.5x** | 4.0% |
| LC lobula columnar | 4,257 | **50** | **16.1x** | 4.4% |
| LPLC looming | 417 | 4 | 11.0x | 4.9% |
| ER ring neurons | 282 | 26 | 8.5x | 4.5% |
| **DN (deployed readout)** | 1,314 | -- | **1.0x** | 8.9% |
| EPG/PEN/PEG compass | 110 | 5 | 0.5x | 14.4% |
| PFL steering | 50 | 3 | 0.1x | 23.7% |

In absolute discriminative signal -- activity times change response -- T4/T5
carry roughly 25x what the descending neurons do. The project has been driving
photoreceptors, passing the signal through 13,585 motion detectors and 4,257
object detectors, and then reading the motor-output layer at the far end, which
is close to the faintest thing in the chain.

`population_indices` in `flygi.arc.factory` makes this a configuration change
rather than a recompilation: a readout group compiled into `groups.npz` is used
as-is, and one declared only under `groups:` is resolved against
`node_metadata.npz` by exact or prefix match. Adding a readout no longer costs a
24.5M-edge rebuild.

Three arms, each identical to `configs/literal_rate_mb_learning.yaml` apart from
the decoded population, learning off so the readout is isolated, matched against
`sg-g2-nolearn` (0.203443, 21 levels):

| Config | Readout | Size | Action spread (standardized) |
| --- | --- | ---: | --- |
| `literal_rate_lc_readout` | LC object detectors | 4,257 | 0.214-0.511 |
| `literal_rate_t4t5_readout` | T4/T5 motion | 13,585 | 0.124-0.303 |
| `literal_rate_central_complex` | EPG/PEN/PEG/ER/FC/PFL | 719 | 0.773-1.978 |

**Limitation recorded before the runs.** The central-complex arm reads a circuit
that is not receiving the input it evolved to integrate. A ring attractor
integrates *angular velocity*: the fly updates its compass from its own turning.
An ARC agent does not turn, does not move, and has no heading. A null result
there is therefore weak evidence about the circuit rather than strong evidence
against it. Driving it properly means synthesizing a heading from something in
the ARC frame, which is engineering rather than anatomy and needs its own
justification.

### 11. We have not been using the circuits properly. Three of three.

Prompted by the user asking whether the components are connected and calibrated
as they should be. They are not, and this revises the "stop adding fly
components" recommendation made just before it. The null results so far are not
evidence that these circuits cannot help; they are evidence that each was given
input it cannot use.

**1. The mushroom body is wired to a sense we never drive.** Input composition
of the 4,064 Kenyon cells, by total absolute incoming weight:

| Source | Share of KC input |
| --- | ---: |
| Other Kenyon cells (KCg-m, KCab-s/m/c, KCa'b'-*) | ~85% |
| APL | 2.0% |
| PAM dopaminergic | ~7% |
| `cb_sensory` (the olfactory pathway) | **0.00%** |
| `ol_sensory` (what we drive) | **0.00%** |

In *Drosophila* the mushroom body is primarily an olfactory structure: Kenyon
cells are driven by uniglomerular projection neurons from the antennal lobe.
Those neurons live in `cb_sensory`, 4,868 of them, and the encoder drives
`ol_sensory` -- photoreceptors -- exclusively. So the learning experiment in
section 9 taught a circuit that receives essentially none of this agent's
sensory input, and is otherwise dominated by its own recurrence. The rule fired
and moved weight on activity that was mostly indirect leakage. That is why it
did nothing, and it says nothing about mushroom-body learning.

**2. T4/T5 and LC are correctly wired but fed spatially scrambled input.** Their
anatomy checks out -- photoreceptors to `ol_intrinsic` lamina/medulla (97.4% of
T4/T5 input) to T4/T5 to LC (62.0% `ol_intrinsic`, 26.2% `visual_projection`).
The defect is upstream. `build_sensory_projection` assigns each photoreceptor 64
**uniformly random** features:

```python
columns = generator.integers(0, FEATURE_DIMENSION, size=(rows, per_row))
```

Neighbouring photoreceptors therefore see uncorrelated parts of the screen. T4
and T5 compute direction-selective motion by comparing *adjacent* columns with a
delay; LC neurons integrate over retinotopic neighbourhoods. Both are pure
spatial computations, and retinotopy is destroyed before the graph sees
anything. The three perception arms now running are motion and object detectors
fed a spatial scramble.

**3. The two encoders are each broken, in complementary ways.**

| Encoder | Retinotopy | Colour |
| --- | --- | --- |
| `sparse_projection` (deployed) | **destroyed** (random) | preserved (16-way one-hot) |
| `retinotopic` | preserved (columnar lattice) | **destroyed** (`grid / 15.0` scalar) |

This is the real explanation for the retinotopic encoder's 0.190476 -> 0.003156
collapse, which was previously guessed at. ARC colours are **categorical**:
colour 3 is not between 2 and 4. Mapping sixteen categories onto a scalar
luminance ramp discards the distinction the benchmark is built from. So one
encoder gives the fly colour without space, the other space without colour, and
the fly's visual system needs both.

**Consequence.** No experiment run so far has given the fly's visual hierarchy an
input it could use, and no experiment has given the mushroom body any sensory
input at all. The sequence of nulls is consistent with that and does not yet
license a conclusion about the fly.

**Next, and it is upstream of everything else:** a retinotopic encoder that
preserves colour identity. The fly's medulla carries roughly 60 cell types per
column, each encoding different visual features, so distributing ARC's sixteen
categorical colours across distinct medulla types within each column is
anatomically defensible rather than invented. The currently running arms become
the matched scrambled-retinotopy control for it rather than wasted work.

### 18. Three proposed improvements, two killed by measurement in ten minutes

Asked what else would make a positive difference. Applying the claim-tier rule
before building anything:

1. **More seeds per arm -- rejected, measured.** Variance decomposition of the
   paired differences (bio-eye vs control): between-game variance 0.080,
   within-game 0.068. At 3 seeds the game term contributes ~78% of the cluster
   variance, so doubling seeds narrows CIs by ~6% for 2x compute. The games
   are the noise, not the seeds. (The probe script's own printed inference
   said otherwise; its threshold compared between to within instead of
   between to within/n_seeds -- the claim-tier rule catching a bad bridge in
   the same hour it was written.)

2. **Saliency-guided candidate injection -- demoted, measured.** On 323
   click-tie turns across three click-dominant games, the controller's
   candidate menu already lies within 3 cells of the fly's saliency argmax on
   76% of turns (median 2.0 cells; 5% beyond 8). The menu is not the
   bottleneck. Parked with its measurement; worth revisiting only if the
   decoder arms show an effect that the 5% tail could be capping.

3. **Treatment-matched endpoints -- adopted, free.** Measured on
   sg-g2-nolearn: 6 of 25 games never click, so every click-decoder effect is
   structurally diluted ~24% on the full-set mean, and game heterogeneity is
   the dominant noise term (see 1). The decoder arms now carry PREREGISTERED
   endpoints, declared before either arm has run a row: primary = the 19
   click games, secondary = the 9 click-dominant games, with the full 25-game
   comparison always reported alongside. Registered in EXPERIMENTS.yaml; this
   is a design decision made blind, not a post-hoc subgroup.

### 17. The efference copy: the connectome learns what it just did

Prompted by asking whether any non-visual sense exists for ARC. Two do, and one
was mis-wired: reinforcement already reaches dopamine correctly, but the
agent's knowledge of its own action -- proprioception -- was spliced into the
VISUAL feature vector under the old encoder and lost entirely under the
bio-eye one.

**Precision, before anyone else has to burst this balloon.** Only the
*connectome* was action-blind; the controller always knew its actions, and the
fly speaks only at ties. And the old scrambled arms were *near*-blind rather
than blind: the 16 action features were sampled into roughly 90 of 390,272
projection connections -- present as noise. The section-16-adjacent claim
"every bio-eye arm was action-blind" is correct only with "connectome" in
front of it.

**Built and measured.** `encoder.efference_copy: antennal_mechanosensory`
delivers the previous action to Johnston's organ, the fly's own mechanosensory
entry (672 neurons, 34 types, sorted round-robin over the 8 action slots --
convention, declared). The chosen action rides from the controller into
`fly.observe(previous_action_id=...)`, and the forward model's reference
carries the same copy.

| property | measured |
| --- | --- |
| KC action separation (scale 0.05) | **144.7%** -- the learning site knows the action |
| LC (visual readout) perturbation | 0.2% |
| surprise on action-only turns | **exactly 0.000** at every scale (the copy cancels) |
| localization through the real path | 3.4 cells (surprise alone: 3.5) |

**Honest expectation, preregistered.** `sg-bioeye-lc-efference` should be
near-null on score BY CONSTRUCTION: the copy cancels out of the saliency map
and barely moves the readout. Its load-bearing use is `sg-mbdr-learn` -- the
mushroom body could not previously know which action preceded a reward, so
depression-only learning could form context->valence associations but never
context->action ones. The mbdr config now carries the copy at the calibrated
scale. A null on the bio-eye arm does not falsify H-EFFERENCE; a null on the
mbdr retest would.

### 16. The decoder was the scrambled half all along -- measured, then fixed

Prompted by asking what perception work is *demonstrably* wrong after the
bio-eye null. Reference practice (flyvis, Lappalainen et al., Nature 2024)
decodes the optic lobe as instantaneous per-column, per-cell-type activity.
Ours decodes click coordinates from **body-id-ordered blocks** of the readout
-- spatially meaningless, the exact mirror of the input scramble fixed in
section 12.

**The measurement that proves it** (16 trials, structured scenes, one 6x6
change at a known place, bio-eye encoder):

| method | median localization error |
| --- | ---: |
| hex-map readback of the state change (joint) | **0.8 cells** |
| prediction-error readback (joint) | **0.8 cells** |
| the deployed coordinate head | 23.5 cells |
| chance | 37.2 cells |

The fly's optic-lobe state knows WHERE to sub-cell precision; the deployed
decoder reads that same brain at chance. Side-finding: T4/T5 carry no hex
assignments in MaleCNS, so the spatial substrate is the 15 mapped
lamina/medulla types.

**Implemented**: `decoder.coordinate_source` --

- `retinotopic_state`: click x/y scores from per-column |state change| mapped
  back through the inverse of the encoder's affine assignment;
- `retinotopic_surprise`: the reference is the frozen connectome advanced on
  the previous frame -- the network free-running as its own one-step forward
  model. Predictive coding in spirit, JEPA-adjacent in shape, and zero trained
  parameters because the predictor IS the graph. Cost: one extra advance per
  turn.

**The wired-path measurement, and the day's most interesting number.** Through
the real `preference()` path (separable x+y marginals over candidate clicks):
state_change degrades to **12.1 cells**; surprise holds at **3.5**. Mechanism:
the free-run reference contains the network's own settling transients, so they
cancel, leaving only input-caused deviation -- the forward model explains away
self-generated dynamics. The prediction is not decoration; it is what makes
the marginal readback usable.

**Claim boundary, stated before the arms run.** All of this is localization,
measured; none of it is score. H-RETINO-DECODER is open, `sg-bioeye-lc-retdec`
and `sg-bioeye-lc-surprise` are registered against `sg-bioeye-lc`, and three
straight full-matrix nulls counsel exactly zero confidence beyond the
measurements themselves.

### 15. The bio-eye result: null, and the third partial-lead collapse

`sg-bioeye-lc` against its matched scrambled control `sg-lc`, 75 rows each,
identical readout, identical everything except the encoder:

| | score | levels | delta |
| --- | ---: | ---: | --- |
| scrambled projection (`sg-lc`) | 0.241245 | 16 | reference |
| retinotopic categorical colour (`sg-bioeye-lc`) | 0.250396 | **16** | `+0.009151`, CI `[-0.125, +0.172]`, p=0.817 |

Levels exactly tied. H-RETINOTOPY-COLOUR is **null** on the LC readout: giving
the visual hierarchy input it can use -- adjacency preserved, colours
categorical, motion visible to T4/T5 at 3.4x -- changed nothing the score can
see. The T4/T5 bio-eye arm is still running and gets its own verdict.

**The partial-lead collapse, third occurrence.** At 59 rows the matched delta
had drifted to +0.072 with a 14-12 level lead; the final 16 rows erased it
completely. Same shape as the tiebreak arm (+10.6% at 41 rows, gone at 75) and
consistent across this project: seed-ordered partials drift positive in the
middle rows and regress by the end. The league's no-verdict-on-partials rule
has now paid for itself three times. The currently running arms show partial
deltas of +0.12 (permuted) and +0.07 (bio-eye t4t5); given the pattern, the
expectation is regression, and no excitement is licensed before row 75.

Both scrambled-readout arms also completed and received verdicts:
`sg-lc` +0.0378 (p=0.526) and `sg-t4t5` -0.0280 (p=0.557) against
`sg-g2-nolearn` -- H-PERCEPTION-READOUT closes as null on complete pairs.

### 14. The mushroom body done right: built, calibrated, awaiting its turn

Built now, to run after the bio-eye battery settles, per the plan. Everything
below is construction and calibration; no behavioural claim is made until the
`sg-mbdr-*` arms run.

**The input bus (H-MB-INPUT-BUS).** `encoder.mb_input_bus: colour_histogram`
drives the 627 uniglomerular projection neurons -- measured direct: 22,581
synapses reaching 3,811/4,064 Kenyon cells at ONE hop, 7.23% of KC input weight,
which corrects section 11's "two hops" framing -- with the screen's global
colour histogram as an odour-mixture analogue. Glomerular types are assigned to
colours by sorted order, round-robin: convention, not biology, and the
permutation-control pattern applies here too if the bus ever shows an effect.
Live probe: PN activity 2.5e-05 -> 2.3e-01; KC patterns separate colour-9 from
colour-3 screens by 23-78%; reinforcement moves |dW|=3.6. The composite
projection refuses any overlap with the visual encoder, so nothing can be
double-driven silently.

**APL sparsification (H-APL) -- supported, with a mechanism finding worth more
than the knob.** Scaling the 4,633 APL->KC inhibitory synapses is exact to the
digit and touches nothing else. But in a signed tanh network, inhibition CANNOT
sparsify absolute activity: it drives cells negative, and |-0.4| counts as
active. Measured: APL x4-x25 made |abs| sparsity worse (0.123 -> 0.177,
latching 0.95). On the positive lobe -- firing, the only biological reading --
APL behaves exactly as Lin et al. 2014 predicts: x2 0.098, x4 0.078 (in the
0.05-0.11 band), plateauing at x10-25 because negative feedback self-limits.

**Corollary fix: rectified eligibility.** The plasticity trace previously used
|abs| Kenyon activity, which counted an APL-inhibited cell as MORE eligible the
harder it was suppressed -- backwards from the biology it models. Eligibility
now reads the positive lobe only (`eligibility_rectified`, default true,
declared with the measurement that exposed it; `false` restores |abs| for
comparison).

**Calibration, not assumption.** `mb_input_scale` swept against the KC firing
band: every naive scale (1.0 down to 0.02) saturates the KC pool through its
85% recurrence; 0.003 at APL x4 lands at 0.091, in band, DN live at 1.5e-04.
The sparse-and-loud-but-starved regime (APL x10-25, tiny scale, separation up
to 227% but DN dimming toward 5e-05) was measured and deliberately not chosen.

**Registered ahead of running:** `sg-mbdr-nolearn` (circuit changes alone, vs
`sg-g2-nolearn`), `sg-mbdr-learn` (the fair retest of H-MB-LEARNING, vs
`sg-mbdr-nolearn`), and both falsification controls, gated on the main arm
separating from its baseline. The league lists them as `missing` until they
run.

### 13. The bio-eye battery: main arm, its falsification control, and T4/T5

Three arms complete the encoder experiment. All assemble and discriminate,
verified before launch, all on the threaded matvec (4 threads, bit-identical).

| Arm | Config | What it isolates |
| --- | --- | --- |
| `sg-bioeye-lc` (running) | `literal_rate_bioeye_lc` | encoder vs the scrambled `sg-lc` control: does retinotopic categorical colour matter at all |
| `sg-bioeye-lc-permuted` (queued) | `literal_rate_bioeye_lc_permuted` | assumption A: does it matter *which* medulla type carries which colour |
| `sg-bioeye-t4t5` (queued) | `literal_rate_bioeye_t4t5` | the highest-signal readout (13,585 T4/T5, ~25x DN discriminative signal) with usable input; `sg-t4t5` becomes its matched scrambled control |

**The permutation control, measured before use.** `colour_permutation_seed:
20260923` reassigns 14 of 16 colours to different cell types; the 0/15
collision pair still shares a channel, so the collision structure is matched.
Deterministic across builds. An identity permutation is refused at construction
-- a control that changes nothing must fail loudly, not run quietly.

**Known imperfection of the control, declared rather than discovered later:**
cell types differ in neurons per column, so reassigning colours shifts total
injected drive by ~4% (1531.5 vs 1593.2 on a random frame) and nonzero support
by ~3.7%. Matched in information and structure, not exactly in input energy.
The adaptive per-neuron standardizer removes global scale downstream, but a
small score difference between the declared rule and the permutation should be
checked against drive totals before being read as mapping semantics.

**How to read the three results together, written before any of them exist:**

- bio-eye > scrambled, permuted = bio-eye: retinotopic categorical input helps;
  the specific colour-to-type assignment is harmless convention, as assumed.
- bio-eye > scrambled, permuted < bio-eye: the assignment itself carries weight
  it has no biological right to carry; report as an interface artifact, not as
  fly computation.
- bio-eye = scrambled: the encoder fix, the best-motivated change in the
  project, did not matter either -- and the perception readouts join the list of
  correctly-implemented components that produced nothing.

### 12. Plan: give the fly's eye a real image (measured before designing)

The first principle above says every computation must be carried by fly neurons.
Section 11 established that no experiment has yet given a fly circuit input it
could use. This is the fix, and per the user's instruction the assumptions were
measured **before** the design rather than after.

#### What was measured, including two assumptions that failed

| # | Assumption | Measured | Verdict |
| --- | --- | --- | --- |
| A1 | The optic lobe can be addressed retinotopically | 23,720 `ol_intrinsic` neurons, 892 columns on a 36x39 lattice; `ol_sensory` photoreceptors carry **no** column assignment, 0 of 6,098 | holds -- inject at lamina/medulla, not photoreceptors |
| A2 | A column has enough distinct cell types to carry 16 colours | **15** types, not 16: C2, C3, L1, L2, L3, L5, Mi1, Mi4, Mi9, T1, Tm1, Tm2, Tm20, Tm4, Tm9. 814 of 892 columns (91.3%) carry all 15 | **FAILED as stated** -- one collision is unavoidable |
| A3 | ARC colour 0 is background, so 15 types suffice for colours 1-15 | Over 1,200 real frames across 4 games: colour 0 is **2.72%**, not background. Colour 9 dominates at 36.89%, then 12 at 17.18%, 4 at 15.37%, 5 at 13.03% | **FAILED** -- there is no free colour to drop |
| A4 | The mushroom body's real input pathway could be driven | `cb_sensory` reaches **4,025 of 4,064** Kenyon cells in **2 hops**, inside the K=4 budget | holds, with a caveat below |

A2 and A3 would each have forced a revert within two commits. They are recorded
here because the design below is shaped by their failure, not by their success.

#### The design

**Injection site.** The 892 occupied columns, at the lamina and medulla
interneurons, because photoreceptors carry no coordinates. The ARC 64x64 grid
maps onto the hex lattice by the fixed affine assignment already compiled by
`scripts/build_retinotopy.py`.

**Colour.** Colour `c` drives medulla type index `c mod 15`. Fifteen channels,
sixteen colours, so colours 0 and 15 share a channel. The rule is fixed and
game-independent **on purpose**: choosing the collision from the measured
frequencies above would tune the encoder to four games and is exactly the kind
of engineering this project must not put in the plumbing. The collision is
declared, not hidden, and 78 columns (8.7%) carrying fewer than 15 types lose
their highest channels.

This is the fix for the previous retinotopic encoder's 0.190476 -> 0.003156
collapse. That encoder preserved space and destroyed colour, mapping sixteen
categories onto a scalar luminance ramp `grid / 15.0`. ARC colours are
categorical: colour 3 is not between 2 and 4.

**Change detection is removed, deliberately.** The previous encoder spent T1, C2
and C3 on an explicit changed-cell channel. Those channels are returned to
colour, and **T4/T5 compute motion themselves** from the frame-to-frame sequence,
which is what 13,585 direction-selective neurons are for and what the first
principle demands. Network state already persists across actions, so the
temporal structure the computation needs is present.

**Non-visual features.** The legal-action mask and previous-action one-hot are
not visual quantities and have no retinotopic home. They keep the existing sparse
projection into a disjoint sensory subset, declared as plumbing.

#### The mushroom body, and an honest caveat

A4 holds structurally, but driving `cb_sensory` means piping ARC data into the
fly's **olfactory** input. ARC has no odours, so this is not a more faithful use
of the organ than the current one -- it is a different arbitrary mapping. The
defensible framing, and the only one to be used: the mushroom body is an
associative memory whose input bus is the projection-neuron pathway, and that bus
is what gets driven. It is not being treated as an olfactory organ. This is a
**separate change from the encoder** and must not be bundled with it, or the two
confound.

#### Order of work

1. Compile `retinotopy.npz` into the `-modulators` bundle, which does not have it.
2. Implement the colour-preserving retinotopic encoder.
3. Verify before running anything: neighbouring ARC cells drive neighbouring
   columns; distinct colours drive distinct types; T4/T5 respond to a moving
   stimulus more than to a static one.
4. Run it against the scrambled-retinotopy arms already in flight, which become
   its matched control.
5. Only afterwards, and separately, consider the mushroom-body input bus.

## Execution telemetry

Every runnable component is instrumented. Result bundles already recorded
*provenance* -- which graph, which config, which game, hashed. What nothing
recorded was *execution*: what a run did, in what order, how long each stage
took, what it decided and why, and how it ended. That lived in ad-hoc `print`
calls whose format differed per script, so reconstructing a run meant reading
the source that produced it.

`src/flygi/telemetry.py` is the single place that changes. One JSON object per
line in `results/telemetry/<run_id>.jsonl`, append-only, so a killed run still
leaves everything up to the moment it died -- which is when telemetry matters
most. The console keeps its existing prose: machines read the file, people read
the terminal, neither is degraded for the other.

**Coverage: 22 of 22 scripts plus the `flygi` CLI.** Each gets `run.start`,
`run.end` and a recorded cause when it does not finish, from one line at its
`__main__`.

The five questions a reader or tool can answer without the source:

| Question | Answered by |
| --- | --- |
| what | `event` (dotted, hierarchical) plus `data` |
| when | `ts` wall clock, `elapsed_s` monotonic, `seq` for ordering within a timestamp |
| where | `run.start`: git commit and dirty flag, host, platform, Python and package versions, pid, argv, cwd, plus the resolved path and SHA-256 of every config read |
| how | `phase.begin`/`phase.end` with per-phase duration and outcome |
| why | every decision, warning and failure carries `reason` |

Read them with `scripts/inspect_telemetry.py`: recent runs, one run in full,
filtered by component or event name, `--failures` for bad endings, `--json` for
another tool to consume.

**Three defects the tests and first runs caught, all fixed:**

- `json.dumps(default=str)` invokes `__repr__` on the payload, which is
  arbitrary code and can raise anything. The guard caught only `TypeError` and
  `ValueError`, so an awkward object could have killed a six-hour evaluation.
  Now deliberately broad, degrading the event to a warning.
- `argparse --help` exits via `SystemExit(0)`, which was recorded as **failed**.
  Every help invocation would have poisoned the failure list until real failures
  stopped standing out. Clean exits are now `ok`; nonzero is `failed` with the
  code.
- A coverage audit reported the CLI as instrumented. It was a false positive:
  `cli.py` owns an unrelated function also called `entrypoint`. The CLI was
  genuinely uninstrumented and now is, via an aliased import.

Secrets are never captured: environment recording is an explicit allowlist, and
a test asserts a token in the environment does not reach the log.

## Interruption and recovery

Every evaluation checkpoints each completed row to `<condition>.rows.jsonl`
immediately, rows are independent and deterministic given (seed, game) -- the
tiebreaker and its standardizer are reset per game -- so an interrupted run
loses at most the row in flight, and `--resume` continues exactly. Laptop sleep
is not an interruption at all: macOS suspends the processes and they continue
on wake.

The gap was recovery after a real death (reboot, battery, kill): nothing
auto-restarts and the launch commands lived in nobody's head reliably.
`scripts/resume_runs.py` closes it using what telemetry already records --
every run's full argv at `run.start`. It lists each condition that has a
checkpoint but no final bundle and no clean `run.end`, prints the exact command
to continue it, skips anything currently running (checked against the process
table), and relaunches only with `--exec`. After any reboot:

    uv run python scripts/resume_runs.py --exec

## Execution speed

The agent is one sparse matvec in a loop, and SciPy's `csr_matvec` is a
single-threaded C kernel that Apple's Accelerate does not touch. Measured on the
deployed graph (166,700 nodes, 24,994,595 edges, float32) on an Apple M4: 54.0
ms per matvec at 3.7 GB/s, against roughly 120 GB/s of machine bandwidth. The
operation is bandwidth-bound and was using about 3% of the machine.

| Implementation | ms | GB/s | Speedup | Bit-identical |
| --- | ---: | ---: | ---: | --- |
| SciPy CSR, single thread | 54.0 | 3.7 | 1.00x | reference |
| Numba `njit(parallel=True)` | 18.7 | 10.7 | 2.88x | **no**, 1.19e-07 |
| **SciPy + threaded row split** | **14.4** | **13.9** | **3.76x** | **yes** |

End to end on a real 120-action game: 24.2 s at one thread, 10.5 s at four
(2.31x), 10.2 s at six -- with **identical replay hashes at every thread count**,
so no baseline in this worklog needs re-measuring. The end-to-end figure is
below the matvec figure because encoding, decoding and the environment step are
serial.

**Why row splitting is exact.** Each output element is one row's dot product,
computed by SciPy's own kernel in SciPy's own order. Float32 addition is not
associative, so order is everything. Splitting *within* a row -- a GPU segmented
reduction, or Numba's restructured reduction -- is not exact, which is why Numba
was measured, found slower *and* inexact, and removed again rather than adopted.

**The dangerous defect found on the way, and the reason to have written the
test.** `csr_matrix((data, indices, indptr), copy=False)` **copies anyway**:
measured, the block does not share memory with the parent even when every dtype
already matches. That would double the 200 MB matrix and, far worse, silently
sever in-place plasticity -- the mushroom body writes weights through the parent
matrix, and a copied block would never see them, so section 9's learning would
have appeared to run while changing nothing. Blocks are now built as empty
shells with their arrays assigned afterwards, and `SpmvPlan.rebuild` raises if
they ever stop sharing memory rather than degrading quietly.

Defaults and gotchas are in `docs/performance.md`; the numbered pitfalls are in
the `src/flygi/dynamics/spmv.py` docstring. Short version: default 4 threads,
`FLYGI_SPMV_THREADS=6` for a machine to yourself, `=1` to reproduce a
pre-optimisation measurement, and keep `arms x threads <= 10`.

## The experiment league

`EXPERIMENTS.yaml` at the repository root is the central claim-tracker: every
condition ever run, the baseline it is fairly compared against, the operating
regime it belongs to, and the hypothesis its result moves. `scripts/league.py`
joins it with the immutable bundles, the live checkpoints and the telemetry to
render the leaderboard -- the registry owns the *why*, the artifacts own every
number, so the table cannot drift from reality. `LEAGUE.md` is the generated
snapshot; edit the registry, never the snapshot.

Guardrails, each one a mistake this project actually made:

- **No verdict from a partial.** A 41-row seed-ordered partial once showed
  +10.6% that the full matrix erased. Partials get a delta labelled `partial`
  and an explicit "biased sample, no verdict" warning.
- **No cross-regime comparison.** gain0.9 numbers are measurements of a
  numerically dead network; the league refuses to compare them against live
  ones (controller-only excepted, since it uses no connectome).
- **Unregistered bundles are surfaced loudly.** All 20 historical Track A/B
  bundles are now registered, so the full ablation record -- 35 experiments, 10
  hypotheses, 3 regimes -- is in one queryable place.

The hypothesis register in `EXPERIMENTS.yaml` supersedes the prose assumptions
table below as the tracked state; the prose stays as narrative.

## Assumptions register

Every mapping from an ARC quantity onto a fly quantity is an invention until
shown otherwise. This is the list, kept current, so no reader has to guess which
results rest on a choice rather than a fact. Each is labelled in the source with
`ASSUMPTION` or `HYPOTHESIS` at the line that encodes it.

| # | Assumption | Where | Status | If wrong |
| --- | --- | --- | --- | --- |
| A | Colour `c` drives medulla type index `c % 15` | `encoding/retinotopic.py` | **assumed, biologically unmotivated** | Results hold as "retinotopic categorical input helps", not as "the fly's visual feature channels help" |
| B | Channel order is the sorted type name | `encoding/retinotopic.py` | assumed, arbitrary | Nothing, if A's permutation control is null |
| C | Drive magnitude is fractional colour occupancy of a column | `encoding/retinotopic.py` | assumed | Weakly constrained; ~3.4 ARC cells per column |
| D | All drive is positive; ON/OFF opponency dropped | `encoding/retinotopic.py` | assumed | The lamina's opponency is unexercised by this input |
| E | T4/T5 can compute motion from the frame sequence | `encoding/retinotopic.py` | **hypothesis, partially verified** | See below |
| F | Dopamine's sign in ordinary propagation is positive | `configs/*_modulators.yaml` | declared approximation | Modulator contribution to rate is mis-signed; plasticity uses activity and real anatomy, not this sign |
| G | The mushroom body may be driven through its olfactory input bus | WORKLOG section 12 | **assumed, not yet built** | ARC has no odours; this is a different arbitrary mapping, not a more faithful one |
| H | `gain=2.0` is the right operating point | `configs/literal_rate_mb_learning.yaml` | measured compromise | KC sparsity sits at 0.123 against a biological 0.05-0.11; declared, not hidden |

**On A, the largest one.** Medulla and lamina types are not colour bins. L1 and
L2 head the ON and OFF luminance pathways; Mi and Tm types carry sustained and
transient features. None of them encodes "ARC colour 7". The mapping exists
because the grid has sixteen categories and a column has fifteen addressable
types, and something had to be chosen. **The control that tests it** is a
permuted colour-to-type assignment: if a permutation scores the same, the
specific mapping carries nothing and only the categorical-plus-retinotopic
structure matters. That control must run before any claim that the fly's visual
*types* are doing work.

**On E, including a wrong measurement.** The first check compared population-mean
T4/T5 activity for a moving versus a static bar and found a ratio of 1.001,
which reads as failure. That metric was wrong: direction-selective cells encode
motion in *which* cells fire, not how many. Measured at the pattern level, the
frame-to-frame change in T4/T5 activity is **3.41x** larger for a moving bar,
2.53x for LC, with the conditions separated by ~10% of activity. Motion is
visible. What is **not** established is that it is visible as *direction-
selective* motion: a frozen rate model has none of the explicit delay lines that
make T4/T5 direction-tuned in the animal, so this may be undifferentiated change
sensitivity wearing a motion detector's name.

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

## Submission gate (set by the user, 2026-09-23)

Nothing is submitted unless **both** hold:

1. **The fly is load-bearing.** The agent must use the connectome in a way that
   changes its decisions. The Phase 1 state-graph controller alone is not a
   submission candidate however well it scores locally -- a scaffold that scores
   with the connectome inert is a negative result about the fly wearing a
   leaderboard entry as a disguise.
2. **It beats both existing submissions.** `56444435` and `56459984` each scored
   0.00, so the bar is a nonzero leaderboard score.

Condition 1 is not satisfied merely by the fly being present in the process. It
requires a control arm showing the connectome contributes beyond what any
state-dependent tiebreaker would: see the `grid_hash` arm (no anatomy, varies
with the observation) and the degree-preserving null arm. If the real fly ties
the grid hash, the fly is decoration and the honest report is that the
controller scores.

Slots reset 00:00 UTC, one per day.

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

1. Finish the Phase 5 three-way ablation (controller alone / + real fly / +
   degree-preserving null fly) and record all three rows before interpreting any
   of them.
2. If the real fly beats both the null fly and controller-alone, that is the
   submission candidate and the headline claim. If it ties the null, report that
   the controller scores and the fly does not, and say so in the social drafts.
3. Treat submission 56459984's 0.00 as the stop result for budget/loop-escape
   tuning; do not spend another slot on variants of the same capability.
4. Audit and pin a permissively licensed state-graph donor; reproduce it
   standalone before hybridizing it.
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
