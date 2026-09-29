"""FlattenBuilderArchetype (sb26): parser and planner on planted boards.

The COMPARISON evidence for this archetype is the executor-driven offline
run recorded in WORKLOG/the extension dossier: seated alone in FapExecutor
it completes sb26 8/8 levels to GameState.WIN in 124 steps (the dossier's
hand-verified p_full.json is the oracle at the same count), against a
trivial alternative (random play) that has never scored on sb26. The
25-game recognizer-frame audit measured zero false matches. These tests
pin the parsing grammar and planner rules to planted frames so refactors
cannot silently bend them; planted geometry deliberately differs from
every real sb26 level so nothing here memorizes board instances.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from flygi.controller.fap_archetypes.flatten_builder import FlattenBuilderArchetype
from flygi.controller.fap_library import FapExecutor, Step

_BG = 4
_BAND = 5
_SLOT = 2
_MARK = 0


def _blank() -> np.ndarray:
    return np.full((64, 64), _BG, dtype=np.int16)


def _paint_legend(grid: np.ndarray, rows_of_colours: list[list[int]], col0: int = 4) -> None:
    """Band of hollow 6x6 glyphs; one glyph row per inner list."""

    n = max(len(r) for r in rows_of_colours)
    band_h = 1 + 7 * len(rows_of_colours)
    grid[0 : band_h + 1, col0 : col0 + 1 + 7 * n] = _BAND
    for gr, colours in enumerate(rows_of_colours):
        top = 1 + 7 * gr
        for g, colour in enumerate(colours):
            c = col0 + 1 + 7 * g
            grid[top : top + 6, c : c + 6] = colour
            grid[top + 1 : top + 5, c + 1 : c + 5] = _BAND


def _paint_box(
    grid: np.ndarray, colour: int, top: int, left: int, elements: list, root: bool = False
) -> None:
    width = 6 * len(elements) + 4
    right, bottom = left + width - 1, top + 9
    grid[top, left : right + 1] = colour
    grid[bottom, left : right + 1] = colour
    grid[top : bottom + 1, left] = colour
    grid[top : bottom + 1, right] = colour
    grid[top + 1 : bottom, left + 1 : right] = _BG
    for k, element in enumerate(elements):
        e0 = left + 3 + 6 * k
        if element == "hole":
            grid[top + 4 : top + 6, e0 + 1 : e0 + 3] = _SLOT
        else:
            kind, ecol = element
            grid[top + 3 : top + 7, e0 : e0 + 4] = ecol
            if kind == "ref":
                grid[top + 4 : top + 6, e0 + 1 : e0 + 3] = _BG
    if root:
        for y, x, dy, dx in (
            (top - 1, left - 1, 1, 1),
            (top - 1, right + 1, 1, -1),
            (bottom + 1, left - 1, -1, 1),
            (bottom + 1, right + 1, -1, -1),
        ):
            grid[y, min(x, x + 2 * dx) : max(x, x + 2 * dx) + 1] = _MARK
            grid[min(y + dy, y + 2 * dy) : max(y + dy, y + 2 * dy) + 1, x] = _MARK


def _paint_timer(grid: np.ndarray, row: int = 50) -> None:
    grid[row, :] = _SLOT


def _paint_tray(
    grid: np.ndarray, buttons: list, top: int = 53, col0: int = 5, pitch: int = 7
) -> dict[tuple[str, int], tuple[int, int]]:
    """Buttons as (kind, colour); returns (kind, colour) -> click (x, y)."""

    clicks: dict[tuple[str, int], tuple[int, int]] = {}
    for i, (kind, colour) in enumerate(buttons):
        c = col0 + pitch * i
        grid[top : top + 4, c : c + 4] = colour
        if kind == "ref":
            grid[top + 1 : top + 3, c + 1 : c + 3] = _BG
        clicks[(kind, colour)] = (c + 1, top + 1)
    return clicks


def _pairs(steps: list[Step]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Split a plan into ((button x, y), (slot x, y)) pairs; drops the submit."""

    assert steps[-1] == Step(action=5)
    body = steps[:-1]
    assert len(body) % 2 == 0
    return [
        ((body[i].x, body[i].y), (body[i + 1].x, body[i + 1].y))
        for i in range(0, len(body), 2)
    ]


def _literal_board() -> tuple[np.ndarray, dict]:
    """Level-1-shaped board on deliberately different coordinates:
    legend 9,e,b,f; root with four holes; scrambled literal tray."""

    grid = _blank()
    _paint_legend(grid, [[9, 14, 11, 15]])
    _paint_box(grid, 8, 20, 10, ["hole"] * 4, root=True)
    _paint_timer(grid)
    clicks = _paint_tray(grid, [("lit", 14), ("lit", 9), ("lit", 15), ("lit", 11)])
    return grid, clicks


