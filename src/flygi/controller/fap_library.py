"""Fixed-action-pattern library: parse a displayed goal, emit an exact program.

REGISTERED under H-FAP-PROGRAMS (supported 2026-09-27): both template-flavour
dead games fall to short exact programs derivable from the displayed goal
(ft09 level 1 in four clicks, level 2 in seven; sc25 level 1 in ~17 actions).
H-LC-RECOGNIZER (refuted the same day) closed the fly seat for recognition,
so this module is ENGINEERED SCAFFOLD end to end, recorded as such per the
first principle -- the fly earns no credit for anything here, and the agent's
fly-load-bearing component remains the retinotopic click head.

Design contract:
  * Each archetype exposes ``match(grid) -> parse | None`` and
    ``next_actions(parse, grid) -> list[Step]``. A failed parse ABSTAINS --
    the caller falls back to the champion stack unchanged, so a library miss
    costs nothing.
  * Programs are re-derived from the CURRENT frame every time they are
    requested; the library never replays stale coordinates.
  * ASSUMPTION (labelled): the glyph-miniature rule was measured on ft09
    levels 1-2 and the pip-punch/roll rule on sc25 level 1. Later levels are
    assumed to follow the same displayed-goal grammar; the offline evaluation
    (scripts/fap_solver_eval.py) is the check, and abstention bounds the harm
    if the assumption fails.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

_TILE = 6
_SUB = 2


@dataclass(frozen=True)
class Step:
    """One emitted action; ``x``/``y`` only for clicks (action 6)."""

    action: int
    x: int | None = None
    y: int | None = None


# --------------------------------------------------------------------- ft09


@dataclass
class GlyphGridParse:
    """A lattice of 6x6 tiles plus the glyph tiles' prescriptions."""

    rows: list[int]
    cols: list[int]
    tile_colour: dict[tuple[int, int], int]
    glyphs: dict[tuple[int, int], NDArray[np.int16]]  # 3x3 sub-block colours
    dominant: int


def _subblocks(tile: NDArray[np.int16]) -> NDArray[np.int16] | None:
    """Decompose a 6x6 tile into 3x3 uniform 2x2 sub-blocks, else None."""

    blocks = np.zeros((3, 3), dtype=np.int16)
    for r in range(3):
        for c in range(3):
            sub = tile[r * _SUB : (r + 1) * _SUB, c * _SUB : (c + 1) * _SUB]
            if not (sub == sub[0, 0]).all():
                return None
            blocks[r, c] = sub[0, 0]
    return blocks


