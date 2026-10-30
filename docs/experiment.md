# Experiment protocol

## Current scope (as of 2026-10-08)

By 2026-09-21 this repository had completed Milestones 0 through 3, and part
of Milestone 4:

1. exercise the official ARC-AGI-3-compatible random-agent path locally;
2. reproducibly fetch, inspect, and convert MaleCNS v1.0 into sparse runtime
   graphs, unsigned and heuristic-signed, with provenance manifests;
3. run the frozen full-graph leaky-rate equation through a deterministic SciPy
   CPU backend with a separate correctness, stability, and timing gate;
4. run a live closed loop from ARC frame to legal ARC action through the full
   166,700-neuron graph, with a nonlearned encoder and seeded stochastic
   decoder calibrated without score; and
5. generate seeded directed degree-preserving nulls and an interface-matched
   no-recurrent-graph bypass, and evaluate them on the public set.

Since then the measured record has moved (2026-09 to 2026-10): the Track B
trained head was built and run (520 parameters, CEM-trained; genuinely
connectome-dependent, with zero held-out generalization); the Track C
mushroom-body plasticity arms were built and run (the `mb-plastic` rows in
`LEAGUE.md`, null against the frozen control); and nine Kaggle competition
submissions were scored -- six 0.00s whose root cause was a construction
crash, so zero actions were ever played, then three COMPLETE runs at 0.15
(submissions 56620463, 56650224, 56683298). All three scored agents ran with
`neuronal_dynamics_active=false`; their only fly content was the compiled
static retinotopic eye map. See `docs/arenas/task1_arc_paper/factsheet.md`
and `docs/arenas/SYNTHESIS.md`.

Still not done: ten or more independently seeded directed
degree-preserving nulls for the confirmatory analysis (three are built and
evaluated). Done since this list was written: the weight and sign shuffles
(implemented, validated, run 2026-10 -- H-STAGEA-NULL-DECOMPOSITION,
`docs/controls.md`) and the reservoir ARC runs (both arms complete 2026-10,
measured FLAT -- see the harness-sensitivity boundary below).

The existence of configuration sections for encoders, decoders, controls, or
Kaggle packaging does not mean those milestones have been executed. Run the
repository's verification commands and inspect an actual result manifest before
making a completion claim.

Connectome-driven ARC results exist for the public set and are recorded in
`WORKLOG.md` with their immutable artifacts. Within the class-1
recurrent-dynamics program, no connectome-versus-control advantage was
measured: the real graph came out null against its degree-preserving rewires
and against the interface-matched bypass (`LEAGUE.md`). Two bounded
fly-positive results are measured: the compiled retinotopic eye map at 2.59x
the human action-cost baseline versus its scrambled-map twin at 11.59x
(scores 0.3064/0.3058 vs 0.1875), and `sg-bioeye-t4t5`, the league's only
HELPS verdict versus its scrambled control (+0.0717 [+0.005,+0.156],
p=0.070, recorded as borderline) -- an advantage attributable to its
retinotopic encoder versus the scrambled twin, not to a
connectome-versus-rewire comparison. The full arena-program record is in
`docs/arenas/SYNTHESIS.md`. A measured structural difference between the
real graph and its degree-preserving nulls is recorded in
`results/manifests/degree_preserving_comparison_20260921.json`; that is a
property of the graph's dynamics, not evidence that the property helps on ARC.

## Scientific question

The eventual experiment asks whether MaleCNS topology supports more useful
closed-loop computation on unfamiliar interactive tasks than rigorously matched
artificial graphs. The preregistered primary comparison is the real graph versus
multiple directed degree-preserving rewirings, holding the encoder, decoder,
dynamics, trainable parameter count, training data, action budget, search
budget, and random seeds fixed.

The proposed primary endpoint is the paired mean difference in public-set RHAE
across games and seeds, accompanied by level-completion rate because RHAE is
zero when no level is completed.

## Tracks

- **Track A — Literal Fly:** fixed mappings and dynamics; no ARC-specific
  training. This is the first full-agent target after ingestion and dynamics.
- **Track B — Frozen Fly Reservoir:** a frozen recurrent graph with a small,
  parameter-matched trainable interface. This is later work.
- **Track C — Plastic Fly:** constrained local plasticity. It is explicitly out
  of scope until the fixed and frozen controls are understood.

## Claim boundary

A positive controlled result would mean only that, under the chosen interface
and dynamics, MaleCNS structural features made some ARC-relevant computations
more accessible than in the selected nulls. It would not show that a fly
understands ARC, that the connectome is a complete brain emulation, that the
modeled units reproduce fly electrophysiology, or that a nonzero score is
general intelligence. Passing information through a graph is not evidence that
its biological organization caused performance.

Likewise, a zero result is informative engineering and does not imply that the
biological nervous system lacks intelligence.

**Measured harness-sensitivity boundary (2026-10, H-ARC-HARNESS-SENSITIVITY):
the long-memory positive-control reservoir also produced no score separation
on the full matched protocol (both decision CIs span zero; detection power
~ +0.1 score at 75 rows).** The class-1 ARC real-vs-null and real-vs-bypass
results in this document therefore carry the weakened reading: under this
interface, no tested graph — including a reservoir validated into the regime
reservoir computing recommends — moved official score, and the real wiring
also did not. They are not evidence that the harness could have registered a
graph advantage had one existed.

## Reproducibility rules

- Treat each result directory as immutable.
- Record configs, seeds, code revision, environment, graph and source hashes,
  action traces, timing, failures, and the result schema.
- Pair every graph condition on `(game, seed, training run)`.
- Never choose only the best seed or tune a mapping per game.
- Freeze the confirmatory configuration before inspecting final results.