class TestParser:
    def test_literal_board_parse(self) -> None:
        grid, _ = _literal_board()
        parse = FlattenBuilderArchetype().match(grid)
        assert parse is not None
        assert parse.legend == (9, 14, 11, 15)
        assert parse.root_colour == 8 and sorted(parse.boxes) == [8]
        assert [e.kind for e in parse.boxes[8].elements] == ["hole"] * 4
        assert [(b.kind, b.colour) for b in parse.buttons] == [
            ("lit", 14), ("lit", 9), ("lit", 15), ("lit", 11)
        ]

    def test_two_row_legend_reads_row_major(self) -> None:
        grid = _blank()
        _paint_legend(grid, [[11, 12], [11, 12]])
        _paint_box(grid, 8, 18, 8, ["hole", "hole"], root=True)
        _paint_box(grid, 9, 32, 30, ["hole", "hole"])
        _paint_timer(grid)
        _paint_tray(grid, [("lit", 11), ("lit", 12), ("ref", 9), ("ref", 8)])
        parse = FlattenBuilderArchetype().match(grid)
        assert parse is not None
        assert parse.legend == (11, 12, 11, 12)

    def test_connector_interrupted_border_still_parses(self) -> None:
        # Measured on level 2: a prefilled reference draws a 2-px connector
        # of its colour through the referencing box's bottom border.
        grid = _blank()
        _paint_legend(grid, [[6, 9, 8]])
        _paint_box(grid, 8, 18, 8, ["hole", ("ref", 9)], root=True)
        _paint_box(grid, 9, 32, 6, [("lit", 9), "hole"])
        grid[25:32, 18:20] = 9  # connector crossing the root bottom border
        _paint_timer(grid)
        clicks = _paint_tray(grid, [("lit", 6), ("lit", 8)])
        arch = FlattenBuilderArchetype()
        parse = arch.match(grid)
        assert parse is not None
        steps = arch.next_actions(parse, grid)
        assert _pairs(steps) == [
            (clicks[("lit", 6)], (12, 22)),
            (clicks[("lit", 8)], (16, 36)),
        ]

    def test_missing_root_brackets_abstains(self) -> None:
        grid = _blank()
        _paint_legend(grid, [[9, 14, 11, 15]])
        _paint_box(grid, 8, 20, 10, ["hole"] * 4, root=False)
        _paint_timer(grid)
        _paint_tray(grid, [("lit", 9), ("lit", 14), ("lit", 11), ("lit", 15)])
        assert FlattenBuilderArchetype().match(grid) is None

    def test_two_roots_abstain(self) -> None:
        grid = _blank()
        _paint_legend(grid, [[9, 14]])
        _paint_box(grid, 8, 18, 8, ["hole", "hole"], root=True)
        _paint_box(grid, 9, 32, 30, ["hole", "hole"], root=True)
        _paint_timer(grid)
        _paint_tray(grid, [("lit", 9), ("lit", 14), ("lit", 11), ("lit", 15)])
        assert FlattenBuilderArchetype().match(grid) is None

    def test_no_timer_row_abstains(self) -> None:
        grid, _ = _literal_board()
        grid[50, :] = _BG
        assert FlattenBuilderArchetype().match(grid) is None

    def test_random_grids_abstain(self) -> None:
        rng = np.random.default_rng(0)
        arch = FlattenBuilderArchetype()
        for _ in range(25):
            grid = rng.integers(0, 16, size=(64, 64)).astype(np.int16)
            assert arch.match(grid) is None

    def test_structured_foreign_board_abstains(self) -> None:
        # ft09-shaped board: colour-5 background with a 6x6 tile lattice.
        grid = np.full((64, 64), 5, dtype=np.int16)
        for r in range(2, 26, 8):
            for c in range(4, 28, 8):
                grid[r : r + 6, c : c + 6] = 9
        assert FlattenBuilderArchetype().match(grid) is None


