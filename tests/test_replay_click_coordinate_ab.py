"""Comparison-contract tests for H-COORDINATE-CONVENTION replay."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "replay_click_coordinate_ab.py"
SPEC = importlib.util.spec_from_file_location("_flygi_test_coordinate_replay", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
_binary_log_loss = MODULE._binary_log_loss
_summarize = MODULE._summarize


def test_binary_log_loss_rewards_better_prequential_probabilities() -> None:
    labels = [False, True, False, True]
    uncertain = [0.5, 0.5, 0.5, 0.5]
    informed = [0.1, 0.9, 0.2, 0.8]

    assert _binary_log_loss(labels, informed) < _binary_log_loss(labels, uncertain)
    assert math.isfinite(_binary_log_loss(labels, [0.0, 1.0, 0.0, 1.0]))


def test_preregistered_promotion_requires_every_check() -> None:
    rows = []
    examples = []
    for game in ("ft09", "lp85", "r11l", "tn36", "vc33", "sp80"):
        rows.append(
            {
                "game_id": f"{game}-version",
                "legacy_log_loss": 0.7,
                "corrected_log_loss": 0.5,
                "corrected_minus_legacy_log_loss": -0.2,
            }
        )
        for label in (False, True):
            examples.append(
                {
                    "seed": 0,
                    "game_id": f"{game}-version",
                    "changed": label,
                    "legacy_probability": 0.5,
                    "corrected_probability": 0.8 if label else 0.2,
                }
            )

    passed = _summarize(rows, examples)
    assert passed["replay_gate_passed"] is True
    assert all(passed["promotion_checks"].values())

    rows[-1] = {
        **rows[-1],
        "corrected_log_loss": 2.0,
        "corrected_minus_legacy_log_loss": 1.3,
    }
    rows[-2] = dict(rows[-1], game_id="vc33-version")
    rows[-3] = dict(rows[-1], game_id="tn36-version")
    failed = _summarize(rows, examples)
    assert failed["replay_gate_passed"] is False
    assert failed["promotion_checks"]["at_least_four_games_nonworse"] is False


def test_average_precision_excludes_single_class_rows_before_pooling() -> None:
    rows = [
        {
            "game_id": "mixed-version",
            "legacy_log_loss": 0.7,
            "corrected_log_loss": 0.6,
            "corrected_minus_legacy_log_loss": -0.1,
        },
        {
            "game_id": "all-positive-version",
            "legacy_log_loss": 0.7,
            "corrected_log_loss": 0.6,
            "corrected_minus_legacy_log_loss": -0.1,
        },
    ]
    examples = [
        {
            "seed": 0,
            "game_id": "mixed-version",
            "changed": False,
            "legacy_probability": 0.4,
            "corrected_probability": 0.2,
        },
        {
            "seed": 0,
            "game_id": "mixed-version",
            "changed": True,
            "legacy_probability": 0.6,
            "corrected_probability": 0.8,
        },
        {
            "seed": 0,
            "game_id": "all-positive-version",
            "changed": True,
            "legacy_probability": 0.01,
            "corrected_probability": 0.01,
        },
    ]

    summary = _summarize(rows, examples)

    assert summary["average_precision_rows"] == 1
    assert summary["average_precision_clicks"] == 2
    assert summary["legacy_aggregate_average_precision"] == pytest.approx(1.0)
    assert summary["corrected_aggregate_average_precision"] == pytest.approx(1.0)
