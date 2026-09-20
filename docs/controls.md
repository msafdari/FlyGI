# Experimental controls

Controls are the core scientific test, but their generation and full evaluation
belong to Milestone 4. Milestones 0-1 establish the graph representation and
manifest fields needed to make later comparisons auditable. No null graph or
biological advantage is claimed here.

| Condition | Must preserve or match | Question |
| --- | --- | --- |
| MaleCNS | Observed topology and configured weights | Target condition |
| Directed degree-preserving rewires | Per-node in/out degree and a declared weight assignment | Does higher-order topology matter? |
| Weight shuffle | Exact edge locations and global weight/sign multiset | Does weight placement matter? |
| Sign shuffle | Topology and magnitudes, stratified as declared | Does sign organization matter? |
| Generic sparse reservoir | Node/edge counts and weight distribution | Does almost any large reservoir work? |
| No reservoir | Interface dimensions and readout budget | Does recurrence contribute? |
| Random legal agent | ARC action affordances | Chance and submission baseline |

The confirmatory topology test requires at least ten independently seeded
directed degree-preserving nulls. Each must serialize its algorithm parameters,
seed, graph hash, rejection policy, and invariant checks. A single convenient
rewire is not a distribution.

All conditions must use identical sensory/readout node identities, dynamics,
normalization, encoder/readout dimensions, trainable parameter counts, training
data and update budgets, evaluation seeds, and ARC action budgets. Hyperparameter
search must be symmetric. The no-reservoir baseline receives a matched interface
and readout budget.

Required automated checks include exact directed in/out degree sequences for
the degree-preserving null, the exact weight multiset when promised, no
unintended loops or duplicate aggregated edges, preserved interface nodes, and
paired result rows for every `(game, seed, training run)`.

Only a comparison that survives the preregistered degree-preserving test can
support the narrow claim that higher-order MaleCNS structure helped under the
chosen model. Beating an unmatched random graph is insufficient.
