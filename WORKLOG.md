# FlyGI worklog

This file records durable checkpoints, measured results, limitations, and the
next implementation steps. Large upstream and generated artifacts remain local
and are not stored in normal Git history.

## 2026-09-19 — Milestones 0–1 and full-data checkpoint

### Completed

- Created the Python 3.12 repository, locked its dependencies, and implemented
  the Milestones 0–1 package, CLI, configs, documentation, tests, and Kaggle
  adapter plumbing.
- Added a root `AGENTS.md` operating directive requiring worklog-first recovery,
  frequent small verified commits, periodic pushes to the private remote, and
  strict exclusion of downloaded/generated artifacts from normal Git history.
- Pinned the official ARC-AGI-3 agent framework at
  `4743e7d0aaae0ded0d98a89a7e282e63564cd58b` and the starter interface at
  `eeb1535404f321d280a8f9194bbc1d7aca5f05fc`.
- Downloaded all three required MaleCNS v1.0 Feather tables: 1,109,008,094
  bytes in total. No individual-synapse tables, skeletons, meshes, segmentation
  volumes, or EM imagery were downloaded.
- Compiled the literal-rate graph with strict source schemas, ascending 64-bit
  body IDs, `W[post, pre]` edge orientation, `log1p` weights, unsigned edges,
  incoming-L1 normalization, no self-edges, and the declared nonempty
  `superclass` node filter.
- Refreshed the locked ARC dependencies and cached all 25 currently public game
  packages for strict-offline use.
- Configured the Kaggle notebook owner as `megusalexandrus`, created a dedicated
  `FlyGI local CLI` API token, and stored it only in the ignored local
  `.kaggle/access_token` file with mode `600`. The secret value is not recorded
  in this worklog or Git history.
- The user reported completing competition enrollment and identity
  verification. Independently, the authenticated submissions endpoint now
  succeeds and reports `No submissions found` instead of HTTP 403.
- Published the repository privately at <https://github.com/msafdari/FlyGI>.

### Verification results

- `uv run pytest`: 25 tests passed.
- Ruff lint and formatting checks passed.
- Wheel build and generated-notebook schema validation passed.
- `flygi validate all --require-data` passed and rehashed all three sources and
  all three runtime assets.
- The official-style 50-action `ls20,vc33` local verification passed offline.
- Every cached public game imported, initialized, reset, and accepted at least
  one legal action in strict-offline mode.
- A public-set random-baseline run completed in all 25 games without an
  exception. The requested 200-action ceiling was reduced by the adapter's
  existing `MAX_ACTIONS=80` setting, and it completed one level in `sp80`.
  A later scorecard probe found that the pinned upstream loop uses `<=` and
  therefore permits 81 actions at that setting; the earlier 2,000-action total
  was an invalid estimate and no exact per-game artifact was preserved. This is
  a smoke result, not evidence about connectome performance.

### Measured MaleCNS build

| Measurement | Observed value |
| --- | ---: |
| Source directed edge rows | 151,856,684 |
| Source synaptic-contact weight sum | 311,833,243 |
| Annotated neurons | 211,577 |
| Retained neurons | 166,700 |
| Runtime nonzero directed edges | 25,582,837 |
| Retained synaptic-contact weight sum | 124,177,143 |
| Descending-neuron group | 1,314 |
| Disconnected retained nodes | 217 |
| Dropped rows with missing annotations | 125,828,298 |
| Dropped rows due to node filtering | 445,448 |
| Dropped retained self-edges | 101 |

The build took approximately 14 minutes on the development machine and peaked
at roughly 3.6 GB observed resident memory. The compressed runtime is about
101 MB in total; `graph.npz` itself is 90,033,466 bytes.

### Recorded hashes

The source digests below were observed during download and reverified locally.
The publisher did not provide an independent expected SHA-256, so they must not
be described as publisher-preverified.

| Artifact | SHA-256 |
| --- | --- |
| Source weights | `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1` |
| Source annotations | `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2` |
| Source neurotransmitters | `95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621` |
| Runtime graph | `99c9441be6e6ac89eb20c3c17162308240f2e4326003d97a4e5034e998be8acc` |
| Runtime node metadata | `2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c` |
| Runtime groups | `09736379ce989268080f57b64f357e800cf446972007c1af2287a86b9985a89d` |

### Findings and decisions

- The aggregate weights table contains 151.9 million rows, but only 25.6
  million nonzero edges remain after restricting both endpoints to the curated
  retained neuron population and removing self-edges.
- Missing annotation endpoints account for most dropped source rows. This is a
  measured property of the selected source tables and filter, not a schema
  failure.
- The complete graph can be compiled without a dense adjacency matrix on the
  development machine. Sparse aggregation, rather than final asset size, is
  the expensive phase.
- Four ARC game downloads (`re86`, `s5i5`, `sb26`, and `sc25`) failed during
  the first pass and all succeeded on an immediate targeted retry. All 25 then
  passed strict-offline loading and action smoke tests.
- The current adapter is intentionally a deterministic random-legal baseline.
  It does not load the compiled graph, so its public-game result cannot be
  interpreted as a FlyGI/connectome result.
- The generated Milestone 0 notebook embeds FlyGI Python code but explicitly
  reports `contains_connectome_assets: false`. A hidden Kaggle evaluation is
  therefore not yet a connectome evaluation.
- The user reports that competition enrollment and identity verification are
  complete. Independently observed read-only CLI requests can list both the
  competition files and the account's submissions, confirming that the prior
  access blocker is cleared. Uploading/executing the private random-agent
  notebook and making any leaderboard submission remain separate external
  actions.

### Local artifacts intentionally excluded from Git

| Path | Approximate size | Reason |
| --- | ---: | --- |
| `data/raw/` | 1.0 GB | Upstream MaleCNS tables |
| `data/processed/` | 101 MB | Reproducible compiled runtime |
| `environment_files/` | 3.9 MB | Downloaded public ARC game packages |
| `.venv/` | 389 MB | Reproducible virtual environment |
| `vendor/` | 1.2 MB | Reproducible pinned framework checkout |
| `notebooks/submission.ipynb` | generated | Rebuilt from tracked source |

The small acquisition manifest under `data/manifests/` is tracked because it
contains provenance rather than the downloaded tables themselves.

## 2026-09-19 — Private Kaggle notebook smoke

### Completed

- After explicit user authorization to export and execute the repository code,
  ran `UV_CACHE_DIR=/tmp/flygi-uv-cache make submit`. Kaggle created private
  kernel version 1 at
  <https://www.kaggle.com/code/megusalexandrus/flygi-arc-agi-3> and reported
  `KernelWorkerStatus.COMPLETE`.
- Downloaded the completed run's output and log to a temporary directory for
  inspection. Neither file was added to the repository.
- Removed the optional `arc-agi-3` and `connectome` notebook keywords from the
  tracked metadata after Kaggle reported that they were not valid tags. Their
  rejection did not prevent the kernel from running.

### Verification results

- The uploaded generated notebook was 58,530 bytes with SHA-256
  `0464b7792238f4d4bc95e0b9fad8af09c44d3cbb70460fd86bb16a337c12453c`.
  It embedded the adapter and 40 Python source files, contained no credentials
  or local home paths, and declared `contains_connectome_assets: false`.
- The ordinary private run produced the expected 2,648-byte dummy
  `submission.parquet` with SHA-256
  `71bfd543030e339d87bd9ff744d466218398a1259650b2c255626d27049c88bb`.
  It contained one row with columns `row_id`, `game_id`, `end_of_game`, and
  `score`; this validates artifact production, not agent performance.
- The 9,805-byte run log had SHA-256
  `8955a9f589a42590b34c0f9f081b5c34575cc50918201d499514c3633cf9d03f`.
  It contained no Python traceback. Kaggle installed `arc-agi==0.9.8`,
  `arcengine==0.9.3`, and `pillow==12.2.0` from the competition wheels.

### Findings and limitations

- A normal Kaggle kernel execution does not set
  `KAGGLE_IS_COMPETITION_RERUN`, so it exercises notebook setup and writes the
  declared dummy artifact without contacting the hidden game gateway. An
  official competition submission is still required for a hidden evaluation
  and needs separate explicit authorization because it spends submission quota.
- The run log reported pre-existing Kaggle image dependency conflicts:
  `dopamine-rl` expects `gym<=0.25.2`, and `gradio` expects `pillow<12.0`.
  Neither package is used by FlyGI's submission path, and the kernel completed,
  but these warnings should be rechecked after future competition-wheel updates.
- This kernel contains the deterministic random-legal baseline and no compiled
  graph assets. Even an official rerun of this version would be a pipeline and
  random-baseline measurement, not a connectome-driven FlyGI evaluation.
- The user decided to defer any official competition submission until local
  baseline and engineering gates pass. No leaderboard submission has been made.
- The Kaggle image installed `arc-agi==0.9.8`, while the current local lock
  resolves `arc-agi==0.9.9`. Local results must record this parity difference,
  and the submission package must be rechecked against the competition wheel.

## 2026-09-20 — Local pre-submission gates and evaluator

### Completed

- Adopted an explicit no-submission policy until the local engineering gates in
  `docs/local_acceptance_gates.md` pass. The random notebook remains a packaging
  smoke and will not be submitted as though it were a FlyGI baseline.
- Added `scripts/evaluate_random_baseline.py` and `make baseline-local`. The
  evaluator runs only cached, exact-version public games in strict-offline mode,
  uses five explicit evaluation seeds by default, and enforces an exact
  80-environment-action ceiling independently of the upstream off-by-one loop.
- The evaluator writes a new immutable JSON artifact under the ignored
  `results/random_baseline/` tree and refuses to overwrite an existing result.
  It preserves full action/payload traces, frame hashes, official local
  scorecards, seeds, failures, dependency and Git provenance, source hashes,
  timing, memory, legal-action checks, coordinate checks, and summaries.
- Added an automatic deterministic replay of cached game `lf52` (or the first
  selected game if `lf52` is absent). Replay comparison excludes timing noise
  but includes action payloads, states, levels, legal masks, and observation
  hashes.

### Verification results

- `uv run pytest`: 29 tests passed, including four new evaluator tests.
- Ruff lint and formatting checks passed for all 78 checked files.
- A real strict-offline 2-game by 2-seed smoke matrix (`lf52`, `sp80`; 12
  actions each) produced 4/4 successful rows, 48/48 completed actions, zero
  illegal actions, zero invalid `ACTION6` coordinates, zero budget violations,
  and a matching `lf52` deterministic replay. This temporary smoke artifact is
  not a public-set baseline result.

### Gate 0 full public result

- Ran `make baseline-local` from clean commit
  `0c619e81d919600193f3ac15715fa01bc6f3aae5`. The exact-version matrix covered
  all 25 cached public games, seeds `0..4`, and an exact 80-action ceiling: 125
  rows and 10,000 actions.
- Gate 0 passed: 125/125 rows succeeded with zero exceptions, illegal actions,
  invalid `ACTION6` coordinates, or budget violations. The seeded `lf52` replay
  matched exactly with trace SHA-256
  `10dd5c7c10005434e59a5cd03e5523e2509f970ec8dd54608c94b403ac20392e`.
- The ignored full artifact is
  `results/random_baseline/20260920T223612.620834Z-8ebd0f45f4.json`: 8,029,063
  bytes, SHA-256
  `05af1d81f7132d268cf50e075c15981459cf8e4c9eb5c65a86c5d6461b57dba2`.
  A small reviewed summary is tracked at
  `results/manifests/random_baseline_gate0_20260920.json`.

| Chance-control measurement | Observed value |
| --- | ---: |
| Mean official-style public score over 125 rows | 0.0506261 |
| Median score | 0 |
| Maximum row score | 4.7619048 |
| Rows with any level progress | 2 / 125 (1.6%) |
| Levels completed | 2 / 915 available game-seed levels (0.219%) |
| Fully completed games | 0 |
| Resets | 54 |
| Median policy time | 0.0154 ms/action |
| p95 policy time | 0.0243 ms/action |
| Median environment-step time | 0.360 ms/action |
| p95 environment-step time | 1.570 ms/action |
| Peak process RSS | 173,522,944 bytes |

Both nonzero rows were `sp80`: seed 1 completed one level with score 1.56636,
and seed 2 completed one level with score 4.76190. The other 123 rows scored
zero. These descriptive chance numbers are not independent Bernoulli trials and
must not be interpreted as a general game-solving probability or a connectome
result.

### Provisional full-graph feasibility measurement

On the development Apple M4 machine with 16 GB memory, loading the compiled
166,700-node, 25,582,837-edge graph took 0.736 seconds. The uncompressed SciPy
CSR arrays occupied 205,329,500 bytes, and the process peak RSS reported during
the probe was 345,423,872 bytes.

After one warmup update, eight exploratory timings of the simple float32 update
`h <- tanh(0.7 h + 0.3 W h)` produced:

| Internal steps per action | Median ms | p95 ms | Derived actions/s |
| ---: | ---: | ---: | ---: |
| 1 | 35.34 | 37.13 | 28.30 |
| 2 | 70.79 | 71.43 | 14.13 |
| 4 | 141.50 | 142.18 | 7.07 |
| 8 | 282.84 | 303.58 | 3.54 |

These were back-of-the-envelope sparse-update timings, not a Milestone 2
benchmark: at the time, the dynamics backend, sensory input, state contract,
10,000-step finite-activity test, and controlled benchmark protocol did not yet
exist. At the observed medians, graph updates alone would take approximately
71, 142, 283, or 566 seconds for one 25-game seed at 80 actions for
`K=1,2,4,8`.

### Milestone 2 implementation checkpoint

- Implemented the exact declared float32 rate equation
  `h_next = (1 - leak) h + leak tanh(gain W h + drive + bias)` behind a pure
  SciPy/CPU sparse interface. `step` is exactly one internal update; `advance`
  holds a graph-aligned drive fixed for `K` updates and returns a new state.
- Promoted the dynamics YAML into strict typed configuration. The literal
  baseline now explicitly declares the rate model, SciPy CSR CPU execution,
  tanh activation, `K=2`, leak `0.3`, gain `0.9`, scalar zero bias, zero
  initialization, float32 state, and a frozen graph.
- Added one-time runtime-bundle loading that verifies output hashes and manifest
  graph semantics, cross-checks node/edge counts, validates required sorted
  groups, and freezes the CSR and group arrays. Serialized graph/group loaders
  now reject unexpected dtypes instead of silently casting them.
