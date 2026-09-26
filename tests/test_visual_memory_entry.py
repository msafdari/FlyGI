"""Contract tests for the outcome-blind visual-memory entry probe."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/probe_visual_memory_entry.py"
SPEC = importlib.util.spec_from_file_location("_flygi_test_visual_memory_entry", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _shape_code() -> np.ndarray:
    values = np.zeros((16, 2, 2), dtype=np.float64)
    values[:, 0, 0] = 1.0
    values[:, 1, 1] = 1.0
    return values


def _constant_code(dim: int = 3) -> np.ndarray:
    return np.ones((16, 2, dim), dtype=np.float64)


def _passing_inputs() -> tuple[np.ndarray, dict[str, dict[str, object]]]:
    native = _shape_code()
    return native, {
        "native": MODULE.transfer_scores(native),
        "sensory": MODULE.transfer_scores(_constant_code()),
        "type_mean": MODULE.transfer_scores(_constant_code(5)),
        "graph_off": MODULE.transfer_scores(np.zeros((16, 2, 2))),
    }


def test_panel_geometry_area_values_and_order() -> None:
    panel = MODULE.make_panel()
    assert panel.shape == (16, 2, 64, 64)
    assert panel.dtype == np.int8

    for position, (row, column) in enumerate(product((20, 28, 36, 44), repeat=2)):
        horizontal = np.zeros((64, 64), dtype=np.int8)
        vertical = np.zeros((64, 64), dtype=np.int8)
        horizontal[row - 1 : row + 2, column - 4 : column + 5] = 15
        vertical[row - 4 : row + 5, column - 1 : column + 2] = 15
        np.testing.assert_array_equal(panel[position, 0], horizontal)
        np.testing.assert_array_equal(panel[position, 1], vertical)
        assert np.count_nonzero(panel[position, 0]) == 27
        assert np.count_nonzero(panel[position, 1]) == 27
    assert set(np.unique(panel)) == {0, 15}
    assert np.unique(panel.reshape(32, -1), axis=0).shape[0] == 32


@pytest.mark.parametrize(
    ("values", "accuracy"),
    [
        (_shape_code(), 1.0),
        (_constant_code(), 0.5),
        (np.repeat(np.eye(16, dtype=np.float64)[:, None, :], 2, axis=1), 0.5),
        (np.tile(np.array([[1.0, 1.0], [1.0 + 1e-7, 1.0]]), (16, 1, 1)), 0.5),
    ],
    ids=("perfect-shape", "constant", "location-only", "sub-tolerance-tie"),
)
def test_transfer_scores_known_codes(values: np.ndarray, accuracy: float) -> None:
    result = MODULE.transfer_scores(values)
    assert result["accuracy"] == pytest.approx(accuracy)
    assert len(result["per_position"]) == 16
    assert len(result["decisions"]) == 480
    assert len(result["margins"]) == 480


def test_transfer_scores_awards_half_credit_within_frozen_tie_tolerance() -> None:
    values = np.tile(np.array([[1.0, 1.0], [1.0 + 1e-7, 1.0]]), (16, 1, 1))
    result = MODULE.transfer_scores(values)
    assert all(decision == 0.5 for decision in result["decisions"])
    assert all(0.0 < margin <= 1e-12 for margin in result["margins"])


def test_transfer_scores_rectifies_and_is_invariant_to_positive_scale() -> None:
    values = _shape_code()
    negative_junk = -np.arange(1, 16 * 2 + 1, dtype=np.float64).reshape(16, 2, 1)
    with_negative = np.concatenate((values, negative_junk), axis=2)
    without_negative = np.concatenate((values, np.zeros_like(negative_junk)), axis=2)
    expected = MODULE.transfer_scores(without_negative)
    observed = MODULE.transfer_scores(with_negative)
    assert observed == expected

    scales = np.arange(1, 33, dtype=np.float64).reshape(16, 2, 1)
    assert MODULE.transfer_scores(values * scales) == MODULE.transfer_scores(values)


@pytest.mark.parametrize(
    "shape",
    [(15, 2, 3), (16, 1, 3), (16, 2, 0), (16, 2), (16, 2, 3, 1)],
)
def test_transfer_scores_rejects_malformed_shapes(shape: tuple[int, ...]) -> None:
    with pytest.raises(ValueError):
        MODULE.transfer_scores(np.zeros(shape, dtype=np.float64))


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_transfer_scores_rejects_nonfinite_values(bad: float) -> None:
    values = _shape_code()
    values[0, 0, 0] = bad
    with pytest.raises(ValueError):
        MODULE.transfer_scores(values)


def test_atomic_json_publishes_once_without_leaving_temporary_files(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    first = {"status": "complete", "scores": [0.5, 1.0]}
    MODULE.atomic_json(output, first)
    assert json.loads(output.read_text()) == first
    assert list(tmp_path.iterdir()) == [output]

    with pytest.raises(FileExistsError):
        MODULE.atomic_json(output, {"status": "replacement"})
    assert json.loads(output.read_text()) == first
    assert list(tmp_path.iterdir()) == [output]


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_atomic_json_rejects_nonfinite_without_publishing(tmp_path: Path, bad: float) -> None:
    output = tmp_path / "result.json"
    with pytest.raises(ValueError):
        MODULE.atomic_json(output, {"value": bad})
    assert not output.exists()
    assert list(tmp_path.iterdir()) == []


def test_scientific_gate_passes_only_when_all_clauses_pass() -> None:
    native, scores = _passing_inputs()
    result = MODULE.scientific_gate(native, scores)
    assert set(result) == {"passed", "checks"}
    assert result["passed"] is True
    assert result["checks"] and all(result["checks"].values())


@pytest.mark.parametrize(
    ("baseline_decisions", "expected"),
    [
        ([1.0] * 312 + [0.0] * 168, True),
        ([1.0] * 312 + [0.5] + [0.0] * 167, False),
    ],
    ids=("exact-48-decision-margin", "half-credit-below-margin"),
)
def test_scientific_gate_uses_exact_decision_count_margin(
    baseline_decisions: list[float], expected: bool
) -> None:
    native, scores = _passing_inputs()
    scores = copy.deepcopy(scores)
    scores["native"].update(
        accuracy=360 / 480,
        decisions=[1.0] * 360 + [0.0] * 120,
        per_position=[1.0] * 12 + [0.0] * 4,
    )
    for baseline in ("sensory", "type_mean"):
        scores[baseline].update(
            accuracy=sum(baseline_decisions) / 480,
            decisions=baseline_decisions,
        )

    result = MODULE.scientific_gate(native, scores)
    assert result["checks"]["sensory_margin"] is expected
    assert result["checks"]["type_mean_margin"] is expected
    assert result["passed"] is expected


@pytest.mark.parametrize(
    "case",
    [
        "absolute_accuracy",
        "sensory_margin",
        "type_mean_margin",
        "position_count",
        "graph_off_chance",
        "native_signal_floor",
        "paired_shape_floor",
    ],
)
def test_each_scientific_gate_clause_can_fail(case: str) -> None:
    native, scores = _passing_inputs()
    scores = copy.deepcopy(scores)
    if case == "absolute_accuracy":
        scores["native"]["accuracy"] = 0.74
    elif case == "sensory_margin":
        scores["sensory"].update(
            accuracy=437 / 480,
            decisions=[1.0] * 437 + [0.0] * 43,
        )
    elif case == "type_mean_margin":
        scores["type_mean"].update(
            accuracy=437 / 480,
            decisions=[1.0] * 437 + [0.0] * 43,
        )
    elif case == "position_count":
        scores["native"]["per_position"] = [1.0] * 11 + [0.5] * 5
    elif case == "graph_off_chance":
        scores["graph_off"]["accuracy"] = 0.51
    elif case == "native_signal_floor":
        native[0, 0] = 0.0
    elif case == "paired_shape_floor":
        native[0, 1] = native[0, 0]

    result = MODULE.scientific_gate(native, scores)
    assert result["passed"] is False
    assert not all(result["checks"].values())
