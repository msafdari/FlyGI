"""Porter-ferry archetype (wa30): parser and planner pinned to planted boards.

The COMPARISON evidence for this component is the executor-driven offline
run recorded in WORKLOG/structured output: FapExecutor seated with this
archetype alone completes wa30 levels 1-3 (the dossier's verified-program
target) in 160 actions against the hand programs' 169, and the 25-game
recognizer-frame audit measured zero false matches on the other 24 games
(960 frames). These tests pin the measured parsing grammar and the
planner's mark/pick/carry/drop/plant rules to planted frames so refactors
cannot silently bend them.

The planted boards use coordinates unlike any real wa30 level where the
scenario allows, so nothing here doubles as board-instance data.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from flygi.controller.fap_library import Step
from flygi.controller.fap_archetypes.porter_ferry import PorterFerryArchetype

_SPECKLE = np.array(
    [[2, 1, 2, 2], [1, 2, 2, 2], [2, 2, 2, 1], [2, 2, 1, 2]], dtype=np.int16
)

_FACING_STRIP = {
    (-1, 0): (slice(0, 1), slice(0, 4)),
    (1, 0): (slice(3, 4), slice(0, 4)),
    (0, -1): (slice(0, 4), slice(0, 1)),
    (0, 1): (slice(0, 4), slice(3, 4)),
}


def _blank() -> np.ndarray:
    grid = np.full((64, 64), 1, dtype=np.int16)
    grid[63, :] = 7  # full timer bar
    return grid


def _block(grid: np.ndarray, r: int, c: int) -> np.ndarray:
    return grid[r * 4 : r * 4 + 4, c * 4 : c * 4 + 4]


def _put_player(grid: np.ndarray, r: int, c: int, facing=(-1, 0)) -> None:
    blk = _block(grid, r, c)
    blk[:] = 14
    blk[_FACING_STRIP[facing]] = 0


def _put_box(grid: np.ndarray, r: int, c: int, border: int = 4) -> None:
    blk = _block(grid, r, c)
    blk[:] = border
    blk[1:3, 1:3] = 9


def _put_rival(grid: np.ndarray, r: int, c: int) -> None:
    _block(grid, r, c)[:] = 12


def _put_speckle(grid: np.ndarray, r: int, c: int) -> None:
    _block(grid, r, c)[:] = _SPECKLE


def _put_dock(grid: np.ndarray, r: int, c: int, hblocks: int, wblocks: int) -> None:
    y0, x0 = r * 4, c * 4
    y1, x1 = y0 + 4 * hblocks, x0 + 4 * wblocks
    grid[y0:y1, x0:x1] = 2
    grid[y0, x0:x1] = 9
    grid[y1 - 1, x0:x1] = 9
    grid[y0:y1, x0] = 9
    grid[y0:y1, x1 - 1] = 9


def _l1_like() -> np.ndarray:
    """Three boxes, a 1x3 dock, no rival (the L1 shape, shifted)."""

    grid = _blank()
    _put_player(grid, 11, 5)
    _put_box(grid, 8, 5)
    _put_box(grid, 6, 2)
    _put_box(grid, 5, 9)
    _put_dock(grid, 6, 5, 1, 3)  # slots (6,5) (6,6) (6,7)
    return grid


# ------------------------------------------------------------------ match


def test_match_parses_planted_l1_like_board():
    arch = PorterFerryArchetype()
    parse = arch.match(_l1_like())
    assert parse is not None
    assert parse.player == (11, 5)
    assert parse.facing == (-1, 0)
    assert parse.boxes == {(8, 5): "free", (6, 2): "free", (5, 9): "free"}
    assert parse.dock == frozenset({(6, 5), (6, 6), (6, 7)})
    assert parse.rivals == frozenset()
    assert (10, 5) in parse.floor and (0, 0) in parse.floor


def test_match_reads_box_states_and_walls():
    grid = _blank()
    _put_player(grid, 9, 3, facing=(0, 1))
    _put_box(grid, 9, 4, border=0)  # held, glued east
    _put_box(grid, 2, 2, border=3)  # marked
    _put_box(grid, 2, 12, border=5)  # rival-dragged
    _put_rival(grid, 2, 13)
    _put_dock(grid, 12, 12, 2, 1)
    for r in range(15):
        _put_speckle(grid, r, 7)
    parse = PorterFerryArchetype().match(grid)
    assert parse is not None
    assert parse.boxes[(9, 4)] == "held"
    assert parse.boxes[(2, 2)] == "marked"
    assert parse.boxes[(2, 12)] == "dragged"
    assert (5, 7) in parse.speckle
    assert parse.rivals == frozenset({(2, 13)})
    assert parse.dock == frozenset({(12, 12), (13, 12)})


def test_match_abstains_on_random_grids():
    rng = np.random.default_rng(0)
    arch = PorterFerryArchetype()
    for _ in range(20):
        grid = rng.integers(0, 16, size=(64, 64)).astype(np.int16)
        assert arch.match(grid) is None


def test_match_abstains_on_structured_foreign_board():
    """A tile-lattice board in the ft09 style, even with a 7-filled bottom
    row, has no wa30 block grammar and must abstain."""

    grid = np.full((64, 64), 0, dtype=np.int16)
    for ti in range(4):
        for tj in range(4):
            r, c = 4 + 8 * ti, 4 + 8 * tj
            grid[r : r + 6, c : c + 6] = 8 if (ti + tj) % 2 else 3
    grid[63, :] = 7
    assert PorterFerryArchetype().match(grid) is None


def test_match_requires_full_signature():
    arch = PorterFerryArchetype()
    base = _l1_like()

    no_player = base.copy()
    _block(no_player, 11, 5)[:] = 1
    assert arch.match(no_player) is None

    no_boxes = base.copy()
    for pos in ((8, 5), (6, 2), (5, 9)):
        _block(no_boxes, *pos)[:] = 1
    assert arch.match(no_boxes) is None

    dead_timer = base.copy()
    dead_timer[63, :] = 4  # timer exhausted = GAME_OVER frame
    assert arch.match(dead_timer) is None

    ragged_timer = base.copy()
    ragged_timer[63, ::2] = 4  # interleaved, not the 7^k 4^m pattern
    assert arch.match(ragged_timer) is None

    alien_block = base.copy()
    _block(alien_block, 3, 3)[:] = 8  # colour outside the wa30 palette
    assert arch.match(alien_block) is None

    detached_hold = base.copy()
    _put_box(detached_hold, 2, 12, border=0)  # held box far from the player
    assert arch.match(detached_hold) is None


NPZ = Path(__file__).resolve().parents[1] / "results/diagnostics/recognizer_frames.npz"


@pytest.mark.skipif(not NPZ.exists(), reason="recognizer frame bank not present")
def test_match_abstains_on_every_foreign_recognizer_frame():
    z = np.load(NPZ)
    arch = PorterFerryArchetype()
    for key in z.keys():
        if key == "wa30":
            continue
        for frame in z[key]:
            assert arch.match(np.asarray(frame, dtype=np.int16)) is None


# ---------------------------------------------------------------- planner


def _one(steps: list[Step]) -> Step:
    """The archetype must emit ONE step per call (autonomous world)."""

    assert len(steps) == 1
    return steps[0]


def test_planner_walks_toward_a_pick_cell():
    arch = PorterFerryArchetype()
    grid = _l1_like()
    step = _one(arch.next_actions(arch.match(grid), grid))
    assert step.action in (1, 2, 3, 4)


def test_planner_picks_faced_marked_box():
    """At the pick cell, facing a marked box with a feasible carry: pick."""

    arch = PorterFerryArchetype()
    grid = _blank()
    _put_player(grid, 9, 5, facing=(-1, 0))
    _put_box(grid, 8, 5, border=3)  # marked, faced
    _put_dock(grid, 6, 5, 1, 3)
    step = _one(arch.next_actions(arch.match(grid), grid))
    assert step.action == 5


def test_planner_carries_held_box_toward_dock_and_drops_on_slot():
    arch = PorterFerryArchetype()
    carry = _blank()
    _put_player(carry, 9, 5, facing=(-1, 0))
    _put_box(carry, 8, 5, border=0)  # held, glued north
    _put_dock(carry, 6, 5, 1, 3)
    step = _one(arch.next_actions(arch.match(carry), carry))
    assert step.action == 1  # pair straight up: box (8,5) -> slot (6,5)

    on_slot = _blank()
    _put_player(on_slot, 7, 6, facing=(-1, 0))
    _put_box(on_slot, 6, 6, border=0)  # held box covers the middle slot
    _put_dock(on_slot, 6, 5, 1, 3)
    _block(on_slot, 6, 6)[:] = 0
    _block(on_slot, 6, 6)[1:3, 1:3] = 9
    step = _one(arch.next_actions(arch.match(on_slot), on_slot))
    assert step.action == 5  # slot remembered from the previous frame: drop


def test_planner_plants_through_wall_when_no_dock_is_reachable():
    """L3's measured loop: push the held box into an empty speckle socket
    whose far side reaches a rival and a dock, drop it, then release."""

    arch = PorterFerryArchetype()

    def wall_board():
        grid = _blank()
        for r in range(15):
            _put_speckle(grid, r, 8)
        _put_dock(grid, 6, 13, 2, 1)
        _put_rival(grid, 5, 12)
        return grid

    approach = wall_board()
    _put_player(approach, 5, 6, facing=(0, 1))
    _put_box(approach, 5, 7, border=0)  # held, glued east, beside the wall
    step = _one(arch.next_actions(arch.match(approach), approach))
    assert step.action == 4  # push east: box enters socket (5,8)

    in_socket = wall_board()
    _put_player(in_socket, 5, 7, facing=(0, 1))
    _put_box(in_socket, 5, 8, border=0)  # held box inside the wall socket
    step = _one(arch.next_actions(arch.match(in_socket), in_socket))
    assert step.action == 5  # drop in the socket

    dropped = wall_board()
    _put_player(dropped, 5, 7, facing=(0, 1))
    _put_box(dropped, 5, 8, border=3)  # dropped, still faced: must release
    step = _one(arch.next_actions(arch.match(dropped), dropped))
    assert step.action in (1, 2, 3)  # step away, never back into the box


def test_planner_idles_while_rivals_ferry():
    """All own-side work done (box planted and released): idle with 5, the
    measured safe world tick, while the rival ferries."""

    arch = PorterFerryArchetype()
    grid = _blank()
    for r in range(15):
        _put_speckle(grid, r, 8)
    _put_dock(grid, 6, 13, 2, 1)
    _put_rival(grid, 5, 12)
    _put_player(grid, 4, 6, facing=(-1, 0))  # parked, facing empty floor
    _put_box(grid, 5, 8, border=4)  # released box sitting in the wall
    step = _one(arch.next_actions(arch.match(grid), grid))
    assert step.action == 5


def test_planner_does_not_replant_a_delivered_box():
    """A released box inside the wall is the rivals' job now: the planner
    must not pull it back out even when it could reach it."""

    arch = PorterFerryArchetype()
    grid = _blank()
    for r in range(15):
        _put_speckle(grid, r, 8)
    _put_dock(grid, 6, 13, 2, 1)
    _put_rival(grid, 5, 12)
    _put_player(grid, 5, 6, facing=(0, 1))
    _put_box(grid, 5, 8, border=4)  # planted + released
    _put_box(grid, 9, 3, border=4)  # one ordinary box still to deliver
    parse = arch.match(grid)
    step = _one(arch.next_actions(parse, grid))
    assert step.action in (1, 2, 3, 4)
    # the move heads for the free box at (9,3), not the wall at (5,8)
    dr, dc = {1: (-1, 0), 2: (1, 0), 3: (0, -1), 4: (0, 1)}[step.action]
    assert (5 + dr, 6 + dc) != (5, 7)


def test_reset_clears_slot_memory():
    arch = PorterFerryArchetype()
    grid = _l1_like()
    arch.next_actions(arch.match(grid), grid)
    assert arch._dock_seen
    arch.reset()
    assert not arch._dock_seen and not arch._speckle_seen