- Replaced the benchmark placeholder with an immutable Gate 1 runner. It
  selects a deterministic real edge entering the descending-neuron group,
  checks an actual graph-mediated response, exact CPU repeatability, finite and
  bounded activity, and warmed `K=1,2,4,8` timings without imposing a
  machine-dependent speed threshold. A pass is pinned to the exact literal
  runtime release, 166,700 nodes, 25,582,837 edges, three runtime digests, and
  config-matched preprocessing; it also requires at least three warmups and 25
  measured actions per `K` and records an RSS snapshot after each `K`.
- Added fast unit coverage for the exact equation, directionality, `step` versus
  `advance`, caller immutability, same-seed determinism, a 10,000-step tiny-graph
  stability case, descending-neuron sensitivity, runtime asset tampering, and
  benchmark protocol helpers.

Verification before the source checkpoint:

- `uv run pytest`: 93 tests passed.
- Ruff lint and formatting checks passed for all 82 checked files.
- `flygi validate all --require-data` reverified all six source/runtime files,
  then ran a finite, exact-repeat full-graph CPU update with shape `(166700,)`
  and dtype float32.
- An intentionally abbreviated real-graph integration smoke loaded and verified
  166,700 nodes, 25,582,837 edges, and 1,314 descending neurons in 0.905 seconds
  at 332 MiB peak RSS. The graph-mediated probe selected body 70869 feeding
  descending body 55579 and produced opposite nonzero target activity after two
  internal steps. Its formal gate status was correctly `failed` because the
  development tree was dirty, stability was shortened to 10 steps, and only
  `K=1,2` were timed. That smoke is not a Gate 1 result.

### Gate 1 full-graph dynamics result

- Ran `make benchmark-full-graph` from clean commit
  `9ec7930ab66bf14a55b449cdda70192810b98da1`. The runner verified the
  exact literal-runtime release, node/edge counts, preprocessing contract, and
  all three pinned runtime hashes before exercising the graph.
- Gate 1 passed with no issues. One full rate update returned a finite float32
  state of shape `(166700,)`. Repeating the configured `K=2` update from the
  same state and drive matched bit-for-bit at SHA-256
  `7f32ec1beb739556605fea18b42e8a0072a1d1a00a1af2cbd98180a2a260e8d4`.
- The deterministic graph-mediated probe injected body 70869, which is not a
  descending neuron, through a real edge of weight `0.06378546` into descending
  body 55579. Opposite inputs produced opposite nonzero selected-target
  activity (`+/-0.00126539`), different full states, and different DN vectors.
- All 10,000 full-graph internal steps were finite and within the declared
  float32 bound. The maximum observed absolute activity was `0.24695361`; the
  final saturation fraction at `|h| >= 0.99` was zero. The stability phase took
  353.585 seconds.
- Verified process-cold loading took 0.886 seconds. Peak process RSS was
  348,536,832 bytes (332.4 MiB); the process-wide high-water RSS sampled after
  every `K` remained the same.
- The ignored full artifact is
  `results/dynamics/20260921T040425.078313Z-gate1.json`: 11,772 bytes,
  SHA-256
  `048e277cd8b71d623fab7f35333d5239f6e8eec98df8f95a1b2a054740b5d161`.
  Its reviewed summary is tracked at
  `results/manifests/dynamics_gate1_20260921.json`.

| Internal steps per action | Median ms | p95 ms | Actions/s | Projected 125-row graph time |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 35.080 | 35.329 | 28.51 | 350.8 s |
| 2 | 70.171 | 71.145 | 14.25 | 701.7 s |
| 4 | 140.302 | 141.185 | 7.13 | 1,403.0 s |
| 8 | 285.704 | 322.078 | 3.50 | 2,857.0 s |

`K=2` remains the declared local-development default. Its graph-only projection
for the future 125-row public agent gate is about 11.7 minutes on this Apple M4.
This is not a final deployment choice: timing and memory must be remeasured on
the actual Kaggle runtime before submission.

## 2026-09-21 — Dynamical-regime diagnostic of the declared operating point

### Why this was run

Gate 1 established that the full graph runs, is deterministic, stays finite,
and that a single injected edge can move a descending neuron. It did not
establish that the *declared operating point* can carry ARC frame information
from a sensory population to the readout population within a decision, nor that
the real graph is dynamically distinguishable from a null. Those are
preconditions for Milestone 3 being worth building, because Milestone 3 freezes
`K`, `leak`, `gain`, `sign_mode`, and the readout population into the agent.

### Completed

- Added `scripts/probe_dynamics_regime.py` and `make probe-regime`. It is a
  measurement, not an acceptance gate, and records `is_acceptance_gate: false`.
- Added eight fast offline tests, including one that asserts the probe's
  optional null does **not** preserve out-degree, so it cannot be mistaken for
  the preregistered control.
- Ran the probe from clean commit `a68205923eb2d269ac48f1316cc89ac999c33042`
  against the pinned literal runtime at the declared `K=2`, `leak=0.3`,
  `gain=0.9` operating point, injecting the 6,098-neuron `ol_sensory`
  superclass and reading the 1,314-neuron descending-neuron group.

### Verification results

- `uv run pytest`: 101 tests passed (93 before, plus eight new probe tests).
- Ruff lint and formatting checks passed for all 84 checked files.
- The probe verified all three pinned runtime output hashes before measuring.

### Measured results

The ignored full artifact is
`results/diagnostics/20260921T065851.628556Z-regime.json`: 17,790 bytes,
SHA-256 `dede33ca6da0ced54b6b17b55dd506bfbfebcfd9003ae5d46ff63742bbd89e94`.
Its reviewed index is tracked at
`results/manifests/dynamics_regime_20260921.json`. Cold load took 0.848 s; the
probe's peak process RSS was 1,060,765,696 bytes, which is higher than Gate 1's
348 MB because the probe additionally materializes a transpose and a null copy.
That figure describes the probe, not the deployment path.

**Finding 1 — the declared `K=2` is smaller than the anatomy requires.**
Breadth-first search along directed edges from `ol_sensory` reaches 3 of 1,314
descending neurons at one hop, 688 at two hops, and all 1,314 at three hops.
Driving all photoreceptors with a constant unit input moves zero descending
neurons after one internal step, 3 after two, 688 after three, and all 1,314
after four. With `internal_steps: 2` the descending readout is therefore
effectively blind on the first decision of an episode and reads a roughly
two-turn-stale frame thereafter. 2,879 retained nodes are not reachable from
the visual sensory population at all.

**Finding 2 — cross-action memory is set by the leak term, not by the graph.**
After driving two distinct input patterns for 8 actions and then removing all
drive, the normalized state difference decays as follows, per external action:

| Silent actions | Real graph | Weak null |
| ---: | ---: | ---: |
| 1 | 0.5386 | 0.5026 |
| 2 | 0.3101 | 0.2568 |
| 4 | 0.1227 | 0.0705 |
| 8 | 0.0312 | 0.0105 |
| 12 | 0.0115 | 0.0068 |

The half-life is 2 actions in both conditions. The observed `rho(W) = 1.000254`
implies a 33-step time constant, but that applies only to the uniform Perron
mode; the informative modes decay far faster. Under `sign_mode: unsigned` with
`normalization: incoming_l1` every row sums to 1 by construction, so the matrix
is exactly row-stochastic and its spectral radius is pinned near 1 for any
topology — the weak null observes `rho = 0.997754`. A dynamical property that
is identical by construction across conditions cannot discriminate them.

**Finding 3 — the real graph and the null differ sharply, but not in memory.**

| Measurement | Real | Weak null |
| --- | ---: | ---: |
| Hops to reach all 1,314 DNs | 3 | 2 |
| DNs reached at hop 1 | 3 | 1,305 |
| Nodes unreachable from sensory | 2,879 | 302 |
| Mean absolute DN activity (settled) | 5.83e-06 | 3.70e-03 |
| Readout participation ratio (32 inputs) | 5.53 | 28.95 |
| Top-1 variance fraction of DN code | 0.3048 | 0.0506 |
| Cross-action memory half-life | 2 actions | 2 actions |

The rewiring short-circuits the fly's layered visual pathway: 1,305 of 1,314
descending neurons become directly postsynaptic to photoreceptors. The real
graph's descending code is about 630 times weaker in absolute magnitude and
about five times lower-dimensional. These are large, reproducible structural
differences. They are *not* evidence of a biological advantage, because the
weak null is not the preregistered control and because no ARC outcome has been
measured.

### Findings and decisions

- A decoder reading raw descending activity must standardize it. Settled mean
  absolute DN activity is 5.83e-06 against a network-wide mean of order 1e-2.
  The values are comfortably representable in float32, but an unnormalized
  linear readout would be dominated by its bias.
- The effective descending-neuron code is roughly 5.5-dimensional under real
  anatomy. That is a real constraint on the Milestone 3 decoder, which must
  drive up to eight discrete actions plus two coordinate heads.
- `K` must be at least 4 on anatomical grounds. The Gate 1 timing table puts
  `K=4` at 140.3 ms per action on this machine, against 70.2 ms at `K=2`. The
  compute cost is real but is not obviously prohibitive; Kaggle-runtime timing
  is still required before any deployment choice.
- The unsigned/incoming-L1 combination should not remain the only compiled
  condition. Building the `sign_mode: heuristic` runtime is the next step.
- Correction to an earlier informal estimate made during review: a first pass
  that injected 2,000 *randomly chosen* nodes rather than the annotated visual
  population found the real and null graphs to be nearly indistinguishable.
  With the anatomically declared `ol_sensory` injection they are strongly
  distinguishable on pathway depth, readout magnitude, and dimensionality. The
  claim that survives both passes is the narrower one: *cross-action memory* is
  leak-dominated and near-identical across conditions.

### Limitations

- The probe's null is a within-row presynaptic shuffle. It preserves each
  postsynaptic node's in-degree and its exact per-row weight multiset, and
  destroys out-degree and all higher-order structure. It is strictly weaker
  than the preregistered directed degree-preserving rewire, and no real-versus-
  null conclusion in this entry may be carried into a confirmatory claim.
- One null seed was measured. The preregistered analysis requires at least ten
  independently seeded nulls.
- Sensory injection used i.i.d. random patterns over photoreceptors, not ARC
  frames. No encoder exists yet, so these numbers bound the interface rather
  than describe it.
- No ARC game was played and no score was produced.

## 2026-09-21 — Signed runtime condition compiled and measured

### Completed

- Surfaced `graph.unknown_transmitter_treatment` as a declared, validated config
  field. It was previously reachable only as a `BuildOptions` default, and
  because unknown config keys are rejected, omitting it from the YAML meant the
  choice was being made silently. Both transmitter treatments are now written
  explicitly in every checked-in config and fail closed on an unsupported value.
- Added `configs/literal_rate_signed.yaml`. It differs from
  `configs/literal_rate.yaml` in exactly two fields, `sign_mode` and
  `output_dir`; a test asserts that every other build choice is identical.
- Compiled the signed runtime with `flygi graph build --config
  configs/literal_rate_signed.yaml` from clean commit
  `50a2dc4b8e0855c34476ec847dc71a47bc8a1985`. The build took about 14 minutes
  and peaked at roughly 4.3 GB observed resident memory.
- Ran `flygi validate all --require-data --config configs/literal_rate_signed.yaml`
  (exit 0) and `make probe-regime REGIME_CONFIG=configs/literal_rate_signed.yaml`.

### Verification results

- `uv run pytest`: 106 tests passed (101 before, plus five new config tests).
- Ruff lint and formatting checks passed for all 84 checked files.
- `validate all --require-data` reverified the three sources and the three
  signed runtime outputs.

### Measured signed build

| Measurement | Unsigned | Signed |
| --- | ---: | ---: |
| Retained neurons | 166,700 | 166,700 |
| Runtime nonzero directed edges | 25,582,837 | 24,559,055 |
| Edges zeroed by sign or normalization | 0 | 1,023,782 |
| Negative weight fraction | 0.0000 | 0.3996 |
| Descending-neuron group | 1,314 | 1,314 |

The 1,023,782 deleted edges (4.00% of the unsigned graph) are exactly the
outgoing edges of the 541 modulatory and 3,177 unknown-transmitter presynaptic
neurons, which `modulator_treatment: zero` and
`unknown_transmitter_treatment: zero` assign sign 0. The two runtimes are
therefore **not** edge-count-matched, and the signed condition requires null
graphs generated from the signed graph itself.

`node_metadata.npz` and `groups.npz` are byte-identical between the two
runtimes (SHA-256 `2a84309b...` and `09736379...`). The node set, node order,
and descending-neuron group membership are therefore provably shared, which is
what the specification's fairness constraint requires of the sensory and readout
identities across graph variants.

| Signed runtime artifact | SHA-256 |
| --- | --- |
| `graph.npz` | `45e332d90ea4e881ece5d4d72216955bd53eec922aa60955a69db510272eff61` |
| `node_metadata.npz` | `2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c` |
| `groups.npz` | `09736379ce989268080f57b64f357e800cf446972007c1af2287a86b9985a89d` |
| `manifest.json` | `6223e065029b2699d2e21e079ca7a6a8349672785230a0ba3f4ecf83eacd27f4` |

### Measured signed regime

The ignored full artifact is
`results/diagnostics/20260921T071754.435672Z-regime.json`: 17,904 bytes,
SHA-256 `19a52aa679d36afdbf52421f721c113484655197d7c8fb0c627a1ddc46da2426`.
Its reviewed index is tracked at
`results/manifests/signed_runtime_regime_20260921.json`.

**Signing makes the real graph far more distinguishable from a null.** At the
same declared `K=2`, `leak=0.3`, `gain=0.9` operating point:

| Measurement | Unsigned real | Unsigned weak null | Signed real | Signed weak null |
| --- | ---: | ---: | ---: | ---: |
| Spectral radius | 1.000254 | 0.997754 | 0.828897 | 0.229790 |
| Real-to-null radius ratio | 1.003 | | 3.607 | |
| State difference at 12 silent actions | 0.01154 | 0.00684 | 0.00335 | 0.00050 |
| Real-to-null retention ratio | 1.69 | | 6.67 | |
| Readout participation ratio | 5.53 | 28.95 | 4.42 | 28.81 |
| Nodes unreachable from sensory | 2,879 | 302 | 8,957 | 327 |

Under unsigned weights with incoming-L1 normalization the matrix is exactly
row-stochastic, so its spectral radius is pinned near 1 for any topology and
separates real from null by 0.3%. Signing releases that constraint and the
separation becomes a factor of 3.6. This is the clearest real-versus-null
structural signature measured so far.

**Signing does not fix cross-action memory.** The half-life is still exactly
2 actions. Because E/I cancellation lowers the spectral radius from 1.0003 to
0.8289, the signed graph in fact retains *less* at a fixed gain: 0.00335 against
0.01154 at 12 silent actions. Reaching comparable effective recurrence requires
roughly 1.21x the gain, which the operating-point sweep must search rather than
assume.

