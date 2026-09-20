"""Smoke-test the Kaggle adapter without installing the official framework."""

from __future__ import annotations

import builtins
import importlib.util
import sys
from dataclasses import dataclass
from enum import Enum, StrEnum
from importlib import import_module
from pathlib import Path
from types import ModuleType

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
ADAPTER_PATH = REPOSITORY_ROOT / "kaggle" / "agent" / "my_agent.py"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

NoLegalActionError = import_module("flygi.arc").NoLegalActionError


class FakeGameState(StrEnum):
    NOT_PLAYED = "NOT_PLAYED"
    NOT_FINISHED = "NOT_FINISHED"
    WIN = "WIN"
    GAME_OVER = "GAME_OVER"


class FakeGameAction(Enum):
    RESET = 0
    ACTION1 = 1
    ACTION2 = 2
    ACTION3 = 3
    ACTION4 = 4
    ACTION5 = 5
    ACTION6 = 6
    ACTION7 = 7

    def __init__(self, _: int) -> None:
        self.action_data: dict[str, int] = {}
        self.reasoning: object | None = None

    def is_complex(self) -> bool:
        return self is type(self).ACTION6

    def set_data(self, data: dict[str, int]) -> dict[str, int]:
        self.action_data = dict(data)
        return self.action_data

    @classmethod
    def from_id(cls, action_id: int) -> FakeGameAction:
        try:
            return cls(action_id)
        except ValueError as exc:
            raise ValueError(f"unknown fake action id {action_id}") from exc


@dataclass
class FakeFrameData:
    state: FakeGameState
    available_actions: list[int]


class FakeAgent:
    MAX_ACTIONS = 80

    def __init__(self, *args: object, **kwargs: object) -> None:
        del args
        self.game_id = str(kwargs["game_id"])

    @property
    def name(self) -> str:
        return f"{self.game_id}.{self.__class__.__name__.lower()}"


def _load_adapter(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    arcengine = ModuleType("arcengine")
    arcengine.FrameData = FakeFrameData  # type: ignore[attr-defined]
    arcengine.GameAction = FakeGameAction  # type: ignore[attr-defined]
    arcengine.GameState = FakeGameState  # type: ignore[attr-defined]

    agents = ModuleType("agents")
    agents.__path__ = []  # type: ignore[attr-defined]
    agent_module = ModuleType("agents.agent")
    agent_module.Agent = FakeAgent  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "arcengine", arcengine)
    monkeypatch.setitem(sys.modules, "agents", agents)
    monkeypatch.setitem(sys.modules, "agents.agent", agent_module)

    module_name = "_flygi_kaggle_adapter_smoke"
    spec = importlib.util.spec_from_file_location(module_name, ADAPTER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)
    return module


def test_adapter_module_imports_without_the_optional_official_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def import_without_arc(name: str, *args: object, **kwargs: object) -> object:
        if name in {"arcengine", "agents", "agents.agent"}:
            raise ModuleNotFoundError(f"No module named {name!r}", name=name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_arc)
    module_name = "_flygi_kaggle_adapter_no_runtime"
    spec = importlib.util.spec_from_file_location(module_name, ADAPTER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)

    assert module.MyAgent.__name__ == "MyAgent"
    with pytest.raises(RuntimeError, match="official 'arcengine' and 'agents'"):
        module.MyAgent(game_id="smoke-v1")


def test_random_adapter_obeys_official_contract_with_fakes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_adapter(monkeypatch)
    agent = module.MyAgent(game_id="smoke-v1", rng_seed=20260919)

    initial = FakeFrameData(FakeGameState.NOT_PLAYED, [])
    assert agent.is_done([], initial) is False
    assert agent.choose_action([], initial) is FakeGameAction.RESET

    only_action_2 = FakeFrameData(FakeGameState.NOT_FINISHED, [2])
    assert agent.choose_action([], only_action_2) is FakeGameAction.ACTION2

    only_click = FakeFrameData(FakeGameState.NOT_FINISHED, [6])
    click = agent.choose_action([], only_click)
    assert click is FakeGameAction.ACTION6
    assert set(click.action_data) == {"x", "y"}
    assert 0 <= click.action_data["x"] <= 63
    assert 0 <= click.action_data["y"] <= 63

    game_over = FakeFrameData(FakeGameState.GAME_OVER, [1, 2])
    assert agent.is_done([], game_over) is False
    assert agent.choose_action([], game_over) is FakeGameAction.RESET

    won = FakeFrameData(FakeGameState.WIN, [1])
    assert agent.is_done([], won) is True


def test_random_adapter_refuses_an_empty_active_action_mask(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_adapter(monkeypatch)
    agent = module.MyAgent(game_id="smoke-v1", rng_seed=0)
    active = FakeFrameData(FakeGameState.NOT_FINISHED, [])

    with pytest.raises(NoLegalActionError):
        agent.choose_action([], active)
