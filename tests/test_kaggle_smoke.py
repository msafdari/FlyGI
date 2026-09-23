"""Smoke-test the Kaggle adapter without installing the official framework."""

from __future__ import annotations

import builtins
import contextlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from enum import Enum, StrEnum
from importlib import import_module
from pathlib import Path
from types import ModuleType, SimpleNamespace

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
    monkeypatch.setattr(module, "_find_runtime", lambda: None)
    agent = module.MyAgent(game_id="smoke-v1", rng_seed=20260919, allow_random_fallback=True)

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
    monkeypatch.setattr(module, "_find_runtime", lambda: None)
    agent = module.MyAgent(game_id="smoke-v1", rng_seed=0, allow_random_fallback=True)
    active = FakeFrameData(FakeGameState.NOT_FINISHED, [])

    with pytest.raises(NoLegalActionError):
        agent.choose_action([], active)


def test_connectome_adapter_passes_the_per_game_decision_seed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_adapter(monkeypatch)
    bundle = SimpleNamespace(node_count=166_700, edge_count=24_559_055)
    module._LOADED.update(
        {
            "available": True,
            "config": object(),
            "runtime_dir": Path("/attached/runtime"),
            "bundle": bundle,
            "projection": object(),
            "interface": {"internal_steps": 4},
        }
    )
    observed: dict[str, object] = {}

    def fake_build_connectome_policy(*args: object, **kwargs: object) -> SimpleNamespace:
        observed["args"] = args
        observed["kwargs"] = kwargs
        return SimpleNamespace(policy=SimpleNamespace(internal_steps=4))

    factory = import_module("flygi.arc.factory")
    monkeypatch.setattr(factory, "build_connectome_policy", fake_build_connectome_policy)

    agent = module.MyAgent(game_id="seeded-game", rng_seed=12345)

    assert agent._mode == "connectome"
    assert observed["kwargs"]["decision_seed"] == 12345


def test_adapter_fails_closed_when_runtime_is_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_adapter(monkeypatch)
    monkeypatch.delenv("FLYGI_RUNTIME_DIR", raising=False)
    monkeypatch.delenv("FLYGI_ALLOW_RANDOM_FALLBACK", raising=False)
    monkeypatch.delenv("KAGGLE_IS_COMPETITION_RERUN", raising=False)
    monkeypatch.setattr(module, "_KAGGLE_INPUT", tmp_path)

    with pytest.raises(module.RuntimePreflightError, match="Random fallback is disabled"):
        module.MyAgent(game_id="missing-runtime")


