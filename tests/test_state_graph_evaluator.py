"""Frozen promotion contract for the Phase 1 controller evaluator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_state_graph.py"


def _load_evaluator() -> ModuleType:
    name = "_flygi_state_graph_evaluator_test"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EVALUATOR = _load_evaluator()


def _row(game_id: str, score: float, levels: int) -> dict[str, object]:
    return {
        "game_id": game_id,
        "official": {"score": score, "levels_completed": levels},
    }


def test_promotion_requires_score_and_three_distinct_progress_games() -> None:
    rows = [
        _row("aa00-v1", 0.5, 1),
        _row("bb00-v1", 0.5, 1),
        _row("cc00-v1", 0.5, 1),
        _row("dd00-v1", 0.0, 0),
    ]

    check = EVALUATOR.promotion_check(rows)

    assert check["passed"]
    assert check["mean_score"] == pytest.approx(0.375)
    assert check["progress_games"] == ["aa00-v1", "bb00-v1", "cc00-v1"]


def test_promotion_does_not_count_duplicate_seed_rows_as_distinct_games() -> None:
    rows = [
        _row("aa00-v1", 0.2, 1),
        _row("aa00-v1", 0.2, 1),
        _row("bb00-v1", 0.2, 1),
    ]

    check = EVALUATOR.promotion_check(rows)

    assert not check["passed"]
    assert check["progress_games"] == ["aa00-v1", "bb00-v1"]
    assert any("required at least 3" in issue for issue in check["issues"])


def test_promotion_requires_strict_improvement_over_frozen_random_mean() -> None:
    rows = [_row("aa00-v1", EVALUATOR.RANDOM_500_MEAN_SCORE, 1) for _ in range(3)]
    rows[1]["game_id"] = "bb00-v1"
    rows[2]["game_id"] = "cc00-v1"

    check = EVALUATOR.promotion_check(rows)

    assert not check["passed"]
    assert any("did not exceed random" in issue for issue in check["issues"])
