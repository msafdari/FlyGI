"""wa30's archetype: warehouse ferry with autonomous porter NPCs.

Everything encoded here is MEASURED in the wa30 dossier
(docs/fap_extension_20260928/wa30/, completion_reports.json entry "wa30")
unless a comment says otherwise. The measured grammar, on a 16x16 grid of
4x4-pixel blocks over background colour 1:

  * row 63 is the timer: 7^k 4^(64-k), ticking right to left; 0 sevens is
    GAME_OVER (terminal, score retained).
  * player = solid colour-14 block with a 4-cell colour-0 strip on the
    FACING edge; rival porters = solid colour-12 blocks, advancing exactly
    one block per player action of any kind (lockstep world tick).
  * boxes = 4x4 blocks with a 9-coloured 2x2 interior; the 12-cell border
    colour is the state: 4 free, 3 marked/just-dropped, 0 held by the
    player, 5 dragged by a rival.
  * docks = block-aligned rectangles with a 1-pixel colour-9 ring and
    colour-2 fill; each covered 4x4 block is one slot. The level completes
    the moment every box sits on a dock slot (a border-3 box counts:
    measured, L1 completed on the final drop with no release step).
  * walls = {1,2}-speckle blocks (accept a carried box pushed into them =
    "plant"; rivals fetch planted boxes from the far side) or solid
    colour-5 blocks (plant untested there -- never targeted).

Measured mechanics the planner relies on (dossier probes 15-21 plus the
169-step verified 0->3 program): arriving adjacent to a box moving toward
it, or bumping into it, marks it (border 4->3) and faces it; action 5 picks
the faced marked box, which then stays glued at its pick-time offset
(player->box) through every subsequent move, leading, trailing or sideways;
5 drops it in place (border->3); moving so the box is no longer faced
releases it (3->4); rivals ignore border-3 boxes; rivals autonomously
ferry released boxes to free dock slots.

This module is ENGINEERED SCAFFOLD, recorded as such per the repository
first principle: no fly neuron computes anything here. Its comparison
evidence is the executor-driven offline run against the dossier's verified
hand programs (target: the 3 levels the dossier verified).

The planner is reactive: ONE step per next_actions call, re-derived from
the current grid every turn, because the world is autonomous (rivals move
on every player action). Per-life state kept on self (cleared in reset()):
the union of dock and speckle-wall cells seen this life (a box covering a
slot hides the slot, so "this box is already delivered" needs the memory of
where slots were; RESET and level advance both rebuild the board, so the
executor's reset() hook keeps the memory honest) and the current
shuffle-wait direction.

ASSUMPTION (labelled, also in WORKLOG): the planner treats dock cells and
walls as impassable for the player (never contradicted in the dossier;
probe16 measured open speckle sockets as impassable), treats an all-2 block
as a dock slot (the interior of a hypothetical >=3-wide dock; never
observed -- all observed dock blocks carry ring pixels), and assumes a
merely-marked never-picked box releases when the player faces away, the
same as a dropped one (measured only for dropped boxes).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

_BG = 1
_SIDE = 64
_B = 4  # block edge, pixels
_COLS = 16  # block columns
_ROWS = 15  # playable block rows; block row 15 = timer strip + wall stubs

# action id -> (drow, dcol), measured (probe drive scripts label 1/2/3/4
# as U/D/L/R and the traces confirm it)
_DIRS = {1: (-1, 0), 2: (1, 0), 3: (0, -1), 4: (0, 1)}
_DIR_ID = {v: k for k, v in _DIRS.items()}

# box border colour -> state
_BOX_STATE = {4: "free", 3: "marked", 0: "held", 5: "dragged"}


@dataclass
class PorterFerryParse:
    """One classified 16x15-block board."""

    player: tuple[int, int]
    facing: tuple[int, int]  # (drow, dcol) of the 0-strip edge
    boxes: dict[tuple[int, int], str]
    dock: frozenset  # visible (= empty) dock slot blocks
    speckle: frozenset  # visible (= empty) speckle wall blocks
    solid: frozenset  # solid colour-5 wall blocks
    rivals: frozenset
    floor: frozenset


def _classify(grid: NDArray[np.int16]):
    """Classify every playable block; None if any block is off-grammar."""

    blocks = grid[: _ROWS * _B].reshape(_ROWS, _B, _COLS, _B).transpose(0, 2, 1, 3)
    mn = blocks.min(axis=(2, 3))
    mx = blocks.max(axis=(2, 3))
    uniform = mn == mx

    player = None
    facing = None
    boxes: dict[tuple[int, int], str] = {}
    dock: set = set()
    speckle: set = set()
    solid: set = set()
    rivals: set = set()
    floor: set = set()

    for r in range(_ROWS):
        for c in range(_COLS):
            if uniform[r, c]:
                v = int(mn[r, c])
                if v == _BG:
                    floor.add((r, c))
                elif v == 12:
                    rivals.add((r, c))
                elif v == 5:
                    solid.add((r, c))
                elif v == 2:
                    # ASSUMPTION: an all-2 block is the interior slot of a
                    # wide dock (never observed; all observed dock blocks
                    # carry ring pixels). Speckle always mixes 1s.
                    dock.add((r, c))
                else:
                    return None
                continue
            blk = blocks[r, c]
            vals = set(int(x) for x in np.unique(blk))
            interior = blk[1:3, 1:3]
            if (interior == 9).all():
                ring = set(int(x) for x in blk.ravel()) - {9}
                if len(ring) == 1:
                    state = _BOX_STATE.get(next(iter(ring)))
                    if state is None:
                        return None
                    boxes[(r, c)] = state
                    continue
                return None
            if vals == {0, 14}:
                if player is not None:
                    return None  # two players: off-grammar
                zeros = blk == 0
                if int(zeros.sum()) != 4:
                    return None
                if zeros[0].all():
                    facing = (-1, 0)
                elif zeros[3].all():
                    facing = (1, 0)
                elif zeros[:, 0].all():
                    facing = (0, -1)
                elif zeros[:, 3].all():
                    facing = (0, 1)
                else:
                    return None
                player = (r, c)
                continue
            if vals <= {1, 2}:
                speckle.add((r, c))
                continue
            if vals <= {2, 9}:
                dock.add((r, c))
                continue
            return None

    # No dock-visibility requirement: when the last box is carried onto the
    # last free slot, every slot is covered and the board shows no dock at
    # all (measured on L1's endgame); the per-life dock memory still knows
    # where the slot is so the drop can be emitted.
    if player is None or not boxes:
        return None
    held = [b for b, s in boxes.items() if s == "held"]
    if len(held) > 1:
        return None
    if held:
        d = (held[0][0] - player[0], held[0][1] - player[1])
        if abs(d[0]) + abs(d[1]) != 1:
            return None  # a held box is glued to the player (measured)
    return PorterFerryParse(
        player=player,
        facing=facing,
        boxes=boxes,
        dock=frozenset(dock),
        speckle=frozenset(speckle),
        solid=frozenset(solid),
        rivals=frozenset(rivals),
        floor=frozenset(floor),
    )


def _bfs_walk(start, passable):
    """Distance and first-move maps over single-cell walking."""

    dist = {start: 0}
    first: dict = {start: None}
    q = deque([start])
    while q:
        p = q.popleft()
        for d in _DIRS.values():
            n = (p[0] + d[0], p[1] + d[1])
            if n in passable and n not in dist:
                dist[n] = dist[p] + 1
                first[n] = first[p] if first[p] is not None else d
                q.append(n)
    return dist, first


def _bfs_pair(start, offset, passable, targets):
    """BFS the rigid player+box pair (box = player + offset).

    A state whose box cell sits on a target is terminal (measured: the box
    enters a dock slot or wall socket and stops there; it never transits
    over one, and the planner never routes it over one). Returns
    (distance, first_move) or None.
    """

    def box_of(p):
        return (p[0] + offset[0], p[1] + offset[1])

    if box_of(start) in targets:
        return (0, None)
    dist = {start: 0}
    first: dict = {start: None}
    q = deque([start])
    while q:
        p = q.popleft()
        for d in _DIRS.values():
            n = (p[0] + d[0], p[1] + d[1])
            if n in dist or n not in passable:
                continue
            nb = box_of(n)
            goal = nb in targets
            if not goal and nb not in passable:
                continue
            dist[n] = dist[p] + 1
            first[n] = first[p] if first[p] is not None else d
            if goal:
                return (dist[n], first[n])
            q.append(n)
    return None


class PorterFerryArchetype:
    """wa30's measured rule: mark, pick, ferry, drop, release; rivals help."""

    name = "porter_ferry"

    def __init__(self) -> None:
        self._dock_seen: set = set()
        self._speckle_seen: set = set()
        self._wait_dir: tuple[int, int] | None = None

    def reset(self) -> None:
        # RESET and level advance both rebuild the board from scratch
        # (measured in probe21), so every remembered cell is stale.
        self._dock_seen.clear()
        self._speckle_seen.clear()
        self._wait_dir = None

    # ------------------------------------------------------------- match

    def match(self, grid: NDArray[np.int16]) -> PorterFerryParse | None:
        g = np.asarray(grid)
        if g.shape != (_SIDE, _SIDE):
            return None
        # Fail-fast signature: the timer row costs 64 comparisons and kills
        # virtually every off-archetype frame before any block work.
        bottom = g[63]
        sevens = int((bottom == 7).sum())
        if sevens < 1:
            return None
        if not ((bottom[:sevens] == 7).all() and (bottom[sevens:] == 4).all()):
            return None
        # Rows 60-62 (the truncated 16th block row) carry floor and wall
        # stubs, and occasionally entities: a rival was measured walking
        # into block row 15 on L4, so the whole entity palette is legal
        # here. Colours outside it (6, 8, 10, 11, 13, 15) never appear.
        if not np.isin(g[60:63], (0, 1, 2, 3, 4, 5, 9, 12, 14)).all():
            return None
        return _classify(g.astype(np.int16, copy=False))

    # ------------------------------------------------------------ planner

    def _planted(self, parse: PorterFerryParse) -> set:
        """Boxes sitting inside a wall (plugs and our plants)."""

        wallish = set(parse.speckle) | set(parse.solid)

        def in_wall(b, extra):
            for a, o in (((-1, 0), (1, 0)), ((0, -1), (0, 1))):
                n1 = (b[0] + a[0], b[1] + a[1])
                n2 = (b[0] + o[0], b[1] + o[1])
                ok1 = n1 in wallish or n1 in extra or not (0 <= n1[0] < _ROWS and 0 <= n1[1] < _COLS)
                ok2 = n2 in wallish or n2 in extra or not (0 <= n2[0] < _ROWS and 0 <= n2[1] < _COLS)
                if ok1 and ok2:
                    return True
            return False

        out = {b for b in parse.boxes if b in self._speckle_seen}
        out |= {b for b in parse.boxes if b not in out and in_wall(b, set())}
        # second pass: two boxes planted side by side in the same wall line
        out |= {b for b in parse.boxes if b not in out and in_wall(b, out)}
        return out

    def _regions(self, parse: PorterFerryParse, done: set):
        """Macro connectivity over floor + movable occupants.

        Rivals and undelivered boxes stand ON floor, so they belong to the
        region for reachability purposes even though they block a single
        step right now.
        """

        cells = set(parse.floor) | set(parse.rivals) | {parse.player}
        cells |= {b for b in parse.boxes if b not in done}
        label: dict = {}
        has_rival: dict = {}
        has_dock: dict = {}
        rid = 0
        for seed in cells:
            if seed in label:
                continue
            rid += 1
            comp = [seed]
            label[seed] = rid
            has_rival[rid] = False
            has_dock[rid] = False
            while comp:
                p = comp.pop()
                if p in parse.rivals:
                    has_rival[rid] = True
                for d in _DIRS.values():
                    n = (p[0] + d[0], p[1] + d[1])
                    if n in parse.dock:
                        has_dock[rid] = True
                    if n in cells and n not in label:
                        label[n] = rid
                        comp.append(n)
        return label, has_rival, has_dock

    def _plant_targets(self, parse: PorterFerryParse, offset, label, has_rival, has_dock):
        """Speckle cells a box may be pushed into with this carry offset.

        Measured rule (probes 18-20): a carried box pushed into an empty
        speckle block is fetchable by a rival on the far side, which ferries
        it to a dock. So a socket is useful iff the far cell (across the
        wall along the push offset) belongs to a region holding at least
        one rival and touching at least one empty dock slot.
        """

        out = set()
        for w in parse.speckle:
            far = (w[0] + offset[0], w[1] + offset[1])
            rid = label.get(far)
            if rid is None:
                continue
            if has_rival.get(rid) and has_dock.get(rid):
                out.add(w)
        return out

    def _step_away(self, parse: PorterFerryParse, walk):
        """Release a faced box: any legal move changes facing and adjacency.

        Prefer a landing cell with no adjacent box so the move does not
        immediately mark another one.
        """

        p = parse.player
        legal = []
        for aid, d in _DIRS.items():
            n = (p[0] + d[0], p[1] + d[1])
            if n in walk:
                near_box = any(
                    (n[0] + e[0], n[1] + e[1]) in parse.boxes for e in _DIRS.values()
                )
                legal.append((near_box, aid))
        if legal:
            legal.sort()
            return [Step(action=legal[0][1])]
        # Boxed in: turn the facing onto a non-box neighbour (a bump into a
        # wall is a measured no-op that still turns the facing).
        for aid, d in _DIRS.items():
            n = (p[0] + d[0], p[1] + d[1])
            if n not in parse.boxes:
                return [Step(action=aid)]
        return []

    def next_actions(
        self, parse: PorterFerryParse, grid: NDArray[np.int16]
    ) -> list[Step]:
        p = parse.player
        self._dock_seen |= parse.dock
        self._speckle_seen |= parse.speckle

        planted = self._planted(parse)
        docked = {b for b in parse.boxes if b in self._dock_seen}
        done = docked | planted
        walk = set(parse.floor)
        label, has_rival, has_dock = self._regions(parse, done)
        dock_targets = set(parse.dock)

        held = [b for b, s in parse.boxes.items() if s == "held"]
        if held:
            return self._act_holding(parse, held[0], walk, label, has_rival, has_dock, dock_targets)
        self._wait_dir = None

        # A just-planted box: still marked, still faced, sitting in its wall
        # socket. Step away so it releases -- rivals ignore border-3 boxes
        # (measured, probe16), so an unreleased plant is never fetched.
        # Docked boxes need no release: a border-3 box on a slot already
        # counts as docked (measured: L1 completed on the final drop), and
        # walking off toward the next task changes the facing anyway.
        faced = (p[0] + parse.facing[0], p[1] + parse.facing[1])
        if parse.boxes.get(faced) == "marked" and faced in planted:
            return self._step_away(parse, walk)

        walk_dist, walk_first = _bfs_walk(p, walk)

        best = None
        # Recovery pre-pass. HYPOTHESIS (labelled, also in WORKLOG): a box
        # that is merely arrival-marked -- faced while walking past, never
        # picked -- does not release when the player faces away (a stuck
        # border-3 planted box was measured on L4 after exactly such a
        # pass-by). Rivals ignore border-3 boxes, so a stuck planted box
        # stalls its level. The recovery uses only measured operations:
        # re-face, pick, drop in place, step away (probe20 measured that
        # drop-then-step-away releases).
        for b in planted:
            if parse.boxes.get(b) != "marked" or b == faced:
                continue
            for d in _DIRS.values():
                q = (b[0] - d[0], b[1] - d[1])
                if q != p and q not in walk_dist:
                    continue
                cost = walk_dist.get(q, 0) + 3
                key = (cost, -1, b, d)
                if best is None or key < best[0]:
                    best = (key, b, d, q)
        for b, s in parse.boxes.items():
            if s not in ("free", "marked") or b in done:
                continue
            for d in _DIRS.values():
                q = (b[0] - d[0], b[1] - d[1])
                if q != p and q not in walk_dist:
                    continue
                passable = walk | {p, q, b}
                res = _bfs_pair(q, d, passable, dock_targets)
                kind = 0  # dock preferred
                if res is None:
                    plant = self._plant_targets(parse, d, label, has_rival, has_dock)
                    if plant:
                        res = _bfs_pair(q, d, passable, plant)
                    kind = 1
                if res is None:
                    continue
                cost = walk_dist.get(q, 0) + 2 + res[0] + kind
                key = (cost, kind, b, d)
                if best is None or key < best[0]:
                    best = (key, b, d, q)

        if best is not None:
            _, b, d, q = best
            if p == q:
                if parse.boxes[b] == "marked" and parse.facing == d:
                    return [Step(action=5)]  # pick the faced marked box
                return [Step(action=_DIR_ID[d])]  # bump: mark + face
            move = walk_first[q]
            return [Step(action=_DIR_ID[move])]

        # Nothing the player can deliver. If undelivered boxes remain
        # anywhere (plugs being extracted, rivals mid-ferry, far-region
        # boxes), idle with 5: measured safe world tick while no box is
        # faced, and the rivals advance one block per action.
        if any(b not in docked for b in parse.boxes):
            if faced in parse.boxes:
                return self._step_away(parse, walk)
            return [Step(action=5)]
        return []

    def _act_holding(self, parse, box, walk, label, has_rival, has_dock, dock_targets):
        p = parse.player
        d = (box[0] - p[0], box[1] - p[1])
        if box in self._dock_seen or box in self._speckle_seen:
            return [Step(action=5)]  # box is on its slot/socket: drop
        passable = walk | {p, box}
        res = _bfs_pair(p, d, passable, dock_targets)
        if res is None:
            plant = self._plant_targets(parse, d, label, has_rival, has_dock)
            if plant:
                res = _bfs_pair(p, d, passable, plant)
        if res is not None and res[1] is not None:
            self._wait_dir = None
            return [Step(action=_DIR_ID[res[1]])]
        # No target right now (e.g. a plug still blocks the socket and the
        # rival is busy): shuffle-wait, carrying. Rivals tick per action, so
        # waiting is just extra actions (measured in probe18).
        if self._wait_dir is not None:
            back = (-self._wait_dir[0], -self._wait_dir[1])
            n = (p[0] + back[0], p[1] + back[1])
            nb = (n[0] + d[0], n[1] + d[1])
            if n in passable and nb in passable:
                self._wait_dir = back
                return [Step(action=_DIR_ID[back])]
        for m in _DIRS.values():
            n = (p[0] + m[0], p[1] + m[1])
            nb = (n[0] + d[0], n[1] + d[1])
            if n in passable and nb in passable:
                self._wait_dir = m
                return [Step(action=_DIR_ID[m])]
        return []

    def describe(self):
        return {
            "kind": "fap_archetype",
            "name": self.name,
            "fly_content": "none; engineered scaffold",
        }