def test_competition_rerun_ignores_random_fallback_opt_in(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_adapter(monkeypatch)
    monkeypatch.delenv("FLYGI_RUNTIME_DIR", raising=False)
    monkeypatch.setenv("KAGGLE_IS_COMPETITION_RERUN", "1")
    monkeypatch.setenv("FLYGI_ALLOW_RANDOM_FALLBACK", "1")
    monkeypatch.setattr(module, "_KAGGLE_INPUT", tmp_path)

    with pytest.raises(module.RuntimePreflightError, match="official competition rerun"):
        module.MyAgent(game_id="competition", allow_random_fallback=True)


def test_preflight_prints_machine_readable_verified_identity(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_adapter(monkeypatch)
    bundle = SimpleNamespace(
        node_count=166_700,
        edge_count=24_559_055,
        manifest={
            "release": "male-cns:v1.0",
            "preprocessing": {"sign_mode": "heuristic"},
        },
        verified_hashes={
            "/attached/runtime/graph.npz": "a" * 64,
            "/attached/runtime/groups.npz": "b" * 64,
            "/attached/runtime/node_metadata.npz": "c" * 64,
        },
    )
    monkeypatch.setattr(
        module,
        "_shared_runtime",
        lambda: {
            "available": True,
            "bundle": bundle,
            "interface": {"internal_steps": 4},
        },
    )

    identity = module.preflight_runtime()
    output = capsys.readouterr().out.strip()

    assert output.startswith("FLYGI_PREFLIGHT=")
    assert json.loads(output.removeprefix("FLYGI_PREFLIGHT=")) == identity
    assert identity == {
        # No controller.yaml is attached here, so the adapter must still build
        # the pure connectome policy and say so.
        "controller": None,
        "edges": 24_559_055,
        "internal_steps": 4,
        "mode": "connectome",
        "nodes": 166_700,
        "release": "male-cns:v1.0",
        "sign_mode": "heuristic",
        "verified": True,
        "verified_output_hashes": {
            "graph.npz": "a" * 64,
            "groups.npz": "b" * 64,
            "node_metadata.npz": "c" * 64,
        },
    }


def test_preflight_fails_closed_without_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_adapter(monkeypatch)
    monkeypatch.setattr(
        module,
        "_shared_runtime",
        lambda: {"available": False, "reason": "hash mismatch"},
    )

    with pytest.raises(module.RuntimePreflightError, match="hash mismatch"):
        module.preflight_runtime()


def test_preflight_fails_closed_for_an_incomplete_runtime(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    (runtime / "graph.npz").write_bytes(b"not a graph")
    (runtime / "config.yaml").write_text(
        (REPOSITORY_ROOT / "configs" / "literal_rate_signed.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setenv("FLYGI_RUNTIME_DIR", str(runtime))
    module = _load_adapter(monkeypatch)

    with pytest.raises(module.RuntimePreflightError, match=r"manifest\.json"):
        module.preflight_runtime()


def test_wall_clock_guard_reports_done_past_the_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A notebook overrun loses the submission and the day's quota with it."""

    adapter = _load_adapter(monkeypatch)
    monkeypatch.setattr(adapter, "_WALL_CLOCK_DEADLINE_SECONDS", 0.0)
    assert adapter._deadline_exceeded()

    monkeypatch.setattr(adapter, "_WALL_CLOCK_DEADLINE_SECONDS", float("inf"))
    assert not adapter._deadline_exceeded()


def test_wall_clock_deadline_defaults_below_the_notebook_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Nine hours is the notebook limit; the guard must fire before it."""

    adapter = _load_adapter(monkeypatch)
    assert 0 < adapter._WALL_CLOCK_DEADLINE_SECONDS < 9 * 3600


def test_deployed_action_budget_exceeds_observed_completion_costs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """r11l was only ever completed at 164-333 actions; 80 could not reach it."""

    adapter = _load_adapter(monkeypatch)
    assert adapter.MyAgent.MAX_ACTIONS >= 500


def test_controller_config_discovery_is_opt_in(tmp_path: pytest.MonkeyPatch) -> None:
    """Without a staged controller.yaml the adapter must behave exactly as before."""

    import importlib.util

    spec = importlib.util.spec_from_file_location("_flygi_adapter_disc", ADAPTER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with contextlib.suppress(RuntimeError):
        spec.loader.exec_module(module)

    runtime = tmp_path / "runtime"  # type: ignore[operator]
    runtime.mkdir(parents=True)
    config = runtime.parent / "config.yaml"
    config.write_text("schema_version: 1\n", encoding="utf-8")
    assert module._find_controller_config(runtime, config) is None

    (runtime / "controller.yaml").write_text("schema_version: 1\n", encoding="utf-8")
    found = module._find_controller_config(runtime, config)
    assert found is not None and found.name == "controller.yaml"


def test_attached_controller_puts_the_connectome_in_the_tie_position(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The packaged agent must use the controller+fly path, not the plain policy.

    The trivial alternative here is the connectome policy the adapter has always
    built. If attaching a controller declaration does not change which policy is
    constructed, the packaging change is inert and no submission built from it
    would carry the controller at all.
    """

    from flygi.config import ControllerConfig

    module = _load_adapter(monkeypatch)
    built: dict[str, object] = {}

    class _StubFly:
        def __init__(self, *args: object, **kwargs: object) -> None:
            built["fly_kwargs"] = sorted(kwargs)

        def describe(self) -> dict:
            return {"kind": "stub"}

        def reset(self) -> None:
            return None

    class _StubPolicy:
        def __init__(self, *args: object, **kwargs: object) -> None:
            built["fly"] = kwargs.get("fly")

        internal_steps = 4

    controller_module = ModuleType("flygi.controller")
    controller_module.StateGraphPolicy = _StubPolicy  # type: ignore[attr-defined]
    tiebreak_module = ModuleType("flygi.controller.fly_tiebreak")
    tiebreak_module.FlyTiebreaker = _StubFly  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "flygi.controller", controller_module)
    monkeypatch.setitem(sys.modules, "flygi.controller.fly_tiebreak", tiebreak_module)

    bundle = SimpleNamespace(node_count=166_700, edge_count=24_559_055)
    monkeypatch.setattr(
        module,
        "_shared_runtime",
        lambda: {
            "available": True,
            "config": object(),
            "controller_config": SimpleNamespace(controller=ControllerConfig(enabled=True)),
            "controller_path": "/attached/controller.yaml",
            "runtime_dir": "/attached/runtime",
            "bundle": bundle,
            "projection": object(),
            "interface": {"internal_steps": 4},
        },
    )

    agent = module.MyAgent(game_id="controller-smoke", rng_seed=20260919)

    assert agent._mode == "controller-fly", "the attached controller was ignored"
    assert isinstance(built.get("fly"), _StubFly), "the connectome never reached the tie position"
    assert "bundle" in built["fly_kwargs"], (
        "the tiebreaker reloaded the graph instead of sharing it"
    )