def _find_tile_lattice(
    grid: NDArray[np.int16], background: int
) -> list[GlyphGridParse]:
    """Find groups of 6x6 sub-block tiles on a shared 8-pixel pitch."""

    height, width = grid.shape
    if height < _TILE or width < _TILE:
        return []
    # Vectorized candidate scan (the 2026-09-27 review measured the Python
    # window loop at 17-65 ms per abstaining turn, a Kaggle wall-clock leak):
    # uniform[r, c] marks a uniform 2x2 block; a 6x6 window is a tile
    # candidate iff its nine 2x2 sub-blocks are all uniform and none carries
    # the background colour.
    uniform = (
        (grid[:-1, :-1] == grid[:-1, 1:])
        & (grid[:-1, :-1] == grid[1:, :-1])
        & (grid[:-1, :-1] == grid[1:, 1:])
    )
    rows_span = height - _TILE + 1
    cols_span = width - _TILE + 1
    valid = np.ones((rows_span, cols_span), dtype=bool)
    has_background = np.zeros((rows_span, cols_span), dtype=bool)
    for i in range(0, _TILE, _SUB):
        for j in range(0, _TILE, _SUB):
            valid &= uniform[i : i + rows_span, j : j + cols_span]
            has_background |= (
                grid[i : i + rows_span, j : j + cols_span] == background
            )
    tiles: dict[tuple[int, int], NDArray[np.int16]] = {}
    for r, c in zip(*np.nonzero(valid & ~has_background)):
        r, c = int(r), int(c)
        window = grid[r : r + _TILE, c : c + _TILE]
        blocks = _subblocks(window)
        assert blocks is not None  # guaranteed by the vectorized scan
        # A true tile is set off by a separator: the 1-pixel ring around
        # it (clipped at the frame edge) must be one uniform colour that
        # the tile itself does not use. This rejects impostor windows
        # straddling a tile and its border.
        ring = np.concatenate(
            [
                grid[max(r - 1, 0), max(c - 1, 0) : min(c + _TILE + 1, width)],
                grid[
                    min(r + _TILE, height - 1),
                    max(c - 1, 0) : min(c + _TILE + 1, width),
                ],
                grid[max(r - 1, 0) : min(r + _TILE + 1, height), max(c - 1, 0)],
                grid[
                    max(r - 1, 0) : min(r + _TILE + 1, height),
                    min(c + _TILE, width - 1),
                ],
            ]
        )
        if not (ring == ring[0]).all() or ring[0] in blocks:
            continue
        tiles[(r, c)] = blocks
    # Keep lattice-aligned representatives: prefer positions whose neighbours
    # at +-8 pixels are also tiles, then greedily drop overlaps.
    def support(position: tuple[int, int]) -> int:
        r, c = position
        return sum(
            (r + dr, c + dc) in tiles
            for dr, dc in ((0, 8), (0, -8), (8, 0), (-8, 0))
        )

    kept: dict[tuple[int, int], NDArray[np.int16]] = {}
    for position in sorted(tiles, key=lambda p: (-support(p), p)):
        r, c = position
        if any(abs(r - kr) < _TILE and abs(c - kc) < _TILE for kr, kc in kept):
            continue
        kept[position] = tiles[position]

    # Cluster into connected lattices via 8-pitch adjacency.
    parses: list[GlyphGridParse] = []
    unvisited = set(kept)
    while unvisited:
        seed = unvisited.pop()
        cluster = {seed}
        frontier = [seed]
        while frontier:
            r, c = frontier.pop()
            for dr, dc in ((0, 8), (0, -8), (8, 0), (-8, 0)):
                neighbour = (r + dr, c + dc)
                if neighbour in unvisited:
                    unvisited.remove(neighbour)
                    cluster.add(neighbour)
                    frontier.append(neighbour)
        if len(cluster) < 4:
            continue
        rows = sorted({r for r, _ in cluster})
        cols = sorted({c for _, c in cluster})
        tile_colour: dict[tuple[int, int], int] = {}
        glyphs: dict[tuple[int, int], NDArray[np.int16]] = {}
        colour_census: dict[int, int] = {}
        for i, r in enumerate(rows):
            for j, c in enumerate(cols):
                blocks = kept.get((r, c))
                if blocks is None:
                    continue
                if (blocks == blocks[0, 0]).all():
                    colour = int(blocks[0, 0])
                    tile_colour[(i, j)] = colour
                    colour_census[colour] = colour_census.get(colour, 0) + 1
                else:
                    glyphs[(i, j)] = blocks
        if not tile_colour:
            continue
        dominant = max(colour_census, key=lambda k: colour_census[k])
        parses.append(
            GlyphGridParse(
                rows=rows,
                cols=cols,
                tile_colour=tile_colour,
                glyphs=glyphs,
                dominant=dominant,
            )
        )
    return parses


