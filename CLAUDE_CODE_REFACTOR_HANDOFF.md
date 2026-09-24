# Claude Code handoff: close FlyARC cleanly before the FlyGI refactor

**Audience:** Claude Code, currently operating the FlyARC experiment queue
**Issued:** 2026-09-23 (America/Los_Angeles)
**Repository:** `/Users/mustafasafdari/Documents/ChatGPT/FlyGI`
**Current branch at inspection:** `main`, tracking `origin/main`
**Inspected HEAD:** `96353dd` (`Preregister click-game endpoints for the decoder arms; kill two ideas by measurement`)
**Status:** Historical coordination record. The queue described below is closed;
do not relaunch it from this document.

> **Closure notice — 2026-09-23:** The ARC queue reached closure commit
> `ca26587`. Three conditions produced complete 75-row bundles; the surprise
> condition was stopped by priority decision and has only a partial checkpoint.
> Treat sections 1–4 below as the record of the then-live handoff, not current
> launch instructions. The current Experiment 000 draft and resume point live
> under `experiments/000_mb_sanity/`; remaining ARC closure corrections are
> recorded in the root `WORKLOG.md`.

This document was requested by Mustafa to coordinate two concurrent workflows. It
is deliberately additive: its creation does not authorize a broad refactor while
the current jobs are alive. Direct instructions from Mustafa and `AGENTS.md`
remain higher authority.

## The decision in one paragraph

FlyGI is becoming an umbrella research program, not primarily an ARC leaderboard
repository. The next mainline milestone is **Experiment 000: a biologically
specified MaleCNS mushroom-body conditioning experiment**, followed—only if the
mechanism survives controls—by low-data online personalization. FlyARC will be
preserved as Experiment 002 and as an important negative/engineering record; it
will not be erased or rewritten. Finish the two active bio-eye arms and the two
already-armed decoder arms under their frozen ARC regime. Then close and
checkpoint their evidence. **Do not launch the registered `sg-mbdr-*` battery.**
Its extraction rules, dynamics, plasticity, and null are materially different
from the incoming Experiment 000 contract, so running it now would spend hours
answering a question we have already decided to reformulate.

## North star

> **The computation has to go through the fly's brain, or nothing goes at all.**

Encoders and decoders may translate between a task and biological populations,
but they must be constrained plumbing. They may not solve the task around the
connectome. Biological claims require the native circuit to beat controls that
hold the non-biological plumbing fixed.

The project-wide public question is now:

> **What useful computations are latent in biological wiring that evolved for
> entirely different purposes?**

The career-facing sequence is:

1. **Experiment 000 — MB sanity checks:** prove that the extracted MaleCNS
   PN→KC→MBON circuit, with compartment-specific DAN modulation and APL
   inhibition, can learn elementary associations under explicit controls.
2. **Experiment 001 — FlyMB/FlyRec:** ask whether that circuit adapts to an
   unseen person's preferences from unusually few observations.
3. **Experiment 002 — FlyARC:** preserve and continue the ARC program only when
   it tests a clearly specified connectome contribution rather than an
   anatomy-free controller wearing a fly-shaped wrapper.
4. **Experiment 003 — capability atlas:** compare native biological topology to
   matched nulls across memory, novelty, latent-state, control, and world-model
   probes.

The canonical planning context for that program is currently:

`/Users/mustafasafdari/Downloads/FlyGI_CODEX_HANDOFF.md`

That handoff is context and a research charter, not permission to refactor a
live checkout. An implementation-grade Experiment 000 specification will be
owned by the Codex workflow after the ARC closure point described below.

---

## 1. Live ARC state: snapshot, not a verdict

Mustafa reported the following queue shortly before this handoff:

