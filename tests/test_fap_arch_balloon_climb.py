"""Offline acceptance tests for the bp35 balloon_climb archetype.

Oracles: docs/fap_extension_20260928/bp35/ -- live_init.txt, live_003.txt
and live_last.txt are MEASURED frame dumps of the real offline game (the
dossier's drive.py renders at level-1 start, after 4 actions of the
verified program, and at level-5 start), and grids.txt transcribes the
level maps those frames must parse into.  The synthetic boards below are
built from the same sprite grammar (game source sprite table, confirmed
against the dumps) so the planner's unit behaviour can be pinned on
hand-crafted layouts.

The end-to-end number, MEASURED with the executor driver on the offline
arcade (seed derived_run_seeds(0), 2026-09-28): levels 1-6 completed in
222 driver steps; the dossier's verified hand programs covered levels 1-4.
Level 7's toggle labyrinth is the recorded planner limit.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from flygi.controller.fap_archetypes import balloon_climb as bc
from flygi.controller.fap_archetypes.balloon_climb import (
    BalloonClimbArchetype,
    _read_budget,
)
from flygi.controller.fap_library import Step

REPO = Path(__file__).resolve().parents[1]
DOSSIER = REPO / "docs/fap_extension_20260928/bp35"
RECOGNIZER_NPZ = REPO / "results/diagnostics/recognizer_frames.npz"

HEX = "0123456789abcdef"


def load_dump(name: str) -> np.ndarray:
    rows = []
    for line in (DOSSIER / name).read_text().splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        if len(parts[1]) == 64 and all(ch in HEX for ch in parts[1]):
            rows.append([HEX.index(ch) for ch in parts[1]])
    assert len(rows) == 64
    return np.array(rows, dtype=np.int16)


# ------------------------------------------------------------- renderer
# Synthetic frames from the sprite grammar (game source sprite table,
# confirmed against the dossier dumps).  World chars follow the dossier
# solver's vocabulary: o wall, . air, x door, 1/2 toggles, g gravity,
# v spike, + gem, n player, m/w flood.


def _paint(canvas: np.ndarray, sy: int, sx: int, ch: str) -> None:
    cell = canvas[sy : sy + 6, sx : sx + 6]
    if ch == "o":
        cell[:] = bc._WALL_CELL
        return
    cell[:] = 10
    if ch == ".":
        return
    if ch in "x1g":
        colour = {"x": 14, "1": 12, "g": 8}[ch]
        cell[:] = 5
        cell[1:6, 1:6] = colour
        for r, c in ((1, 1), (1, 5), (5, 1), (5, 5)):
            cell[r, c] = 3
    elif ch == "2":
        for r, c in ((2, 2), (2, 4), (3, 3), (4, 2), (4, 4)):
            cell[r, c] = 12
    elif ch == "+":
        for r, c in ((1, 3), (2, 2), (2, 3), (2, 4), (3, 3)):
            cell[r, c] = 7
    elif ch == "v":
        cell[:] = 5
        cell[1:5, 2:5] = 15
        cell[5, 2] = 11
        cell[5, 3] = 0
        cell[5, 4] = 11
    elif ch == "n":
        for r, c in ((1, 3), (2, 2), (2, 3), (3, 2), (3, 3), (4, 3)):
            cell[r, c] = 9
        cell[2, 4] = 11
        cell[3, 4] = 11
    elif ch == "m":
        cell[:] = 5
        cell[5, 1] = 15
        cell[5, 2] = 15
        cell[5, 4] = 15
    elif ch == "w":
        cell[:] = 15
        cell[2, 2] = 5
        cell[4, 1] = 5
    else:  # pragma: no cover - typo guard
        raise ValueError(ch)


def render(world: dict[int, str], player_row: int, budget: int = 0) -> np.ndarray:
    """Render the rising-camera frame for a world given as {row: 11 chars}."""

    canvas = np.zeros((70, 66), dtype=np.int16)
    for block in range(11):
        wr = player_row + block - 6
        line = world.get(wr, "o" * 11)
        assert len(line) == 11
        for col, ch in enumerate(line):
            _paint(canvas, block * 6, col * 6, ch)
    frame = canvas[:64, :64].copy()
    frame[63, :] = 0
    if budget:
        frame[63, :budget] = 15
    return frame


def small_world(rows: list[str], player_row_index: int) -> dict[int, str]:
    """Rows listed top-down; the player's 'n' row index anchors them."""

    base = 100 - player_row_index
    return {base + i: row for i, row in enumerate(rows)}