**The anatomical constraint on `K` is unchanged and slightly stronger.** Sensory
drive still needs three hops and four internal steps to move all 1,314
descending neurons (3 at one hop, 528 at two, 1,314 at three; 528 versus 688 in
the unsigned graph because inhibitory cancellation silences some two-hop
targets). `K=2` remains too small.

### Findings and decisions

- The signed condition is promoted to a first-class compiled runtime rather than
  an unexercised config option. Both runtimes are retained; neither replaces the
  other, and the unsigned runtime remains the pinned Gate 1 identity.
- Adding `unknown_transmitter_treatment: zero` to `configs/literal_rate.yaml`
  changes that file's SHA-256. The value is unchanged from what the existing
  unsigned manifest already recorded, so the compiled unsigned runtime is
  unaffected and Gate 1's preprocessing cross-check still matches. The
  `config_sha256` recorded in `results/manifests/dynamics_gate1_20260921.json`
  remains an accurate record of the file as it was when that gate ran.
- Retaining both runtimes costs about 200 MB of ignored local disk.
- The `driven_readout_cosine` for two distinct inputs is near zero in all four
  conditions (unsigned real +0.033, signed real -0.154). Instantaneous
  separability at the readout is not the bottleneck; cross-action retention is.

### Limitations

- The 3.6x spectral-radius separation is measured against the probe's within-row
  shuffle, which does not preserve out-degree. Some of the gap may be a pure
  out-degree effect. It must be re-measured against the preregistered directed
  degree-preserving null before it can support any claim, and against at least
  ten independently seeded nulls before a confirmatory one.
- The heuristic sign rule remains an approximation. Receptor and cell context can
  reverse or modulate the real effect of a transmitter.
- Deleting modulatory and unknown presynaptic neurons' outgoing edges is a
  modeling choice, not a biological fact. `positive`, `negative`, and `error`
  treatments are available and unexercised.
- No ARC game was played and no score was produced.

## 2026-09-21 — Degree-preserving nulls, closed-loop agent, and the first FlyGI ARC runs

### Completed

- Implemented `src/flygi/connectome/nulls.py`, previously a one-line stub: batched
  directed double-edge swaps that preserve both degree sequences exactly, with
  fourteen invariant tests. `flygi graph nulls` writes each null as a
  self-contained, hash-verified runtime bundle.
- Generated three independently seeded degree-preserving nulls of the signed
  runtime (seeds 20260921-20260923), 10 swaps per edge, about 350 s each.
- Implemented Milestone 3: the closed-loop connectome policy, its encoder,
  descending trace, literal action map, coordinate head and state policy.
- Implemented the corrected no-recurrent-graph bypass control.
- Launched the first full public evaluations of the FlyGI agent.

### Measured null quality

| Seed | Accepted swaps | Acceptance | Fraction of real edges retained |
| --- | ---: | ---: | ---: |
| 20260921 | 245,590,550 | 0.9895 | 0.005079 |
| 20260922 | 245,590,550 | 0.9895 | 0.005088 |
| 20260923 | 245,590,550 | 0.9895 | 0.005083 |

Each null keeps 0.51% of the real edge set, so the topology is thoroughly
randomized while in-degree, out-degree and the weight multiset are exact.

### The preregistered degree-preserving comparison

This is the comparison the whole project was gated on. Measured at `K=4`,
`leak=0.3`, `gain=0.9` on the heuristic-signed runtime.

| Measurement | Real signed | Null 20260921 | Null 20260922 | Null 20260923 |
| --- | ---: | ---: | ---: | ---: |
| Spectral radius | **0.828897** | 0.236000 | 0.234800 | 0.221900 |
| Hops to reach all 1,314 DNs | **3** | 2 | 2 | 2 |
| Readout targets per hop | 3, 528, 1314 | 783, 1314 | 795, 1314 | 787, 1314 |
| Nodes unreachable from sensory | 8,957 | 457 | 458 | 458 |
| Readout participation ratio | **5.385** | 18.54 | 14.33 | 16.00 |
| Settled mean absolute DN activity | 4.345e-06 | — | — | 4.798e-03 (mean) |
| State difference at 12 silent actions | **1.90e-04** | 1e-06 | 1e-06 | 1e-06 |

Null spectral radius: mean 0.230894, standard deviation 0.007816. The ratio is
**3.590**.

**The separation is not an out-degree artifact.** The earlier within-row shuffle,
which preserves in-degree only, gave 0.2298. Preserving out-degree exactly as
well moves it to 0.2309. Both are about a quarter of the real graph's 0.8289.

The reading is that excitation and inhibition in the fly are arranged so that
they do not cancel as completely as in a degree-matched random rewiring. The
real graph additionally keeps a deeper sensory-to-readout pathway, a roughly
three times lower-dimensional readout code, and measurably more cross-action
retention.

**This is a structural and dynamical result about the graph. It is not an ARC
result.** It does not show that any of these properties help on ARC-AGI-3. The
paired agent comparison is what tests that, and it is running.

The reviewed index is `results/manifests/degree_preserving_comparison_20260921.json`.

### Two control defects found and fixed

- **The graph ablation was degenerate.** It zeroed the persistent state every
  turn, so the readout was never driven and the control measured nothing; it
  finished all 125 rows in 45 seconds. The corrected bypass keeps the entire
  interface and removes only the graph: the projection targets the descending
  population directly with `connections_per_neuron` rescaled so total interface
  nonzeros match the real condition (389,471 against 390,272), and the recurrent
  gain is zero. The policy now refuses to be constructed as ablated with nonzero
  gain.
- **Null bundles were unloadable.** `file_record` stores an absolute filesystem
  path while runtime loading resolves output hashes relative to the bundle root,
  so every null was rejected with "manifest is missing runtime outputs". The
  arrays were always correct; only the manifest records were wrong, so the three
  existing nulls were repaired in place instead of being regenerated.

### The output-invariance failure and the adaptive readout

The first real-graph closed-loop run chose `ACTION1` on all twelve turns of
`ls20` with action entropy 0.000, while the readout was neither silent nor tied.

Measured cause: the descending block means are dominated by each neuron's fixed
offset and by a slow monotonic drift as the state integrates toward the fixed
point set by its average input. Between-block offset exceeds frame-driven
variation by roughly a factor of two, and the drift saturates within a handful
of turns, so an argmax over raw block means locks.

`AdaptiveStandardizer` reports each neuron's deviation from an EMA expectation
in units of its recent variability. One declared scalar, no trained parameter,
no per-game fitting, identical across graph conditions, output clipped. After
the change the same smoke gives entropy 1.459 on `ls20` and 1.895 on `sp80`.

This was a numerical-behavior fix, not tuning toward a score: the specification
requires checking output invariance before interpreting action patterns, and a
policy whose action never changes cannot test anything.

### Verification results

- `uv run pytest`: 158 tests passed (25 at the first checkpoint).
- Ruff lint and formatting checks passed.
- A staged Kaggle dataset loads and hash-checks through the ordinary runtime
  loader with no network and no source tables present.

### Limitations

- Three nulls were generated. The preregistration requires at least ten for a
  confirmatory claim.
- The signed graph's sign assignment remains a transmitter heuristic.
- `K=4` was chosen on the measured anatomical grounds recorded on this date, not
  by a completed operating-point sweep over `(K, leak, gain)`.
- No ARC performance comparison is recorded in this entry.

## 2026-09-21 — Gate 2: the first FlyGI ARC-AGI-3 results

### Completed

- Ran the closed-loop FlyGI agent and two controls on all 25 cached public games,
  seeds 0-4, exact 80-action ceiling, `K=4`, on the heuristic-signed runtime.
  Each condition is 125 rows and 10,000 actions.
- Staged and verified the offline Kaggle dataset (94,508,993 bytes) and rewrote
  the Kaggle adapter to run the connectome policy.

### Gate 2 outcome: passed

All three connectome conditions passed: 125/125 rows each, zero exceptions,
zero illegal actions, zero invalid `ACTION6` coordinates, zero budget
violations, and a matching deterministic replay. The complete 166,700-neuron,
24,559,055-edge graph is in every decision, with zero trainable parameters.
Median policy time was 164 ms per action; the maximum was 231 ms.

### Measured ARC results

| Condition | Mean score | Max | Rows > 0 | Levels | Games with a level |
| --- | ---: | ---: | ---: | ---: | --- |
| Real signed MaleCNS | **0.190476** | 4.7619 | 5 | 5 | `sp80` |
| No-recurrent-graph bypass | **0.190476** | 4.7619 | 5 | 5 | `r11l` |
| Degree-preserving null | 0.000000 | 0.0000 | 0 | 0 | none |
| Random legal (Gate 0) | 0.050626 | 4.7619 | 2 | 2 | `sp80` |

**The real graph and the interface-matched bypass scored exactly the same mean.**
Each completed one level in exactly one game out of 25, and they were different
games. This is the specification's section 19.3 cautionary pattern realized: a
parameter-matched adapter that bypasses the graph matches the graph. The
degree-preserving null scored zero, but the whole comparison rests on one game
per condition and carries no statistical weight.

### The seeds are not replicates

In every connectome condition, all 25 games produced **identical action traces
across all five seeds**. The policy is deterministic and these environments are
deterministic given the game, so the seeds add nothing. The effective sample
size is 25 games, not 125 rows. This removes most of the power the paired
`(game, seed)` design was assumed to have, and it must be corrected before any
confirmatory analysis: either the policy needs a declared stochastic component,
or the design needs many more games.

The random control does not share this property, because its policy is seeded;
its 25 games each produced five distinct traces.

### Behavioral diagnostics

| Measurement | Real | Null | Bypass | Random |
| --- | ---: | ---: | ---: | ---: |
| Mean unique observations per run | 52.84 | 49.08 | 55.12 | **64.18** |
| Observation repeat rate | 34.8% | 39.4% | 32.0% | **20.8%** |
| Mean consecutive repeats | 23.72 | 28.16 | 22.96 | **13.64** |
| Mean action entropy (bits) | 1.385 | 1.157 | 1.439 | **1.718** |
| `ACTION6` share | 47.4% | 35.3% | 39.2% | 35.3% |
| Rows with entropy < 0.2 bits | 30 | 40 | 35 | 30 |

**The connectome agent explores less than chance.** A deterministic argmax
policy falls into loops that a random policy escapes. The real graph sits
between the null and the bypass on most of these measures. The real condition
also leans much harder on `ACTION6` than any other condition.

No action trace was identical between any two graph conditions in any game
(0/25 for real versus bypass, 0/25 for real versus null), so the graph does
causally determine behavior. It simply does not determine it better than a
matched bypass does.

### What this does and does not establish

Established:

- engineering success, in the specification's sense: a valid, gate-passing
  ARC-AGI-3 agent that uses the complete MaleCNS graph in every decision;
- a live, tested causal path from frame to action through the graph;
- a replicable structural difference between the real graph and its
  degree-preserving nulls, recorded separately on this date.

Not established, and not claimed:

- that the fly connectome confers any advantage on ARC-AGI-3. It did not beat a
  parameter-matched bypass;
- that the structural difference measured in the dynamics probe has any
  behavioral consequence. The agent comparison is the test of that, and it came
  out flat;
- anything at all from the `sp80` result. One game, one level, at a score the
  random control also reached.

### Artifacts

| Condition | Artifact | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Real signed | `results/connectome_agent/20260921T144321.262543Z-real-signed.json` | 8,224,279 | see index |
| Null | `results/connectome_agent/20260921T144956.557736Z-null-degree-preserving.json` | — | see index |
| Bypass | `results/connectome_agent/20260921T144908.137005Z-no-graph-bypass.json` | — | see index |

The reviewed index is `results/manifests/connectome_agent_gate2_20260921.json`.

### Limitations

- One null seed was evaluated on ARC, though three were built.
- No weight shuffle, sign shuffle, or matched generic reservoir exists.
- The operating point `K=4`, `leak=0.3`, `gain=0.9` was chosen on anatomical
  grounds, not by a completed sweep. `leak` and `gain` are unchanged from the
  original K=2 declaration and have never been searched.
- The unsigned runtime has not been evaluated on ARC.
- No competition submission has been made.

## 2026-09-21 — Leaderboard-readiness audit

### Observed external state

- An authenticated read-only Kaggle query returned `No submissions found` for
  `arc-prize-2026-arc-agi-3`.
- An authenticated dataset listing returned `No datasets found` for the account,
  so `megusalexandrus/flygi-malecns-runtime` is staged locally but is not yet
  published or attachable by the notebook.
- The existing private notebook
  `megusalexandrus/flygi-arc-agi-3` reports `KernelWorkerStatus.COMPLETE`; that is
  the earlier packaging smoke, not a connectome competition rerun.
- The official competition page currently says notebook submissions may run for
  up to nine hours and the final submission deadline is 2026-11-02. Kaggle staff
  separately clarified that the effective limit is one submission per day. The
  optional second milestone deadline is 2026-09-30 and requires a public,
  open-source notebook for prize eligibility. None of these facts authorizes an
  upload or submission.

### Deployment defects found

- The ordinary private notebook execution never instantiates `MyAgent`: the
  adapter is imported only inside the competition-rerun branch. The current
  instruction to confirm `mode=connectome` from an ordinary run therefore cannot
  work. Add a no-game preflight that discovers, hashes, loads, and reports the
  attached runtime before writing the dummy artifact.
- A missing or invalid attached runtime still makes the competition adapter fall
  back to random legal play. That is useful for a generic import smoke but unsafe
  for an official FlyGI submission. Competition reruns must fail closed when the
  connectome is unavailable; the fallback should remain opt-in for tests only.

### Behavioral implications for the next decoder

- Action-only temperature sampling does **not** repair the seed defect. Six
  public games (`ft09`, `lp85`, `r11l`, `s5i5`, `tn36`, and `vc33`) expose only
  `ACTION6` during active play. Their action choice cannot vary, so independent
  runs require seeded coordinate selection as well.
- In the Gate 2 real trace, `lp85` used only six unique coordinates in 80 clicks
  and never changed the observation; `ft09` used four and changed it once. This
  makes the ungrounded deterministic coordinate head an immediate leaderboard
  bottleneck, not merely a statistical issue.
- A read-only three-game probe found median legal-logit ranges of 0.157 on
  `ls20` and 0.260 on `sp80`. On those visited states, a raw softmax temperature
  of 1.0 had expected entropy within roughly 0.01 bits of uniform. Naively adding
  `temperature=1` would therefore erase most graph preference. Use a declared,
  scale-aware rule (for example z-score legal logits before sampling) or choose a
  smaller temperature using behavior-only criteria, never public score.
