"""Score-blind contracts for the loop-escape calibration runner."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "calibrate_loop_escape.py"


def _load_calibrator() -> ModuleType:
    name = "_flygi_loop_escape_calibration"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


calibrator = _load_calibrator()


def test_candidate_grid_and_temperatures_are_frozen() -> None:
    assert [candidate.name for candidate in calibrator.CANDIDATES] == [
        "mild",
        "balanced",
        "strong",
    ]
    assert [candidate.exploration_bonus for candidate in calibrator.CANDIDATES] == [
        0.25,
        0.5,
        1.0,
    ]
    assert [candidate.unchanged_failure_penalty for candidate in calibrator.CANDIDATES] == [
        0.5,
        1.0,
        2.0,
    ]
    assert all(candidate.action_temperature == 0.15 for candidate in calibrator.CANDIDATES)
    assert all(candidate.coordinate_temperature == 0.2 for candidate in calibrator.CANDIDATES)


def test_policy_factory_passes_only_the_declared_loop_overrides() -> None:
    calls: list[dict[str, object]] = []

    def builder(*_: object, **kwargs: object) -> object:
        calls.append(kwargs)
        return SimpleNamespace(policy="policy", describe=lambda: {"ok": True})

    candidate = calibrator.CANDIDATES[1]
    factory = calibrator.PolicyFactory(
        builder,
        "config",
        "actions",
        runtime_dir=None,
        bundle="bundle",
        projection="projection",
        internal_steps=4,
        candidate=candidate,
    )

    assert factory(123) == "policy"
    assert calls[0]["decision_seed"] == 123
    assert calls[0]["action_temperature"] == 0.15
    assert calls[0]["coordinate_temperature"] == 0.2
    assert calls[0]["loop_escape_enabled"] is True
    assert calls[0]["loop_escape_exploration_bonus"] == 0.5
    assert calls[0]["loop_escape_unchanged_failure_penalty"] == 1.0


def test_ranking_is_lexicographic_and_ineligible_candidates_sort_last() -> None:
    def result(
        name: str,
        metrics: tuple[float, float, float, float],
        *,
        eligible: bool = True,
    ) -> dict[str, object]:
        return {
            "candidate": {"name": name},
            "selection_metrics": {
                key: value
                for (key, _direction), value in zip(
                    calibrator.SELECTION_ORDER,
                    metrics,
                    strict=True,
                )
            },
            "checks": {"eligible": eligible},
            "official": {"score": 1e99 if name == "worse" else -1e99},
        }

    better_unique = result("better_unique", (11.0, 10.0, 0.1, 500.0))
    worse = result("worse", (10.0, 0.0, 1.0, 1.0))
    invalid = result("invalid", (100.0, 0.0, 1.0, 1.0), eligible=False)

    ranking = calibrator.rank_candidates([worse, invalid, better_unique])

    assert [item["candidate"] for item in ranking] == [
        "better_unique",
        "worse",
        "invalid",
    ]


def test_trace_provenance_records_every_bias_and_count_vector() -> None:
    record = SimpleNamespace(
        loop_escape_state_key="abc",
        loop_escape_standardized_bias=[0.0] * 8,
        loop_escape_selected_bias=0.0,
        loop_escape_attempts_before=1,
        loop_escape_unchanged_failures_before=1,
        loop_escape_attempt_counts=[0, 1, 0, 0, 0, 0, 0, 0],
        loop_escape_unchanged_failure_counts=[0, 1, 0, 0, 0, 0, 0, 0],
        loop_escape_prior_choice_failed=True,
        loop_escape_bias_changed_argmax=False,
    )
    trace = [{"action_id": 1}]

    calibrator._attach_loop_escape_trace([record], trace)

    persisted = trace[0]["loop_escape"]
    assert persisted["state_key"] == "abc"
    assert len(persisted["standardized_bias"]) == 8
    assert persisted["attempt_counts"][1] == 1
    assert persisted["unchanged_failure_counts"][1] == 1
