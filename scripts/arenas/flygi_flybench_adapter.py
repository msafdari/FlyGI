"""FlyGI -> flybench simulator adapter (Task 3 kill test).

PREREGISTRATION: docs/arenas/task3_flybench/killtest_design.md +
EXPERIMENTS.yaml H-FLYGI-FLYBENCH-ADAPTER (2026-10-01, frozen before
this file existed). This module is PLUMBING ONLY, and everything it
does is declared there:

  - flygi.dynamics.spiking.SpikingNetwork runs UNMODIFIED; this file
    may not alter the engine's dynamics in any way.
  - Weight bridge: flybench's connectome.W is CSR rows=pre, signed
    synapse counts; our engine wants W[post, pre] -> transpose. Unit
    bridge DERIVED (unit analysis, not tuning):
        w_scale = w_syn_mv * gain / tau_m_ms
    because their per-spike kick w = w_syn*gain*count enters the
    membrane as integral(g/tau_m)dt = w*tau_syn/tau_m, while ours
    D = w_scale*count enters as integral(i)dt = D*tau_syn.
  - Constants: the Shiu 2024 set carried by their LIFParams, mapped
    onto our TypeParams default (shared published anchor, not a fit).
    dt = 0.5 ms (our engine default; theirs 0.1 -- declared
    difference). No axonal delay line in our engine (theirs 1.8 ms);
    effective one-step delay, declared difference.
  - Stimulus bridge: their stimuli are Poisson FORCED spikes; the
    adapter samples the same events (np RNG from params.seed, fresh
    per run -> determinism) and injects a one-step current pulse
    (v_th - v_rest)/dt + 1.0 so the spike happens through the engine's
    own threshold (refractory honoured as their forced path honours
    it). DECLARED LIMIT, stated in the registration: a driven neuron
    held far below rest by inhibition may not cross; their forced path
    would fire it regardless.
  - capabilities = {"can_silence"}: silencing arrives as zeroed
    outgoing rows in the handed connectome; we read W from it, so it
    holds structurally.

Run (from the FlyGI repo root, flybench installed):
    PYTHONPATH=src:scripts/arenas flybench verify-adapter \
        flygi_flybench_adapter:FlyGIAdapter -c toy
    PYTHONPATH=src:scripts/arenas flybench run -c toy \
        --simulator flygi_flybench_adapter:FlyGIAdapter
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# flybench's CLI imports this module bare; make flygi importable too.
_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from flybench.sim import LIFParams, SimResult  # noqa: E402
from flygi.dynamics.spiking import (  # noqa: E402
    ParameterTable,
    SpikingNetwork,
    TypeParams,
)

DT_MS = 0.5   # our engine default; declared in the registration


class FlyGIAdapter:
    """flybench Simulator contract over the unmodified class-2 engine."""

    capabilities: frozenset = frozenset({"can_silence"})

    def __init__(self, connectome, params: LIFParams | None = None):
        self.c = connectome
        self.p = params or LIFParams()
        p = self.p
        # Declared unit bridge (registration): w_scale = w_syn*gain/tau_m.
        w_scale = p.w_syn_mv * p.gain / p.tau_m_ms
        table = ParameterTable(
            default=TypeParams(
                tau_m_ms=p.tau_m_ms,
                v_thresh=p.v_th_mv,
                provenance=(
                    "Shiu 2024 constants via flybench LIFParams "
                    "(shared published anchor; killtest_design.md)"
                ),
                tau_syn_ms=p.tau_syn_ms,
                v_rest=p.v_rest_mv,
                v_reset=p.v_reset_mv,
                refractory_ms=p.t_ref_ms,
                graded=False,
            ),
        )
        # The toy carries no APL/CT1-class labels, so the graded mask is
        # empty here by construction (declared); a uniform type vector
        # resolves everything to the default row.
        types = np.full(connectome.n, "neuron", dtype="U16")
        self.net = SpikingNetwork(
            connectome.W.T.tocsr(),
            types,
            table,
            dt_ms=DT_MS,
            w_scale=w_scale,
            seed=p.seed,
        )
        self._spiking = ~self.net.params["graded"]
        # One-step suprathreshold pulse (frozen formula, registration).
        self._pulse = (p.v_th_mv - p.v_rest_mv) / DT_MS + 1.0

    def run(self, duration_ms: float, stimuli=None) -> SimResult:
        net = self.net
        net.reset()
        rng = np.random.default_rng(self.p.seed)
        stimuli = stimuli or []
        n = self.c.n
        n_steps = int(round(duration_ms / DT_MS))
        per_ms = DT_MS / 1000.0
        stim = [
            (np.asarray(s.neurons, dtype=np.int32), s.rate_hz * per_ms,
             s.t_start_ms, s.t_end_ms, s)
            for s in stimuli
            if len(s.neurons)
        ]
        times: list[np.ndarray] = []
        ids: list[np.ndarray] = []
        external = np.zeros(n, dtype=np.float64)
        for k in range(n_steps):
            t_now = k * DT_MS          # window test at step start (as theirs)
            external[:] = 0.0
            any_event = False
            for neurons, prob, t0, t1, s in stim:
                if not (t0 <= t_now < t1):
                    continue
                if s.rate_series_hz is not None:
                    events = neurons[
                        rng.random(neurons.size) < s.rates_at(t_now) * per_ms
                    ]
                elif s.rate_end_hz is not None:
                    events = neurons[
                        rng.random(neurons.size) < s.rate_at(t_now) * per_ms
                    ]
                else:
                    events = neurons[rng.random(neurons.size) < prob]
                if events.size:
                    external[events] += self._pulse
                    any_event = True
            output = net.step(external if any_event else None)
            fired = np.flatnonzero((output > 0) & self._spiking)
            if fired.size:
                # spike timestamp = end of the step, as the reference stamps
                times.append(np.full(fired.size, (k + 1) * DT_MS,
                                     dtype=np.float32))
                ids.append(fired.astype(np.int32))
        return SimResult(
            spike_times_ms=(np.concatenate(times) if times
                            else np.empty(0, dtype=np.float32)),
            spike_neurons=(np.concatenate(ids) if ids
                           else np.empty(0, dtype=np.int32)),
            duration_ms=float(n_steps * DT_MS),
            n=n,
        )
