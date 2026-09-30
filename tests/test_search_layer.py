"""Seating and mechanism contract for the H-ONLINE-SEARCH layer.

The invariant that makes search_layer deployable is measured here at the unit
level, mirroring test_fap_seating: an IDLE layer leaves the policy
byte-identical to one built without it, and an ENGAGED layer emits the
preregistered mechanism -- RESET + prefix replay, frontier expansion, the
1,500-action budget with permanent per-level abstention, program banking and
execution. The premise evidence for the mechanism itself lives under
H-ONLINE-SEARCH (11 of 25 games, results/online_search_premise.json).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np

from flygi.config import ControllerConfig
from flygi.controller import StateGraphPolicy
from flygi.controller.search_layer import (
    LEVEL_ACTION_BUDGET,
    STUCK_OBSERVE_TURNS,
    OnlineSearchLayer,
    Step,
)

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
    available_actions: list[int] = field(default_factory=lambda: [1, 2, 3, 4, 5, 6])
    levels_completed: int = 0
    frame: list = field(default_factory=list)


def _random_frames(count: int, seed: int = 0) -> list[FakeFrame]:
    generator = np.random.default_rng(seed)
    return [
        FakeFrame(frame=[generator.integers(0, 16, size=GRID, dtype=np.int8)])
        for _ in range(count)
    ]


def _actions_taken(search: object | None, frames: list[FakeFrame]) -> list[tuple]:
    policy = StateGraphPolicy(
        FakeAction, ControllerConfig(enabled=True), decision_seed=7, search=search
    )
    taken = []
    for frame in frames:
        action = policy.choose_action(frame)
        taken.append((action.value, dict(action.action_data)))
    return taken


class TinyGame:
    """Deterministic FSM the layer explores: states are ints drawn as grids.

    RESET returns to the start state. ``swallow_after_reset`` reproduces the
    measured sc25/g50t quirk: the first non-reset action after every RESET is
    swallowed completely.
    """

    def __init__(
        self,
        transitions: dict[tuple[int, int], int],
        *,
        start: int = 0,
        legal: tuple[int, ...] = (1, 2),
        swallow_after_reset: bool = False,
    ) -> None:
        self.transitions = transitions
        self.start = start
        self.state = start
        self.legal = tuple(legal)
        self.swallow_after_reset = swallow_after_reset
        self._swallow_next = swallow_after_reset

    def grid(self) -> np.ndarray:
        grid = np.zeros(GRID, dtype=np.int8)
        value = self.state
        for i in range(8):
            grid[10, i] = 1 + (value % 8)
            value //= 8
        return grid

    def apply(self, step: Step) -> None:
        if step.action == 0:
            self.state = self.start
            self._swallow_next = self.swallow_after_reset
            return
        if self._swallow_next:
            self._swallow_next = False
            return
        self.state = self.transitions.get((self.state, step.action), self.state)


def _drive(
    layer: OnlineSearchLayer,
    game: TinyGame,
    turns: int,
    *,
    win_state: int | None = None,
) -> list[Step | None]:
    """The policy-style loop at unit scale: observe, propose, apply, and the
    host-side level-advance notification the reconciler would deliver."""

    emitted: list[Step | None] = []
    for _ in range(turns):
        grid = game.grid()
        layer.observe(grid, game.legal)
        step = layer.propose(grid)
        emitted.append(step)
        if step is None:
            continue
        game.apply(step)
        if win_state is not None and game.state == win_state:
            layer.notify_level_advance()
            break
    return emitted


def _idle_spin(layer: OnlineSearchLayer, game: TinyGame, turns: int) -> None:
    for _ in range(turns):
        grid = game.grid()
        layer.observe(grid, game.legal)
        assert layer.propose(grid) is None


class TestIdleAbstention:
    def test_idle_layer_is_byte_identical(self) -> None:
        frames_a = _random_frames(12, seed=3)
        frames_b = _random_frames(12, seed=3)
        without = _actions_taken(None, frames_a)
        with_search = _actions_taken(OnlineSearchLayer(), frames_b)
        assert with_search == without

    def test_idle_layer_reports_zero_engagement(self) -> None:
        policy = StateGraphPolicy(
            FakeAction,
            ControllerConfig(enabled=True),
            decision_seed=7,
            search=OnlineSearchLayer(),
        )
        for frame in _random_frames(6, seed=5):
            policy.choose_action(frame)
        diagnostics = policy.diagnostics()
        assert diagnostics["search_engaged_turns"] == 0
        assert diagnostics["search_programs_found"] == 0
        assert diagnostics["search"]["engaged"] is False


class TestEngagementCounter:
    def test_engages_exactly_at_the_preregistered_signal(self) -> None:
        layer = OnlineSearchLayer()
        game = TinyGame({})
        _idle_spin(layer, game, STUCK_OBSERVE_TURNS - 1)
        grid = game.grid()
        layer.observe(grid, game.legal)
        step = layer.propose(grid)
        assert step is not None and step.action == 0  # the traversal RESET
        assert layer.engaged

    def test_level_advance_restarts_the_counter(self) -> None:
        layer = OnlineSearchLayer()
        game = TinyGame({})
        _idle_spin(layer, game, 50)
        layer.notify_level_advance()
        _idle_spin(layer, game, STUCK_OBSERVE_TURNS - 1)
        assert not layer.engaged

    def test_forced_reset_does_not_restart_the_counter(self) -> None:
        # PREREGISTERED signal: no level ADVANCE for 75 turns. A forced
        # reset is not an advance -- measured on sp80 (a death every ~31
        # champion turns), a counter restarting on forced resets would
        # never reach 75 at all.
        layer = OnlineSearchLayer()
        game = TinyGame({})
        _idle_spin(layer, game, 50)
        layer.notify_reset()
        _idle_spin(layer, game, STUCK_OBSERVE_TURNS - 51)
        grid = game.grid()
        layer.observe(grid, game.legal)  # the 75th observe since the start
        step = layer.propose(grid)
        assert step is not None and step.action == 0
        assert layer.engaged


class TestBudget:
    def test_budget_exhaustion_is_permanent_for_the_level(self) -> None:
        # An effectively unbounded tree: every action reaches a fresh state.
        transitions = {}
        for state in range(5000):
            for action in (1, 2, 3, 4):
                transitions[(state, action)] = state * 4 + action
        game = TinyGame(transitions, legal=(1, 2, 3, 4))
        layer = OnlineSearchLayer()
        emitted = _drive(layer, game, STUCK_OBSERVE_TURNS + LEVEL_ACTION_BUDGET + 60)
        assert sum(step is not None for step in emitted) == LEVEL_ACTION_BUDGET
        report = layer.describe()
        assert report["level_abstain"] is True
        assert report["abstain_reason"] == "action-budget-exhausted"
        assert report["actions_emitted"] == LEVEL_ACTION_BUDGET
        # Permanent for this level: nothing more is ever proposed.
        late = _drive(layer, game, 50)
        assert all(step is None for step in late)

    def test_level_advance_resets_the_budget(self) -> None:
        transitions = {}
        for state in range(5000):
            for action in (1, 2, 3, 4):
                transitions[(state, action)] = state * 4 + action
        game = TinyGame(transitions, legal=(1, 2, 3, 4))
        layer = OnlineSearchLayer()
        _drive(layer, game, STUCK_OBSERVE_TURNS + LEVEL_ACTION_BUDGET + 10)
        assert layer.describe()["level_abstain"] is True
        layer.notify_level_advance()
        report = layer.describe()
        assert report["level_abstain"] is False
        assert report["actions_emitted"] == 0


class TestReplayEmissionOrder:
    def test_reset_prefix_expansion_order(self) -> None:
        # Root 0 has two moving branches; node 10 has one no-op and one
        # moving branch, so the trace exercises every traversal shape:
        # direct expansion, RESET return, prefix replay, and the
        # at-the-node continuation after a no-op child.
        game = TinyGame({(0, 1): 10, (0, 2): 20, (10, 2): 30})
        layer = OnlineSearchLayer()
        emitted = _drive(layer, game, STUCK_OBSERVE_TURNS + 8)
        actions = [step.action for step in emitted if step is not None]
        assert actions[:8] == [0, 1, 0, 2, 0, 1, 1, 2]

    def test_post_reset_swallow_is_probed_once(self) -> None:
        # The measured sc25/g50t quirk: the first post-reset action is
        # swallowed; the layer must re-emit it exactly once and continue.
        game = TinyGame({(0, 1): 10, (0, 2): 20}, swallow_after_reset=True)
        layer = OnlineSearchLayer()
        emitted = _drive(layer, game, STUCK_OBSERVE_TURNS + 10)
        actions = [step.action for step in emitted if step is not None]
        # Every post-reset first action is probed once: 1 swallowed, 1 real.
        assert actions[:6] == [0, 1, 1, 0, 2, 2]
        # Both children were genuinely reached despite the swallow.
        assert layer.describe()["nodes"] >= 3


class TestBankingAndExecution:
    def test_program_is_banked_when_its_step_completes_the_level(self) -> None:
        game = TinyGame({(0, 1): 10, (10, 2): 99})
        layer = OnlineSearchLayer()
        _drive(layer, game, STUCK_OBSERVE_TURNS + 30, win_state=99)
        report = layer.describe()
        assert layer.programs_found == 1
        assert report["banked_programs"] == 1
        assert report["engaged"] is False
        assert report["actions_emitted"] == 0  # per-level counters reset

    def test_banked_program_is_executed_directly_on_a_banked_root(self) -> None:
        game = TinyGame({(0, 1): 10, (10, 2): 99})
        layer = OnlineSearchLayer()
        _drive(layer, game, STUCK_OBSERVE_TURNS + 30, win_state=99)
        assert layer.programs_found == 1
        # The next level starts on the same board (the banked root): after
        # the stuck signal the layer must replay RESET + program directly,
        # with no exploration in between.
        game.state = 0
        _idle_spin(layer, game, STUCK_OBSERVE_TURNS - 1)
        emitted = _drive(layer, game, 10, win_state=99)
        actions = [step.action for step in emitted if step is not None]
        assert actions == [0, 1, 2]
        assert layer.describe()["programs_executed"] == 1

    def test_stale_bank_is_dropped_and_exploration_resumes(self) -> None:
        game = TinyGame({(0, 1): 10, (10, 2): 99})
        layer = OnlineSearchLayer()
        _drive(layer, game, STUCK_OBSERVE_TURNS + 30, win_state=99)
        # Same root, but the banked program no longer completes the level.
        game.transitions = {(0, 1): 10}
        game.state = 0
        _idle_spin(layer, game, STUCK_OBSERVE_TURNS - 1)
        _drive(layer, game, 6)
        report = layer.describe()
        assert report["banked_programs"] == 0  # the failed program is dropped
        assert report["engaged"] is True  # back to exploring
        assert report["nodes"] >= 2  # the tree is being rebuilt
        assert report["programs_executed"] == 0


class TestRejectLast:
    def test_rejected_step_rolls_back_the_budget(self) -> None:
        layer = OnlineSearchLayer()
        game = TinyGame({})
        _idle_spin(layer, game, STUCK_OBSERVE_TURNS - 1)
        grid = game.grid()
        layer.observe(grid, game.legal)
        step = layer.propose(grid)
        assert step is not None and step.action == 0
        layer.reject_last()
        assert layer.describe()["actions_emitted"] == 0

    def test_repeated_reset_rejection_fails_safe(self) -> None:
        layer = OnlineSearchLayer()
        game = TinyGame({})
        _idle_spin(layer, game, STUCK_OBSERVE_TURNS - 1)
        for _ in range(3):
            grid = game.grid()
            layer.observe(grid, game.legal)
            step = layer.propose(grid)
            assert step is not None and step.action == 0
            layer.reject_last()
        report = layer.describe()
        assert report["level_abstain"] is True
        assert report["abstain_reason"] == "reset-rejected"

    def test_rejected_expansion_consumes_the_branch(self) -> None:
        game = TinyGame({(0, 1): 10, (0, 2): 20})
        layer = OnlineSearchLayer()
        _idle_spin(layer, game, STUCK_OBSERVE_TURNS - 1)
        # Engagement RESET, then the first expansion (branch 1).
        grid = game.grid()
        layer.observe(grid, game.legal)
        reset = layer.propose(grid)
        assert reset is not None and reset.action == 0
        game.apply(reset)
        grid = game.grid()
        layer.observe(grid, game.legal)
        first = layer.propose(grid)
        assert first == Step(action=1)
        layer.reject_last()  # e.g. hard-banned: the step never ran
        # The refused branch is consumed; after the conservative restart the
        # next expansion from the root must be branch 2, never branch 1.
        emitted = _drive(layer, game, 6)
        actions = [step.action for step in emitted if step is not None]
        assert actions[:2] == [0, 2]


class _RecordingSearch:
    """Stub layer recording seam calls; propose returns a fixed step."""

    def __init__(self, step=None, raise_on_propose: bool = False) -> None:
        self.step = step
        self.raise_on_propose = raise_on_propose
        self.calls: list[str] = []
        self.engaged = step is not None

    def observe(self, grid, legal_ids=None) -> None:
        self.calls.append("observe")

    def propose(self, grid):
        self.calls.append("propose")
        if self.raise_on_propose:
            raise RuntimeError("layer bug")
        return self.step

    def reject_last(self) -> None:
        self.calls.append("reject_last")

    def notify_reset(self) -> None:
        self.calls.append("notify_reset")

    def notify_level_advance(self) -> None:
        self.calls.append("notify_level_advance")

    def describe(self) -> dict:
        return {"kind": "stub"}


class TestPolicySeating:
    def test_search_step_overrides_with_mode_search(self) -> None:
        search = _RecordingSearch(step=Step(action=1))
        policy = StateGraphPolicy(
            FakeAction, ControllerConfig(enabled=True), decision_seed=7, search=search
        )
        frame = _random_frames(1, seed=11)[0]
        action = policy.choose_action(frame)
        assert action.value == 1
        assert policy.records[-1].mode == "search"
        assert policy.diagnostics()["search_engaged_turns"] == 1

    def test_search_reset_is_emitted_despite_the_legal_mask(self) -> None:
        # MEASURED 2026-09-30: the engine accepts RESET on active frames
        # while never listing it in available_actions.
        search = _RecordingSearch(step=Step(action=0))
        policy = StateGraphPolicy(
            FakeAction, ControllerConfig(enabled=True), decision_seed=7, search=search
        )
        frame = _random_frames(1, seed=12)[0]
        action = policy.choose_action(frame)
        assert action.value == 0
        assert policy.records[-1].mode == "search-reset"
        assert policy.records[-1].forced_reset is False

    def test_illegal_proposal_is_rejected_back_to_the_layer(self) -> None:
        search = _RecordingSearch(step=Step(action=5))
        policy = StateGraphPolicy(
            FakeAction, ControllerConfig(enabled=True), decision_seed=7, search=search
        )
        frame = FakeFrame(
            available_actions=[1, 2], frame=[_random_frames(1, seed=13)[0].frame[0]]
        )
        action = policy.choose_action(frame)
        assert action.value in (1, 2)
        assert "reject_last" in search.calls

    def test_layer_exception_degrades_to_abstention(self) -> None:
        search = _RecordingSearch(raise_on_propose=True)
        policy = StateGraphPolicy(
            FakeAction, ControllerConfig(enabled=True), decision_seed=7, search=search
        )
        frames = _random_frames(4, seed=9)
        baseline = _actions_taken(None, _random_frames(4, seed=9))
        taken = []
        for frame in frames:
            action = policy.choose_action(frame)
            taken.append((action.value, dict(action.action_data)))
        assert taken == baseline  # abstention, never random substitution
        assert policy.diagnostics()["search_errors"] == 4

    def test_fap_override_preempts_the_search_consult(self) -> None:
        class _FiringFap:
            def observe(self, grid) -> None:
                pass

            def propose(self, grid):
                return Step(action=2)

            def reject_last(self) -> None:
                pass

            def notify_reset(self) -> None:
                pass

            def notify_level_advance(self) -> None:
                pass

            def describe(self) -> dict:
                return {"kind": "stub-fap"}

        search = _RecordingSearch(step=Step(action=1))
        policy = StateGraphPolicy(
            FakeAction,
            ControllerConfig(enabled=True),
            decision_seed=7,
            fap=_FiringFap(),
            search=search,
        )
        frame = _random_frames(1, seed=14)[0]
        action = policy.choose_action(frame)
        assert action.value == 2  # the FAP step, not the search step
        assert policy.records[-1].mode == "fap"
        assert "observe" in search.calls  # the layer still saw the frame
        assert "propose" not in search.calls

    def test_forced_reset_notifies_the_layer(self) -> None:
        search = _RecordingSearch()
        policy = StateGraphPolicy(
            FakeAction, ControllerConfig(enabled=True), decision_seed=7, search=search
        )
        frame = FakeFrame(
            state=FakeState.GAME_OVER,
            available_actions=[0],
            frame=[_random_frames(1, seed=1)[0].frame[0]],
        )
        action = policy.choose_action(frame)
        assert action.value == 0
        assert "notify_reset" in search.calls


class TestBudgetAwareEngagement:
    """Registered gate-(a) amendment: engage only with budget to finish."""

    def test_short_budget_blocks_engagement(self) -> None:
        import numpy as np
        from flygi.controller.search_layer import OnlineSearchLayer

        layer = OnlineSearchLayer()
        layer.set_remaining_budget(500)
        grid = np.random.default_rng(0).integers(0, 16, (64, 64), dtype=np.int16)
        for _ in range(120):
            layer.observe(grid, (1, 2, 3, 4, 6))
            assert layer.propose(grid) is None
        assert not layer.engaged

    def test_unknown_budget_engages(self) -> None:
        import numpy as np
        from flygi.controller.search_layer import OnlineSearchLayer

        layer = OnlineSearchLayer()
        layer.set_remaining_budget(None)
        grid = np.random.default_rng(0).integers(0, 16, (64, 64), dtype=np.int16)
        engaged = False
        for _ in range(120):
            layer.observe(grid, (1, 2, 3, 4, 6))
            layer.propose(grid)
            engaged = engaged or layer.engaged
        assert engaged

    def test_ample_budget_engages(self) -> None:
        import numpy as np
        from flygi.controller.search_layer import OnlineSearchLayer

        layer = OnlineSearchLayer()
        layer.set_remaining_budget(5000)
        grid = np.random.default_rng(0).integers(0, 16, (64, 64), dtype=np.int16)
        engaged = False
        for _ in range(120):
            layer.observe(grid, (1, 2, 3, 4, 6))
            layer.propose(grid)
            engaged = engaged or layer.engaged
        assert engaged
