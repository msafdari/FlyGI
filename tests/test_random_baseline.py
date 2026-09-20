"""Deterministic, exact-budget tests for the strict-offline baseline runner."""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from enum import Enum, StrEnum
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_random_baseline.py"


def _load_evaluator() -> ModuleType:
    name = "_flygi_random_baseline"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


evaluator = _load_evaluator()


class FakeState(StrEnum):
    NOT_PLAYED = "NOT_PLAYED"
    NOT_FINISHED = "NOT_FINISHED"
    WIN = "WIN"
    GAME_OVER = "GAME_OVER"


class FakeAction(Enum):
    RESET = 0
    ACTION1 = 1
    ACTION6 = 6

    def __init__(self, _: int) -> None:
        self.action_data: dict[str, int] = {}
        self.reasoning: object | None = None

    def is_complex(self) -> bool:
        return self is type(self).ACTION6

    def set_data(self, data: dict[str, int]) -> dict[str, int]:
        self.action_data = dict(data)
        return self.action_data

    @classmethod
    def from_id(cls, identifier: int) -> FakeAction:
        return cls(identifier)


@dataclass
class FakeFrame:
    state: FakeState
    available_actions: list[int]
    levels_completed: int
    frame: list[np.ndarray]


class FakeEnvironment:
    def __init__(self) -> None:
        self.actions: list[int] = []
        self.observation_space = self._frame(FakeState.NOT_PLAYED)

    def _frame(self, state: FakeState) -> FakeFrame:
        actions = [] if state is FakeState.NOT_PLAYED else [1, 6]
        pixels = np.full((2, 2), len(self.actions), dtype=np.uint8)
        return FakeFrame(state, actions, 0, [pixels])

    def step(self, action: FakeAction, **_: object) -> FakeFrame:
        self.actions.append(action.value)
        self.observation_space = self._frame(FakeState.NOT_FINISHED)
        return self.observation_space


class FakeRun:
    def __init__(self, actions: int) -> None:
        self.actions = actions

    def model_dump(self, **_: object) -> dict[str, object]:
        return {
            "score": 0.0,
            "levels_completed": 0,
            "actions": self.actions,
            "resets": 0,
            "state": FakeState.NOT_FINISHED,
            "completed": False,
            "level_scores": [0.0],
            "level_actions": [self.actions],
            "level_baseline_actions": [2],
            "message": None,
        }


class FakeScorecard:
    def __init__(self, actions: int) -> None:
        run = FakeRun(actions)
        self.environment = SimpleNamespace(
            runs=[run],
            score=0.0,
            levels_completed=0,
            actions=actions,
            resets=0,
            completed=False,
        )

    def find_environment(self, _: str) -> object:
        return self.environment


class FakeArcade:
    operation_mode = "offline"

    def __init__(self) -> None:
        self.environment: FakeEnvironment | None = None

    def open_scorecard(self, **_: object) -> str:
        return "fake-card"

    def make(self, *_: object, **__: object) -> FakeEnvironment:
        self.environment = FakeEnvironment()
        return self.environment

    def close_scorecard(self, _: str) -> FakeScorecard:
        assert self.environment is not None
        return FakeScorecard(len(self.environment.actions))


def _runtime() -> object:
    return evaluator.ArcRuntime(
        Arcade=FakeArcade,
        OperationMode=SimpleNamespace(OFFLINE="offline"),
        GameAction=FakeAction,
    )


def _game(tmp_path: Path) -> object:
    return evaluator.FrozenGame(
        game_id="zz99-deadbeef",
        base_game_id="zz99",
        title="fake",
        metadata_path=tmp_path / "metadata.json",
        metadata_sha256="0" * 64,
        source_sha256="1" * 64,
        baseline_actions=(2,),
    )


def test_evaluate_one_enforces_exact_budget_and_replays(tmp_path: Path) -> None:
    kwargs = {
        "runtime": _runtime(),
        "game": _game(tmp_path),
        "experiment_seed": 7,
        "action_budget": 5,
        "environments_dir": tmp_path,
        "arcade_factory": FakeArcade,
    }
    first = evaluator.evaluate_one(**kwargs)
    second = evaluator.evaluate_one(**kwargs)

    assert first["status"] == "success"
    assert first["termination_reason"] == "budget_exhausted"
    assert first["actions_completed"] == 5
    assert first["official"]["actions"] == 5
    assert first["illegal_action_count"] == 0
    assert first["action6_coordinates"]["invalid"] == 0
    assert [entry["step"] for entry in first["trace"]] == list(range(5))
    assert first["replay_trace_sha256"] == second["replay_trace_sha256"]


def test_official_scorecard_preserves_reset_delimited_runs() -> None:
    first = FakeRun(3)
    second = FakeRun(5)
    environment = SimpleNamespace(
        runs=[first, second],
        score=2.5,
        levels_completed=1,
        actions=8,
        resets=1,
        completed=False,
    )
    scorecard = SimpleNamespace(find_environment=lambda _: environment)

    result = evaluator._official_run(scorecard, "zz99-deadbeef")

    assert result["run_count"] == 2
    assert result["actions"] == 8
    assert [run["actions"] for run in result["runs"]] == [3, 5]


def test_result_write_is_immutable(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    evaluator.write_json_exclusive(output, {"ok": True})
    assert json.loads(output.read_text(encoding="utf-8")) == {"ok": True}

    with pytest.raises(FileExistsError):
        evaluator.write_json_exclusive(output, {"ok": False})


def test_seed_derivation_is_stable_and_domain_separated() -> None:
    first = evaluator.derived_run_seeds(7, "zz99-deadbeef")
    second = evaluator.derived_run_seeds(7, "zz99-deadbeef")

    assert first == second
    assert first[0] != first[1]
    assert first != evaluator.derived_run_seeds(8, "zz99-deadbeef")
