"""Lockstep-maze archetype (tu93): parser and planner pinned to planted boards.

The COMPARISON evidence for this component is the executor-driven offline
run recorded in WORKLOG/structured output: FapExecutor seated with this
archetype alone completes tu93 9/9 levels to GameState.WIN in 185 actions
(dossier hand-program target: 9/9 in 187), and the 25-game recognizer-frame
audit measured zero false matches and zero emitted actions on the other 24
games. These tests pin the measured parsing grammar and the planner's
lethality rules to planted frames so refactors cannot silently bend them.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from flygi.controller.fap_library import FapExecutor, Step
from flygi.controller.fap_archetypes.lockstep_maze import (
    LockstepMazeArchetype,
    _step_patroller,
)

_R0, _C0 = 9, 9  # planted lattice origin, unlike any real level's


def _blank() -> np.ndarray:
    grid = np.full((64, 64), 5, dtype=np.int16)
    grid[63, :] = 6  # full timer strip
    return grid


def _room(grid: np.ndarray, i: int, j: int, colour: int) -> None:
    r, c = _R0 + 6 * i, _C0 + 6 * j
    grid[r : r + 3, c : c + 3] = colour


def _eye(grid: np.ndarray, i: int, j: int, facing: tuple[int, int], colour: int) -> None:
    r, c = _R0 + 6 * i + 1, _C0 + 6 * j + 1
    grid[r + facing[0], c + facing[1]] = colour


def _door(grid: np.ndarray, i: int, j: int, di: int, dj: int) -> None:
    r, c = _R0 + 6 * i + 3 * di, _C0 + 6 * j + 3 * dj
    grid[r : r + 3, c : c + 3] = 2


def _avatar(grid: np.ndarray, i: int, j: int, facing: tuple[int, int] = (0, 1)) -> None:
    _room(grid, i, j, 9)
    _eye(grid, i, j, facing, 4)


def _corridor_maze() -> np.ndarray:
    """Rooms (0,0)-(0,1)-(1,1); avatar at (0,0), goal at (1,1)."""

    grid = _blank()
    _avatar(grid, 0, 0)
    _room(grid, 0, 1, 0)
    _room(grid, 1, 1, 14)
    _room(grid, 1, 0, 0)  # fourth room, doorless spur via (0,0)
    _door(grid, 0, 0, 0, 1)
    _door(grid, 0, 1, 1, 0)
    _door(grid, 0, 0, 1, 0)
    return grid


class TestMatch:
    def test_planted_maze_parses(self) -> None:
        arch = LockstepMazeArchetype()
        parse = arch.match(_corridor_maze())
        assert parse is not None
        assert parse.avatar == (0, 0)
        assert parse.goal == (1, 1)
        assert parse.rooms == frozenset({(0, 0), (0, 1), (1, 0), (1, 1)})
        assert frozenset({(0, 0), (0, 1)}) in parse.doors
        assert len(parse.doors) == 3

    def test_random_grids_abstain(self) -> None:
        arch = LockstepMazeArchetype()
        rng = np.random.default_rng(20260928)
        for _ in range(20):
            grid = rng.integers(0, 16, size=(64, 64)).astype(np.int16)
            assert arch.match(grid) is None

    def test_structured_glyph_board_abstains(self) -> None:
        # An ft09-flavour glyph lattice: tiles on an 8-pixel pitch.
        grid = np.full((64, 64), 5, dtype=np.int16)
        for i, r in enumerate((2, 10, 18)):
            for j, c in enumerate((4, 12, 20)):
                grid[r : r + 6, c : c + 6] = 9 if (i + j) % 2 else 8
        assert LockstepMazeArchetype().match(grid) is None

    def test_structured_pip_board_abstains(self) -> None:
        # An sc25-flavour pip board: colour-3 box with 0/2 cells.
        grid = np.full((64, 64), 5, dtype=np.int16)
        grid[47:64, 22:41] = 3
        for i, row in enumerate((49, 54, 59)):
            for j, col in enumerate((24, 29, 34)):
                grid[row : row + 3, col : col + 3] = 0 if (i + j) % 2 else 2
        assert LockstepMazeArchetype().match(grid) is None

    def test_missing_timer_row_abstains(self) -> None:
        grid = _corridor_maze()
        grid[63, :] = 5
        assert LockstepMazeArchetype().match(grid) is None

    def test_off_pitch_room_abstains(self) -> None:
        grid = _corridor_maze()
        grid[_R0 + 6 * 2 + 1 : _R0 + 6 * 2 + 4, _C0 : _C0 + 3] = 0  # 1px off
        assert LockstepMazeArchetype().match(grid) is None

    def test_unknown_colour_abstains(self) -> None:
        grid = _corridor_maze()
        _room(grid, 1, 0, 7)
        assert LockstepMazeArchetype().match(grid) is None

    def test_goalless_board_without_movers_abstains(self) -> None:
        grid = _corridor_maze()
        _room(grid, 1, 1, 0)  # goal painted over, no patroller to blame
        assert LockstepMazeArchetype().match(grid) is None

    def test_covered_goal_needs_memory(self) -> None:
        covered = _corridor_maze()
        _room(covered, 1, 1, 12)  # patroller covers the goal completely
        _eye(covered, 1, 1, (-1, 0), 15)
        fresh = LockstepMazeArchetype()
        assert fresh.match(covered) is None  # no within-life goal memory
        primed = LockstepMazeArchetype()
        open_frame = _corridor_maze()
        parse = primed.match(open_frame)
        assert parse is not None
        primed.next_actions(parse, open_frame)  # memorizes the goal room
        assert primed.match(covered) is not None
        primed.reset()  # per-life memory must not survive a reset
        assert primed.match(covered) is None


class TestPlanner:
    def test_one_step_per_call_along_doors(self) -> None:
        arch = LockstepMazeArchetype()
        grid = _corridor_maze()
        parse = arch.match(grid)
        steps = arch.next_actions(parse, grid)
        assert steps == [Step(action=4)]  # only door out of (0,0) toward goal
        # Closed loop: apply the move, rebuild the frame, ask again.
        grid2 = _corridor_maze()
        grid2[_R0 : _R0 + 3, _C0 : _C0 + 3] = 5  # avatar leaves (0,0)
        _room(grid2, 0, 0, 0)
        _room(grid2, 0, 1, 9)
        _eye(grid2, 0, 1, (0, 1), 4)
        parse2 = arch.match(grid2)
        steps2 = arch.next_actions(parse2, grid2)
        assert steps2 == [Step(action=2)]  # down onto the goal

    def test_timer_bound_abstains(self) -> None:
        arch = LockstepMazeArchetype()
        grid = _corridor_maze()
        grid[63, :] = 0
        grid[63, 0] = 6  # one pixel left: no 2-move plan fits
        parse = arch.match(grid)
        assert parse is not None
        assert arch.next_actions(parse, grid) == []

    def test_sentinel_frontal_corridor_has_no_path(self) -> None:
        # (0,0) avatar - (0,1) sentinel facing left - (0,2) goal, straight
        # corridor: the only entry into the sentinel's room is frontal.
        grid = _blank()
        _avatar(grid, 0, 0)
        _room(grid, 0, 1, 8)
        _eye(grid, 0, 1, (0, -1), 15)
        _room(grid, 0, 2, 14)
        _room(grid, 1, 0, 0)  # spur to reach the 4-room minimum
        _door(grid, 0, 0, 0, 1)
        _door(grid, 0, 1, 0, 1)
        _door(grid, 0, 0, 1, 0)
        arch = LockstepMazeArchetype()
        parse = arch.match(grid)
        assert parse is not None
        assert arch.next_actions(parse, grid) == []

    def test_sentinel_side_kill_is_planned(self) -> None:
        # Same corridor plus a loop below: the plan must go DOWN and kill
        # the sentinel from below instead of entering its faced room.
        grid = _blank()
        _avatar(grid, 0, 0)
        _room(grid, 0, 1, 8)
        _eye(grid, 0, 1, (0, -1), 15)  # faces the avatar's room
        _room(grid, 0, 2, 14)
        _room(grid, 1, 0, 0)
        _room(grid, 1, 1, 0)
        _door(grid, 0, 0, 0, 1)  # frontal door: lethal entry
        _door(grid, 0, 1, 0, 1)
        _door(grid, 0, 0, 1, 0)
        _door(grid, 1, 0, 0, 1)
        _door(grid, 1, 1, -1, 0)
        arch = LockstepMazeArchetype()
        parse = arch.match(grid)
        steps = arch.next_actions(parse, grid)
        assert steps == [Step(action=2)]  # down, around, up into its back
        assert arch._plan_actions == [4, 1, 4]

    def test_dormant_chaser_faced_room_avoided(self) -> None:
        # A dormant chaser is sentinel-like: its faced adjacent room kills.
        grid = _blank()
        _avatar(grid, 1, 0)
        _room(grid, 0, 0, 0)
        _room(grid, 0, 1, 13)
        _eye(grid, 0, 1, (0, -1), 15)  # faces (0,0)
        _room(grid, 1, 1, 0)
        _room(grid, 1, 2, 14)
        _door(grid, 1, 0, -1, 0)
        _door(grid, 0, 0, 0, 1)   # into the faced room: lethal
        _door(grid, 1, 0, 0, 1)
        _door(grid, 1, 1, 0, 1)
        arch = LockstepMazeArchetype()
        parse = arch.match(grid)
        steps = arch.next_actions(parse, grid)
        assert steps == [Step(action=4)]  # straight along row 1, never up

    def test_armed_chaser_faced_room_avoided(self) -> None:
        # An 11-eye chaser was triggered THIS tick and enters its faced
        # room next tick; stepping there is co-entry.
        grid = _blank()
        _avatar(grid, 1, 0)
        _room(grid, 1, 1, 0)
        _room(grid, 0, 1, 13)
        _eye(grid, 0, 1, (1, 0), 11)  # armed, about to enter (1,1)
        _room(grid, 1, 2, 14)
        _room(grid, 0, 0, 0)
        _door(grid, 1, 0, 0, 1)
        _door(grid, 1, 1, 0, 1)
        _door(grid, 0, 1, 1, 0)
        _door(grid, 0, 0, 0, 1)
        _door(grid, 0, 0, 1, 0)
        arch = LockstepMazeArchetype()
        parse = arch.match(grid)
        steps = arch.next_actions(parse, grid)
        # (1,1) is where the chaser lands next tick: the first move must
        # not be into it even though it lies on the shortest path.
        assert steps and steps[0] != Step(action=4)

    def test_patroller_world_closed_loop(self) -> None:
        """Drive the archetype against a simulated patroller world built
        from the measured rules; the sim raises on any lethal co-entry."""

        rooms = {(i, j) for i in range(2) for j in range(4)}
        doors = set()
        for i, j in rooms:
            for di, dj in ((0, 1), (1, 0)):
                if (i + di, j + dj) in rooms:
                    doors.add(frozenset({(i, j), (i + di, j + dj)}))
        avatar, goal = (0, 0), (0, 3)
        patroller, facing = (1, 3), (0, -1)  # patrols row 1

        def render() -> np.ndarray:
            grid = _blank()
            for i, j in rooms:
                _room(grid, i, j, 0)
            _room(grid, *goal, 14)
            _avatar(grid, *avatar)
            _room(grid, *patroller, 12)
            _eye(grid, *patroller, facing, 15)
            for pair in doors:
                (i, j), (i2, j2) = sorted(pair)
                _door(grid, i, j, i2 - i, j2 - j)
            return grid

        arch = LockstepMazeArchetype()
        deltas = {1: (-1, 0), 2: (1, 0), 3: (0, -1), 4: (0, 1)}
        for _ in range(20):
            grid = render()
            parse = arch.match(grid)
            assert parse is not None
            steps = arch.next_actions(parse, grid)
            assert len(steps) == 1 and 1 <= steps[0].action <= 4
            di, dj = deltas[steps[0].action]
            nxt = (avatar[0] + di, avatar[1] + dj)
            assert frozenset({avatar, nxt}) in doors, "planned through a wall"
            old_pat = patroller
            patroller, facing = _step_patroller(patroller, facing, frozenset(doors))
            assert patroller != nxt, "patroller co-entry (lethal)"
            assert not (old_pat == nxt and patroller == avatar), "swap-through"
            avatar = nxt
            if avatar == goal:
                break
        assert avatar == goal

    def test_step_patroller_bounces_at_walls(self) -> None:
        doors = frozenset({frozenset({(0, 0), (0, 1)}), frozenset({(0, 1), (0, 2)})})
        pos, fac = (0, 1), (0, 1)
        pos, fac = _step_patroller(pos, fac, doors)
        assert (pos, fac) == ((0, 2), (0, -1))  # advanced, flipped at wall
        pos, fac = _step_patroller(pos, fac, doors)
        assert (pos, fac) == ((0, 1), (0, -1))


class TestExecutorSeating:
    def test_executor_proposes_on_planted_board_abstains_off_it(self) -> None:
        executor = FapExecutor(archetypes=[LockstepMazeArchetype()])
        grid = _corridor_maze()
        executor.observe(grid)
        step = executor.propose(grid)
        assert step == Step(action=4)
        executor.notify_reset()
        noise = np.random.default_rng(7).integers(0, 16, (64, 64)).astype(np.int16)
        executor.observe(noise)
        assert executor.propose(noise) is None


_FRAMES = Path(__file__).resolve().parents[1] / "results/diagnostics/recognizer_frames.npz"


@pytest.mark.skipif(not _FRAMES.exists(), reason="recognizer frame dump not present")
class TestRecognizerFrameAudit:
    def test_all_real_tu93_frames_match(self) -> None:
        frames = np.load(_FRAMES)["tu93"]
        arch = LockstepMazeArchetype()
        for frame in frames:
            assert arch.match(np.asarray(frame, dtype=np.int16)) is not None

    def test_every_other_game_abstains(self) -> None:
        bundle = np.load(_FRAMES)
        for key in bundle.keys():
            if key == "tu93":
                continue
            arch = LockstepMazeArchetype()
            for frame in bundle[key]:
                grid = np.asarray(frame, dtype=np.int16)
                parse = arch.match(grid)
                if parse is not None:
                    assert arch.next_actions(parse, grid) == [], key