- The literal coordinate rule in the specification is a fixed novelty centroid,
  whereas the current implementation folds arbitrary DN body-ID blocks into 64
  bins per axis. A novelty-aware fallback is spatially grounded, but it still
  needs a seeded exploration rule when a click produces no change; otherwise a
  click-only game can repeat the same miss indefinitely.

## Next steps

Gate 2 is passed and the current agent is no longer a barebones submission. The
shortest responsible route to the leaderboard is now separate from the longer
scientific-control backlog.

1. **Completed: harden the Kaggle path.** The ordinary-run runtime preflight now
   verifies and reports the attached graph, and competition reruns fail closed
   rather than silently becoming a random agent. Missing, incomplete, verified,
   and competition-rerun paths have tests.
2. **Completed: make the fixed policy genuinely seeded.** Both masked action
   logits and factorized `ACTION6` coordinate logits now use one recorded,
   per-policy NumPy RNG. The same sampler is used by every graph condition, and
   the full evaluator now passes and records the derived seed for every row.
3. **Completed: ground click exploration.** The policy uses the changed-cell
   novelty centroid when available, then seeded untried-grid exploration after
   a click causes no observation change.
4. **Completed: calibrate without score tuning.** The preregistered three-point
   sampler grid was ranked
   using only action entropy, unique observations, consecutive repeats, graph
   sensitivity, and runtime. The focused choice was frozen before looking at
   scores. The next gate is one full 25-game by five-seed real-agent run; the
   deployment candidate must keep zero illegal actions, valid coordinates,
   replay stability, and a live graph-to-action causal path.
5. **Stage and inspect the final bundle.** Rebuild the deterministic source zip
   and 95 MB dataset, verify every digest from the staged directory, and run the
   private notebook. Its ordinary log must explicitly report the signed
   166,700-node runtime, 24,559,055 edges, and `K=4` before any official rerun.
6. **Publish and submit under the user's explicit authorization.** The user
   authorized the private Kaggle Dataset publish, private notebook push, and one
   daily competition submission on 2026-09-21. Execute them only after the local
   calibration and full gate pass, verify the ordinary notebook log first, and
   record the version, hashes, runtime status, and leaderboard score.
7. **Add a positive control after the first leaderboard entry.** Every null is
   built to be no better than the fly. With real, bypass and null all near zero,
   the design cannot separate "the biological graph confers no advantage" from
   "this interface and operating point cannot express an advantage any graph
   could confer." A reservoir
   deliberately tuned to the edge of chaos at matched node and edge count would
   separate them.
8. **Complete the operating-point sweep.** `K=4` was chosen on anatomical
   grounds; `leak=0.3` and `gain=0.9` are unchanged from the original `K=2`
   declaration and have never been searched. Sweep `(K, leak, gain)` on the
   dynamical diagnostics, apply the winner identically to every condition.
9. **Reconsider the primary endpoint.** Gate 0 chance is 2 of 125 rows; Gate 2
   real is 5 of 125, all one game. A paired test on public-set RHAE at this base
   rate cannot detect anything. Promote the specification's section 13.3
   behavioral diagnostics to co-primary, and record the change before inspecting
   further results.
10. **Scale the controls.** Evaluate all three existing nulls rather than one,
   build the remaining seven, and add the weight shuffle, the sign shuffle within
   transmitter strata, and the matched generic reservoir.
11. **Track B.** A small trained readout on a frozen graph is where the
   specification expects any real signal. It must be compared against the same
   parameter-matched bypass, which has now beaten the fly once already.

### Open design questions

- **The primary endpoint is near-degenerate.** See step 9.
- **There is no positive control.** See step 7.
- **The structural finding has no behavioral consequence yet.** The real graph
  separates cleanly from its degree-preserving nulls on spectral radius (3.59x),
  pathway depth, readout dimensionality and retention. None of that produced an
  ARC advantage. Either the interface cannot exploit those properties, or they
  are not useful for this task. Distinguishing those two is what the positive
  control is for.

## 2026-09-21 — Seeded decoder and deployment-hardening checkpoint

The source implementation for leaderboard hardening is complete and locally
verified; the score-blind calibration itself has not yet been run at full
declared size.

### Implemented

- Legal action choice now uses a declared z-score/softmax categorical sampler.
  The three preregistered action/coordinate temperature pairs are `focused`
  (0.15/0.20), `balanced` (0.35/0.50), and `exploratory` (0.70/1.00).
- `ACTION6` samples both factorized axes from the same policy RNG. A changed
  observation supplies a novelty-centroid click; an unchanged observation after
  a click supplies a seeded, not-yet-clicked uniform grid location.
- One derived 64-bit decision seed is supplied per `(experiment seed, game)`
  row. Same-seed replay rewinds the RNG, while tests establish different-seed
  divergence for click payloads. The full evaluator previously discarded this
  seed; it now passes it to the policy and records it in each row's diagnostics.
- The score-blind calibration runner evaluates matched real and no-recurrent-
  graph bypass conditions. Its equal-weight ordinal criteria are unique
  observations, consecutive repeats, legal-normalized action entropy, causal
  real/bypass turn disagreement, and median policy time. It strips official
  score and level-progress fields before writing its immutable artifact.
- Kaggle ordinary runs now load and hash-verify all three deployment arrays and
  emit one `FLYGI_PREFLIGHT=` JSON identity line. Missing or invalid assets fail
  closed. Random fallback requires an explicit local smoke-test opt-in and is
  disabled unconditionally during competition reruns.

### Verification observed before checkpoint

- `UV_CACHE_DIR=/tmp/flygi-uv-cache uv run pytest -q`: **189 passed**.
- `UV_CACHE_DIR=/tmp/flygi-uv-cache uv run ruff check .`: passed.
- `UV_CACHE_DIR=/tmp/flygi-uv-cache uv run ruff format --check .`: all 91 files
  already formatted.
- Real staged Kaggle bundle preflight: **166,700 nodes**, **24,559,055 edges**,
  `K=4`, release `male-cns:v1.0`, heuristic signs, with `graph.npz`,
  `node_metadata.npz`, and `groups.npz` all verified against manifest hashes.
- A four-action, two-seed real-graph smoke on `ls20` completed with the
  `balanced` candidate and demonstrated the runner end to end. This smoke is not
  the calibration result and does not freeze the candidate.

### Immediate ordered next steps

1. Run one 25-game by five-seed signed-real gate at 80 actions, verify engineering
   validity, replay, seed diversity, and live graph-use diagnostics, then record an
   immutable reviewed manifest.
2. Rebuild and verify the staged dataset and deterministic notebook source.
3. Publish the private dataset, run the private notebook, verify its preflight
   log, and make exactly one official competition submission.

## 2026-09-21 — Score-blind sampler calibration passed

The full preregistered calibration completed successfully on four games
(`ft09`, `lp85`, `ls20`, `sp80`), seeds 0 and 1, 40 actions, and matched
real-signed and no-recurrent-graph-bypass conditions. All three candidates were
eligible: both conditions had zero failed rows, illegal actions, invalid
coordinates, and budget violations; same-seed replay matched; both click-only
and mixed games produced across-seed trace diversity; and every candidate had a
nonzero real-versus-bypass action/payload disagreement.

The equal-weight ordinal result, computed without public score or level
progress, was:

| Candidate | Action T | Coordinate T | Rank sum | Rank |
| --- | ---: | ---: | ---: | ---: |
| **focused** | **0.15** | **0.20** | **8** | **1** |
| balanced | 0.35 | 0.50 | 9 | 2 |
| exploratory | 0.70 | 1.00 | 10 | 3 |

Focused recorded 28.125 mean unique observations, 12.25 mean consecutive
repeats, 0.11345 legal-normalized action entropy, 0.43125 real/bypass causal
turn disagreement, and 134.90 ms median policy time. It won on unique
observations and causal disagreement, tied on repeats, ranked second on runtime,
and traded away entropy. This is a small calibration and the one-point rank-sum
margin should not be overinterpreted; the point of the procedure is to freeze a
reasonable operating point without score selection.

The immutable ignored artifact is
`results/sampler_calibration/20260921T211921.876683Z-5a1228c249.json`
(1,815,901 bytes, SHA-256
`0146857a58f6830841688a28e6a3f04ea6eab4adaf45f39bd6dc18419c63af58`).
A recursive audit found zero keys named `official`, `score`,
`levels_completed`, or `final_levels_completed`. The reviewed, tracked summary
is `results/manifests/sampler_calibration_20260921.json`.

The focused temperatures are now frozen in all three checked-in decoder
configs and in the source defaults. The next action is the full 25-game by
five-seed signed-real gate; only that post-freeze run may be inspected for ARC
performance before deployment.

## 2026-09-21 — Post-freeze full signed-real gate passed and audited

The frozen `focused` policy was run with `make connectome-local` at Git commit
`e5695d3e4e5b6b5ad0cedbe4ec504f9740644d2d`: all 25 cached public games,
seeds 0 through 4, exact 80-action ceiling, signed MaleCNS runtime, `K=4`, and
zero trainable parameters. The immutable ignored artifact is
`results/connectome_agent/20260921T215856.747869Z-real-signed-focused.json`.

Observed before the detailed artifact audit:

- the engineering gate passed all **125/125 rows** with no reported issues;
- all 10,000 attempted actions completed, with zero failed rows, illegal
  actions, invalid `ACTION6` coordinates, or budget violations;
- the fixed-seed replay on `lf52`, seed 0, matched exactly;
- `sp80` completed one level for seeds 1, 3, and 4, each scoring 4.76190476;
  seeds 0 and 2 did not complete a level;
- all other games and seeds scored zero;
- the overall mean score is therefore **0.1142857143**, with three total level
  completions in 125 rows. This is below the old deterministic real-condition
  mean of 0.190476 and above the earlier random-control mean of 0.050626, but all
  signal still comes from one game and no biological advantage is claimed;
- the artifact reports mean policy time 140.44 ms/action, median 136.48 ms,
  p95 157.05 ms, peak process RSS 422,723,584 bytes, and the expected signed
  graph identity: 166,700 nodes, 24,559,055 edges.

The evaluator's final console line printed `mean score=None max=None` because it
looked for those fields at `summaries` rather than `summaries.overall`; the
artifact itself contains complete scorecards and the correct summary. The
report-only lookup is fixed in the working tree and does not require rerunning
the 10,000-action experiment.

### Audit results and next actions

The detailed audit found zero policy-seed provenance mismatches and zero rows in
which the graph failed to advance on every decision. All 25 games produced five
distinct action/payload trace hashes across the five seeds; no game retained the
old duplicate-seed defect.

The new policy averaged 54.664 unique observations and 20.76 consecutive
repeats per row, compared with 52.84 and 23.72 for the old deterministic real
condition and 64.184 and 13.64 for random legal play. Exploration improved
modestly but remains worse than chance. Across 4,292 clicks, the policy used the
novelty centroid 2,701 times, seeded untried exploration 1,512 times, and the
factorized graph proposal 79 times; the sum of within-row unique coordinates was
3,574. In `lp85`, rows used 78–80 unique coordinates while still seeing only
2–6 unique observations, confirming that the remaining loop is not caused by
repeating the same click.

The artifact is 8,256,340 bytes with SHA-256
`8ca66324e5a91a5407cf6e9688ffe3f5f2bd3f8439a474b502c769ae1b5e6cca`.
The reviewed tracked summary is
`results/manifests/connectome_agent_seeded_gate_20260921.json`.

Next:

1. commit and push the report fix, reviewed manifest, and worklog checkpoint;
2. rebuild the deterministic notebook source and the signed runtime dataset,
   verify every staged hash, and run tests;
3. publish the authorized private Kaggle Dataset and push the authorized private
   notebook;
4. inspect the ordinary notebook log for the exact verified
   `FLYGI_PREFLIGHT=` identity before making the one authorized official
   submission; then record its version and status here.

## 2026-09-21 — Final Kaggle bundle staged and locally preflighted

After the post-freeze gate checkpoint was pushed as `6ac1d49`, the Kaggle
dataset was rebuilt from `configs/literal_rate_signed.yaml` and the generated
notebook was rebuilt from tracked source. Both outputs remain ignored by Git.

The staged dataset contains 94,508,993 bytes of runtime/config inputs:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `runtime/graph.npz` | 92,033,305 | `45e332d90ea4e881ece5d4d72216955bd53eec922aa60955a69db510272eff61` |
| `runtime/node_metadata.npz` | 2,464,976 | `2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c` |
| `runtime/groups.npz` | 3,189 | `09736379ce989268080f57b64f357e800cf446972007c1af2287a86b9985a89d` |
| `runtime/manifest.json` | 7,523 | `6223e065029b2699d2e21e079ca7a6a8349672785230a0ba3f4ecf83eacd27f4` |
| `config.yaml` | 4,650 | `98f6d7b10acd6336af73daa2bae47933b721988758858a3cedd021991a803262` |

The stage loader independently loaded and verified 166,700 nodes, 24,559,055
edges, 1,314 descending neurons, release `male-cns:v1.0`, and heuristic signs.
A local import of the exact adapter against the staged directory completed and
emitted:

```text
FLYGI_PREFLIGHT={"edges":24559055,"internal_steps":4,"mode":"connectome","nodes":166700,"release":"male-cns:v1.0","sign_mode":"heuristic","verified":true,...}
```

The generated notebook is 110,068 bytes with SHA-256
`4eac1595996d22919e76bceb620c2b7f8a9b88c2e5769329ae03650c50543118`.
Its tracked metadata hash is
`d729819b3e4dc494c4a2bec179a50768887461ac4aa12ba1672372a19f9221e5`
and declares the private notebook `megusalexandrus/flygi-arc-agi-3`, private
dataset source `megusalexandrus/flygi-malecns-runtime`, CPU execution, and no
internet.

Current action: publish the staged dataset privately. Next: confirm the dataset
exists and is private, push the private notebook, wait for its ordinary run,
inspect the log for the exact preflight identity above, and only then make the
one authorized official submission.

## 2026-09-21 — Private Kaggle assets published; notebook validation running

The authorized external packaging actions have begun:

- Kaggle accepted the runtime as the **private** Dataset
  `megusalexandrus/flygi-malecns-runtime`; the creation command explicitly
  reported “Your private Dataset is being created.” A subsequent authenticated
  status query returned `status=ready`, `current_version_number=1`.
- Kaggle accepted **private notebook version 2** for
  `megusalexandrus/flygi-arc-agi-3`. The notebook remains CPU-only,
  internet-disabled, and attached to private dataset version 1 through its
  declared dataset source.

