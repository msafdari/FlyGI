"""Pattern-key archetype (ls20): parser, transforms and planner on planted boards.

The COMPARISON evidence for this component is the executor-driven offline
run recorded in the structured output: FapExecutor seated with this
archetype alone completes ls20 levels 1-5 to score 5 in 190 actions
(dossier hand-program target: 5 levels in 226), and the 25-game
recognizer-frame audit measured zero false matches on the other 24 games
(960 frames) while all 40 ls20 frames parsed.  The parser + transition
model was additionally validated exact on all 265 transitions of the
dossier's verified composite replay (key cell, carried pattern, ink,
rings, timer; win instants 13/58/107/174/226/265), with one measured
drain-free device landing (L1 frame 6) tolerated.  These tests pin the
measured grammar, the transform algebra and the planner's use of every
device class to planted frames so refactors cannot silently bend them.
"""

from __future__ import annotations

import numpy as np

from flygi.controller.fap_archetypes.pattern_key import (
    _CELL,
    _F,
    _INK_NEXT,
    _ROT,
    _World,
    KeyMazeParse,
    PatternKeyArchetype,
    _detect_cycle,
    _parse,
    _pat_of,
    _plan_route,
    _step,
)
from flygi.controller.fap_library import Step

# --------------------------------------------------------- planted-board kit


def _blank() -> np.ndarray:
    """Wall everywhere plus the measured UI fixtures (chrome margin,
    display box frame, full timer bar, three lives)."""

    grid = np.full((64, 64), 4, dtype=np.int16)
    grid[0:52, 0:4] = 5  # left chrome margin
    grid[53:63, 1:11] = 5  # display interior (cols 0/11 stay wall)
    grid[60, 12:64] = 5
    grid[61:63, 12] = 5
    grid[61:63, 13:55] = 11  # full timer
    grid[61:63, 55:64] = 5
    for c0 in (56, 59, 62):  # three 2x2 colour-8 life blocks
        grid[61:63, c0 : c0 + 2] = 8
    grid[63, 12:64] = 5
    return grid


def _floor(grid: np.ndarray, cells) -> None:
    for R, C in cells:
        grid[R : R + _CELL, C : C + _CELL] = 3


def _key(grid: np.ndarray, cell) -> None:
    R, C = cell
    grid[R : R + 2, C : C + _CELL] = 12
    grid[R + 2 : R + _CELL, C : C + _CELL] = 9


_SPRITES = {
    "rot": ((3, 0, 3), (1, 0, 0), (3, 1, 3)),
    "shift": ((0, 3, 3), (3, 0, 0), (3, 0, 3)),
    "ink": ((9, 14, 14), (9, 0, 8), (12, 12, 8)),
    "ring": ((11, 11, 11), (11, 3, 11), (11, 11, 11)),
}


def _device(grid: np.ndarray, cell, kind: str) -> None:
    R, C = cell
    _floor(grid, [cell])
    grid[R + 1 : R + 4, C + 1 : C + 4] = np.array(_SPRITES[kind], dtype=np.int16)


def _goal_box(grid: np.ndarray, cell, pattern: str, ink: int) -> None:
    """A 9x9 goal box whose glyph centre sits on the cell centre."""

    R, C = cell[0] - 2, cell[1] - 2
    grid[R : R + 9, C : C + 9] = 3
    grid[R + 1 : R + 8, C + 1 : C + 8] = 5
    p = _pat_of(pattern)
    for i in range(3):
        for j in range(3):
            if p >> (3 * i + j) & 1:
                grid[R + 3 + i, C + 3 + j] = ink


def _display(grid: np.ndarray, pattern: str, ink: int) -> None:
    p = _pat_of(pattern)
    for i, r in enumerate((55, 57, 59)):
        for j, c in enumerate((3, 5, 7)):
            if p >> (3 * i + j) & 1:
                grid[r : r + 2, c : c + 2] = ink


def _strip(grid: np.ndarray, wall_cell, edge: str) -> None:
    R, C = wall_cell
    if edge == "top":
        grid[R, C : C + _CELL] = 1
    elif edge == "bottom":
        grid[R + 4, C : C + _CELL] = 1
    elif edge == "left":
        grid[R : R + _CELL, C] = 1
    else:
        grid[R : R + _CELL, C + 4] = 1


def _static_world(parse: KeyMazeParse, rate: int = 1) -> _World:
    return _World(
        passable=parse.passable,
        goals=parse.goals,
        strips=parse.strips,
        rings=parse.rings,
        statics=dict(parse.devices),
        movers=[],
        avoid=frozenset(),
        rate=rate,
    )


