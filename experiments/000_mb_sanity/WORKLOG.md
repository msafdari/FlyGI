# Experiment 000 durable worklog

Read this file together with `SPEC.md` before changing Experiment 000. Record
the what, why, how, measured evidence, invalidated assumptions, and ordered next
step after every meaningful milestone. Never record secrets or generated raw
connectome data.

## Operating rule

Measure twice, cut once. A source implementation begins only after its contract
and analytic failure tests are explicit. A failed hypothesis is retained as a
result; a failed implementation is repaired before interpretation. No
behavioral result may be used to tune a supposedly outcome-blind extraction,
calibration, null, or statistical choice.

The project-wide thesis remains non-negotiable:

> The computation has to go through the fly's measured circuit, or it does not
> count as a FlyGI result.

## Checkpoint — 2026-09-23 15:10 PDT

### What changed

Created the isolated branch `codex/experiment-000` from `39bdd6b`, the latest
pushed FlyARC main commit at branch creation. This separate clone/worktree is
under `/private/tmp/flygi-exp000-codex`; the live FlyARC checkout and its
processes were not edited, staged, restarted, or stopped.

Converted the planning draft into an implementation-grade biological
specification after three independent read-only audits:

- equation/state-machine and deterministic-generation audit;
- topology-null/statistical-inference audit;
- current-repository migration/reuse audit;
- followed by a final contradiction and primary-source audit.

### Decisions frozen

- Exact MaleCNS predicates use `class`/`type` equality. Compartment suffixes
  such as `PAM08(y4)` are biological display prose, not table selectors.
- Extraction retains 686 ALPNs for provenance, a 314-body direct PN interface,
  and 294 cue-eligible bodies spanning 74 bilateral cholinergic types.
- Runtime state is a new float64 314-PN / 4,064-KC / 2-APL model; it does not
  reuse the transformed, signed, normalized float32 ARC graph runtime.
- APL feedback is explicit; top-k is an ablation. The 5% KC target is labeled a
  model assumption, not a measured universal set point.
- Value is a fixed MBON11-minus-MBON05 readout. Literature supports broad
  opposite valence biases, but the two-type scalar is explicitly assumed.
- Plasticity touches only 6,183 existing KC→MBON05/11 edges. The proposed rule
  is reinforcement-gated local plasticity, not RPE: it has no predicted-reward
  term or MBON→DAN feedback.
- Missing feedback and DAN-off skip updates. Numeric `r=0` executes recovery;
  `D=0` with an update is named `recovery-only`.
- Every trial records separate pre-reward A/B probes. Reward is revealed only
  after both; only plastic gains persist.
- The independent unit is one cue world. Trials, tasks, mirrored orientations,
  graph-null draws, and software seeds never inflate `n` beyond 128.
- `H000-MECH` uses three nonredundant primary controls: frozen gains,
  within-phase reward-time shuffle, and graph-off. DAN-off and full-mask/readout
  lesions are required diagnostics but mathematically redundant for inference.
- `H000-TOPO` uses 39 whole-bilateral, anatomically stratified, degree-exact
  Curveball joint rewires of PN→KC and the complete 61,210-edge KC→97-MBON
  layer. The four result-bearing MBONs are never rewired in isolation.
- Confirmatory inference and replication thresholds are frozen before code.

## Pause checkpoint — 2026-09-23 15:17 PDT

Work paused at the user's request before any Experiment 000 source code or run
was started. This checkpoint is intentionally documentation-only and safe to
push as a draft branch.

Since the 15:10 checkpoint, the specification was tightened in response to the
final contradiction/source audit:

- pinned the three raw artifact byte counts, total row counts, Arrow schemas,
  and the distinction between R1's 166,691 paper count and the pinned
  annotation file's measured 211,577 total / 166,700 classified rows;
- split noisy reward and sparse feedback into separate 256-event 000D subarms
  instead of confounding noise with missingness;
- specified pairwise pre-reward A/B probing and equal task/orientation/world
  reductions;
- replaced fixture confidence intervals with exact oracle/zero/inverted
  evaluator assertions;
- narrowed H000-TOPO to weighted PN→KC plus KC→all-MBON wiring because APL is
  held fixed;
- declared the runtime block whitelist and every omitted measured block,
  including APL→APL;
- made threshold/APL-gain calibration algorithmic and bounded rather than an
  exhaustive or underspecified search;
- added primary-source links and downgraded unsupported biological wording.

The following specification audit items remain before M000-0 can be called
frozen:

- define recovery-only as a post-conditioning extinction sensitivity beginning
  from depressed gains, or remove it;
- make Curveball attempted-trades-per-sweep/rejection telemetry and fresh
  replication-null generation fully explicit;
- finish the scalar/omitted-block parameter ledger and add the remaining
  pre-run golden-test contracts (mirror coupling, reward-shuffle preservation,
  reductions, inference fixtures, and replication namespaces);
- rerun a clean contradiction audit over the whole assembled document.

No uncommitted implementation is being abandoned. Resume from this section,
then inspect the branch diff and current FlyARC main before changing anything.

### Assumptions corrected or invalidated

