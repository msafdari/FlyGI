# Local acceptance gates before competition submission

FlyGI does not spend ARC-AGI-3 submission quota merely because a notebook can
execute. The private Kaggle smoke validates packaging only. An official
competition run is deferred until the local gates below pass and the result is
checkpointed in `WORKLOG.md`.

## Gate 0 — evaluator and chance floor

Run the deterministic random-legal control on every cached public game with
evaluation seeds `0, 1, 2, 3, 4` and an exact budget of 80 environment actions
per game. This is 125 game-seed rows and at most 10,000 actions.

Run the gate with:

```bash
make baseline-local
```

Pass only when:

- all 125 rows are present in an immutable machine-readable result;
- there are no exceptions or timeouts;
- every active-state action is in the frame's legal-action mask, and `RESET` is
  used only in a protocol-required reset state;
- every `ACTION6` coordinate is an integer in `[0, 63]`;
- every run respects the declared action budget; and
- replaying a fixed game and seed produces the same action/payload trace.

A positive score is not required. This gate validates the evaluator and records
chance behavior; it is not a FlyGI or connectome result.

## Gate 1 — full-graph dynamics

Run the manual full-data gate with:

```bash
make benchmark-full-graph
```

The reviewed 2026-09-21 local run passed; its small tracked index is
`results/manifests/dynamics_gate1_20260921.json`. Re-run the gate after any
change to dynamics, graph assets, or the benchmark protocol.

Before the graph is connected to ARC decisions:

- execute one CPU update on the full 166,700-neuron graph with the declared
  shape, orientation, and dtype;
- reproduce the same CPU state for a fixed input, initial state, and seed;
- keep every activity value finite for 10,000 internal steps;
- show that distinct nonzero inputs produce distinguishable graph states and
  descending-neuron traces; and
- record cold-load time, median and p95 update time, and peak memory for
  `K = 1, 2, 4, 8` after warmup.

Select `K` under a fixed compute budget with headroom for the verified Kaggle
limits. A raw sparse matrix-vector timing is only a feasibility estimate and
does not satisfy this gate.

## Gate 2 — closed-loop literal FlyGI

Run with `scripts/evaluate_connectome.py`, which reuses the Gate 0 harness
unchanged and swaps only the policy, so matched `(game, seed)` rows compare
directly with the chance control.

Before packaging a connectome submission:

- prove the live causal path `frame -> encoder -> graph state ->
  descending-neuron trace -> logits -> legal action`;
- verify the declared persistence and reset policy;
- load and hash-check graph assets once, then propagate the graph on every
  active non-reset decision;
- show that a preregistered graph-output ablation changes at least one action in
  a fixed replay; and
- run all 25 public games with the same five seeds and exact 80-action budget,
  producing 125 complete rows with no exceptions, illegal actions, invalid
  coordinates, or missing timing and memory diagnostics.

Compare the full agent with the random control on identical `(game, seed)`
pairs. Report scores and level completions descriptively. Beating random is not
required for the first honest Track A submission, and doing so would not by
itself establish a biological-topology advantage.

## Gate 3 — offline Kaggle packaging

`scripts/package_kaggle_dataset.py` stages the compiled connectome, its config,
and an independent digest record, then verifies the staged copy loads and
hash-checks through the ordinary runtime loader with no network and no source
tables present. It uploads nothing.

Before spending a competition submission:

- the notebook must run with internet disabled and must not download MaleCNS,
  call neuPrint, or rebuild the graph during evaluation;
- assets must be loaded and hash-verified once per process, not once per game;
- the adapter must report which mode it is in, and must never silently fall
  back to the random policy while appearing to be a connectome run;
- `K` and every other deployment setting must be declared in the packaged
  config rather than inherited from a default; and
- timing and memory must be remeasured on the actual Kaggle runtime, because
  the local `K=4` cost of about 140 ms per action is machine-specific.

A competition submission spends quota and is an outward-facing action. It
requires explicit authorization each time; passing these gates does not confer
standing permission.
