# Experiment protocol

## Current scope

This repository has completed Milestones 0 through 3, and part of Milestone 4:

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

Not done: weight and sign shuffles, a matched generic reservoir, ten or more
nulls for confirmatory analysis, any trained interface (Track B), plasticity
(Track C), and any competition submission.

The existence of configuration sections for encoders, decoders, controls, or
Kaggle packaging does not mean those milestones have been executed. Run the
repository's verification commands and inspect an actual result manifest before
making a completion claim.

Connectome-driven ARC results now exist for the public set and are recorded in
`WORKLOG.md` with their immutable artifacts. No leaderboard result exists, and
no biological advantage on ARC is claimed. A measured structural difference
between the real graph and its degree-preserving nulls is recorded in
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

## Reproducibility rules

- Treat each result directory as immutable.
- Record configs, seeds, code revision, environment, graph and source hashes,
  action traces, timing, failures, and the result schema.
- Pair every graph condition on `(game, seed, training run)`.
- Never choose only the best seed or tune a mapping per game.
- Freeze the confirmatory configuration before inspecting final results.