# --------------------------------------------------- measured positives


def test_matches_level1_start_frame() -> None:
    arch = BalloonClimbArchetype()
    parse = arch.match(load_dump("live_init.txt"))
    assert parse is not None
    assert parse.pos == (3, 100)
    assert parse.grav_up is True
    assert parse.budget_used == 0 and parse.budget_limit == 64
    # grids.txt (grid1): doors three cells up at cols 2-4, walls flanking
    assert [parse.cells[(c, -6)] for c in range(2, 5)] == ["x", "x", "x"]
    assert parse.cells[(0, 0)] == "o"
    assert parse.cells[(3, 0)] == "n"
    assert parse.cells[(7, -1)] == "."


def test_matches_mid_program_frame() -> None:
    # after four verified actions (R,R,R,R) of prog_l1234
    arch = BalloonClimbArchetype()
    parse = arch.match(load_dump("live_003.txt"))
    assert parse is not None
    assert parse.pos[0] == 7
    assert parse.budget_used == 4


def test_matches_level5_start_frame() -> None:
    arch = BalloonClimbArchetype()
    parse = arch.match(load_dump("live_last.txt"))
    assert parse is not None
    assert parse.pos[0] == 3 and parse.grav_up is True
    # grids.txt (grid5): gem five cells up at col 5, spikes right of it,
    # a gravity button on the player's row at col 8
    assert parse.cells[(5, -5)] == "+"
    assert parse.cells[(7, -5)] == "v"
    assert parse.cells[(8, 0)] == "g"
    steps = arch.next_actions(parse, load_dump("live_last.txt"))
    assert len(steps) == 1 and steps[0].action in (3, 4, 6)


# ------------------------------------------------------------ negatives


def test_abstains_on_random_grids() -> None:
    rng = np.random.default_rng(20260928)
    arch = BalloonClimbArchetype()
    for _ in range(50):
        grid = rng.integers(0, 16, size=(64, 64), dtype=np.int16)
        assert arch.match(grid) is None


def test_abstains_on_structured_pip_board() -> None:
    # an sc25-flavoured colour-3 framed pip lattice: structured, non-bp35
    grid = np.full((64, 64), 5, dtype=np.int16)
    for by in range(3):
        for bx in range(3):
            y, x = 10 + by * 5, 20 + bx * 5
            grid[y : y + 5, x : x + 5] = 3
            grid[y + 1 : y + 4, x + 1 : x + 4] = 0 if (by + bx) % 2 else 2
    grid[63, :] = 0
    assert BalloonClimbArchetype().match(grid) is None


def test_abstains_on_misaligned_avatar() -> None:
    # a bp35-looking frame whose player sits OFF the 36/26 camera line
    world = small_world(
        ["ooooooooooo", "o...n....oo", "ooooooooooo"], 1
    )
    frame = render(world, 100)
    good = BalloonClimbArchetype().match(frame)
    assert good is not None
    shifted = np.full_like(frame, 5)
    shifted[:-6] = frame[6:]  # move everything up one cell row
    shifted[63, :] = 0
    assert BalloonClimbArchetype().match(shifted) is None


@pytest.mark.skipif(
    not RECOGNIZER_NPZ.exists(), reason="recognizer frames not present"
)
def test_negative_audit_recognizer_frames() -> None:
    npz = np.load(RECOGNIZER_NPZ)
    offenders = []
    for key in npz.files:
        if key.startswith("bp35"):
            continue
        for i, frame in enumerate(np.asarray(npz[key], dtype=np.int16)):
            if BalloonClimbArchetype().match(frame) is not None:
                offenders.append((key, i))
    assert offenders == []


# --------------------------------------------------------- planner units


