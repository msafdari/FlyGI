"""re86's archetype: crosshair parking -- cycle geometric avatars, park each one
so that every same-colour dot lies on its outline.

Every mechanic encoded here is MEASURED, either in the re86 dossier
(docs/fap_extension_20260928/re86/NOTES.md) or re-measured live in the offline
arcade on 2026-09-28 while porting, unless a comment says ASSUMPTION.
The measured grammar:

  * Background is colour 5; row 63 is the timer: a colour-15 prefix consumed
    right to left into colour-1 cells (fresh boards are all 15).
  * Avatars are outlines: plus (two bars), X (four diagonal arms), diamond
    (a hollow |dr|+|dc| == R ring), line (one bar), rect (a wall outline).
    Actions 1/2/3/4 move the ACTIVE avatar exactly 3 px up/down/left/right;
    action 5 cycles which avatar is active (round robin).
  * The single colour-0 pixel marks the active avatar at its nominal centre
    (for a split plus: (vbar mid row, hbar mid col); for a rect: the
    round-half-up bbox centre -- both measured live). It can be HIDDEN under
    another avatar (measured on L6), so the parse tolerates its absence.
  * Dots are 3x3 boxes: a colour-4 ring around a coloured centre pixel. The
    level falls the moment every dot box overlaps a cell of an avatar whose
    colour matches the dot's (wrong-colour overlap is inert; dots are never
    consumed, so coverage must be simultaneous).
  * Palette tiles are 6x6 blocks: a colour-2 ring around a uniform 4x4
    interior. An avatar touching a tile's area with ANY cell (arm tips
    included; measured on L5) is recoloured to the tile colour instantly;
    the LAST touch wins and persists.
  * Z-order (measured live): avatars render over dots and tiles; one avatar
    can render over another and over the marker. Hidden cells re-appear when
    the coverer moves away.
  * The squeeze object (colour-1 block, L6+) is the only thing that blocks
    movement: each PART of the active avatar (a bar of a plus, the whole of
    a rigid shape) sweeps 3 px and stays iff its sweep hits an object cell,
    so a plus's two bars can displace relative to each other. A rect pressed
    against the object deforms: blocked wall stays, trailing wall advances
    +3, the perpendicular dimension grows +3 on alternating sides (h+w
    conserved); grid edges only clip and never deform.

This module is ENGINEERED SCAFFOLD, recorded as such per the repository
first principle: no fly neuron computes anything here. Its comparison
evidence is the executor-driven offline run against the dossier's verified
hand programs (6 levels, the dossier's own L1-L6 ceiling; L7 is recorded
UNSOLVED in the dossier, combines tiles with the squeeze object, and this
planner abstains there).

ASSUMPTION (labelled where encoded, summarised here):
  * Tile contact is evaluated at the 3-px landing positions; avoidance is
    computed on the full 1-px sweep, which is safe under either semantics.
  * Lines, X arms and plus arms are symmetric, so an edge-clipped arm's
    hidden length equals its visible opposite arm's.
  * Rigid non-plus, non-rect shapes never touch the squeeze object (their
    contact physics was never measured); routes forbid the contact instead.
  * Minimum structural sizes (arms >= 3, diamond R >= 4, rect side >= 4,
    line length >= 5) sit below every measured instance and reject noise.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

_BG = 5
_RING = 4
_TILE_RING = 2
_OBJECT = 1
_MARKER = 0
_TIMER_FULL = 15
_TIMER_SPENT = 1
_STEP = 3
_BODY_ROWS = 63
_COLS = 64

_MIN_ARM = 3
_MIN_RADIUS = 4
_MIN_RECT_SIDE = 4
_MIN_LINE = 5

_MAX_PLAN = 250
_BFS_NODE_CAP = 400_000
_ASSIGN_NODE_CAP = 20_000
_MAX_REQUIRED = 400

Cell = tuple[int, int]

_DIR = {1: (-1, 0), 2: (1, 0), 3: (0, -1), 4: (0, 1)}
_INV = {1: 2, 2: 1, 3: 4, 4: 3}


@dataclass(frozen=True)
class Tile:
    top: int
    left: int
    colour: int  # interior colour; the 6x6 area includes the colour-2 ring


@dataclass(frozen=True)
class Dot:
    row: int
    col: int
    colour: int | None  # None = centre hidden under an avatar right now


@dataclass
class Avatar:
    kind: str  # 'plus' | 'x' | 'diamond' | 'line_h' | 'line_v' | 'rect' | 'split_plus'
    colour: int
    params: dict[str, int]

    @property
    def centre(self) -> Cell:
        p = self.params
        if self.kind == "rect":
            # Measured: the marker sits at the round-half-up bbox centre.
            return (
                (p["top"] + p["top"] + p["h"] - 1 + 1) // 2,
                (p["left"] + p["left"] + p["w"] - 1 + 1) // 2,
            )
        if self.kind == "split_plus":
            # Measured: (vbar mid row, hbar mid col), even while separated.
            return (p["vtop"] + p["vlen"] // 2, p["hleft"] + p["hlen"] // 2)
        return (p["r"], p["c"])

    def cell_offsets(self) -> list[Cell]:
        """Ideal cell offsets from the centre (clipping applied at placement)."""

        p = self.params
        if self.kind == "plus":
            offs = [(dr, 0) for dr in range(-p["au"], p["ad"] + 1)]
            offs += [(0, dc) for dc in range(-p["al"], p["ar"] + 1) if dc != 0]
            return offs
        if self.kind == "x":
            offs = [(0, 0)]
            for d in range(1, p["arm"] + 1):
                offs += [(-d, -d), (-d, d), (d, -d), (d, d)]
            return offs
        if self.kind == "diamond":
            radius = p["radius"]
            return [
                (dr, dc)
                for dr in range(-radius, radius + 1)
                for dc in {-(radius - abs(dr)), radius - abs(dr)}
            ]
        if self.kind == "line_h":
            return [(0, dc) for dc in range(-p["half"], p["half"] + 1)]
        if self.kind == "line_v":
            return [(dr, 0) for dr in range(-p["half"], p["half"] + 1)]
        raise ValueError(self.kind)  # rect/split_plus use their own geometry

    def coverage_offsets(self) -> list[Cell]:
        """Offsets that COUNT for dot coverage. MEASURED (L2, live): an
        inactive X's centre cell renders background, and the dossier's
        verified L3 geometry (solve3.py) already excluded it (1 <= |dr|),
        so the X centre is not a covering cell."""

        if self.kind == "x":
            return [o for o in self.cell_offsets() if o != (0, 0)]
        return self.cell_offsets()

    def cells(self) -> set[Cell]:
        """Current on-board cells (clipped)."""

        p = self.params
        if self.kind == "rect":
            out: set[Cell] = set()
            r1, c1 = p["top"] + p["h"] - 1, p["left"] + p["w"] - 1
            for k in range(p["left"], c1 + 1):
                out.add((p["top"], k))
                out.add((r1, k))
            for k in range(p["top"], r1 + 1):
                out.add((k, p["left"]))
                out.add((k, c1))
        elif self.kind == "split_plus":
            out = {(p["hrow"], p["hleft"] + k) for k in range(p["hlen"])}
            out |= {(p["vtop"] + k, p["vcol"]) for k in range(p["vlen"])}
        else:
            cr, cc = self.params["r"], self.params["c"]
            out = {(cr + dr, cc + dc) for dr, dc in self.cell_offsets()}
        return {
            (r, c) for r, c in out if 0 <= r < _BODY_ROWS and 0 <= c < _COLS
        }


@dataclass
class ParkParse:
    avatars: list[Avatar]
    dots: list[Dot]
    tiles: list[Tile]
    object_cells: frozenset[Cell]
    marker: Cell | None
    timer_pixels: int


# --------------------------------------------------------------------- parse


def _timer_pixels(row: NDArray[np.int16]) -> int | None:
    """Colour-15 prefix + colour-1 suffix (measured), else None."""

    n15 = 0
    for v in row:
        if int(v) != _TIMER_FULL:
            break
        n15 += 1
    if n15 < 1:
        return None
    if not (row[n15:] == _TIMER_SPENT).all():
        return None
    return n15


def _find_tiles(body: NDArray[np.int16]) -> list[Tile]:
    """Intact palette tiles: colour-2 ring around a uniform 4x4 interior."""

    tiles: list[Tile] = []
    seen: set[Cell] = set()
    for r, c in np.argwhere(body == _TILE_RING):
        r, c = int(r), int(c)  # candidate top-left of the 6x6 area
        if (r, c) in seen:
            continue
        if r + 6 > _BODY_ROWS or c + 6 > _COLS:
            continue
        block = body[r : r + 6, c : c + 6]
        ring = np.concatenate([block[0], block[5], block[1:5, 0], block[1:5, 5]])
        if not (ring == _TILE_RING).all():
            continue
        inner = block[1:5, 1:5]
        colour = int(inner[0, 0])
        if colour in (_MARKER, _OBJECT, _TILE_RING, _RING, _BG, _TIMER_FULL):
            continue
        if not (inner == colour).all():
            continue
        tiles.append(Tile(top=r, left=c, colour=colour))
        for dr in range(6):
            for dc in range(6):
                seen.add((r + dr, c + dc))
    return tiles


def _find_dots_strict(body: NDArray[np.int16]) -> list[Dot]:
    """Uncovered dots: all eight ring cells colour 4, centre something else."""

    dots: list[Dot] = []
    for r, c in np.argwhere(body == _RING):
        r, c = int(r) + 1, int(c) + 1  # ring top-left -> candidate centre
        if not (1 <= r < _BODY_ROWS - 1 and 1 <= c < _COLS - 1):
            continue
        block = body[r - 1 : r + 2, c - 1 : c + 2]
        if int((block == _RING).sum()) != 8 or block[1, 1] == _RING:
            continue
        centre = int(block[1, 1])
        if centre in (_BG, _TILE_RING, _TIMER_FULL):
            continue
        dots.append(Dot(row=r, col=c, colour=centre))
    return dots


def _probable_dot_centres(body: NDArray[np.int16]) -> set[Cell]:
    """Cells with >= 3 colour-4 neighbours: dot centres whose ring is partly
    hidden under an avatar. Excluded from the avatar-fitting requirement."""

    fours = (body == _RING).astype(np.int8)
    padded = np.zeros((body.shape[0] + 2, body.shape[1] + 2), dtype=np.int8)
    padded[1:-1, 1:-1] = fours
    count = np.zeros_like(fours)
    for dr in (0, 1, 2):
        for dc in (0, 1, 2):
            if dr == 1 and dc == 1:
                continue
            count += padded[dr : dr + body.shape[0], dc : dc + body.shape[1]]
    return {
        (int(r), int(c))
        for r, c in np.argwhere((count >= 3) & (body != _RING) & (body != _BG))
    }


def _fit_colour_shapes(
    body: NDArray[np.int16],
    colour: int,
    required: set[Cell],
    allowed: NDArray[np.bool_],
    object_present: bool,
    marker: Cell | None,
) -> list[Avatar] | None:
    """Decompose one colour's required cells into avatar shapes.

    ``allowed`` marks cells a shape may occupy: its own colour, plus cells
    where a shape cell can be hidden (the marker, tile areas, dot boxes and
    already-fitted avatars -- z-order is measured, avatars render over tiles
    and dots and can cover each other). Returns None when some required cell
    cannot be explained by any accepted shape.
    """

    height, width = body.shape
    vmask = body == colour

    def arm_len(r: int, c: int, dr: int, dc: int) -> tuple[int, int]:
        """(extension through ``allowed``, last index that is truly colour)."""

        n = 0
        last_v = 0
        rr, cc = r + dr, c + dc
        while 0 <= rr < height and 0 <= cc < width and allowed[rr, cc]:
            n += 1
            if vmask[rr, cc]:
                last_v = n
            rr, cc = rr + dr, cc + dc
        return n, last_v

    def edge_dist(r: int, c: int, dr: int, dc: int) -> int:
        steps = 1 << 20
        if dr < 0:
            steps = min(steps, r)
        if dr > 0:
            steps = min(steps, height - 1 - r)
        if dc < 0:
            steps = min(steps, c)
        if dc > 0:
            steps = min(steps, width - 1 - c)
        return steps

    candidates: list[tuple[int, str, dict[str, int], frozenset[Cell]]] = []

    def add_candidate(
        kind: str,
        params: dict[str, int],
        cells: Iterable[Cell],
        exempt: frozenset[Cell] = frozenset(),
    ) -> None:
        """``exempt`` cells may render background: MEASURED (L2, live), an
        inactive avatar's centre cell can be a background 'hole' where the
        marker used to sit."""

        cellset = frozenset(
            p for p in cells if 0 <= p[0] < height and 0 <= p[1] < width
        )
        for r, c in cellset:
            if not allowed[r, c] and not ((r, c) in exempt and body[r, c] == _BG):
                return
        candidates.append((len(cellset), kind, params, cellset))

    dirs_x = ((-1, -1), (-1, 1), (1, -1), (1, 1))
    dirs_p = ((-1, 0), (1, 0), (0, -1), (0, 1))

    seeds: set[Cell] = set(required)
    if marker is not None and allowed[marker]:
        seeds.add(marker)  # an active plus/X/line centre renders as 0
    # A centre hidden under another avatar's crossing bar (measured overlap
    # on L2's final layout), or rendering as a background hole (measured on
    # the inactive X), is still adjacent to its visible arm cells, so every
    # neighbour of a required cell is a candidate centre too.
    for r, c in required:
        for dr, dc in dirs_x + dirs_p:
            cell = (r + dr, c + dc)
            if 0 <= cell[0] < height and 0 <= cell[1] < width:
                seeds.add(cell)
    for r, c in sorted(seeds):
        # ----- X candidate around (r, c) ---------------------------------
        arms = [arm_len(r, c, dr, dc) for dr, dc in dirs_x]
        edges = [edge_dist(r, c, dr, dc) for dr, dc in dirs_x]
        trimmed = [n if n >= e else v for (n, v), e in zip(arms, edges)]
        unclipped = [t for t, e in zip(trimmed, edges) if t < e]
        if (
            len(unclipped) >= 2
            and len(set(unclipped)) == 1
            and unclipped[0] >= _MIN_ARM
        ):
            arm = unclipped[0]
            if all(n >= min(arm, e) for (n, _), e in zip(arms, edges)):
                cells = [(r, c)]
                for dr, dc in dirs_x:
                    cells += [(r + dr * d, c + dc * d) for d in range(1, arm + 1)]
                add_candidate(
                    "x", {"r": r, "c": c, "arm": arm}, cells,
                    exempt=frozenset({(r, c)}),
                )
        if object_present:
            continue  # bars are fitted as lines and re-merged (split physics)
        # ----- plus candidate around (r, c) ------------------------------
        arms = [arm_len(r, c, dr, dc) for dr, dc in dirs_p]
        edges = [edge_dist(r, c, dr, dc) for dr, dc in dirs_p]
        au, ad, al, ar = (n if n >= e else v for (n, v), e in zip(arms, edges))
        e_up, e_dn, e_lf, e_rt = edges
        # ASSUMPTION (holds on every measured instance): opposite arms are
        # equal, so a clipped arm's ideal length is its visible opposite's.
        if au >= e_up and ad < e_dn:
            au = max(au, ad)
        if ad >= e_dn and au < e_up:
            ad = max(ad, au)
        if al >= e_lf and ar < e_rt:
            al = max(al, ar)
        if ar >= e_rt and al < e_lf:
            ar = max(ar, al)
        v_ok = (au == ad) or au >= e_up or ad >= e_dn
        h_ok = (al == ar) or al >= e_lf or ar >= e_rt
        if v_ok and h_ok and min(au, ad) >= _MIN_ARM and min(al, ar) >= _MIN_ARM:
            cells = [(r + dr, c) for dr in range(-min(au, e_up), min(ad, e_dn) + 1)]
            cells += [(r, c + dc) for dc in range(-min(al, e_lf), min(ar, e_rt) + 1)]
            add_candidate(
                "plus", {"r": r, "c": c, "au": au, "ad": ad, "al": al, "ar": ar},
                cells, exempt=frozenset({(r, c)}),
            )

    # ----- diamond candidates (hollow ring, from any extreme vertex; a
    # vertex can coincide with a dot centre or hide under another avatar,
    # so all four are tried) ----------------------------------------------
    _VERTEXES = (
        ((-1, 0), (1, 1), (1, 0)),    # top vertex, walk down-right
        ((0, -1), (-1, 1), (0, 1)),   # left vertex, walk up-right
        ((1, 0), (-1, -1), (-1, 0)),  # bottom vertex, walk up-left
        ((0, 1), (-1, -1), (0, -1)),  # right vertex, walk up-left
    )
    for r, c in sorted(required):
        for (vr, vc), (dr, dc), (cr_dir, cc_dir) in _VERTEXES:
            pr, pc = r + vr, c + vc
            if 0 <= pr < height and 0 <= pc < width and vmask[pr, pc]:
                continue  # not an extreme vertex
            n, v = arm_len(r, c, dr, dc)
            # Two radius readings: trimmed to the last truly-coloured cell,
            # and the full allowed extension (the far vertex can be hidden
            # under another avatar). The ring check rejects the wrong one.
            for radius in sorted({min(n, v), n}):
                if radius < _MIN_RADIUS:
                    continue
                cr, cc = r + cr_dir * radius, c + cc_dir * radius
                ring: list[Cell] = []
                visible = 0
                ok = True
                for ddr in range(-radius, radius + 1):
                    for ddc in {-(radius - abs(ddr)), radius - abs(ddr)}:
                        cell = (cr + ddr, cc + ddc)
                        if not (0 <= cell[0] < height and 0 <= cell[1] < width):
                            continue  # clipped at the frame edge
                        if not allowed[cell]:
                            ok = False
                            break
                        if vmask[cell]:
                            visible += 1
                        ring.append(cell)
                    if not ok:
                        break
                if ok and visible >= 2 * radius:
                    add_candidate("diamond", {"r": cr, "c": cc, "radius": radius}, ring)

    # ----- line candidates (also the bars of a split plus) ----------------
    line_cands: list[
        tuple[int, str, dict[str, int], frozenset[Cell], frozenset[Cell]]
    ] = []
    for horizontal in (True, False):
        outer, inner = (height, width) if horizontal else (width, height)
        for a in range(outer):
            b = 0
            while b < inner:
                cell = (a, b) if horizontal else (b, a)
                if not allowed[cell]:
                    b += 1
                    continue
                first_v = last_v = None
                n_v = 0
                bridges: list[int] = []
                while b < inner:
                    cell = (a, b) if horizontal else (b, a)
                    if not allowed[cell]:
                        # MEASURED (L2, live): a cycled-away centre renders
                        # background; bridge a single such hole when the run
                        # continues right after it.
                        nxt = (a, b + 1) if horizontal else (b + 1, a)
                        if (
                            body[cell] == _BG
                            and b + 1 < inner
                            and allowed[nxt]
                        ):
                            bridges.append(b)
                            b += 1
                            continue
                        break
                    if vmask[cell]:
                        if first_v is None:
                            first_v = b
                        last_v = b
                        n_v += 1
                    b += 1
                if first_v is None or last_v - first_v + 1 < _MIN_LINE or n_v < 2:
                    continue
                lo, hi = first_v, last_v
                cells = frozenset(
                    (a, k) if horizontal else (k, a) for k in range(lo, hi + 1)
                )
                exempt = frozenset(
                    (a, k) if horizontal else (k, a)
                    for k in bridges
                    if lo <= k <= hi
                )
                if horizontal:
                    kind, params = "line_h", {"row": a, "left": lo, "length": hi - lo + 1}
                else:
                    kind, params = "line_v", {"col": a, "top": lo, "length": hi - lo + 1}
                line_cands.append((len(cells), kind, params, cells, exempt))

    # ----- rect candidates (wall outlines, grown from their top walls) ----
    for _, kind, params, _, _ in list(line_cands):
        if kind != "line_h":
            continue
        r0, cl = params["row"], params["left"]
        cr_ = cl + params["length"] - 1
        if params["length"] < _MIN_RECT_SIDE:
            continue
        n, v = arm_len(r0, cl, 1, 0)
        for h in range(_MIN_RECT_SIDE, min(n, v) + 2):
            r1 = r0 + h - 1
            if r1 >= height:
                break
            outline: set[Cell] = set()
            for k in range(cl, cr_ + 1):
                outline.add((r0, k))
                outline.add((r1, k))
            for k in range(r0, r1 + 1):
                outline.add((k, cl))
                outline.add((k, cr_))
            if any(not allowed[p] for p in outline):
                continue
            if sum(1 for p in outline if vmask[p]) < len(outline) // 2:
                continue
            if any(r0 < rr < r1 and cl < cc < cr_ for rr, cc in required):
                continue  # a wall outline holds no interior cells
            add_candidate(
                "rect", {"top": r0, "left": cl, "h": h, "w": cr_ - cl + 1}, outline
            )

    for size, kind, params, cells, exempt in line_cands:
        add_candidate(kind, params, cells, exempt=exempt)

    # ----- greedy selection: structured shapes first, then lines ----------
    priority = {"plus": 0, "x": 0, "diamond": 0, "rect": 1, "line_h": 2, "line_v": 2}
    candidates.sort(key=lambda t: (priority[t[1]], -t[0], sorted(t[3])[:1]))
    uncovered = set(required)
    chosen: list[tuple[str, dict[str, int], frozenset[Cell]]] = []
    for _, kind, params, cells in candidates:
        if not (uncovered & cells):
            continue
        chosen.append((kind, params, cells))
        uncovered -= cells
        if not uncovered:
            break
    if uncovered:
        return None

    avatars: list[Avatar] = []
    lines_h = [(p, cells) for kind, p, cells in chosen if kind == "line_h"]
    lines_v = [(p, cells) for kind, p, cells in chosen if kind == "line_v"]
    # Structural sanity (measured grammar): no board carries two same-colour
    # line avatars. More than one line means a larger shape is currently
    # broken by an overlapping avatar -- fail here so the multi-pass retry
    # refits it with the other avatars' cells as wildcards. With the object
    # the one legal pair is a split plus's H+V bars.
    n_lines = len(lines_h) + len(lines_v)
    if object_present:
        if n_lines > 2 or (n_lines == 2 and not (len(lines_h) == 1 and len(lines_v) == 1)):
            return None
    elif n_lines > 1:
        return None
    if object_present and len(lines_h) == 1 and len(lines_v) == 1:
        # Measured: only the squeeze object can separate a plus's bars, so a
        # same-colour H+V line pair on an object board is one split plus.
        ph, pv = lines_h[0][0], lines_v[0][0]
        avatars.append(
            Avatar(
                kind="split_plus",
                colour=colour,
                params={
                    "vtop": pv["top"], "vcol": pv["col"], "vlen": pv["length"],
                    "hrow": ph["row"], "hleft": ph["left"], "hlen": ph["length"],
                },
            )
        )
        chosen = [t for t in chosen if t[0] not in ("line_h", "line_v")]
    for kind, params, cells in chosen:
        if kind == "line_h":
            half = (params["length"] - 1) // 2
            avatars.append(
                Avatar("line_h", colour, {"r": params["row"], "c": params["left"] + half, "half": half})
            )
        elif kind == "line_v":
            half = (params["length"] - 1) // 2
            avatars.append(
                Avatar("line_v", colour, {"r": params["top"] + half, "c": params["col"], "half": half})
            )
        else:
            avatars.append(Avatar(kind, colour, params))
    return avatars


def _parse_board(
    grid: NDArray[np.int16],
    tile_memory: dict[Cell, int],
    dot_memory: dict[Cell, int],
) -> ParkParse | None:
    if grid.shape != (64, 64):
        return None
    if int(grid.min()) < 0 or int(grid.max()) > 15:
        return None
    timer = _timer_pixels(grid[63])
    if timer is None:
        return None
    body = grid[:_BODY_ROWS]
    census = np.bincount(body.ravel(), minlength=16)
    if int(census.argmax()) != _BG:
        return None
    if int(census[_MARKER]) > 1:
        return None
    if int(census[_TIMER_FULL]) > 0:
        return None

    marker_list = np.argwhere(body == _MARKER)
    marker = (
        (int(marker_list[0][0]), int(marker_list[0][1])) if len(marker_list) else None
    )

    tile_map = {(t.top, t.left): t.colour for t in _find_tiles(body)}
    for key, colour in tile_memory.items():
        tile_map.setdefault(key, colour)
    all_tiles = [Tile(top=k[0], left=k[1], colour=v) for k, v in sorted(tile_map.items())]

    strict_dots = _find_dots_strict(body)
    strict_centres = {(d.row, d.col) for d in strict_dots}
    probable_centres = _probable_dot_centres(body)
    object_cells = frozenset(
        (int(r), int(c)) for r, c in np.argwhere(body == _OBJECT)
    )

    tile_area = np.zeros(body.shape, dtype=bool)
    for t in all_tiles:
        tile_area[t.top : t.top + 6, t.left : t.left + 6] = True
    dot_box = np.zeros(body.shape, dtype=bool)
    for d in strict_dots:
        dot_box[d.row - 1 : d.row + 2, d.col - 1 : d.col + 2] = True
    for r, c in dot_memory:
        if 1 <= r < _BODY_ROWS - 1 and 1 <= c < _COLS - 1:
            dot_box[r - 1 : r + 2, c - 1 : c + 2] = True

    colours = [
        v
        for v in range(16)
        if census[v] > 0
        and v not in (_MARKER, _OBJECT, _TILE_RING, _RING, _BG, _TIMER_FULL)
    ]
    if len(colours) > 10:
        return None

    fitted: dict[int, list[Avatar]] = {}
    fitted_cells: dict[int, set[Cell]] = {}
    remaining = list(colours)
    passes = 0
    while remaining and passes < 3:
        passes += 1
        still: list[int] = []
        others = np.zeros(body.shape, dtype=bool)
        for cells in fitted_cells.values():
            for r, c in cells:
                others[r, c] = True
        for colour in remaining:
            vmask = body == colour
            required: set[Cell] = set()
            for r, c in np.argwhere(vmask):
                r, c = int(r), int(c)
                if dot_box[r, c] or (r, c) in strict_centres or (r, c) in probable_centres:
                    continue
                if tile_area[r, c] and any(
                    t.colour == colour
                    and t.top < r < t.top + 5
                    and t.left < c < t.left + 5
                    for t in all_tiles
                ):
                    continue  # a tile interior cell of its own colour
                required.add((r, c))
            if not required:
                continue  # this colour appears only as dots/tiles
            if len(required) > _MAX_REQUIRED:
                return None
            allowed = vmask | tile_area | dot_box | others
            if marker is not None:
                allowed[marker] = True
            shapes = _fit_colour_shapes(
                body, colour, required, allowed, bool(object_cells), marker
            )
            if shapes is None:
                still.append(colour)
                continue
            fitted[colour] = shapes
            fitted_cells[colour] = set()
            for s in shapes:
                fitted_cells[colour] |= s.cells()
        if still == remaining:
            return None  # no progress: some colour is unexplainable
        remaining = still
    if remaining:
        return None

    avatars = [a for shapes in fitted.values() for a in shapes]
    if len(avatars) < 2:
        return None

    covered = np.zeros(body.shape, dtype=bool)
    for cells in fitted_cells.values():
        for r, c in cells:
            covered[r, c] = True

    # Tolerant dots: boxes whose hidden cells sit under fitted avatar cells.
    dots: dict[Cell, Dot] = {(d.row, d.col): d for d in strict_dots}
    for r, c in np.argwhere(body == _RING):
        r, c = int(r), int(c)
        if any(abs(r - dr) <= 1 and abs(c - dc) <= 1 for dr, dc in dots):
            continue
        placed = False
        for cr in range(max(r - 1, 1), min(r + 2, _BODY_ROWS - 1)):
            for cc in range(max(c - 1, 1), min(c + 2, _COLS - 1)):
                ok = True
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        cell = (cr + dr, cc + dc)
                        val = int(body[cell])
                        if covered[cell]:
                            continue  # hidden under an avatar: anything goes
                        if dr == 0 and dc == 0:
                            if val in (_RING, _BG, _TILE_RING, _TIMER_FULL):
                                ok = False
                        elif val != _RING:
                            ok = False
                    if not ok:
                        break
                if ok:
                    centre_val = int(body[cr, cc])
                    colour = (
                        centre_val
                        if not covered[cr, cc]
                        else dot_memory.get((cr, cc))
                    )
                    dots[(cr, cc)] = Dot(row=cr, col=cc, colour=colour)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            return None  # a colour-4 cell outside any dot box
    for (r, c), colour in dot_memory.items():
        dots.setdefault((r, c), Dot(row=r, col=c, colour=colour))
    if len(dots) < 2:
        return None

    explained = covered | tile_area | dot_box
    for d in dots.values():
        explained[max(d.row - 1, 0) : d.row + 2, max(d.col - 1, 0) : d.col + 2] = True
    unexplained = (body != _BG) & (body != _OBJECT) & ~explained
    if marker is not None:
        unexplained[marker] = False
    if unexplained.any():
        return None

    return ParkParse(
        avatars=sorted(avatars, key=lambda a: (a.colour, a.kind, a.centre)),
        dots=sorted(dots.values(), key=lambda d: (d.row, d.col)),
        tiles=all_tiles,
        object_cells=object_cells,
        marker=marker,
        timer_pixels=timer,
    )


# ------------------------------------------------------------------ coverage


def _dot_box_cells(dot: Dot) -> list[Cell]:
    return [
        (dot.row + dr, dot.col + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
    ]


def _cover_centres(avatar: Avatar, dot: Dot) -> set[Cell]:
    """Centres on the avatar's mod-3 lattice whose placement puts at least
    one avatar cell inside the dot's 3x3 box. Box cells are always on the
    board, so edge clipping can never make this overclaim coverage."""

    lat = avatar.centre
    out = set()
    for dr, dc in avatar.coverage_offsets():
        for br, bc in _dot_box_cells(dot):
            r, c = br - dr, bc - dc
            if (r - lat[0]) % _STEP or (c - lat[1]) % _STEP:
                continue
            if 0 <= r < _BODY_ROWS and 0 <= c < _COLS:
                out.add((r, c))
    return out


def _bar_cover_positions(length: int, vertical: bool, res: Cell, dot: Dot) -> set[Cell]:
    """Bar top-left positions (residue-preserving) covering the dot box."""

    out = set()
    for k in range(length):
        orr, occ = (k, 0) if vertical else (0, k)
        for br, bc in _dot_box_cells(dot):
            r, c = br - orr, bc - occ
            if (r - res[0]) % _STEP == 0 and (c - res[1]) % _STEP == 0:
                out.add((r, c))
    return out


def _rect_outline_cover(top: int, left: int, h: int, w: int, dot: Dot) -> bool:
    r1, c1 = top + h - 1, left + w - 1
    for br, bc in _dot_box_cells(dot):
        on_h = br in (top, r1) and left <= bc <= c1
        on_v = bc in (left, c1) and top <= br <= r1
        if on_h or on_v:
            return True
    return False


# -------------------------------------------------------------------- routes


def _sweep_offset_arrays(avatar: Avatar) -> dict[int, NDArray[np.int64]]:
    """Per action, every 1-px offset swept during one 3-px move (unclipped
    superset: safe for avoidance under either contact semantics)."""

    offs = np.array(avatar.cell_offsets(), dtype=np.int64)
    out = {}
    for action, (dr, dc) in _DIR.items():
        stack = [offs + np.array([dr * k, dc * k]) for k in range(_STEP + 1)]
        out[action] = np.unique(np.vstack(stack), axis=0)
    return out


def _route_field(
    avatar: Avatar,
    start: Cell,
    forbidden: NDArray[np.bool_] | None,
) -> tuple[dict[Cell, int], dict[Cell, tuple[Cell, int] | None]]:
    """BFS distances over 3-px centre moves; a move is illegal when its 1-px
    sweep touches a forbidden cell. Returns (dist, prev)."""

    sweeps = _sweep_offset_arrays(avatar)
    dist: dict[Cell, int] = {start: 0}
    prev: dict[Cell, tuple[Cell, int] | None] = {start: None}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for action, (dr, dc) in _DIR.items():
            nxt = (cur[0] + dr * _STEP, cur[1] + dc * _STEP)
            if not (0 <= nxt[0] < _BODY_ROWS and 0 <= nxt[1] < _COLS):
                continue
            if nxt in prev:
                continue
            if forbidden is not None:
                cells = sweeps[action] + np.array(cur)
                inb = (
                    (cells[:, 0] >= 0)
                    & (cells[:, 0] < _BODY_ROWS)
                    & (cells[:, 1] >= 0)
                    & (cells[:, 1] < _COLS)
                )
                if forbidden[cells[inb, 0], cells[inb, 1]].any():
                    continue
            prev[nxt] = (cur, action)
            dist[nxt] = dist[cur] + 1
            queue.append(nxt)
    return dist, prev


def _walk(prev: dict[Cell, tuple[Cell, int] | None], node: Cell) -> list[int]:
    path: list[int] = []
    while prev[node] is not None:
        parent, action = prev[node]
        path.append(action)
        node = parent
    return path[::-1]


def _tiles_mask(tiles: Iterable[Tile]) -> NDArray[np.bool_]:
    mask = np.zeros((_BODY_ROWS, _COLS), dtype=bool)
    for t in tiles:
        mask[t.top : t.top + 6, t.left : t.left + 6] = True
    return mask


def _object_mask(object_cells: frozenset[Cell]) -> NDArray[np.bool_] | None:
    if not object_cells:
        return None
    mask = np.zeros((_BODY_ROWS, _COLS), dtype=bool)
    for r, c in object_cells:
        mask[r, c] = True
    return mask


def _drop_overlapped(avatar: Avatar, tiles: list[Tile]) -> list[Tile]:
    """Tiles the avatar currently overlaps: contact already happened, so a
    route may leave through them (the parse re-reads the colour anyway)."""

    cells = avatar.cells()
    return [
        t
        for t in tiles
        if not any(
            t.top <= r < t.top + 6 and t.left <= c < t.left + 6 for r, c in cells
        )
    ]


# --------------------------------------------------------- split-plus physics


def _split_plus_route(
    plus: Avatar,
    target: tuple[int, int, int, int],
    object_cells: frozenset[Cell],
    cache: dict,
) -> list[int] | None:
    """BFS over joint (vbar, hbar) states under the measured per-part
    physics: a bar whose 3-px sweep hits an object cell stays for that step
    while the other bar still moves; grid edges only clip."""

    p = plus.params
    start = (p["vtop"], p["vcol"], p["hrow"], p["hleft"])
    key = (start, target, p["vlen"], p["hlen"])
    if key in cache:
        return cache[key]
    vlen, hlen = p["vlen"], p["hlen"]
    obj = object_cells

    def band_hit(r0: int, r1: int, c0: int, c1: int) -> bool:
        for r in range(max(r0, 0), min(r1, _BODY_ROWS - 1) + 1):
            for c in range(max(c0, 0), min(c1, _COLS - 1) + 1):
                if (r, c) in obj:
                    return True
        return False

    lo = -12  # deep edge clipping is never useful; keeps the state space sane
    blocked_v: dict[tuple[int, int, int], bool] = {}
    blocked_h: dict[tuple[int, int, int], bool] = {}

    def v_blocked(top: int, col: int, action: int) -> bool:
        key_ = (top, col, action)
        hit = blocked_v.get(key_)
        if hit is None:
            dr, dc = _DIR[action]
            if dr < 0:
                hit = band_hit(top - 3, top - 1, col, col)
            elif dr > 0:
                hit = band_hit(top + vlen, top + vlen + 2, col, col)
            elif dc < 0:
                hit = band_hit(top, top + vlen - 1, col - 3, col - 1)
            else:
                hit = band_hit(top, top + vlen - 1, col + 1, col + 3)
            blocked_v[key_] = hit
        return hit

    def h_blocked(row: int, left: int, action: int) -> bool:
        key_ = (row, left, action)
        hit = blocked_h.get(key_)
        if hit is None:
            dr, dc = _DIR[action]
            if dr < 0:
                hit = band_hit(row - 3, row - 1, left, left + hlen - 1)
            elif dr > 0:
                hit = band_hit(row + 1, row + 3, left, left + hlen - 1)
            elif dc < 0:
                hit = band_hit(row, row, left - 3, left - 1)
            else:
                hit = band_hit(row, row, left + hlen, left + hlen + 2)
            blocked_h[key_] = hit
        return hit

    prev: dict[tuple, tuple | None] = {start: None}
    queue = deque([start])
    goal_state = None
    nodes = 0
    while queue:
        state = queue.popleft()
        if state == target:
            goal_state = state
            break
        vt, vc, hr, hl = state
        for action in (1, 2, 3, 4):
            dr, dc = _DIR[action]
            nvt, nvc = (vt, vc) if v_blocked(vt, vc, action) else (
                vt + dr * _STEP, vc + dc * _STEP
            )
            nhr, nhl = (hr, hl) if h_blocked(hr, hl, action) else (
                hr + dr * _STEP, hl + dc * _STEP
            )
            nxt = (nvt, nvc, nhr, nhl)
            if nxt == state:
                continue  # both bars blocked: the engine's no-op
            if not (lo <= nvt < _BODY_ROWS and 0 <= nvc < _COLS):
                continue
            if not (0 <= nhr < _BODY_ROWS and lo <= nhl < _COLS):
                continue
            if nxt in prev:
                continue
            prev[nxt] = (state, action)
            nodes += 1
            if nodes > _BFS_NODE_CAP:
                cache[key] = None
                return None
            queue.append(nxt)
    if goal_state is None:
        cache[key] = None
        return None
    path: list[int] = []
    walk = goal_state
    while prev[walk] is not None:
        parent, action = prev[walk]
        path.append(action)
        walk = parent
    cache[key] = path[::-1]
    return cache[key]


# ------------------------------------------------------------- rect planning


def _rect_route(
    rect: Avatar,
    goal: tuple[int, int, int, int],
    object_cells: frozenset[Cell],
) -> list[int] | None:
    """Reactive rect planning. While the shape differs from the goal shape,
    navigate object-safely to a press position and emit ONE squeeze press:
    the executor re-parses after the chunk, so the measured alternating-side
    growth needs no modelling. Once shapes match, navigate to the goal."""

    p = rect.params
    top, left, h, w = p["top"], p["left"], p["h"], p["w"]
    g_top, g_left, g_h, g_w = goal
    obj = object_cells
    if (h, w) != (g_h, g_w) and not obj:
        return None
    if obj:
        rows = [r for r, _ in obj]
        cols = [c for _, c in obj]
        o_r0, o_r1, o_c0, o_c1 = min(rows), max(rows), min(cols), max(cols)

    def outline(t: int, l: int) -> list[Cell]:
        cells = []
        r1, c1 = t + h - 1, l + w - 1
        for k in range(l, c1 + 1):
            cells.append((t, k))
            cells.append((r1, k))
        for k in range(t + 1, r1):
            cells.append((k, l))
            cells.append((k, c1))
        return cells

    def move_deforms(t: int, l: int, action: int) -> bool:
        """A wall's 1..3 px sweep hitting an object cell deforms the rect."""

        if not obj:
            return False
        dr, dc = _DIR[action]
        for r, c in outline(t, l):
            for k in (1, 2, 3):
                if (r + dr * k, c + dc * k) in obj:
                    return True
        return False

    def navigate(src: Cell, dst: Cell) -> list[int] | None:
        if src == dst:
            return []
        prev: dict[Cell, tuple[Cell, int] | None] = {src: None}
        queue = deque([src])
        while queue:
            cur = queue.popleft()
            if cur == dst:
                break
            for action, (dr, dc) in _DIR.items():
                nxt = (cur[0] + dr * _STEP, cur[1] + dc * _STEP)
                if nxt in prev:
                    continue
                if not (
                    0 <= nxt[0]
                    and nxt[0] + h <= _BODY_ROWS
                    and 0 <= nxt[1]
                    and nxt[1] + w <= _COLS
                ):
                    continue
                if move_deforms(cur[0], cur[1], action):
                    continue
                prev[nxt] = (cur, action)
                queue.append(nxt)
        if dst not in prev:
            return None
        return _walk(prev, dst)

    if (h, w) == (g_h, g_w):
        return navigate((top, left), (g_top, g_left))

    # One squeeze press toward the needed shape. A horizontal press shrinks
    # w by 3 and grows h by 3 (measured); a vertical press does the reverse.
    presses: list[tuple[int, Cell]] = []
    if g_h > h:
        for press, l_pos in ((4, o_c0 - w), (3, o_c1 + 1)):
            if not (0 <= l_pos and l_pos + w <= _COLS):
                continue
            if (l_pos - left) % _STEP:
                continue
            for t in range((top % _STEP), _BODY_ROWS - h + 1, _STEP):
                if t + h - 1 < o_r0 or t > o_r1:
                    continue  # the pressed wall would miss the object rows
                # margin for the alternating perpendicular growth
                if t - _STEP < 0 or t + h - 1 + _STEP > _BODY_ROWS - 1:
                    continue
                presses.append((press, (t, l_pos)))
    else:
        for press, t_pos in ((2, o_r0 - h), (1, o_r1 + 1)):
            if not (0 <= t_pos and t_pos + h <= _BODY_ROWS):
                continue
            if (t_pos - top) % _STEP:
                continue
            for l in range((left % _STEP), _COLS - w + 1, _STEP):
                if l + w - 1 < o_c0 or l > o_c1:
                    continue
                if l - _STEP < 0 or l + w - 1 + _STEP > _COLS - 1:
                    continue
                presses.append((press, (t_pos, l)))
    best: list[int] | None = None
    for press, pos in presses:
        nav = navigate((top, left), pos)
        if nav is None:
            continue
        seq = nav + [press]
        if best is None or len(seq) < len(best):
            best = seq
    return best