| Condition | Reported progress | Role |
| --- | ---: | --- |
| `sg-bioeye-lc-permuted` | 62/75 | H-COLOUR-MAP control |
| `sg-bioeye-t4t5` | 61/75 | second H-RETINOTOPY-COLOUR arm |
| `sg-bioeye-lc-retdec` | 0/75, chained | retinotopic state-change decoder |
| `sg-bioeye-lc-surprise` | 0/75, chained | connectome prediction-error decoder |
| `sg-mbdr-*` | registered only | legacy mushroom-body battery |

A read-only local inspection at **2026-09-23 13:21 PDT** saw the first two
checkpoints at 64/75 and 63/75 respectively, confirming that they were still
progressing. These numbers will be stale when you read this. Treat checkpoint
counts as health telemetry only—never as scientific evidence.

### Process topology actually observed

- The two active jobs are exact `scripts/evaluate_state_graph.py` invocations:
  3 seeds × 25 games, 600-action budget, 4 sparse-matvec threads per arm.
- Their checkpoints and final bundles live under
  `results/connectome_agent/`.
- The parent chain script observed during inspection was:
  `/private/tmp/claude-501/-Users-mustafasafdari-Documents-ChatGPT-FlyGI/cff83bb1-4408-49fb-9bcd-66f308a8f609/scratchpad/chain_bioeye.sh`.
- The decoder waiter was genuinely armed at:
  `/private/tmp/claude-501/-Users-mustafasafdari-Documents-ChatGPT-FlyGI/cff83bb1-4408-49fb-9bcd-66f308a8f609/scratchpad/chain_retdec.sh`.
- That waiter polls for **both** final bio-eye bundles, then launches
  `sg-bioeye-lc-retdec` and `sg-bioeye-lc-surprise`, again at 4 threads,
  3 × 25 rows, and 600 actions.
- Relevant scratch logs are `bioeye_permuted.log`, `bioeye_t4t5.log`,
  `retdec.log`, and `surprise.log` in the same scratchpad.
- `caffeinate -i -t 10800` was active at inspection.
- **No process or launcher for any `sg-mbdr-*` arm was found.** Those conditions
  are registered in `EXPERIMENTS.yaml`; they are not actually queued.

### Frozen config identities

Record these as the expected on-disk identities. The final run record must use
the hash captured by telemetry for that particular process, not merely assume
the current file still matches.

| Condition | Config | SHA-256 observed 2026-09-23 |
| --- | --- | --- |
| `sg-bioeye-lc-permuted` | `configs/literal_rate_bioeye_lc_permuted.yaml` | `393d2c2168f827cbc07569410651184202734859fb02dc61a98298b265105896` |
| `sg-bioeye-t4t5` | `configs/literal_rate_bioeye_t4t5.yaml` | `759214b63be51057282ca35795d3b14d79123bac1ad971926bb3668acdcff335` |
| `sg-bioeye-lc-retdec` | `configs/literal_rate_bioeye_lc_retdec.yaml` | `4fdcff17eaa1b1002c87ca86410524125ffd4d08d014cf8a8248eb4643fb76d9` |
| `sg-bioeye-lc-surprise` | `configs/literal_rate_bioeye_lc_surprise.yaml` | `99417e77f0528540be64b2d86dc64d6713805f83f231313fb0f7fe7190c16833` |
| legacy `sg-mbdr-*` | `configs/literal_rate_mb_done_right.yaml` | `5e7f681a185c9122d707817220349dc1d45048ded2f2c6166a63c13ee4f0119a` |

### Provenance caveat that must be disclosed

The active arms' `run.start` telemetry reports `git_commit=2cf2098` and
`git_dirty=true`. The already-armed decoder jobs will import the checkout that
exists when the waiter launches them, currently based on a later commit. This is
a mixed-launch history. It does not automatically invalidate the comparisons,
because the interventions are opt-in through separate configs, but it **must not
be hidden**.

For closure, determine which intervening commits can affect each executed code
path. Report the result as one of:

- `source-equivalent`: intervening changes provably do not enter either arm;
- `source-different but comparison-matched`: both members of the relevant pair
  execute the same changed path;
- `source-confounded`: an intervention and its baseline differ in source code
  beyond the declared treatment.

