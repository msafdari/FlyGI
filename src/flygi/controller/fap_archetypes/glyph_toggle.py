"""ft09 levels 5-6 archetype: two-sided glyph rule with flip-mask toggles.

ENGINEERED SCAFFOLD, recorded as such per the repository first principle --
no fly neuron computes anything here. Grammar and rule are MEASURED
(2026-09-28 investigation, docs/fap_extension_20260928/ft09_L5/NOTES.md;
verified programs in programs.json, final state GameState.WIN 6/6):

  * The board is an 8-pixel-pitch lattice of 6x6 tiles made of nine uniform
    2x2 sub-cells, set off by a uniform separator ring.
  * Non-uniform tiles are either GLYPHS (centre sub-cell = a palette colour,
    the other eight sub-cells drawn in ink colours {0,2,3}) or BOARD TILES
    carrying a FLIP MASK (colour-6 sub-cells at edge-centre positions only;
    the tile's displayed phase is its non-6 colour).
  * Palette: two stacked 4x4 uniform blocks at an off-lattice position
    surrounded by background (measured top-right on L5/L6; ASSUMPTION: the
    detection here is position-agnostic because only two instances were
    measured). Fallback when no indicator is present: the two colours seen
    across tile phases and glyph centres (dossier sketch item 3).
  * Rule (measured): glyph 0-cells prescribe the glyph's centre colour and
    2-cells the other palette colour at the corresponding tile of the
    glyph's 3x3 neighbourhood; 3-cells mark non-prescribable positions
    (off-lattice, absent, or another glyph) -- verified 100% consistent
    across all 12 glyphs of L5+L6. Clicking a board tile toggles its own
    palette phase plus the phase of each mask-directed orthogonal neighbour
    that is a present board tile (flips aimed at glyphs or absences are
    dropped). The win fires on the click that satisfies every prescription;
    unprescribed tiles are free.
  * Toggles commute (XOR), so the planner solves A x = needed over GF(2)
    with one variable per board tile and one row per prescribed tile.
    INFERRED (stated in the dossier): click order within a solution is
    irrelevant to the final state; the emitted order still puts masked
    tiles first, mirroring the executed, verified order.

Coexistence contract: the built-in GlyphMiniatureArchetype handles ft09
levels 1-4 (plain glyph boards) and MIS-parses 6-masked tiles as glyphs, so
this archetype claims exactly the boards that carry flip-mask tiles or the
stacked palette indicator, and abstains on plain glyph boards. To claim
those boards it must be seated BEFORE GlyphMiniatureArchetype: the executor
takes the first archetype whose match+plan succeeds, and GlyphMiniature
matches (and mis-plans) L5-style boards, as measured in the dossier.

Everything is derived from the CURRENT grid. Grammar constants above are
dossier-measured; no board-instance data (absolute coordinates, level
layouts, action scripts) appears here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

_TILE = 6
_SUB = 2
_PITCH = 8
_MASK = 6
_GLYPH_INK = (0, 2, 3)
_IND = 4  # indicator block edge length in pixels

# Sub-cell position in a tile's 3x3 block layout -> neighbour tile delta
# (measured: (0,1)=N, (1,0)=W, (1,2)=E, (2,1)=S; discriminated on L6 by the
# click at lattice (2,3) flipping (2,3)+(1,3), not (3,3)).
_EDGE_DIRS: dict[tuple[int, int], tuple[int, int]] = {
    (0, 1): (-1, 0),
    (1, 0): (0, -1),
    (1, 2): (0, 1),
    (2, 1): (1, 0),
}


@dataclass
class GlyphToggleParse:
    """One validated lattice: board tiles, glyphs, palette, prescriptions."""

    rows: list[int]  # pixel row of each lattice row
    cols: list[int]  # pixel col of each lattice col
    # (i, j) -> (phase colour, mask directions as tile-index deltas)
    tiles: dict[tuple[int, int], tuple[int, tuple[tuple[int, int], ...]]]
    glyphs: dict[tuple[int, int], NDArray[np.int16]]
    palette: frozenset[int]
    targets: dict[tuple[int, int], int]  # prescribed tile -> required phase


def _find_block_lattices(
    grid: NDArray[np.int16], background: int
) -> list[dict[tuple[int, int], NDArray[np.int16]]]:
    """Clusters of 6x6 sub-block tiles on the 8-pixel pitch.

    Same lattice grammar as fap_library._find_tile_lattice (vectorized
    candidate scan, separator-ring test, support dedupe, pitch clustering),
    re-implemented here because that helper drops clusters containing no
    uniform tile -- and on L6 every board tile carries a mask, so none is
    uniform. Returns raw 3x3 sub-block arrays; classification happens later.
    """

    height, width = grid.shape
    if height < _TILE or width < _TILE:
        return []
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
        blocks = window[::_SUB, ::_SUB].astype(np.int16)
        # Separator test: every existing 1-pixel ring cell around the tile
        # is one uniform colour the tile itself does not use.
        ring_cells: list[int] = []
        if r > 0:
            ring_cells.extend(
                grid[r - 1, max(c - 1, 0) : min(c + _TILE + 1, width)].tolist()
            )
        if r + _TILE < height:
            ring_cells.extend(
                grid[r + _TILE, max(c - 1, 0) : min(c + _TILE + 1, width)].tolist()
            )
        if c > 0:
            ring_cells.extend(
                grid[max(r - 1, 0) : min(r + _TILE + 1, height), c - 1].tolist()
            )
        if c + _TILE < width:
            ring_cells.extend(
                grid[max(r - 1, 0) : min(r + _TILE + 1, height), c + _TILE].tolist()
            )
        if not ring_cells:
            continue
        first = ring_cells[0]
        if any(v != first for v in ring_cells) or first in blocks:
            continue
        tiles[(r, c)] = blocks

    def support(position: tuple[int, int]) -> int:
        r, c = position
        return sum(
            (r + dr, c + dc) in tiles
            for dr, dc in ((0, _PITCH), (0, -_PITCH), (_PITCH, 0), (-_PITCH, 0))
        )

    kept: dict[tuple[int, int], NDArray[np.int16]] = {}
    for position in sorted(tiles, key=lambda p: (-support(p), p)):
        r, c = position
        if any(abs(r - kr) < _TILE and abs(c - kc) < _TILE for kr, kc in kept):
            continue
        kept[position] = tiles[position]

    clusters: list[dict[tuple[int, int], NDArray[np.int16]]] = []
    unvisited = set(kept)
    while unvisited:
        seed = unvisited.pop()
        cluster = {seed}
        frontier = [seed]
        while frontier:
            r, c = frontier.pop()
            for dr, dc in ((0, _PITCH), (0, -_PITCH), (_PITCH, 0), (-_PITCH, 0)):
                neighbour = (r + dr, c + dc)
                if neighbour in unvisited:
                    unvisited.remove(neighbour)
                    cluster.add(neighbour)
                    frontier.append(neighbour)
        if len(cluster) < 4:
            continue
        clusters.append({pos: kept[pos] for pos in cluster})
    return clusters


def _find_indicator(
    grid: NDArray[np.int16], background: int
) -> list[tuple[int, int]]:
    """Stacked 4x4 palette-indicator candidates: two uniform 4x4 blocks of
    distinct non-background colours, one atop the other, every existing
    1-pixel ring cell around the 8x4 stack being background."""

    height, width = grid.shape
    if height < 2 * _IND or width < _IND:
        return []
    span_r = height - _IND + 1
    span_c = width - _IND + 1
    uni = np.ones((span_r, span_c), dtype=bool)
    base = grid[:span_r, :span_c]
    for di in range(_IND):
        for dj in range(_IND):
            uni &= grid[di : di + span_r, dj : dj + span_c] == base
    stack_r = height - 2 * _IND + 1
    top = grid[:stack_r, :span_c]
    bottom = grid[_IND : _IND + stack_r, :span_c]
    ok = (
        uni[:stack_r]
        & uni[_IND : _IND + stack_r]
        & (top != bottom)
        & (top != background)
        & (bottom != background)
    )
    found: list[tuple[int, int]] = []
    for r, c in zip(*np.nonzero(ok)):
        r, c = int(r), int(c)
        ring: list[int] = []
        if r > 0:
            ring.extend(grid[r - 1, max(c - 1, 0) : min(c + _IND + 1, width)])
        if r + 2 * _IND < height:
            ring.extend(
                grid[r + 2 * _IND, max(c - 1, 0) : min(c + _IND + 1, width)]
            )
        if c > 0:
            ring.extend(grid[max(r - 1, 0) : min(r + 2 * _IND + 1, height), c - 1])
        if c + _IND < width:
            ring.extend(
                grid[max(r - 1, 0) : min(r + 2 * _IND + 1, height), c + _IND]
            )
        if ring and all(int(v) == background for v in ring):
            found.append((int(grid[r, c]), int(grid[r + _IND, c])))
        if len(found) > 2:
            break  # already ambiguous; no need to enumerate further
    return found


def _classify_blocks(
    blocks: NDArray[np.int16],
) -> tuple[str, int, tuple[tuple[int, int], ...]] | None:
    """('tile', phase, dirs) | ('glyph', centre, ()) | None on violation."""

    mask_positions = {
        (int(r), int(c)) for r, c in zip(*np.nonzero(blocks == _MASK))
    }
    if mask_positions:
        if not mask_positions <= set(_EDGE_DIRS):
            return None  # 6s anywhere but edge-centres: not this grammar
        rest = {
            int(blocks[r, c])
            for r in range(3)
            for c in range(3)
            if (r, c) not in mask_positions
        }
        if len(rest) != 1:
            return None
        phase = rest.pop()
        dirs = tuple(sorted(_EDGE_DIRS[p] for p in mask_positions))
        return ("tile", phase, dirs)
    centre = int(blocks[1, 1])
    if centre in _GLYPH_INK or centre == _MASK:
        return None
    off_cells = {
        int(blocks[r, c]) for r in range(3) for c in range(3) if (r, c) != (1, 1)
    }
    if not off_cells <= set(_GLYPH_INK):
        return None
    return ("glyph", centre, ())


def _solve_gf2(
    matrix: NDArray[np.uint8], rhs: NDArray[np.uint8]
) -> NDArray[np.uint8] | None:
    """One solution of A x = b over GF(2) (free variables 0), else None."""

    a = (matrix.astype(np.uint8) & 1).copy()
    b = (rhs.astype(np.uint8) & 1).copy()
    m, n = a.shape
    aug = np.hstack([a, b.reshape(-1, 1)])
    pivot_row_of_col: dict[int, int] = {}
    row = 0
    for col in range(n):
        hits = np.nonzero(aug[row:, col])[0]
        if hits.size == 0:
            continue
        pivot = row + int(hits[0])
        if pivot != row:
            aug[[row, pivot]] = aug[[pivot, row]]
        for other in np.nonzero(aug[:, col])[0]:
            if int(other) != row:
                aug[int(other)] ^= aug[row]
        pivot_row_of_col[col] = row
        row += 1
        if row == m:
            break
    inconsistent = (aug[:, :n].sum(axis=1) == 0) & (aug[:, n] == 1)
    if bool(inconsistent.any()):
        return None
    solution = np.zeros(n, dtype=np.uint8)
    for col, pivot in pivot_row_of_col.items():
        solution[col] = aug[pivot, n]
    return solution


class GlyphToggleArchetype:
    """Parser + GF(2) planner for ft09's flip-mask glyph boards (L5-L6)."""

    name = "glyph_toggle"

    def reset(self) -> None:
        pass  # stateless: everything is re-derived from the current grid

    def match(self, grid: NDArray[np.int16]) -> GlyphToggleParse | None:
        frame = np.asarray(grid, dtype=np.int16)
        if frame.ndim != 2 or min(frame.shape) < 2 * _IND:
            return None
        # Cheap gates for the abstain path: glyph ink must exist, and either
        # a flip mask (colour 6) or a candidate palette indicator must be
        # claimable; plain glyph boards stay with GlyphMiniatureArchetype.
        if not np.isin(frame, _GLYPH_INK).any():
            return None
        background = int(np.bincount(frame.ravel(), minlength=16).argmax())
        clusters = _find_block_lattices(frame, background)
        # ASSUMPTION: the archetype's boards carry exactly one lattice (true
        # of both measured levels); anything else abstains rather than guess.
        if len(clusters) != 1:
            return None
        cluster = clusters[0]
        rows = sorted({r for r, _ in cluster})
        cols = sorted({c for _, c in cluster})
        tiles: dict[tuple[int, int], tuple[int, tuple[tuple[int, int], ...]]] = {}
        glyphs: dict[tuple[int, int], NDArray[np.int16]] = {}
        for (r, c), blocks in cluster.items():
            key = (rows.index(r), cols.index(c))
            if (blocks == blocks[0, 0]).all():
                tiles[key] = (int(blocks[0, 0]), ())
                continue
            classified = _classify_blocks(blocks)
            if classified is None:
                return None  # a tile outside the grammar: not our archetype
            kind, colour, dirs = classified
            if kind == "tile":
                tiles[key] = (colour, dirs)
            else:
                glyphs[key] = blocks
        if not glyphs or not tiles:
            return None
        has_mask = any(dirs for _, dirs in tiles.values())
        indicators = _find_indicator(frame, background)
        if len(indicators) > 1:
            return None  # ambiguous indicator: abstain
        if not indicators and not has_mask:
            return None  # plain glyph board: GlyphMiniature's territory
        if indicators:
            palette = frozenset(indicators[0])
        else:
            # Measured fallback (dossier sketch item 3): tile phases plus
            # glyph centres must name exactly the two palette colours.
            palette = frozenset(
                {phase for phase, _ in tiles.values()}
                | {int(blocks[1, 1]) for blocks in glyphs.values()}
            )
        if len(palette) != 2:
            return None
        if palette & (set(_GLYPH_INK) | {_MASK, background}):
            return None
        if any(phase not in palette for phase, _ in tiles.values()):
            return None
        if any(int(blocks[1, 1]) not in palette for blocks in glyphs.values()):
            return None
        # Prescriptions, with the measured 3-cell consistency as a hard
        # structural check: 0/2 must aim at present board tiles, 3 must not.
        targets: dict[tuple[int, int], int] = {}
        for (gi, gj), blocks in glyphs.items():
            marked = int(blocks[1, 1])
            other = next(iter(palette - {marked}))
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    value = int(blocks[1 + dr, 1 + dc])
                    key = (gi + dr, gj + dc)
                    is_board_tile = key in tiles
                    if value == 3:
                        if is_board_tile:
                            return None
                        continue
                    if not is_board_tile:
                        return None
                    required = marked if value == 0 else other
                    previous = targets.get(key)
                    if previous is not None and previous != required:
                        return None
                    targets[key] = required
        if not targets:
            return None
        return GlyphToggleParse(
            rows=rows,
            cols=cols,
            tiles=tiles,
            glyphs=glyphs,
            palette=palette,
            targets=targets,
        )

    def next_actions(
        self, parse: GlyphToggleParse, grid: NDArray[np.int16]
    ) -> list[Step]:
        order = sorted(parse.tiles)
        index_of = {key: i for i, key in enumerate(order)}
        prescribed = sorted(parse.targets)
        matrix = np.zeros((len(prescribed), len(order)), dtype=np.uint8)
        needed = np.zeros(len(prescribed), dtype=np.uint8)
        row_of = {key: i for i, key in enumerate(prescribed)}
        for key, (phase, dirs) in parse.tiles.items():
            column = index_of[key]
            touched = [key] + [
                (key[0] + dr, key[1] + dc)
                for dr, dc in dirs
                if (key[0] + dr, key[1] + dc) in parse.tiles
            ]  # flips aimed at glyphs or absences are dropped (measured)
            for target in touched:
                if target in row_of:
                    matrix[row_of[target], column] ^= 1
        for key in prescribed:
            phase, _ = parse.tiles[key]
            needed[row_of[key]] = 1 if phase != parse.targets[key] else 0
        solution = _solve_gf2(matrix, needed)
        if solution is None:
            return []  # measured levels are always solvable; abstain if not
        clicks = [order[i] for i in range(len(order)) if solution[i]]
        # Masked tiles first, mirroring the verified executed order (the
        # final state is order-independent; see module docstring).
        clicks.sort(key=lambda key: (not parse.tiles[key][1], key))
        return [
            Step(
                action=6,
                x=parse.cols[key[1]] + _TILE // 2,
                y=parse.rows[key[0]] + _TILE // 2,
            )
            for key in clicks
        ]
