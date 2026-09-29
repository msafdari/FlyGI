"""su15's archetype: merge creatures up a size ladder and deliver to discs.

Every mechanic encoded here is MEASURED in the su15 dossier
(docs/fap_extension_20260928/su15/NOTES.md) or re-measured against the
dossier's verified 97-action L1-L7 replay (frame-by-frame component diffs,
2026-09-28) unless a comment says otherwise:

* header rows 0-9 are a colour-4 band holding a stage-legend panel
  (background-5 rectangles of 2x2 chips, absent on level 1) and the GOAL
  DISPLAY: exact k x k squares of ladder colours, one per shape to build,
  plus decorative glyphs (colour-7 predator zigzag, colour-14 diamond);
* the board (rows 10-62, background 5) holds creatures -- solid squares on
  a size ladder 1x1 c10 / 2x2 c6 / 3x3 c15 / 4x4 c11 / 5x5 c12 / 7x7 c8,
  masses 1/2/4/8/16/32 -- plus 69-cell colour-9 discs (9x9 bbox, row
  widths 5,7,9,9,9,9,9,7,5; level 1 carves a colour-3 socket+entrance out
  of the same pattern), colour-7 predators (8 cells in a 4x5 bbox, drawn
  partially when overlapping), and inert decoration (colour-3 path dashes,
  a colour-0 waypoint diamond, transient colour-14 move trails);
* row 63 is a timer: colour-0 cells consumed right-to-left into colour 5;
* click semantics (measured): >= 2 same-stage creatures with centres
  within Euclidean 8.00 of the click all fuse into one next-stage creature
  AT the click (third same-stage wheels at 8.06+ are excluded); otherwise
  the single nearest creature within its move range relocates to the click
  (measured caps 7.91 / 8.49 / 8.86 for 2x2 / 3x3 / 4x4); landings within
  ~7-8 of another creature are refused (world freezes, timer penalty);
  odd sizes centre on the click, even sizes land with the click at cell
  (size/2, size/2) of the footprint; a click beyond every creature's range
  moves nothing but still ticks the world (the L6 wait mechanic);
* predators hunt the nearest creature at ~4 cells per click (occasional
  longer pounces), eat 1x1s, degrade larger creatures one stage on contact
  and fling the remnant; the player's move resolves before predator moves;
* a level completes the instant every goal shape overlaps a distinct disc
  (partial overlap suffices); some discs are decoys (measured L6: the SE
  disc does not complete) -- discovered only by docking and observing the
  level persist, which this planner recovers from by re-targeting.

This module is ENGINEERED SCAFFOLD, recorded as such per the repository
first principle: no fly neuron computes anything here.  Its comparison
evidence is the executor-driven offline run against the dossier's verified
hand programs (target 7/7 levels).

The planner is a greedy per-turn re-planner (one Step per call, because
predators move autonomously between our clicks): parse the frame, allocate
creatures to displayed goals (direct match, else a same-stage pairwise
merge tree over smaller creatures, else wait for a predator to chew a
bigger creature down), then emit the single most urgent click -- protect
threatened allocated pieces, fire ready merges, approach far pairs, march
finished shapes to their discs, and dock everything once every shape is
one hop from its disc.  Board geometry is re-derived from the CURRENT
frame on every call; nothing level-specific is stored in this file.

ASSUMPTION (labelled, greppable): a 1x1 creature's move range was never
measured (the verified programs always found 1x1 pairs within merge
reach); _MOVE_CAP assumes ~6.0.  A refused click is detected by the world
freezing (board unchanged outside the timer row) and that exact click is
banned for the rest of the life, so a wrong cap costs one click, not a
loop.  ASSUMPTION: the wait-click safety radius treats >= 12 as beyond
every creature's move range; the 7x7's cap is only bounded below (11.2
in, 41 observed not to move), so wait points prefer the farthest corner.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import cos, hypot, pi, sin
from typing import Any

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

_BG = 5
_HEADER_BG = 4
_DISC = 9
_PRED = 7
_BOARD_TOP = 10
_BOARD_BOTTOM = 63  # exclusive

_SIZES = (1, 2, 3, 4, 5, 7)  # stage 1..6
_COLOURS = (10, 6, 15, 11, 12, 8)
_SIZE_OF_STAGE = {s + 1: size for s, size in enumerate(_SIZES)}
_STAGE_OF_COLOUR = {c: s + 1 for s, c in enumerate(_COLOURS)}
_COLOUR_OF_STAGE = {s + 1: c for s, c in enumerate(_COLOURS)}
_MASS = {s: 1 << (s - 1) for s in range(1, 7)}

# Move-range caps, measured minus a rounding margin (2x2 7.91, 3x3 8.49
# routine / 9.2 max, 4x4 8.86, 5x5 8.06 in / 7.6 routine, 7x7 >= 11.2).
# ASSUMPTION: the 1x1 cap (never measured) is ~6.0.
_MOVE_CAP = {1: 6.0, 2: 7.8, 3: 9.0, 4: 8.8, 5: 7.8, 6: 11.0}
_MERGE_IN = 7.75  # both merge targets within this of the click (8.00 in)
_MERGE_OUT = 8.6  # everything else at least this far (8.06 measured out)
_REFUSAL_GAP = 8.25  # landing this close to another creature is refused
_PRED_SAFE = 8.5  # measured sitting-survival gap
_PRED_DANGER = 11.0  # act on an allocated piece once a predator is this close
_WAIT_MIN_GAP = 12.0  # a wait click must be beyond every move cap we use

_HEADER_ALLOWED = frozenset({2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15})
# Colour 2 is a DEAD disc: measured 2026-09-28 (this build's executor run),
# the instant a predator chew made the level's remaining mass insufficient
# for the displayed goal, the disc recoloured 9 -> 2 wholesale.  The parse
# accepts it (the level still has to be played out to the reset); the
# planner's own mass accounting flags the goal as failed independently.
_BOARD_ALLOWED = frozenset({0, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15})
_GLYPH_COLOURS = frozenset({7, 13, 14})  # header decorations, ignored
_DECOR_LIMITS = {0: 6, 3: 2, 13: 8, 14: 8}  # board decor, max cells/component

_DISC_WIDTHS = (5, 7, 9, 9, 9, 9, 9, 7, 5)
_DISC_CELLS = frozenset(
    (dr, dc)
    for dr, w in enumerate(_DISC_WIDTHS)
    for dc in range((9 - w) // 2, (9 - w) // 2 + w)
)  # 69 cells
_DISC_OCCLUDERS = frozenset({0, 3, 7, 13, 14} | set(_COLOURS))
_DISC_COLOURS = (9, 2)  # live disc / dead disc (see _BOARD_ALLOWED note)


@dataclass(frozen=True)
class _Creature:
    stage: int
    size: int
    centre: tuple[float, float]  # (row, col) of the footprint centre
    anchor: tuple[int, int]  # top-left pixel


@dataclass(frozen=True)
class _Disc:
    anchor: tuple[int, int]  # top-left of the 9x9 pattern bbox
    centre: tuple[float, float]
    cells: frozenset[tuple[int, int]]  # absolute pattern cells
    live: bool = True  # False for a colour-2 (dead) disc


@dataclass
class MergeBoardParse:
    """Everything ``next_actions`` needs, derived from one frame."""

    goals: tuple[int, ...]  # stages, descending
    creatures: list[_Creature]
    discs: list[_Disc]
    predators: list[tuple[float, float]]
    timer: int


# ------------------------------------------------------------------ parsing


def _parse(grid: NDArray[np.int16]) -> MergeBoardParse | None:
    """Strict structural parse of the merge-deliver grammar; None = abstain.

    Ordered so the abstain path for foreign games stays cheap: shape, timer
    row, header band and colour censuses run before any component labelling.
    """

    if grid.shape != (64, 64):
        return None
    timer_row = grid[63]
    # Roaming sprites can straddle the timer row (measured: a predator
    # glyph's bottom line, and a flung 1x1's pixel, both overwrote row 63
    # cells mid-level), so board-grammar colours are transparent overlays:
    # the visible {0, 5} cells must still read zeros-then-fives.
    if any(int(v) not in _BOARD_ALLOWED for v in np.unique(timer_row)):
        return None
    visible = timer_row[(timer_row == 0) | (timer_row == _BG)]
    n_timer = int((visible == 0).sum())
    if not (visible[:n_timer] == 0).all() or not (visible[n_timer:] == _BG).all():
        return None
    if not (grid[9] == _HEADER_BG).all():
        return None
    header = grid[:10]
    board = grid[_BOARD_TOP:_BOARD_BOTTOM]
    hvals = np.unique(header)
    if any(int(v) not in _HEADER_ALLOWED for v in hvals):
        return None
    bvals = np.unique(board)
    if any(int(v) not in _BOARD_ALLOWED for v in bvals):
        return None
    if float((board == _BG).mean()) < 0.45:
        return None
    if int((header == _HEADER_BG).sum()) < 200:
        return None

    from scipy import ndimage

    eight = np.ones((3, 3), dtype=bool)

    # --- header: legend chips (5-ring), goal squares (4-ring), glyphs.
    goals: list[int] = []
    for colour in (int(v) for v in hvals):
        if colour in (_HEADER_BG, _BG):
            continue
        labels, count = ndimage.label(header == colour, structure=eight)
        for index, slices in enumerate(ndimage.find_objects(labels), start=1):
            if slices is None:
                continue
            sy, sx = slices
            h, w = sy.stop - sy.start, sx.stop - sx.start
            comp = labels[sy, sx] == index
            square = h == w and bool(comp.all())
            ring_vals = _ring_values(grid, sy.start, sy.stop, sx.start, sx.stop)
            if colour in _STAGE_OF_COLOUR and square:
                if ring_vals <= {_BG} and h == 2:
                    continue  # legend chip
                if ring_vals <= {_HEADER_BG}:
                    stage = _STAGE_OF_COLOUR[colour]
                    if h != _SIZE_OF_STAGE[stage]:
                        return None  # size/colour mismatch: not this grammar
                    goals.append(stage)
                    continue
                return None
            if colour in _GLYPH_COLOURS and ring_vals <= {_HEADER_BG, _BG}:
                continue  # predator zigzag / diamond glyph / late chips
            if colour == 2 and ring_vals <= {_HEADER_BG, _BG}:
                # DEAD display (measured: the goal squares AND the glyphs
                # recolour to 2 the instant the level's remaining mass
                # cannot satisfy the goal).  A goal-sized square keeps its
                # stage (carried by size alone) so the mass accounting
                # flags the level as lost and burns the timer toward the
                # reset; dead glyph shapes are plain decoration.
                if square and h in _SIZES and ring_vals <= {_HEADER_BG}:
                    goals.append(_SIZES.index(h) + 1)
                continue
            return None
    if not goals:
        return None
    goals.sort(reverse=True)

    # --- creatures: exact solid squares of ladder colours.
    creatures: list[_Creature] = []
    board_h = _BOARD_BOTTOM - _BOARD_TOP
    for stage, colour in enumerate(_COLOURS, start=1):
        size = _SIZE_OF_STAGE[stage]
        labels, count = ndimage.label(board == colour)
        for index, slices in enumerate(ndimage.find_objects(labels), start=1):
            if slices is None:
                continue
            sy, sx = slices
            h, w = sy.stop - sy.start, sx.stop - sx.start
            solid = int((labels[sy, sx] == index).sum()) == h * w
            if not (
                solid
                and w == size
                and (
                    h == size
                    # A flung creature can land straddling the timer row
                    # (measured: a chewed b4's remnant at rows 60-63), so a
                    # square clipped by the board's bottom edge still reads
                    # as the full square extending below.
                    or (h < size and sy.stop == board_h)
                )
            ):
                return None
            r0, c0 = sy.start + _BOARD_TOP, sx.start
            creatures.append(
                _Creature(
                    stage=stage,
                    size=size,
                    centre=(r0 + (size - 1) / 2.0, c0 + (size - 1) / 2.0),
                    anchor=(r0, c0),
                )
            )
    if not creatures:
        return None

    # --- predators: small colour-7 blobs (drawn partially when occluded).
    predators: list[tuple[float, float]] = []
    labels, count = ndimage.label(board == _PRED, structure=eight)
    for index, slices in enumerate(ndimage.find_objects(labels), start=1):
        if slices is None:
            continue
        sy, sx = slices
        h, w = sy.stop - sy.start, sx.stop - sx.start
        cells = int((labels[sy, sx] == index).sum())
        # One glyph is 8 cells in 4x5; overlapping hunters fuse into one
        # component (measured: two predators shared (39.5, 37) mid-L5).
        if h > 9 or w > 9 or cells > 20:
            return None
        predators.append(
            (sy.start + _BOARD_TOP + (h - 1) / 2.0, sx.start + (w - 1) / 2.0)
        )

    # --- discs: every colour-9 component must sit inside a placement of
    # the 69-cell disc pattern whose other cells are known occluders.
    discs = _find_discs(grid)
    if discs is None or not discs:
        return None

    # --- decoration bounds: dashes, waypoint diamonds, move trails.
    disc_cells = frozenset().union(*(d.cells for d in discs))
    for colour, limit in _DECOR_LIMITS.items():
        if not (board == colour).any():
            continue
        labels, count = ndimage.label(board == colour, structure=eight)
        for index, slices in enumerate(ndimage.find_objects(labels), start=1):
            if slices is None:
                continue
            sy, sx = slices
            cells = [
                (int(r) + sy.start + _BOARD_TOP, int(c) + sx.start)
                for r, c in zip(*np.nonzero(labels[sy, sx] == index))
            ]
            if all(cell in disc_cells for cell in cells):
                continue  # socket / entrance carved out of a disc
            if len(cells) > limit:
                return None

    return MergeBoardParse(
        goals=tuple(goals),
        creatures=creatures,
        discs=discs,
        predators=predators,
        timer=n_timer,
    )


def _ring_values(
    grid: NDArray[np.int16], r0: int, r1: int, c0: int, c1: int
) -> set[int]:
    """Values of the 1-pixel ring around a bbox, clipped at the frame."""

    rr0, rr1 = max(r0 - 1, 0), min(r1 + 1, grid.shape[0])
    cc0, cc1 = max(c0 - 1, 0), min(c1 + 1, grid.shape[1])
    window = grid[rr0:rr1, cc0:cc1]
    mask = np.ones(window.shape, dtype=bool)
    mask[r0 - rr0 : r0 - rr0 + (r1 - r0), c0 - cc0 : c0 - cc0 + (c1 - c0)] = False
    return {int(v) for v in window[mask]}


def _find_discs(grid: NDArray[np.int16]) -> list[_Disc] | None:
    from scipy import ndimage

    labels, count = ndimage.label(
        np.isin(grid[_BOARD_TOP:_BOARD_BOTTOM], _DISC_COLOURS)
    )
    anchors: set[tuple[int, int]] = set()
    for index, slices in enumerate(ndimage.find_objects(labels), start=1):
        if slices is None:
            continue
        sy = slice(slices[0].start + _BOARD_TOP, slices[0].stop + _BOARD_TOP)
        sx = slices[1]
        cells = {
            (int(r) + sy.start, int(c) + sx.start)
            for r, c in zip(
                *np.nonzero(labels[slices[0], sx] == index)
            )
        }
        best: tuple[int, tuple[int, int]] | None = None
        for ar in range(sy.stop - 9, sy.start + 1):
            for ac in range(sx.stop - 9, sx.start + 1):
                if ar < _BOARD_TOP or ar + 9 > _BOARD_BOTTOM or ac < 0 or ac + 9 > 64:
                    continue
                pattern = {(ar + dr, ac + dc) for dr, dc in _DISC_CELLS}
                if not cells <= pattern:
                    continue
                nines = 0
                ok = True
                for pr, pc in pattern:
                    value = int(grid[pr, pc])
                    if value in _DISC_COLOURS:
                        nines += 1
                    elif value not in _DISC_OCCLUDERS:
                        ok = False
                        break
                if not ok:
                    continue
                if best is None or nines > best[0] or (
                    nines == best[0] and (ar, ac) < best[1]
                ):
                    best = (nines, (ar, ac))
        if best is None:
            return None  # unexplained colour-9 pixels: not this grammar
        anchors.add(best[1])
    discs = []
    for ar, ac in sorted(anchors):
        cells = frozenset((ar + dr, ac + dc) for dr, dc in _DISC_CELLS)
        discs.append(
            _Disc(
                anchor=(ar, ac),
                centre=(ar + 4.0, ac + 4.0),
                cells=cells,
                live=any(int(grid[r, c]) == _DISC for r, c in cells),
            )
        )
    return discs


# ----------------------------------------------------------------- geometry


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def _landing_anchor(size: int, click: tuple[int, int]) -> tuple[int, int]:
    """Top-left of a size x size footprint landed by clicking ``click``.

    Measured: odd sizes centre on the click; even sizes land with the click
    at footprint cell (size/2, size/2) (2x2 bottom-right at click, 4x4
    spanning click-2..click+1)."""

    return (click[0] - size // 2, click[1] - size // 2)


def _landing_centre(size: int, click: tuple[int, int]) -> tuple[float, float]:
    r0, c0 = _landing_anchor(size, click)
    return (r0 + (size - 1) / 2.0, c0 + (size - 1) / 2.0)


def _in_bounds(size: int, click: tuple[int, int]) -> bool:
    r0, c0 = _landing_anchor(size, click)
    return r0 >= _BOARD_TOP and r0 + size <= _BOARD_BOTTOM and c0 >= 0 and c0 + size <= 64


def _footprint(size: int, anchor: tuple[int, int]) -> frozenset[tuple[int, int]]:
    r0, c0 = anchor
    return frozenset((r0 + i, c0 + j) for i in range(size) for j in range(size))


def _overlaps_disc(creature: _Creature, disc: _Disc) -> bool:
    return bool(_footprint(creature.size, creature.anchor) & disc.cells)


def _min_pred_gap(parse: MergeBoardParse, point: tuple[float, float]) -> float:
    if not parse.predators:
        return 1e9
    return min(_dist(point, p) for p in parse.predators)


def _threat_gap(parse: MergeBoardParse, i: int) -> float:
    """Danger distance for creature i: a predator counts only when i is its
    current quarry (predators hunt the NEAREST creature, measured) or when
    it is close enough (<= 6.5) to retarget i within one move."""

    if not parse.predators:
        return 1e9
    centre = parse.creatures[i].centre
    worst = 1e9
    for pred in parse.predators:
        d = _dist(centre, pred)
        target = min(
            range(len(parse.creatures)),
            key=lambda k: (_dist(parse.creatures[k].centre, pred), k),
        )
        if target == i or d <= 6.5:
            worst = min(worst, d)
    return worst


# --------------------------------------------------------------- allocation


def _landing_risk(
    parse: MergeBoardParse,
    exclude: set[int],
    landing: tuple[float, float],
    bait: frozenset[int] = frozenset(),
) -> int:
    """Aggro-aware landing safety (the load-bearing predator mechanic,
    measured 2026-09-28: a piece landing ONE cell nearer to a predator
    than its current quarry steals the aggro and turns a working
    sacrifice into a pursuit).

    Only BAIT creatures (spares, sacrifices, chew targets) count as
    distraction: handing aggro to another allocated piece is not safety
    (measured: a hop that "escaped" by making the build's own F3 the
    nearest prey got that F3 chewed one move later).

    0 = every predator has closer BAIT prey (distracted);
    1 = this landing becomes some predator's quarry, but with room;
    2 = quarry inside the catch band (< _PRED_SAFE);
    3 = collision course (< 4.5) -- veto.
    """

    risk = 0
    for pred in parse.predators:
        d = _dist(landing, pred)
        if d <= 4.5:
            risk = max(risk, 3)
            continue
        others = min(
            (
                _dist(parse.creatures[k].centre, pred)
                for k in bait
                if k not in exclude
            ),
            default=1e9,
        )
        if d < others + 1.0:  # we are (or become) this predator's quarry
            risk = max(risk, 2 if d < _PRED_SAFE else 1)
    return risk


def _allocate(
    parse: MergeBoardParse,
    doomed: frozenset[int] = frozenset(),
) -> list[tuple[str, tuple[int, ...]]]:
    """Assign creatures to displayed goals.

    Returns one entry per goal: ('direct', (i,)), ('build', (i, j, ...)),
    ('wait', (i,)) or ('fail', ()).  The first pass excludes ``doomed``
    creatures (the life's committed sacrifices, held by the archetype so
    the commitment is STICKY -- re-deriving them per turn dissolved the
    measured L5 bait pattern mid-life); if that starves a goal, the
    second pass uses every creature.
    """

    creatures = parse.creatures
    for exclude_doomed in (True, False):
        used: set[int] = set()
        entries: list[tuple[str, tuple[int, ...]]] = []
        failed = False
        for goal in parse.goals:
            pool = [
                i
                for i in range(len(creatures))
                if i not in used and not (exclude_doomed and i in doomed)
            ]
            direct = [i for i in pool if creatures[i].stage == goal]
            if direct:
                pick = min(direct, key=lambda i: _direct_rank(parse, i))
                used.add(pick)
                entries.append(("direct", (pick,)))
                continue
            build = _build_set(creatures, pool, goal)
            if build is not None:
                used.update(build)
                entries.append(("build", tuple(build)))
                continue
            bigger = [
                i
                for i in range(len(creatures))
                if i not in used and creatures[i].stage > goal
            ]
            if bigger and parse.predators:
                pick = min(
                    bigger,
                    key=lambda i: (
                        creatures[i].stage,
                        _min_pred_gap(parse, creatures[i].centre),
                        i,
                    ),
                )
                used.add(pick)
                entries.append(("wait", (pick,)))
                continue
            entries.append(("fail", ()))
            failed = True
        if not failed or not exclude_doomed:
            return entries
    return entries  # pragma: no cover - loop always returns


def _direct_rank(parse: MergeBoardParse, i: int) -> tuple[float, float, int]:
    creature = parse.creatures[i]
    docked = any(_overlaps_disc(creature, d) for d in parse.discs)
    nearest = min(_dist(creature.centre, d.centre) for d in parse.discs)
    return (0.0 if docked else 1.0, nearest, i)


def _build_set(
    creatures: list[_Creature], pool: list[int], goal: int
) -> list[int] | None:
    """Largest-first exact subset of smaller creatures summing to the goal
    mass (powers of two, so largest-first is exact when possible; any
    multiset of powers summing to a power merges pairwise same-stage)."""

    need = _MASS[goal]
    picks: list[int] = []
    for stage in range(goal - 1, 0, -1):
        tier = [i for i in pool if creatures[i].stage == stage]
        while tier and need >= _MASS[stage]:
            if picks:
                cr, cc = (
                    sum(creatures[i].centre[0] for i in picks) / len(picks),
                    sum(creatures[i].centre[1] for i in picks) / len(picks),
                )
                pick = min(
                    tier, key=lambda i: (_dist(creatures[i].centre, (cr, cc)), i)
                )
            else:
                if len(tier) > 1:
                    pick = min(
                        tier,
                        key=lambda i: (
                            min(
                                _dist(creatures[i].centre, creatures[j].centre)
                                for j in tier
                                if j != i
                            ),
                            i,
                        ),
                    )
                else:
                    pick = tier[0]
            tier.remove(pick)
            picks.append(pick)
            need -= _MASS[stage]
    if need:
        return None
    return picks


# ------------------------------------------------------------ click search


def _capture_ok(
    parse: MergeBoardParse,
    click: tuple[int, int],
    participants: set[int],
) -> bool:
    """No unintended capture: every non-participant is at least _MERGE_OUT
    away, and no stage ends up with two non-participants inside the radius
    (which would fire a different merge)."""

    for k, other in enumerate(parse.creatures):
        if k in participants:
            continue
        if _dist(other.centre, click) < _MERGE_OUT:
            return False
    return True


def _merge_click(
    parse: MergeBoardParse,
    i: int,
    j: int,
    banned: set[tuple[int, int]],
    aim: tuple[float, float] | None = None,
    bait: frozenset[int] = frozenset(),
) -> tuple[int, int] | None:
    """A click fusing exactly creatures i and j, or None.

    Landing preference: out of predator reach first (gap >= _PRED_SAFE),
    then compact -- toward ``aim`` (the build's assembly point) so merges
    converge instead of scattering (measured cost of gap-maximising
    placement: pieces pushed into corners, approach distances inflated).
    A landing closer than 4.5 to a predator is vetoed outright; anything
    farther survives the predator's response move (measured: a freshly
    landed b4 at gap 3.6 was not chewed until it SAT a second move) and
    the danger pass moves it next click.
    """

    a, b = parse.creatures[i], parse.creatures[j]
    landing_size = _SIZE_OF_STAGE[a.stage + 1]
    if aim is None:
        aim = ((a.centre[0] + b.centre[0]) / 2, (a.centre[1] + b.centre[1]) / 2)
    r_lo = int(min(a.centre[0], b.centre[0]) - _MERGE_IN)
    r_hi = int(max(a.centre[0], b.centre[0]) + _MERGE_IN) + 1
    c_lo = int(min(a.centre[1], b.centre[1]) - _MERGE_IN)
    c_hi = int(max(a.centre[1], b.centre[1]) + _MERGE_IN) + 1
    for refusal_gap in (_REFUSAL_GAP, 7.0):
        best: tuple[tuple[float, float, float], tuple[int, int]] | None = None
        for r in range(max(r_lo, _BOARD_TOP), min(r_hi, _BOARD_BOTTOM)):
            for c in range(max(c_lo, 0), min(c_hi, 64)):
                click = (r, c)
                if click in banned or not _in_bounds(landing_size, click):
                    continue
                da, db = _dist(a.centre, click), _dist(b.centre, click)
                if da > _MERGE_IN or db > _MERGE_IN:
                    continue
                if not _capture_ok(parse, click, {i, j}):
                    continue
                landing = _landing_centre(landing_size, click)
                risk = _landing_risk(parse, {i, j}, landing, bait)
                if risk >= 3:
                    continue
                if any(
                    _dist(parse.creatures[k].centre, landing) < refusal_gap
                    for k in range(len(parse.creatures))
                    if k not in (i, j)
                ):
                    continue
                score = (
                    -float(risk),
                    -_dist(landing, aim),
                    _min_pred_gap(parse, landing),
                )
                if best is None or score > best[0]:
                    best = (score, click)
        if best is not None:
            return best[1]
    return None


def _hop_click(
    parse: MergeBoardParse,
    i: int,
    target: tuple[float, float],
    banned: set[tuple[int, int]],
    mode: str = "travel",
    bait: frozenset[int] = frozenset(),
) -> tuple[int, int] | None:
    """A click moving exactly creature i toward (or safely near) target.

    Modes: 'travel' makes progress toward target, preferring landings out
    of predator reach; 'flee' escapes a pursuit -- maximise the landing
    gap (capped, so escape beats overshoot), stay off the board edge
    (measured failure: an edge-hugging flee let the hunter herd the piece
    into a corner), then progress; 'orbit' loiters safely near target.
    """

    creature = parse.creatures[i]
    cap = _MOVE_CAP[creature.stage]
    seen: set[tuple[int, int]] = set()
    feasible: list[tuple[tuple[int, int], float, float, float]] = []
    for radius in (cap - 0.1, cap * 0.75, cap * 0.5, 3.0):
        for k in range(32):
            angle = 2 * pi * k / 32
            click = (
                int(round(creature.centre[0] + radius * sin(angle))),
                int(round(creature.centre[1] + radius * cos(angle))),
            )
            if click in seen:
                continue
            seen.add(click)
            if click in banned or not _in_bounds(creature.size, click):
                continue
            d_i = _dist(creature.centre, click)
            if d_i > cap or d_i < 1.0:
                continue
            ok = True
            for k2, other in enumerate(parse.creatures):
                if k2 == i:
                    continue
                d_o = _dist(other.centre, click)
                if d_o < _MERGE_OUT or d_o <= d_i + 0.5:
                    ok = False  # wrong capture or unintended merge risk
                    break
                if _dist(other.centre, _landing_centre(creature.size, click)) < _REFUSAL_GAP:
                    ok = False  # landing would be refused
                    break
            if not ok:
                continue
            r0, c0 = _landing_anchor(creature.size, click)
            edge = min(
                r0 - _BOARD_TOP,
                _BOARD_BOTTOM - 1 - (r0 + creature.size - 1),
                c0,
                63 - (c0 + creature.size - 1),
            )
            landing = _landing_centre(creature.size, click)
            risk = _landing_risk(parse, {i}, landing, bait)
            if risk >= 3:
                continue
            gap = _min_pred_gap(parse, landing)
            feasible.append(
                (click, _dist(landing, target), gap, float(edge), risk)
            )
    if not feasible:
        return None
    if mode == "orbit":
        return min(
            feasible, key=lambda f: (f[4], -min(f[2], 14.0), f[1], f[0])
        )[0]
    if mode == "flee":
        # Lowest risk first, then progress toward the aim with a mild
        # off-the-edge bonus, so a hunted piece converges on its merge
        # partner instead of being herded into a corner (both failure
        # modes measured: gap-first flight scattered pieces to opposite
        # corners; edge-hugging flight let the hunter pin the piece).
        return min(
            feasible,
            key=lambda f: (f[4], f[1] - 0.4 * min(f[3], 4.0), f[0]),
        )[0]
    return min(
        feasible,
        key=lambda f: (f[4], f[1] - 0.2 * min(f[2], 12.0), f[0]),
    )[0]


def _dock_click(
    parse: MergeBoardParse,
    i: int,
    disc: _Disc,
    banned: set[tuple[int, int]],
    reachable_only: bool = True,
    bait: frozenset[int] = frozenset(),
) -> tuple[int, int] | None:
    """A click landing creature i overlapping the disc; best overlap wins."""

    creature = parse.creatures[i]
    cap = _MOVE_CAP[creature.stage]
    ar, ac = disc.anchor
    best: tuple[tuple[float, float, float], tuple[int, int]] | None = None
    for r in range(ar - creature.size, ar + 9 + creature.size):
        for c in range(ac - creature.size, ac + 9 + creature.size):
            click = (r, c)
            if click in banned or not _in_bounds(creature.size, click):
                continue
            d_i = _dist(creature.centre, click)
            if reachable_only and d_i > cap:
                continue
            overlap = len(_footprint(creature.size, _landing_anchor(creature.size, click)) & disc.cells)
            if not overlap:
                continue
            ok = True
            for k2, other in enumerate(parse.creatures):
                if k2 == i:
                    continue
                d_o = _dist(other.centre, click)
                if d_o < _MERGE_OUT or d_o <= d_i + 0.5:
                    ok = False
                    break
                if _dist(other.centre, _landing_centre(creature.size, click)) < _REFUSAL_GAP:
                    ok = False
                    break
            if not ok:
                continue
            landing = _landing_centre(creature.size, click)
            score = (
                float(min(overlap, creature.size * creature.size)),
                -float(_landing_risk(parse, {i}, landing, bait)),
                -_dist(landing, disc.centre),
                _min_pred_gap(parse, landing),
            )
            if best is None or score > best[0]:
                best = (score, click)
    return best[1] if best else None


def _wait_click(
    parse: MergeBoardParse, banned: set[tuple[int, int]]
) -> tuple[int, int] | None:
    """A click beyond every creature's move range: a pure world tick."""

    candidates = [
        (12, 3), (12, 60), (60, 3), (60, 60),
        (12, 32), (60, 32), (36, 3), (36, 60),
    ]
    best: tuple[float, tuple[int, int]] | None = None
    for click in candidates:
        if click in banned:
            continue
        gap = min(_dist(c.centre, click) for c in parse.creatures)
        if gap < _WAIT_MIN_GAP:
            continue
        if best is None or gap > best[0]:
            best = (gap, click)
    return best[1] if best else None


