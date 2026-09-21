"""Fast offline tests for the dynamics-regime diagnostic probe."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "scripts" / "probe_dynamics_regime.py"


def _load_probe() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_flygi_dynamics_regime_probe", PROBE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PROBE = _load_probe()
_cosine = PROBE._cosine
_forward_hops = PROBE._forward_hops
_validate_args = PROBE._validate_args
_weak_null = PROBE._weak_null
_write_json_exclusive = PROBE._write_json_exclusive


def _chain(node_count: int = 4) -> sparse.csr_matrix:
    """Build ``0 -> 1 -> 2 -> 3`` under the ``W[post, pre]`` convention."""

    rows = np.arange(1, node_count, dtype=np.int32)
    cols = np.arange(0, node_count - 1, dtype=np.int32)
    data = np.ones(node_count - 1, dtype=np.float32)
    matrix = sparse.csr_matrix((data, (rows, cols)), shape=(node_count, node_count))
    matrix.sort_indices()
    return matrix


def test_forward_hops_follows_edge_direction() -> None:
    result = _forward_hops(
        _chain(), np.array([0], dtype=np.int64), np.array([3], dtype=np.int64), max_hops=8
    )
    assert result["first_target_hop"] == 3
    assert result["all_targets_hop"] == 3
    assert result["targets_total"] == 1


def test_forward_hops_does_not_traverse_edges_backwards() -> None:
    result = _forward_hops(
        _chain(), np.array([3], dtype=np.int64), np.array([0], dtype=np.int64), max_hops=8
    )
    assert result["first_target_hop"] is None
    assert result["nodes_unreached"] == 3


def test_weak_null_preserves_in_degree_and_row_weight_multiset() -> None:
    generator = np.random.default_rng(7)
    dense = (generator.random((60, 60)) < 0.2) * generator.random((60, 60))
    np.fill_diagonal(dense, 0.0)
    matrix = sparse.csr_matrix(dense.astype(np.float32))
    matrix.sort_indices()

    shuffled = _weak_null(matrix, seed=11)

    assert np.array_equal(np.diff(matrix.indptr), np.diff(shuffled.indptr))
    for row in range(matrix.shape[0]):
        original = np.sort(matrix.data[matrix.indptr[row] : matrix.indptr[row + 1]])
        rewired = np.sort(shuffled.data[shuffled.indptr[row] : shuffled.indptr[row + 1]])
        assert np.allclose(original, rewired)


def test_weak_null_is_deterministic_and_changes_topology() -> None:
    generator = np.random.default_rng(3)
    dense = (generator.random((80, 80)) < 0.15) * generator.random((80, 80))
    matrix = sparse.csr_matrix(dense.astype(np.float32))
    matrix.sort_indices()

    first = _weak_null(matrix, seed=5)
    second = _weak_null(matrix, seed=5)
    other = _weak_null(matrix, seed=6)

    assert np.array_equal(first.indices, second.indices)
    assert not np.array_equal(first.indices, matrix.indices)
    assert not np.array_equal(first.indices, other.indices)


def test_weak_null_does_not_preserve_out_degree() -> None:
    """The probe must not be mistaken for the preregistered control."""

    generator = np.random.default_rng(1)
    dense = np.zeros((40, 40))
    dense[:, 0] = generator.random(40)  # node 0 is a hub with out-degree 40
    matrix = sparse.csr_matrix(dense.astype(np.float32))
    matrix.sort_indices()

    shuffled = _weak_null(matrix, seed=2)
    original_out = np.bincount(matrix.indices, minlength=40)
    rewired_out = np.bincount(shuffled.indices, minlength=40)

    assert original_out[0] == 40
    assert rewired_out[0] < 40


def test_cosine_reports_none_for_a_silent_population() -> None:
    zeros = np.zeros(4, dtype=np.float32)
    ones = np.ones(4, dtype=np.float32)
    assert _cosine(zeros, ones) is None
    assert _cosine(ones, ones) == pytest.approx(1.0)


def test_write_json_exclusive_refuses_to_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "regime.json"
    _write_json_exclusive(target, {"kind": "flygi-dynamics-regime-probe"})
    with pytest.raises(FileExistsError):
        _write_json_exclusive(target, {"kind": "flygi-dynamics-regime-probe"})


def _args(**overrides: object) -> argparse.Namespace:
    defaults = {
        "arrival_steps": 4,
        "max_hops": 4,
        "drive_actions": 2,
        "silent_actions": 2,
        "settle_actions": 2,
        "power_iterations": 10,
        "code_inputs": 4,
        "amplitude": 0.5,
        "internal_steps": 2,
        "leak": None,
        "recurrent_gain": None,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_validate_args_rejects_degenerate_protocols() -> None:
    _validate_args(_args())
    _validate_args(_args(leak=0.1, recurrent_gain=1.4))
    for override in (
        {"arrival_steps": 0},
        {"drive_actions": -1},
        {"code_inputs": 1},
        {"amplitude": 0.0},
        {"internal_steps": 0},
        {"leak": 0.0},
        {"leak": 1.5},
        {"recurrent_gain": -0.1},
    ):
        with pytest.raises(SystemExit):
            _validate_args(_args(**override))
