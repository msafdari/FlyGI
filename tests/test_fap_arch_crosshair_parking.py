"""Crosshair-parking archetype (re86): parser and planner pinned to planted boards.

The COMPARISON evidence for this component is the executor-driven offline
run recorded in WORKLOG/structured output: FapExecutor seated with this
archetype alone completes re86's levels 1-6 (score 0 -> 6, the dossier's own
hand-program ceiling) in 271 actions against the dossier's 335, and the
25-game recognizer-frame audit measured zero false matches and zero emitted
actions on the other 24 games' 960 frames. These tests pin the measured
parsing grammar (avatar shapes, dots, tiles, timer), the planner's coverage
geometry, the split-plus physics and the rect squeeze planning to planted
frames so refactors cannot silently bend them.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from flygi.controller.fap_library import FapExecutor, Step
from flygi.controller.fap_archetypes.crosshair_parking import (
    Avatar,
    CrosshairParkingArchetype,
    Dot,
    _cover_centres,
    _rect_route,
    _split_plus_route,
)

_BG = 5
_DIR = {1: (-1, 0), 2: (1, 0), 3: (0, -1), 4: (0, 1)}


# ------------------------------------------------------------------- builders


def _blank() -> np.ndarray:
    grid = np.full((64, 64), _BG, dtype=np.int16)
    grid[63, :] = 15  # fresh timer strip
    return grid


def _paint_tile(grid: np.ndarray, top: int, left: int, colour: int) -> None:
    grid[top : top + 6, left : left + 6] = 2
    grid[top + 1 : top + 5, left + 1 : left + 5] = colour


def _paint_dot(grid: np.ndarray, row: int, col: int, colour: int) -> None:
    grid[row - 1 : row + 2, col - 1 : col + 2] = 4
    grid[row, col] = colour


def _paint_avatar(grid: np.ndarray, avatar: Avatar) -> None:
    for r, c in avatar.cells():
        grid[r, c] = avatar.colour


class _Sim:
    """Mini engine for planted boards, implementing the MEASURED rules:
    3-px moves, action-5 cycling, landing-based tile recolour (last touch
    wins), avatars rendered over dots and tiles, marker at the active
    avatar's centre, win = every dot box overlapped by a matching-colour
    covering cell simultaneously."""

    def __init__(self, avatars: list[Avatar], dots: list[Dot], tiles):
        self.avatars = avatars
        self.dots = dots
        self.tiles = tiles  # list of (top, left, colour)
        self.active = 0
        self.steps: list[int] = []

    def render(self) -> np.ndarray:
        grid = _blank()
        for top, left, colour in self.tiles:
            _paint_tile(grid, top, left, colour)
        for d in self.dots:
            _paint_dot(grid, d.row, d.col, d.colour)
        for avatar in self.avatars:
            _paint_avatar(grid, avatar)
        marker = self.avatars[self.active].centre
        grid[marker] = 0
        return grid

    def apply(self, step: Step) -> None:
        self.steps.append(step.action)
        if step.action == 5:
            self.active = (self.active + 1) % len(self.avatars)
            return
        avatar = self.avatars[self.active]
        dr, dc = _DIR[step.action]
        avatar.params["r"] += dr * 3
        avatar.params["c"] += dc * 3
        cells = avatar.cells()
        for top, left, colour in self.tiles:  # landing contact recolours
            if any(top <= r < top + 6 and left <= c < left + 6 for r, c in cells):
                avatar.colour = colour

    def won(self) -> bool:
        for d in self.dots:
            box = {
                (d.row + dr, d.col + dc)
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
            }
            covered = False
            for avatar in self.avatars:
                if avatar.colour != d.colour:
                    continue
                cr, cc = avatar.centre
                cover = {
                    (cr + orr, cc + occ) for orr, occ in avatar.coverage_offsets()
                }
                if cover & box:
                    covered = True
                    break
            if not covered:
                return False
        return True


def _drive(sim: _Sim, max_parses: int = 40, max_steps: int = 400) -> int:
    arch = CrosshairParkingArchetype()
    used = 0
    for _ in range(max_parses):
        grid = sim.render()
        parse = arch.match(grid)
        assert parse is not None, "archetype abstained on its own planted board"
        steps = arch.next_actions(parse, grid)
        assert steps, "planner returned no steps before the win"
        for step in steps:
            sim.apply(step)
            used += 1
            assert used <= max_steps, "planner exceeded the step budget"
            if sim.won():
                return used
    raise AssertionError("planted board was never completed")


def _l1_like() -> _Sim:
    avatars = [
        Avatar("plus", 9, {"r": 45, "c": 36, "au": 12, "ad": 12, "al": 12, "ar": 12}),
        Avatar("plus", 11, {"r": 27, "c": 21, "au": 8, "ad": 8, "al": 8, "ar": 8}),
    ]
    dots = [
        Dot(15, 36, 9), Dot(24, 24, 9), Dot(24, 45, 9),
        Dot(9, 21, 11), Dot(18, 12, 11), Dot(18, 30, 11),
    ]
    return _Sim(avatars, dots, tiles=[])


# ------------------------------------------------------------ parse positives


def test_parse_planted_board() -> None:
    sim = _l1_like()
    parse = CrosshairParkingArchetype().match(sim.render())
    assert parse is not None
    kinds = sorted((a.kind, a.colour, a.centre) for a in parse.avatars)
    assert kinds == [("plus", 9, (45, 36)), ("plus", 11, (27, 21))]
    nine = next(a for a in parse.avatars if a.colour == 9)
    assert (nine.params["au"], nine.params["al"]) == (12, 12)
    assert {(d.row, d.col, d.colour) for d in parse.dots} == {
        (15, 36, 9), (24, 24, 9), (24, 45, 9),
        (9, 21, 11), (18, 12, 11), (18, 30, 11),
    }
    assert parse.marker == (45, 36)
    assert parse.timer_pixels == 64
    assert not parse.tiles and not parse.object_cells


def test_parse_reads_tiles_and_shapes() -> None:
    grid = _blank()
    _paint_tile(grid, 4, 28, 12)
    _paint_tile(grid, 54, 52, 14)
    x = Avatar("x", 10, {"r": 21, "c": 24, "arm": 8})
    diamond = Avatar("diamond", 14, {"r": 40, "c": 20, "radius": 7})
    _paint_avatar(grid, x)
    _paint_avatar(grid, diamond)
    grid[21, 24] = 0  # X active
    _paint_dot(grid, 18, 45, 12)
    _paint_dot(grid, 30, 45, 14)
    parse = CrosshairParkingArchetype().match(grid)
    assert parse is not None
    assert sorted((t.top, t.left, t.colour) for t in parse.tiles) == [
        (4, 28, 12), (54, 52, 14),
    ]
    kinds = sorted((a.kind, a.colour, a.centre) for a in parse.avatars)
    assert kinds == [("diamond", 14, (40, 20)), ("x", 10, (21, 24))]


# ------------------------------------------------------------------ negatives


def test_abstains_on_random_grids() -> None:
    rng = np.random.default_rng(0)
    arch = CrosshairParkingArchetype()
    for _ in range(25):
        grid = rng.integers(0, 16, size=(64, 64), dtype=np.int16)
        assert arch.match(grid) is None


def test_abstains_on_structured_non_matching_boards() -> None:
    arch = CrosshairParkingArchetype()
    # (a) the full planted board with a broken timer row
    sim = _l1_like()
    grid = sim.render()
    grid[63, :] = 3
    assert arch.match(grid) is None
    # (b) dots and tiles but solid-square "avatars" outside the grammar
    grid = _blank()
    _paint_tile(grid, 4, 28, 12)
    _paint_dot(grid, 18, 45, 9)
    _paint_dot(grid, 30, 45, 9)
    grid[30:37, 10:17] = 9
    grid[40:47, 30:37] = 11
    grid[33, 13] = 0
    assert CrosshairParkingArchetype().match(grid) is None
    # (c) a lockstep-maze-style frame (tu93 grammar: colour-6 timer, rooms)
    maze = np.full((64, 64), 5, dtype=np.int16)
    maze[63, :] = 6
    maze[9:12, 9:12] = 9
    maze[9:12, 15:18] = 14
    maze[9:12, 12:15] = 2
    assert CrosshairParkingArchetype().match(maze) is None


_FRAMES = Path(__file__).resolve().parents[1] / "results/diagnostics/recognizer_frames.npz"


@pytest.mark.skipif(not _FRAMES.exists(), reason="recognizer frame bank absent")
def test_no_action_on_other_games_frame_bank() -> None:
    bank = np.load(_FRAMES)
    for key in bank.files:
        if key == "re86":
            continue
        for frame in bank[key]:
            arch = CrosshairParkingArchetype()
            grid = np.asarray(frame, dtype=np.int16)
            parse = arch.match(grid)
            assert parse is None or not arch.next_actions(parse, grid), key


# ---------------------------------------------------------------- planner units


def test_x_centre_does_not_count_for_coverage() -> None:
    # MEASURED (live L2): the inactive X's centre renders background, and the
    # dossier's verified L3 geometry excluded it (solve3.py, 1 <= |dr|).
    x = Avatar("x", 9, {"r": 30, "c": 30, "arm": 5})
    plus = Avatar("plus", 9, {"r": 30, "c": 30, "au": 5, "ad": 5, "al": 5, "ar": 5})
    assert (0, 0) not in x.coverage_offsets()
    assert (0, 0) in x.cell_offsets()  # still rendered and parsed
    assert (0, 0) in plus.coverage_offsets()


def test_cover_centres_respects_lattice_and_boxes() -> None:
    plus = Avatar("plus", 9, {"r": 45, "c": 36, "au": 10, "ad": 10, "al": 10, "ar": 10})
    centres = _cover_centres(plus, Dot(15, 36, 9))
    assert centres, "no covering placements found"
    for r, c in centres:
        assert (r - 45) % 3 == 0 and (c - 36) % 3 == 0
    # vbar reaches the box from (24, 36): rows 14..34 meet box rows 14-16
    assert (24, 36) in centres


def test_drive_planted_l1_like_board_to_win() -> None:
    used = _drive(_l1_like())
    assert used <= 60


def test_drive_planted_tile_board_recolours_last_touch() -> None:
    avatars = [
        Avatar("plus", 6, {"r": 36, "c": 54, "au": 10, "ad": 10, "al": 10, "ar": 10}),
        Avatar("x", 10, {"r": 21, "c": 24, "arm": 8}),
    ]
    dots = [Dot(18, 24, 12), Dot(27, 15, 12), Dot(27, 45, 14)]
    tiles = [(4, 28, 12), (54, 52, 14)]
    sim = _Sim(avatars, dots, tiles)
    used = _drive(sim, max_steps=500)
    assert used <= 200
    colours = sorted(a.colour for a in sim.avatars)
    assert colours == [12, 14], "both avatars must end recoloured to dot colours"


def test_split_plus_route_matches_independent_physics() -> None:
    # L6-like: the rigid plus cannot cover its dots; the route must press a
    # bar against the object to displace the bars relative to each other.
    obj = frozenset(
        (r, c) for r in range(28, 36) for c in range(28, 36)
        if r in (28, 35) or c in (28, 35)
    )
    plus = Avatar(
        "split_plus", 9,
        {"vtop": 3, "vcol": 48, "vlen": 25, "hrow": 15, "hleft": 36, "hlen": 25},
    )
    target = (3, 12, 9, 6)
    route = _split_plus_route(plus, target, obj, {})
    assert route, "no route found to the split target"

    # Independent re-implementation of the measured per-part physics.
    def band_hit(r0, r1, c0, c1):
        return any(
            (r, c) in obj
            for r in range(max(r0, 0), min(r1, 62) + 1)
            for c in range(max(c0, 0), min(c1, 63) + 1)
        )

    vt, vc, hr, hl = 3, 48, 15, 36
    for action in route:
        dr, dc = _DIR[action]
        if dr < 0:
            v_hit = band_hit(vt - 3, vt - 1, vc, vc)
            h_hit = band_hit(hr - 3, hr - 1, hl, hl + 24)
        elif dr > 0:
            v_hit = band_hit(vt + 25, vt + 27, vc, vc)
            h_hit = band_hit(hr + 1, hr + 3, hl, hl + 24)
        elif dc < 0:
            v_hit = band_hit(vt, vt + 24, vc - 3, vc - 1)
            h_hit = band_hit(hr, hr, hl - 3, hl - 1)
        else:
            v_hit = band_hit(vt, vt + 24, vc + 1, vc + 3)
            h_hit = band_hit(hr, hr, hl + 25, hl + 27)
        if not v_hit:
            vt, vc = vt + dr * 3, vc + dc * 3
        if not h_hit:
            hr, hl = hr + dr * 3, hl + dc * 3
    assert (vt, vc, hr, hl) == target


def test_rect_options_offer_deformed_geometry() -> None:
    arch = CrosshairParkingArchetype()
    rect = Avatar("rect", 11, {"top": 39, "left": 6, "h": 19, "w": 19})
    group = [Dot(30, 45, 11), Dot(30, 54, 11), Dot(57, 45, 11), Dot(57, 54, 11)]
    options = arch._rect_options(rect, 11, group, deformable=True)
    full = [o for o in options if len(o.covered) == 4]
    assert any(o.spec == ("rect", (30, 45, 28, 10)) for o in full)
    # without the object no deformed shape may be offered
    rigid = arch._rect_options(rect, 11, group, deformable=False)
    assert all(o.spec[1][2:] == (19, 19) for o in rigid)


def test_rect_route_navigates_then_presses_once() -> None:
    obj = frozenset((r, c) for r in range(28, 36) for c in range(28, 36))
    rect = Avatar("rect", 11, {"top": 39, "left": 6, "h": 19, "w": 19})
    plan = _rect_route(rect, (30, 45, 28, 10), obj)
    assert plan, "no squeeze plan found"

    def outline(t, l):
        cells = set()
        for k in range(l, l + 19):
            cells.add((t, k))
            cells.add((t + 18, k))
        for k in range(t, t + 19):
            cells.add((k, l))
            cells.add((k, l + 18))
        return cells

    t, l = 39, 6
    for action in plan[:-1]:  # navigation legs must never touch the object
        dr, dc = _DIR[action]
        swept = {
            (r + dr * k, c + dc * k)
            for r, c in outline(t, l)
            for k in (1, 2, 3)
        }
        assert not (swept & obj), "navigation move would deform the rect"
        t, l = t + dr * 3, l + dc * 3
    dr, dc = _DIR[plan[-1]]
    swept = {
        (r + dr * k, c + dc * k) for r, c in outline(t, l) for k in (1, 2, 3)
    }
    assert swept & obj, "the final action must press against the object"


def test_l7_style_tiles_plus_object_abstains() -> None:
    # The dossier records L7 (tiles AND squeeze object) UNSOLVED; the
    # planner must abstain rather than thrash the timer.
    grid = _blank()
    _paint_tile(grid, 2, 14, 9)
    _paint_tile(grid, 2, 24, 11)
    for r in range(28, 36):
        for c in range(28, 36):
            if r in (28, 35) or c in (28, 35):
                grid[r, c] = 1
    plus = Avatar("plus", 9, {"r": 48, "c": 12, "au": 9, "ad": 9, "al": 9, "ar": 9})
    rect = Avatar("rect", 12, {"top": 45, "left": 40, "h": 13, "w": 13})
    _paint_avatar(grid, plus)
    _paint_avatar(grid, rect)
    grid[48, 12] = 0
    _paint_dot(grid, 9, 9, 9)
    _paint_dot(grid, 15, 3, 9)
    arch = CrosshairParkingArchetype()
    parse = arch.match(grid)
    if parse is not None:  # a parse is fine; acting is not
        assert arch.next_actions(parse, grid) == []


def test_seats_in_fap_executor() -> None:
    sim = _l1_like()
    executor = FapExecutor(archetypes=[CrosshairParkingArchetype()])
    grid = sim.render()
    executor.observe(grid)
    step = executor.propose(grid)
    assert isinstance(step, Step) and step.action in (1, 2, 3, 4, 5)
    assert executor.describe()["matched"] == "crosshair_parking"