class GlyphMiniatureArchetype:
    """ft09's measured rule: a glyph is a miniature of its 3x3 neighbourhood.

    The lattice's plain tiles use a two-colour palette. Each glyph's centre
    sub-block carries its MARKED colour; sub-block 0 prescribes the marked
    colour for that neighbourhood tile, and any other sub-block value
    prescribes the OTHER palette colour. (Levels 1-2 were solved with the
    0-side alone because "other" coincided with the dominant colour there;
    level 3 is where the 2-side becomes load-bearing -- measured violation
    at a 2-prescribed tile sitting at the marked colour.) Clicking a tile
    toggles it between the palette colours; the program is every tile whose
    current colour mismatches its prescription.
    """

    name = "glyph_miniature"

    def match(self, grid: NDArray[np.int16]) -> list[GlyphGridParse] | None:
        background = int(np.bincount(grid.ravel(), minlength=16).argmax())
        parses = [p for p in _find_tile_lattice(grid, background) if p.glyphs]
        return parses or None

    def next_actions(
        self, parses: list[GlyphGridParse], grid: NDArray[np.int16]
    ) -> list[Step]:
        steps: list[Step] = []
        seen: set[tuple[int, int]] = set()
        for parse in parses:
            census: dict[int, int] = {}
            for colour in parse.tile_colour.values():
                census[colour] = census.get(colour, 0) + 1
            for blocks in parse.glyphs.values():
                census.setdefault(int(blocks[1, 1]), 0)
            palette = sorted(census, key=lambda k: -census[k])[:2]
            for (gi, gj), blocks in parse.glyphs.items():
                marked_colour = int(blocks[1, 1])
                other = next(
                    (c for c in palette if c != marked_colour), parse.dominant
                )
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        prescription = int(blocks[1 + dr, 1 + dc])
                        ti, tj = gi + dr, gj + dc
                        current = parse.tile_colour.get((ti, tj))
                        if current is None:
                            continue
                        target = marked_colour if prescription == 0 else other
                        if current != target and (ti, tj) not in seen:
                            seen.add((ti, tj))
                            row = parse.rows[ti] + _TILE // 2
                            col = parse.cols[tj] + _TILE // 2
                            steps.append(Step(action=6, x=col, y=row))
        return steps


# --------------------------------------------------------------------- sc25


@dataclass
class PipBoardParse:
    cell_centres: dict[tuple[int, int], tuple[int, int]]  # (i,j) -> (row, col)
    zero_cells: list[tuple[int, int]]


