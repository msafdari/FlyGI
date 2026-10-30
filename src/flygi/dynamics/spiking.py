"""Fidelity-class-2 dynamics: leaky integrate-and-fire on a subcircuit.

The class-1 verdict (H-MODULE-VERDICT) measured that the frozen uniform
tanh rate model reproduces none of the core physiological codes at any
operating point, and located the missing physics: temporal heterogeneity.
This engine supplies it: current-based LIF with PER-NODE membrane and
synaptic time constants, thresholds, refractory periods, and a graded
(non-spiking) unit mask -- resolved per cell type through a provenance-
labelled parameter table. The model form follows the whole-brain LIF
precedent (Shiu et al. 2024) extended with per-type time constants (the
element Lappalainen et al. 2024 showed recovers direction selectivity on
connectome wiring).

Dynamics (per timestep dt, all arrays per-node, W[post, pre] signed
synapse counts from flygi.connectome.subcircuit):

    i_syn <- i_syn + dt/tau_syn * (-i_syn) + w_scale * (W @ out)
    v     <- v + dt/tau_m * (-(v - v_rest)) + dt * i_syn + dt * i_ext
    spike where v >= v_thresh and not refractory; then v <- v_reset
    out   = spike (0/1) for spiking nodes;
    out   = relu(v - v_rest) * graded_gain for graded nodes (APL, CT1:
            ESTABLISHED non-spiking interneurons)

Optional, DEFAULT-OFF spike-frequency adaptation (H-FLYGI-FLYBENCH-SFA,
docs/arenas/task10_menu/killtest_design.md section 6; mechanism form
ESTABLISHED: Benda & Herz 2003 via FlyBench adaptive_lif.py -- one
adaptation state per neuron):

    on spike: sfa_a += sfa_b          # sfa_b in the engine's CURRENT units
    sfa_a    <- sfa_a * exp(-dt/sfa_tau_ms)
    total_input <- i_syn + i_ext - sfa_a   # adaptation opposes the drive

With sfa_b = 0.0 (the default) every adaptation branch is skipped, so the
engine's arithmetic is BIT-IDENTICAL to the pre-extension behavior
(asserted by tests/test_flybench_mechanisms.py against a frozen copy of
the pre-extension step).

Every default below is labelled; ASSUMED values carry sweep ranges in the
benchmark scripts, never silent trust.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray
from scipy import sparse


class SpikingError(RuntimeError):
    pass


@dataclass(frozen=True)
class TypeParams:
    """Parameters for one cell-type pattern, with provenance."""

    tau_m_ms: float
    v_thresh: float
    provenance: str  # ESTABLISHED (source) or ASSUMED (range)
    tau_syn_ms: float = 5.0
    v_rest: float = 0.0
    v_reset: float = 0.0
    refractory_ms: float = 2.2
    graded: bool = False
    graded_gain: float = 1.0


@dataclass
class ParameterTable:
    """Ordered pattern -> TypeParams mapping; first match wins."""

    default: TypeParams
    rules: list[tuple[str, TypeParams]] = field(default_factory=list)

    def resolve(self, types: NDArray[np.str_]) -> dict[str, NDArray[np.floating] | NDArray[np.bool_]]:
        count = types.shape[0]
        out = {
            "tau_m_ms": np.full(count, self.default.tau_m_ms, dtype=np.float32),
            "tau_syn_ms": np.full(count, self.default.tau_syn_ms, dtype=np.float32),
            "v_rest": np.full(count, self.default.v_rest, dtype=np.float32),
            "v_thresh": np.full(count, self.default.v_thresh, dtype=np.float32),
            "v_reset": np.full(count, self.default.v_reset, dtype=np.float32),
            "refractory_ms": np.full(count, self.default.refractory_ms, dtype=np.float32),
            "graded": np.zeros(count, dtype=bool),
            "graded_gain": np.full(count, self.default.graded_gain, dtype=np.float32),
        }
        if self.default.graded:
            out["graded"][:] = True
        assigned = np.zeros(count, dtype=bool)
        for pattern, params in self.rules:
            mask = np.array(
                [fnmatch.fnmatchcase(t, pattern) for t in types.astype("U")]
            ) & ~assigned
            if not mask.any():
                continue
            assigned |= mask
            out["tau_m_ms"][mask] = params.tau_m_ms
            out["tau_syn_ms"][mask] = params.tau_syn_ms
            out["v_rest"][mask] = params.v_rest
            out["v_thresh"][mask] = params.v_thresh
            out["v_reset"][mask] = params.v_reset
            out["refractory_ms"][mask] = params.refractory_ms
            out["graded"][mask] = params.graded
            out["graded_gain"][mask] = params.graded_gain
        return out

    def provenance_report(self) -> list[dict[str, str]]:
        rows = [{"pattern": "<default>", "provenance": self.default.provenance}]
        rows += [{"pattern": p, "provenance": tp.provenance} for p, tp in self.rules]
        return rows


class SpikingNetwork:
    """Vectorized current-based LIF over a signed CSR subcircuit."""

    def __init__(
        self,
        matrix: sparse.csr_matrix,
        types: NDArray[np.str_],
        table: ParameterTable,
        *,
        dt_ms: float = 0.5,
        w_scale: float = 1.0,
        seed: int = 0,
        sfa_b: float = 0.0,
        sfa_tau_ms: float = 200.0,
    ) -> None:
        if matrix.shape[0] != matrix.shape[1] or matrix.shape[0] != types.shape[0]:
            raise SpikingError("matrix and types must agree on node count")
        if dt_ms <= 0:
            raise SpikingError("dt_ms must be positive")
        if sfa_tau_ms <= 0:
            raise SpikingError("sfa_tau_ms must be positive")
        self.matrix = sparse.csr_matrix(matrix, dtype=np.float32)
        self.node_count = int(matrix.shape[0])
        self.dt = float(dt_ms)
        self.w_scale = float(w_scale)
        # Spike-frequency adaptation, DEFAULT OFF (sfa_b = 0.0). The per-spike
        # increment sfa_b is in the engine's current units; callers derive it
        # from a published mV value via the registered unit bridge
        # sfa_b = b_mv / tau_m_ms (AF-10, flygi_flybench_adapter.py).
        # ASSUMPTION (AF-10, scheme choice): the adaptation state decays
        # EXPONENTIALLY (a *= exp(-dt/tau_a)), matching FlyBench's
        # AdaptiveLIFSimulator, while this engine's synaptic current decays by
        # the Euler factor (1 - dt/tau_syn). A declared scheme difference, not
        # a fit; wrong only if the two decay schemes diverge at dt = 0.5 ms,
        # which the Benda-Herz closed-form gate bounds.
        self.sfa_b = float(sfa_b)
        self.sfa_tau_ms = float(sfa_tau_ms)
        self._sfa_decay = np.float32(np.exp(-self.dt / self.sfa_tau_ms))
        self.params = table.resolve(types)
        self._refractory_steps = np.maximum(
            np.round(self.params["refractory_ms"] / self.dt).astype(np.int32), 0
        )
        self._rng = np.random.default_rng(seed)
        self.reset()

    def reset(self) -> None:
        self.v = self.params["v_rest"].astype(np.float32).copy()
        self.i_syn = np.zeros(self.node_count, dtype=np.float32)
        self._refractory_left = np.zeros(self.node_count, dtype=np.int32)
        self.last_output = np.zeros(self.node_count, dtype=np.float32)
        # adaptation state exists even when off (zeros; introspectable)
        self.sfa_a = np.zeros(self.node_count, dtype=np.float32)

    def step(self, external: NDArray[np.floating] | None = None) -> NDArray[np.float32]:
        """Advance one dt; returns the per-node output (spikes / graded rate)."""

        p = self.params
        drive = self.w_scale * (self.matrix @ self.last_output)
        self.i_syn += (self.dt / p["tau_syn_ms"]) * (-self.i_syn) + drive
        total_input = self.i_syn if external is None else self.i_syn + external
        if self.sfa_b != 0.0:
            # SFA (default off): the pre-decay adaptation state opposes the
            # drive this step, exactly as FlyBench's AdaptiveLIFSimulator uses
            # its pre-decay `a` in the membrane update. Guarded so sfa_b = 0
            # leaves the arithmetic bit-identical to the unextended engine.
            total_input = total_input - self.sfa_a
        refractory = self._refractory_left > 0
        dv = (self.dt / p["tau_m_ms"]) * (-(self.v - p["v_rest"])) + self.dt * total_input
        self.v = np.where(refractory, self.v, self.v + dv).astype(np.float32)
        self._refractory_left = np.maximum(self._refractory_left - 1, 0)
        if self.sfa_b != 0.0:
            self.sfa_a *= self._sfa_decay   # exponential decay (AF-10 scheme)

        graded = p["graded"]
        spiking = ~graded
        fired = spiking & (self.v >= p["v_thresh"]) & ~refractory
        output = np.zeros(self.node_count, dtype=np.float32)
        output[fired] = 1.0
        output[graded] = (
            np.maximum(self.v[graded] - p["v_rest"][graded], 0.0)
            * p["graded_gain"][graded]
        )
        self.v[fired] = p["v_reset"][fired]
        self._refractory_left[fired] = self._refractory_steps[fired]
        if self.sfa_b != 0.0:
            self.sfa_a[fired] += self.sfa_b   # a += b on spike (their rule)
        self.last_output = output
        return output

    def run(
        self,
        steps: int,
        external_fn: Callable[[int], NDArray[np.floating] | None] | None = None,
        record: NDArray[np.integer] | None = None,
    ) -> dict[str, Any]:
        """Run ``steps`` timesteps; returns spike counts and optional traces."""

        spike_counts = np.zeros(self.node_count, dtype=np.int64)
        traces = (
            np.zeros((steps, len(record)), dtype=np.float32)
            if record is not None
            else None
        )
        for step_index in range(steps):
            external = external_fn(step_index) if external_fn is not None else None
            output = self.step(external)
            spike_counts += (output > 0).astype(np.int64) * (
                ~self.params["graded"]
            ).astype(np.int64)
            if traces is not None:
                traces[step_index] = output[record]
        result: dict[str, Any] = {
            "spike_counts": spike_counts,
            "duration_ms": steps * self.dt,
            "rate_hz": spike_counts / (steps * self.dt / 1000.0),
        }
        if traces is not None:
            result["traces"] = traces
        return result