Current action: wait for notebook version 2 to finish its ordinary run, then
inspect its server-side log for `FLYGI_PREFLIGHT=` with `mode=connectome`,
`verified=true`, 166,700 nodes, 24,559,055 edges, `K=4`, release
`male-cns:v1.0`, heuristic signs, and all three expected array hashes. Do not
spend the authorized competition submission unless that exact validation
passes. After validation, submit notebook version 2 once and record the Kaggle
submission identifier/status here; make no second submission.

## 2026-09-21 — Private notebook version 2 validated on Kaggle

Kaggle reported `KernelWorkerStatus.COMPLETE` for private notebook version 2.
The server-side log emitted the required identity at 23.92 seconds:

```text
FLYGI_PREFLIGHT={"edges":24559055,"internal_steps":4,"mode":"connectome","nodes":166700,"release":"male-cns:v1.0","sign_mode":"heuristic","verified":true,"verified_output_hashes":{"graph.npz":"45e332d90ea4e881ece5d4d72216955bd53eec922aa60955a69db510272eff61","groups.npz":"09736379ce989268080f57b64f357e800cf446972007c1af2287a86b9985a89d","node_metadata.npz":"2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c"}}
```

This proves that Kaggle, not only the local machine, discovered the attached
private dataset, loaded the complete signed MaleCNS graph, verified every
deployment array, and assembled the declared `K=4` policy. The ordinary run
also produced `submission.parquet` (868 bytes; Kaggle creation time 22:10 UTC).
Pip printed unrelated dependency-conflict warnings for preinstalled Dopamine and
Gradio packages, but the required competition wheels installed, preflight
passed, the notebook completed, and the output exists.

Current action: make the one authorized official submission for competition
`arc-prize-2026-arc-agi-3` from notebook
`megusalexandrus/flygi-arc-agi-3`, version 2, file `submission.parquet`. Record
the returned submission reference/status and monitor it to completion. Do not
submit another version.

## 2026-09-21 — First official FlyGI submission accepted and pending

The one authorized daily competition submission was made from private notebook
`megusalexandrus/flygi-arc-agi-3`, **version 2**, output
`submission.parquet`, with description `FlyGI signed MaleCNS seeded literal
policy`. Kaggle returned zero submissions remaining today, confirming that the
single daily slot was consumed; no retry or second submission is authorized.

The authenticated competition record is:

- competition: `arc-prize-2026-arc-agi-3`;
- submission ref: **56444435**;
- submitted at: `2026-09-21T22:14:13.373000` UTC;
- status: `SubmissionStatus.PENDING`;
- public score: not yet available;
- private score: not yet available.

Current action: monitor submission ref 56444435 until Kaggle reports completion
or an actionable failure. In parallel, prepare honest LinkedIn and X copy around
“I made a fly take ARC-AGI-3,” clearly separating the engineering milestone from
the negative/uncertain scientific result. Do not publish social content or make
another competition submission; save drafts in the repository and update them
with the actual leaderboard status when known.

A thread heartbeat named `Monitor FlyGI submission` is active at a 20-minute
interval. It is instructed to remain quiet while the state is unchanged, never
submit or retry, and on completion/failure to update this worklog and the social
draft, run checks, commit, push, and report the outcome.

## 2026-09-22 — First official submission scored: 0.00, rank 3212 of 3215

### Observed external result

Submission **56444435** finished. The authenticated competition record now
reads:

- competition: `arc-prize-2026-arc-agi-3`;
- submission ref: **56444435**;
- file: `submission.parquet` from private notebook version 2;
- submitted at: `2026-09-21T22:14:13.373000` UTC;
- status: **`SubmissionStatus.COMPLETE`**;
- **public score: 0.00**;
- private score: not available.

A downloaded public-leaderboard snapshot taken at `2026-09-22T00:25:25` UTC
(223,877 bytes, SHA-256
`8251a9fb93dc791a5cfae558d9112764b5fb823596568d71b71c2926fc1acd58`, not
committed) places the entry as:

| Field | Observed |
| --- | --- |
| Team | `Megus Alexandrus` (`megusalexandrus`), team id 16928093 |
| Rank | **3212 of 3215** |
| Score | 0.00 |
| Submission count | 1 |

Distribution context from the same snapshot: 3,052 teams scored above zero, the
lowest nonzero score was 0.01, the top score was 18.81, and **163 teams are tied
at 0.00** occupying ranks 3050 through 3212. FlyGI sits at the bottom of that
tied band.

### Reading the result honestly

The hidden-set score is zero. That is the outcome the specification anticipated
in its closing section, and it is consistent with everything measured locally:
all of the public-set signal came from a single game (`sp80`), and the hidden
set does not contain it.

What the submission does establish is the specification's level-1 success: a
valid, accepted competition entry in which the complete 166,700-neuron,
24,559,055-edge signed MaleCNS graph is verified on Kaggle's own machine and
used in every decision, with zero trainable parameters. The server-side
`FLYGI_PREFLIGHT=` line with `mode=connectome`, `verified=true`, and all three
matching array hashes is the evidence that this was a connectome run and not a
fallback.

What it does not establish is any of levels 3 through 5. A zero score cannot
separate the real graph from its controls, and no biological advantage is
claimed. The local Gate 2 finding stands unchanged: the real graph did not beat
an interface-matched bypass.

### Process note

The 20-minute monitor heartbeat described in the previous entry did not fire on
completion; it ended with the session that created it. The submission had
already been `COMPLETE` for some time before this entry was written. Any future
monitoring of an external state should not rely on a session-scoped heartbeat
surviving across sessions.

### Next

No further competition submission is authorized. The scientific backlog is
unchanged and is led by the matched positive-control reservoir, without which a
zero-versus-zero comparison cannot distinguish "the biological graph confers no
advantage" from "this interface cannot express an advantage any graph could
confer."

## 2026-09-22 — Action-efficiency sweep (COMPLETE)

### Why this is running

The 0.00 hidden-set score prompted a question about what would raise it. Two
diagnoses were tested rather than assumed.

**Diagnosis 1: the score is depth-limited, not efficiency-limited.** The ARC
scorecard computes `sum(level_score * level_index) / sum(level_index)` and caps
the result at `max_weights / total_weights * 100`, where `max_weights` sums the
indices of levels actually completed. The observed `sp80` score of
`4.76190476` is exactly `100/21`: the agent completed level 1 at or better than
the human action baseline, and was capped at one level's weight out of 21. Its
efficiency on that level was already maximal. What limits the score is how many
levels it clears.

**Diagnosis 2: the action budget is not the binding constraint. Measured.**
`sp80` was rerun at 2,000 actions, 25x the deployed ceiling:

| Seed | 80 actions | 2,000 actions |
| --- | --- | --- |
| 0 | 0 levels, score 0 | **0 levels, score 0** |
| 1 | 1 level, 4.76190476 | **1 level, 4.76190476** |

Twenty-five times the budget produced no additional level on either seed. Seed 0
used all 2,000 actions with 76 resets and a 0.562 observation repeat rate. The
frozen agent does not run out of budget; it exhausts what a fixed policy can do.
Raising `MAX_ACTIONS` is therefore not a route to a better score, and the
framework's 80 is an anti-infinite-loop default rather than a competition rule.

**The signal that prompted this sweep.** At a matched 2,000-action budget on
`sp80`, the fly and the random control reached the same depth but not the same
efficiency:

| Condition | Levels | Score |
| --- | ---: | ---: |
| Real signed fly | 1 | **4.76190476** |
| Random legal, seed 0 | 1 | 0.81969864 |
| Random legal, seed 1 | 1 | 1.56636184 |

The fly reached level 1 in far fewer actions, and RHAE rewards exactly that.
This is the first measurement in which the connectome beats chance on the
competition metric itself. It is a single game, so it may be an `sp80`
artifact. This sweep tests whether it generalizes.

### Protocol

All 25 cached public games, seeds 0-2, **500-action ceiling**, strict offline,
frozen `focused` sampler, signed runtime, `K=4`, zero trainable parameters.
37,500 actions per condition. Four matched conditions:

1. `eff-real-signed` — real heuristic-signed MaleCNS;
2. `eff-null-degree-preserving` — directed degree-preserving null, seed 20260921;
3. `eff-no-graph-bypass` — interface-matched, zero recurrent gain;
4. random legal — the chance control, same games/seeds/budget.

The primary measurement is **actions taken to complete a level**, on
`(game, seed)` rows where any condition completes one, plus the official score.
This is a predeclared comparison of efficiency, not of depth; the 2,000-action
probe already established that depth does not move.

### Completed results

All four conditions completed their full 75-row matrices. Every condition had
75/75 successful rows, 37,500/37,500 completed actions, zero exceptions,
illegal actions, invalid `ACTION6` coordinates, or budget violations, and a
matching deterministic `lf52` replay.

| Condition | Mean score | Max score | Rows with progress | Levels | Unique observations | Observation repeats | Median policy ms/action |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Real signed MaleCNS | **0.06475067** | 4.76190476 | 2 | 2 | 15,996 | 21,579 | 164.12 |
| Degree-preserving null | 0.00787215 | 0.28292411 | 3 | 3 | 16,262 | 21,313 | 164.62 |
| No-graph bypass | 0.00075350 | 0.05651241 | 1 | 1 | 16,339 | 21,236 | 164.21 |
| Random legal | **0.09756824** | 4.76190476 | 6 | 6 | **25,140** | **12,435** | 0.0277 |

The three graph conditions were deliberately run concurrently and contended for
memory bandwidth, so their approximately 164 ms policy timings describe that
execution regime. The random policy has no sparse graph update and its timing
is not a compute-matched comparison.

Every graph-condition completion was the first level of `sp80`:

- real signed: seed 1 in **9 actions** (score 4.76190476) and seed 2 in
  **277 actions** (score 0.09439530);
- degree-preserving null: seeds 0, 1, and 2 in **303, 160, and 178 actions**
  (scores 0.07889049, 0.28292411, and 0.22859668);
- no-graph bypass: seed 2 in **358 actions** (score 0.05651241).

Random legal completed the first `sp80` level in **94, 68, and 14 actions** for
seeds 0, 1, and 2, and the first `r11l` level in **333, 164, and 191 actions**.
No condition completed a second level.

### Preliminary reading, before formal paired analysis

The isolated 9-action fly completion is real, but its efficiency advantage did
not generalize consistently across matched seeds. On `sp80` seed 1 the fly was
faster than random and the degree-preserving null; on seed 2 it was much slower
than both. Seed 0 produced no fly completion. Across the full matrix, random
legal had the highest mean score and twice as many level completions as the real
graph; the degree-preserving null completed more levels than the real graph but
at lower scores.

This is descriptive, not a completed statistical result. Progress is confined
to two games, and rows without a completion are right-censored at 500 actions.
The completion-only action counts must not be averaged as though the censored
rows were missing at random. The paired-analysis implementation must predeclare
that treatment, cluster uncertainty over games, and preserve all zero rows.

The evidence therefore does **not** support a connectome efficiency advantage.
It does strengthen the earlier conclusion that the frozen literal policy has no
observed path beyond level 1, even when given far more actions.

### Immutable artifacts

All full artifacts are ignored by Git; the paths, byte counts, and SHA-256
digests below are the durable identities used by the forthcoming analysis.

| Condition | Artifact | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Real signed | `results/connectome_agent/20260922T032548.496866Z-eff-real-signed.json` | 29,229,516 | `9e97aa7a726d31cad82492f0dd44659578a16326828ffdef60a404d9c583338f` |
| Degree-preserving null | `results/connectome_agent/20260922T032558.385563Z-eff-null-degree-preserving.json` | 29,195,496 | `18d53914a9d96b5f1b070cf381fbd44b6f75d86fedc9348de311b5990c408b25` |
| No-graph bypass | `results/connectome_agent/20260922T032518.416940Z-eff-no-graph-bypass.json` | 29,209,629 | `f40c1454631d735149b0cc7873163cac608906b6ca09a3c1499a655d7867e22e` |
| Random legal | `results/random_baseline/20260922T013053.669084Z-d8b863adad.json` | 28,934,324 | `0a1c036c62b2503842e263d18909b796a78801bd078dfa61da5b094a1f9defe5` |

### Progress update — positive control implemented

While the sweep runs, `src/flygi/connectome/reservoirs.py` was implemented with
eleven tests. It provides both remaining reservoir conditions:

- **`matched_random`** — the specification's generic matched reservoir. Real
  node count, real edge count, the real weight multiset permuted rather than
  resampled, edges placed uniformly at random, and the *same* incoming-L1
  normalization as the real condition. A negative control.
- **`edge_of_chaos`** — the positive control. Not a null; its purpose is to be
  good, so that a set of near-zero results can distinguish "the biological graph
  confers no advantage" from "this interface cannot express an advantage that
  any graph could confer."

**A design error was caught by its own test.** The positive control was first
built by scaling to a spectral radius of 0.95, which failed against the matched
null. The reason is the finding already recorded on 2026-09-21: incoming-L1
normalization of non-negative weights yields a row-stochastic matrix whose
spectral radius is exactly one for *any* topology. Targeting 0.95 therefore
placed the "positive" control *below* its own null, and a memory probe confirmed
it retained less state.

A non-negative row-stochastic matrix is an averaging operator: repeated
application diffuses and its memory is confined to one global mode. Scaling the
radius is not sufficient. The positive control now assigns symmetric random
signs before scaling, which is the standard echo-state construction, and its
statistics record `signs_randomized`, `departs_from_declared_normalization`, and
`departs_from_declared_sign_mode` so it can never be reported as a matched null.

This is the same mechanism behind the real graph's measured 3.59x separation
from its degree-preserving nulls appearing only in the signed condition.

Verification: `uv run pytest -q` → **200 passed**; ruff lint and format checks
passed.

### Sweep throughput, measured

During execution, each of the three graph conditions used 58-59% CPU rather
than 100%. Three concurrent sparse matrix-vector products over a roughly 200 MB
working set contended for memory bandwidth rather than cores. The observed rate
was about 2.4 minutes per row and the three artifacts completed within seconds
of one another at 03:25 UTC. No sweep process remains active.

### Progress update — both reservoirs compiled and the positive control validated

Both reservoir conditions were compiled at full scale from the signed runtime
(`flygi graph reservoirs`, seed 20260922, 104 s and 121 s respectively). Each is
a hash-verified runtime bundle with exactly 24,559,055 edges, readable by the
existing evaluator with no special-casing.

They were then probed at the deployed operating point (`K=4`, `leak=0.3`,
`gain=0.9`):

