# Task 3 (FlyBench) — due-diligence delta check, 2026-10-01

Opened per the program's operating rule 1, immediately after Task 2
closed cloud-side. Base: the 2026-09-30 ten-agent survey
(due_diligence_20260930.md, `flybench`) and the AF-* register rows.
Everything below is MEASURED in this session unless marked otherwise.

## Measured deltas against the survey

1. **flybench is NOT on PyPI** (pypi.org/pypi/flybench -> 404; `pip
   index versions flybench` -> no distribution). The survey's "pip
   install" path is really `pip install -e .` from a clone of
   github.com/brandoncho369/flybench (the repo's own README agrees).
   Survey row corrected.
2. **Repo cloned read-only in-cloud** (public-repo git read lane):
   commit `3052ce5fa9ab8cc0a9e101e8cd8f5bb520a80ff5`, package version
   0.2.1. The project moved since the survey: terminal-aware LIF (RFCs
   M1/M1b, no free parameters) is now a second verified mechanism row
   (FlyWire graded 0.655 -> 0.711, MaleCNS 0.660 -> 0.700, MB sparse on
   both brains), a flyvis-fronted eye task (task 32) showed the
   reference model's loom escape was being hand-fed, and a closed-loop
   embodied escape task (36) exists that nobody passes. Our planned
   angle (Litwin-Kumar-calibrated MB vs their PN-broadcast finding)
   remains unclaimed territory.
3. **neuprint.janelia.org is still HTTP 000 from this container**
   (re-measured; AF-2 stands INVALIDATED in-cloud). The MaleCNS fetch
   path (`flybench fetch-neuprint`) is local-only regardless of
   anything else.
4. **NEW BLOCKER, measured: this environment denies installing or
   executing third-party code** (the `pip install -e .` of the cloned
   package was refused by the container's execution policy). So even
   the no-fetch toy suite (`flybench toy` + `flybench run -c toy`)
   cannot be verified in-cloud. Everything executable about Task 3 is
   therefore user-side (or needs the user to explicitly authorize
   third-party execution here, which remains their call, not ours to
   work around). Reading the cloned source is fine and is how the
   facts below were obtained.

## Interface facts read from source (grounds the adapter design)

- Contract (`flybench/adapter.py`): an adapter is anything callable as
  `Simulator(connectome, params)` returning `run(duration_ms, stimuli)
  -> SimResult`. `connectome.W` is CSR, rows = presynaptic, signed
  synapse counts; `params` is `LIFParams` (gain, seed, dt; extras in
  `params.extra`). Runs must be seed-deterministic and reset state per
  call. Optional `capabilities` frozenset (currently just
  `can_silence`); tasks skip, never fail, adapters lacking a required
  capability. `flybench verify-adapter module:Class` is the
  maintainer's pre-merge check.
- `Stimulus` is a Poisson drive on named neurons (constant, ramp, or a
  per-neuron rate time series from their sensory front ends).
  `SimResult` is SPIKES: spike times (ms float32) + neuron indices
  (int32, connectome row order). CONSEQUENCE for us, recorded as the
  key adapter assumption-to-be: our class-2 validated MB operating
  point uses GRADED APL units and threshold-calibrated KCs; mapping
  our dynamics onto their spike-only result type needs a declared
  conversion, labelled at the code site when built (new AF-4).
- Open division (`flybench/evaluate.py`): `n_free_parameters`
  (required, 0 if literature values) and `fit_data` (<= 300 chars;
  parameters fitted ON benchmark tasks are ineligible). Matches AF-3's
  plan: our calibrations were on our own protocols, and the
  declaration text should say exactly that.

## Consequence for the task plan

The cloud container can prepare (adapter code, config, declaration
text, runbook) but can verify nothing that imports flybench. Per the
kill-test-first rule, the first executable step — `flybench toy` +
`verify-adapter` against our stack — is the user's local run, exactly
like Task 2's measurement. Next session step: decide with the user
whether Task 3 proceeds as prepare-here/run-there (the Task 2 pattern)
before any adapter code is written.
