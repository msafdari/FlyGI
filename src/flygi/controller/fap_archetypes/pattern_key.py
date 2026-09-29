"""ls20's archetype: pattern-key transport through transform devices.

Every mechanic encoded here is MEASURED in the ls20 dossier
(docs/fap_extension_20260928/ls20/NOTES.md) and re-verified against a
fresh 265-frame replay of the dossier's composite program unless a comment
says otherwise.  The board is a maze of 5x5-pixel cells (walls colour 4,
floors colour 3, chrome 5); the MOVER is a 5x5 two-tone key tile (2 rows
colour 12 over 3 rows colour 9) that steps one cell per action (1=up
2=down 3=left 4=right).  It carries a hidden 3x3 binary pattern in an ink
colour, shown in the bottom-left display box (a UI fixture constant across
all measured levels; UI coordinates are game-grammar constants, not
board-instance data).  A 9x9 goal box (border 3, interior 5) shows a 3x3
glyph; driving the key onto the lattice cell centred on the glyph
completes the level, but the entry is GATED: it succeeds only when
carried pattern == glyph pattern AND carried ink == glyph ink (refusal
bumps are free).  Devices transform the key when it lands on their cell:
a rotator (0/1 arrow sprite) applies rot90 clockwise, a shifter (four
colour-0 pixels) applies a fixed measured bijection f that commutes with
rotation, a recolourer (9ee/908/cc8 sprite) advances the ink along
c->9->e->8->c, and a colour-11 ring refills the timer and is consumed.
Colour-1 strips on wall edges fling an entering key away from the strip
until it hits a wall (one action; no chaining over other strips; gated
boxes stop the fling at the partial-overlap cell).  A timer bar (rows
61-62, cols 13-54, colour 11, draining left to right at a per-level rate)
kills the current life when an action is taken on an empty bar; wall
bumps drain it without advancing the world.  From level 5 on, devices
PATROL, advancing one step per successful key move; a collision fires
when the key and the device enter the same cell on the same move
(measured: the L5 rotator pingpongs cols 14-19-24-19 with period 4 and
transformed exactly on co-entry).

This module is ENGINEERED SCAFFOLD, recorded as such per the repository
first principle: no fly neuron computes anything here.  Its comparison
evidence is the executor-driven offline run against the dossier's
verified hand programs (levels 1-5 of the 226-action composite).

Labelled assumptions (each encoded exactly once, at the site it is used):
  * ASSUMPTION(fling-effects): a fling applies device/ring effects at its
    LANDING cell only, not at cells it passes over.  Never contradicted in
    the composite replay; no measured fling crossed or landed on a device
    or ring.  Wrong-case cost: one mispredicted transform, corrected by
    the next re-parse.
  * ASSUMPTION(fling-collision-tick): a fling counts as one action, so a
    patrolling device advances once during it and a collision at the
    landing cell transforms.  Same evidential status and failure cost.
  * ASSUMPTION(unknown-f): the shifter bijection f is known only on the
    measured rotation-closed orbit (NOTES.md pairs); the planner refuses
    to enter a shifter while carrying a pattern outside that domain
    because the result would be unpredictable.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import gcd

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

# ------------------------------------------------- measured grammar constants
_CELL = 5
_WALL = 4
_FLOOR = 3
_CHROME = 5
_STRIP = 1
_KEY_TOP = 12  # colour c
_KEY_BODY = 9
_RING_COLOUR = 11
_INK_NEXT = {12: 9, 9: 14, 14: 8, 8: 12}  # recolourer cycle c->9->e->8->c
_INKS = frozenset(_INK_NEXT)
_TIMER_FULL = 42
_TIMER_ROWS = (61, 62)
_TIMER_COL0, _TIMER_COL1 = 13, 55
_LIVES_COL0, _LIVES_COL1 = 55, 64

# actions 1..4 as pixel steps of one 5px cell
_DIRS: dict[int, tuple[int, int]] = {1: (-5, 0), 2: (5, 0), 3: (0, -5), 4: (0, 5)}

# device sprites: the exact 3x3 centre of a 5x5 floor cell whose remaining
# 16 border pixels are colour 3 (identical in every measured occurrence,
# levels 1-6)
_SPRITE_ROT = ((3, 0, 3), (1, 0, 0), (3, 1, 3))
_SPRITE_SHIFT = ((0, 3, 3), (3, 0, 0), (3, 0, 3))
_SPRITE_INK = ((9, 14, 14), (9, 0, 8), (12, 12, 8))
_SPRITE_RING = ((11, 11, 11), (11, 3, 11), (11, 11, 11))
_SPRITES = {
    _SPRITE_ROT: "rot",
    _SPRITE_SHIFT: "shift",
    _SPRITE_INK: "ink",
    _SPRITE_RING: "ring",
}

_NODE_CAP = 150_000
_MAX_HORIZON = 200
_CYCLE_MAX_PERIOD = 8
_SHUFFLE_TICK_CAP = 60

# ----------------------------------------------------------- pattern algebra
# A pattern is a 9-bit int: bit (3*r + c) set <=> glyph cell (r, c) inked.


def _pat_of(bits: str) -> int:
    """Row-major 9-character 0/1 string -> pattern int."""

    return sum(1 << i for i, ch in enumerate(bits) if ch == "1")


def _rot_cw_one(p: int) -> int:
    out = 0
    for r in range(3):
        for c in range(3):
            if p >> (3 * (2 - c) + r) & 1:
                out |= 1 << (3 * r + c)
    return out


_ROT = tuple(_rot_cw_one(p) for p in range(512))

# Measured shifter pairs (docs/fap_extension_20260928/ls20/NOTES.md): a
# 6-cycle plus two chains, all row-major 9-bit strings.  f commutes with
# rotation (measured there on six pairs; re-checked at import below), so
# the table closes over all four rotations of every measured pair.
_F_MEASURED = (
    ("010110011", "111001101"),
    ("111001101", "110011101"),
    ("110011101", "010010111"),
    ("010010111", "101101111"),
    ("101101111", "011101010"),
    ("011101010", "010110011"),
    ("101110011", "111010010"),
    ("111010010", "111101101"),
    ("101011110", "100111100"),
    ("100111100", "111100111"),
    ("111100111", "010101011"),
)


def _build_f() -> dict[int, int]:
    table: dict[int, int] = {}
    for src, dst in _F_MEASURED:
        a, b = _pat_of(src), _pat_of(dst)
        for _ in range(4):
            if table.setdefault(a, b) != b:
                raise AssertionError("shifter table inconsistent under rotation")
            a, b = _ROT[a], _ROT[b]
    return table


_F = _build_f()


# ------------------------------------------------------------------- parsing


@dataclass
class KeyMazeParse:
    """Everything the planner needs, derived from the current frame only."""

    key: tuple[int, int]
    carried: int
    ink: int
    passable: frozenset[tuple[int, int]]
    devices: dict[tuple[int, int], str]  # 'rot' | 'shift' | 'ink'
    rings: frozenset[tuple[int, int]]
    strips: dict[tuple[int, int], tuple[int, int]]  # entered cell -> push dir
    goals: dict[tuple[int, int], tuple[int, int]]  # goal cell -> (pattern, ink)
    timer: int
    lives: int


def _find_key(grid: NDArray[np.int16]) -> tuple[int, int] | None:
    """The unique 5x5 two-tone key block, via integral images (cheap)."""

    top = (grid == _KEY_TOP).astype(np.int32)
    body = (grid == _KEY_BODY).astype(np.int32)
    it = np.zeros((65, 65), np.int32)
    ib = np.zeros((65, 65), np.int32)
    it[1:, 1:] = top.cumsum(0).cumsum(1)
    ib[1:, 1:] = body.cumsum(0).cumsum(1)

    def _rect(ii: NDArray[np.int32], r0: int, r1: int) -> NDArray[np.int32]:
        # window sums over rows r+r0..r+r1-1, cols c..c+4, r/c in [0, 60)
        return (
            ii[r1 : r1 + 60, 5:65]
            - ii[r0 : r0 + 60, 5:65]
            - ii[r1 : r1 + 60, 0:60]
            + ii[r0 : r0 + 60, 0:60]
        )

    hits = np.argwhere((_rect(it, 0, 2) == 10) & (_rect(ib, 2, 5) == 15))
    if len(hits) != 1:
        return None
    return int(hits[0][0]), int(hits[0][1])


def _read_display(grid: NDArray[np.int16]) -> tuple[int, int] | None:
    """Carried pattern and ink from the bottom-left display box (UI fixture:
    frame rows 52-63 cols 0-11, glyph at 2px/cell in rows 55-60, cols 3-8)."""

    if not (
        (grid[52, 0:12] == _WALL).all()
        and (grid[63, 0:12] == _WALL).all()
        and (grid[53:63, 0] == _WALL).all()
        and (grid[53:63, 11] == _WALL).all()
    ):
        return None
    if not np.isin(grid[53:63, 1:11], (_CHROME, 12, 9, 14, 8)).all():
        return None
    pattern = 0
    inks: set[int] = set()
    for i, r in enumerate((55, 57, 59)):
        for j, c in enumerate((3, 5, 7)):
            block = grid[r : r + 2, c : c + 2]
            v = int(block[0, 0])
            if not (block == v).all():
                return None
            if v != _CHROME:
                if v not in _INKS:
                    return None
                inks.add(v)
                pattern |= 1 << (3 * i + j)
    if pattern == 0 or len(inks) != 1:
        return None
    return pattern, inks.pop()


def _read_timer(grid: NDArray[np.int16]) -> int | None:
    """Remaining columns: the bar drains left to right (drained pixels
    render colour 3), so the live part is a right-anchored colour-11 run."""

    row = grid[_TIMER_ROWS[0], _TIMER_COL0:_TIMER_COL1]
    if not (grid[_TIMER_ROWS[1], _TIMER_COL0:_TIMER_COL1] == row).all():
        return None
    n = int((row == _RING_COLOUR).sum())
    drained = _TIMER_FULL - n
    if not ((row[:drained] == _FLOOR).all() and (row[drained:] == _RING_COLOUR).all()):
        return None
    return n


def _read_lives(grid: NDArray[np.int16]) -> int | None:
    """2x2 colour-8 blocks in rows 61-62, cols 55-63 (two pixels per row
    per life)."""

    row = grid[_TIMER_ROWS[0], _LIVES_COL0:_LIVES_COL1]
    if not (grid[_TIMER_ROWS[1], _LIVES_COL0:_LIVES_COL1] == row).all():
        return None
    if not np.isin(row, (_CHROME, 8)).all():
        return None
    n8 = int((row == 8).sum())
    if n8 % 2:
        return None
    return n8 // 2


def _find_goal_boxes(
    grid: NDArray[np.int16], kr: int, kc: int
) -> dict[tuple[int, int], tuple[int, int]] | None:
    """9x9 boxes: border colour 3, inner ring colour 5, non-empty single-ink
    3x3 glyph whose centre coincides with a key-lattice cell centre.

    The key's own 5x5 footprint is treated as a wildcard: when the key
    stands on a partial-overlap cell it covers part of the box border
    (measured on the composite replay, L1 frames 11-12), and the box must
    still parse or the archetype would abstain during the final approach."""

    keymask = np.zeros_like(grid, dtype=bool)
    keymask[kr : kr + _CELL, kc : kc + _CELL] = True
    floor_ok = (grid == _FLOOR) | keymask
    chrome_ok = (grid == _CHROME) | keymask
    cand = (
        floor_ok[0:56, 0:56]
        & floor_ok[0:56, 8:64]
        & floor_ok[8:64, 0:56]
        & floor_ok[8:64, 8:64]
        & chrome_ok[1:57, 1:57]
        & chrome_ok[7:63, 7:63]
    )
    goals: dict[tuple[int, int], tuple[int, int]] = {}
    for r, c in zip(*np.nonzero(cand)):
        r, c = int(r), int(c)
        blk_ok = floor_ok[r : r + 9, c : c + 9]
        border = np.concatenate(
            [blk_ok[0], blk_ok[8], blk_ok[1:8, 0], blk_ok[1:8, 8]]
        )
        if not border.all():
            continue
        inner = chrome_ok[r + 1 : r + 8, c + 1 : c + 8]
        ring = np.concatenate([inner[0], inner[6], inner[1:6, 0], inner[1:6, 6]])
        if not ring.all():
            continue
        if keymask[r + 3 : r + 6, c + 3 : c + 6].any():
            continue  # glyph unreadable under the key: not usable this frame
        glyph = grid[r + 3 : r + 6, c + 3 : c + 6]
        inks = set(int(v) for v in glyph.ravel()) - {_CHROME}
        if len(inks) != 1 or not inks <= _INKS:
            continue  # empty or malformed glyph: not a live goal box
        if (r + 4) % _CELL != (kr + 2) % _CELL or (c + 4) % _CELL != (kc + 2) % _CELL:
            continue  # not aligned to the key lattice: not this game's box
        ink = inks.pop()
        pattern = 0
        for i in range(3):
            for j in range(3):
                if int(glyph[i, j]) != _CHROME:
                    pattern |= 1 << (3 * i + j)
        cell = (r + 2, c + 2)
        if cell in goals:
            return None  # two boxes on one cell: outside the measured grammar
        goals[cell] = (pattern, ink)
    return goals


def _classify_cells(
    grid: NDArray[np.int16],
    key: tuple[int, int],
    goals: dict[tuple[int, int], tuple[int, int]],
) -> tuple[
    frozenset[tuple[int, int]],
    dict[tuple[int, int], str],
    frozenset[tuple[int, int]],
    dict[tuple[int, int], tuple[int, int]],
    int,
] | None:
    """Classify every lattice cell; None = a structure outside the grammar.

    A cell is enterable exactly when its 5x5 block holds no wall pixel;
    box-overlap cells ("partial overlap cells next to the box are always
    enterable", measured) then fall out as plain passable cells, and cells
    mixing wall with box or chrome pixels fall out as walls."""

    kr, kc = key
    passable: set[tuple[int, int]] = set()
    devices: dict[tuple[int, int], str] = {}
    rings: set[tuple[int, int]] = set()
    strip_walls: list[tuple[tuple[int, int], tuple[int, int]]] = []
    wall_count = 0
    plain_ok = frozenset({_FLOOR, _CHROME}) | _INKS
    for R in range(kr % _CELL, 60, _CELL):
        for C in range(kc % _CELL, 60, _CELL):
            blk = grid[R : R + _CELL, C : C + _CELL]
            vals = set(int(v) for v in np.unique(blk))
            cell = (R, C)
            if _WALL in vals:
                if _STRIP in vals:
                    if not vals <= {_STRIP, _WALL}:
                        return None
                    allowed = np.zeros((_CELL, _CELL), bool)
                    for edge, push in (
                        ((0, slice(None)), (-_CELL, 0)),
                        ((4, slice(None)), (_CELL, 0)),
                        ((slice(None), 0), (0, -_CELL)),
                        ((slice(None), 4), (0, _CELL)),
                    ):
                        if (blk[edge] == _STRIP).all():
                            allowed[edge] = True
                            strip_walls.append(((R + push[0], C + push[1]), push))
                    if ((blk == _STRIP) != allowed).any():
                        return None  # stray colour-1 pixels: unknown structure
                elif not vals <= {_FLOOR, _WALL, _CHROME}:
                    return None
                wall_count += 1
                continue
            if cell == (kr, kc):
                passable.add(cell)
                continue
            if cell in goals:
                continue  # gated: never freely passable
            centre = tuple(tuple(int(v) for v in row) for row in blk[1:4, 1:4])
            ring16 = np.concatenate([blk[0], blk[4], blk[1:4, 0], blk[1:4, 4]])
            kind = _SPRITES.get(centre)
            if kind is not None and (ring16 == _FLOOR).all():
                passable.add(cell)
                if kind == "ring":
                    rings.add(cell)
                else:
                    devices[cell] = kind
                continue
            if not vals <= plain_ok:
                return None  # unknown sprite or stray colour: abstain
            passable.add(cell)
    strips: dict[tuple[int, int], tuple[int, int]] = {}
    for target, push in strip_walls:
        if target in passable or target in goals:
            if target in strips:
                return None  # two strips on one cell: outside measured grammar
            strips[target] = push
    return frozenset(passable), devices, frozenset(rings), strips, wall_count


def _parse(grid: NDArray[np.int16]) -> KeyMazeParse | None:
    """Strict structural parse; None = abstain.  The cheap census and key
    gates run first because this path executes on every turn of every game
    when the archetype is seated."""

    if grid.shape != (64, 64):
        return None
    if int(grid.min()) < 0 or int(grid.max()) > 15:
        return None
    census = np.bincount(grid.ravel().astype(np.int64), minlength=16)
    if (
        census[_KEY_TOP] < 10
        or census[_KEY_BODY] < 15
        or census[_WALL] < 150
        or census[_FLOOR] < 30
        or census[_CHROME] < 100
    ):
        return None
    key = _find_key(grid)
    if key is None:
        return None
    if not (grid[0:52, 0:4] == _CHROME).all():  # left chrome margin, all levels
        return None
    display = _read_display(grid)
    if display is None:
        return None
    timer = _read_timer(grid)
    lives = _read_lives(grid)
    if timer is None or lives is None:
        return None
    goals = _find_goal_boxes(grid, key[0], key[1])
    if not goals:
        return None
    cells = _classify_cells(grid, key, goals)
    if cells is None:
        return None
    passable, devices, rings, strips, wall_count = cells
    if wall_count < 12 or len(passable) < 6:
        return None
    carried, ink = display
    return KeyMazeParse(
        key=key,
        carried=carried,
        ink=ink,
        passable=passable,
        devices=devices,
        rings=rings,
        strips=strips,
        goals=goals,
        timer=timer,
        lives=lives,
    )


# ------------------------------------------------------------ world stepping


@dataclass
class _World:
    """The planner's transition model over one parsed board.

    ``mover_at(j)`` gives {cell: kind} for confirmed patrolling devices j
    successful moves from now; ``statics`` holds everything believed
    stationary; ``avoid`` holds cells owned by movers whose cycle is not
    yet confirmed (entering them could apply an unpredictable transform).
    """

    passable: frozenset[tuple[int, int]]
    goals: dict[tuple[int, int], tuple[int, int]]
    strips: dict[tuple[int, int], tuple[int, int]]
    rings: frozenset[tuple[int, int]]
    statics: dict[tuple[int, int], str]
    movers: list[tuple[str, list[tuple[int, int]]]] = field(default_factory=list)
    avoid: frozenset[tuple[int, int]] = frozenset()
    rate: int = 1

    def mover_at(self, j: int) -> dict[tuple[int, int], str]:
        out: dict[tuple[int, int], str] = {}
        for kind, future in self.movers:
            out[future[j % len(future)]] = kind
        return out


def _resolve_fling(
    world: _World, cell: tuple[int, int], push: tuple[int, int]
) -> tuple[int, int]:
    """Slide from an entered strip cell until a wall or a gated box blocks.
    Measured: one action, no chaining over other strips; door gates stop
    the fling at the partial-overlap cell."""

    r, c = cell
    dr, dc = push
    for _ in range(16):
        nxt = (r + dr, c + dc)
        if nxt not in world.passable or nxt in world.goals:
            break
        r, c = nxt
    return (r, c)


def _step(
    world: _World,
    cell: tuple[int, int],
    pat: int,
    ink: int,
    rings: frozenset[tuple[int, int]],
    timer: int,
    j: int,
    action: int,
):
    """One planned action from tick offset j.  Returns None (not takable),
    'win' (a matching gated entry), or the successor state tuple
    (cell, pattern, ink, rings-left, timer)."""

    if timer < 1:
        return None  # acting on an empty bar is death (measured)
    dr, dc = _DIRS[action]
    target = (cell[0] + dr, cell[1] + dc)
    if target in world.goals:
        if world.goals[target] == (pat, ink):
            return "win"
        return None  # a refusal bump is free but useless inside a plan
    if target not in world.passable:
        return None  # planned wall bumps only waste timer
    land = target
    if target in world.strips:
        # ASSUMPTION(fling-effects) + ASSUMPTION(fling-collision-tick):
        # the effects below apply at the landing cell only, after one tick.
        land = _resolve_fling(world, target, world.strips[target])
    if land in world.avoid:
        return None  # unconfirmed mover territory: unpredictable transform
    kind = world.statics.get(land) or world.mover_at(j + 1).get(land)
    if kind == "rot":
        pat = _ROT[pat]
    elif kind == "shift":
        nxt = _F.get(pat)
        if nxt is None:
            return None  # ASSUMPTION(unknown-f): refuse unpredictable result
        pat = nxt
    elif kind == "ink":
        ink = _INK_NEXT[ink]
    if land in rings:
        rings = rings - {land}
        timer = _TIMER_FULL
    else:
        timer = max(timer - world.rate, 0)
    return (land, pat, ink, rings, timer)


def _plan_route(
    world: _World,
    key: tuple[int, int],
    pat: int,
    ink: int,
    timer: int,
) -> list[tuple[int, tuple | str]] | None:
    """BFS over (cell, pattern, ink, rings-left, patrol phase), shortest in
    actions, dominated on remaining timer.  Returns [(action, state_after)]
    ending with (action, 'win') for the gated entry, or None."""

    period = 1
    for _, future in world.movers:
        period = period * len(future) // gcd(period, len(future))
    period = min(period, 24)
    root = (key, pat, ink, world.rings, timer)
    entries: list[tuple[int, int, tuple]] = [(-1, 0, root)]
    best: dict[tuple, int] = {(key, pat, ink, world.rings, 0): timer}
    queue: deque[tuple[int, int]] = deque([(0, 0)])  # (entry index, tick offset)
    while queue:
        idx, j = queue.popleft()
        cell, cpat, cink, crings, ctimer = entries[idx][2]
        if j >= _MAX_HORIZON:
            continue
        for action in (1, 2, 3, 4):
            nxt = _step(world, cell, cpat, cink, crings, ctimer, j, action)
            if nxt is None:
                continue
            if nxt == "win":
                seq: list[tuple[int, tuple | str]] = [(action, "win")]
                walk = idx
                while entries[walk][0] >= 0:
                    parent, act, state = entries[walk]
                    seq.append((act, state))
                    walk = parent
                seq.reverse()
                return seq
            dkey = (nxt[0], nxt[1], nxt[2], nxt[3], (j + 1) % period)
            if best.get(dkey, -1) >= nxt[4]:
                continue
            best[dkey] = nxt[4]
            entries.append((idx, action, nxt))
            if len(entries) > _NODE_CAP:
                return None
            queue.append((len(entries) - 1, j + 1))
    return None


# ------------------------------------------------------------- patrol memory


def _detect_cycle(hist: list[tuple[int, int]]) -> int | None:
    """Smallest period P (1..8) explaining a per-tick position history, or
    None while unconfirmed.  Requires at least P+2 samples, so a pingpong
    (measured: L5 rotator, cols 14-19-24-19, period 4) confirms from six
    observations."""

    n = len(hist)
    for period in range(1, _CYCLE_MAX_PERIOD + 1):
        if n < period + 2:
            return None
        if all(hist[i] == hist[i - period] for i in range(period, n)):
            return period
    return None


class PatternKeyArchetype:
    """Parser + BFS planner for the pattern-key maze; one step per call.

    The world advances only on successful key moves, but from level 5 the
    devices patrol, so the archetype re-parses and re-plans every turn
    (single-step emissions) with a plan cache that skips the BFS while a
    re-simulation of the remaining plan still wins from the observed
    state.  Per-life state on self (cleared in reset()): the
    successful-move tick, the measured timer drain rate, per-device
    position histories (a device hidden under the key is carried through
    the gap), and the cached plan."""

    name = "pattern_key"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear all per-life state (called on RESET and level advance)."""

        self._tick = 0
        self._rate: int | None = None
        self._prev: dict | None = None
        self._trackers: list[dict] = []
        self._plan: list[int] = []
        self._shuffle_from: tuple[int, int] | None = None

    # ------------------------------------------------------------- contract

    def match(self, grid: NDArray[np.integer]) -> KeyMazeParse | None:
        return _parse(np.asarray(grid, dtype=np.int16))

    def next_actions(
        self, parse: KeyMazeParse, grid: NDArray[np.integer]
    ) -> list[Step]:
        del grid  # the parse carries everything derived from the frame
        self._update_life_state(parse)
        world = self._world_model(parse)
        if self._plan and self._plan_wins(world, parse, self._plan):
            return [Step(action=self._plan.pop(0))]
        self._plan = []
        route = _plan_route(world, parse.key, parse.carried, parse.ink, parse.timer)
        if route is None:
            return self._no_plan_fallback(parse, world)
        self._plan = [action for action, _ in route]
        return [Step(action=self._plan.pop(0))]

    # ---------------------------------------------------------- plan cache

    def _plan_wins(self, world: _World, parse: KeyMazeParse, actions: list[int]) -> bool:
        """The cached plan survives only while re-simulating its remaining
        actions from the OBSERVED state, under the CURRENT device model,
        still ends in the winning gated entry.  This invalidates the plan
        the moment reality diverges (a missed transform, a mispredicted
        drain, a device newly revealed as a patroller) at the cost of a
        replay whose length is bounded by the plan."""

        state = (parse.key, parse.carried, parse.ink, parse.rings, parse.timer)
        for j, action in enumerate(actions):
            out = _step(world, *state, j, action)
            if out == "win":
                return j == len(actions) - 1
            if out is None:
                return False
            state = out
        return False

    # ------------------------------------------------------ per-life memory

    def _update_life_state(self, parse: KeyMazeParse) -> None:
        prev = self._prev
        self._prev = {
            "key": parse.key,
            "timer": parse.timer,
            "lives": parse.lives,
            "rings": parse.rings,
            "goals": frozenset(parse.goals),
            "carried": parse.carried,
            "ink": parse.ink,
        }
        if prev is None:
            self._observe_devices(parse)
            return
        if (
            parse.lives < prev["lives"]
            or frozenset(parse.goals) != prev["goals"]
            or (parse.timer > prev["timer"] and parse.rings >= prev["rings"])
        ):
            # A death restores the board (timer refills with no ring spent,
            # a life disappears); a level advance replaces the goal set.
            # Either way every per-life belief is stale.
            self._tick = 0
            self._rate = None
            self._trackers = []
            self._plan = []
            self._shuffle_from = None
            self._observe_devices(parse)
            return
        if parse.key != prev["key"]:
            self._tick += 1
            if parse.rings == prev["rings"] and prev["timer"] > parse.timer:
                drained = prev["timer"] - parse.timer
                if 1 <= drained <= 4:
                    self._rate = drained  # measured per-level drain rate
            self._observe_devices(parse)
        # An unmoved key means a bump or a swallowed step: the world is
        # frozen (measured), so device histories gain nothing this turn.

    def _observe_devices(self, parse: KeyMazeParse) -> None:
        seen = dict(parse.devices)
        for tracker in self._trackers:
            last = tracker["hist"][-1]
            candidate = None
            for cell, kind in seen.items():
                if kind != tracker["kind"]:
                    continue
                dist = abs(cell[0] - last[0]) + abs(cell[1] - last[1])
                if dist <= 2 * _CELL and (candidate is None or dist < candidate[1]):
                    candidate = (cell, dist)
            if candidate is not None:
                tracker["hist"].append(candidate[0])
                del seen[candidate[0]]
            elif abs(parse.key[0] - last[0]) + abs(parse.key[1] - last[1]) <= _CELL:
                # Hidden under the key: the collision cell is its position.
                tracker["hist"].append(parse.key)
            else:
                tracker["hist"].append(last)
            if len(tracker["hist"]) > 4 * _CYCLE_MAX_PERIOD:
                del tracker["hist"][0]
        for cell, kind in seen.items():
            self._trackers.append({"kind": kind, "hist": [cell]})

    def _world_model(self, parse: KeyMazeParse) -> _World:
        statics: dict[tuple[int, int], str] = {}
        movers: list[tuple[str, list[tuple[int, int]]]] = []
        avoid: set[tuple[int, int]] = set()
        for tracker in self._trackers:
            hist = tracker["hist"]
            if all(h == hist[0] for h in hist):
                statics[hist[-1]] = tracker["kind"]
                continue
            period = _detect_cycle(hist)
            if period is None or period == 1:
                avoid.update(hist)
                last = hist[-1]
                for dr, dc in _DIRS.values():
                    avoid.add((last[0] + dr, last[1] + dc))
                continue
            n = len(hist)
            # pos(now + j) continues the periodic history: representative
            # index inside the last full period window [n-period, n-1].
            future = [
                hist[n - period + ((period - 1 + j) % period)]
                for j in range(period)
            ]
            movers.append((tracker["kind"], future))
        return _World(
            passable=parse.passable,
            goals=parse.goals,
            strips=parse.strips,
            rings=parse.rings,
            statics=statics,
            movers=movers,
            avoid=frozenset(avoid),
            rate=self._rate if self._rate is not None else 1,
        )

    def _no_plan_fallback(self, parse: KeyMazeParse, world: _World) -> list[Step]:
        """No route: shuffle on safe floor while unconfirmed movers reveal
        their cycles; otherwise abstain honestly and let the host act."""

        if not world.avoid or self._tick > _SHUFFLE_TICK_CAP:
            return []
        if parse.timer <= 4 * world.rate:
            return []
        neighbours = []
        for action, (dr, dc) in _DIRS.items():
            cell = (parse.key[0] + dr, parse.key[1] + dc)
            if (
                cell in world.passable
                and cell not in world.avoid
                and cell not in world.statics
                and cell not in world.strips
                and cell not in world.rings
            ):
                neighbours.append((action, cell))
        if not neighbours:
            return []
        for action, cell in neighbours:
            if cell == self._shuffle_from:
                self._shuffle_from = parse.key
                return [Step(action=action)]
        self._shuffle_from = parse.key
        return [Step(action=neighbours[0][0])]