| Condition | rho | Half-life | Retained @12 silent actions | Readout PR |
| --- | ---: | ---: | ---: | ---: |
| Real signed fly | 0.8289 | 1 action | 0.00019 | 5.38 |
| Matched random reservoir | 0.1608 | 1 action | 0.00000 | 20.44 |
| **Positive control (edge of chaos)** | **0.9924** | **3 actions** | **0.07686** | **24.40** |

**The positive control is valid.** Its declared criterion was that it must
retain state measurably longer than the real graph, and it retains roughly 400
times as much after 12 silent actions, with three times the half-life. It is
therefore usable as the discriminating condition.

This makes the outstanding interpretive question answerable for the first time:

- if the positive control **also** scores near zero on the public set, then this
  interface and operating point cannot register an advantage that *any* graph
  could confer, and the fly's null ARC result says nothing about the fly;
- if the positive control scores **clearly above zero**, the harness can register
  an advantage, and the fly's failure to beat its bypass is a real finding about
  the connectome.

Two secondary observations. The real graph sits far above the matched random
reservoir (0.8289 against 0.1608), consistent with the degree-preserving
comparison: the fly is not a generic random sparse graph. It also sits far below
the regime that actually sustains memory.

Recorded discrepancy: the build targeted a spectral radius of 0.95 and the probe
measured 0.9924. Both use power iteration with different iteration caps, so this
is estimator disagreement rather than a failed scaling, and it does not affect
the conclusion, which only requires the positive control to sit in a long-memory
regime.

The reviewed index is `results/manifests/positive_control_regime_20260922.json`.

### Revised planned next (updated after sweep completion)

1. Implement the currently placeholder Milestone 4 paired-analysis stack:
   strict artifact/protocol validation, a complete 75-pair join, explicit
   handling of budget-censored non-completions, paired outcome and behavioral
   summaries, game-clustered bootstrap intervals, within-pair permutation
   tests, immutable output, and unit tests.
2. Freeze the analysis endpoints and pairwise contrasts before inspecting new
   reservoir ARC outcomes.
3. Evaluate the **positive control** on the public set at the same 25 games,
   seeds 0-2, and 500-action budget. Then evaluate the matched random reservoir
   on the identical protocol. Both compiled bundles already load through the
   existing evaluator; these are experiment runs, not new model implementation.
4. Run the paired six-condition analysis and write a small reviewed manifest.
5. Complete the remaining Milestone 4 control implementations: weight shuffle,
   sign shuffle within declared transmitter strata, and seven additional
   degree-preserving nulls for the required ten-null distribution.
6. Follow the specification's declared order: controls, then Track B's frozen
   trained interface. Track C plasticity remains later work because it changes
   the research question and makes null matching substantially harder.

## 2026-09-22 — Score-improvement intervention 1: state-conditioned loop escape (PREREGISTERED)

### Why this is the next finite change

The completed 500-action sweep rules out action budget as the immediate
bottleneck and identifies a concrete behavioral deficit: the real signed agent
recorded 21,579 repeated observations across 75 rows, versus 12,435 for random
legal play. Its 15,996 unique observations were also well below random's
25,140. All real-agent progress remained confined to two first-level
completions in `sp80`, with mean score `0.06475067`; random reached six first
levels across `sp80` and `r11l`, with mean score `0.09756824`.

The next intervention is therefore a bounded state-conditioned loop-escape
layer, not another budget increase or an analysis-only subsystem. It preserves
the signed MaleCNS computation and adds a recorded bias to its action logits:

- identify the current observation by a stable grid hash;
- remember action attempts and unchanged-observation failures separately for
  each observation;
- give less-tried legal actions a finite exploration bonus and penalize actions
  that previously left that same observation unchanged;
- keep the first decision in a newly observed state graph-driven because every
  legal action receives the same initial bonus;
- track attempted `ACTION6` coordinates per observation rather than globally,
  so a click known to fail in one state is avoided when that state recurs;
- reset all loop memory at the environment boundary and use only the existing
  policy-owned seeded RNG.

The feature will be explicit in typed configuration, disabled by default, and
fully visible in turn records. Existing configs and policies must retain their
current behavior when it is disabled. If the intervention fails, it remains as
a named optional ablation with its result documented; source history will not
be rewritten or reverted merely because the outcome is negative.

### Frozen selection and score gate

Action and coordinate temperatures stay fixed at the already frozen focused
values, `0.15` and `0.20`. Three strength settings will be compared using only
behavioral diagnostics on the predeclared calibration subset `ft09`, `lp85`,
`ls20`, and `sp80`, seeds 0 and 1, at exactly 40 actions per row:

| Candidate | Untried-action bonus | Unchanged-failure penalty |
| --- | ---: | ---: |
| mild | 0.25 | 0.50 |
| balanced | 0.50 | 1.00 |
| strong | 1.00 | 2.00 |

Eligibility requires zero failed rows, illegal actions, invalid coordinates,
or budget violations, plus matching same-seed replay and across-seed diversity.
The winner is selected without using score or level progress: maximize unique
observations, minimize consecutive observation repeats, then use higher
legal-normalized action entropy and lower policy time as fixed tie-breakers.
The chosen setting is frozen in a separate checked-in config before the full
score artifact is inspected.

The only score-bearing gate is then all 25 public games, seeds 0-2, at exactly
500 actions. Minimum success is both mean score greater than the frozen real
baseline `0.06475067` and more than two completed levels. The stronger target is
to exceed the matched random baseline mean `0.09756824` and its six completed
levels. No Kaggle submission is authorized by this experiment.

Current action: implement the configuration, state memory, standardized-logit
bias, per-observation click memory, turn provenance, and focused unit tests.
Next: run all fast checks, checkpoint and push; run the score-blind calibration,
freeze its winner, checkpoint and push; only then launch the full score gate.

### Implementation checkpoint — complete, calibration not yet run

The bounded intervention is implemented behind typed configuration and remains
disabled in every pre-existing config. The disabled path retains the frozen
sampler's original probability arithmetic, RNG calls, global click history,
actions, payloads, and selected-action probabilities; an explicit multi-turn
regression compares it with the legacy constructor.

When enabled, `LoopEscapeMemory` hashes the exact grid with 128-bit BLAKE2b,
attributes an unchanged outcome to the prior observation/action exactly once,
and emits the preregistered additive bias *after* legal graph logits are
standardized. A prior click coordinate enters the per-observation exclusion set
only after it is observed to fail; a click that changes the frame is not marked
as failed. Forced protocol resets are never counted as policy choices. All maps,
pending outcomes, graph state, standardizer state, and the seeded RNG reset at
the environment boundary.

Every enabled turn persists its state key, complete eight-slot bias vector,
attempt vector, unchanged-failure vector, selected bias/counts, prior-outcome
status, and whether the bias changed the graph argmax. The ordinary connectome
evaluator now copies this provenance into its immutable trace and summarizes
revisits, failures, and argmax changes.

A dedicated `flygi.loop-escape-calibration` runner preserves the historical
temperature-calibration schema. It fixes temperatures at `0.15/0.20`, accepts
only the three declared strength pairs, strips all score and level-progress
fields, applies the frozen lexicographic selection order, and writes every
turn's loop provenance. `make calibrate-loop-escape` is the reproducible entry
point.

Verification observed:

- `uv run pytest -q`: **228 passed** (200 before this intervention);
- ruff lint passed and all 98 checked files are formatted;
- a temporary 4-action end-to-end smoke covered all four calibration games and
  both seeds: 8/8 rows succeeded, the same-seed replay matched, seed diversity
  passed, and the one smoke candidate was eligible;
- a recursive JSON-key audit of that smoke artifact found no keys named
  `official`, `score`, `levels_completed`, or `final_levels_completed`;
- the smoke artifact is temporary under `/tmp` and is not an experimental
  result or a source of candidate selection.

Current action: review, commit, and push this verified implementation checkpoint.
Next: run the exact three-candidate, eight-row-per-candidate score-blind
calibration; inspect only the declared behavioral metrics; freeze the selected
strength in a separate signed config before any full score-bearing evaluation.

### Score-blind calibration result — mild frozen, no short-horizon improvement

The exact calibration ran from clean commit
`f5c2423c946a3c1583ee792a95782588a2d903e4`: four declared games, seeds 0 and
1, 40 actions, frozen focused temperatures, and the real signed graph. All
24/24 candidate rows succeeded with zero illegal actions, invalid coordinates,
or budget violations. Every candidate passed same-seed replay and across-seed
diversity. A recursive artifact audit found zero keys named `official`, `score`,
`levels_completed`, or `final_levels_completed`.

| Candidate | Mean unique obs. | Mean consecutive repeats | Legal-normalized entropy | Median policy ms | Rank |
| --- | ---: | ---: | ---: | ---: | ---: |
| **mild (0.25 / 0.50)** | **28.000** | **12.375** | **0.11344597** | 136.46 | **1** |
| balanced (0.50 / 1.00) | 28.000 | 12.375 | 0.11344214 | **135.91** | 2 |
| strong (1.00 / 2.00) | 28.000 | 12.375 | 0.11343802 | 136.01 | 3 |

The result is weaker than the rank alone suggests. All three strength settings
produced identical action/payload traces on all eight matched rows: zero
differing turns out of 320 in every pairwise comparison. Each recorded 103
unchanged prior choices, 103 revisit decisions, 103 state-conditioned click
explorations, and **zero graph-argmax changes**. The frozen third criterion
therefore selected mild on an entropy difference of only `3.83e-06` over
balanced.

Relative to the earlier focused no-loop calibration on the identical games,
seeds, and budget, mild was slightly worse descriptively: 28.000 versus 28.125
mean unique observations and 12.375 versus 12.250 mean consecutive repeats.
The calibration therefore provides **no evidence of a short-horizon behavioral
improvement**. It does establish that the implementation is safe and that the
three declared strengths are behaviorally indistinguishable over 40 actions.
The predeclared procedure still freezes mild; the 500-action score gate is the
finite longer-horizon test, not a presumed win.

The ignored immutable artifact is
`results/loop_escape_calibration/20260922T045245.693168Z-6cb9eb2696.json`:
1,929,105 bytes, SHA-256
`8526ff343ad2ec02b69b716112afa8fa9e7103a3f34fda1368646727165490e1`.
Its reviewed tracked index is
`results/manifests/loop_escape_calibration_20260922.json`.

The selected candidate is frozen in
`configs/literal_rate_signed_loop_escape.yaml` with SHA-256
`63b50521c324ecd1c2d39e1498dd8113b9d6838731ea7f31b3fb8a94317e5c7c`.
A config-diff test proves it shares the signed baseline's data, graph, dynamics,
encoder, state policy, groups, temperatures, and every decoder field except the
three declared loop-escape enable/strength values.

Current action: checkpoint and push the calibration result, reviewed index, and
frozen config. Next: run exactly 25 games by seeds 0-2 at 500 actions from that
checkpoint, then compare mean score and completed levels against the frozen
real baseline (`0.06475067`, 2 levels) and random (`0.09756824`, 6 levels).

## 2026-09-22 — Correction: action budget IS a score lever, and the plan to exploit it

### A wrong conclusion, corrected

The 2026-09-22 sweep entry records "the action budget is not the binding
constraint" on the basis of an `sp80` rerun at 2,000 actions. That test was run
on the one game the frozen agent already solved within 80 actions, so it could
only ever show that `sp80` does not go *deeper*. It could not show whether a
larger budget unlocks *other* games, which is a different question and the one
that matters for the score.

Re-reading the completed 500-action artifacts answers it directly. Of the twelve
level completions recorded across all four conditions, **nine required more than
80 actions**:

| Condition | Game | Seed | Score | Within the deployed 80-action ceiling? |
| --- | --- | ---: | ---: | --- |
| real signed | `sp80` | 1 | 4.76190 | yes |
| real signed | `sp80` | 2 | 0.09440 | no |
| degree-preserving null | `sp80` | 0, 1, 2 | 0.07889, 0.28292, 0.22860 | no |
| no-graph bypass | `sp80` | 2 | 0.05651 | no |
| random legal | `sp80` | 0 | 0.81970 | no |
| random legal | `sp80` | 1, 2 | 1.56636, 4.76190 | yes |
| random legal | `r11l` | 0, 1, 2 | 0.02078, 0.08569, 0.06318 | no |

`r11l` was completed only beyond 80 actions, at 164, 191, and 333 actions. The
submitted configuration used an 80-action ceiling, so it could not have reached
`r11l` at all. **The deployed budget was leaving completions on the table.**

### What actually sets the score

The scorecard caps a game at `max_weights / total_weights * 100` over completed
levels. For a six-level game that makes the first level worth at most
`100/21 = 4.76190476`, and both the fly's 9-action completion and random's
14-action completion hit that cap exactly. Efficiency therefore stops mattering
once the cap is reached; **what matters is how many games yield a first level
at all.**

That reframes the objective. Five games at level one across a 25-game set gives
a mean of about `0.95`, roughly ten times the best result observed so far. The
levers, in order of expected effect:

1. a budget large enough to reach first levels that sit beyond 80 actions;
2. exploration good enough to find them in more games;
3. efficiency, which only matters until the per-game cap is hit.

### Compute headroom

Competition notebooks may run up to nine hours. At the observed 136-164 ms per
action, a 25-game hidden set at 800 actions per game is roughly 20,000 actions,
about 55 minutes. The 80-action ceiling was conservative by more than an order
of magnitude.

### Plan, in small shippable chunks

1. **Chunk A (this entry).** Record the correction and the revised objective.
2. **Chunk B (running).** Score-blind loop-escape calibration on the
   preregistered subset; freeze the winner.
3. **Chunk C.** Quick score probe: loop escape enabled, all 25 games, seed 0, at
   a raised budget. Compare against the frozen real baseline `0.06475067` and
   the matched random baseline `0.09756824`.
4. **Chunk D.** If the probe improves on the baseline, rebuild the Kaggle bundle
   with the raised budget and the frozen loop-escape setting, verify the
   preflight, and submit.

Detailed statistical hardening, the paired censored analysis, and the ARC
evaluation of the positive control are explicitly deferred to a later session by
the user's decision, in order to establish a leaderboard position early. They
remain in the backlog and are not cancelled.

### Standing caveat

Random legal still outscores the real graph at 500 actions (`0.09756824` against
`0.06475067`, six completed levels against two). Nothing in this plan claims a
connectome advantage; the objective here is the leaderboard number, and the
controls already on record continue to say the fly has not earned credit for it.

### Chunk B result — loop-escape calibration selected `mild`, but the strengths are indistinguishable

The preregistered score-blind calibration completed and selected `mild`
(exploration bonus 0.25, unchanged-failure penalty 0.50). All three candidates
were eligible.

