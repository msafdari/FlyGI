"""sc25's door archetype: punch the displayed 6-pattern with line-of-sight.

Every mechanic encoded here is MEASURED in the sc25 door dossier
(docs/fap_extension_20260928/sc25_door/NOTES.md, runs 0-17, levels 3-4
verified end to end) unless a comment says otherwise:

  * The pip board is a colour-3 framed 3x3 lattice of 3x3-pixel cells whose
    values are 0 (pre-marked), 2 (blank) or 14/e (punched); clicking a cell
    toggles punched/unpunched, and acceptance fires the instant the punched
    set EQUALS a displayed pattern, consuming it (cells -> 2).
  * A pattern display is a colour-3 framed 10x10 box whose 8x8 interior is
    a 3x3 lattice of 2x2 cells on a 3-pixel pitch; the mark colour names
    the device: colour 6 = door pattern, colour 15/f = shrink pattern.
  * The d-coloured (13) door dissolves at the moment the 6-pattern is
    completed, and only if the die's LAST SUCCESSFUL ROLL points it along a
    clear track ray at the level's key box (a 2x2 colour-d block ringed by
    colour 6). Post-acceptance rolls do NOT open it; the check fires on the
    completing click only.
  * The die is a filled 2x2 or 4x4 square, half colour 9 / half colour 10,
    rolling by its own size per action on colour-2 track (blocked
    otherwise). Completing the f-pattern shrinks it 4x4 -> 2x2, die
    anywhere, no arming needed.

This module is ENGINEERED SCAFFOLD, recorded as such per the repository
first principle: no fly neuron computes anything here. Its comparison
evidence is the executor-driven offline run against the dossier's verified
hand programs (L3_program.json, L4_program.json).

Planner: derive everything from the current grid. If the punched set has
strayed outside the target pattern, un-punch the strays. If an f-display is
present and the die is still 4x4, punch the shrink pattern first
(ASSUMPTION, labelled below). Otherwise BFS the die over the track lattice
(stride = die size) to the cheapest position from which one more roll both
succeeds and leaves the die with line-of-sight to a key box, then emit:
navigation rolls, all-but-one of the unpunched 6-pattern clicks, the arming
roll, the completing click. Once the door is open the board carries no
colour-d structure, match() abstains, and the seated PipPunchRollArchetype's
marker-to-dock roller finishes the level (measured working on L3 and L4).

Off-archetype boards abstain: match() requires the full co-present
signature (pip board + 6-pattern display + d-door + d key box + die), which
no frame of any other public game carries (negative audit, 2026-09-28:
0 matches on 960 non-sc25 recognizer frames).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

# Grammar constants, all MEASURED in the dossier (colour census + geometry
# of every probe frame, runs 0-17). Board-instance data (absolute
# coordinates of a level's rooms) is deliberately absent.
_TRACK = 2
_FRAME = 3
_KEY_RING = 6
_DIE_DARK = 9
_DIE_LIGHT = 10
_DOOR = 13
_PUNCHED = 14
_SHRINK_MARK = 15
_DOOR_MARK = 6
_CELL = 3  # pip cell pixels (square)
_CELL_PITCH_MIN = 4  # cells are separated by at least one wall pixel
_DISPLAY_OUTER = 10  # display box outer size (1px frame + 8x8 interior)
_DISPLAY_CELL = 2
_DISPLAY_PITCH = 3
_BOARD_DIM = 3  # the pip board and displays are 3x3 lattices (measured
# on every sc25 level seen, 1-5; a differently-sized hidden
# board abstains rather than guessing an index mapping)

# action ids, measured against the verified programs (L3: action 4 = the
# RIGHT arming roll; L4: action 2 x5 = DOWN x5, action 3 = LEFT arming).
_UP, _DOWN, _LEFT, _RIGHT = 1, 2, 3, 4
_DELTAS = {_UP: (-1, 0), _DOWN: (1, 0), _LEFT: (0, -1), _RIGHT: (0, 1)}


@dataclass
class PipDoorParse:
    """Everything next_actions needs, all read off the current frame."""

    cell_origin: dict[tuple[int, int], tuple[int, int]]  # (i,j) -> top-left
    cell_value: dict[tuple[int, int], int]
    door_pattern: frozenset[tuple[int, int]]
    shrink_pattern: frozenset[tuple[int, int]] | None
    key_boxes: list[tuple[int, int]]  # top-left of each 4x4 key box
    die: tuple[int, int, int]  # top-left row, col, size (2 or 4)


def _key_boxes(grid: NDArray[np.int16]) -> list[tuple[int, int]]:
    """2x2 colour-d blocks whose full 1px ring is colour 6, as 4x4 boxes."""

    height, width = grid.shape
    is_d = grid == _DOOR
    if height < 4 or width < 4:
        return []
    two_by_two = is_d[:-1, :-1] & is_d[:-1, 1:] & is_d[1:, :-1] & is_d[1:, 1:]
    boxes: list[tuple[int, int]] = []
    for r, c in zip(*np.nonzero(two_by_two)):
        r0, c0 = int(r) - 1, int(c) - 1
        if r0 < 0 or c0 < 0 or r0 + 4 > height or c0 + 4 > width:
            continue
        box = grid[r0 : r0 + 4, c0 : c0 + 4]
        ring_ok = (
            (box[0, :] == _KEY_RING).all()
            and (box[3, :] == _KEY_RING).all()
            and (box[1:3, 0] == _KEY_RING).all()
            and (box[1:3, 3] == _KEY_RING).all()
        )
        if ring_ok:
            boxes.append((r0, c0))
    return boxes


def _door_present(
    grid: NDArray[np.int16], key_boxes: list[tuple[int, int]]
) -> bool:
    """A solid colour-d rectangle (both dims >= 2) outside every key box."""

    from scipy import ndimage

    mask = grid == _DOOR
    for r0, c0 in key_boxes:
        mask[r0 : r0 + 4, c0 : c0 + 4] = False
    if not mask.any():
        return False
    labels, _ = ndimage.label(mask)
    for slices in ndimage.find_objects(labels):
        if slices is None:
            continue
        sy, sx = slices
        h, w = sy.stop - sy.start, sx.stop - sx.start
        if h >= 2 and w >= 2 and mask[sy, sx].all():
            return True
    return False


def _find_die(grid: NDArray[np.int16]) -> tuple[int, int, int] | None:
    """The unique filled 2x2/4x4 square split half colour 9, half colour 10.

    The dock is also drawn in 9/10 but is a frame-plus-interior blob with
    unequal colour counts and a non-square bounding box (measured on levels
    1-4), so the equal-halves square test isolates the die.
    """

    from scipy import ndimage

    mask = np.isin(grid, (_DIE_DARK, _DIE_LIGHT))
    labels, _ = ndimage.label(mask)
    found: tuple[int, int, int] | None = None
    for index, slices in enumerate(ndimage.find_objects(labels), start=1):
        if slices is None:
            continue
        sy, sx = slices
        h, w = sy.stop - sy.start, sx.stop - sx.start
        if h != w or h not in (2, 4):
            continue
        window = labels[sy, sx]
        if not (window == index).all():
            continue
        block = grid[sy, sx]
        if int((block == _DIE_DARK).sum()) != h * h // 2:
            continue
        if found is not None:
            return None  # ambiguous: abstain rather than guess
        found = (sy.start, sx.start, h)
    return found


def _pip_board(
    grid: NDArray[np.int16],
) -> tuple[dict[tuple[int, int], tuple[int, int]], dict[tuple[int, int], int]] | None:
    """The colour-3 enclosed 3x3 lattice of uniform 3x3 cells in {0,2,e}."""

    from scipy import ndimage

    height, width = grid.shape
    mask = np.isin(grid, (0, _TRACK, _PUNCHED))
    labels, _ = ndimage.label(mask)
    cells: list[tuple[int, int, int]] = []
    for index, slices in enumerate(ndimage.find_objects(labels), start=1):
        if slices is None:
            continue
        sy, sx = slices
        if sy.stop - sy.start != _CELL or sx.stop - sx.start != _CELL:
            continue
        if not (labels[sy, sx] == index).all():
            continue
        block = grid[sy, sx]
        if not (block == block[0, 0]).all():
            continue
        y0, y1 = sy.start - 1, sy.stop
        x0, x1 = sx.start - 1, sx.stop
        if y0 < 0 or x0 < 0 or y1 >= height or x1 >= width:
            continue
        ring = np.concatenate(
            [
                grid[y0, x0 : x1 + 1],
                grid[y1, x0 : x1 + 1],
                grid[y0 : y1 + 1, x0],
                grid[y0 : y1 + 1, x1],
            ]
        )
        if not (ring == _FRAME).all():
            continue
        cells.append((sy.start, sx.start, int(block[0, 0])))
    if len(cells) != _BOARD_DIM * _BOARD_DIM:
        return None
    rows = sorted({r for r, _, _ in cells})
    cols = sorted({c for _, c, _ in cells})
    if len(rows) != _BOARD_DIM or len(cols) != _BOARD_DIM:
        return None
    row_gaps = {b - a for a, b in zip(rows, rows[1:])}
    col_gaps = {b - a for a, b in zip(cols, cols[1:])}
    if len(row_gaps) != 1 or len(col_gaps) != 1:
        return None
    if min(row_gaps) < _CELL_PITCH_MIN or min(col_gaps) < _CELL_PITCH_MIN:
        return None
    origin: dict[tuple[int, int], tuple[int, int]] = {}
    value: dict[tuple[int, int], int] = {}
    for r, c, v in cells:
        key = (rows.index(r), cols.index(c))
        if key in origin:
            return None
        origin[key] = (r, c)
        value[key] = v
    return origin, value


def _displays(grid: NDArray[np.int16]) -> dict[int, frozenset[tuple[int, int]]]:
    """Pattern displays: mark colour -> set of marked (i,j) display cells.

    A display is a 36-pixel colour-3 component forming exactly the 1px ring
    of a 10x10 box whose interior is a 3x3 lattice of uniform 2x2 cells on
    a 3-pixel pitch, gaps colour 2.
    """

    from scipy import ndimage

    patterns: dict[int, set[tuple[int, int]]] = {}
    labels, _ = ndimage.label(grid == _FRAME)
    for index, slices in enumerate(ndimage.find_objects(labels), start=1):
        if slices is None:
            continue
        sy, sx = slices
        if (
            sy.stop - sy.start != _DISPLAY_OUTER
            or sx.stop - sx.start != _DISPLAY_OUTER
        ):
            continue
        window = labels[sy, sx] == index
        if int(window.sum()) != 4 * (_DISPLAY_OUTER - 1):
            continue
        if not (
            window[0, :].all()
            and window[-1, :].all()
            and window[:, 0].all()
            and window[:, -1].all()
        ):
            continue
        interior = grid[sy.start + 1 : sy.stop - 1, sx.start + 1 : sx.stop - 1]
        ok = True
        marks: dict[int, set[tuple[int, int]]] = {}
        for i in range(_BOARD_DIM):
            for j in range(_BOARD_DIM):
                cell = interior[
                    i * _DISPLAY_PITCH : i * _DISPLAY_PITCH + _DISPLAY_CELL,
                    j * _DISPLAY_PITCH : j * _DISPLAY_PITCH + _DISPLAY_CELL,
                ]
                if not (cell == cell[0, 0]).all():
                    ok = False
                    break
                colour = int(cell[0, 0])
                if colour != _TRACK:
                    marks.setdefault(colour, set()).add((i, j))
            if not ok:
                break
        if not ok:
            continue
        gaps = np.concatenate(
            [interior[2::3, :].ravel(), interior[:, 2::3].ravel()]
        )
        if not (gaps == _TRACK).all():
            continue
        for colour, cells in marks.items():
            patterns.setdefault(colour, set()).update(cells)
    return {colour: frozenset(cells) for colour, cells in patterns.items()}


class PipDoorArchetype:
    """sc25 levels with a d-door: arm the die's ray, then complete the pips."""

    name = "pip_door"

    def reset(self) -> None:
        pass  # stateless: every plan is re-derived from the current frame

    def match(self, grid: NDArray[np.int16]) -> PipDoorParse | None:
        frame = np.asarray(grid, dtype=np.int16)
        if frame.ndim != 2 or min(frame.shape) < 16:
            return None
        # Cheap census gates first: this path runs on every abstaining turn
        # of every game, so the structural parses below only ever run on
        # frames that already carry door-level pigment.
        if int((frame == _DOOR).sum()) < 8:  # key (4) + smallest door (4)
            return None
        if int((frame == _KEY_RING).sum()) < 16:  # key ring (12) + display
            return None
        if int((frame == _FRAME).sum()) < 4 * (_DISPLAY_OUTER - 1):
            return None
        if int((frame == _DIE_DARK).sum()) < 2 or int((frame == _DIE_LIGHT).sum()) < 2:
            return None
        key_boxes = _key_boxes(frame)
        if not key_boxes:
            return None
        if not _door_present(frame, key_boxes):
            return None
        die = _find_die(frame)
        if die is None:
            return None
        board = _pip_board(frame)
        if board is None:
            return None
        patterns = _displays(frame)
        door_pattern = patterns.get(_DOOR_MARK)
        if not door_pattern:
            return None
        return PipDoorParse(
            cell_origin=board[0],
            cell_value=board[1],
            door_pattern=door_pattern,
            shrink_pattern=patterns.get(_SHRINK_MARK),
            key_boxes=key_boxes,
            die=die,
        )

    # ------------------------------------------------------------- planner

    def next_actions(
        self, parse: PipDoorParse, grid: NDArray[np.int16]
    ) -> list[Step]:
        frame = np.asarray(grid, dtype=np.int16)
        punched = {
            cell for cell, value in parse.cell_value.items() if value == _PUNCHED
        }
        # ASSUMPTION: shrink whenever a shrink display exists and the die is
        # still 4x4, before any arming attempt. Measured on L4 (verified
        # program) and L5 (shrink observed, run17); on L3 no f-display
        # exists so this branch never fires there. To check: a hidden level
        # where the 4x4 die could arm directly would waste one punched
        # pattern; shrinking was never observed to hurt. If wrong, the cost
        # is actions, not correctness.
        target: frozenset[tuple[int, int]] = parse.door_pattern
        arming = True
        if parse.shrink_pattern and parse.die[2] == 4:
            target = parse.shrink_pattern
            arming = False
        stray = punched - target
        if stray:
            # Un-punch strays first (click toggles), then let the executor
            # re-parse: the punched set must EQUAL the pattern (measured
            # acceptance rule), so a stray blocks acceptance outright.
            return [self._click(parse, cell) for cell in sorted(stray)]
        remaining = sorted(target - punched)
        if not remaining:
            # Acceptance is instant on completion (measured), so a fully
            # punched pattern cannot appear in a parse; abstain on anomaly.
            return []
        clicks = [self._click(parse, cell) for cell in remaining]
        if not arming:
            return clicks  # shrink fires with the die anywhere (measured)
        plan = self._arming_plan(frame, parse)
        if plan is None:
            return []  # no line-of-sight reachable: a recorded limit, abstain
        rolls, arm_action = plan
        return (
            [Step(action=a) for a in rolls]
            + clicks[:-1]
            + [Step(action=arm_action), clicks[-1]]
        )

    def _click(self, parse: PipDoorParse, cell: tuple[int, int]) -> Step:
        r0, c0 = parse.cell_origin[cell]
        return Step(action=6, x=c0 + _CELL // 2, y=r0 + _CELL // 2)

    def _arming_plan(
        self, frame: NDArray[np.int16], parse: PipDoorParse
    ) -> tuple[list[int], int] | None:
        """Cheapest (nav rolls, arming roll) leaving the die sighted on a key.

        BFS over the die's roll lattice (stride = its size) on open track;
        the arming roll must itself be a legal move (measured: the door rule
        reads the last SUCCESSFUL roll). Line-of-sight tiers: prefer plans
        where EVERY row/column of the die's span has a clear track ray to a
        key box, then plans where at least one does. ASSUMPTION on the
        second tier: any-row line-of-sight suffices -- measured directly on
        L3 (die rows 22-25 armed through a 2-row gate corridor), consistent
        with L4; a stricter hidden rule would make tier-2 plans fail and the
        executor's cycle guards would abstain.
        """

        die_r, die_c, size = parse.die
        height, width = frame.shape
        open_px = frame == _TRACK
        open_px[die_r : die_r + size, die_c : die_c + size] = True  # vacated

        def square_open(r: int, c: int) -> bool:
            if r < 0 or c < 0 or r + size > height or c + size > width:
                return False
            return bool(open_px[r : r + size, c : c + size].all())

        key_px = np.zeros_like(open_px)
        for r0, c0 in parse.key_boxes:
            key_px[r0 : r0 + 4, c0 : c0 + 4] = True

        def los_rows_ok(r: int, c: int, action: int) -> int:
            """How many of the die's span lines reach a key box along action."""

            dr, dc = _DELTAS[action]
            count = 0
            if dr == 0:  # horizontal ray: walk each row
                for row in range(r, r + size):
                    col = c + size if dc > 0 else c - 1
                    while 0 <= col < width and open_px[row, col]:
                        col += dc
                    if 0 <= col < width and key_px[row, col]:
                        count += 1
            else:  # vertical ray: walk each column
                for col in range(c, c + size):
                    row = r + size if dr > 0 else r - 1
                    while 0 <= row < height and open_px[row, col]:
                        row += dr
                    if 0 <= row < height and key_px[row, col]:
                        count += 1
            return count

        # BFS over reachable die positions.
        start = (die_r, die_c)
        prev: dict[tuple[int, int], tuple[tuple[int, int], int] | None] = {
            start: None
        }
        dist = {start: 0}
        order = [start]
        queue = deque([start])
        while queue:
            r, c = queue.popleft()
            for action in (_UP, _DOWN, _LEFT, _RIGHT):
                dr, dc = _DELTAS[action]
                nxt = (r + dr * size, c + dc * size)
                if nxt in dist or not square_open(*nxt):
                    continue
                dist[nxt] = dist[(r, c)] + 1
                prev[nxt] = ((r, c), action)
                order.append(nxt)
                queue.append(nxt)
        best: tuple[int, int, int, tuple[int, int], int] | None = None
        for index, (r, c) in enumerate(order):
            for action in (_UP, _DOWN, _LEFT, _RIGHT):
                dr, dc = _DELTAS[action]
                landing = (r + dr * size, c + dc * size)
                if not square_open(*landing):
                    continue  # the arming roll must actually move the die
                reached = los_rows_ok(landing[0], landing[1], action)
                if reached == 0:
                    continue
                tier = 0 if reached == size else 1
                candidate = (tier, dist[(r, c)] + 1, index, (r, c), action)
                if best is None or candidate[:3] < best[:3]:
                    best = candidate
        if best is None:
            return None
        _, _, _, position, arm_action = best
        rolls: list[int] = []
        while prev[position] is not None:
            position, action = prev[position]  # type: ignore[misc]
            rolls.append(action)
        rolls.reverse()
        return rolls, arm_action
