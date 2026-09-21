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

## Next steps

Gate 2 is passed and its result is negative: the real graph did not beat a
parameter-matched bypass on ARC. The ordering below follows from that, and from
two design defects Gate 2 exposed.

1. **Fix the sample-size defect.** All 25 games gave identical traces across all
   five seeds, because the policy is deterministic and these environments are
   deterministic given the game. The effective n is 25, not 125. Either give the
   policy a declared stochastic component (for example sampling from masked
   logits at a declared temperature, seeded per run) or stop reporting seeds as
   replicates. This must be decided and recorded before any confirmatory
   analysis, not after seeing more results.
2. **Fix the exploration defect.** The connectome agent explores *less* than
   chance: 52.8 unique observations against 64.2, and 23.7 consecutive repeats
   against 13.6. A deterministic argmax falls into loops. Temperature sampling
   would address both defects at once. Whatever is chosen must apply identically
   to every graph condition.
3. **Add a positive control.** Every null is built to be no better than the fly.
   With real, bypass and null all near zero, the design cannot separate "the
   biological graph confers no advantage" from "this interface and operating
   point cannot express an advantage any graph could confer." A reservoir
   deliberately tuned to the edge of chaos at matched node and edge count would
   separate them. This is the single most informative missing condition.
4. **Complete the operating-point sweep.** `K=4` was chosen on anatomical
   grounds; `leak=0.3` and `gain=0.9` are unchanged from the original `K=2`
   declaration and have never been searched. Sweep `(K, leak, gain)` on the
   dynamical diagnostics, apply the winner identically to every condition.
5. **Reconsider the primary endpoint.** Gate 0 chance is 2 of 125 rows; Gate 2
   real is 5 of 125, all one game. A paired test on public-set RHAE at this base
   rate cannot detect anything. Promote the specification's section 13.3
   behavioral diagnostics to co-primary, and record the change before inspecting
   further results.
6. **Scale the controls.** Evaluate all three existing nulls rather than one,
   build the remaining seven, and add the weight shuffle, the sign shuffle within
   transmitter strata, and the matched generic reservoir.
7. **Kaggle submission.** The offline dataset is staged and verified and the
   adapter runs the connectome. Publishing the dataset and spending a competition
   submission are outward-facing actions that require explicit authorization each
   time; passing the local gates does not confer standing permission.
8. **Track B.** A small trained readout on a frozen graph is where the
   specification expects any real signal. It must be compared against the same
   parameter-matched bypass, which has now beaten the fly once already.

### Open design questions

- **The primary endpoint is near-degenerate.** See step 5.
- **There is no positive control.** See step 3.
- **The structural finding has no behavioral consequence yet.** The real graph
  separates cleanly from its degree-preserving nulls on spectral radius (3.59x),
  pathway depth, readout dimensionality and retention. None of that produced an
  ARC advantage. Either the interface cannot exploit those properties, or they
  are not useful for this task. Distinguishing those two is what the positive
  control is for.