The selection keys are worth recording because they qualify the result:

| Candidate | Unique observations | Consecutive repeats | Legal-normalized entropy |
| --- | ---: | ---: | ---: |
| mild | 28.0 | 12.375 | 0.11344597 |
| balanced | 28.0 | 12.375 | 0.11344214 |
| strong | 28.0 | 12.375 | 0.11343802 |

The two primary criteria are **identical to the last digit** across all three
strengths, and the tie was broken on the fourth decimal place of entropy. Over
the calibration subset at 40 actions per row, loop-escape strength made no
measurable behavioral difference. The selection procedure was followed exactly
and its winner is frozen, but it should not be read as evidence that the
intervention works. Whether the layer helps at all is a separate question from
which strength to use, and the calibration was not designed to answer it.

### Chunk C — raising the deployed budget, and the probe now running

`kaggle/agent/my_agent.py` had `MAX_ACTIONS = 80`, the ceiling that made `r11l`
unreachable. It is now **600**, with the measurement recorded inline. A larger
budget only adds completion opportunities: the scorecard caps a game by the
level weight completed, and a bigger ceiling never slows a completion that would
have happened earlier. At 136-164 ms per action, 25 games at 600 actions is
roughly 40 minutes against a nine-hour notebook limit.

Two probes are running to decide what to submit, both at all 25 public games,
seed 0, and exactly 600 actions:

- `probe600-loopescape` — the frozen `mild` loop-escape configuration;
- `probe600-plain` — the same frozen sampler with loop escape disabled.

Comparison baselines, both at 500 actions over seeds 0-2: frozen real
`0.06475067` with two completed levels, and matched random `0.09756824` with
six. The probes use one seed, so their means are noisier than those baselines
and will be read as a direction, not a measurement.

Verification before launch: `uv run pytest -q` → **229 passed**; ruff clean.

### Parallel work completed while the probes run

Three chunks were taken off the critical path so that submission is a single
command once the probes land.

**External readiness, read-only.** One submission exists (`56444435`, 2026-09-21
22:14 UTC, score 0.00); it is now 2026-09-22 05:25 UTC, so a fresh daily slot is
expected. The private dataset `megusalexandrus/flygi-malecns-runtime` is
published at 93,436,139 bytes. Its `config.yaml` is **byte-identical** to the
current `configs/literal_rate_signed.yaml` (both
`98f6d7b10acd6336af73daa2bae47933b721988758858a3cedd021991a803262`), which
determines the deployment path:

- if loop escape **loses**, no dataset version bump is required and only the
  notebook needs pushing;
- if loop escape **wins**, dataset version 2 is required, carrying
  `configs/literal_rate_signed_loop_escape.yaml`
  (`63b50521c324ecd1c2d39e1498dd8113b9d6838731ea7f31b3fb8a94317e5c7c`).

**Runtime projection.** The two concurrent probes are averaging about 1.72
minutes per 600-action row. At a pessimistic 300 ms per action on Kaggle, a
25-game hidden set costs about 75 minutes and 100 games about five hours,
against a nine-hour notebook limit. The 600-action budget is therefore safe for
any plausible hidden set.

**Wall-clock guard added.** The residual risk is that an unexpectedly large
hidden set overruns the notebook, which would lose both the run and the day's
submission quota. The adapter now carries a deadline, default seven hours and
overridable by `FLYGI_DEADLINE_SECONDS`. Past it every agent reports itself done,
which ends its game cleanly and **preserves levels already completed** instead of
failing the run. Three tests cover it, including one asserting the default is
below the nine-hour notebook limit and one asserting the deployed budget stays
at or above 500 so the `r11l` class of completion remains reachable.

**Both candidate bundles staged and locally preflighted.** Each reports
`available=True`, `MAX_ACTIONS=600`, a 25,200-second deadline, `K=4`, 166,700
nodes, and the correct loop-escape flag: disabled for `kaggle/dist/dataset`,
enabled at 0.25/0.50 for `kaggle/dist/dataset-loopescape`.

Verification: `uv run pytest -q` → **232 passed** (229 before the guard); ruff
clean; notebook rebuilt at 122,655 bytes with `MAX_ACTIONS = 600`, the deadline
guard, and the `FLYGI_PREFLIGHT` line all confirmed embedded.

Still blocked on the probes: choosing the configuration, and submitting.

## 2026-09-22 — Track B: trained readout on the frozen graph (the score multiplier)

### Why this, and why it is expected to be the biggest lever

The measured deficit is not randomness. Over the 500-action sweep the real
agent and random legal play had comparable action entropy, 1.618 against 1.776
bits, but very different reach: **213.3 mean unique observations against
335.2**. The fly's *choices* are worse at reaching new states, not merely less
random.

The simplest explanation is structural. The connectome is a function from fly
sensory input to fly motor output. FlyGI computes `h(f(g(ARC)))` where `g`, the
encoder, is a seeded random projection of a one-hot ARC grid, and `h`, the
decoder, splits 1,314 descending neurons into eight contiguous blocks by body-ID
order. Descending neurons encode commands for a body that is not present, and
nothing aligns those blocks with ARC's action slots. **Both `g` and `h` are
frozen and arbitrary, so the composition is arbitrary however good `f` is.**

Three further reasons the innate structure has not transferred, recorded so the
negative result is not over-read:

1. **The sensorimotor loop is cut.** Those circuits are tuned to actions that
   change sensory input in specific ways. Mapping a descending command to
   `ACTION3` breaks the contingency they were shaped by.
2. **The input statistics are wrong.** Photoreceptors expect luminance over a
   hexagonal eye with self-motion optic flow, not a projected one-hot grid.
3. **The physiology was replaced with something that cannot remember.** Spiking,
   adaptation, neuromodulation and heterogeneous time constants were replaced by
   one uniform leaky-tanh unit with a single global leak and gain. The measured
   memory half-life is 1-3 actions, while fly central-complex circuits hold
   heading for minutes. The machinery that would implement working memory was
   removed, and then the agent was asked to plan.

A genuine ceiling also exists -- ARC-AGI-3 requires inferring novel symbolic
rules, which flies do not do -- but points 1 to 3 dominate so completely that it
has not been tested. **The result so far shows the harness cannot express an
advantage, not that the connectome lacks one.**

Track B unfreezes exactly one thing: a small readout. The graph, encoder,
descending population and standardizer all stay frozen, so whatever the head
learns it learns *through* the connectome's dynamics.

### Chunk 1 complete — the head

`src/flygi/decoding/trained_head.py` with eight tests. The standardized
descending trace is compressed by a **fixed, seeded, never-trained** projection
to 48 dimensions, concatenated with the previous-action one-hot and the
legal-action mask, and mapped linearly to eight action logits.

| Property | Value |
| --- | ---: |
| Frozen readout size | 1,314 |
| Fixed compression | 48 |
| Head input dimension | 64 |
| **Trainable parameters** | **520** |

The budget is deliberately tiny. A head large enough to solve ARC by itself
would prove nothing, and the specification's section 19.3 warning is precisely
that a parameter-matched adapter bypassing the graph can match it. The identical
budget must therefore be given to the no-recurrent-graph bypass before any
fly-credit claim; that comparison is deferred, not cancelled.

Verification: `uv run pytest -q` → **240 passed**; ruff clean.

### Planned next chunks

2. A CEM trainer over the 520 parameters. Raw ARC score is far too sparse to
   learn from -- roughly one completion per 25 games -- so the declared training
   objective is dense: unique observations visited, plus a large bonus per
   completed level. Exploration is the measured deficit and random legal play,
   which explores most, also completes most.
3. Train on public games with parallel candidate evaluation, then freeze the
   winning parameters into a checked-in artifact.
4. Evaluate the trained head at 600 actions against the frozen real baseline
   `0.06475067` and the matched random baseline `0.09756824`, then package and
   submit if it improves.

### Declared limitation, fixed before any result is seen

Training on public games and evaluating on the hidden set is legitimate for the
leaderboard and is the specification's "public-ARC development" regime. It is
**not** evidence of zero-shot generality, and it will not be described as such.

### Chunk C result — loop escape wins, and unlocks a game nothing had solved

Both 600-action probes passed their engineering gate with 25/25 rows.

| Probe | Mean score | Levels | Mean unique observations | Game solved |
| --- | ---: | ---: | ---: | --- |
| `probe600-loopescape` | **0.190476** | 1 | **280.3** | **`cd82`** |
| `probe600-plain` | 0.000000 | 0 | 234.4 | none |

Loop escape wins on both the dense behavioral measure and the score, raising
unique observations by about 20%. More importantly it completed the first level
of **`cd82`**, a game no condition had ever completed in any previous run: all
prior progress across every condition was confined to `sp80` and `r11l`.

Two cautions attach to this. It is a single seed over 25 rows, so the means are
noisy; and the plain condition's 0.000000 is worse than its own three-seed
500-action baseline of `0.06475067`, which is consistent with the known fact
that `sp80` does not complete at seed 0. The comparison is therefore directional
rather than decisive. It is nonetheless the best evidence available, it points
the same way on two independent measures, and the new-game completion is not
something noise readily produces.

Earlier this session the calibration was recorded as showing loop-escape
*strength* made no measurable difference. That remains true and is not in
conflict: the calibration compared three enabled strengths against each other
over 40 actions, never enabled against disabled. This probe is the first test of
whether the layer helps at all, and it indicates that it does.

**Decision: the submission candidate is loop escape enabled at 600 actions.**
That requires Kaggle dataset version 2, because the deployed `config.yaml` lives
in the dataset and must become
`configs/literal_rate_signed_loop_escape.yaml`
(`63b50521c324ecd1c2d39e1498dd8113b9d6838731ea7f31b3fb8a94317e5c7c`). That
bundle is already staged and locally preflighted at
`kaggle/dist/dataset-loopescape`.

### Submission status

Not submitted. A competition submission spends the single daily slot and is an
outward-facing action on the account owner's behalf; passing local gates confers
no standing permission. Everything is staged so that authorization is the only
remaining step. Track B training continues in the meantime and would target a
later slot.

## 2026-09-22 — Score campaign: target 2x per submission

### Direction set by the user

Every submission must be worth its daily slot: a minimum of 2x the previous
score, improving fairly and without per-game hardcoding or public-set
overfitting dressed up as generality. The trajectory being aimed at is roughly
0.2 -> 0.4 -> 0.8 -> 1.6 -> 3.2 -> 6.4 -> above 10.0 within a week. Checkpoint
and push at every step so the work can be resumed by anyone at any point.

### What sets the score, restated as an operating rule

The scorecard caps each game at `completed_level_weight / total_weight * 100`.
A first level in a six-level game is worth `100/21 = 4.76190476`, and a mean is
taken across games. On a 25-game set that makes **each additional game reaching
level one worth about +0.19 of mean score**. The current best local result,
`0.190476`, is exactly one such game.

The 2x ladder therefore translates directly into games solved: 1 -> 2 -> 4 -> 8
-> 17, or fewer games solved more deeply. Deeper levels are worth much more
(level 2 of six carries weight 2 of 21, level 3 carries 3), so depth becomes the
only route past roughly 4.0.

### Honest assessment of today's options

Full CEM training of the 520-parameter head will not converge today. At roughly
four minutes per candidate evaluation it needs on the order of a thousand
evaluations, which is an overnight job, not an afternoon one. It remains the
largest multiplier and is scheduled next.

Today's highest-expected-value lever is the one already demonstrated twice:
**budget plus exploration strength**. `r11l` was only ever completed between 164
and 333 actions, and `cd82` appeared only at 600. Each unlock is worth about
+0.19.

### In progress — loop-escape strength sweep at 800 actions

Three matched runs over all 25 public games, seed 0, 800-action ceiling:

| Config | Exploration bonus | Unchanged-failure penalty |
| --- | ---: | ---: |
| `literal_rate_signed_loop_escape` (frozen `mild`) | 0.25 | 0.50 |
| `literal_rate_signed_loop_balanced` | 0.50 | 1.00 |
| `literal_rate_signed_loop_strong` | 1.00 | 2.00 |

800 was chosen as the submission-safe ceiling: at a pessimistic 300 ms per
action it costs about 100 minutes for 25 hidden games and about 6.7 hours for
100, which stays inside the seven-hour wall-clock guard so that no game is cut
off before it starts.

The earlier strength calibration found no measurable difference, but it compared
strengths over only 40 actions per row. The `cd82` unlock at 600 actions shows
the layer matters at realistic budgets, so strength is worth retesting there.

**Selection rule, fixed before results are seen:** choose the highest mean
public score; break ties on games reaching level one, then on mean unique
observations. This is public-set model selection. It is standard practice and is
the specification's "public-ARC development" regime, and it will be labelled as
such rather than presented as zero-shot generality.

### Next

1. Pick the winning strength, package it with the 800-action ceiling, verify the
   Kaggle preflight, and spend today's submission on it.
2. Start CEM training of the 520-parameter head overnight for tomorrow's slot.

### Track B chunk 2 — the head is wired into the live policy

`LiteralActionMap.decide` gained one optional `logits_override` seam. When a
trained head is present it supplies the eight action scores; everything
downstream is untouched and still applies in exactly the declared order: legal
masking, the loop-escape bias, temperature sampling, and the seeded per-policy
RNG. When unused, behaviour is byte-identical to before, which the existing
suite confirms.

`ConnectomePolicy` and `build_connectome_policy` now accept an optional trained
head. `describe()` reports it and switches `trainable_parameters` from 0 to the
head's count, so no result artifact can silently claim zero trainable parameters
while a trained head is active.

Two causal tests were added, mirroring the ones that pin the graph itself:
the trained head must change the action sequence relative to the untrained
policy, and it must never select an action outside the legal mask.

Verification: `uv run pytest -q` → **242 passed**; ruff clean.

### Track B chunk 3 — the CEM trainer, with a built-in honesty check

`scripts/train_head.py` trains the 520-parameter head by cross-entropy method
while the graph, encoder, descending population and standardizer stay frozen.
Workers load the graph once each rather than once per candidate, and a failed
candidate returns negative infinity instead of killing the run.

**The objective is dense, by necessity.** Raw ARC score cannot train anything:
the real agent completed two levels across 75 rows of the 500-action sweep. The
declared objective is

    mean over rows of ( unique_observations + level_bonus * levels_completed )

with `level_bonus` defaulting to 500. Unique-observation count is the measured
deficit -- 213.3 for the real agent against random legal play's 335.2 -- and the
condition that explores most also completes most levels, so it is a defensible
proxy that keeps real progress dominant whenever it occurs.