def test_plans_direct_move_onto_gem() -> None:
    world = small_world(
        ["ooooooooooo", "o..n+....oo", "ooooooooooo"], 1
    )
    frame = render(world, 100)
    arch = BalloonClimbArchetype()
    parse = arch.match(frame)
    assert parse is not None and parse.pos == (3, 100)
    assert arch.next_actions(parse, frame) == [Step(action=4)]


def test_plans_click_launch_through_door() -> None:
    # gem two cells above the player behind a door: the measured
    # click-above launch traverses the clicked door in one action
    world = small_world(
        [
            "ooooooooooo",
            "ooo+ooooooo",
            "ooo.ooooooo",
            "oooxooooooo",
            "o..n.....oo",
            "ooooooooooo",
        ],
        4,
    )
    frame = render(world, 100)
    arch = BalloonClimbArchetype()
    parse = arch.match(frame)
    assert parse is not None
    steps = arch.next_actions(parse, frame)
    assert steps == [Step(action=6, x=3 * 6 + 3, y=33)]  # click one above


def test_avoids_spike_route() -> None:
    # right route rises into a spike (death); left route reaches the gem
    world = small_world(
        [
            "ooooooooooo",
            "o+ooooooooo",
            "o.ooooooooo",
            "o.oovoooooo",
            "o..n.oooooo",
            "ooooooooooo",
        ],
        4,
    )
    frame = render(world, 100)
    arch = BalloonClimbArchetype()
    parse = arch.match(frame)
    assert parse is not None
    # moving right would rise into the spike: the simulator must prune it
    assert arch._sim_move(parse.pos, True, {}, None, 0, 1) is None
    assert arch.next_actions(parse, frame) == [Step(action=3)]


def test_flood_kill_rule_is_conservative() -> None:
    # the dossier solver's verified rule: a zero-rise lateral on an even
    # post-parity advances the surface and must not land at/below it
    world = small_world(
        ["ooooooooooo", "o..n.oooooo", "ooooooooooo"], 1
    )
    frame = render(world, 100)
    arch = BalloonClimbArchetype()
    parse = arch.match(frame)
    assert parse is not None
    # surface one row below the player, advancing move -> caught
    assert arch._sim_move(parse.pos, True, {}, 101, 1, 1) is None
    # same move on odd post-parity does not advance the flood
    out = arch._sim_move(parse.pos, True, {}, 101, 0, 1)
    assert out is not None and out.s_row == 101 and out.pos == (4, 100)


def test_click_xy_mapping() -> None:
    arch = BalloonClimbArchetype()
    pos = (3, 100)
    assert arch._click_xy(3, 99, pos, True) == (21, 33)
    assert arch._click_xy(3, 104, pos, True) == (21, 62)  # row 63 avoided
    assert arch._click_xy(3, 94, pos, True) == (21, 3)  # gravity-only row
    assert arch._click_xy(8, 101, pos, False) == (51, 35)


def test_budget_bar_decoding() -> None:
    row = np.zeros(64, dtype=np.int16)
    assert _read_budget(row) == (0, 64)
    row[:17] = 15
    assert _read_budget(row) == (17, 64)  # levels 1-6 fill colour 15
    row[:] = 0
    row[:30] = 7
    assert _read_budget(row) == (30, 128)  # levels 7+ fill colour 7
    row[:64] = 7
    row[:10] = 15
    assert _read_budget(row) == (74, 128)
    assert _read_budget(np.full(64, 5, dtype=np.int16)) is None
    assert _read_budget(np.full(64, 4, dtype=np.int16)) is None


def test_reset_clears_life_but_keeps_level_memory() -> None:
    frame = render(
        small_world(["ooooooooooo", "o..n+....oo", "ooooooooooo"], 1), 100
    )
    arch = BalloonClimbArchetype()
    parse = arch.match(frame)
    assert parse is not None
    arch.next_actions(parse, frame)
    assert arch._anchored and arch._world
    arch.reset()
    assert not arch._anchored and not arch._world
    # the per-LEVEL cache (keyed by the level's first-frame bytes) stays:
    # a re-run life on the byte-identical board reloads its geometry
    assert arch._level_cache
    parse2 = arch.match(frame)
    assert parse2 is not None and arch._world