def _simulate(world: _World, parse: KeyMazeParse, actions) -> str | tuple:
    state = (parse.key, parse.carried, parse.ink, parse.rings, parse.timer)
    for j, action in enumerate(actions):
        out = _step(world, *state, j, action)
        assert out is not None, f"action {action} at step {j} was blocked"
        if out == "win":
            assert j == len(actions) - 1, "win before the plan's last action"
            return "win"
        state = out
    return state


def _l1_like_board(
    carried: str = "111001101",
    ink: int = 9,
    glyph: str = "111001101",
    glyph_ink: int = 9,
) -> np.ndarray:
    """A minimal level-1-like maze: key at (45,34), a vertical corridor up
    column 34 to the goal box at cell (10,34)."""

    grid = _blank()
    _floor(grid, [(R, 34) for R in range(15, 50, 5)])
    _goal_box(grid, (10, 34), glyph, glyph_ink)
    _key(grid, (45, 34))
    _display(grid, carried, ink)
    return grid


# ------------------------------------------------------- transform algebra


def test_shifter_table_is_a_rotation_commuting_bijection():
    # Bijective on its measured domain.
    assert len(set(_F.values())) == len(_F)
    # Commutes with clockwise rotation everywhere it is defined.
    for a, b in _F.items():
        assert _F[_ROT[a]] == _ROT[b]
    # The measured 6-cycle closes.
    a = _pat_of("010110011")
    x = a
    for _ in range(6):
        x = _F[x]
    assert x == a
    # The measured chains map as recorded in NOTES.md.
    assert _F[_pat_of("101110011")] == _pat_of("111010010")
    assert _F[_pat_of("111100111")] == _pat_of("010101011")


def test_rotation_table_matches_numpy():
    rng = np.random.default_rng(7)
    for _ in range(20):
        p = int(rng.integers(0, 512))
        mat = np.array([[p >> (3 * r + c) & 1 for c in range(3)] for r in range(3)])
        rot = np.rot90(mat, k=-1)  # clockwise
        q = sum(int(rot[r, c]) << (3 * r + c) for r in range(3) for c in range(3))
        assert _ROT[p] == q
    for p in range(512):
        assert _ROT[_ROT[_ROT[_ROT[p]]]] == p


def test_ink_cycle_is_the_measured_four_cycle():
    ink = 12
    seen = []
    for _ in range(4):
        seen.append(ink)
        ink = _INK_NEXT[ink]
    assert seen == [12, 9, 14, 8] and ink == 12


# ----------------------------------------------------------------- parsing


def test_parse_planted_board_reads_every_field():
    grid = _blank()
    corridor = [(R, 34) for R in range(15, 50, 5)] + [(45, C) for C in range(19, 35, 5)]
    corridor += [(R, 19) for R in range(25, 50, 5)]
    _floor(grid, corridor)
    _device(grid, (30, 19), "rot")
    _device(grid, (35, 19), "shift")
    _device(grid, (40, 19), "ink")
    _device(grid, (25, 19), "ring")
    _strip(grid, (45, 14), "right")  # strip faces (45,19), pushes east
    _goal_box(grid, (10, 34), "111001101", 9)
    _key(grid, (45, 34))
    _display(grid, "010110011", 9)
    parse = _parse(grid)
    assert parse is not None
    assert parse.key == (45, 34)
    assert parse.carried == _pat_of("010110011")
    assert parse.ink == 9
    assert parse.goals == {(10, 34): (_pat_of("111001101"), 9)}
    assert parse.devices == {(30, 19): "rot", (35, 19): "shift", (40, 19): "ink"}
    assert parse.rings == frozenset({(25, 19)})
    assert parse.strips == {(45, 19): (0, _CELL)}
    assert parse.timer == 42
    assert parse.lives == 3
    assert (45, 29) in parse.passable
    assert (10, 34) not in parse.passable  # the gated goal cell
    assert (45, 14) not in parse.passable  # the strip wall itself
    # Partial-overlap cell below the box is enterable (measured).
    assert (15, 34) in parse.passable


def test_parse_reads_partial_timer_and_lives():
    grid = _l1_like_board()
    grid[61:63, 13:23] = 3  # ten columns drained (left to right)
    grid[61:63, 62:64] = 5  # third life gone
    parse = _parse(grid)
    assert parse is not None
    assert parse.timer == 32
    assert parse.lives == 2


def test_parse_survives_key_overlapping_the_goal_box():
    # Measured on the composite replay (L1 frames 11-12): the key on a
    # partial-overlap cell covers part of the box border and the frame
    # must still parse during the final approach.
    grid = _l1_like_board()
    grid[45:50, 34:39] = 3  # remove the key from its start cell
    _key(grid, (15, 34))  # directly below the goal cell, over the border
    parse = _parse(grid)
    assert parse is not None
    assert parse.key == (15, 34)
    assert (10, 34) in parse.goals


