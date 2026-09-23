# Experiment 000 — mushroom-body sanity checks

Experiment 000 is FlyGI's preflight for every later mushroom-body claim. It
asks whether a reproducibly extracted, whole-bilateral MaleCNS v1.0
PN→KC→MBON circuit, with measured APL feedback topology and explicitly assumed
rate dynamics/local plasticity, can learn elementary cue value—and whether the
native topology adds anything beyond conservative matched rewires.

The two claims are separate:

- `H000-MECH`: the declared circuit with reinforcement-gated local plasticity
  beats frozen, reward-shuffled, and graph-off controls.
- `H000-TOPO`: conditional on `H000-MECH`, native topology beats 39
  degree-exact, anatomically stratified joint PN→KC/KC→MBON rewires.

A mechanism pass with a topology tie supports a generic mushroom-body-like
learning mechanism, not superiority of exact MaleCNS wiring.

## Current status

The experiment is pre-implementation. The equations, task schedules, primary
endpoints, controls, null construction, inference, and kill tests are frozen in
[SPEC.md](SPEC.md). Four outcome-blind empirical gates remain:

1. recompute and lock the exact raw PN→KC support;
2. manually sign off the DAN/MBON compartments and 37-type MBON family registry;
3. measure null switchability and calibrate Curveball burn-in structurally;
4. pass the analytic kill battery and then the 16-world harness pilot.

No confirmatory result may be generated before those gates close.

## Files

- [SPEC.md](SPEC.md) — normative biological, mathematical, control, and
  statistical contract.
- [WORKLOG.md](WORKLOG.md) — durable experiment-local decisions, evidence,
  status, and ordered next work.

Generated graphs, schedules, traces, and result bundles stay outside normal Git
history. Only source, small manifests, schemas, hashes, tests, and aggregate
reports are committed.

## Workflow boundary

FlyARC remains Experiment 002 and is being advanced independently. Experiment
000 is developed additively on `codex/experiment-000`; it does not import or
generalize the ARC controller, encoder, decoder, dynamics, config, result, or
legacy MB-learning paths. Integration into the default branch waits for a
reconciled FlyARC closure point and compatibility goldens.