Do not call a source-confounded comparison a null or a win. Do not rerun it
without an explicit decision from Mustafa; first report the cost and the exact
confound.

---

## 2. What Claude Code should do now

### 2.1 Preserve the four-arm bio-eye/decoder sequence

1. Let `sg-bioeye-lc-permuted` and `sg-bioeye-t4t5` finish.
2. Confirm the armed waiter launches exactly one process for each decoder arm
   only after both final input bundles exist.
3. Let both decoder arms finish.
4. Do not modify source, configs, dependencies, compiled graph data, or result
   files while a queued process could still import them.
5. Do not duplicate-launch a healthy condition.
6. Do not interpret or publicize a partial delta.

The following surfaces are read-locked until all four final bundles exist:

- `scripts/evaluate_state_graph.py`
- `configs/state_graph_controller.yaml`
- the four hashed configs in the table above
- `src/flygi/config.py`
- `src/flygi/controller/fly_tiebreak.py`
- `src/flygi/controller/policy.py`
- `src/flygi/encoding/**`
- `src/flygi/decoding/**`
- `src/flygi/dynamics/**`
- `data/processed/**/literal-rate-signed-modulators/**`
- every live checkpoint, final bundle, and telemetry file

Documentation-only planning outside those surfaces is safe. Do not make a
tracked source commit merely to make the checkout look clean while the decoder
waiter is pending.

### 2.2 Monitor; do not tune

Health checks should answer only:

- Is the checkpoint row count increasing?
- Is its modification time fresh?
- Is there exactly one evaluator for the condition?
- Does telemetry contain errors or a non-`ok` `run.end`?
- Did the expected final bundle appear?

Do not use a partial score, level count, or effect size to change code, seeds,
games, mappings, endpoints, or queue order. This project has already seen three
positive-looking partials collapse at the complete matrix.

### 2.3 Recovery rules

Each completed `(seed, game)` row is append-only and resumable. If a **started**
evaluator dies, use the exact telemetry-recorded command and existing checkpoint;
`scripts/resume_runs.py --exec` can recover it and skips completed identities.

There is one important hole: `resume_runs.py` cannot recover a stage that has
never launched. If the machine or parent workflow dies before the decoder pair
starts, re-arm `chain_retdec.sh` manually after confirming that no decoder
process already exists. Preserve the exact launch commands in the closure
report because the scratchpad waiter is ephemeral.

Never delete a checkpoint to “start clean.” Never reconstruct a command from
memory when telemetry contains the original argv.

### 2.4 Stop after the decoder pair

Do **not** launch:

- `sg-mbdr-nolearn`
- `sg-mbdr-learn`
- `sg-mbdr-learn-rewired`
- `sg-mbdr-learn-shuffled`

This is a priority decision, not a negative result. Keep their registry entries
and configs so the historical plan remains auditable. Mark them deferred or
superseded only when writing the final closure record; do not mark their
hypotheses falsified.

Why stop there:

| Legacy ARC MB choice | Incoming Experiment 000 requirement | Consequence |
| --- | --- | --- |
| substring-selected 627 PN bus driven by ARC colour histogram | exact `class == "ALPN"` population (686 total), with the 314 direct PN→KC cells distinguished and balanced frozen synthetic cue panels | the input populations and task are different |
| PAM/PPL/PPM prefix DAN heuristic, legacy count 354 | exact `class == "DAN"`, 340 cells, then named compartment-specific DAN pools | the teaching population is different |
| plasticizes all 61,210 KC→MBON edges | 6,183 existing edges in two preregistered KC→MBON compartment targets for the primary test | the adaptive state is different |
| direct DAN→MBON adjacency and delayed eligibility participate in gating | compartment identity gates plasticity; delayed reward is excluded from the core gate | the learning rule answers a different question |
| rewire preserves each MBON's input count and per-MBON weight multiset | exact bipartite degree preservation on both sides, with side/subtype/compartment strata and validated mixing | the old “degree-preserving” null is not degree-exact |
| whole-brain float32 tanh, `log1p`/incoming-L1 weights, heuristic signs, gain 2.0, K=4 | an explicitly specified float64 PN/KC/APL fixed-point model and frozen MBON value equation | the neural dynamics and normalization are different |
| APL ×4 calibrated inside the ARC full-network runtime | APL gain calibrated reward-free on the Experiment 000 cue ensemble | the calibration does not transfer |

