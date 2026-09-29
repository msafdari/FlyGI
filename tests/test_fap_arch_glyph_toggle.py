"""Offline acceptance tests for the ft09 glyph_toggle archetype (L5-L6).

Oracle: docs/fap_extension_20260928/ft09_L5/ -- the planted boards are the
MEASURED level-5/6 start grids and programs.json holds the click programs
that were executed against the real game (score transitions observed,
final GameState.WIN). The planner's solutions are unique on these boards
(masked tiles are toggled only by their own click, which pins every
prescribed variable), so the tests assert exact click-SET equality with
the verified programs rather than merely "some solution".
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from flygi.controller.fap_archetypes.glyph_toggle import (
    GlyphToggleArchetype,
    _solve_gf2,
    GlyphToggleParse,
)
from flygi.controller.fap_library import GlyphMiniatureArchetype, Step

DOSSIER = Path(__file__).resolve().parents[1] / "docs/fap_extension_20260928/ft09_L5"
RECOGNIZER_NPZ = (
    Path(__file__).resolve().parents[1] / "results/diagnostics/recognizer_frames.npz"
)


def load_board(name: str) -> np.ndarray:
    """Invert drive.py's render_grid: hex rows after a 4-char line prefix."""

    lines = (DOSSIER / name).read_text().splitlines()
    return np.array(
        [[int(ch, 16) for ch in line[4:68]] for line in lines[1:65]], dtype=np.int16
    )


def oracle_clicks(level: int) -> set[tuple[int, int]]:
    programs = json.loads((DOSSIER / "programs.json").read_text())
    return {(p["y"], p["x"]) for p in programs["programs"][str(level)]}


# ------------------------------------------------------- dossier-rule simulator


def _tile_block(grid: np.ndarray, r: int, c: int) -> np.ndarray | None:
    if r < 0 or c < 0 or r + 6 > grid.shape[0] or c + 6 > grid.shape[1]:
        return None
    return grid[r : r + 6, c : c + 6]


def _is_board_tile(block: np.ndarray | None, palette: set[int]) -> bool:
    return block is not None and set(np.unique(block)) <= (palette | {6})


def _flip(block: np.ndarray, palette: set[int]) -> None:
    a, b = sorted(palette)
    mask_a = block == a
    mask_b = block == b
    block[mask_a] = b
    block[mask_b] = a  # colour-6 mask sub-cells are untouched


def simulate(grid: np.ndarray, clicks, palette: set[int]) -> np.ndarray:
    """Apply the MEASURED click rule: a click toggles the tile's own palette
    phase plus each mask-directed orthogonal neighbour that is a present
    board tile; flips aimed at glyphs or absences are dropped."""

    out = grid.copy()
    for y, x in clicks:
        r, c = y - 3, x - 3
        block = _tile_block(out, r, c)
        assert _is_board_tile(block, palette), f"click at non-board tile ({y},{x})"
        # edge-centre sub-cells: (0,1)=N (1,0)=W (1,2)=E (2,1)=S
        dirs = []
        if block[0, 2] == 6:
            dirs.append((-1, 0))
        if block[2, 0] == 6:
            dirs.append((0, -1))
        if block[2, 4] == 6:
            dirs.append((0, 1))
        if block[4, 2] == 6:
            dirs.append((1, 0))
        _flip(block, palette)
        for dr, dc in dirs:
            neighbour = _tile_block(out, r + 8 * dr, c + 8 * dc)
            if _is_board_tile(neighbour, palette):
                _flip(neighbour, palette)
    return out


# ----------------------------------------------------------- planted positives


def test_level5_board_parses_and_plans_the_verified_program():
    grid = load_board("level5_start.txt")
    arch = GlyphToggleArchetype()
    parse = arch.match(grid)
    assert parse is not None
    assert parse.palette == frozenset({14, 15})
    assert len(parse.glyphs) == 8
    masked = {key for key, (_, dirs) in parse.tiles.items() if dirs}
    assert len(masked) == 3
    # the three checkered tiles carry all four directions
    assert all(len(parse.tiles[key][1]) == 4 for key in masked)
    steps = arch.next_actions(parse, grid)
    assert all(s.action == 6 for s in steps)
    assert {(s.y, s.x) for s in steps} == oracle_clicks(5)
    assert len(steps) == 21  # no duplicate clicks in a GF(2) solution
    # masked tiles first, mirroring the verified executed order
    kinds = [bool(parse.tiles[_key(parse, s)][1]) for s in steps]
    assert kinds == sorted(kinds, reverse=True)