# ---------------------------------------------------------------- archetype


class MergeDeliverArchetype:
    """Parser + greedy per-turn planner for su15; one step per call."""

    name = "merge_deliver"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear all per-life state (called on RESET and level advance)."""

        self._banned: set[tuple[int, int]] = set()
        self._bad_discs: set[tuple[int, tuple[int, int]]] = set()
        self._sacrifices: list[tuple[int, tuple[float, float]]] = []
        self._sacrifices_chosen = False
        self._last_click: tuple[int, int] | None = None
        self._last_key: bytes | None = None
        self.last_reason: str = ""  # debug/telemetry only; no behaviour

    # ------------------------------------------------------------- contract

    def match(self, grid: NDArray[np.integer]) -> MergeBoardParse | None:
        return _parse(np.asarray(grid, dtype=np.int16))

    def next_actions(
        self, parse: MergeBoardParse, grid: NDArray[np.integer]
    ) -> list[Step]:
        frame = np.asarray(grid, dtype=np.int16)
        key = frame[:_BOARD_BOTTOM].tobytes()
        if self._last_click is not None and key == self._last_key:
            # Our click froze the world (refused): never repeat it this life.
            self._banned.add(self._last_click)
        self._last_click = None
        click = self._plan(parse)
        if click is None:
            return []
        self._last_click = click
        self._last_key = key
        return [Step(action=6, x=int(click[1]), y=int(click[0]))]

    # -------------------------------------------------------------- planner

    def _plan(self, parse: MergeBoardParse) -> tuple[int, int] | None:
        creatures = parse.creatures

        # Sticky sacrifices: commit ONCE per life to each predator's
        # opening quarry, then re-identify those creatures by position as
        # the life unfolds.  A sacrifice that is chewed or flung stops
        # matching and simply drops out; nothing new is ever doomed
        # mid-life (measured: per-turn re-derivation dissolved the L5
        # bait pattern and fed the build's own pieces to the hunters).
        if parse.predators and not self._sacrifices_chosen:
            self._sacrifices_chosen = True
            for pred in parse.predators:
                pick = min(
                    range(len(creatures)),
                    key=lambda i: (_dist(creatures[i].centre, pred), i),
                )
                self._sacrifices.append(
                    (creatures[pick].stage, creatures[pick].centre)
                )
        doomed: set[int] = set()
        surviving: list[tuple[int, tuple[float, float]]] = []
        for stage, pos in self._sacrifices:
            match = min(
                (
                    (i, _dist(creatures[i].centre, pos))
                    for i in range(len(creatures))
                    if creatures[i].stage == stage and i not in doomed
                ),
                key=lambda t: (t[1], t[0]),
                default=None,
            )
            if match is not None and match[1] <= 6.0:
                doomed.add(match[0])
                surviving.append((stage, creatures[match[0]].centre))
        self._sacrifices = surviving

        entries = _allocate(parse, frozenset(doomed))

        direct_pieces = [e[1][0] for e in entries if e[0] == "direct"]
        build_sets = [set(e[1]) for e in entries if e[0] == "build"]
        wait_pieces = {e[1][0] for e in entries if e[0] == "wait"}
        wait_pending = bool(wait_pieces)
        used = {i for e in entries for i in e[1]}
        bait = frozenset(
            (set(range(len(creatures))) - used) | wait_pieces
        )

        assignment = self._assign_discs(parse, direct_pieces)

        # Pending same-stage merge pairs, intra-build only.
        pairs: list[tuple[float, int, int, int]] = []  # (dist, stage, i, j)
        for members in build_sets:
            for i, j in combinations(sorted(members), 2):
                if creatures[i].stage == creatures[j].stage:
                    pairs.append(
                        (
                            _dist(creatures[i].centre, creatures[j].centre),
                            creatures[i].stage,
                            i,
                            j,
                        )
                    )

        ready: dict[int, tuple[int, int]] = {}  # piece -> dock click
        for piece in direct_pieces:
            disc = assignment.get(piece)
            if disc is None:
                continue
            if _overlaps_disc(creatures[piece], disc):
                ready[piece] = (-1, -1)  # already docked
                continue
            dock = _dock_click(parse, piece, disc, self._banned, bait=bait)
            if dock is not None:
                ready[piece] = dock
        all_ready = all(p in ready for p in direct_pieces)

        # 1. Danger: protect the most threatened allocated piece.
        protected = [
            i
            for i in set(direct_pieces) | set().union(*build_sets, set())
            if i not in wait_pieces
        ]
        threatened = sorted(
            (
                (_threat_gap(parse, i), i)
                for i in protected
                if _threat_gap(parse, i) <= _PRED_DANGER
            ),
        )
        for _, piece in threatened:
            step = self._protect(
                parse, piece, pairs, build_sets, assignment, ready, all_ready,
                wait_pending, bait,
            )
            if step is not None:
                self.last_reason = f"danger:{piece}"
                return step

        # 2. Ready merges (lowest stage, closest pair first).
        for dist, stage, i, j in sorted(pairs, key=lambda p: (p[1], p[0])):
            if dist <= 2 * _MERGE_IN:
                click = _merge_click(
                    parse, i, j, self._banned,
                    aim=self._pair_aim(parse, build_sets, i, j), bait=bait,
                )
                if click is not None:
                    self.last_reason = f"merge:{i}+{j}"
                    return click

        # 3. Approach the closest pair.  This also covers near-ready pairs
        # whose integer-click merge lens came up empty (measured: two F3s
        # at 15.13 have no integer point within 7.75 of both).
        for dist, stage, i, j in sorted(pairs):
            gap_i = _min_pred_gap(parse, creatures[i].centre)
            gap_j = _min_pred_gap(parse, creatures[j].centre)
            first, second = (i, j) if (gap_i, i) <= (gap_j, j) else (j, i)
            for mover, still in ((first, second), (second, first)):
                click = _hop_click(
                    parse, mover, creatures[still].centre, self._banned, bait=bait
                )
                if click is not None:
                    self.last_reason = f"approach:{mover}->{still}"
                    return click

        # 4. March unfinished direct pieces toward their discs.
        if not all_ready:
            farthest = max(
                (p for p in direct_pieces if p not in ready),
                key=lambda p: (
                    _dist(
                        creatures[p].centre,
                        assignment[p].centre if p in assignment else (36.0, 32.0),
                    ),
                    p,
                ),
                default=None,
            )
            if farthest is not None and farthest in assignment:
                click = _hop_click(
                    parse,
                    farthest,
                    assignment[farthest].centre,
                    self._banned,
                    bait=bait,
                )
                if click is not None:
                    self.last_reason = f"march:{farthest}"
                    return click

        # 5. Everything staged but a chew still pending: tick the world.
        if wait_pending:
            self.last_reason = "wait"
            return _wait_click(parse, self._banned)

        # 6. Dock sequence (most threatened first); the last dock wins.
        undocked = [p for p in direct_pieces if ready.get(p, None) not in (None, (-1, -1))]
        if undocked:
            piece = min(
                undocked,
                key=lambda p: (_min_pred_gap(parse, creatures[p].centre), p),
            )
            self.last_reason = f"dock:{piece}"
            return ready[piece]

        # 7. All docked yet the level persists: a decoy disc (measured L6).
        if direct_pieces and all(ready.get(p) == (-1, -1) for p in direct_pieces):
            for piece in direct_pieces:
                disc = assignment.get(piece)
                if disc is not None:
                    self._bad_discs.add((creatures[piece].stage, disc.anchor))
            assignment = self._assign_discs(parse, direct_pieces)
            for piece in direct_pieces:
                disc = assignment.get(piece)
                if disc is None or _overlaps_disc(creatures[piece], disc):
                    continue
                dock = _dock_click(parse, piece, disc, self._banned, bait=bait)
                if dock is not None:
                    self.last_reason = f"redock:{piece}"
                    return dock
                click = _hop_click(parse, piece, disc.centre, self._banned, bait=bait)
                if click is not None:
                    self.last_reason = f"remarch:{piece}"
                    return click
        # 8. Nothing productive: tick the world if possible (each wait that
        # freezes the board gets banned, so this cannot loop forever).
        self.last_reason = "idle-wait"
        return _wait_click(parse, self._banned)

    def _pair_aim(
        self,
        parse: MergeBoardParse,
        build_sets: list[set[int]],
        i: int,
        j: int,
    ) -> tuple[float, float]:
        """Where a merge of (i, j) should land: the centroid of the rest of
        its build set, or the nearest live disc once the set is exhausted."""

        for members in build_sets:
            if i in members and j in members:
                rest = [k for k in members if k not in (i, j)]
                if rest:
                    return (
                        sum(parse.creatures[k].centre[0] for k in rest) / len(rest),
                        sum(parse.creatures[k].centre[1] for k in rest) / len(rest),
                    )
                break
        mid = (
            (parse.creatures[i].centre[0] + parse.creatures[j].centre[0]) / 2,
            (parse.creatures[i].centre[1] + parse.creatures[j].centre[1]) / 2,
        )
        discs = [d for d in parse.discs if d.live] or parse.discs
        disc = min(discs, key=lambda d: (_dist(mid, d.centre), d.anchor))
        return disc.centre

    def _protect(
        self,
        parse: MergeBoardParse,
        piece: int,
        pairs: list[tuple[float, int, int, int]],
        build_sets: list[set[int]],
        assignment: dict[int, _Disc],
        ready: dict[int, tuple[int, int]],
        all_ready: bool,
        wait_pending: bool,
        bait: frozenset[int],
    ) -> tuple[int, int] | None:
        creatures = parse.creatures
        # A ready merge involving the threatened piece: fuse (the fused
        # creature lands at the click, i.e. the piece moves -- safe).
        for dist, stage, i, j in sorted(pairs, key=lambda p: p[0]):
            if piece in (i, j) and dist <= 2 * _MERGE_IN:
                click = _merge_click(
                    parse, i, j, self._banned,
                    aim=self._pair_aim(parse, build_sets, i, j), bait=bait,
                )
                if click is not None:
                    return click
        if piece in assignment:
            dock = ready.get(piece)
            if dock == (-1, -1):
                return None  # already docked; nothing to protect it with
            if dock is not None and all_ready and not wait_pending:
                landing = _landing_centre(
                    creatures[piece].size, dock
                )
                if _landing_risk(parse, {piece}, landing, bait) <= 2:
                    return dock
            if dock is not None:
                # Staged and threatened: orbit near the disc, stay safe.
                return _hop_click(
                    parse, piece, assignment[piece].centre, self._banned,
                    mode="orbit", bait=bait,
                )
            return _hop_click(
                parse, piece, assignment[piece].centre, self._banned, bait=bait
            )
        # A build member with no ready merge: escape the pursuit band
        # toward its build's assembly point (measured failure of plain
        # partner-chasing: the L4 F3 stayed inside the 8.5-11 band for
        # eight clicks, monopolised every turn and was finally cornered).
        aims: list[tuple[float, float]] = []
        for dist, i, j in sorted(
            (d, i, j) for d, _, i, j in pairs if piece in (i, j)
        ):
            other = j if piece == i else i
            aims.append(creatures[other].centre)
        for members in build_sets:
            if piece in members:
                rest = [k for k in members if k != piece]
                if rest:
                    aims.append(
                        (
                            sum(creatures[k].centre[0] for k in rest) / len(rest),
                            sum(creatures[k].centre[1] for k in rest) / len(rest),
                        )
                    )
                break
        aims.append((36.0, 32.0))
        for aim in aims:
            click = _hop_click(
                parse, piece, aim, self._banned, mode="flee", bait=bait
            )
            if click is not None:
                return click
        return None

    def _assign_discs(
        self, parse: MergeBoardParse, pieces: list[int]
    ) -> dict[int, _Disc]:
        """Greedy global-min matching of goal pieces to distinct discs,
        avoiding discs recorded as decoys for that stage this life."""

        assignment: dict[int, _Disc] = {}
        taken: set[tuple[int, int]] = set()
        remaining = list(pieces)
        for use_bad in (False, True):
            while remaining:
                options = [
                    (
                        _dist(parse.creatures[p].centre, d.centre),
                        p,
                        d,
                    )
                    for p in remaining
                    for d in parse.discs
                    if d.anchor not in taken
                    and (
                        use_bad
                        or (parse.creatures[p].stage, d.anchor) not in self._bad_discs
                    )
                ]
                if not options:
                    break
                _, p, d = min(options, key=lambda o: (o[0], o[1], o[2].anchor))
                assignment[p] = d
                taken.add(d.anchor)
                remaining.remove(p)
            if not remaining:
                break
        return assignment

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "fap_archetype",
            "name": self.name,
            "banned_clicks": len(self._banned),
            "bad_discs": len(self._bad_discs),
            "fly_content": "none; engineered scaffold",
        }