Running the legacy battery cannot validate the new extraction or mechanism.

---

## 3. Exact scientific questions the four remaining ARC arms close

### `sg-bioeye-lc-permuted`: H-COLOUR-MAP

**Intention:** determine whether the declared mapping from ARC colour IDs to
medulla cell types carries useful signal, or whether only the generic
categorical-plus-retinotopic structure matters.

**Primary comparison:** `sg-bioeye-lc-permuted` vs `sg-bioeye-lc`.

**Prior expectation:** regression toward the null. The partial delta is not
evidence.

**Interpretation:** if the permutation ties the declared mapping, the particular
colour→type identity is an arbitrary interface convention. If it is materially
worse, inspect the known ~4% drive-energy and ~3.7% support mismatch before
attributing an effect to medulla semantics.

### `sg-bioeye-t4t5`: H-RETINOTOPY-COLOUR, second readout

**Intention:** test the retinotopic categorical encoder through T4/T5 motion
populations against the matched scrambled-input `sg-t4t5` arm.

**Primary comparison:** `sg-bioeye-t4t5` vs `sg-t4t5`.

**Interpretation boundary:** a null is evidence about this frozen rate-model
interface, not proof that biological T4/T5 circuitry lacks useful motion
computation. The implementation has no explicit physiological delay-line model.

### `sg-bioeye-lc-retdec`: H-RETINO-DECODER

**Intention:** replace the body-ID-ordered coordinate decoder with a
retinotopically meaningful state-change readback.

**Primary comparison:** `sg-bioeye-lc-retdec` vs `sg-bioeye-lc`.

### `sg-bioeye-lc-surprise`: H-RETINO-DECODER, fly-native predictor

**Intention:** test whether a frozen connectome advanced on the previous frame
serves as a useful one-step reference, so self-generated settling transients
cancel and input-caused deviations localize clicks.

**Primary comparison:** `sg-bioeye-lc-surprise` vs
`sg-bioeye-lc-retdec`. Also report it against `sg-bioeye-lc` as a descriptive
secondary contrast, clearly labelled as such.

For both decoder arms the endpoints were preregistered before either ran:

- **Primary:** the 19 games in which ACTION6 occurs; equivalently all games
  except `g50t`, `ls20`, `re86`, `tr87`, `tu93`, and `wa30`.
- **Secondary:** the 9 click-dominant games: `bp35`, `dc22`, `ft09`, `lp85`,
  `r11l`, `s5i5`, `su15`, `tn36`, and `vc33`.
- **Required context:** the complete 25-game result must always be displayed
  alongside the two treatment-matched endpoints.

Uncertainty remains clustered on game. Seeds are not independent biological
replicates when traces are deterministic.

---

## 4. Closure work to perform after all four bundles are complete

Do this only after the two active and two decoder arms have final bundles and
`run.end=status=ok` telemetry. If another workflow has tracked edits at that
point, stop and coordinate before writing shared files.

### 4.1 Validate every artifact before interpreting it

For each of the four conditions, record:

1. final bundle path and SHA-256;
2. checkpoint path and SHA-256;
3. telemetry file/run ID;
4. telemetry source commit and dirty flag;
5. exact argv and config path/hash captured at run start;
6. graph manifest and array hashes used by the run;
7. exactly 75 rows;
8. exactly 25 expected game IDs × seeds `{0, 1, 2}`;
9. no duplicate `(seed, game_id)` keys;
10. no exception/failure rows, illegal actions, invalid coordinates, or budget
    violations;