class TestPlanner:
    def test_literal_plan_follows_legend_order(self) -> None:
        grid, clicks = _literal_board()
        arch = FlattenBuilderArchetype()
        steps = arch.next_actions(arch.match(grid), grid)
        # Slots left-to-right get the legend colours in order, each pair
        # clicking the (scrambled) tray button before its slot.
        assert _pairs(steps) == [
            (clicks[("lit", 9)], (14, 24)),
            (clicks[("lit", 14)], (20, 24)),
            (clicks[("lit", 11)], (26, 24)),
            (clicks[("lit", 15)], (32, 24)),
        ]

    def test_reference_plan_expands_sub_box(self) -> None:
        grid = _blank()
        _paint_legend(grid, [[6, 9, 8]])
        _paint_box(grid, 8, 18, 8, ["hole", "hole"], root=True)
        _paint_box(grid, 9, 32, 30, [("lit", 9), "hole"])
        _paint_timer(grid)
        clicks = _paint_tray(grid, [("lit", 6), ("ref", 9), ("lit", 8)])
        arch = FlattenBuilderArchetype()
        steps = arch.next_actions(arch.match(grid), grid)
        assert _pairs(steps) == [
            (clicks[("lit", 6)], (12, 22)),
            (clicks[("ref", 9)], (18, 22)),
            (clicks[("lit", 8)], (40, 36)),
        ]

    def test_cyclic_expansion_matches_legend_prefix(self) -> None:
        # Level-8-shaped: the legend shows two periods of an infinite
        # flatten produced by a reference cycle root <-> sub-box.
        grid = _blank()
        _paint_legend(grid, [[11, 12], [11, 12]])
        _paint_box(grid, 8, 18, 8, ["hole", "hole"], root=True)
        _paint_box(grid, 9, 32, 30, ["hole", "hole"])
        _paint_timer(grid)
        clicks = _paint_tray(grid, [("lit", 11), ("lit", 12), ("ref", 9), ("ref", 8)])
        arch = FlattenBuilderArchetype()
        steps = arch.next_actions(arch.match(grid), grid)
        assert _pairs(steps) == [
            (clicks[("lit", 11)], (12, 22)),
            (clicks[("ref", 9)], (18, 22)),
            (clicks[("lit", 12)], (34, 36)),
            (clicks[("ref", 8)], (40, 36)),
        ]

    def test_complete_matching_board_submits(self) -> None:
        grid = _blank()
        _paint_legend(grid, [[9, 14]])
        _paint_box(grid, 8, 20, 10, [("lit", 9), ("lit", 14)], root=True)
        _paint_timer(grid)
        arch = FlattenBuilderArchetype()
        parse = arch.match(grid)
        assert parse is not None
        assert arch.next_actions(parse, grid) == [Step(action=5)]

    def test_complete_mismatching_board_abstains(self) -> None:
        grid = _blank()
        _paint_legend(grid, [[9, 9]])
        _paint_box(grid, 8, 20, 10, [("lit", 9), ("lit", 14)], root=True)
        _paint_timer(grid)
        arch = FlattenBuilderArchetype()
        parse = arch.match(grid)
        assert parse is not None
        assert arch.next_actions(parse, grid) == []

    def test_button_hole_count_mismatch_abstains(self) -> None:
        grid = _blank()
        _paint_legend(grid, [[9, 14]])
        _paint_box(grid, 8, 20, 10, ["hole", "hole"], root=True)
        _paint_timer(grid)
        _paint_tray(grid, [("lit", 9)])
        arch = FlattenBuilderArchetype()
        parse = arch.match(grid)
        assert parse is not None
        assert arch.next_actions(parse, grid) == []

    def test_unsolvable_fill_abstains(self) -> None:
        grid = _blank()
        _paint_legend(grid, [[9]])
        _paint_box(grid, 8, 20, 10, ["hole"], root=True)
        _paint_timer(grid)
        _paint_tray(grid, [("lit", 11)])
        arch = FlattenBuilderArchetype()
        parse = arch.match(grid)
        assert parse is not None
        assert arch.next_actions(parse, grid) == []

    def test_selected_button_pair_goes_first_without_reclick(self) -> None:
        # Measured (level 1, run 1): a selected button carries a colour-0
        # ring; re-clicking it is unmeasured, so the plan places it first
        # via the slot click alone.
        grid, clicks = _literal_board()
        bx, by = clicks[("lit", 9)]  # click point = button top-left + 1
        grid[by - 2, bx - 2 : bx + 4] = _MARK  # 6x6 ring around the 4x4 button
        grid[by + 3, bx - 2 : bx + 4] = _MARK
        grid[by - 2 : by + 4, bx - 2] = _MARK
        grid[by - 2 : by + 4, bx + 3] = _MARK
        arch = FlattenBuilderArchetype()
        parse = arch.match(grid)
        assert parse is not None
        assert [(b.colour, b.selected) for b in parse.buttons if b.selected] == [(9, True)]
        steps = arch.next_actions(parse, grid)
        assert steps[0] == Step(action=6, x=14, y=24)  # slot click, no re-click
        assert len(steps) == 8  # 3 full pairs + 1 slot-only + submit
        assert steps[-1] == Step(action=5)

    def test_seated_in_executor_emits_first_step(self) -> None:
        grid, clicks = _literal_board()
        executor = FapExecutor(archetypes=[FlattenBuilderArchetype()])
        step = executor.propose(grid)
        assert step == Step(action=6, x=clicks[("lit", 9)][0], y=clicks[("lit", 9)][1])


_NPZ = Path(__file__).resolve().parents[1] / "results/diagnostics/recognizer_frames.npz"


@pytest.mark.skipif(not _NPZ.exists(), reason="recognizer frame archive absent")
def test_foreign_game_frames_never_match() -> None:
    z = np.load(_NPZ)
    arch = FlattenBuilderArchetype()
    for key in z.files:
        if key == "sb26":
            continue
        for frame in z[key]:
            assert arch.match(np.asarray(frame, dtype=np.int16)) is None, key