class PipPunchRollArchetype:
    """sc25's measured rule: punch the 0-marked pips, then roll home.

    Per-game state: the last roll direction chosen while the marker and dock
    were still separable. Measured on level 2: at arrival the marker merges
    with the dock into one component, and one more roll in the same
    direction completes the level -- so a failed detection repeats the last
    known-good direction instead of guessing.
    """

    name = "pip_punch_roll"

    def __init__(self) -> None:
        self._last_roll: Step | None = None

    def match(self, grid: NDArray[np.int16]) -> PipBoardParse | None:
        # The board: colour-3 bordered box holding 3x3 cells of 3x3 pixels
        # whose values are 0 (pip to punch) or 2 (leave alone), separated by
        # colour-3 walls. Located structurally: 0-or-2 cells fully enclosed
        # by colour 3.
        from scipy import ndimage

        board = np.isin(grid, (0, 2))
        labels, count = ndimage.label(board)
        cells: list[tuple[int, int, int]] = []  # (row, col, value)
        # find_objects keeps the per-component cost bounded on busy frames
        # (the full-grid labels==index scan was O(count x 4096)).
        for index, slices in enumerate(ndimage.find_objects(labels), start=1):
            if slices is None:
                continue
            sy, sx = slices
            if sy.stop - sy.start != 3 or sx.stop - sx.start != 3:
                continue
            if int((labels[sy, sx] == index).sum()) != 9:
                continue
            ys = np.array([sy.start, sy.stop - 1])
            xs = np.array([sx.start, sx.stop - 1])
            # Enclosed by colour 3 on all sides (board wall), not background.
            y0, y1, x0, x1 = ys.min() - 1, ys.max() + 1, xs.min() - 1, xs.max() + 1
            if y0 < 0 or x0 < 0 or y1 >= grid.shape[0] or x1 >= grid.shape[1]:
                continue
            ring = np.concatenate(
                [
                    grid[y0, x0 : x1 + 1],
                    grid[y1, x0 : x1 + 1],
                    grid[y0 : y1 + 1, x0],
                    grid[y0 : y1 + 1, x1],
                ]
            )
            if not (ring == 3).all():
                continue
            value = int(grid[ys[0], xs[0]])
            cells.append((int(ys.min()) + 1, int(xs.min()) + 1, value))
        if len(cells) < 4:
            return None
        rows = sorted({r for r, _, _ in cells})
        cols = sorted({c for _, c, _ in cells})
        centres: dict[tuple[int, int], tuple[int, int]] = {}
        zeros: list[tuple[int, int]] = []
        for r, c, value in cells:
            key = (rows.index(r), cols.index(c))
            centres[key] = (r, c)
            if value == 0:
                zeros.append(key)
        return PipBoardParse(cell_centres=centres, zero_cells=zeros)

    def _roll_direction(self, grid: NDArray[np.int16]) -> list[Step]:
        """Roll the 9/a marker toward the 9/a dock (measured on levels 1-2:
        the track is colour 2, the dock sits on background, and the four
        directional actions roll up/down/left/right)."""

        from scipy import ndimage

        marker_dock = np.isin(grid, (9, 10))
        labels, count = ndimage.label(marker_dock)
        marker = dock = None
        height, width = grid.shape
        for index in range(1, count + 1):
            ys, xs = np.nonzero(labels == index)
            if ys.size < 4 or ys.size > 40:
                continue
            y0, y1 = max(ys.min() - 1, 0), min(ys.max() + 1, height - 1)
            x0, x1 = max(xs.min() - 1, 0), min(xs.max() + 1, width - 1)
            ring = np.concatenate(
                [
                    grid[y0, x0 : x1 + 1],
                    grid[y1, x0 : x1 + 1],
                    grid[y0 : y1 + 1, x0],
                    grid[y0 : y1 + 1, x1],
                ]
            )
            centre = (float(ys.mean()), float(xs.mean()))
            on_track = float((ring == 2).mean())
            if on_track >= 0.5:
                marker = centre
            elif (ring == 5).mean() >= 0.5 or (ring == grid[0, 0]).mean() >= 0.5:
                dock = centre
        if marker is None or dock is None:
            if self._last_roll is not None:
                return [self._last_roll]
            return [Step(action=3)]  # level-1 fallback, measured to work there
        dy, dx = dock[0] - marker[0], dock[1] - marker[1]
        vertical = Step(action=1) if dy < 0 else Step(action=2)
        horizontal = Step(action=3) if dx < 0 else Step(action=4)
        # Dominant axis first; the secondary queues behind it so a walled
        # dominant roll (frame unchanged, executor re-parses) still makes
        # progress on the next proposal.
        if abs(dy) >= abs(dx):
            self._last_roll = vertical
            return [vertical, horizontal] if abs(dx) > 1 else [vertical]
        self._last_roll = horizontal
        return [horizontal, vertical] if abs(dy) > 1 else [horizontal]

    def next_actions(self, parse: PipBoardParse, grid: NDArray[np.int16]) -> list[Step]:
        if parse.zero_cells:
            return [
                Step(action=6, x=parse.cell_centres[cell][1], y=parse.cell_centres[cell][0])
                for cell in parse.zero_cells
            ]
        # No pips left: roll the marker toward the dock. The executor repeats
        # this while the frame keeps changing and re-parses when it stops.
        return self._roll_direction(grid)


# ----------------------------------------------------------------- executor


_MATCH_BACKOFF_AFTER = 32
_MATCH_BACKOFF_STRIDE = 4


