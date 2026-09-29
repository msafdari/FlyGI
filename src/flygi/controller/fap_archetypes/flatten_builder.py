"""sb26 archetype: recursive sequence builder ("flatten builder").

Decoded 2026-09-28 (docs/fap_extension_20260928/sb26/): the legend band at
the top of the screen displays FLATTEN(root box), where flatten walks a
box's elements left-to-right, a literal contributes its colour, and a
reference contributes the flatten of the box outlined in its colour. The
player fills every empty slot by clicking a tray button (solid = colour
literal, hollow = reference) and then the slot, then presses action 5 to
submit. Verified oracle: p_full.json replays 8/8 levels to GameState.WIN.

This module is ENGINEERED SCAFFOLD end to end, recorded as such per the
repository first principle -- no fly circuit computes anything here.

Grammar constants (all MEASURED across the 8 verified levels):
  * background colour 4; legend band fill colour 5; slot marks, tray
    remnants and the remaining-timer cells colour 2; used-timer cells
    colour 3; root-corner brackets and the selection ring colour 0.
  * legend glyphs: 6x6 hollow squares (ring = entry colour, interior 5),
    read row-major (level 8 renders the cyclic expansion as two band rows).
  * boxes: 1-px rectangular outlines, exactly 10 rows tall, width 6n+4 for
    n elements at columns left+3+6k; elements are 4x4 blocks vertically
    centred (rows top+3..top+6): empty slot = central 2x2 colour-2 mark on
    background, literal = solid 4x4, reference = 4x4 ring with background
    interior. The root box carries colour-0 corner brackets diagonally
    outside its four corners. A prefilled reference may draw a 2-px
    connector line of its colour which can interrupt a box border (level 2
    bottom border) -- borders are therefore matched with <=2-px non-
    background gaps allowed.
  * timer: the single full-width row whose cells are all in {2, 3}.
  * tray: 4x4 solid/hollow buttons sharing one top row below the timer; a
    selected button carries a colour-0 ring (rows t-1..t+4).

Board-instance data (absolute coordinates of any specific level, action
scripts, game-id checks) is deliberately absent: everything above is a
shape/colour grammar re-derived from the current frame on every call.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

_BG = 4  # background (measured, levels 1-8)
_BAND = 5  # legend band fill
_SLOT = 2  # slot mark / tray remnant / timer "remaining"
_TIMER_USED = 3
_MARK = 0  # root corner brackets, selection ring
_RESERVED = frozenset({_MARK, _SLOT, _TIMER_USED, _BG, _BAND})

_BOX_HEIGHT = 10  # border rows included (measured on every box, levels 1-8)
_ELEM = 4  # element block size
_PITCH = 6  # element pitch inside a box
_GLYPH = 6  # legend glyph size
# ASSUMPTION: hidden levels keep every geometric constant above. Measured
# only on the 8 public levels; a level violating them makes match() abstain
# (checked by construction below), which costs nothing but the level.


@dataclass(frozen=True)
class _Element:
    kind: str  # 'lit' | 'ref' | 'hole'
    colour: int  # -1 for holes
    click_col: int  # slot-mark top-left (holes; click target)
    click_row: int


@dataclass(frozen=True)
class _Box:
    colour: int
    top: int
    left: int
    width: int
    elements: tuple[_Element, ...]
    is_root: bool


@dataclass(frozen=True)
class _Button:
    kind: str  # 'lit' | 'ref'
    colour: int
    click_col: int
    click_row: int
    selected: bool


@dataclass(frozen=True)
class BuilderParse:
    legend: tuple[int, ...]
    boxes: dict[int, _Box]  # keyed by outline colour
    root_colour: int
    buttons: tuple[_Button, ...]


def _find_timer_row(grid: NDArray[np.int16]) -> Optional[int]:
    rows = np.nonzero(np.isin(grid, (_SLOT, _TIMER_USED)).all(axis=1))[0]
    if rows.size != 1:
        return None
    return int(rows[0])


def _find_legend(
    grid: NDArray[np.int16], timer_row: int
) -> Optional[list[tuple[int, int, int]]]:
    """Return legend glyphs as (row, col, colour), or None.

    A glyph is a 6x6 hollow square whose 4x4 interior is band colour 5 and
    whose ring is one colour outside the reserved set, embedded in the band
    (the pixels above and left of its top-left corner are colour 5).
    """

    interior5 = grid == _BAND
    if not interior5.any():
        return None
    win = np.lib.stride_tricks.sliding_window_view(interior5, (4, 4))
    inner_ok = win.all(axis=(2, 3))  # inner_ok[r, c]: 4x4 all-5 at (r, c)
    glyphs: list[tuple[int, int, int]] = []
    height, width = grid.shape
    limit = min(timer_row - _GLYPH, height - _GLYPH)
    for r in range(1, max(limit, 1)):
        for c in range(1, width - _GLYPH + 1):
            if not inner_ok[r + 1, c + 1]:
                continue
            colour = int(grid[r, c])
            if colour in _RESERVED:
                continue
            block = grid[r : r + _GLYPH, c : c + _GLYPH]
            ring = np.concatenate(
                [block[0], block[-1], block[1:-1, 0], block[1:-1, -1]]
            )
            if not (ring == colour).all():
                continue
            if grid[r - 1, c] != _BAND or grid[r, c - 1] != _BAND:
                continue
            glyphs.append((r, c, colour))
    return glyphs or None


def _merged_runs(row: NDArray[np.int16], colour: int) -> list[tuple[int, int]]:
    """Maximal runs of ``colour``, merging gaps of <=2 non-background pixels
    (a prefilled reference's connector line may cross a box border)."""

    idx = np.nonzero(row == colour)[0]
    if idx.size == 0:
        return []
    runs: list[list[int]] = [[int(idx[0]), int(idx[0])]]
    for i in idx[1:]:
        i = int(i)
        if i == runs[-1][1] + 1:
            runs[-1][1] = i
            continue
        gap = row[runs[-1][1] + 1 : i]
        if gap.size <= 2 and not (gap == _BG).any():
            runs[-1][1] = i
        else:
            runs.append([i, i])
    return [(a, b) for a, b in runs]


def _border_line_ok(cells: NDArray[np.int16], colour: int) -> bool:
    """A 10-px vertical border: all box colour, allowing <=2 non-background
    interruptions (connector crossings; unmeasured on vertical borders but
    symmetric with the measured horizontal case)."""

    wrong = cells != colour
    return int(wrong.sum()) <= 2 and not (cells[wrong] == _BG).any()


def _parse_box_elements(
    grid: NDArray[np.int16], top: int, left: int, width: int
) -> Optional[tuple[_Element, ...]]:
    count = (width - 4) // _PITCH
    elements: list[_Element] = []
    interior_cols = np.ones(width - 2, dtype=bool)  # cols left+1..left+width-2
    for k in range(count):
        e0 = left + 3 + _PITCH * k
        interior_cols[e0 - left - 1 : e0 - left - 1 + _ELEM] = False
        block = grid[top + 3 : top + 7, e0 : e0 + _ELEM]
        centre = block[1:3, 1:3]
        ring = np.concatenate(
            [block[0], block[-1], block[1:-1, 0], block[1:-1, -1]]
        )
        colour = int(block[0, 0])
        if colour == _BG:
            # Empty slot: central 2x2 mark on background.
            if not (centre == _SLOT).all():
                return None
            outer = block.copy()
            outer[1:3, 1:3] = _BG
            if not (outer == _BG).all():
                return None
            elements.append(_Element("hole", -1, e0 + 1, top + 4))
        elif colour in _RESERVED:
            return None
        elif (block == colour).all():
            elements.append(_Element("lit", colour, e0 + 1, top + 4))
        elif (ring == colour).all() and (centre == _BG).all():
            elements.append(_Element("ref", colour, e0 + 1, top + 4))
        else:
            return None
    # Between and beside elements the element rows are background (measured
    # on all boxes; connectors never cross element rows of another box).
    gap = grid[top + 3 : top + 7, left + 1 : left + width - 1][:, interior_cols]
    if gap.size and not (gap == _BG).all():
        return None
    return tuple(elements)


def _find_boxes(
    grid: NDArray[np.int16], row_lo: int, row_hi: int
) -> Optional[dict[int, _Box]]:
    """Boxes in rows [row_lo, row_hi); None on any structural violation."""

    height, width = grid.shape
    found: list[_Box] = []
    claimed: set[tuple[int, int]] = set()
    for r in range(row_lo, min(row_hi - _BOX_HEIGHT + 1, height - _BOX_HEIGHT + 1)):
        row = grid[r]
        for colour in np.unique(row):
            colour = int(colour)
            if colour in _RESERVED:
                continue
            for c0, c1 in _merged_runs(row, colour):
                w = c1 - c0 + 1
                if w < 10 or (w - 4) % _PITCH != 0:
                    continue
                if (r, c0) in claimed:
                    continue
                bottom = r + _BOX_HEIGHT - 1
                if bottom >= row_hi:
                    continue
                if not any(
                    a <= c0 and c1 <= b
                    for a, b in _merged_runs(grid[bottom], colour)
                ):
                    continue
                if not _border_line_ok(grid[r : bottom + 1, c0], colour):
                    continue
                if not _border_line_ok(grid[r : bottom + 1, c1], colour):
                    continue
                elements = _parse_box_elements(grid, r, c0, w)
                if elements is None:
                    continue
                corners = [
                    (r - 1, c0 - 1),
                    (r - 1, c1 + 1),
                    (bottom + 1, c0 - 1),
                    (bottom + 1, c1 + 1),
                ]
                is_root = all(
                    0 <= y < height and 0 <= x < width and grid[y, x] == _MARK
                    for y, x in corners
                )
                claimed.add((r, c0))
                found.append(_Box(colour, r, c0, w, elements, is_root))
    if not found:
        return None
    boxes: dict[int, _Box] = {}
    for box in found:
        if box.colour in boxes:
            return None  # ambiguous references; measured levels never do this
        boxes[box.colour] = box
    return boxes


def _find_buttons(
    grid: NDArray[np.int16], timer_row: int
) -> Optional[tuple[_Button, ...]]:
    height, width = grid.shape
    buttons: list[_Button] = []
    for t in range(timer_row + 1, height - _ELEM + 1):
        for c in range(width - _ELEM + 1):
            colour = int(grid[t, c])
            if colour in _RESERVED:
                continue
            if grid[t - 1, c] == colour or (c > 0 and grid[t, c - 1] == colour):
                continue  # not a top-left corner
            block = grid[t : t + _ELEM, c : c + _ELEM]
            ring = np.concatenate(
                [block[0], block[-1], block[1:-1, 0], block[1:-1, -1]]
            )
            centre = block[1:3, 1:3]
            if (block == colour).all():
                kind = "lit"
            elif (ring == colour).all() and (centre == _BG).all():
                kind = "ref"
            else:
                return None  # stray non-grammar shape below the timer
            selected = bool(t >= 1 and grid[t - 1, c] == _MARK)
            buttons.append(_Button(kind, colour, c + 1, t + 1, selected))
    rows = {b.click_row for b in buttons}
    if len(rows) > 1:
        return None  # tray buttons share one top row (measured, all levels)
    return tuple(buttons)


class FlattenBuilderArchetype:
    """sb26's measured rule: fill slots so flatten(root) renders the legend,
    then submit with action 5. Fully stateless: every call re-derives the
    parse and the plan from the current grid."""

    name = "flatten_builder"

    def reset(self) -> None:
        pass  # no per-life state; the plan is re-derived from the grid

    def match(self, grid: NDArray[np.int16]) -> Optional[BuilderParse]:
        grid = np.asarray(grid, dtype=np.int16)
        if grid.shape != (64, 64):
            return None
        # Cheap gates first: this path runs on every turn of every game.
        counts = np.bincount(grid.ravel(), minlength=16)
        if int(counts.argmax()) != _BG:
            return None
        timer_row = _find_timer_row(grid)
        if timer_row is None or timer_row < 12:
            return None
        glyphs = _find_legend(grid, timer_row)
        if glyphs is None:
            return None
        band_bottom = max(r for r, _, _ in glyphs) + _GLYPH
        boxes = _find_boxes(grid, band_bottom + 1, timer_row)
        if boxes is None:
            return None
        roots = [b.colour for b in boxes.values() if b.is_root]
        if len(roots) != 1:
            return None
        # Every reference (element or button) must name an existing box.
        for box in boxes.values():
            for element in box.elements:
                if element.kind == "ref" and element.colour not in boxes:
                    return None
        buttons = _find_buttons(grid, timer_row)
        if buttons is None:
            return None
        for button in buttons:
            if button.kind == "ref" and button.colour not in boxes:
                return None
        legend = tuple(colour for _, _, colour in sorted(glyphs))
        return BuilderParse(legend, boxes, roots[0], buttons)

    def next_actions(
        self, parse: BuilderParse, grid: NDArray[np.int16]
    ) -> list[Step]:
        holes: list[tuple[int, int]] = []  # (box colour, element index)
        for box in parse.boxes.values():
            for i, element in enumerate(box.elements):
                if element.kind == "hole":
                    holes.append((box.colour, i))
        # ASSUMPTION (measured invariant, levels 1-8, incl. the level-8
        # rejection of an unfilled slot): every slot gets filled and every
        # button is used exactly once, so holes and buttons biject. A hidden
        # level violating this makes the solver abstain rather than guess.
        if len(parse.buttons) != len(holes):
            return []
        assignment = _solve(parse, holes)
        if assignment is None:
            return []
        if not holes:
            return [Step(action=5)]  # board already complete and correct
        return _emit(parse, assignment)


# ------------------------------------------------------------------ solver


_MAX_NODES = 200_000


def _solve(
    parse: BuilderParse, holes: list[tuple[int, int]]
) -> Optional[dict[tuple[int, int], tuple[str, int]]]:
    """Assign button kinds to holes so the legend equals flatten(root).

    Lazy left-to-right expansion of the root box against the legend. A
    reference re-enters its box (level 5: the same box expands twice); a
    reference to a box already OPEN on the expansion stack makes the
    expansion infinite, and the legend is then required to be a prefix of
    it (level 8 displays two full periods of the cycle). Finite expansions
    must consume the legend exactly.
    """

    legend = parse.legend
    boxes = parse.boxes
    remaining: dict[tuple[str, int], int] = {}
    for button in parse.buttons:
        key = (button.kind, button.colour)
        remaining[key] = remaining.get(key, 0) + 1
    assign: dict[tuple[int, int], tuple[str, int]] = {}
    budget = [_MAX_NODES]
    max_depth = len(legend) + len(boxes) + 3
    # Note: len(buttons) == len(holes) is pre-checked by next_actions, and
    # each fresh assignment consumes one of each, so any accepted state
    # leaves exactly as many leftover buttons as unassigned holes.

    def search(frames: tuple[tuple[int, int], ...], pos: int) -> bool:
        budget[0] -= 1
        if budget[0] <= 0 or len(frames) > max_depth:
            return False
        if not frames:
            return pos == len(legend)
        box_colour, idx = frames[-1]
        box = boxes[box_colour]
        if idx == len(box.elements):
            return search(frames[:-1], pos)
        if pos == len(legend):
            # Expansion still pending. Accept only a cyclic expansion (a
            # box open twice on the stack: the legend is then a displayed
            # prefix of the infinite flatten, measured on level 8).
            opened = [f[0] for f in frames]
            return len(opened) != len(set(opened))
        element = box.elements[idx]
        rest = frames[:-1] + ((box_colour, idx + 1),)
        hole_key = (box_colour, idx)
        if element.kind == "hole":
            if hole_key in assign:
                options = [(assign[hole_key], False)]
            else:
                options = [
                    (key, True) for key, n in remaining.items() if n > 0
                ]
        else:
            options = [((element.kind, element.colour), False)]
        for (kind, colour), fresh in options:
            if fresh:
                assign[hole_key] = (kind, colour)
                remaining[(kind, colour)] -= 1
            ok = False
            if kind == "lit":
                if legend[pos] == colour:
                    ok = search(rest, pos + 1)
            elif colour in boxes:
                ok = search(rest + ((colour, 0),), pos)
            if ok:
                return True
            if fresh:
                del assign[hole_key]
                remaining[(kind, colour)] += 1
        return False

    if not search(((parse.root_colour, 0),), 0):
        return None
    # Holes never reached by the expansion (possible only past a cycle-cut
    # display) take the leftover buttons in deterministic order; their
    # content cannot change the matched prefix.
    leftover = sorted(
        key for key, n in remaining.items() for _ in range(n)
    )
    for hole in holes:
        if hole not in assign:
            assign[hole] = leftover.pop(0)
    return assign


def _emit(
    parse: BuilderParse,
    assignment: dict[tuple[int, int], tuple[str, int]],
) -> list[Step]:
    """Button-then-slot click pairs, then submit.

    If a button is already selected (colour-0 ring, measured level 1 run1),
    its pair goes first and omits the button click: re-clicking a selected
    button and switching selections are both unmeasured, so the plan uses
    only measured transitions (select -> place).
    """

    pools: dict[tuple[str, int], list[_Button]] = {}
    for button in parse.buttons:
        pools.setdefault((button.kind, button.colour), []).append(button)
    for pool in pools.values():
        pool.sort(key=lambda b: (not b.selected, b.click_col))
    selected_kinds = {
        (b.kind, b.colour) for b in parse.buttons if b.selected
    }
    pairs = list(assignment.items())  # insertion order = expansion order
    if selected_kinds:
        # One selection at most can exist; float one matching pair first.
        for i, (_, key) in enumerate(pairs):
            if key in selected_kinds:
                pairs.insert(0, pairs.pop(i))
                break
    steps: list[Step] = []
    first = True
    for (box_colour, idx), key in pairs:
        button = pools[key].pop(0)
        element = parse.boxes[box_colour].elements[idx]
        if not (first and button.selected):
            steps.append(Step(action=6, x=button.click_col, y=button.click_row))
        steps.append(Step(action=6, x=element.click_col, y=element.click_row))
        first = False
    steps.append(Step(action=5))
    return steps
