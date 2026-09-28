"""FAP library: parser correctness on planted boards.

The COMPARISON evidence for this component (the operating directive's
requirement) is recorded under H-FAP-PROGRAMS: solver-driven offline play
completes ft09 levels 1-2 and sc25 level 1 against a trivial alternative
(random legal play) that has scored 0 on those games in every battery row
ever run, and the 25-game audit measured zero false matches and zero
emitted actions on the other 23 games. These tests only pin the parsing
rules to planted frames so refactors cannot silently bend them.
"""

from __future__ import annotations

import numpy as np
import pytest

from flygi.controller.fap_library import (
    FapExecutor,
    GlyphMiniatureArchetype,
    PipPunchRollArchetype,
    Step,
)


def _paint_tile(grid: np.ndarray, row: int, col: int, blocks: np.ndarray) -> None:
    for r in range(3):
        for c in range(3):
            grid[row + 2 * r : row + 2 * r + 2, col + 2 * c : col + 2 * c + 2] = blocks[r, c]


def _glyph_frame() -> np.ndarray:
    """One 3x3 lattice: dominant tiles 9, one 8-tile, a mismatching glyph."""

    grid = np.full((64, 64), 5, dtype=np.int16)
    plain9 = np.full((3, 3), 9, dtype=np.int16)
    plain8 = np.full((3, 3), 8, dtype=np.int16)
    # Glyph prescribes tile (0,0) of its neighbourhood to be 8 (cell 0) and
    # the rest to stay 9 (cell 2); centre carries the marked colour 8.
    glyph = np.array([[0, 2, 2], [2, 8, 2], [2, 2, 2]], dtype=np.int16)
    rows, cols = [2, 10, 18], [4, 12, 20]
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            if (i, j) == (1, 1):
                _paint_tile(grid, r, c, glyph)
            elif (i, j) == (2, 2):
                _paint_tile(grid, r, c, plain8)
            else:
                _paint_tile(grid, r, c, plain9)
    return grid


class TestGlyphMiniature:
    def test_emits_click_only_for_unsatisfied_zero_cell(self) -> None:
        archetype = GlyphMiniatureArchetype()
        grid = _glyph_frame()
        parses = archetype.match(grid)
        assert parses is not None and len(parses) == 1
        steps = archetype.next_actions(parses, grid)
        # Tile (0,0) (top-left, currently 9) is the only 0-prescribed
        # mismatch; its centre pixel is (row 2+3, col 4+3).
        assert steps == [Step(action=6, x=7, y=5)]

    def test_satisfied_board_emits_nothing(self) -> None:
        archetype = GlyphMiniatureArchetype()
        grid = _glyph_frame()
        grid[2:8, 4:10] = 8  # satisfy the prescription
        parses = archetype.match(grid)
        assert parses is not None
        assert archetype.next_actions(parses, grid) == []

    def test_plain_screen_abstains(self) -> None:
        grid = np.full((64, 64), 5, dtype=np.int16)
        grid[10:20, 10:30] = 7
        assert GlyphMiniatureArchetype().match(grid) is None


class TestPipPunchRoll:
    def _board(self) -> np.ndarray:
        grid = np.full((64, 64), 5, dtype=np.int16)
        grid[47:64, 22:41] = 3
        for i, row in enumerate((49, 54, 59)):
            for j, col in enumerate((24, 29, 34)):
                value = 0 if (i + j) % 2 == 1 else 2
                grid[row : row + 3, col : col + 3] = value
        return grid

    def test_punches_zero_cells(self) -> None:
        archetype = PipPunchRollArchetype()
        grid = self._board()
        parse = archetype.match(grid)
        assert parse is not None
        steps = archetype.next_actions(parse, grid)
        assert all(step.action == 6 for step in steps)
        assert len(steps) == 4  # the (i+j) odd cells
        clicked = {(step.y, step.x) for step in steps}
        assert (49 + 1, 29 + 1) in clicked  # a punched pip's centre

    def test_rolls_when_no_pips_remain(self) -> None:
        archetype = PipPunchRollArchetype()
        grid = self._board()
        grid[grid == 0] = 2
        parse = archetype.match(grid)
        assert parse is not None
        assert archetype.next_actions(parse, grid) == [Step(action=3)]


class TestExecutor:
    def test_abstains_and_costs_nothing_on_unknown_screens(self) -> None:
        executor = FapExecutor()
        grid = np.random.default_rng(0).integers(0, 16, size=(64, 64), dtype=np.int16)
        executor.observe(grid)
        assert executor.propose(grid) is None
        assert executor.describe()["matched"] is None

    def test_swallow_retry_reissues_once(self) -> None:
        executor = FapExecutor()
        grid = _glyph_frame()
        executor.observe(grid)
        first = executor.propose(grid)
        assert first is not None
        executor.observe(grid)  # frame unchanged: the engine swallowed it
        second = executor.propose(grid)
        assert second == first


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