11. complete matching coverage against the declared baseline;
12. whether action traces are seed-diverse or byte-identical.

A checkpoint with 75 lines is not by itself a final artifact. Require the final
bundle and clean telemetry termination.

### 4.2 Compute only declared comparisons

Use the repository's paired comparison implementation and game-clustered
uncertainty. Do not substitute a row-level test. Report:

- mean score and completed levels for each condition;
- paired score delta, 95% clustered-bootstrap interval, permutation p-value,
  and nonzero-game count;
- full 25-game results for every comparison;
- the preregistered 19-game and 9-game decoder endpoints;
- behavior diagnostics needed to explain a result, clearly marked secondary.

The current `scripts/compare_conditions.py` and `scripts/league.py` do not
appear to materialize named endpoint subsets from `EXPERIMENTS.yaml`. If that is
still true after the runs finish, add the **smallest deterministic analyzer**
that:

1. reads the endpoint definitions rather than duplicating an invisible list;
2. filters both treatment and baseline to identical game IDs;
3. calls the existing paired/game-clustered statistics;
4. always emits primary, secondary, and full-set results together;
5. refuses a verdict on incomplete coverage; and
6. has tests for membership, matched coverage, and the no-partial-verdict rule.

Do not build a general analytics framework for this one need.

### 4.3 Update the durable record

After validation—not before:

1. Update hypothesis evidence/status in `EXPERIMENTS.yaml`.
2. Regenerate `LEAGUE.md` with
   `uv run python scripts/league.py --write-md LEAGUE.md`.
3. Update `WORKLOG.md` with:
   - measured final results;
   - source/config provenance and any mixed-launch limitation;
   - what each result can and cannot support;
   - the decision to defer the legacy `sg-mbdr-*` battery;
   - the exact next step: Experiment 000 refactor after handoff.
4. Never hand-edit numeric cells in generated `LEAGUE.md`.
5. Never put raw result bundles, checkpoints, telemetry, cached games, compiled
   arrays, logs, or other generated content into Git.

### 4.4 Produce one ARC closure report

Create `docs/arc_agi/ARC_CLOSURE_2026-09-23.md` after the queue is drained. It
should contain:

- the four final comparisons and endpoint results;
- the provenance table from §4.1;
- actual launch/finish order and any recovery event;
- every failed or incomplete row, if any;
- the exact claim-tier interpretation;
- a list of reusable infrastructure and ARC-specific code;
- untracked source that must not be lost;
- known bugs or mismatches that the refactor must not inherit;
- the final closure commit SHA and remote branch after checkpointing.

Use measured facts in this report. Label expectations, inferences, and project
decisions as such.

### 4.5 Verify, checkpoint, and push the closure

Run at minimum:

```bash
make test
make lint
make smoke
git status --short --ignored
git diff --cached --check
git diff --cached --stat
```

Review the staged diff and confirm no secret or generated artifact is present.
Create a small closure commit and push it to the configured private `origin`.
Do not rebase, force-push, tag, submit to Kaggle, or merge another branch as part
of closure.

The unrelated untracked `.fly-or-fake-work/` directory was present at
inspection. Do not add, delete, move, or inspect it as part of this task.

---

## 5. What the major refactor will do

The refactor will be **logical first, physical second**. We will not perform a
one-shot directory shuffle that breaks imports, invalidates old configs, and is
reverted three commits later.

### 5.1 Intended destination

The repository becomes the FlyGI umbrella with explicit experiment verticals:

