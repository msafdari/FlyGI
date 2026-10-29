# Experimental controls

Controls are the core scientific test. The directed degree-preserving null and
the no-recurrent-graph bypass are implemented and have been run; the generic
matched reservoir and the positive control are implemented and compiled with
ARC runs pending; weight and sign shuffles are not implemented. Within the
class-1 recurrent-dynamics program this document covers, no
connectome-versus-control advantage was measured: the real graph came out
null against its degree-preserving rewires and against the interface-matched
bypass (`LEAGUE.md`). Two bounded fly-positive results are measured: the
compiled static retinotopic eye map at 2.59x the human action-cost baseline
versus its scrambled-map twin at 11.59x, and `sg-bioeye-t4t5`, the league's
only HELPS versus its scrambled control (+0.0717 [+0.005,+0.156], p=0.070,
recorded as borderline). For the full program record -- six consecutive
rewire-over-real results, with the surviving positives being an anatomy
index, a mechanism, a parameter set, and a transformation-over-input -- see
`docs/arenas/SYNTHESIS.md`.

## Implementation status

| Condition | Status |
| --- | --- |
| MaleCNS, unsigned and heuristic-signed | Compiled, hash-verified, evaluated |
| Directed degree-preserving rewires | Implemented in `flygi/connectome/nulls.py`; three seeds built and evaluated |
| No recurrent graph (bypass) | Implemented; interface-matched and evaluated |
| Random legal agent | Implemented; Gate 0 chance floor recorded |
| Generic matched sparse reservoir | Implemented and compiled; ARC run pending |
| Positive control (edge of chaos) | Implemented, compiled and validated; ARC run pending |
| Weight shuffle | Implemented + validated in-cloud 2026-10-23 (flygi.connectome.nulls.weight_shuffle, within-presynaptic PRIMARY + global variant; dissociation gates in tests/test_stagea_nulls2.py). Stage-A application registered (H-STAGEA-NULL-DECOMPOSITION), pending the local run |
| Sign shuffle within transmitter strata | Implemented + validated in-cloud 2026-10-23 (flygi.connectome.nulls.sign_shuffle, per-presynaptic-neuron, Dale-consistent; mixed-sign columns rejected). Stage-A application registered, pending the local run; ARC-scope application deferred (recorded, killtest_design.md section 7) |

## The implemented degree-preserving null

Batched directed double-edge swaps: `a -> b` and `c -> d` become `a -> d` and
`c -> b`, which leaves `out_degree(a)`, `out_degree(c)`, `in_degree(b)` and
`in_degree(d)` unchanged. Proposals that are degenerate, that would create a
self-edge under a config forbidding them, that would duplicate an existing
aggregated edge, or that collide with another accepted swap in the same batch
are rejected.

The declared weight rule is that each weight travels with its presynaptic slot,
so the global weight multiset and every node's outgoing weight multiset are
preserved exactly by the rewiring. The real condition's normalization is then
re-applied, because moving edges between postsynaptic rows changes those rows'
incoming sums.

Each null is written as a self-contained, hash-verified runtime bundle whose
`node_metadata.npz` and `groups.npz` are copied from the source runtime, so
declared sensory and readout node identities are shared with the real graph by
construction rather than by convention.

At ten swaps per edge, the measured nulls retain 0.51% of the real edge set.

## The implemented bypass

The no-recurrent-graph control keeps the entire interface and removes only the
graph. Its projection targets the descending population directly, with
`connections_per_neuron` rescaled so total interface nonzeros match the real
condition, and the recurrent gain is zero. A policy refuses to be constructed
as ablated with nonzero gain, and a test asserts its readout is not silent: a
bypass whose readout is always zero measures nothing. An earlier version of
this control simply zeroed the persistent state, which made it a do-nothing
agent rather than a matched comparison.

## The positive control

Every condition above is built to be no better than the fly. That is what makes
a set of near-zero results uninterpretable: it cannot separate "the biological
graph confers no advantage" from "this interface and operating point cannot
express an advantage that *any* graph could confer."

The positive control exists to break that tie. It is a reservoir deliberately
placed in the regime reservoir computing says is good, so it *should* outperform
if the harness can register an advantage at all.

Placing it there takes two changes, not one. Scaling to a spectral radius near
one is not sufficient, because incoming-L1 normalization of non-negative weights
already produces a row-stochastic matrix whose radius is exactly one for any
topology; such a matrix is an averaging operator that diffuses information. The
positive control therefore also assigns symmetric random signs, which is the
standard echo-state construction. An early version omitted the signs, targeted
0.95, and landed *below* its own null; its own test caught this.

Because its purpose is to differ, it departs from the declared normalization and
sign mode. Both departures are recorded in its statistics as
`departs_from_declared_normalization` and `departs_from_declared_sign_mode`, and
it must never be reported as a matched null.

Validated at the deployed operating point:

| Condition | rho | Memory half-life | Retained after 12 silent actions |
| --- | ---: | ---: | ---: |
| Real signed fly | 0.8289 | 1 action | 0.00019 |
| Matched random reservoir | 0.1608 | 1 action | 0.00000 |
| Positive control | 0.9924 | 3 actions | 0.07686 |

**ARC outcome, measured 2026-10 (H-ARC-HARNESS-SENSITIVITY, run record
in WORKLOG; the registered certification test): FLAT.** On the full
eff- protocol (25 games x seeds 0-2 x 500 actions, matched pairs,
clustered bootstrap), the positive control scored 0.0137 vs the real
graph's 0.0648 (delta -0.0511, CI [-0.153, +0.000]) and vs the
degree-preserving null's 0.0079 (delta +0.0058, CI [+0.000, +0.017]);
it did not separate from its own rho-0.16 matched-random twin
(0.0320; CI [-0.055, +0.000]). Both decision CIs span zero. The tie
this section describes is therefore resolved in the UNINFORMATIVE
direction, and the sentence above is hereby weakened to its measured
form: the class-1 ARC near-zero results read as "under this interface
and operating point, no tested graph — including a reservoir
validated into the known-good long-memory regime — moved official
score; the real wiring also did not." They are statements about this
interface's tested graphs, never a measured absence of advantage
attributable to the fly wiring specifically. Certification power
floor: the comparator CI half-widths (±0.07-0.19 score at 75 rows)
mean only advantages of roughly >= +0.1 score were detectable. This
downgrade does NOT touch the arena-program rewire results (each arena
harness carried its own measured positive control) or the structural
separations.

## The full declared control set

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