def _key(parse: GlyphToggleParse, step: Step) -> tuple[int, int]:
    return (parse.rows.index(step.y - 3), parse.cols.index(step.x - 3))


def test_level6_board_parses_and_plans_the_verified_program():
    grid = load_board("level6_start.txt")
    arch = GlyphToggleArchetype()
    parse = arch.match(grid)
    assert parse is not None
    assert parse.palette == frozenset({11, 14})
    assert len(parse.glyphs) == 4
    # measured: EVERY level-6 board tile carries exactly the north mask
    assert all(dirs == ((-1, 0),) for _, dirs in parse.tiles.values())
    assert len(parse.tiles) == 22
    steps = arch.next_actions(parse, grid)
    assert {(s.y, s.x) for s in steps} == oracle_clicks(6)
    assert len(steps) == 13


def test_replanning_mid_solve_emits_exactly_the_remaining_clicks():
    """The executor re-parses whenever its queue empties; after k oracle
    clicks the re-derived plan must be exactly the remaining click set."""

    grid = load_board("level5_start.txt")
    arch = GlyphToggleArchetype()
    programs = json.loads((DOSSIER / "programs.json").read_text())
    ordered = [(p["y"], p["x"]) for p in programs["programs"]["5"]]
    for k in (3, 12, 20):
        mid = simulate(grid, ordered[:k], {14, 15})
        parse = arch.match(mid)
        assert parse is not None, f"abstained mid-solve after {k} clicks"
        steps = arch.next_actions(parse, mid)
        assert {(s.y, s.x) for s in steps} == set(ordered[k:])


def test_indicator_fallback_palette_from_phases_and_centres():
    """With the indicator erased, masks still claim the board and the
    fallback palette (tile phases + glyph centres) yields the same plan."""

    grid = load_board("level5_start.txt")
    grid[0:8, 53:59] = 4  # erase the e/f indicator pair
    arch = GlyphToggleArchetype()
    parse = arch.match(grid)
    assert parse is not None
    assert parse.palette == frozenset({14, 15})
    assert {(s.y, s.x) for s in arch.next_actions(parse, grid)} == oracle_clicks(5)


# ------------------------------------------------------------------- negatives


def test_abstains_on_random_grids():
    arch = GlyphToggleArchetype()
    rng = np.random.default_rng(20260928)
    for _ in range(25):
        grid = rng.integers(0, 16, size=(64, 64)).astype(np.int16)
        assert arch.match(grid) is None


def _plain_glyph_board() -> np.ndarray:
    """A structured NON-matching board: levels-1-4-style plain glyph lattice
    (no flip masks, no palette indicator) that GlyphMiniature handles."""

    grid = np.full((64, 64), 5, dtype=np.int16)
    for r in (8, 16):
        for c in (8, 16):
            grid[r : r + 6, c : c + 6] = 9
    glyph = np.array([[0, 0, 0], [0, 9, 0], [0, 0, 2]], dtype=np.int16)
    grid[8:14, 8:14] = np.kron(glyph, np.ones((2, 2), dtype=np.int16))
    return grid


def test_abstains_on_plain_glyph_board_which_glyph_miniature_claims():
    grid = _plain_glyph_board()
    assert GlyphToggleArchetype().match(grid) is None
    assert GlyphMiniatureArchetype().match(grid) is not None


def test_glyph_miniature_mis_claims_level5_so_seating_order_matters():
    """MEASURED coexistence hazard (dossier): GlyphMiniature parses the
    6-masked checkered tiles as glyphs and matches the L5 board, so
    glyph_toggle must be seated BEFORE it. This test documents the hazard;
    if GlyphMiniature ever learns to abstain here, seating becomes free."""

    grid = load_board("level5_start.txt")
    assert GlyphMiniatureArchetype().match(grid) is not None
    assert GlyphToggleArchetype().match(grid) is not None


