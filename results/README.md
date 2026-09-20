# Results

No ARC score or biological advantage is reported by the Milestone 0-1
repository. This directory documents where later immutable experiment bundles
belong; generated bundles are ignored by Git by default.

Each run should use a unique directory such as a UTC timestamp plus a short
config hash. A command must refuse to overwrite an existing run. At minimum,
store:

- the resolved config, seed list, code revision, and environment lock/hash;
- source, graph, interface, and model manifests with SHA-256 values;
- full per-game/per-seed outcomes, action traces, and failures;
- timing, peak memory, and invalid-action diagnostics;
- null-invariant and parameter-count checks; and
- a report based on [`docs/results_template.md`](../docs/results_template.md).

Do not commit large traces or binaries to normal Git history. Publish them as a
versioned release asset or dataset and commit only a small index with immutable
URLs and hashes.

The minimum pre-submission checks are specified in
[`docs/local_acceptance_gates.md`](../docs/local_acceptance_gates.md). Random
control results validate the evaluator and establish a chance floor; they are
not connectome-performance results.

The current strict-offline chance-control runner is invoked with
`make baseline-local`. Its JSON bundles are generated beneath
`results/random_baseline/` and are intentionally ignored by Git.

Small reviewed result indexes under `results/manifests/` are tracked. They
record the local artifact path, digest, clean code revision, gate outcome, and
summary without committing multi-megabyte action traces.