| Prior assumption | Evidence | Resolution |
| --- | --- | --- |
| MaleCNS `type` contains compartment-decorated names | Exact pinned-table scan returns only `PAM08`, `PPL101`, `MBON05`, `MBON11` | invalidated; exact short types plus separate reviewed compartment registry |
| DAN-off can be implemented by setting `D=0` | The declared equation then recovers depressed active gains toward 1 | invalidated; DAN-off skips update, `D=0` update is recovery-only |
| Existing ARC MB/runtime code can be generalized safely | It has heuristic selectors, transformed float32 weights, incomplete metadata, non-degree-exact MB nulls, and ARC-specific config/result semantics | invalidated; additive Experiment 000 implementation with narrow shared utilities |
| Four mechanism controls can all be independent | DAN-off equals frozen from pristine gains; full selected-mask/readout lesion collapses to graph-off | invalidated; three nonredundant primary contrasts, redundant arms retained as kill tests |
| Five-percent KC activity is a measured biological constant | APL literature establishes sparsening/decorrelation, not a universal numeric set point | downgraded to `MODEL_ASSUMPTION` |
| The declared gain update is RPE-like | It contains neither prediction error nor MBON→DAN feedback and is not Bennett et al.'s rule | invalidated wording; call it reinforcement-gated local plasticity |

## Hypothesis ledger

| ID | Claim | Status | Pass condition | Failure interpretation |
| --- | --- | --- | --- | --- |
| H000-MECH | Declared circuit + local plasticity learns cue value | `PREREGISTERED / NOT RUN` | all three primary paired effects ≥0.10, lower one-sided 95% bounds >0, and p≤0.05 | stop before topology; mechanism/evaluator/model is insufficient |
| H000-TOPO | Native exact topology beats conservative rewires | `BLOCKED ON H000-MECH` | rank p≤0.05, mean effect ≥0.05, lower bound >0 | mechanism may work, but exact MaleCNS wiring earns no superiority claim |

## Milestone and experiment ledger

| ID | Work item | State | Evidence required before promotion |
| --- | --- | --- | --- |
| M000-0 | Freeze specification | `PAUSED / DRAFT` | contradiction audit clean; source labels/links checked; no undefined primary endpoint |
| M000-1 | ARC compatibility goldens | `NOT STARTED` | public imports, CLI, representative config snapshots, v1 result adapters, resume behavior pinned |
| M000-2 | Raw MB extractor + manifest | `NOT STARTED` | source hashes/schema, exact predicates/counts/direction, deterministic round trip |
| M000-3 | Dynamics + fixed readout | `NOT STARTED` | analytic `.8` fixed-point microcircuit, convergence/failure/reset tests |
| M000-4 | Plasticity + trial runner | `NOT STARTED` | one-pulse direction, half-life, missing/zero/DAN semantics, pre-reward causality |
| M000-5 | Mechanism controls + 16-world pilot | `NOT STARTED` | ideal oracle and negative harness gates; no parameter tuning from pilot |
| M000-6 | Locked 128-world mechanism run | `BLOCKED` | M000-0 through M000-5 complete and artifact hashes frozen |
| M000-7 | Structural null pilot + 39 nulls | `BLOCKED` | H000-MECH passed; registry signed off; switchability/mixing gates pass |
| M000-8 | Fresh replication | `BLOCKED` | Gates 0–3 pass with unchanged code/config |

## Reuse boundary measured against current repository

Reusable unchanged: deterministic seed derivation, telemetry, MaleCNS
download/schema utilities, `NodeIndex`, raw `W[post,pre]` construction, exact
group filtering, and generic provenance primitives.

New implementation required: extracted-circuit manifest, nested experiment
config loader, float64 MB dynamics, plastic state/trial runner, degree-exact
stratified nulls, cue-world inference, and umbrella-ledger adapter.

FlyARC quarantine: current ARC config/runtime/dynamics, controller, encoder,
decoder, MB bus/plasticity, results, league adapter, and root configs remain
Experiment 002 compatibility surfaces. They are not imported into Experiment
000.

## Open blind gates

- [ ] Recompute raw PN→KC support and explain 22,586/3,812 exact-selection
      result versus legacy 22,581/3,811 record.
- [ ] Review bilateral PAM08/MBON05 and PPL101/MBON11 morphology/overlap.
- [ ] Review the proposed 37-type MBON input-family registry against official
      morphology documentation.
- [ ] Measure ≥80% switchability in both primary blocks and calibrate Curveball
      burn-in from structural diagnostics only.
- [ ] Pass analytic kill tests and the outcome-blind 16-world harness pilot.

## Ordered next work

1. Resume the four explicitly listed specification-audit items in the 15:17
   pause checkpoint; rerun the contradiction audit.
2. Close M000-0 in a second documentation checkpoint only after that audit is
   clean.
3. Reconcile this branch with the eventual FlyARC closure commit without
   changing Experiment 002 behavior.
4. Add the five minimal ARC compatibility goldens before moving or sharing any
   legacy surface.
5. Implement only M000-2: raw pinned tables → deterministic extracted-circuit
   manifest. Do not add dynamics in the same checkpoint.
6. Run and record the first blind extraction gates; update this ledger before
   beginning M000-3.