def test_structural_violations_abstain():
    arch = GlyphToggleArchetype()

    # (a) a 0-cell aimed at an ABSENT position: glyph at lattice (0,1)
    # (rows 4-9, cols 14-19) has a 3 in sub-cell (1,0) pointing at the
    # absent (0,0); rewriting it to 0 breaks the measured consistency rule.
    grid = load_board("level5_start.txt")
    assert grid[6, 14] == 3
    grid[6:8, 14:16] = 0
    assert arch.match(grid) is None

    # (b) conflicting prescriptions: the glyphs at lattice (1,4) and (3,4)
    # both aim at tile (2,3); rewriting the (3,4) glyph's NW cell from 2 to
    # 0 makes them demand different phases.
    grid = load_board("level5_start.txt")
    assert grid[28, 38] == 2
    grid[28:30, 38:40] = 0
    assert arch.match(grid) is None

    # (c) a third colour among tile phases falls outside the palette.
    grid = load_board("level5_start.txt")
    assert (grid[20:26, 6:12] == 14).all()
    grid[20:26, 6:12] = 9
    assert arch.match(grid) is None

    # (d) a mask colour anywhere but an edge-centre sub-cell.
    grid = load_board("level5_start.txt")
    assert (grid[20:26, 14:20] == 14).all()
    grid[20:22, 14:16] = 6  # corner sub-cell of a board tile
    assert arch.match(grid) is None


@pytest.mark.skipif(not RECOGNIZER_NPZ.exists(), reason="diagnostics npz absent")
def test_negative_audit_recognizer_frames():
    """match() must abstain on every stored frame of every OTHER public
    game -- and on ft09's own stored frames too, which are plain level-1
    boards belonging to GlyphMiniature."""

    arch = GlyphToggleArchetype()
    frames = np.load(RECOGNIZER_NPZ)
    offenders = []
    for key in frames.keys():
        for index in range(frames[key].shape[0]):
            grid = np.asarray(frames[key][index], dtype=np.int16)
            if arch.match(grid) is not None:
                offenders.append((key, index))
    assert offenders == []


# ---------------------------------------------------------------- planner units


def test_gf2_solver_solves_and_detects_inconsistency():
    matrix = np.array([[1, 1, 0], [0, 1, 1], [0, 0, 1]], dtype=np.uint8)
    rhs = np.array([1, 0, 1], dtype=np.uint8)
    solution = _solve_gf2(matrix, rhs)
    assert solution is not None
    assert np.array_equal((matrix @ solution) % 2, rhs)
    bad = np.array([[1, 1], [1, 1]], dtype=np.uint8)
    assert _solve_gf2(bad, np.array([1, 0], dtype=np.uint8)) is None


def _chain_parse(phase_top: int, phase_bottom: int, targets) -> GlyphToggleParse:
    return GlyphToggleParse(
        rows=[0, 8],
        cols=[0],
        tiles={(0, 0): (phase_top, ()), (1, 0): (phase_bottom, ((-1, 0),))},
        glyphs={},
        palette=frozenset({11, 14}),
        targets=dict(targets),
    )


def test_planner_chain_back_substitution():
    arch = GlyphToggleArchetype()
    grid = np.zeros((16, 8), dtype=np.int16)  # unused by the planner
    # Only the top tile is wrong: clicking the bottom tile would flip both,
    # so the unique solution is the top tile's own (mask-free) click.
    steps = arch.next_actions(_chain_parse(11, 11, {(0, 0): 14, (1, 0): 11}), grid)
    assert [(s.y, s.x) for s in steps] == [(3, 3)]
    # Both tiles wrong: one bottom click flips both (north-mask carry).
    steps = arch.next_actions(_chain_parse(11, 11, {(0, 0): 14, (1, 0): 14}), grid)
    assert [(s.y, s.x) for s in steps] == [(11, 3)]
    # An already-satisfied board plans zero steps (the executor then treats
    # the archetype as not claiming this frame).
    steps = arch.next_actions(_chain_parse(11, 14, {(0, 0): 11, (1, 0): 14}), grid)
    assert steps == []


def test_reset_is_stateless_noop():
    arch = GlyphToggleArchetype()
    assert arch.name == "glyph_toggle"
    assert arch.reset() is None
    grid = load_board("level6_start.txt")
    first = arch.next_actions(arch.match(grid), grid)
    arch.reset()
    second = arch.next_actions(arch.match(grid), grid)
    assert [(s.y, s.x) for s in first] == [(s.y, s.x) for s in second]
