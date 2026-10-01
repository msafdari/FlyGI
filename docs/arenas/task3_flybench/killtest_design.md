# Task 3 (FlyBench) — adapter kill test registration

Registered 2026-10-01, after the user authorized third-party execution
in this container and BEFORE any adapter code. Per the program rules:
trivial alternative named, bars frozen, a failed kill test ends this
step with a recorded verdict.

## Context measured first (this container, 2026-10-01)

- `pip install -e .` of the clone (v0.2.1, commit 3052ce5) works;
  `flybench toy` builds the bundled 3,792-neuron / 45,343-edge synthetic
  connectome; `flybench run -c toy` completes in ~2 min with the
  REFERENCE simulator: **score 0.93, graded 0.94, 24/30 tasks pass**,
  6 skipped (nerve-cord readouts absent on toy; flygym/flyvis extras
  not installed — the embodied/closed-loop track is out of scope here).
- Contract read from source: `Simulator(connectome, params)` with
  `run(duration_ms, stimuli) -> SimResult` (spike times float32 ms +
  neuron ids int32); `flybench verify-adapter module:Class -c toy`
  names every defect and exits 1 on any; `--simulator module:Class`
  runs the suite on a custom simulator.

## Premise under test

Our fidelity-class-2 engine (`flygi.dynamics.spiking.SpikingNetwork`,
UNMODIFIED — modifying it for the benchmark would invalidate the point)
can sit behind flybench's simulator contract with declared plumbing
only, pass `verify-adapter`, and reproduce the toy's canonical core
reflexes that the reference LIF passes. This is the premise under
everything else Task 3 could become (first MaleCNS rows, the MB
comparison): if our engine cannot run their tasks at contract level on
the toy, nothing downstream exists.

## Trivial alternative (named)

Their reference `LIFSimulator` on the same toy: measured 0.93 / 0.94 /
24/30 above. The adapter is not required to beat it — the reference IS
the benchmark's own model; the kill test asks whether our engine
functions as a peer behind the same contract.

## Declared plumbing (all of it; anything beyond this list is a bug)

1. Weight bridge: their `connectome.W` is CSR rows=pre, signed synapse
   counts; our engine wants `W[post, pre]` -> transpose. Unit bridge,
   DERIVED (unit analysis, not tuning): their per-spike synaptic kick
   `w = w_syn_mv * gain * count` enters their membrane as
   `integral g/tau_m dt = w * tau_syn / tau_m`; our kick
   `D = w_scale * count` enters as `integral i dt = D * tau_syn`.
   Equating: **w_scale = w_syn_mv * gain / tau_m_ms**. One formula,
   fixed before any run.
2. Constants: the Shiu 2024 set their `LIFParams` carries (v_rest =
   v_reset = -52 mV, v_th = -45 mV, tau_m = 20 ms, tau_syn = 5 ms,
   t_ref = 2.2 ms) mapped onto our `TypeParams` default — both models
   descend from the same published constants, so this is a shared
   anchor, not a fit. dt = 0.5 ms (our engine default; theirs 0.1 —
   declared difference). Our engine has no axonal delay line (their
   1.8 ms); effective one-step delay, declared difference.
3. Stimulus bridge: their stimuli are Poisson FORCED spikes. The
   adapter samples the same Poisson events (np RNG seeded from
   `params.seed`, re-seeded every `run` -> determinism) and injects a
   one-step suprathreshold current pulse
   `(v_th - v_rest) / dt + 1.0` onto the event's neurons, so the spike
   happens through the engine's own threshold (and refractory is
   honoured exactly as their forced path honours it). Ramps and
   rate-series use their own `rate_at`/`rates_at` methods.
4. Readout: spikes collected from the engine's spiking-node outputs
   per step into their `SimResult`. The graded mask is EMPTY on the
   toy (no APL/CT1-class labels there); on real connectomes it is the
   distinctive feature and gets its own declaration later.
5. `capabilities = {"can_silence"}`: silencing arrives as zeroed
   outgoing rows in the connectome we are handed; our construction
   reads W from that connectome, so it holds structurally.

## PASS / KILL (frozen now)

PASS iff BOTH:

1. `flybench verify-adapter flygi_flybench_adapter:FlyGIAdapter -c toy`
   exits 0 (zero defects), with the engine unmodified.
2. The five canonical core reflexes the reference passes on toy —
   silence-in/silence-out, sugar -> proboscis, bitter suppresses sugar,
   looming -> giant fiber, bitter alone does not extend — all PASS
   under our adapter with the DERIVED w_scale. Declared fallback, the
   same freedom the reference's own rows use ("gain swept; not fitted
   to any task", 1 free parameter): if the derived point fails, one
   global gain sweep over {0.3, 0.5, 0.7, 1.0, 1.5} x derived, taking
   the passing point nearest 1.0x; it counts as 1 free parameter in
   any later submission and both results are recorded.

The full-suite toy score under our adapter is reported against the
reference's 0.93 as CONTEXT, not a bar. KILL if either bar fails:
recorded verdict = our model form does not function behind their
contract within the declared freedom; Task 3 then either pivots to
running our PARAMETER VALUES through their reference simulator (a
different, smaller claim) or ends — the user's call, with the verdict
on the table.

## What this test does NOT decide

MaleCNS rows (the fetch is neuprint-gated, local-only — AF-2), the
Litwin-Kumar-MB-vs-PN-broadcast comparison, substrate reconciliation
(AF-1), the spike-conversion question for our graded operating points
(AF-4), and anything submission-shaped (verified badge, PR). Each is
its own registered step, reached only on PASS.

## Registration and single commands

Hypothesis: EXPERIMENTS.yaml `H-FLYGI-FLYBENCH-ADAPTER` (same commit).
Adapter: `scripts/arenas/flybench_adapter.py` (plumbing only).

    PYTHONPATH=src:scripts/arenas flybench verify-adapter \
        flygi_flybench_adapter:FlyGIAdapter -c toy
    PYTHONPATH=src:scripts/arenas flybench run -c toy \
        --simulator flygi_flybench_adapter:FlyGIAdapter