@dataclass
class FapExecutor:
    """Per-game program executor: parse, emit, verify, re-derive.

    ``propose`` returns the next Step or None (abstain). The host reports
    frames back through ``observe``, tells the executor when it REJECTED a
    proposed step (``reject_last``: hard-banned or illegal, so the step never
    ran), and notifies life/level boundaries (``notify_reset``,
    ``notify_level_advance``) so no program state survives a board it was
    parsed from. All of this hardening follows the 2026-09-27 adversarial
    seating review: stale queues replayed pre-death coordinates, the revisit
    guard counted abstentions and was never cleared (permanently muting the
    4th life), the swallow retry armed once per game instead of once per
    life, and a rejected step desynced the program pointer.
    """

    archetypes: list[Any] = field(
        default_factory=lambda: [GlyphMiniatureArchetype(), PipPunchRollArchetype()]
    )
    _queue: list[Step] = field(default_factory=list)
    _matched: str | None = None
    _last_emitted: Step | None = None
    _last_grid_bytes: bytes | None = None
    _retried_swallow: bool = False
    _stall_count: int = 0
    _frame_emissions: dict[bytes, int] = field(default_factory=dict)
    _match_failures: int = 0
    _turn_index: int = 0

    def _clear_program_state(self) -> None:
        self._queue.clear()
        self._last_emitted = None
        self._last_grid_bytes = None
        self._retried_swallow = False
        self._stall_count = 0
        self._frame_emissions.clear()

    def notify_reset(self) -> None:
        """A RESET ran (forced or otherwise): the board the program was
        parsed from is gone, and the engine's post-reset swallow (measured,
        per reset) gets a fresh retry budget."""

        self._clear_program_state()

    def notify_level_advance(self) -> None:
        """The level fell: everything parsed from the previous board is
        stale, including the roll-direction memory's frame guards."""

        self._clear_program_state()

    def reject_last(self) -> None:
        """The host refused the last proposed step (illegal or hard-banned),
        so it never executed: it must not arm the swallow retry, and the
        emission it recorded on this frame is rolled back."""

        if self._last_emitted is not None and self._last_grid_bytes is not None:
            count = self._frame_emissions.get(self._last_grid_bytes, 0)
            if count > 0:
                self._frame_emissions[self._last_grid_bytes] = count - 1
        self._last_emitted = None

    def observe(self, grid: NDArray[np.integer]) -> None:
        key = np.asarray(grid, dtype=np.int16).tobytes()
        if key != self._last_grid_bytes:
            self._stall_count = 0
        elif self._last_emitted is not None:
            self._stall_count += 1
            if not self._retried_swallow:
                # Measured engine quirk: the first action after a reset is
                # swallowed in some games; retry exactly once per life
                # (notify_reset re-arms this).
                self._queue.insert(0, self._last_emitted)
                self._retried_swallow = True
            elif self._stall_count % 3 == 0:
                self._queue.clear()  # stuck: force a re-parse
        self._last_grid_bytes = key
        self._last_emitted = None

    def propose(self, grid: NDArray[np.integer]) -> Step | None:
        self._turn_index += 1
        if self._stall_count >= 8:
            # Measured on ft09 level 5: a level beyond the parsed rule loops
            # the solver until the timer kills the life. Abstain while stuck;
            # observe() resets the counter as soon as the frame changes, so
            # the solver resumes when the host policy moves the game.
            return None
        frame = np.asarray(grid, dtype=np.int16)
        key = frame.tobytes()
        if self._frame_emissions.get(key, 0) >= 4:
            # The other measured failure mode: a mis-prescribed rule TOGGLES
            # tiles, so frames keep changing while the same states recur.
            # Four EMISSIONS on one frame within a life/level means the
            # solver is cycling; abstain here and let the host break it.
            return None
        if not self._queue:
            if (
                self._matched is None
                and self._match_failures >= _MATCH_BACKOFF_AFTER
                and self._turn_index % _MATCH_BACKOFF_STRIDE != 0
            ):
                # A game that has never matched pays the parse only every
                # few turns after a grace period; a later level that starts
                # matching is still caught within the stride.
                return None
            for archetype in self.archetypes:
                parse = archetype.match(frame)
                if parse is not None:
                    steps = archetype.next_actions(parse, frame)
                    if steps:
                        self._queue = list(steps)
                        self._matched = archetype.name
                        self._match_failures = 0
                        break
            else:
                if self._matched is None:
                    self._match_failures += 1
        if not self._queue:
            return None
        step = self._queue.pop(0)
        self._last_emitted = step
        self._last_grid_bytes = key
        if len(self._frame_emissions) > 512:
            self._frame_emissions.clear()
        self._frame_emissions[key] = self._frame_emissions.get(key, 0) + 1
        return step

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "fap_library",
            "matched": self._matched,
            "queued": len(self._queue),
            "fly_content": "none; engineered scaffold (H-LC-RECOGNIZER refuted)",
        }