def test_match_abstains_on_random_grids():
    arch = PatternKeyArchetype()
    rng = np.random.default_rng(0)
    for _ in range(25):
        grid = rng.integers(0, 16, (64, 64), dtype=np.int16)
        assert arch.match(grid) is None
    palette = np.array([3, 4, 5, 9, 11, 12], dtype=np.int16)
    for _ in range(25):
        grid = palette[rng.integers(0, len(palette), (64, 64))]
        assert arch.match(grid) is None


def test_match_abstains_on_structured_lookalikes():
    arch = PatternKeyArchetype()
    # A lockstep-maze-like board (rooms of colour 0 on chrome, colour-6
    # timer strip): a different archetype's grammar entirely.
    rooms = np.full((64, 64), 5, dtype=np.int16)
    for i in range(0, 54, 6):
        for j in range(0, 54, 6):
            rooms[i : i + 3, j : j + 3] = 0
    rooms[63, :] = 6
    assert arch.match(rooms) is None
    # The planted board without its display box.
    grid = _l1_like_board()
    grid[53:63, 1:11] = 5
    assert arch.match(grid) is None
    # Without any goal box.
    grid = _l1_like_board()
    grid[8:17, 32:41] = 4
    assert arch.match(grid) is None
    # With a second key block.
    grid = _l1_like_board()
    _floor(grid, [(45, 29)])
    _key(grid, (45, 24))
    assert arch.match(grid) is None
    # With an unknown sprite in a floor cell.
    grid = _l1_like_board()
    grid[26:29, 35:38] = 2
    assert arch.match(grid) is None


# ----------------------------------------------------------------- planning


def test_planner_straight_line_and_contract_shape():
    grid = _l1_like_board()
    arch = PatternKeyArchetype()
    parse = arch.match(grid)
    assert parse is not None
    world = _static_world(parse)
    route = _plan_route(world, parse.key, parse.carried, parse.ink, parse.timer)
    assert route is not None
    actions = [a for a, _ in route]
    assert actions == [1] * 7  # shortest: straight up the corridor
    assert _simulate(world, parse, actions) == "win"
    steps = arch.next_actions(parse, grid)
    assert len(steps) == 1  # single-step emissions (patrol worlds re-plan)
    assert isinstance(steps[0], Step) and steps[0].action == 1


def test_planner_routes_through_rotator():
    # Carried is one clockwise rotation short of the glyph; the rotator
    # sits one cell west of the corridor, so the shortest plan detours.
    grid = _blank()
    _floor(grid, [(R, 34) for R in range(15, 50, 5)])
    _floor(grid, [(25, 29)])
    _device(grid, (25, 29), "rot")
    _goal_box(grid, (10, 34), "111001101", 9)
    _key(grid, (45, 34))
    _display(grid, "111100101", 9)  # rot_cw(111100101) == 111001101 (measured L1)
    parse = _parse(grid)
    assert parse is not None
    world = _static_world(parse)
    route = _plan_route(world, parse.key, parse.carried, parse.ink, parse.timer)
    assert route is not None
    actions = [a for a, _ in route]
    assert actions == [1, 1, 1, 1, 3, 4, 1, 1, 1]  # detour costs exactly 2
    assert _simulate(world, parse, actions) == "win"


def test_planner_taps_recolourer_three_times():
    # Ink 12 must become 8: three taps of the recolourer at a corridor
    # dead end, which forces the measured oscillation pattern.
    grid = _blank()
    _floor(grid, [(R, 34) for R in range(15, 50, 5)])
    _floor(grid, [(45, 24), (45, 29)])
    _device(grid, (45, 24), "ink")
    _goal_box(grid, (10, 34), "111001101", 8)
    _key(grid, (45, 34))
    _display(grid, "111001101", 12)
    parse = _parse(grid)
    assert parse is not None
    world = _static_world(parse)
    route = _plan_route(world, parse.key, parse.carried, parse.ink, parse.timer)
    assert route is not None
    actions = [a for a, _ in route]
    assert actions == [3, 3, 4, 3, 4, 3, 4, 4, 1, 1, 1, 1, 1, 1, 1]
    assert _simulate(world, parse, actions) == "win"


def test_planner_refills_at_ring_when_timer_is_short():
    grid = _l1_like_board()
    _floor(grid, [(45, 29)])
    _device(grid, (45, 29), "ring")
    grid[61:63, 13:49] = 3  # only 6 timer columns left
    parse = _parse(grid)
    assert parse is not None
    assert parse.timer == 6
    world = _static_world(parse)
    route = _plan_route(world, parse.key, parse.carried, parse.ink, parse.timer)
    assert route is not None
    actions = [a for a, _ in route]
    assert actions[:2] == [3, 4]  # tap the ring first, then run the corridor
    assert _simulate(world, parse, actions) == "win"
    # Without the ring the same board is unwinnable on 6 columns, and the
    # archetype abstains rather than guessing (no unconfirmed movers).
    grid2 = _l1_like_board()
    grid2[61:63, 13:49] = 3
    arch = PatternKeyArchetype()
    parse2 = arch.match(grid2)
    assert parse2 is not None
    assert _plan_route(_static_world(parse2), parse2.key, parse2.carried, parse2.ink, parse2.timer) is None
    assert arch.next_actions(parse2, grid2) == []