```text
FlyGI/
├── README.md                         # umbrella question and evidence status
├── WORKLOG.md                        # durable current-session index; remains at root
├── EXPERIMENTS.yaml                  # existing ARC registry retained until migrated safely
├── docs/
│   ├── VISION.md
│   ├── PRIOR_ART.md
│   ├── ASSUMPTIONS.md
│   ├── HYPOTHESES.md
│   ├── DATA_PROVENANCE.md
│   └── arc_agi/ARC_CLOSURE_2026-09-23.md
├── configs/
│   ├── connectome/
│   └── experiments/
│       ├── 000_mb_sanity/
│       ├── 001_fewshot_personalization/
│       └── 002_flyarc/
├── src/flygi/
│   ├── connectome/                   # acquisition, provenance, extraction, nulls
│   ├── neuro/mb/                     # new Experiment 000 dynamics/plasticity
│   ├── evaluation/                   # experiment-agnostic statistics
│   ├── experiments/
│   │   ├── mb_sanity/
│   │   ├── personalization/
│   │   └── flyarc/
│   └── telemetry.py
├── experiments/
│   ├── 000_mb_sanity/
│   ├── 001_fewshot_personalization/
│   └── 002_flyarc/
└── tests/
```

This is the target ownership map, not an instruction for Claude to move files
now.

### 5.2 Movement map

| Current surface | Future ownership | Migration rule |
| --- | --- | --- |
| `src/flygi/connectome/{download,manifest,schema,build}.py`, `scripts/fetch_malecns.py`, `data/manifests/` | shared connectome core | reuse only after tests pin schemas, hashes, direction, and provenance |
| `src/flygi/telemetry.py`, checkpoint/resume patterns, deterministic seed/hash utilities | shared experiment infrastructure | preserve behavior; make interfaces task-neutral incrementally |
| `src/flygi/evaluation/{paired_analysis,metrics}.py` | shared evaluation | reuse after Experiment 000 defines cue-world as the independent unit |
| `src/flygi/dynamics/spmv.py` | optional compute machinery | reusable implementation detail, not inherited biological dynamics |
| `src/flygi/arc/**`, `src/flygi/controller/**` | Experiment 002 / FlyARC | preserve; move only after compatibility wrappers and frozen tests exist |
| `src/flygi/encoding/{bio_visual,retinotopic,sparse_projection}.py` and ARC coordinate decoders | Experiment 002 / FlyARC | do not present as generic biological interfaces |
| `scripts/evaluate_state_graph.py` and current ARC configs | Experiment 002 / FlyARC | freeze exact legacy behavior before relocation |
| `src/flygi/encoding/mb_bus.py` | legacy FlyARC only | do not import into Experiment 000 |
| `src/flygi/plasticity/mushroom_body.py` | legacy FlyARC model | preserve for reproducibility; do not re-export as the new MB implementation |
| raw data, compiled graphs, checkpoints, result bundles, telemetry, logs | local/external artifacts | never migrate into normal Git history; preserve hashes and manifests |

### 5.3 Refactor sequence

1. **Freeze:** close the four ARC runs, validate, document, test, commit, and
   push. Return the exact commit SHA.
2. **Reconcile:** Codex reads the closure SHA, current worktree, recent Git
   history, and any new files before proposing a diff.
3. **Add:** create the new Experiment 000 namespaces, schemas, contracts, and
   tests without moving legacy ARC modules.
4. **Prove:** implement and validate extraction, hand-check microcircuits,
   reproduce a literature oracle separately, and pass one-pulse/short-run
   kill tests.
5. **Migrate:** only after the new boundaries are stable, relocate ARC configs
   and entry points with compatibility shims and golden tests.
6. **Retire shims:** only after old commands/configs remain reproducible from
   the frozen ARC closure commit and the new entry points are verified.

The refactor branch will be created by the Codex workflow after the handoff; do
not create or pre-populate a competing refactor branch.

---

## 6. Experiment 000 boundary Claude must preserve

Claude is **not** being asked to implement Experiment 000 in the ARC workflow.
The details below explain why legacy components must remain quarantined.

### 6.1 Pinned measured source

MaleCNS `v1.0` will be pinned to the official flat-connectome files with these
locally observed SHA-256 values:

- annotations: `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`
- neurotransmitters: `95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621`
- connectivity: `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1`

These are measured local hashes, not publisher-issued checksums.

### 6.2 Exact primary populations