# ---------------------------------------------------------------- assignment


@dataclass
class _Option:
    colour: int
    covered: frozenset[Cell]  # dot centres this option covers
    cost: int
    spec: tuple  # ('rigid', centre) | ('split', v, h) | ('rect', geom)


class CrosshairParkingArchetype:
    """Parser + planner for re86's crosshair-parking grammar."""

    name = "crosshair_parking"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear all per-life state (called on RESET and level advance)."""

        self._tile_memory: dict[Cell, int] = {}
        self._dot_memory: dict[Cell, int] = {}
        self._bfs_cache: dict = {}

    # ------------------------------------------------------------- contract

    def match(self, grid: NDArray[np.integer]) -> ParkParse | None:
        frame = np.asarray(grid, dtype=np.int16)
        parse = _parse_board(frame, self._tile_memory, self._dot_memory)
        if parse is None:
            return None
        for t in parse.tiles:
            self._tile_memory[(t.top, t.left)] = t.colour
        for d in parse.dots:
            if d.colour is not None:
                self._dot_memory[(d.row, d.col)] = d.colour
        return parse

    def next_actions(self, parse: ParkParse, grid: NDArray[np.integer]) -> list[Step]:
        del grid  # the parse already carries everything derived from it
        if parse.object_cells and parse.tiles:
            # L7's combination; the dossier records L7 UNSOLVED (every known
            # mechanic leaves the cover at least one line short). Abstain.
            return []
        excluded: set[tuple[int, tuple]] = set()
        for _ in range(6):
            assignment = self._solve_assignment(parse, excluded)
            if assignment is None:
                return []
            active_idx = self._active_index(parse)
            if active_idx is None:
                return [Step(action=5)]  # cycling relocates the marker
            option = assignment.get(active_idx)
            avatar = parse.avatars[active_idx]
            if option is None or self._satisfied(avatar, option):
                if all(
                    assignment.get(i) is None
                    or self._satisfied(parse.avatars[i], assignment[i])
                    for i in range(len(parse.avatars))
                ):
                    return []  # everything parked yet the level did not fall
                return [Step(action=5)]
            steps = self._plan_phase(parse, avatar, option)
            if steps:
                return steps[:_MAX_PLAN]
            excluded.add((active_idx, option.spec))  # unreachable: re-solve
        return []

    # ---------------------------------------------------------- active side

    def _active_index(self, parse: ParkParse) -> int | None:
        if parse.marker is None:
            return None
        for i, avatar in enumerate(parse.avatars):
            if avatar.centre == parse.marker:
                return i
        return None

    def _satisfied(self, avatar: Avatar, option: _Option) -> bool:
        if avatar.colour != option.colour:
            return False
        spec = option.spec
        if spec[0] == "rigid":
            return avatar.centre == spec[1]
        if spec[0] == "split":
            p = avatar.params
            return (p["vtop"], p["vcol"]) == spec[1] and (p["hrow"], p["hleft"]) == spec[2]
        if spec[0] == "rect":
            p = avatar.params
            return (p["top"], p["left"], p["h"], p["w"]) == spec[1]
        return False

    # ---------------------------------------------------------- assignment

    def _solve_assignment(
        self, parse: ParkParse, excluded: set[tuple[int, tuple]]
    ) -> dict[int, _Option] | None:
        dots = parse.dots
        unknown = [d for d in dots if d.colour is None]
        candidate_colours = sorted(
            {d.colour for d in dots if d.colour is not None}
            | {t.colour for t in parse.tiles}
        )
        if unknown and not candidate_colours:
            return None
        combos: list[dict[Cell, int]] = [{}]
        for d in unknown:
            combos = [
                {**combo, (d.row, d.col): colour}
                for combo in combos
                for colour in candidate_colours
            ][:16]
        for combo in combos:
            filled = [
                d if d.colour is not None else Dot(d.row, d.col, combo[(d.row, d.col)])
                for d in dots
            ]
            result = self._assign(parse, filled, excluded)
            if result is not None:
                return result
        return None

    def _assign(
        self,
        parse: ParkParse,
        dots: list[Dot],
        excluded: set[tuple[int, tuple]],
    ) -> dict[int, _Option] | None:
        tile_colours = {t.colour for t in parse.tiles}
        by_colour: dict[int, list[Dot]] = {}
        for d in dots:
            by_colour.setdefault(d.colour, []).append(d)
        deformable = bool(parse.object_cells)
        option_memo: dict[tuple[int, int], list[_Option]] = {}
        nodes = [0]

        def all_options(idx: int, colour: int) -> list[_Option]:
            key = (idx, colour)
            if key in option_memo:
                return option_memo[key]
            avatar = parse.avatars[idx]
            group = by_colour[colour]
            reachable = avatar.colour == colour or colour in tile_colours
            options: list[_Option] = []
            if reachable:
                needs_recolour = avatar.colour != colour
                if avatar.kind == "split_plus":
                    if not needs_recolour:
                        options = self._split_options(avatar, colour, group)
                elif avatar.kind == "rect":
                    # No measured level recolours the rect; keep it literal.
                    if not needs_recolour:
                        options = self._rect_options(avatar, colour, group, deformable)
                elif not (needs_recolour and parse.object_cells):
                    options = self._rigid_options(avatar, colour, group, needs_recolour)
            options = [o for o in options if (idx, o.spec) not in excluded]
            option_memo[key] = options
            return options

        order = sorted(dots, key=lambda d: (d.row, d.col))

        def dfs(
            uncovered: list[Dot], assigned: dict[int, _Option]
        ) -> dict[int, _Option] | None:
            nodes[0] += 1
            if nodes[0] > _ASSIGN_NODE_CAP:
                return None
            if not uncovered:
                return dict(assigned)
            dot = uncovered[0]
            assert dot.colour is not None
            for idx in range(len(parse.avatars)):
                if idx in assigned:
                    continue
                for option in all_options(idx, dot.colour):
                    if (dot.row, dot.col) not in option.covered:
                        continue
                    assigned[idx] = option
                    rest = [d for d in uncovered if (d.row, d.col) not in option.covered]
                    result = dfs(rest, assigned)
                    if result is not None:
                        return result
                    del assigned[idx]
            return None

        return dfs(order, {})

    def _rigid_options(
        self, avatar: Avatar, colour: int, group: list[Dot], needs_recolour: bool
    ) -> list[_Option]:
        cover = {(d.row, d.col): _cover_centres(avatar, d) for d in group}
        positions: set[Cell] = set()
        for pset in cover.values():
            positions |= pset
        cur = avatar.centre
        options = []
        for pos in sorted(positions):
            covered = frozenset(dc for dc, pset in cover.items() if pos in pset)
            dist = (abs(pos[0] - cur[0]) + abs(pos[1] - cur[1])) // _STEP
            cost = dist + (12 if needs_recolour else 0)
            options.append(_Option(colour, covered, cost, ("rigid", pos)))
        options.sort(key=lambda o: (o.cost, o.spec))
        return options

    def _split_options(
        self, plus: Avatar, colour: int, group: list[Dot]
    ) -> list[_Option]:
        p = plus.params
        v_res = (p["vtop"], p["vcol"])
        h_res = (p["hrow"], p["hleft"])
        v_cover: dict[Cell, set[Cell]] = {v_res: set()}
        h_cover: dict[Cell, set[Cell]] = {h_res: set()}
        for d in group:
            for pos in _bar_cover_positions(p["vlen"], True, v_res, d):
                v_cover.setdefault(pos, set()).add((d.row, d.col))
            for pos in _bar_cover_positions(p["hlen"], False, h_res, d):
                h_cover.setdefault(pos, set()).add((d.row, d.col))
        options = []
        for vp, vcov in sorted(v_cover.items()):
            for hp, hcov in sorted(h_cover.items()):
                covered = frozenset(vcov | hcov)
                if not covered:
                    continue
                dist = (
                    abs(vp[0] - v_res[0])
                    + abs(vp[1] - v_res[1])
                    + abs(hp[0] - h_res[0])
                    + abs(hp[1] - h_res[1])
                ) // _STEP
                options.append(_Option(colour, covered, dist, ("split", vp, hp)))
        options.sort(key=lambda o: (o.cost, o.spec))
        # Keep the few cheapest options per distinct coverage set, so a
        # full-coverage option always survives the pool truncation.
        kept: dict[frozenset[Cell], int] = {}
        pruned = []
        for o in options:
            n = kept.get(o.covered, 0)
            if n >= 3:
                continue
            kept[o.covered] = n + 1
            pruned.append(o)
        return pruned[:400]

    def _rect_options(
        self, rect: Avatar, colour: int, group: list[Dot], deformable: bool
    ) -> list[_Option]:
        p = rect.params
        h0, w0 = p["h"], p["w"]
        total = h0 + w0
        shapes = [(h0, w0)]
        if deformable:
            shapes = [
                (h, total - h)
                for h in range(_MIN_RECT_SIDE, total - _MIN_RECT_SIDE + 1)
                if (h - h0) % _STEP == 0
            ]
        found: dict[tuple, _Option] = {}
        for h, w in shapes:
            tops: set[int] = set()
            lefts: set[int] = set()
            for d in group:
                for br, bc in _dot_box_cells(d):
                    for t in (br, br - h + 1):
                        if (t - p["top"]) % _STEP == 0:
                            tops.add(t)
                    for l in (bc, bc - w + 1):
                        if (l - p["left"]) % _STEP == 0:
                            lefts.add(l)
                    # box cells can also lie mid-wall
                    for t in range(br - h + 1, br + 1):
                        if (t - p["top"]) % _STEP == 0:
                            tops.add(t)
                    for l in range(bc - w + 1, bc + 1):
                        if (l - p["left"]) % _STEP == 0:
                            lefts.add(l)
            for top in sorted(tops):
                if not (0 <= top and top + h <= _BODY_ROWS):
                    continue
                for left in sorted(lefts):
                    if not (0 <= left and left + w <= _COLS):
                        continue
                    covered = frozenset(
                        (d.row, d.col)
                        for d in group
                        if _rect_outline_cover(top, left, h, w, d)
                    )
                    if not covered:
                        continue
                    presses = abs(h - h0) // _STEP
                    dist = (abs(top - p["top"]) + abs(left - p["left"])) // _STEP
                    geom = (top, left, h, w)
                    option = _Option(
                        colour, covered, dist + presses * 8, ("rect", geom)
                    )
                    if geom not in found or option.cost < found[geom].cost:
                        found[geom] = option
        options = sorted(found.values(), key=lambda o: (o.cost, o.spec))
        kept: dict[frozenset[Cell], int] = {}
        pruned = []
        for o in options:
            n = kept.get(o.covered, 0)
            if n >= 3:
                continue
            kept[o.covered] = n + 1
            pruned.append(o)
        return pruned[:400]

    # ------------------------------------------------------------- planning

    def _plan_phase(
        self, parse: ParkParse, avatar: Avatar, option: _Option
    ) -> list[Step] | None:
        spec = option.spec
        if spec[0] == "split":
            target = (spec[1][0], spec[1][1], spec[2][0], spec[2][1])
            actions = _split_plus_route(
                avatar, target, parse.object_cells, self._bfs_cache
            )
            return [Step(action=a) for a in actions] if actions else None
        if spec[0] == "rect":
            actions = _rect_route(avatar, spec[1], parse.object_cells)
            return [Step(action=a) for a in actions] if actions else None

        goal = spec[1]
        start = avatar.centre
        if start == goal and avatar.colour == option.colour:
            return None  # nothing to do; _satisfied should have caught this
        if parse.object_cells:
            # ASSUMPTION: contact physics for rigid non-plus shapes was never
            # measured; route around the object instead of touching it.
            dist, prev = _route_field(avatar, start, _object_mask(parse.object_cells))
            if goal not in prev:
                return None
            return [Step(action=a) for a in _walk(prev, goal)]
        if not parse.tiles:
            steps: list[Step] = []
            dr, dc = goal[0] - start[0], goal[1] - start[1]
            steps += [Step(action=1 if dr < 0 else 2)] * (abs(dr) // _STEP)
            steps += [Step(action=3 if dc < 0 else 4)] * (abs(dc) // _STEP)
            return steps or None

        # Tiles present: the LAST tile touched decides the colour.
        needs_recolour = avatar.colour != option.colour
        if not needs_recolour:
            forbidden = _tiles_mask(_drop_overlapped(avatar, parse.tiles))
            dist, prev = _route_field(avatar, start, forbidden)
            if goal in prev:
                return [Step(action=a) for a in _walk(prev, goal)]
            # boxed in: fall through and re-touch an own-colour tile last
        target_tiles = [t for t in parse.tiles if t.colour == option.colour]
        best: list[int] | None = None
        for tile in target_tiles:
            others = [t for t in parse.tiles if t is not tile]
            forbidden = _tiles_mask(_drop_overlapped(avatar, others))
            dist_s, prev_s = _route_field(avatar, start, forbidden)
            dist_g, prev_g = _route_field(avatar, goal, forbidden)
            touches = self._tile_touch_positions(avatar, tile)
            for q in touches:
                if q not in dist_s or q not in dist_g:
                    continue
                seq = _walk(prev_s, q) + [
                    _INV[a] for a in reversed(_walk(prev_g, q))
                ]
                if best is None or len(seq) < len(best):
                    best = seq
                break  # touches are sorted; the first reachable one is best
        if best is None:
            return None
        return [Step(action=a) for a in best]

    def _tile_touch_positions(self, avatar: Avatar, tile: Tile) -> list[Cell]:
        """Landing centres whose placement overlaps the tile's 6x6 area
        (contact is measured on landings), nearest to the avatar first."""

        res = avatar.centre
        out = set()
        for dr, dc in avatar.coverage_offsets():
            for tr in range(tile.top, tile.top + 6):
                for tc in range(tile.left, tile.left + 6):
                    r, c = tr - dr, tc - dc
                    if (r - res[0]) % _STEP or (c - res[1]) % _STEP:
                        continue
                    if 0 <= r < _BODY_ROWS and 0 <= c < _COLS:
                        out.add((r, c))
        return sorted(out, key=lambda q: abs(q[0] - res[0]) + abs(q[1] - res[1]))

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "fap_archetype",
            "name": self.name,
            "fly_content": "none; engineered scaffold per the first principle",
        }
