# FlyGI result report template

> Replace every bracketed field from immutable result artifacts. Do not remove
> failed seeds, zero scores, timeouts, or null graphs.

## Identity and scope

- Result ID: `[unique immutable directory name]`
- Run type: `[exploratory or confirmatory]`
- UTC start/end: `[timestamps]`
- Code revision and dirty-tree state: `[revision/status]`
- Environment: `[Python, OS, CPU/GPU, package lock hash]`

## Data and graph provenance

- MaleCNS release: `[release]`
- Source manifest SHA-256: `[digest]`
- Preprocessing/config SHA-256: `[digest]`
- Runtime graph SHA-256: `[digest]`
- Measured node, edge, and contact totals: `[from manifest]`
- Graph conditions and null seeds: `[complete list]`

## Protocol

- Games/task families: `[list or manifest]`
- Evaluation seeds: `[all seeds]`
- Training data and update budget: `[none or exact description]`
- Dynamics, internal steps, and reset policy: `[config references]`
- Encoder/readout and trainable parameter counts: `[per condition]`
- Primary endpoint and predeclared test: `[definition]`

## Outcomes

| Condition | Runs | RHAE mean | Levels completed | Failures/timeouts | Median ms/action | Peak RAM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `[condition]` | `[n]` | `[value]` | `[n]` | `[n]` | `[value]` | `[value]` |

Include the full machine-readable table by `(game, seed, training run,
condition)`. Report paired mean and median differences, game-level bootstrap
95% intervals, the within-pair permutation test, standardized effect size, and
multiple-testing treatment for secondary endpoints.

## Diagnostics and checks

- Null invariant reports: `[paths/hashes]`
- Invalid actions before masking: `[counts]`
- Unique states, loop rate, action entropy, and frame-change sensitivity:
  `[artifact references]`
- Determinism and graph-causal-path checks: `[results]`

## Interpretation

State the narrow result before speculation. A positive result concerns only the
chosen interface, dynamics, and null distribution. A zero result does not imply
that a biological fly lacks intelligence. Routing through the graph, beating a
generic unmatched random graph, or selecting the best seed is not evidence for
an evolved-topology advantage.

## Deviations and failures

List every departure from the preregistered config, why it occurred, when it was
decided, and whether the affected analysis is now exploratory. Preserve logs
and partial outputs rather than silently dropping them.