Selection uses exact annotation equality and requires
`superclass == "cb_intrinsic"` and `status == "Traced"`:

| Role | Predicate | Expected count |
| --- | --- | ---: |
| PN | `class == "ALPN"` | 686 |
| KC | `class == "Kenyon_Cell"` | 4,064 |
| MBON | `class == "MBON"` | 97 |
| DAN | `class == "DAN"` | 340 |
| APL | `type == "APL"` | 2 |

Use `consensus_nt`, never raw `predicted_nt`. Use all released `weight >= 1`
edges for the primary artifact and `weight >= 5` only as a preregistered
sensitivity. Edge-list orientation is `body_pre → body_post`; matrix orientation
is `W[post, pre]`, so propagation is `W @ x_pre`.

### 6.3 Primary learning substrate

- cue input enters balanced, frozen synthetic panels of direct PN→KC ALPNs;
  KCs are never stimulated directly;
- the whole bilateral circuit is retained;
- APL neurons are the measured IDs `10540` and `10977`, not an unlabeled top-k
  surrogate;
- reward uses `PAM08(y4)` with `MBON05(y4>y1y2)`;
- punishment uses `PPL101(y1ped)` with `MBON11(y1pedc>a/B)`;
- only the 6,183 existing KC→MBON edges in those two target populations are
  plastic in the primary model;
- the fixed untrained readout is the opponent MBON value, not a learned bypass;
- every cue prediction is recorded before reward is revealed and before the
  local update;
- only plastic gains persist between trials; neural activity resets.

The primary mechanism gate and topology gate are separate. If the native circuit
learns but degree-exact rewires learn equally well, the result supports a generic
mushroom-body architecture—not superiority of the exact MaleCNS topology.

Every implementation statement will be tagged as one of:

- `MEASURED_CONNECTOME`
- `LITERATURE_ESTABLISHED`
- `MODEL_ASSUMPTION`
- `ENGINEERING_CHOICE`
- `HYPOTHESIS`

Do not import an ARC calibration or heuristic into the new model without one of
those labels and an explicit validation test.

---

## 7. Assumptions, hypotheses, and measurements for this handoff

### Measurements

- `main` matched `origin/main` at `96353dd` during inspection.
- Only `.fly-or-fake-work/` appeared as unrelated untracked content before this
  coordination file was added; generated datasets/results were ignored.
- The two active checkpoints were advancing.
- The decoder waiter existed and was armed.
- No MBdr launcher existed.
- Existing raw MaleCNS artifacts match the three hashes in §6.1.
- The legacy MB rewire preserves MBON-side input degree/weight multisets but not
  KC out-degree; it is not the planned exact bipartite-degree null.

### Assumptions to verify at closure

| ID | Assumption | Required check |
| --- | --- | --- |
| C-A1 | Active processes retain their already-imported Python code. | Record launch telemetry and process lifetime; do not infer from current HEAD. |
| C-A2 | The decoder waiter launches each arm once after both prerequisites. | Inspect processes, log start, telemetry, and bundle identities. |
| C-A3 | The four configs above remain byte-identical until their run starts. | Compare telemetry config hash to the frozen table. |
| C-A4 | Each condition has 75 independent row identities even if policies are deterministic across seeds. | Validate the 25×3 key set and trace diversity. |
| C-A5 | Intervening commits do not confound declared treatment comparisons. | Perform the source-path audit described in §1. |
| C-A6 | Existing baselines remain immutable and cover the same row keys. | Hash baseline bundles and require exact matched coverage. |

### Hypotheses closed by this ARC tail

| ID | Hypothesis | Decision rule |
| --- | --- | --- |
| H-COLOUR-MAP | Which medulla type carries which categorical colour affects behavior. | Complete paired permuted-vs-declared result, interpreted with drive/support mismatch. |
| H-RETINOTOPY-COLOUR | Retinotopic categorical input helps through the tested visual readout. | Complete T4/T5 bio-eye-vs-scrambled comparison; combine with the already-complete LC arm without pooling them invisibly. |
| H-RETINO-DECODER | Retinotopic state/surprise readback turns measured localization into score. | Preregistered 19-game primary, 9-game secondary, and full-set results. |