**Trace ablation is built into the run.** After the final generation the winning
parameters are re-evaluated with the descending trace zeroed, through a proper
`ablate_trace` flag on the policy rather than a monkey-patched attribute. If the
objective barely drops, the head has learned to ignore the connectome and the
result is an interface result, not a connectome result. That number is recorded
in the artifact next to the winning objective so it cannot be quietly omitted. A
test pins the flag's behaviour.

### Two declared limitations, recorded before any training result

1. This trains on public games. It is the specification's "public-ARC
   development" regime, legitimate for a leaderboard entry, and it is **not**
   evidence of zero-shot generality.
2. The no-recurrent-graph bypass must receive the identical head, budget and
   trainer before any claim that the connectome deserves credit for a trained
   result. Deferred, not cancelled.

Verification: `uv run pytest -q` → **243 passed**; ruff clean.

### Schedule reality, stated plainly

Three-way concurrent evaluation was running at roughly one row per twenty
minutes, which would not finish today. Two of the three strength arms were
stopped -- the earlier calibration had already shown strength makes no
measurable difference -- and the freed capacity was redirected to the lever that
is actually proven: budget. Two runs are in flight, `mild` at 800 actions and
`mild` at 1600 actions, both over all 25 games at seed 0. Whichever scores
higher becomes today's submission candidate.

CEM training runs after those finish, since both compete for the same
memory bandwidth.

## 2026-09-22 — Anatomical audit: the fly's learning circuit is present, and we deleted its reward system

### Question asked

Can the connectome's actual modules -- sensing, learning, navigation -- be used
for the task instead of arbitrary mappings, and could the fly form and refine a
latent world model through interaction?

This was answered by measurement against the compiled runtimes, not by argument.

### The modules are present and annotated

| Structure | Count | Role |
| --- | ---: | --- |
| Kenyon cells (`class=Kenyon_Cell`) | 4,064 | sparse high-dimensional expansion |
| MBONs (`class=MBON`) | 97 | learned valence readout |
| Dopaminergic `PAM`/`PPL`/`PPM` | 354 (350 confirmed dopamine) | teaching signal |
| Ellipsoid-body ring `ER*` | 282 | visual/contextual input to the compass |
| Compass `EPG`/`PEN`/`PEG` | 110 | ring-attractor heading state |
| Motion detectors `T4`/`T5` | 13,585 | elementary motion |
| Lobula columnar `LC`/`LPLC` | 4,670 | feature and looming detection |

### The circuits are genuinely wired

Measured on the signed runtime unless noted, as `W[post, pre]` submatrices:

| Pathway | Edges | Density |
| --- | ---: | ---: |
| Kenyon cells -> MBON | 61,210 | 0.1553 |
| ER ring -> compass | 13,760 | 0.4436 |
| compass -> compass (ring attractor) | 4,503 | 0.3721 |
| T4/T5 -> LC/LPLC | 54,515 | 0.0009 |
| MBON -> dopaminergic (value loop) | 2,618 | 0.0762 |
| MBON -> descending | 409 | 0.0032 |

The mushroom-body readout and the central-complex ring attractor are both dense
and intact. These are not labels; they are working subgraphs.

### The finding that matters: we deleted the fly's reward system

| Pathway | Unsigned runtime | **Signed runtime (submitted)** |
| --- | ---: | ---: |
| dopaminergic -> Kenyon cells | **129,132 edges**, weight sum 567.93 | **0** |
| dopaminergic -> MBON | 3,195 edges, weight sum 3.62 | **0** |

`modulator_treatment: zero` assigns sign 0 to monoaminergic neurons, which
deletes every one of their outgoing edges. 350 of the 354 PAM/PPL/PPM neurons
are dopaminergic, so the signed graph -- **the configuration actually
submitted** -- has the entire dopaminergic pathway removed, including the
single largest input to the mushroom body at 129,132 edges.

In Drosophila, reinforcement learning happens at Kenyon-cell-to-MBON synapses
under dopaminergic gating. FlyGI submitted a fly with its reward machinery
surgically removed and then observed that it did not learn. That treatment was
declared and recorded from the start, and it was defensible for a *frozen*
model where modulators have no dynamics to modulate. It is indefensible for any
experiment about learning.

### One genuine anatomical constraint

`LC`/`LPLC` -> Kenyon cells is **20 edges**, essentially nothing, and
photoreceptor -> `T4`/`T5` is zero directly because that pathway runs through
lamina and medulla. The adult *Drosophila* mushroom body is overwhelmingly
**olfactory**; it receives very little visual input. There is therefore no
strong biological route from an ARC image into the learning circuit, and any
visual-to-MB injection is an interface choice rather than something the fly
does. The honest visual route into persistent state is the ring-neuron pathway
into the central complex, which is dense.

### What a fly world model would and would not be

Supported by the anatomy:

- the central complex maintains a genuine persistent latent state -- a
  ring-attractor bump encoding heading, updated by self-motion and vision, with
  fan-shaped-body vector memory for path integration;
- the mushroom body is a three-layer learning system: a sparse high-dimensional
  code, a linear valence readout, and a dopaminergic teaching signal, with
  plasticity at a specific, known synapse.

Not supported: compositional symbolic model building. The fly's latent state is
low-dimensional and domain-shaped, for orientation, place and stimulus valence.
Flies do goal-directed navigation and associative learning; they do not do
program induction, which is what ARC-AGI-3 ultimately asks for.

### Proposed direction

Replace the 520-parameter arbitrary head with the fly's own learning circuit:

1. compile a runtime that **preserves modulators** instead of deleting them;
2. apply reward-modulated plasticity **only at Kenyon-cell-to-MBON synapses**,
   gated by dopaminergic activity, which is where fly plasticity actually
   occurs;
3. derive the reward from ARC progress and inject it into the dopaminergic
   population;
4. read MBONs for valence and the central complex for persistent state, instead
   of eight body-ID-ordered descending blocks.

This is Track C, but anatomically grounded rather than generic, and it remains
falsifiable: the same plasticity can be applied to a mushroom body that has been
rewired while degree is preserved, and to the no-recurrent-graph bypass.

### Cost, stated plainly

This is a larger change than the current score campaign and will not produce a
submission today. It is recorded here as the highest-value scientific direction,
not as a substitute for the in-flight budget runs.

## 2026-09-22 — PLAN: the plastic mushroom body (anatomically grounded Track C)

### Where this stands, in one place

**Done.**

- FlyGI runs the complete 166,700-neuron signed MaleCNS graph in every ARC
  decision with zero trainable parameters, passes its engineering gate on all 25
  public games, and holds a scored leaderboard entry (submission `56444435`,
  public score 0.00, rank 3212 of 3215).
- Controls exist and are measured: three directed degree-preserving nulls, an
  interface-matched no-recurrent-graph bypass, a matched random reservoir, and a
  validated positive control that retains roughly 400x the real graph's state.
- The real graph separates from its degree-preserving nulls by 3.59x in spectral
  radius. That structural difference has produced **no** ARC advantage.
- Score levers found by measurement: the 80-action ceiling could not reach games
  needing 164-333 actions, and a loop-escape layer unlocked `cd82`, a game no
  condition had ever completed. Both are in the current candidate.
- A 520-parameter trained head (Track B) is implemented, wired into the live
  policy, and covered by causal tests, with a CEM trainer that includes a
  trace-ablation honesty check. It has **not** been trained.
- **The audit that changed the plan:** `modulator_treatment: zero` deleted every
  dopaminergic edge -- 129,132 into Kenyon cells and 3,195 into MBONs. The
  submitted fly had no reward system, and we then observed that it did not
  learn.

**Doing now.** Building the fly's own learning circuit, described below.

**Next, in order.** Finish the in-flight budget runs and spend today's
submission on the better of them; train the Track B head overnight as a
comparison arm; then evaluate the plastic mushroom body against it.

### Why the mushroom body instead of a bigger trained head

Track B's head is 520 arbitrary parameters bolted onto an arbitrary readout. The
mushroom body is a three-layer learning system the fly already has, and the
measurements confirm it is intact: 4,064 Kenyon cells giving a sparse
high-dimensional expansion, 61,210 Kenyon-cell-to-MBON edges at density 0.155
forming a learned valence readout, 354 dopaminergic neurons supplying a teaching
signal, and a 2,618-edge MBON-to-dopaminergic recurrent value loop.

Plasticity in *Drosophila* occurs specifically at Kenyon-cell-to-MBON synapses
and is gated by dopaminergic activity, with dopamine **depressing** the synapses
active at the time. That is established neuroscience, not a modeling invention,
and it gives roughly 61,000 plastic weights in the biologically correct place
rather than 520 in an invented one.

### The build, in five stages

1. **`flygi.plasticity.mushroom_body`** -- resolve Kenyon cells, MBONs and
   dopaminergic neurons from node metadata; extract the Kenyon-cell-to-MBON
   submatrix as the plastic block; implement a bounded three-factor rule;
   expose MBON activity. Unit-tested on synthetic graphs.
2. **Declared configuration** -- learning rate, decay, weight bounds, reward
   scale and the reward definition, all typed and validated, disabled by default
   so every existing config and result is untouched.
3. **Policy integration** -- compute reward from ARC progress each turn, drive
   the dopaminergic population with it, update the plastic block, and let the
   change reach behaviour through the existing MBON-to-descending pathway.
   Causal tests: plasticity must change the action sequence, and must not when
   the reward is identically zero.
4. **A runtime that preserves modulators** -- a new compiled asset with
   `modulator_treatment: positive` so the 129,132 dopaminergic edges exist. The
   sign is an acknowledged approximation: dopamine's real effect is to gate
   plasticity, not to drive, and the rule uses dopaminergic *activity* rather
   than its synaptic sign.
5. **Evaluation** -- the plastic agent against the frozen agent on identical
   games, seeds and budget, then against the preregistered controls.

### Falsifiability, fixed before any result

A plastic mushroom body that improves the score proves nothing on its own. The
same plasticity, learning rate and reward must be applied to:

- a mushroom body rewired with degree preserved, keeping Kenyon-cell and MBON
  counts and degrees but destroying which cell contacts which;
- the no-recurrent-graph bypass.

If a degree-preserving rewire of the mushroom body learns equally well, the
result is about having 61,000 plastic synapses, not about the fly's wiring.

### The constraint that shapes the interface

Lobula-columnar input to Kenyon cells is **20 edges**. The adult mushroom body
is overwhelmingly olfactory and barely sees. There is therefore no biological
visual route into the learning circuit, and any image-to-Kenyon-cell injection
is a declared interface choice rather than something the fly does. The dense
visual route into persistent state is the ring neurons into the central complex,
which is why the central complex remains the honest place to look for a latent
world-model state later.

### What this is not

The fly's latent state is low-dimensional and domain-shaped, for orientation,
place and stimulus valence. It supports associative learning and goal-directed
navigation, not the compositional program induction ARC ultimately rewards. The
expectation is a measurable improvement in adaptation, not a solved benchmark.

### Stage 1 complete — and it demonstrates the deletion directly

`flygi.plasticity.mushroom_body` implements the three-factor rule with eleven
tests. Running it against both compiled runtimes settles the audit empirically:

| Runtime | Plastic KC->MBON edges | DAN->MBON edges | Mean gate | **Weight change after one rewarded update** |
| --- | ---: | ---: | ---: | ---: |
| Signed (**the configuration submitted**) | 61,210 | **0** | 0.0 | **0.000000** |
| Unsigned (modulators retained) | 61,210 | 3,195 | 1.859e-04 | 0.002782 |

The 61,210 plastic synapses are present in both. In the submitted configuration
the teaching signal that gates them does not exist, so a rewarded update changes
**exactly nothing**. The mushroom body was physically incapable of learning, and
no amount of reward would have changed that.

One update costs 1.1 ms against roughly 136 ms for a single graph step, so
plasticity is essentially free relative to the dynamics.

### What the rule does, and the guarantees around it

`dw[mbon, kc] = -rate * gate[mbon] * kc_activity[kc]`, with dopamine
**depressing** the synapses active when it arrives, which is the established
direction of the effect rather than a convenience. `gate` comes from the real
dopaminergic-to-MBON adjacency, so which MBON a teaching signal reaches is
decided by the connectome; a test removes dopaminergic input from half the MBONs
and asserts only the innervated half learns.

Tested guarantees:

- everything outside the Kenyon-cell-to-MBON block stays byte-identical;
- all three factors are required -- zero reward, zero Kenyon activity or zero
  dopamine each produce no change at all;
- weights stay finite, keep their original sign, and stay inside a declared band
  under a learning rate of 5.0 and a reward of 1000 sustained for 50 updates, so
  plasticity can modulate the connectome but never invert or erase it;
- decay relaxes toward the frozen baseline, and `reset` restores it exactly.

### Stages 2 and 3 complete — declared config and a live plastic loop

**Configuration.** `PlasticityConfig` is typed and validated, and **disabled in
every pre-existing config**, so every recorded result still describes a fully
frozen graph. A test asserts that: `literal_rate_plastic_mb.yaml` is the only
config with plasticity enabled, and every other one both disables it and keeps
`frozen_graph: true`.

The two halves of the invariant are now paired in both directions. Enabling
plasticity with `frozen_graph: true` is rejected, because a config must not
claim a frozen graph while modifying its weights; and `frozen_graph: false`
without plasticity is rejected too, because an unfrozen graph with no declared
learning rule is just an unguarded graph. Both rejections are tested.

**Weights writable, topology never.** `ScipyRateNetwork` gained
`allow_plasticity`. When set, the weight array becomes writable; `indices` and
`indptr` stay read-only unconditionally. A learning rule may change how strong a
connection is, never which neurons are connected. A plastic policy also gets a
private writable copy of the connectivity, so the shared hash-verified bundle
stays frozen for every other condition in the process.

**Reward, from the protocol only.** `observation_change` is the dense term --
normalized changed-cell count, answering "did my action do anything" -- and it
targets the measured deficit directly, since the agent repeats states far more
than chance. `level_progress` is sparse and unambiguous. The plastic config uses
`both`. Neither term reads hidden scoring state; both come from what the frame
already reports.

**Tested in the closed loop.** Four integration tests beyond the eleven unit
tests:

- plasticity changes the action sequence relative to an identical policy with
  learning rate zero, so learning genuinely reaches behaviour;
- a repeated identical frame earns zero reward and produces exactly zero weight
  change, so the dense reward cannot leak signal from nowhere;
- `reset_state` restores the baseline graph byte-for-byte at an environment
  boundary;
- the interface description reports the plasticity site and settings, so no
  result artifact can hide that the graph was not frozen.

Verification: `uv run pytest -q` → **260 passed**; ruff clean.
