"""Behavior-only tests for the preregistered sampler calibration runner."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "calibrate_sampler.py"


def _load_calibrator() -> ModuleType:
    name = "_flygi_sampler_calibration"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


calibrator = _load_calibrator()


def _trace(*actions: tuple[int, dict[str, int]]) -> list[dict[str, object]]:
    return [
        {
            "action_id": action_id,
            "payload": payload,
            "available_action_ids": [1, 2, 6],
            "policy_ns": 100 + index,
            "levels_completed_before": 99,
            "levels_completed_after": 100,
        }
        for index, (action_id, payload) in enumerate(actions)
    ]


def _row(
    *,
    game: str = "lp85-v1",
    base_game: str = "lp85",
    seed: int = 0,
    trace: list[dict[str, object]] | None = None,
    unique: int = 4,
    repeats: int = 1,
    entropy: float = 2.0,
    legal_max: float = 3.0,
    score: float = 0.0,
) -> dict[str, object]:
    decisions = trace or _trace((6, {"x": seed, "y": 3}), (6, {"x": 4, "y": 5}))
    return {
        "game_id": game,
        "base_game_id": base_game,
        "seed": seed,
        "status": "success",
        "termination_reason": "budget_exhausted",
        "failure": None,
        "action_budget": len(decisions),
        "actions_completed": len(decisions),
        "illegal_action_count": 0,
        "action6_coordinates": {"invalid": 0},
        "observations": {
            "count": len(decisions) + 1,
            "unique": unique,
            "consecutive_repeats": repeats,
        },
        "trace": decisions,
        "replay_trace_sha256": f"trace-{game}-{seed}",
        "official": {"score": score, "levels_completed": 1000},
        "final_levels_completed": 1000,
        "sampler_diagnostics": {
            "action_entropy_bits": entropy,
            "legal_max_entropy_bits": legal_max,
            "coordinate_draws": 2,
            "unique_coordinates": 2,
        },
    }


def test_candidate_grid_is_small_fixed_and_scale_aware() -> None:
    assert [candidate.name for candidate in calibrator.CANDIDATES] == [
        "focused",
        "balanced",
        "exploratory",
    ]
    assert len(calibrator.CANDIDATES) == 3
    assert all(candidate.action_temperature > 0 for candidate in calibrator.CANDIDATES)
    assert all(candidate.coordinate_temperature > 0 for candidate in calibrator.CANDIDATES)


def test_sampler_diagnostics_normalize_entropy_by_legal_maximum() -> None:
    trace = [
        {"action_id": 1, "payload": {}, "available_action_ids": [1, 2]},
        {"action_id": 6, "payload": {"x": 7, "y": 8}, "available_action_ids": [1, 2, 6]},
        {"action_id": 1, "payload": {}, "available_action_ids": [1]},
    ]
    records = [
        SimpleNamespace(
            forced_reset=False,
            action_entropy_bits=1.0,
            action_probability=0.5,
            coordinate_x=None,
            coordinate_y=None,
            coordinate_method=None,
        ),
        SimpleNamespace(
            forced_reset=False,
            action_entropy_bits=math.log2(3),
            action_probability=1 / 3,
            coordinate_x=7,
            coordinate_y=8,
            coordinate_method="sampled",
        ),
        SimpleNamespace(
            forced_reset=False,
            action_entropy_bits=0.0,
            action_probability=1.0,
            coordinate_x=None,
            coordinate_y=None,
            coordinate_method=None,
        ),
    ]

    summary = calibrator.sampler_diagnostics(records, trace)

    assert summary["entropy_turns"] == 2
    assert summary["action_entropy_fraction_of_legal_max"] == pytest.approx(1.0)
    assert summary["coordinate_draws"] == 1
    assert summary["unique_coordinates"] == 1
    assert summary["coordinate_methods"] == {"sampled": 1}


def test_behavior_summary_is_blind_to_public_score_and_progress() -> None:
    low_score = _row(score=0.0)
    high_score = _row(score=1_000_000.0)
    high_score["final_levels_completed"] = 1_000_000

    assert calibrator.summarize_behavior([low_score]) == calibrator.summarize_behavior([high_score])

    persisted = calibrator.behavior_only_row(high_score)
    assert "official" not in persisted
    assert "final_levels_completed" not in persisted
    assert all("levels_completed_before" not in entry for entry in persisted["trace"])
    assert all("levels_completed_after" not in entry for entry in persisted["trace"])


def test_graph_causal_diversity_compares_actions_and_coordinate_payloads() -> None:
    real = [
        _row(seed=0, trace=_trace((6, {"x": 1, "y": 2}), (6, {"x": 3, "y": 4}))),
        _row(seed=1, trace=_trace((6, {"x": 5, "y": 6}), (6, {"x": 7, "y": 8}))),
    ]
    bypass = [
        _row(seed=0, trace=_trace((6, {"x": 1, "y": 2}), (6, {"x": 9, "y": 9}))),
        _row(seed=1, trace=_trace((6, {"x": 5, "y": 6}), (6, {"x": 7, "y": 8}))),
    ]

    result = calibrator.graph_causal_diversity(real, bypass)

    assert result["passed"] is True
    assert result["differing_pairs"] == 1
    assert result["differing_turns"] == 1
    assert result["causal_turn_disagreement_rate"] == pytest.approx(0.25)


def test_seed_diversity_counts_coordinate_changes_in_click_only_games() -> None:
    click_rows = [
        _row(seed=0, trace=_trace((6, {"x": 1, "y": 2}))),
        _row(seed=1, trace=_trace((6, {"x": 2, "y": 2}))),
    ]
    mixed_rows = [
        _row(
            game="ls20-v1",
            base_game="ls20",
            seed=0,
            trace=_trace((1, {})),
        ),
        _row(
            game="ls20-v1",
            base_game="ls20",
            seed=1,
            trace=_trace((6, {"x": 3, "y": 3})),
        ),
    ]

    result = calibrator.seed_diversity([*click_rows, *mixed_rows])

    assert result["passed"] is True
    assert result["diverse_categories"] == ["click_only", "mixed"]


def test_policy_factory_passes_derived_decision_seed_and_sampler_overrides() -> None:
    calls: list[dict[str, object]] = []

    def builder(*_: object, **kwargs: object) -> object:
        calls.append(kwargs)
        return SimpleNamespace(policy="policy", describe=lambda: {"ok": True})

    candidate = calibrator.SamplerCandidate("test", 0.25, 0.75)
    factory = calibrator.PolicyFactory(
        builder,
        "config",
        "actions",
        runtime_dir=None,
        bundle="bundle",
        projection="projection",
        ablate_graph=False,
        internal_steps=4,
        candidate=candidate,
    )

    assert factory(123456) == "policy"
    assert calls[0]["decision_seed"] == 123456
    assert calls[0]["action_temperature"] == 0.25
    assert calls[0]["coordinate_temperature"] == 0.75


def test_rank_is_equal_weight_score_blind_and_ineligible_candidates_sort_last() -> None:
    def result(
        name: str,
        values: tuple[float, float, float, float, float],
        *,
        eligible: bool = True,
    ) -> dict[str, object]:
        metrics = {
            metric: value
            for (metric, _direction), value in zip(calibrator.RANKING_METRICS, values, strict=True)
        }
        return {
            "candidate": {"name": name},
            "ranking_metrics": metrics,
            "checks": {"eligible": eligible},
            # This must be unreachable to the ranking implementation.
            "official": {"score": -1e99 if name == "best" else 1e99},
        }

    best = result("best", (10.0, 1.0, 0.8, 0.7, 100.0))
    middle = result("middle", (8.0, 2.0, 0.6, 0.4, 120.0))
    invalid = result("invalid", (20.0, 0.0, 1.0, 1.0, 1.0), eligible=False)

    ranking = calibrator.rank_candidates([best, middle, invalid])

    assert [item["candidate"] for item in ranking] == ["best", "middle", "invalid"]
    assert ranking[0]["rank_sum"] == 5
    assert ranking[-1]["eligible"] is False


def test_unmeasurable_entropy_does_not_crash_a_click_only_smoke() -> None:
    result = {
        "candidate": {"name": "click-only-smoke"},
        "ranking_metrics": {
            "mean_unique_observations": 2.0,
            "mean_consecutive_repeats": 1.0,
            "action_entropy_fraction_of_legal_max": None,
            "causal_turn_disagreement_rate": 0.5,
            "median_policy_ns": 10.0,
        },
        "checks": {"eligible": False},
    }

    ranking = calibrator.rank_candidates([result])

    assert ranking[0]["candidate"] == "click-only-smoke"
    assert ranking[0]["eligible"] is False
