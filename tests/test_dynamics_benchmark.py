"""Fast protocol tests for the manual full-graph dynamics gate."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest
from scipy import sparse

from flygi.config import load_config
from flygi.dynamics import RateParameters, ScipyRateNetwork

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PATH = ROOT / "scripts" / "benchmark_runtime.py"


def _load_benchmark() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_flygi_dynamics_benchmark", BENCHMARK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BENCHMARK = _load_benchmark()
_benchmark_internal_steps = BENCHMARK._benchmark_internal_steps
_protocol_issues = BENCHMARK._protocol_issues
_runtime_identity_issues = BENCHMARK._runtime_identity_issues
_select_pre_dn_probe = BENCHMARK._select_pre_dn_probe
_stability_check = BENCHMARK._stability_check
_timing_summary = BENCHMARK._timing_summary
_validate_args = BENCHMARK._validate_args
_write_json_exclusive = BENCHMARK._write_json_exclusive


def _network() -> ScipyRateNetwork:
    matrix = sparse.csr_matrix(
        (
            np.asarray([0.5, 1.0], dtype=np.float32),
            (np.asarray([1, 2], dtype=np.int32), np.asarray([0, 1], dtype=np.int32)),
        ),
        shape=(3, 3),
        dtype=np.float32,
    )
    return ScipyRateNetwork(
        matrix,
        RateParameters(internal_steps=2, leak=0.3, recurrent_gain=0.9),
    )


def test_timing_summary_uses_raw_nanoseconds_and_linear_p95() -> None:
    assert _timing_summary([]) == {
        "count": 0,
        "total_ns": 0,
        "mean_ns": None,
        "median_ns": None,
        "p95_ns": None,
        "min_ns": None,
        "max_ns": None,
    }
    assert _timing_summary([10, 20, 30, 40]) == {
        "count": 4,
        "total_ns": 100,
        "mean_ns": 25.0,
        "median_ns": 25.0,
        "p95_ns": 38.5,
        "min_ns": 10,
        "max_ns": 40,
    }


def test_pre_dn_probe_selects_strongest_incoming_edge_deterministically() -> None:
    matrix = sparse.csr_matrix(
        (
            np.asarray([0.4, -0.9, 1.5, 0.8], dtype=np.float32),
            (
                np.asarray([2, 2, 2, 3], dtype=np.int32),
                np.asarray([0, 1, 3, 0], dtype=np.int32),
            ),
        ),
        shape=(4, 4),
        dtype=np.float32,
    )

    probe = _select_pre_dn_probe(matrix, np.asarray([2, 3], dtype=np.int32))

    assert probe["presynaptic_index"] == 1
    assert probe["descending_index"] == 2
    assert probe["weight"] == pytest.approx(-0.9)


def test_gate_protocol_rejects_abbreviated_or_mismatched_measurements() -> None:
    complete = argparse.Namespace(
        internal_steps=[1, 2, 4, 8],
        warmup_actions=3,
        measured_actions=25,
        stability_steps=10_000,
    )
    assert _protocol_issues(complete, configured_internal_steps=2) == []

    abbreviated = argparse.Namespace(
        internal_steps=[1, 2],
        warmup_actions=0,
        measured_actions=1,
        stability_steps=10,
    )
    issues = _protocol_issues(abbreviated, configured_internal_steps=3)
    assert any("exactly" in issue for issue in issues)
    assert any("configured internal_steps must be included" in issue for issue in issues)
    assert any("configured internal_steps must be one of" in issue for issue in issues)
    assert any("warmup" in issue for issue in issues)
    assert any("measured" in issue for issue in issues)
    assert any("10,000" in issue for issue in issues)


def test_runtime_identity_rejects_a_self_consistent_tiny_bundle() -> None:
    config = load_config("configs/literal_rate.yaml")
    preprocessing = {
        "matrix_convention": config.graph.matrix_convention,
        "weight_transform": config.graph.weight_transform,
        "sign_mode": config.graph.sign_mode,
        "modulator_treatment": config.graph.modulator_treatment,
        "normalization": config.graph.normalization,
        "epsilon": config.graph.epsilon,
        "allow_self_edges": config.graph.allow_self_edges,
        "node_filter_column": config.graph.node_filter_column,
        "node_filter_values": config.graph.node_filter_values,
    }
    bundle = SimpleNamespace(
        node_count=3,
        edge_count=2,
        manifest={
            "release": "male-cns:v1.0",
            "outputs": [],
            "preprocessing": preprocessing,
        },
        groups={"descending_neurons": np.asarray([2], dtype=np.int32)},
    )

    issues = _runtime_identity_issues(config, bundle)

    assert any("166700" in issue for issue in issues)
    assert any("25582837" in issue for issue in issues)
    assert sum("SHA-256" in issue for issue in issues) == 3
    assert any("1,314" in issue for issue in issues)


def test_tiny_stability_and_timing_protocol() -> None:
    network = _network()
    state = network.initial_state(seed=7, scale=0.01)
    drive = np.asarray([0.25, 0.0, 0.0], dtype=np.float32)

    stability = _stability_check(network, state, drive, steps=11, chunk=4)
    assert stability["steps_completed"] == 11
    assert stability["finite"] is True
    assert stability["within_declared_bound"] is True
    assert stability["final_state"]["nonzero"] == 3

    timings = _benchmark_internal_steps(
        network,
        state,
        drive,
        internal_steps=[1, 2],
        warmup_actions=1,
        measured_actions=3,
    )
    assert set(timings) == {"1", "2"}
    for key, steps in (("1", 1), ("2", 2)):
        row = timings[key]
        assert row["internal_steps"] == steps
        assert len(row["samples_ns"]) == 3
        assert row["summary"]["count"] == 3
        assert row["summary"]["min_ns"] > 0
        assert len(row["final_state_sha256"]) == 64


def test_result_write_is_exclusive(tmp_path: Path) -> None:
    path = tmp_path / "result.json"
    _write_json_exclusive(path, {"passed": True})

    assert json.loads(path.read_text(encoding="utf-8")) == {"passed": True}
    with pytest.raises(FileExistsError):
        _write_json_exclusive(path, {"passed": False})


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"internal_steps": [0]}, "internal-steps"),
        ({"internal_steps": [2, 1]}, "ascending"),
        ({"internal_steps": [1, 1]}, "unique"),
        ({"warmup_actions": -1}, "warmup-actions"),
        ({"measured_actions": 0}, "measured-actions"),
        ({"stability_steps": 0}, "stability-steps"),
        ({"stability_chunk": 0}, "stability-chunk"),
    ],
)
def test_argument_validation_fails_closed(changes: dict[str, object], message: str) -> None:
    values = {
        "internal_steps": [1, 2, 4, 8],
        "warmup_actions": 3,
        "measured_actions": 25,
        "stability_steps": 10_000,
        "stability_chunk": 100,
    }
    values.update(changes)

    with pytest.raises(ValueError, match=message):
        _validate_args(argparse.Namespace(**values))
