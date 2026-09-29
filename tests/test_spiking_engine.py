"""Class-2 engine correctness: LIF analytics, refractory, graded units, table."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from flygi.dynamics.spiking import ParameterTable, SpikingNetwork, TypeParams


def _table(**overrides) -> ParameterTable:
    base = dict(tau_m_ms=20.0, v_thresh=1.0, provenance="ASSUMED (test)")
    base.update(overrides)
    return ParameterTable(default=TypeParams(**base))


def _lonely(table: ParameterTable, dt: float = 0.1) -> SpikingNetwork:
    matrix = sparse.csr_matrix((1, 1), dtype=np.float32)
    return SpikingNetwork(matrix, np.array(["X"]), table, dt_ms=dt)


class TestSingleNeuron:
    def test_constant_current_reaches_threshold_at_analytic_time(self) -> None:
        # v(t) = I*tau*(1 - exp(-t/tau)); threshold 1.0 with I=0.1, tau=20
        # -> t* = -tau*ln(1 - v_th/(I*tau)) = -20*ln(0.5) = 13.86 ms.
        network = _lonely(_table(), dt=0.01)
        current = np.array([0.1], dtype=np.float32)
        fired_at = None
        for step in range(4000):
            if network.step(current)[0] > 0:
                fired_at = step * 0.01
                break
        assert fired_at is not None
        assert fired_at == pytest.approx(13.86, abs=0.5)

    def test_subthreshold_never_fires(self) -> None:
        # I*tau = 0.08*10 = 0.8 < threshold 1.0: silence forever.
        network = _lonely(_table(tau_m_ms=10.0), dt=0.05)
        current = np.array([0.08], dtype=np.float32)
        outputs = [network.step(current)[0] for _ in range(4000)]
        assert max(outputs) == 0.0

    def test_refractory_blocks_immediate_refire(self) -> None:
        table = _table(tau_m_ms=5.0)
        network = _lonely(table, dt=0.1)
        strong = np.array([10.0], dtype=np.float32)
        fire_steps = [i for i in range(60) if network.step(strong)[0] > 0]
        gaps = np.diff(fire_steps)
        # refractory 2.2 ms at dt 0.1 = 22 steps of silence minimum.
        assert gaps.min() >= 22

    def test_reset_after_spike(self) -> None:
        network = _lonely(_table(), dt=0.1)
        strong = np.array([5.0], dtype=np.float32)
        while network.step(strong)[0] == 0:
            pass
        assert network.v[0] == pytest.approx(0.0)


class TestSynapsesAndSigns:
    def test_inhibitory_edge_lowers_target_voltage(self) -> None:
        # node0 -> node1 with weight -3 (signed count); drive node0 to spike.
        matrix = sparse.csr_matrix(
            (np.array([-3.0], dtype=np.float32), (np.array([1]), np.array([0]))),
            shape=(2, 2),
        )
        network = SpikingNetwork(matrix, np.array(["A", "B"]), _table(), dt_ms=0.1)
        external = np.array([5.0, 0.0], dtype=np.float32)
        for _ in range(400):
            network.step(external)
        assert network.v[1] < 0.0  # pushed below rest by inhibition

    def test_excitatory_edge_raises_target_and_can_fire_it(self) -> None:
        matrix = sparse.csr_matrix(
            (np.array([30.0], dtype=np.float32), (np.array([1]), np.array([0]))),
            shape=(2, 2),
        )
        network = SpikingNetwork(matrix, np.array(["A", "B"]), _table(), dt_ms=0.1)
        external = np.array([5.0, 0.0], dtype=np.float32)
        result = network.run(600, lambda _: external)
        assert result["spike_counts"][1] > 0


class TestGradedUnits:
    def test_graded_unit_never_spikes_and_outputs_rectified_rate(self) -> None:
        table = ParameterTable(
            default=TypeParams(tau_m_ms=20.0, v_thresh=1.0, provenance="ASSUMED"),
            rules=[
                (
                    "APL*",
                    TypeParams(
                        tau_m_ms=20.0,
                        v_thresh=1e9,
                        provenance="ESTABLISHED non-spiking (test)",
                        graded=True,
                        graded_gain=2.0,
                    ),
                )
            ],
        )
        matrix = sparse.csr_matrix((1, 1), dtype=np.float32)
        network = SpikingNetwork(matrix, np.array(["APL_R"]), table, dt_ms=0.1)
        out = [network.step(np.array([0.5], dtype=np.float32))[0] for _ in range(200)]
        assert network.params["graded"][0]
        assert max(out) > 0.0
        assert (np.diff(out) >= -1e-6).all()  # smooth graded rise, no reset

    def test_first_match_wins_in_table(self) -> None:
        table = ParameterTable(
            default=TypeParams(tau_m_ms=20.0, v_thresh=1.0, provenance="d"),
            rules=[
                ("T4*", TypeParams(tau_m_ms=5.0, v_thresh=1.0, provenance="fast")),
                ("T4a", TypeParams(tau_m_ms=99.0, v_thresh=1.0, provenance="late")),
            ],
        )
        resolved = table.resolve(np.array(["T4a", "T5x", "KC"]))
        assert resolved["tau_m_ms"][0] == pytest.approx(5.0)  # T4* matched first
        assert resolved["tau_m_ms"][1] == pytest.approx(20.0)
        assert len(table.provenance_report()) == 3


class TestDeterminism:
    def test_same_inputs_same_run(self) -> None:
        matrix = sparse.random(50, 50, density=0.1, format="csr", dtype=np.float32,
                               random_state=7)
        types = np.array([f"N{i%5}" for i in range(50)])
        runs = []
        for _ in range(2):
            network = SpikingNetwork(matrix, types, _table(), dt_ms=0.2, seed=3)
            external = np.zeros(50, dtype=np.float32); external[:10] = 2.0
            runs.append(network.run(300, lambda _: external)["spike_counts"])
        assert (runs[0] == runs[1]).all()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
