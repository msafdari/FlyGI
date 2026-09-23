"""The connectome tiebreaker must change ties -- and nothing except ties.

These are comparison tests, not correctness tests. Each one measures the
component against the trivial alternative it replaces: the deterministic hash
that occupied the tie position before. A tiebreaker that cannot be distinguished
from that hash is inert, and a tiebreaker that outranks the controller's own
learning is unsafe. Both failures are checked here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np

from flygi.config import ControllerConfig
from flygi.controller import StateGraphPolicy

GRID = (64, 64)


class FakeState(Enum):
    NOT_PLAYED = 0
    NOT_FINISHED = 1
    GAME_OVER = 2
    WIN = 3


class FakeAction(Enum):
    RESET = 0
    ACTION1 = 1
    ACTION2 = 2
    ACTION3 = 3
    ACTION4 = 4
    ACTION5 = 5
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
    state: FakeState = FakeState.NOT_FINISHED
    available_actions: list[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])
    levels_completed: int = 0
    frame: list = field(default_factory=list)


class StubFly:
    """A fly whose preferences are dictated by the test, not by anatomy."""

    def __init__(self, preferences: dict[int, float]) -> None:
        self._preferences = preferences
        self.observations = 0

    def observe(self, grid, legal_action_ids) -> None:
        self.observations += 1

    def preference(self, action_id: int, x, y) -> float:
        return self._preferences.get(int(action_id), 0.0)

    def reset(self) -> None:
        self.observations = 0


def _config() -> ControllerConfig:
    return ControllerConfig(enabled=True)


def _frames(count: int, seed: int = 0) -> list[FakeFrame]:
    generator = np.random.default_rng(seed)
    return [
        FakeFrame(frame=[generator.integers(0, 16, size=GRID, dtype=np.int8)]) for _ in range(count)
    ]


def _trajectory(fly: object | None, *, turns: int = 6, seed: int = 0) -> list[int]:
    policy = StateGraphPolicy(FakeAction, _config(), decision_seed=7, fly=fly)
    return [policy.choose_action(frame).value for frame in _frames(turns, seed)]


def test_a_preferential_fly_changes_the_chosen_action() -> None:
    """Against the trivial alternative: the hash and the fly must differ."""

    without = _trajectory(None)
    with_fly = _trajectory(StubFly({1: 5.0, 2: 4.0, 3: 3.0, 4: 2.0, 5: 1.0}))
    assert without != with_fly, "the fly never reached the tie position; it is inert"


def test_a_constant_fly_is_indistinguishable_from_no_fly() -> None:
    """The fly must occupy the tie slot only, so a constant must change nothing."""

    assert _trajectory(StubFly({})) == _trajectory(None)
    assert _trajectory(StubFly(dict.fromkeys(range(8), 3.5))) == _trajectory(None)


def test_the_fly_orders_untried_candidates_by_preference() -> None:
    """On a first, fully tied turn the fly's ranking is the one that applies."""

    policy = StateGraphPolicy(FakeAction, _config(), decision_seed=7, fly=StubFly({4: 9.0}))
    assert policy.choose_action(_frames(1)[0]).value == 4


def test_the_fly_cannot_resurrect_an_already_attempted_action() -> None:
    """Attempt counts rank ahead of the fly, so a favourite is still not repeated."""

    favourite = 4
    fly = StubFly({favourite: 9.0})
    policy = StateGraphPolicy(FakeAction, _config(), decision_seed=7, fly=fly)
    chosen = [policy.choose_action(frame).value for frame in _frames(4)]
    assert chosen[0] == favourite
    assert chosen.count(favourite) == 1, (
        "the fly overrode the controller's attempt counter; it is not confined to ties"
    )


def test_the_fly_observes_every_grid_bearing_turn() -> None:
    fly = StubFly({})
    policy = StateGraphPolicy(FakeAction, _config(), decision_seed=7, fly=fly)
    for frame in _frames(5):
        policy.choose_action(frame)
    assert fly.observations == 5


class LearningStubFly(StubFly):
    """A fly that records the reinforcement the controller sends it."""

    def __init__(self) -> None:
        super().__init__({})
        self.reinforcements: list[float] = []

    def reinforce(self, value: float) -> None:
        self.reinforcements.append(float(value))


def _drive(policy, frames) -> None:
    for frame in frames:
        policy.choose_action(frame)


def test_clearing_a_level_reinforces_the_fly() -> None:
    """Without this the connectome has no teaching signal and cannot learn."""

    fly = LearningStubFly()
    policy = StateGraphPolicy(FakeAction, _config(), decision_seed=7, fly=fly)
    frames = _frames(4)
    policy.choose_action(frames[0])
    # The next frame reports a completed level, which the controller reconciles
    # against the pending transition as LEVEL_ADVANCE.
    frames[1].levels_completed = 1
    policy.choose_action(frames[1])
    assert 1.0 in fly.reinforcements, (
        "clearing a level sent no reward; the controller's own outcome signal "
        "is not reaching the mushroom body"
    )


def test_a_fatal_move_punishes_the_fly() -> None:
    fly = LearningStubFly()
    policy = StateGraphPolicy(FakeAction, _config(), decision_seed=7, fly=fly)
    frames = _frames(4)
    policy.choose_action(frames[0])
    frames[1].state = FakeState.GAME_OVER
    policy.choose_action(frames[1])
    assert -1.0 in fly.reinforcements, "a fatal move sent no punishment"


def test_an_ordinary_turn_sends_no_reinforcement() -> None:
    """Reinforcement on every turn would make the teaching signal meaningless."""

    fly = LearningStubFly()
    policy = StateGraphPolicy(FakeAction, _config(), decision_seed=7, fly=fly)
    _drive(policy, _frames(5))
    assert fly.reinforcements == [], (
        "uneventful turns produced reinforcement; the signal carries no information"
    )


def test_a_tiebreaker_without_a_learning_site_is_unaffected() -> None:
    """GridHashTiebreaker has no reinforce(); the controller must not require one."""

    fly = StubFly({1: 2.0})
    policy = StateGraphPolicy(FakeAction, _config(), decision_seed=7, fly=fly)
    frames = _frames(3)
    policy.choose_action(frames[0])
    frames[1].levels_completed = 1
    policy.choose_action(frames[1])  # must not raise
