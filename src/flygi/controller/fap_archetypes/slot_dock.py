"""ka59's archetype: multi-body sokoban-with-launchers ("slot dock").

Every mechanic encoded here is MEASURED in the ka59 dossier
(docs/fap_extension_20260928/ka59/NOTES.md) or re-measured against the
dossier's verified 321-action full-win replay (7/7 levels, GameState.WIN)
unless a comment says otherwise:

* the world lives on a 3-pixel tile lattice whose offset varies per level
  and is derived from the objects' bounding boxes;
* colour roles: 1 floor, 2 hard wall, 15 membrane, 4 slot outline (and the
  row-63 timer), 14 drivable-object body, 0/5/4 selected / never-selected /
  deselected centre patch, 11 boulder (push-only), 12/13 geyser-block
  charge/material;
* a drivable object renders as a solid colour-14 rectangle whose central
  1-or-2-pixel-per-axis patch carries the selection colour (measured L2/L7:
  one ring per OBJECT, not per tile -- a 3x6 domino shows `ee55ee`, and the
  selected object additionally recolours a full tile-edge line to 0 where it
  touches another object);
* click (action 6) on a centre-patch pixel selects that object; all other
  clicks are no-ops.  Arrows drive the selected object one tile; walking is
  blocked by walls, membranes and objects but passes over slot outlines;
* driving into an occupied tile launches the contacted object 5 tiles,
  extended forward until fully clear of any membrane it overlaps, stopping
  early (whole tiles) if the next step would cross a wall, and retreating
  while it still overlaps a membrane when the flight is wall-stopped;
  objects in the flight path are plowed ahead and deposited adjacent beyond
  the landing; the pusher never advances;
* geyser blocks charge one pixel-line per MOVE action (1-4, blocked moves
  included; clicks never tick -- measured via the L7 clicks and an L5
  blocked-move probe, 2026-09-28).  The charge (colour-12) region grows from
  one face; when it wraps (charge == extent) the block fires a beam from the
  OPPOSITE face: every object in the open-face band (columns of the block,
  walls and membranes cut the band) is launched 3 tiles with the same
  extend-past-membrane rule (measured on all four beam events of the win
  replay: L5 39-41->45-47 without a membrane, L6 39-41->27-29, 24-26->36-38
  and 42-44->27-29 across one);
* a level falls the instant every slot interior is exactly covered by a
  same-shaped drivable object or boulder.

This module is ENGINEERED SCAFFOLD, recorded as such per the repository
first principle: no fly neuron computes anything here.  Its comparison
evidence is the executor-driven offline run against the dossier's verified
hand programs (target 7/7 levels).

The planner is time-expanded A*: states are (object positions, selection,
clock mod geyser cycle), edges are the four drives (blocked drives are legal
waits that tick the geyser clock), selection clicks (which do not tick), and
the physics above; the goal is every slot exactly docked.  Board geometry is
re-derived from the CURRENT frame on every parse; nothing level-specific is
stored in this file.

ASSUMPTION (labelled, greppable): drivable objects are rectangles of at most
2x2 tiles, as measured on all seven levels (1x1, 1x2, 2x1, 2x2).  The centre
patch of such a rectangle touches exactly its own tiles, which is what makes
the merged-sprite split unambiguous; a 3-tile-axis drivable object would
abstain rather than mis-parse.  ASSUMPTION: the timer row is not modelled;
plans are shortest-in-actions and the executor's RESET path absorbs a
timed-out life (measured drain rates vary per level, 0.33-0.64 px/action).
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from math import gcd
from typing import Any

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

_FLOOR = 1
_WALL = 2
_SLOT = 4
_NEVER = 5
_SELECTED = 0
_DESELECTED = 4
_BOULDER = 11
_CHARGE = 12  # "c": charged geyser material
_MATERIAL = 13  # "d": uncharged geyser material
_BODY = 14  # "e": drivable-object body
_MEMBRANE = 15

_T = 3  # tile size in pixels
_PUSH_TILES = 5  # contact-push flight length (measured L1..L7)
_BEAM_TILES = 3  # geyser-beam flight length (measured L5/L6)

_BODY_ALLOWED = frozenset(
    {_SELECTED, _FLOOR, _WALL, _SLOT, _NEVER, _BOULDER, _CHARGE, _MATERIAL, _BODY, _MEMBRANE}
)
_DIRS: dict[int, tuple[int, int]] = {1: (-1, 0), 2: (1, 0), 3: (0, -1), 4: (0, 1)}

_MAX_NODES = 400_000
_MAX_PLAN = 400
_MAX_FLIGHT = 40  # safety cap on any single flight, > board diagonal in tiles


@dataclass(frozen=True)
class _Obj:
    kind: str  # 'drive' | 'boulder' | 'geyser'
    anchor: tuple[int, int]  # top-left pixel of the bounding box
    tiles: frozenset[tuple[int, int]]  # occupied tiles relative to anchor
    shape: tuple[tuple[int, int], ...]  # canonical sorted tile offsets
    sel: int | None = None  # 0/4/5 centre-patch colour for 'drive'
    fill: int | None = None  # geyser charge count at parse time
    fill_dir: tuple[int, int] | None = None  # beam direction, None = unknown
    period: int | None = None  # pixel extent along the charge axis


@dataclass
class SlotParse:
    """Everything ``next_actions`` needs, derived from one frame."""

    lattice: tuple[int, int]  # pixel offset of the tile grid, per axis
    objects: list[_Obj]
    slots: list[tuple[tuple[int, int], tuple[tuple[int, int], ...]]]
    body: NDArray[np.int16]  # rows 0..62 as parsed (for the world build)
    timer_pixels: int


# ------------------------------------------------------------------ parsing


def _patch_span(extent_px: int) -> tuple[int, int]:
    """Centre-patch pixel range along one axis of an ``extent_px`` box."""

    return (extent_px - 1) // 2, extent_px // 2


def _parse(grid: NDArray[np.int16]) -> SlotParse | None:
    """Strict structural parse of the slot-dock grammar; None = abstain.

    Ordered so the abstain path for foreign games stays cheap: shape, timer
    row and colour census run before any component labelling.
    """

    if grid.shape != (64, 64):
        return None
    timer = grid[63]
    n4 = int((timer == _SLOT).sum())
    if n4 < 1 or not (timer[:n4] == _SLOT).all() or not (timer[n4:] == 0).all():
        return None
    body = grid[:63]
    if int(body.min()) < 0 or int(body.max()) > 15:
        return None
    census = np.bincount(body.ravel(), minlength=16)
    if any(int(census[v]) and v not in _BODY_ALLOWED for v in range(16)):
        return None
    # A drivable object contributes 9+ pixels of {14, 0}; contact-edge
    # recolouring (measured L3, frame 79 of the win replay) can take the
    # 14-count of a pushing 1x1 down to 5, so gate on the sum.
    if (
        int(census[_BODY]) + int(census[_SELECTED]) < 9
        or census[_BODY] == 0
        or census[_FLOOR] == 0
        or census[_SLOT] == 0
    ):
        return None

    from scipy import ndimage

    # --- lattice: every sprite bounding box must agree on the 3px offset.
    sprite = np.isin(body, (_BODY, _SELECTED, _BOULDER, _CHARGE, _MATERIAL))
    labels, count = ndimage.label(sprite)
    if count == 0:
        return None
    offsets: set[tuple[int, int]] = set()
    boxes: list[tuple[slice, slice]] = []
    for slices in ndimage.find_objects(labels):
        if slices is None:
            continue
        boxes.append(slices)
        offsets.add((slices[0].start % _T, slices[1].start % _T))
    if len(offsets) != 1:
        return None
    orow, ocol = offsets.pop()
    tile_h = (63 - orow) // _T
    tile_w = (64 - ocol) // _T

    def tile_of(r: int, c: int) -> tuple[int, int] | None:
        if r < orow or c < ocol:
            return None
        tr, tc = (r - orow) // _T, (c - ocol) // _T
        if tr >= tile_h or tc >= tile_w:
            return None
        return tr, tc

    # --- drivable objects: tiles fully made of {14, 0, 4, 5} pixels.
    objects: list[_Obj] = []
    object_px = np.zeros_like(body, dtype=bool)
    emask = (body == _BODY) | (body == _SELECTED)
    elabels, _ = ndimage.label(emask)
    selected_seen = 0
    for index, slices in enumerate(ndimage.find_objects(elabels), start=1):
        if slices is None:
            continue
        sy, sx = slices
        # Component tiles: every tile any 14/0 pixel touches must be a full
        # object tile (all nine pixels in the sprite palette).
        comp_tiles: set[tuple[int, int]] = set()
        for r, c in zip(*np.nonzero(elabels[sy, sx] == index), strict=True):
            t = tile_of(int(r) + sy.start, int(c) + sx.start)
            if t is None:
                return None
            comp_tiles.add(t)
        for tr, tc in comp_tiles:
            window = body[orow + _T * tr : orow + _T * tr + _T, ocol + _T * tc : ocol + _T * tc + _T]
            if not np.isin(window, (_BODY, _SELECTED, _DESELECTED, _NEVER)).all():
                return None
        # Deselected/never patches (4/5 pixels inside the component tiles)
        # seed their objects; ASSUMPTION (see module docstring): a patch
        # touches exactly its object's tiles, so object tiles = patch tiles.
        claimed: set[tuple[int, int]] = set()
        for tr, tc in sorted(comp_tiles):
            window = body[orow + _T * tr : orow + _T * tr + _T, ocol + _T * tc : ocol + _T * tc + _T]
            for pr, pc in zip(*np.nonzero(np.isin(window, (_DESELECTED, _NEVER))), strict=True):
                colour = int(window[pr, pc])
                # gather the whole patch component around this pixel
                patch_tiles = {(tr, tc)}
                stack = [(orow + _T * tr + int(pr), ocol + _T * tc + int(pc))]
                seen_px = set(stack)
                while stack:
                    r, c = stack.pop()
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = r + dr, c + dc
                        if (nr, nc) in seen_px or not (0 <= nr < 63 and 0 <= nc < 64):
                            continue
                        if int(body[nr, nc]) == colour:
                            t = tile_of(nr, nc)
                            if t is None or t not in comp_tiles:
                                return None
                            seen_px.add((nr, nc))
                            patch_tiles.add(t)
                            stack.append((nr, nc))
                if patch_tiles & claimed:
                    continue  # already parsed as part of this object
                trs = sorted({t[0] for t in patch_tiles})
                tcs = sorted({t[1] for t in patch_tiles})
                if trs != list(range(trs[0], trs[-1] + 1)) or tcs != list(
                    range(tcs[0], tcs[-1] + 1)
                ):
                    return None
                rect = {(a, b) for a in trs for b in tcs}
                if rect != patch_tiles or not rect <= comp_tiles:
                    return None
                if not _check_drive_rect(body, orow, ocol, trs, tcs, colour):
                    return None
                claimed |= rect
                anchor = (orow + _T * trs[0], ocol + _T * tcs[0])
                tiles = frozenset((a - trs[0], b - tcs[0]) for a, b in rect)
                objects.append(
                    _Obj(
                        kind="drive",
                        anchor=anchor,
                        tiles=tiles,
                        shape=tuple(sorted(tiles)),
                        sel=colour,
                    )
                )
        rest = comp_tiles - claimed
        if rest:
            # The remainder must be exactly the (single) selected object.
            trs = sorted({t[0] for t in rest})
            tcs = sorted({t[1] for t in rest})
            rect = {(a, b) for a in range(trs[0], trs[-1] + 1) for b in range(tcs[0], tcs[-1] + 1)}
            if rect != rest or len(trs) > 2 or len(tcs) > 2:
                return None  # ASSUMPTION: <= 2x2 tiles per drivable object
            if not _check_drive_rect(body, orow, ocol, trs, tcs, _SELECTED):
                return None
            selected_seen += 1
            anchor = (orow + _T * trs[0], ocol + _T * tcs[0])
            tiles = frozenset((a - trs[0], b - tcs[0]) for a, b in rect)
            objects.append(
                _Obj(
                    kind="drive",
                    anchor=anchor,
                    tiles=tiles,
                    shape=tuple(sorted(tiles)),
                    sel=_SELECTED,
                )
            )
        for tr, tc in comp_tiles:
            object_px[orow + _T * tr : orow + _T * tr + _T, ocol + _T * tc : ocol + _T * tc + _T] = True
    if selected_seen > 1 or not any(o.kind == "drive" for o in objects):
        return None

    # --- boulders: colour-11 blobs, exact unions of lattice tiles.
    blabels, _ = ndimage.label(body == _BOULDER)
    for index, slices in enumerate(ndimage.find_objects(blabels), start=1):
        if slices is None:
            continue
        sy, sx = slices
        tiles_set: set[tuple[int, int]] = set()
        for r, c in zip(*np.nonzero(blabels[sy, sx] == index), strict=True):
            t = tile_of(int(r) + sy.start, int(c) + sx.start)
            if t is None:
                return None
            tiles_set.add(t)
        for tr, tc in tiles_set:
            window = body[orow + _T * tr : orow + _T * tr + _T, ocol + _T * tc : ocol + _T * tc + _T]
            if not (window == _BOULDER).all():
                return None
            object_px[orow + _T * tr : orow + _T * tr + _T, ocol + _T * tc : ocol + _T * tc + _T] = True
        trs = min(t[0] for t in tiles_set)
        tcs = min(t[1] for t in tiles_set)
        tiles = frozenset((a - trs, b - tcs) for a, b in tiles_set)
        objects.append(
            _Obj(
                kind="boulder",
                anchor=(orow + _T * trs, ocol + _T * tcs),
                tiles=tiles,
                shape=tuple(sorted(tiles)),
            )
        )

    # --- geysers: solid 12/13 rectangles with a one-face charge readout.
    glabels, _ = ndimage.label(np.isin(body, (_CHARGE, _MATERIAL)))
    for index, slices in enumerate(ndimage.find_objects(glabels), start=1):
        if slices is None:
            continue
        sy, sx = slices
        h, w = sy.stop - sy.start, sx.stop - sx.start
        window = body[sy, sx]
        if h % _T or w % _T or not np.isin(window, (_CHARGE, _MATERIAL)).any():
            return None
        if not (glabels[sy, sx] == index).all():
            return None
        if tile_of(sy.start, sx.start) is None or tile_of(sy.stop - 1, sx.stop - 1) is None:
            return None
        charged = window == _CHARGE
        fill, fill_dir, period = _read_charge(charged, h, w)
        if fill is None:
            return None
        object_px[sy, sx] = True
        tiles = frozenset((a, b) for a in range(h // _T) for b in range(w // _T))
        objects.append(
            _Obj(
                kind="geyser",
                anchor=(sy.start, sx.start),
                tiles=tiles,
                shape=tuple(sorted(tiles)),
                fill=fill,
                fill_dir=fill_dir,
                period=period,
            )
        )

    # --- base sanity: everything outside objects is floor/wall/membrane/4.
    base_vals = body[~object_px]
    if not np.isin(base_vals, (_FLOOR, _WALL, _SLOT, _MEMBRANE)).all():
        return None

    # --- slots: ring-of-4 placements of the dockable shapes.
    slots = _find_slots(body, object_px, orow, ocol, objects)
    if slots is None or not slots:
        return None
    # Shape bijection: each slot shape needs at least as many dockable
    # objects of that shape as there are slots of it.
    from collections import Counter

    slot_shapes = Counter(shape for _, shape in slots)
    obj_shapes = Counter(o.shape for o in objects if o.kind in ("drive", "boulder"))
    for shape, needed in slot_shapes.items():
        if obj_shapes.get(shape, 0) < needed:
            return None

    return SlotParse(
        lattice=(orow, ocol),
        objects=objects,
        slots=slots,
        body=body.copy(),
        timer_pixels=n4,
    )


def _check_drive_rect(
    body: NDArray[np.int16], orow: int, ocol: int, trs: list[int], tcs: list[int], patch: int
) -> bool:
    """Pixel-level check of one drivable rectangle: centre patch uniform in
    ``patch``, everything else body-coloured (0 allowed only when selected,
    for the measured contact-edge recolouring)."""

    r0, c0 = orow + _T * trs[0], ocol + _T * tcs[0]
    h, w = _T * len(trs), _T * len(tcs)
    window = body[r0 : r0 + h, c0 : c0 + w]
    pr0, pr1 = _patch_span(h)
    pc0, pc1 = _patch_span(w)
    patch_px = window[pr0 : pr1 + 1, pc0 : pc1 + 1]
    if not (patch_px == patch).all():
        return False
    mask = np.ones((h, w), dtype=bool)
    mask[pr0 : pr1 + 1, pc0 : pc1 + 1] = False
    others = window[mask]
    if patch == _SELECTED:
        return bool(np.isin(others, (_BODY, _SELECTED)).all())
    return bool((others == _BODY).all())


def _read_charge(
    charged: NDArray[np.bool_], h: int, w: int
) -> tuple[int | None, tuple[int, int] | None, int | None]:
    """Charge count, beam direction and period from a geyser's 12-pattern.

    The charge grows as full pixel-lines from one face; the beam fires from
    the OPPOSITE face (measured: L5 stack charged top-down and fired down;
    L6 floor block charged bottom-up and fired up; L5's 3x3 charged
    right-to-left and its band was leftward).
    """

    n = int(charged.sum())
    if n == 0:
        # Fully discharged: the beam axis is unreadable, but for a square
        # block the period equals the extent regardless of the axis (all
        # measured blocks are square: 6x6 and 3x3).
        return 0, None, (h if h == w else None)
    rows_full = charged.all(axis=1)
    cols_full = charged.all(axis=0)
    k = n // w
    if k * w == n and rows_full[:k].all() and not charged[k:].any():
        return k, (1, 0), h  # charged from the top -> fires down
    if k * w == n and rows_full[h - k :].all() and not charged[: h - k].any():
        return k, (-1, 0), h  # charged from the bottom -> fires up
    k = n // h
    if k * h == n and cols_full[:k].all() and not charged[:, k:].any():
        return k, (0, 1), w  # charged from the left -> fires right
    if k * h == n and cols_full[w - k :].all() and not charged[:, : w - k].any():
        return k, (0, -1), w  # charged from the right -> fires left
    return None, None, None


def _ring_of(shape_px: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """The 1-pixel 8-connected outline around a pixel shape."""

    ring: set[tuple[int, int]] = set()
    for r, c in shape_px:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if (r + dr, c + dc) not in shape_px:
                    ring.add((r + dr, c + dc))
    return ring


def _find_slots(
    body: NDArray[np.int16],
    object_px: NDArray[np.bool_],
    orow: int,
    ocol: int,
    objects: list[_Obj],
) -> list[tuple[tuple[int, int], tuple[tuple[int, int], ...]]] | None:
    """Slot interiors: lattice placements of dockable shapes whose outline
    pixels are all visible-4 or object-occluded (>= 1 visible), and whose
    interior pixels are floor or object-occluded.  Every visible 4 pixel
    must be explained by exactly this set of rings, else abstain."""

    from scipy import ndimage

    vis4 = (body == _SLOT) & ~object_px
    if not vis4.any():
        return None
    shapes = {o.shape for o in objects if o.kind in ("drive", "boulder")}
    explained = np.zeros_like(vis4)
    slots: list[tuple[tuple[int, int], tuple[tuple[int, int], ...]]] = []
    seen_anchors: set[tuple[tuple[int, int], tuple[tuple[int, int], ...]]] = set()
    labels, _ = ndimage.label(vis4, structure=np.ones((3, 3), dtype=bool))
    boxes = [s for s in ndimage.find_objects(labels) if s is not None]
    for shape in shapes:
        shape_px_base = {
            (_T * tr + i, _T * tc + j) for tr, tc in shape for i in range(_T) for j in range(_T)
        }
        ring_base = _ring_of(shape_px_base)
        hmin = min(r for r, _ in ring_base)
        hmax = max(r for r, _ in ring_base)
        wmin = min(c for _, c in ring_base)
        wmax = max(c for _, c in ring_base)
        for sy, sx in boxes:
            # candidate anchors: ring bbox must contain the 4-component bbox
            for ar in range(sy.stop - 1 - hmax, sy.start - hmin + 1):
                if (ar - orow) % _T:
                    continue
                for ac in range(sx.stop - 1 - wmax, sx.start - wmin + 1):
                    if (ac - ocol) % _T:
                        continue
                    anchor = (ar, ac)
                    if (anchor, tuple(sorted(shape))) in seen_anchors:
                        continue
                    ok = True
                    any_vis = False
                    for r, c in ring_base:
                        rr, cc = ar + r, ac + c
                        if not (0 <= rr < 63 and 0 <= cc < 64):
                            ok = False
                            break
                        if vis4[rr, cc]:
                            any_vis = True
                        elif not object_px[rr, cc]:
                            ok = False
                            break
                    if not ok or not any_vis:
                        continue
                    for r, c in shape_px_base:
                        rr, cc = ar + r, ac + c
                        if not (0 <= rr < 63 and 0 <= cc < 64):
                            ok = False
                            break
                        if not object_px[rr, cc] and body[rr, cc] != _FLOOR:
                            ok = False
                            break
                    if not ok:
                        continue
                    seen_anchors.add((anchor, tuple(sorted(shape))))
                    slots.append((anchor, tuple(sorted(shape))))
                    for r, c in ring_base:
                        rr, cc = ar + r, ac + c
                        if 0 <= rr < 63 and 0 <= cc < 64:
                            explained[rr, cc] = True
    if (vis4 & ~explained).any():
        return None
    return slots


# ------------------------------------------------------------- world model


class _World:
    """Bitboard physics + planner for one parsed board.

    Tiles are indexed ``tr * tw + tc`` into python ints; walls, membranes
    and the frame margin are precomputed masks, so a whole-object collision
    test is a single AND.
    """

    def __init__(self, parse: SlotParse):
        orow, ocol = parse.lattice
        self.orow, self.ocol = orow, ocol
        self.th = (63 - orow) // _T
        self.tw = (64 - ocol) // _T
        th, tw = self.th, self.tw
        body = parse.body
        wall = np.zeros((th, tw), dtype=bool)
        memb = np.zeros((th, tw), dtype=bool)
        for tr in range(th):
            for tc in range(tw):
                window = body[orow + _T * tr : orow + _T * tr + _T, ocol + _T * tc : ocol + _T * tc + _T]
                wall[tr, tc] = bool((window == _WALL).any())
                memb[tr, tc] = bool((window == _MEMBRANE).any())
        # Margin pixels outside the tile grid: treat any wall/membrane there
        # as bordering walls (objects can never overlap the margin anyway).
        self.wall_bits = self._pack(wall)
        self.memb_bits = self._pack(memb)
        self.full = (1 << (th * tw)) - 1
        self.left_col = sum(1 << (tr * tw) for tr in range(th))
        self.right_col = self.left_col << (tw - 1)
        self.top_row = (1 << tw) - 1
        self.bot_row = self.top_row << ((th - 1) * tw)

        self.kinds: list[str] = []
        self.shapes: list[tuple[tuple[int, int], ...]] = []
        self.base_masks: list[int] = []  # shape at tile (0, 0)
        self.periods: list[int | None] = []
        self.fill0: list[int] = []
        self.beam_dirs: list[tuple[int, int] | None] = []
        anchors: list[tuple[int, int]] = []
        sel_idx = None
        for i, o in enumerate(parse.objects):
            self.kinds.append(o.kind)
            self.shapes.append(o.shape)
            self.base_masks.append(sum(1 << (a * tw + b) for a, b in o.tiles))
            self.periods.append(o.period)
            self.fill0.append(o.fill or 0)
            self.beam_dirs.append(o.fill_dir)
            anchors.append(((o.anchor[0] - orow) // _T, (o.anchor[1] - ocol) // _T))
            if o.kind == "drive" and o.sel == _SELECTED:
                sel_idx = i
        self.n = len(self.kinds)
        self.slot_masks: list[int] = []
        self.slot_shapes: list[tuple[tuple[int, int], ...]] = []
        self.slot_anchors: list[tuple[int, int]] = []
        for (ar, ac), shape in parse.slots:
            tr, tc = (ar - orow) // _T, (ac - ocol) // _T
            self.slot_masks.append(sum(1 << ((tr + a) * tw + (tc + b)) for a, b in shape))
            self.slot_shapes.append(shape)
            self.slot_anchors.append((tr, tc))
        cycle = 1
        for p in self.periods:
            if p:
                cycle = cycle * p // gcd(cycle, p)
        self.cycle = cycle
        self.has_geysers = any(k == "geyser" for k in self.kinds)
        self.state0 = (tuple(anchors), sel_idx, 0)

    def _pack(self, arr: NDArray[np.bool_]) -> int:
        bits = 0
        for tr, tc in zip(*np.nonzero(arr), strict=True):
            bits |= 1 << (int(tr) * self.tw + int(tc))
        return bits

    # -- mask helpers ----------------------------------------------------

    def mask_at(self, idx: int, anchor: tuple[int, int]) -> int:
        return self.base_masks[idx] << (anchor[0] * self.tw + anchor[1])

    def shift(self, mask: int, d: tuple[int, int]) -> int | None:
        """Shift a mask one tile; None when it would leave the grid."""

        if d == (-1, 0):
            if mask & self.top_row:
                return None
            return mask >> self.tw
        if d == (1, 0):
            if mask & self.bot_row:
                return None
            return mask << self.tw
        if d == (0, -1):
            if mask & self.left_col:
                return None
            return mask >> 1
        if mask & self.right_col:
            return None
        return mask << 1

    def _masks(self, anchors: tuple[tuple[int, int], ...]) -> list[int]:
        return [self.mask_at(i, a) for i, a in enumerate(anchors)]

    # -- physics ---------------------------------------------------------

    def _advance(
        self,
        anchors: list[tuple[int, int]],
        masks: list[int],
        j: int,
        d: tuple[int, int],
        depth: int = 0,
    ) -> bool:
        """Bulldoze object ``j`` one tile along ``d``, recursively pushing
        whatever occupies its way.  Membranes never stop a plowed object
        (it is airborne); walls and the frame edge do."""

        if depth > self.n:
            return False
        nxt = self.shift(masks[j], d)
        if nxt is None or (nxt & self.wall_bits):
            return False
        for k in range(self.n):
            if k != j and masks[k] & nxt and not self._advance(anchors, masks, k, d, depth + 1):
                return False
        masks[j] = nxt
        anchors[j] = (anchors[j][0] + d[0], anchors[j][1] + d[1])
        return True

    def _launch(
        self,
        anchors: list[tuple[int, int]],
        masks: list[int],
        idx: int,
        d: tuple[int, int],
        base: int,
    ) -> bool:
        """Fly object ``idx``: ``base`` tiles, extended while it overlaps a
        membrane, stopping early (whole tiles) when the next step would
        cross a wall or wedge a plowed object, retreating clear of any
        membrane if stopped mid-overlap.  Objects in the path are bulldozed
        ahead tile-by-tile, so they end adjacent beyond the landing
        (measured L7 frame 258: the launched geyser plowed parked P from
        three tiles inside the path to adjacent past the landing).  Returns
        False only when the physics wedges irrecoverably."""

        pos = masks[idx]
        steps = 0
        moved: set[int] = set()
        while steps < base or (pos & self.memb_bits):
            nxt = self.shift(pos, d)
            stopped = nxt is None or (nxt & self.wall_bits)
            if not stopped:
                blockers = [j for j in range(self.n) if j != idx and masks[j] & nxt]
                blockers.sort(key=lambda j: -(anchors[j][0] * d[0] + anchors[j][1] * d[1]))
                for j in blockers:
                    if masks[j] & nxt and not self._advance(anchors, masks, j, d):
                        stopped = True
                        break
                    moved.add(j)
            if stopped:
                while (pos & self.memb_bits) and steps > 0:
                    back = self.shift(pos, (-d[0], -d[1]))
                    if back is None:
                        return False
                    pos = back
                    steps -= 1
                break
            pos = nxt
            steps += 1
            if steps > _MAX_FLIGHT:
                break
        if pos & self.memb_bits:
            return False  # wedged inside a membrane: not physical
        masks[idx] = pos
        anchors[idx] = (anchors[idx][0] + d[0] * steps, anchors[idx][1] + d[1] * steps)
        # A deposited object may not rest overlapping a membrane: extend it
        # (and anything ahead of it) forward until clear.
        for j in sorted(moved, key=lambda j: -(anchors[j][0] * d[0] + anchors[j][1] * d[1])):
            guard = 0
            while masks[j] & self.memb_bits:
                if not self._advance(anchors, masks, j, d):
                    return False
                guard += 1
                if guard > _MAX_FLIGHT:
                    return False
        return True

    def step(
        self, state: tuple[tuple[tuple[int, int], ...], int | None, int], action: int
    ) -> tuple[tuple[tuple[int, int], ...], int | None, int] | None:
        """Apply one action.  Clicks are select-object-``x`` pseudo-actions
        encoded as ``10 + index``.  Returns None for a pruned edge."""

        anchors_t, sel, t = state
        anchors = list(anchors_t)
        if action >= 10:
            idx = action - 10
            if self.kinds[idx] != "drive" or idx == sel:
                return None
            return (tuple(anchors), idx, t)  # clicks do not tick the clock
        d = _DIRS[action]
        masks = self._masks(tuple(anchors))
        if sel is not None:
            tgt = self.shift(masks[sel], d)
            others = 0
            for j in range(self.n):
                if j != sel:
                    others |= masks[j]
            if tgt is None:
                pass  # blocked at the frame edge; still ticks the clock
            elif tgt & others:
                contacted = [j for j in range(self.n) if j != sel and masks[j] & tgt]
                contacted.sort(key=lambda j: -(anchors[j][0] * d[0] + anchors[j][1] * d[1]))
                for j in contacted:
                    if not self._launch(anchors, masks, j, d, _PUSH_TILES):
                        return None
            elif tgt & (self.wall_bits | self.memb_bits):
                pass  # blocked; still ticks the clock (measured, L5 probe)
            else:
                masks[sel] = tgt
                anchors[sel] = (anchors[sel][0] + d[0], anchors[sel][1] + d[1])
        t2 = t + 1
        # geyser beams at every charge wrap
        for g in range(self.n):
            period = self.periods[g]
            if not period or (self.fill0[g] + t2) % period:
                continue
            bd = self.beam_dirs[g]
            if bd is None:
                continue  # unknown direction: planner never relies on it
            band = 0
            cur = masks[g]
            stop = self.wall_bits | self.memb_bits
            for _ in range(self.th + self.tw):
                nxt = self.shift(cur, bd)
                if nxt is None:
                    break
                cur = nxt & ~stop
                if not cur:
                    break
                band |= cur
            hit = sorted(
                (j for j in range(self.n) if j != g and masks[j] & band),
                key=lambda j: -(anchors[j][0] * bd[0] + anchors[j][1] * bd[1]),
            )
            for j in hit:
                # an earlier launch may have plowed this object out of band
                if masks[j] & band and not self._launch(anchors, masks, j, bd, _BEAM_TILES):
                    return None
        return (tuple(anchors), sel, t2)

    # -- goal ------------------------------------------------------------

    def docked(self, state: tuple[tuple[tuple[int, int], ...], int | None, int]) -> bool:
        anchors, _, _ = state
        for mask, shape in zip(self.slot_masks, self.slot_shapes, strict=True):
            if not any(
                self.kinds[i] in ("drive", "boulder")
                and self.shapes[i] == shape
                and self.mask_at(i, anchors[i]) == mask
                for i in range(self.n)
            ):
                return False
        return True

    # -- planner ---------------------------------------------------------

    def _heuristic(self, anchors: tuple[tuple[int, int], ...]) -> int:
        h = 0
        for (star, stac), shape in zip(self.slot_anchors, self.slot_shapes, strict=True):
            best = None
            for i in range(self.n):
                if self.kinds[i] not in ("drive", "boulder") or self.shapes[i] != shape:
                    continue
                ar, ac = anchors[i]
                dist = max(abs(ar - star), abs(ac - stac))
                if best is None or dist < best:
                    best = dist
            if best is None:
                return 1 << 20
            if best:
                h += 1 + (best - 1) // _PUSH_TILES
        return h

    def _encode(self, state: tuple[tuple[tuple[int, int], ...], int | None, int]) -> int:
        anchors, sel, t = state
        key = (t % self.cycle) | ((0 if sel is None else sel + 1) << 5)
        shift = 10
        for tr, tc in anchors:
            key |= (tr | (tc << 5)) << shift
            shift += 10
        return key

    def _decode(self, key: int) -> tuple[tuple[tuple[int, int], ...], int | None, int]:
        t = key & 0x1F
        sel = (key >> 5) & 0x1F
        anchors = []
        shift = 10
        for _ in range(self.n):
            packed = (key >> shift) & 0x3FF
            anchors.append((packed & 0x1F, packed >> 5))
            shift += 10
        return (tuple(anchors), None if sel == 0 else sel - 1, t)

    def plan(
        self, ladder: tuple[tuple[int, int], ...] = ((4, 200_000), (8, 1_600_000))
    ) -> list[tuple[int, tuple[tuple[tuple[int, int], ...], int | None, int]]] | None:
        """Weighted A* to the all-docked goal; [(action, state_after)] or
        None.  The ladder escalates the heuristic weight with the node
        budget: w=4 finds near-shortest plans on the small boards, w=8 is
        what cracks the 4-driver and finale boards within budget (measured
        2026-09-28: all seven ka59 levels, worst 928k nodes / ~25 s).
        Blocked drives are legal waits only on geyser boards; clicks switch
        the driven object.  States are packed to ints to bound RAM."""

        if self.n > 30 or self.cycle > 31 or self.th > 31 or self.tw > 31:
            return None  # outside the packing bounds; abstain over mis-planning
        for weight, max_nodes in ladder:
            actions = self._plan_once(weight, max_nodes)
            if actions is not None:
                path: list[tuple[int, Any]] = []
                state = self.state0
                for action in actions:
                    nstate = self.step(state, action)
                    if nstate is None:
                        return None  # cannot happen for a returned plan
                    path.append((action, nstate))
                    state = nstate
                return path
        return None

    def _plan_once(self, weight: int, max_nodes: int) -> list[int] | None:
        start = (self.state0[0], self.state0[1], self.state0[2] % self.cycle)
        if self.docked(start):
            return []
        clicks = [10 + i for i in range(self.n) if self.kinds[i] == "drive"]
        key0 = self._encode(start)
        gscore = {key0: 0}
        came: dict[int, tuple[int, int]] = {}
        counter = 0
        heap = [(weight * self._heuristic(start[0]), 0, counter, key0)]
        nodes = 0
        while heap:
            _, g, _, key = heapq.heappop(heap)
            if g > gscore.get(key, 1 << 30):
                continue
            state = self._decode(key)
            if self.docked(state):
                actions: list[int] = []
                walk = key
                while walk != key0:
                    walk, action = came[walk]
                    actions.append(action)
                return actions[::-1]
            if g >= _MAX_PLAN:
                continue
            for action in (1, 2, 3, 4, *clicks):
                nstate = self.step(state, action)
                if nstate is None:
                    continue
                if nstate[0] == state[0] and nstate[1] == state[1] and not self.has_geysers:
                    continue  # pure no-op without a clock to tick
                nkey = self._encode(nstate)
                ng = g + 1
                if ng >= gscore.get(nkey, 1 << 30):
                    continue
                gscore[nkey] = ng
                came[nkey] = (key, action)
                nodes += 1
                if nodes > max_nodes:
                    return None
                counter += 1
                heapq.heappush(
                    heap, (ng + weight * self._heuristic(nstate[0]), ng, counter, nkey)
                )
        return None


# ---------------------------------------------------------------- archetype


class SlotDockArchetype:
    """Parser + time-expanded A* planner for ka59; one step per call."""

    name = "slot_dock"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear all per-life state (called on RESET and level advance)."""

        self._plan: list[tuple[int, Any]] = []
        self._world: _World | None = None
        self._prev_state: Any = None  # the plan state matching the last frame
        self._beam_dir_memory: dict[tuple[int, int], tuple[int, int]] = {}

    # ------------------------------------------------------------- contract

    def match(self, grid: NDArray[np.integer]) -> SlotParse | None:
        return _parse(np.asarray(grid, dtype=np.int16))

    def next_actions(self, parse: SlotParse, grid: NDArray[np.integer]) -> list[Step]:
        del grid  # the parse carries everything derived from the frame
        # Beam-direction memory, keyed by the block's pixel anchor: a fully
        # discharged geyser hides its axis, but an unmoved block keeps the
        # direction it showed earlier in the life.
        for o in parse.objects:
            if o.kind == "geyser" and o.fill_dir is not None:
                self._beam_dir_memory[o.anchor] = o.fill_dir
        parse.objects = [
            _Obj(
                kind=o.kind, anchor=o.anchor, tiles=o.tiles, shape=o.shape,
                fill=o.fill, fill_dir=self._beam_dir_memory.get(o.anchor),
                period=o.period,
            )
            if o.kind == "geyser" and o.fill_dir is None
            else o
            for o in parse.objects
        ]

        world = _World(parse)
        if self._plan and self._world is not None and self._matches(world):
            # The frame is exactly what the cached plan predicted: emit the
            # next step and advance the prediction (old world's indexing).
            action, nstate = self._plan.pop(0)
            step = self._emit(self._world, self._prev_state, action)
            self._prev_state = nstate
            if step is not None:
                return [step]
        # (re)plan from the current frame
        self._plan = []
        self._world = None
        self._prev_state = None
        if any(o.kind == "geyser" and o.fill_dir is None for o in parse.objects):
            # Beam axis unreadable (fully discharged block, no memory):
            # emit one safe probing drive; the next frame's charge lines
            # reveal the axes and the next call plans for real.
            probe = self._probe_step(world)
            return [probe] if probe is not None else []
        path = world.plan()
        if not path:
            return []
        self._world = world
        self._plan = path
        action, nstate = self._plan.pop(0)
        step = self._emit(world, world.state0, action)
        self._prev_state = nstate
        return [step] if step is not None else []

    # ----------------------------------------------------------- internals

    def _matches(self, world: _World) -> bool:
        """Does the freshly parsed world agree with the cached prediction?"""

        old, expected = self._world, self._prev_state
        if old is None or expected is None:
            return False
        if (world.th, world.tw, world.orow, world.ocol) != (
            old.th, old.tw, old.orow, old.ocol,
        ):
            return False
        e_anchors, e_sel, e_t = expected
        want = sorted(
            (old.kinds[i], old.shapes[i], e_anchors[i], i == e_sel)
            for i in range(old.n)
        )
        anchors, sel, _ = world.state0
        have = sorted(
            (world.kinds[i], world.shapes[i], anchors[i], i == sel)
            for i in range(world.n)
        )
        if want != have:
            return False
        # Clock check: every parsed charge must match the prediction, so a
        # swallowed or injected action forces a replan instead of a desync.
        for i in range(world.n):
            if world.kinds[i] != "geyser":
                continue
            for j in range(old.n):
                if (
                    old.kinds[j] == "geyser"
                    and old.shapes[j] == world.shapes[i]
                    and e_anchors[j] == anchors[i]
                ):
                    if old.periods[j] and (
                        (old.fill0[j] + e_t) % old.periods[j] != world.fill0[i]
                    ):
                        return False
                    break
        return True

    def _emit(self, world: _World, state_before: Any, action: int) -> Step | None:
        if action < 10:
            return Step(action=action)
        idx = action - 10
        anchors = state_before[0]
        tr, tc = anchors[idx]
        shape = world.shapes[idx]
        h = (max(a for a, _ in shape) + 1) * _T
        w = (max(b for _, b in shape) + 1) * _T
        r0 = world.orow + _T * tr
        c0 = world.ocol + _T * tc
        pr, _ = _patch_span(h)
        pc, _ = _patch_span(w)
        return Step(action=6, x=c0 + pc, y=r0 + pr)

    def _probe_step(self, world: _World) -> Step | None:
        """A drive that moves the selected object one free tile without
        touching anything, staying out of every possible beam band of the
        discharged blocks; used purely to tick the clock once so the charge
        lines (and with them the beam axes) become readable."""

        anchors, sel, _ = world.state0
        if sel is None:
            return None
        masks = world._masks(anchors)
        occ = 0
        for j in range(world.n):
            if j != sel:
                occ |= masks[j]
        danger = 0
        for g in range(world.n):
            if world.kinds[g] != "geyser":
                continue
            for bd in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                cur = masks[g]
                stop = world.wall_bits | world.memb_bits
                for _ in range(world.th + world.tw):
                    nxt = world.shift(cur, bd)
                    if nxt is None:
                        break
                    cur = nxt & ~stop
                    if not cur:
                        break
                    danger |= cur
        for action, d in _DIRS.items():
            tgt = world.shift(masks[sel], d)
            if tgt is None or tgt & (world.wall_bits | world.memb_bits | occ | danger):
                continue
            return Step(action=action)
        # No fully safe drive: any blocked drive still ticks the clock.
        for action, d in _DIRS.items():
            tgt = world.shift(masks[sel], d)
            if tgt is None or (tgt & (world.wall_bits | world.memb_bits) and not tgt & occ):
                return Step(action=action)
        return None

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "fap_archetype",
            "name": self.name,
            "queued_plan": len(self._plan),
            "fly_content": "none; engineered scaffold",
        }