def test_planner_uses_conveyor_fling():
    # Entering (25,39) flings the key north to (5,39) in one action
    # (measured semantics); the goal sits one cell east of the landing.
    grid = _blank()
    _floor(grid, [(R, 39) for R in range(5, 30, 5)])
    _floor(grid, [(25, 44)])
    _strip(grid, (30, 39), "top")
    _goal_box(grid, (5, 44), "111001101", 9)
    _key(grid, (25, 44))
    _display(grid, "111001101", 9)
    parse = _parse(grid)
    assert parse is not None
    assert parse.strips == {(25, 39): (-_CELL, 0)}
    world = _static_world(parse)
    route = _plan_route(world, parse.key, parse.carried, parse.ink, parse.timer)
    assert route is not None
    actions = [a for a, _ in route]
    assert actions == [3, 4]  # fling west entry, then east into the goal
    assert _simulate(world, parse, actions) == "win"


def test_gate_blocks_mismatched_entry():
    grid = _l1_like_board(carried="010110011", glyph="111001101")
    parse = _parse(grid)
    assert parse is not None
    world = _static_world(parse)
    # Adjacent to the goal with the wrong pattern: entry refused.
    state = ((15, 34), parse.carried, parse.ink, parse.rings, parse.timer)
    assert _step(world, *state, 0, 1) is None
    # With the matching pattern the same entry wins.
    state = ((15, 34), _pat_of("111001101"), 9, parse.rings, parse.timer)
    assert _step(world, *state, 0, 1) == "win"
    # And with no transform device on the board, the archetype abstains.
    arch = PatternKeyArchetype()
    assert arch.next_actions(parse, grid) == []


# ------------------------------------------------------------ patrol memory


def test_cycle_detection_confirms_the_measured_pingpong():
    a, b, c = (35, 14), (35, 19), (35, 24)
    # The L5 rotator's measured trajectory, one observation per tick.
    hist = [a, b, c, b, a, b]
    assert _detect_cycle(hist) == 4
    assert _detect_cycle(hist[:4]) is None  # unconfirmed while too short
    assert _detect_cycle([a, a, a]) == 1  # static
    world = _World(
        passable=frozenset(), goals={}, strips={}, rings=frozenset(),
        statics={}, movers=[("rot", [b, c, b, a])], avoid=frozenset(),
    )
    # future continues the sequence: b (now), c, b, a, b, c ...
    assert [next(iter(world.mover_at(j))) for j in range(5)] == [b, c, b, a, b]


def test_planner_times_a_patroller_collision():
    # A rotator pingpongs between (45,24) and (45,29) (period 2) on the
    # corridor; the carried pattern needs exactly one rotation, so the
    # plan must co-enter the mover's cell, then run to the goal.
    grid = _blank()
    _floor(grid, [(45, C) for C in range(14, 50, 5)])
    _floor(grid, [(R, 14) for R in range(15, 50, 5)])
    _device(grid, (45, 24), "rot")
    _goal_box(grid, (10, 14), "111001101", 9)
    _key(grid, (45, 44))
    _display(grid, "111100101", 9)
    parse = _parse(grid)
    assert parse is not None
    world = _World(
        passable=parse.passable, goals=parse.goals, strips=parse.strips,
        rings=parse.rings, statics={},
        movers=[("rot", [(45, 24), (45, 29)])], avoid=frozenset(), rate=1,
    )
    route = _plan_route(world, parse.key, parse.carried, parse.ink, parse.timer)
    assert route is not None
    actions = [a for a, _ in route]
    assert _simulate(world, parse, actions) == "win"
    # The winning entry needs the rotated pattern, so some step co-entered
    # the mover's cell; verify via the simulated pattern trace.
    state = (parse.key, parse.carried, parse.ink, parse.rings, parse.timer)
    rotated = False
    for j, action in enumerate(actions[:-1]):
        state = _step(world, *state, j, action)
        if state[1] == _pat_of("111001101"):
            rotated = True
    assert rotated


def test_reset_clears_per_life_state():
    grid = _l1_like_board()
    arch = PatternKeyArchetype()
    parse = arch.match(grid)
    assert parse is not None
    arch.next_actions(parse, grid)
    assert arch._plan and arch._prev is not None
    arch.reset()
    assert arch._plan == [] and arch._prev is None
    assert arch._trackers == [] and arch._rate is None and arch._tick == 0
