"""Slot-dock archetype (ka59): parser, physics and planner on planted boards.

The COMPARISON evidence for this component is the executor-driven offline
run recorded in the structured output: FapExecutor seated with this
archetype alone completes ka59 7/7 levels to GameState.WIN in 276 actions
(dossier hand-program target: 7/7 in 321), with zero abstain-fallbacks and
zero forced resets, and the 25-game recognizer-frame audit measured zero
false matches on the other 24 games (960 frames) while all 40 ka59 frames
parsed.  The parser+simulator pair was additionally validated exact on all
321 transitions of the dossier's verified full-win replay (positions,
selection, geyser charge and all seven level-completion instants).  These
tests pin the measured grammar and physics to planted frames so refactors
cannot silently bend them.
"""

from __future__ import annotations

import numpy as np

from flygi.controller.fap_archetypes.slot_dock import (
    _T,
    SlotDockArchetype,
    _parse,
    _ring_of,
    _World,
)
from flygi.controller.fap_library import Step

_OR, _OC = 1, 1  # planted lattice origin (real levels used (0,0) and (2,2))


def _blank() -> np.ndarray:
    grid = np.full((64, 64), 1, dtype=np.int16)
    grid[63, :] = 4  # full timer strip
    return grid


def _drive(grid: np.ndarray, tr: int, tc: int, th: int = 1, tw: int = 1, centre: int = 0) -> None:
    """A drivable rectangle at tile (tr, tc): solid 14 with a centre patch."""

    r, c = _OR + _T * tr, _OC + _T * tc
    h, w = _T * th, _T * tw
    grid[r : r + h, c : c + w] = 14
    grid[r + (h - 1) // 2 : r + h // 2 + 1, c + (w - 1) // 2 : c + w // 2 + 1] = centre


def _boulder(grid: np.ndarray, tr: int, tc: int, tiles=((0, 0),)) -> None:
    for a, b in tiles:
        r, c = _OR + _T * (tr + a), _OC + _T * (tc + b)
        grid[r : r + _T, c : c + _T] = 11


def _slot(grid: np.ndarray, tr: int, tc: int, tiles=((0, 0),)) -> None:
    """A colour-4 outline around the tile-shape interior anchored at (tr, tc)."""

    px = {
        (_T * (tr + a) + i, _T * (tc + b) + j)
        for a, b in tiles
        for i in range(_T)
        for j in range(_T)
    }
    for r, c in _ring_of(px):
        grid[_OR + r, _OC + c] = 4


def _geyser(grid: np.ndarray, tr: int, tc: int, size: int = 2, fill: int = 0, from_face: str = "top") -> None:
    """A size x size tile geyser block charged ``fill`` pixel-lines from
    ``from_face`` (the beam later fires toward the opposite face)."""

    r, c = _OR + _T * tr, _OC + _T * tc
    n = _T * size
    grid[r : r + n, c : c + n] = 13
    if from_face == "top":
        grid[r : r + fill, c : c + n] = 12
    elif from_face == "bottom":
        grid[r + n - fill : r + n, c : c + n] = 12
    elif from_face == "left":
        grid[r : r + n, c : c + fill] = 12
    else:
        grid[r : r + n, c : c + n - fill * 0][:, -fill or n :] = 12  # right


def _membrane(grid: np.ndarray, tr0: int, tc0: int, th: int, tw: int) -> None:
    r, c = _OR + _T * tr0, _OC + _T * tc0
    grid[r : r + _T * th, c : c + _T * tw] = 15


def _wall(grid: np.ndarray, tr0: int, tc0: int, th: int, tw: int) -> None:
    r, c = _OR + _T * tr0, _OC + _T * tc0
    grid[r : r + _T * th, c : c + _T * tw] = 2


def _push_board() -> np.ndarray:
    """Player, one box, two 1x1 slots, a vertical membrane in the box's
    flight path -- a miniature of ka59 level 1."""

    grid = _blank()
    _drive(grid, 10, 4, centre=0)
    _drive(grid, 10, 7, centre=5)
    _membrane(grid, 6, 10, 10, 2)
    _slot(grid, 10, 14)
    _slot(grid, 5, 4)
    return grid


class TestMatch:
    def test_planted_board_parses(self) -> None:
        parse = SlotDockArchetype().match(_push_board())
        assert parse is not None
        kinds = sorted(o.kind for o in parse.objects)
        assert kinds == ["drive", "drive"]
        sels = sorted(o.sel for o in parse.objects)
        assert sels == [0, 5]
        assert len(parse.slots) == 2
        assert parse.lattice == (_OR, _OC)

    def test_domino_parses_as_one_object(self) -> None:
        # One ring per OBJECT (measured L2): a 3x6 sprite with a central
        # 2-pixel patch is a single 1x2 domino, not two 1x1s.
        grid = _blank()
        _drive(grid, 10, 4, th=1, tw=2, centre=5)
        _drive(grid, 15, 4, centre=0)
        _slot(grid, 10, 14, tiles=((0, 0), (0, 1)))
        _slot(grid, 5, 4)
        parse = SlotDockArchetype().match(grid)
        assert parse is not None
        shapes = sorted(o.shape for o in parse.objects)
        assert shapes == [((0, 0),), ((0, 0), (0, 1))]

    def test_adjacent_objects_split(self) -> None:
        # Two touching 1x1 sprites carry two centre patches: they must
        # parse as two objects even though their pixels form one component.
        grid = _blank()
        _drive(grid, 10, 4, centre=0)
        _drive(grid, 10, 5, centre=5)
        _slot(grid, 10, 14)
        parse = SlotDockArchetype().match(grid)
        assert parse is not None
        assert sorted(o.sel for o in parse.objects) == [0, 5]

    def test_contact_edge_zeros_parse(self) -> None:
        # The selected sprite recolours a touching tile-edge line to 0
        # (measured L3 frame 79): the parser must still see a 1x1 at the
        # same anchor.
        grid = _blank()
        _drive(grid, 10, 4, centre=0)
        _drive(grid, 10, 5, centre=5)
        _slot(grid, 10, 14)
        r, c = _OR + _T * 10, _OC + _T * 5 - 1  # player's right edge column
        grid[r : r + 3, c] = 0
        parse = SlotDockArchetype().match(grid)
        assert parse is not None
        anchors = sorted(o.anchor for o in parse.objects)
        assert anchors == [(_OR + 30, _OC + 12), (_OR + 30, _OC + 15)]

    def test_geyser_charge_readout(self) -> None:
        grid = _push_board()
        _geyser(grid, 2, 14, size=2, fill=4, from_face="top")
        parse = SlotDockArchetype().match(grid)
        assert parse is not None
        gey = [o for o in parse.objects if o.kind == "geyser"]
        assert len(gey) == 1
        assert gey[0].fill == 4
        assert gey[0].fill_dir == (1, 0)  # charged from the top: fires down
        assert gey[0].period == 6

    def test_random_grids_abstain(self) -> None:
        arch = SlotDockArchetype()
        rng = np.random.default_rng(20260928)
        for _ in range(20):
            grid = rng.integers(0, 16, size=(64, 64)).astype(np.int16)
            assert arch.match(grid) is None

    def test_structured_maze_board_abstains(self) -> None:
        # A tu93-flavour lockstep maze: 3x3 rooms on a 6-pixel pitch.
        grid = np.full((64, 64), 5, dtype=np.int16)
        grid[63, :] = 6
        for i in range(4):
            for j in range(4):
                grid[9 + 6 * i : 12 + 6 * i, 9 + 6 * j : 12 + 6 * j] = 0
        grid[9:12, 9:12] = 9
        grid[15:18, 15:18] = 14
        assert SlotDockArchetype().match(grid) is None

    def test_structured_glyph_board_abstains(self) -> None:
        # An ft09-flavour glyph lattice on an 8-pixel pitch.
        grid = np.full((64, 64), 5, dtype=np.int16)
        for i, r in enumerate((2, 10, 18)):
            for j, c in enumerate((4, 12, 20)):
                grid[r : r + 6, c : c + 6] = 9 if (i + j) % 2 else 8
        assert SlotDockArchetype().match(grid) is None

    def test_missing_timer_row_abstains(self) -> None:
        grid = _push_board()
        grid[63, :] = 1
        assert SlotDockArchetype().match(grid) is None

    def test_foreign_colour_abstains(self) -> None:
        grid = _push_board()
        grid[50:53, 50:53] = 7
        assert SlotDockArchetype().match(grid) is None

    def test_off_lattice_object_abstains(self) -> None:
        grid = _push_board()
        # shift the box sprite one pixel right: off the 3px lattice
        r, c = _OR + _T * 10, _OC + _T * 7
        grid[r : r + 3, c : c + 3] = 1
        grid[r : r + 3, c + 1 : c + 4] = 14
        grid[r + 1, c + 2] = 5
        assert SlotDockArchetype().match(grid) is None

    def test_unmatched_slot_shape_abstains(self) -> None:
        # A 1x2 slot with only 1x1 objects on the board: shape bijection
        # fails, so this frame is not our archetype.
        grid = _blank()
        _drive(grid, 10, 4, centre=0)
        _slot(grid, 10, 14, tiles=((0, 0), (0, 1)))
        assert SlotDockArchetype().match(grid) is None

    def test_stray_slot_pixel_abstains(self) -> None:
        grid = _push_board()
        grid[50, 50] = 4  # a 4 no slot ring explains
        assert SlotDockArchetype().match(grid) is None


def _world(grid: np.ndarray) -> _World:
    parse = _parse(np.asarray(grid, dtype=np.int16))
    assert parse is not None
    return _World(parse)


def _sel_anchor(w: _World, state) -> tuple[int, int]:
    anchors, sel, _ = state
    return anchors[sel]


class TestPhysics:
    def test_walk_and_block(self) -> None:
        w = _world(_push_board())
        s = w.step(w.state0, 1)  # up: free floor
        assert _sel_anchor(w, s) == (9, 4)
        s2 = w.step(s, 3)
        assert _sel_anchor(w, s2) == (9, 3)

    def test_push_launch_five_tiles_over_membrane(self) -> None:
        # Box at tile col 7; player drives right into it: 5-tile flight
        # lands at col 12, past the membrane at cols 10-11 (measured L1).
        w = _world(_push_board())
        s = w.state0
        for _ in range(3):  # two walks close the gap, the third pushes
            s = w.step(s, 4)
        anchors, sel, _ = s
        box = next(i for i in range(w.n) if i != sel)
        assert anchors[box] == (10, 12)
        assert anchors[sel] == (10, 6)  # the pusher never advances

    def test_launch_extends_past_membrane(self) -> None:
        # A membrane covering the 5-tile landing: the flight extends until
        # the object is fully clear (measured L5 stack, L4).
        grid = _blank()
        _drive(grid, 10, 4, centre=0)
        _drive(grid, 10, 6, centre=5)
        _membrane(grid, 6, 10, 10, 2)
        _slot(grid, 10, 16)
        _slot(grid, 5, 4)
        w = _world(grid)
        s = w.step(w.state0, 4)  # close the gap
        s = w.step(s, 4)  # contact push
        anchors, sel, _ = s
        box = next(i for i in range(w.n) if i != sel)
        assert anchors[box] == (10, 12)  # 5 tiles = col 11 overlaps; +1 clears

    def test_launch_truncates_before_wall(self) -> None:
        grid = _blank()
        _drive(grid, 10, 4, centre=0)
        _drive(grid, 10, 6, centre=5)
        _wall(grid, 8, 10, 6, 1)
        _slot(grid, 15, 16)
        _slot(grid, 5, 4)
        w = _world(grid)
        s = w.step(w.state0, 4)  # close the gap
        s = w.step(s, 4)  # contact push
        anchors, sel, _ = s
        box = next(i for i in range(w.n) if i != sel)
        assert anchors[box] == (10, 9)  # stops adjacent to the wall column

    def test_flight_plows_parked_object(self) -> None:
        # Bulldozer semantics (measured L7 frame 258): an object inside the
        # flight path is carried ahead and deposited adjacent beyond the
        # landing even though it never overlapped the landing tile.
        grid = _blank()
        _drive(grid, 10, 4, centre=0)
        _drive(grid, 10, 6, centre=5)
        _drive(grid, 10, 8, centre=4)
        _slot(grid, 10, 16)
        _slot(grid, 5, 4)
        _slot(grid, 5, 8)
        w = _world(grid)
        s = w.step(w.state0, 4)  # close the gap
        s = w.step(s, 4)  # contact push
        anchors, sel, _ = s
        by_col = sorted(anchors[i][1] for i in range(w.n) if i != sel)
        assert by_col == [11, 12]  # box lands at 11, parked object beyond

    def test_beam_fires_on_charge_wrap(self) -> None:
        # Geyser charged 5/6 from the top; one move ticks the clock, the
        # charge wraps and the beam fires DOWN: 3-tile flight (measured
        # L5/L6 beam distances).
        grid = _blank()
        _drive(grid, 18, 4, centre=0)
        _drive(grid, 10, 15, centre=5)
        _geyser(grid, 4, 14, size=2, fill=5, from_face="top")
        _slot(grid, 18, 16)
        _slot(grid, 5, 4)
        w = _world(grid)
        s = w.step(w.state0, 3)  # unrelated move; the clock ticks
        anchors, _, t = s
        box = next(i for i in range(w.n) if w.kinds[i] == "drive" and anchors[i][0] != 18)
        assert anchors[box] == (13, 15)
        assert t == 1

    def test_beam_blocked_by_membrane(self) -> None:
        grid = _blank()
        _drive(grid, 18, 4, centre=0)
        _drive(grid, 12, 15, centre=5)
        _geyser(grid, 4, 14, size=2, fill=5, from_face="top")
        _membrane(grid, 10, 14, 1, 2)
        _slot(grid, 18, 16)
        _slot(grid, 5, 4)
        w = _world(grid)
        s = w.step(w.state0, 3)
        anchors, _, _ = s
        box = next(i for i in range(w.n) if w.kinds[i] == "drive" and anchors[i][0] != 18)
        assert anchors[box] == (12, 15)  # the beam does not act across f

    def test_clicks_do_not_tick_the_clock(self) -> None:
        grid = _push_board()
        _geyser(grid, 2, 14, size=2, fill=4, from_face="top")
        w = _world(grid)
        _, sel, t0 = w.state0
        other = next(i for i in range(w.n) if w.kinds[i] == "drive" and i != sel)
        s = w.step(w.state0, 10 + other)
        assert s[1] == other and s[2] == t0  # selection changed, no tick

    def test_blocked_move_ticks_the_clock(self) -> None:
        # Measured 2026-09-28 (L5 probe): a drive into a wall/membrane is
        # swallowed positionally but still advances the geyser clock.
        grid = _blank()
        _drive(grid, 10, 9, centre=0)  # against the membrane's left edge
        _membrane(grid, 6, 10, 10, 2)
        _geyser(grid, 2, 2, size=2, fill=2, from_face="top")
        _slot(grid, 15, 16)
        w = _world(grid)
        s = w.step(w.state0, 4)  # blocked by the membrane
        anchors, sel, t = s
        assert anchors[sel] == (10, 9)
        assert t == 1


class TestPlanner:
    def test_push_board_plan_docks(self) -> None:
        w = _world(_push_board())
        path = w.plan()
        assert path
        state = w.state0
        for action, _ in path:
            state = w.step(state, action)
            assert state is not None
        assert w.docked(state)
        # the plan must contain a selection click (the box docks driven)
        assert any(a >= 10 for a, _ in path)

    def test_next_actions_emits_single_step(self) -> None:
        arch = SlotDockArchetype()
        grid = _push_board()
        parse = arch.match(grid)
        steps = arch.next_actions(parse, grid)
        assert len(steps) == 1
        assert isinstance(steps[0], Step)
        assert steps[0].action in (1, 2, 3, 4, 6)

    def test_click_step_targets_centre_patch(self) -> None:
        # Force a plan whose first useful selection switch is a click and
        # check the click pixel is the target object's centre patch.
        arch = SlotDockArchetype()
        grid = _push_board()
        parse = arch.match(grid)
        world = _World(parse)
        path = world.plan()
        clicks = [a for a, _ in path if a >= 10]
        assert clicks
        # replay through _emit by walking next_actions' own plan
        state = world.state0
        for action, nstate in path:
            if action >= 10:
                step = arch._emit(world, state, action)
                assert step.action == 6
                # the click pixel is the target's centre patch at its
                # position AT CLICK TIME (the object may have been pushed)
                tr, tc = state[0][action - 10]
                assert int(step.y) == world.orow + _T * tr + 1
                assert int(step.x) == world.ocol + _T * tc + 1
                break
            state = nstate

    def test_probe_when_geyser_axis_unknown(self) -> None:
        # A fully discharged block hides its beam axis: the first call must
        # emit one safe drive (the probe), not a full plan.
        arch = SlotDockArchetype()
        grid = _push_board()
        _geyser(grid, 2, 14, size=2, fill=0)
        parse = arch.match(grid)
        gey = [o for o in parse.objects if o.kind == "geyser"]
        assert gey[0].fill_dir is None
        steps = arch.next_actions(parse, grid)
        assert len(steps) == 1
        assert steps[0].action in (1, 2, 3, 4)
        assert not arch._plan  # no cached plan yet: it will replan next call

    def test_docked_goal_detection(self) -> None:
        grid = _blank()
        _drive(grid, 10, 14, centre=0)  # exactly inside the slot below
        _slot(grid, 10, 14)
        parse = _parse(np.asarray(grid, dtype=np.int16))
        assert parse is not None
        w = _World(parse)
        assert w.docked(w.state0)
