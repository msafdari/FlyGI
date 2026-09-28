"""Seating contract for the FAP override inside StateGraphPolicy.

The invariant that makes fap_library deployable is measured here at the unit
level: an ABSTAINING executor leaves the policy byte-identical to one built
without it (the 25-game audit measured the same at system level), and a
MATCHING executor overrides the ranking with the program's exact step. The
comparison evidence for the component itself lives under H-FAP-PROGRAMS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np

from flygi.config import ControllerConfig
from flygi.controller import StateGraphPolicy
from flygi.controller.fap_library import FapExecutor

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
    def from_id(cls, identifier: int) -> "FakeAction":
        return cls(identifier)


@dataclass
class FakeFrame:
    state: FakeState = FakeState.NOT_FINISHED
    available_actions: list[int] = field(default_factory=lambda: [1, 2, 3, 4, 5, 6])
    levels_completed: int = 0
    frame: list = field(default_factory=list)


def _random_frames(count: int, seed: int = 0) -> list[FakeFrame]:
    generator = np.random.default_rng(seed)
    return [
        FakeFrame(frame=[generator.integers(0, 16, size=GRID, dtype=np.int8)])
        for _ in range(count)
    ]


def _glyph_grid() -> np.ndarray:
    """The planted board from test_fap_library: one unsatisfied 0-cell whose
    program click lands at (x=7, y=5)."""

    grid = np.full(GRID, 5, dtype=np.int8)
    glyph = np.array([[0, 2, 2], [2, 8, 2], [2, 2, 2]], dtype=np.int8)
    rows, cols = [2, 10, 18], [4, 12, 20]
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            for br in range(3):
                for bc in range(3):
                    value = glyph[br, bc] if (i, j) == (1, 1) else 9
                    grid[r + 2 * br : r + 2 * br + 2, c + 2 * bc : c + 2 * bc + 2] = value
    return grid


def _actions_taken(fap: object | None, frames: list[FakeFrame]) -> list[tuple]:
    policy = StateGraphPolicy(
        FakeAction, ControllerConfig(enabled=True), decision_seed=7, fap=fap
    )
    taken = []
    for frame in frames:
        action = policy.choose_action(frame)
        taken.append((action.value, dict(action.action_data)))
    return taken


class TestAbstentionIdentity:
    def test_abstaining_executor_is_byte_identical(self) -> None:
        frames_a = _random_frames(12, seed=3)
        frames_b = _random_frames(12, seed=3)
        without = _actions_taken(None, frames_a)
        with_fap = _actions_taken(FapExecutor(), frames_b)
        assert with_fap == without

    def test_abstaining_executor_reports_zero_fired(self) -> None:
        policy = StateGraphPolicy(
            FakeAction,
            ControllerConfig(enabled=True),
            decision_seed=7,
            fap=FapExecutor(),
        )
        for frame in _random_frames(6, seed=5):
            policy.choose_action(frame)
        assert policy.diagnostics()["fap_fired_turns"] == 0


class TestOverride:
    def test_matching_frame_overrides_with_program_click(self) -> None:
        policy = StateGraphPolicy(
            FakeAction,
            ControllerConfig(enabled=True),
            decision_seed=7,
            fap=FapExecutor(),
        )
        frame = FakeFrame(available_actions=[6], frame=[_glyph_grid()])
        action = policy.choose_action(frame)
        assert action.value == 6
        assert action.action_data == {"x": 7, "y": 5}
        assert policy.diagnostics()["fap_fired_turns"] == 1
        assert policy.records[-1].mode == "fap"

    def test_illegal_proposal_falls_back_to_champion(self) -> None:
        policy = StateGraphPolicy(
            FakeAction,
            ControllerConfig(enabled=True),
            decision_seed=7,
            fap=FapExecutor(),
        )
        # The archetype matches and proposes a click, but ACTION6 is not
        # legal here; the champion must choose among the declared actions.
        frame = FakeFrame(available_actions=[1, 2], frame=[_glyph_grid()])
        action = policy.choose_action(frame)
        assert action.value in (1, 2)
        assert policy.diagnostics()["fap_fired_turns"] == 0


class _RecordingFap:
    """Stub executor recording seam calls; propose returns a fixed step."""

    def __init__(self, step=None, raise_on_propose: bool = False) -> None:
        self.step = step
        self.raise_on_propose = raise_on_propose
        self.calls: list[str] = []

    def observe(self, grid) -> None:
        self.calls.append("observe")

    def propose(self, grid):
        self.calls.append("propose")
        if self.raise_on_propose:
            raise RuntimeError("executor bug")
        return self.step

    def reject_last(self) -> None:
        self.calls.append("reject_last")

    def notify_reset(self) -> None:
        self.calls.append("notify_reset")

    def notify_level_advance(self) -> None:
        self.calls.append("notify_level_advance")

    def describe(self) -> dict:
        return {"kind": "stub"}


class TestSeamHardening:
    def test_executor_exception_degrades_to_abstention(self) -> None:
        fap = _RecordingFap(raise_on_propose=True)
        policy = StateGraphPolicy(
            FakeAction, ControllerConfig(enabled=True), decision_seed=7, fap=fap
        )
        frames = _random_frames(4, seed=9)
        baseline = _actions_taken(None, _random_frames(4, seed=9))
        taken = []
        for frame in frames:
            action = policy.choose_action(frame)
            taken.append((action.value, dict(action.action_data)))
        assert taken == baseline  # abstention, never random substitution
        assert policy.diagnostics()["fap_errors"] == 4
        assert policy.diagnostics()["fap_fired_turns"] == 0

    def test_hard_banned_proposal_is_refused_and_reported(self) -> None:
        from flygi.controller.state_graph import ActionCandidate

        from flygi.controller.fap_library import Step

        fap = _RecordingFap(step=Step(action=6, x=7, y=5))
        policy = StateGraphPolicy(
            FakeAction, ControllerConfig(enabled=True), decision_seed=7, fap=fap
        )
        grid = _glyph_grid()
        first = FakeFrame(available_actions=[1, 6], frame=[grid.copy()])
        action = policy.choose_action(first)
        assert action.value == 6 and policy.diagnostics()["fap_fired_turns"] == 1
        # Mark the program's click as graph-proven fatal, then present the
        # same board again: the override must refuse it and tell the
        # executor, and the champion must choose instead.
        state_key = policy._pending.source_key
        node = policy._graph.node(state_key)
        node.hard_bans.add(ActionCandidate(6, x=7, y=5))
        second = FakeFrame(available_actions=[1, 6], frame=[grid.copy()])
        chosen = policy.choose_action(second)
        assert policy.diagnostics()["fap_banned"] == 1
        assert "reject_last" in fap.calls
        assert not (chosen.value == 6 and chosen.action_data == {"x": 7, "y": 5})

    def test_forced_reset_notifies_executor(self) -> None:
        fap = _RecordingFap()
        policy = StateGraphPolicy(
            FakeAction, ControllerConfig(enabled=True), decision_seed=7, fap=fap
        )
        frame = FakeFrame(
            state=FakeState.GAME_OVER,
            available_actions=[0],
            frame=[_random_frames(1, seed=1)[0].frame[0]],
        )
        action = policy.choose_action(frame)
        assert action.value == 0
        assert "notify_reset" in fap.calls


class TestExecutorLifecycle:
    def test_reset_rearms_swallow_retry_and_clears_queue(self) -> None:
        executor = FapExecutor()
        grid = _glyph_grid()
        executor.observe(grid)
        first = executor.propose(grid)
        assert first is not None
        executor.observe(grid)  # unchanged: swallow retry arms
        assert executor.propose(grid) == first
        executor.notify_reset()
        assert executor._queue == [] and executor._retried_swallow is False
        # A fresh life gets a fresh retry budget on the same board.
        executor.observe(grid)
        again = executor.propose(grid)
        assert again == first
        executor.observe(grid)
        assert executor.propose(grid) == again

    def test_reject_last_does_not_arm_swallow_retry(self) -> None:
        executor = FapExecutor()
        grid = _glyph_grid()
        executor.observe(grid)
        step = executor.propose(grid)
        assert step is not None
        executor.reject_last()
        executor.observe(grid)  # unchanged frame, but nothing was executed
        assert executor._retried_swallow is False

    def test_emission_guard_counts_emissions_not_visits(self) -> None:
        executor = FapExecutor()
        grid = _random_frames(1, seed=2)[0].frame[0]
        for _ in range(10):
            executor.observe(grid)
            assert executor.propose(grid) is None  # abstains, never matches
        # Ten abstaining visits must not poison the frame for a later match.
        assert executor._frame_emissions.get(
            np.asarray(grid, dtype=np.int16).tobytes(), 0
        ) == 0