### Hypothesis explicitly *not* closed here

`H-MB-LEARNING` remains open. Deferring `sg-mbdr-*` says only that the legacy
ARC formulation is no longer the experiment we want to spend compute on. The
incoming H000 mechanism and topology tests will replace it with stronger
extraction, dynamics, compartment, and null-model controls.

---

## 8. Ownership and communication contract

### Claude Code owns until ARC closure

- health and recovery of the two active and two already-armed decoder jobs;
- final artifact validation;
- the preregistered ARC comparisons;
- updating `EXPERIMENTS.yaml`, generated `LEAGUE.md`, and `WORKLOG.md` after
  results are complete;
- one tested ARC closure report/commit/push;
- a precise handoff message.

### Codex owns after the closure SHA is handed off

- the implementation-grade Experiment 000 biological specification;
- exact MaleCNS MB extraction and provenance contracts;
- new dynamics and plasticity equations;
- exact null algorithms and validation gates;
- the staged repository refactor;
- Experiment 001 design.

### Shared boundary

Neither workflow should silently modify a file the other owns. If a required
change crosses the boundary, stop and describe:

- file and symbol;
- intended change;
- why it is necessary;
- which live/frozen result could be affected;
- validation and rollback plan.

No broad merge, rebase, dependency change, or directory move occurs before that
coordination.

---

## 9. The exact handoff Claude should send when finished

Please report the following in one message after the closure commit is pushed:

```text
ARC QUEUE CLOSED

Final conditions:
- sg-bioeye-lc-permuted: <bundle path, sha256, 75/75, verdict>
- sg-bioeye-t4t5: <bundle path, sha256, 75/75, verdict>
- sg-bioeye-lc-retdec: <bundle path, sha256, 75/75, 19/9/25 endpoints>
- sg-bioeye-lc-surprise: <bundle path, sha256, 75/75, 19/9/25 endpoints>

Launch provenance:
- <condition>: <telemetry run id, source commit, dirty flag, config sha256>

Source-equivalence audit:
- <comparison>: <source-equivalent | comparison-matched | confounded>, because <reason>

Validation:
- tests: <command and pass count>
- lint: <result>
- smoke: <result>
- invalid/duplicate/missing rows: <counts>
- generated or secret files staged: none

Legacy MBdr:
- not launched
- registry disposition: deferred/superseded, not falsified

Reusable modules:
- <exact paths and stable interfaces>

ARC-specific modules:
- <exact paths>

Git:
- closure commit: <full SHA>
- remote branch: <branch>
- push: <confirmed>
- worktree: <clean, with any expected ignored/untracked paths listed>

Refactor release:
- SAFE TO START FROM <full SHA>
```

If any item cannot be supplied, say exactly why. “Mostly done” is not a refactor
release signal.

## Final checklist

- [ ] No verdict taken from a partial run.
- [ ] No active/armed runtime surface changed before all four bundles finished.
- [ ] No duplicate evaluator launched.
- [ ] Decoder waiter recovery path preserved.
- [ ] All four bundles contain 75 unique expected rows and clean telemetry ends.
- [ ] Full-set and preregistered decoder endpoints reported together.
- [ ] Mixed-launch source provenance audited and disclosed.
- [ ] `sg-mbdr-*` not launched and not mislabeled as falsified.
- [ ] `EXPERIMENTS.yaml`, `LEAGUE.md`, and `WORKLOG.md` agree.
- [ ] ARC closure report created from measured facts.
- [ ] Tests, lint, and smoke pass.
- [ ] No generated artifact, raw dataset, log, cache, or secret staged.
- [ ] Small closure commit pushed without history rewriting.
- [ ] Exact safe-to-refactor SHA handed to Codex.

Until every checked item above is true, the major refactor is planned but not
started.
