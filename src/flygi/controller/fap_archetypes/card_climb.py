"""dc22's card-climb archetype: toggle card items, climb onto the b-carrier.

Decoded rules this module implements (dossier: docs/fap_extension_20260928/
dc22/ -- prog_l1/l2/l3.json verified end to end, verify_l123_stdout.txt,
score 0 -> 3):

MEASURED (dossier probes and verified programs):
  * The board is a colour-3 framed 64x64 frame; row 63 is a timer bar
    (colour 3 draining to 0). The interior splits into a FIELD panel
    (background colour 4, left) and a CARD panel (background colour 5,
    right), separated by a dashed colour-0 column pair.
  * The player is a 2x2 colour-14 block. Actions 1/2/3/4 move it exactly
    2 cells up/down/left/right; a refused move changes nothing (the world
    freezes -- probe_quirks_out.txt, and the L1 trace where the verified
    program's net displacement equals 2 cells per arrow).
  * The goal carrier is a 2x2 colour-11 block in the field; stepping the
    player onto it completes the level (L1: the final a1 onto (20,24)
    flipped levels_completed 0 -> 1).
  * Cards are solid-colour blobs in the card panel. Clicking a card
    toggles its item between two FIXED slot rectangles in the field
    (field slot / stack slot, drawn solid when present, sometimes as a
    colour/background checker ghost when absent); a re-click restores the
    board (probe_cards.py, probe_l2/l3 're-click nd' identities).
  * Some levels carry a pair of isolated 2x2 two-colour checker pads and
    a card whose colour belongs to the pad pair: clicking that card while
    the player stands on a pad teleports the player to the other pad
    (solve_l3b.py 'C6 TELEPORT', pads {6,7}).
  * Small item blobs in the field act as pickups: stepping onto one
    materializes a previously invisible card in the card panel
    (l2_after_8card.txt shows the third card visible after the pickup
    descent; l3 cardF appears after 'down onto pickup').
  * The L4 card vocabulary diverges (phase-flip / slide / transmute,
    probe_l4_out.txt); the transmute card is NOT involutive (re-click
    nd=16 after a 40-cell click). The dossier target is therefore the
    3 verified levels; beyond them this planner only proceeds where its
    fingerprints stay involutive, and abstains otherwise.

ASSUMPTION (labelled, per repository rule):
  * Move legality is modelled as "the destination 2x2 is entirely
    non-background". Every destination in the three verified programs
    satisfies it and every checker ghost violates it, but it was never
    exhaustively probed; a per-life refusal memory (one observed frozen
    frame bans that move in that card-state) bounds the harm if some
    non-background colour is unwalkable.
  * Card toggles are assumed independent across cards (fixed slots,
    measured disjoint on L1-L3); overlapping fingerprints drop both cards
    from planning rather than guessing.
  * The teleport is assumed symmetric (either pad -> the other); only the
    L3 direction was measured. A failed teleport click bans that pad for
    the life.

This module is ENGINEERED SCAFFOLD, recorded as such per the repository
first principle: no fly neuron computes anything here. Everything is
derived from the CURRENT grid; the only constants are the grammar colours
and sprite sizes above. Board-instance data (absolute coordinates, level
scripts, game-id checks) is deliberately absent; the dossier's verified
programs are used as test oracle only.

Planner: on a fresh board, fingerprint every visible card (click, diff,
re-click, verify restore), then breadth-first-search over (player
position, card toggle bits) -- moves, card clicks (forbidden while the
player overlaps the card's cells), and pad teleports -- to the carrier.
If the carrier is unreachable, walk to the nearest unexplained small blob
(pickup candidate) instead; a materialized card re-triggers
fingerprinting. One step is emitted per call so every action re-plans
from the real frame.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

# Grammar constants, all measured in the dossier renders (every L1-L4
# frame: after_click_card8/9, l2_*, l3_*, l4_initial, after_timeout).
_FRAME = 3
_FIELD_BG = 4
_PANEL_BG = 5
_DASH = 0
_STRUCT = 2
_PLAYER = 14
_CARRIER = 11
_STRIDE = 2

# Action ids, measured against the verified programs (L1: five a1 = five
# 2-cell moves up the ladder, five a4 = five 2-cell moves right).
_UP, _DOWN, _LEFT, _RIGHT = 1, 2, 3, 4
_DELTAS = {_UP: (-1, 0), _DOWN: (1, 0), _LEFT: (0, -1), _RIGHT: (0, 1)}

_MIN_CARD_CELLS = 8  # real cards are ~35 cells; rejects stray pixels
_MAX_PLAN_CARDS = 6  # 2^6 toggle states is the BFS budget ceiling
_MAX_BFS_NODES = 60000
_PICKUP_MAX_SPAN = 4  # pickup blobs measured 2x4 (L2) and 2x4 (L3)
_PICKUP_MAX_CELLS = 16
_UNKNOWN = -1  # sentinel: cell under the player, value not yet observed


@dataclass(frozen=True)
class CardSpec:
    colour: int
    key: tuple[int, int, int]  # (colour, centroid row // 4, centroid col // 4)
    click: tuple[int, int]  # (x = col, y = row), a cell inside the blob


@dataclass
class CardClimbParse:
    row0: int  # interior rows [row0, row1)
    row1: int
    sep: int  # field cols are [0, sep); the dashed pair sits at sep, sep+1
    player: tuple[int, int]  # top-left of the 2x2 colour-14 block
    carrier: tuple[int, int]
    cards: list[CardSpec]
    pads: list[tuple[tuple[int, int], frozenset[int]]]  # (top-left, pair)


def _blob_cells(labels: NDArray, index: int, sl) -> list[tuple[int, int]]:
    ys, xs = np.nonzero(labels[sl] == index)
    return [(int(r) + sl[0].start, int(c) + sl[1].start) for r, c in zip(ys, xs)]


class CardClimbArchetype:
    """Parser + fingerprinting BFS planner for the dc22 card-climb grammar."""

    name = "card_climb"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear all per-life state (RESET and level advance)."""

        self._fp: dict[tuple, dict] = {}
        self._bits: dict[tuple, int] = {}
        self._order: list[tuple] = []
        self._probe: dict | None = None
        self._pending: dict | None = None
        self._banned: set = set()
        self._distrust: set = set()
        self._visited: set = set()
        self._sig: tuple | None = None
        self._under: dict[tuple[int, int], int] = {}
        self._prev: NDArray[np.int16] | None = None
        self._prev_player: tuple[int, int] | None = None
        self._plan: deque = deque()
        self._explore_target: dict | None = None

    # ------------------------------------------------------------- parsing

    def match(self, grid: NDArray[np.integer]) -> CardClimbParse | None:
        g = np.asarray(grid, dtype=np.int16)
        if g.shape != (64, 64):
            return None
        # Cheap rejects first: this path runs every turn of every game.
        if (
            int(g[0, 0]) != _FRAME
            or int(g[0, 63]) != _FRAME
            or int(g[62, 0]) != _FRAME
            or int(g[62, 63]) != _FRAME
        ):
            return None
        if int((g == _PLAYER).sum()) != 4:
            return None
        if int((g == _CARRIER).sum()) < 4:
            return None
        if not np.isin(g[63], (_DASH, _FRAME)).all():
            return None
        return self._parse(g)

    def _parse(self, g: NDArray[np.int16]) -> CardClimbParse | None:
        body = g[:63]
        all_frame = (body == _FRAME).all(axis=1)
        interior = np.nonzero(~all_frame)[0]
        if interior.size < 24:
            return None
        row0, row1 = int(interior[0]), int(interior[-1]) + 1
        if interior.size != row1 - row0:  # frame rows inside the interior
            return None
        if row0 < 4 or row1 > 60:
            return None
        inter = g[row0:row1]
        # Dashed separator: an adjacent column pair drawn only in colours
        # 0/5, zeros present in a dash pattern, both columns identical.
        col_ok = np.isin(inter, (_DASH, _PANEL_BG)).all(axis=0)
        col_zero = (inter == _DASH).any(axis=0)
        cand = col_ok & col_zero
        sep = None
        for c in range(8, 55):
            if cand[c] and cand[c + 1] and (inter[:, c] == inter[:, c + 1]).all():
                zfrac = float((inter[:, c] == _DASH).mean())
                if 0.2 <= zfrac <= 0.8:
                    sep = c
                    break
        if sep is None or sep < 16 or sep > 52:
            return None
        fieldreg = inter[:, :sep]
        panel = inter[:, sep + 2 :]
        if float((fieldreg == _FIELD_BG).mean()) < 0.35:
            return None
        if float((panel == _PANEL_BG).mean()) < 0.35:
            return None
        if (fieldreg == _DASH).any():  # the field never carries colour 0
            return None
        # Player: exactly one 2x2 colour-14 block, inside the field.
        ys, xs = np.nonzero(g == _PLAYER)
        pr, pc = int(ys.min()), int(xs.min())
        if int(ys.max()) != pr + 1 or int(xs.max()) != pc + 1:
            return None
        if not (row0 <= pr and pr + 1 < row1 and pc + 1 < sep):
            return None
        # Carrier: exactly one 2x2 colour-11 block in the FIELD (the card
        # panel may carry a colour-11 card blob, e.g. L4's slide card).
        bys, bxs = np.nonzero(g[:, :sep] == _CARRIER)
        keep = (bys >= row0) & (bys < row1)
        bys, bxs = bys[keep], bxs[keep]
        if bys.size != 4:
            return None
        cr, cc = int(bys.min()), int(bxs.min())
        if int(bys.max()) != cr + 1 or int(bxs.max()) != cc + 1:
            return None
        # Moves are 2-cell steps, so the carrier must share the player's
        # 2-cell lattice parity or the goal is unreachable by grammar.
        if (cr - pr) % _STRIDE or (cc - pc) % _STRIDE:
            return None
        cards = self._find_cards(g, row0, row1, sep)
        if not cards:
            return None
        pads = self._find_pads(g, row0, row1, sep, (pr, pc))
        return CardClimbParse(
            row0=row0,
            row1=row1,
            sep=sep,
            player=(pr, pc),
            carrier=(cr, cc),
            cards=cards,
            pads=pads,
        )

    def _find_cards(
        self, g: NDArray[np.int16], row0: int, row1: int, sep: int
    ) -> list[CardSpec]:
        from scipy import ndimage

        panel = g[row0:row1, sep + 2 :]
        mask = ~np.isin(panel, (_PANEL_BG, _DASH))
        labels, count = ndimage.label(mask)
        cards: list[CardSpec] = []
        for index, sl in enumerate(ndimage.find_objects(labels), start=1):
            if sl is None:
                continue
            cells = _blob_cells(labels, index, sl)
            if len(cells) < _MIN_CARD_CELLS:
                continue
            vals = {int(panel[r, c]) for r, c in cells}
            if len(vals) != 1:  # cards are solid single-colour sprites
                continue
            colour = vals.pop()
            mr = float(np.mean([r for r, _ in cells]))
            mc = float(np.mean([c for _, c in cells]))
            # click a real blob cell nearest the centroid
            br, bc = min(cells, key=lambda p: (p[0] - mr) ** 2 + (p[1] - mc) ** 2)
            row = br + row0
            col = bc + sep + 2
            key = (colour, int(row // 4), int(col // 4))
            cards.append(CardSpec(colour=colour, key=key, click=(col, row)))
        cards.sort(key=lambda c: c.click[1])
        return cards

    def _find_pads(
        self,
        g: NDArray[np.int16],
        row0: int,
        row1: int,
        sep: int,
        player: tuple[int, int],
    ) -> list[tuple[tuple[int, int], frozenset[int]]]:
        a = g[:-1, :-1]
        b = g[:-1, 1:]
        c = g[1:, :-1]
        d = g[1:, 1:]
        bad = (_FIELD_BG, _PANEL_BG, _DASH, _FRAME, _PLAYER, _CARRIER)
        checker = (a == d) & (b == c) & (a != b)
        checker &= ~np.isin(a, bad) & ~np.isin(b, bad)
        pads: list[tuple[tuple[int, int], frozenset[int]]] = []
        pr, pc = player
        for r, cc0 in zip(*np.nonzero(checker)):
            r, cc0 = int(r), int(cc0)
            if not (row0 <= r and r + 1 < row1 and cc0 + 1 < sep):
                continue
            if (r - pr) % _STRIDE or (cc0 - pc) % _STRIDE:
                continue
            pair = frozenset((int(g[r, cc0]), int(g[r, cc0 + 1])))
            # isolation: the surrounding ring must not continue the checker
            r0, r1_ = max(r - 1, 0), min(r + 3, 64)
            c0, c1_ = max(cc0 - 1, 0), min(cc0 + 3, 64)
            ring = g[r0:r1_, c0:c1_].copy()
            ring[r - r0 : r - r0 + 2, cc0 - c0 : cc0 - c0 + 2] = _FIELD_BG
            if np.isin(ring, list(pair)).any():
                continue
            pads.append(((r, cc0), pair))
        by_pair: dict[frozenset[int], list[tuple[int, int]]] = {}
        for pos, pair in pads:
            by_pair.setdefault(pair, []).append(pos)
        return [
            (pos, pair)
            for pair, poss in by_pair.items()
            if len(poss) == 2
            for pos in poss
        ]

    # ------------------------------------------------------------ planning

    def next_actions(
        self, parse: CardClimbParse, grid: NDArray[np.integer]
    ) -> list[Step]:
        g = np.asarray(grid, dtype=np.int16)
        self._ingest(parse, g)
        step = self._probe_step(parse, g)
        if step is None:
            step = self._planned_step(parse, g)
        self._prev = g.copy()
        self._prev_player = parse.player
        if step is None:
            self._pending = None
            return []
        return [step]

    # -- bookkeeping between calls

    def _player_cells(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        r, c = pos
        return [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]

    def _field_equal(
        self, a: NDArray[np.int16], b: NDArray[np.int16], parse: CardClimbParse
    ) -> bool:
        return bool(
            np.array_equal(
                a[parse.row0 : parse.row1, : parse.sep],
                b[parse.row0 : parse.row1, : parse.sep],
            )
        )

    def _on_set(self) -> frozenset:
        return frozenset(k for k, v in self._bits.items() if v)

    def _ingest(self, parse: CardClimbParse, g: NDArray[np.int16]) -> None:
        sig = tuple(sorted(c.key for c in parse.cards))
        if sig != self._sig:
            # New card set: a fresh board or a pickup materialized a card.
            # Refusal memory and visited pickups survive (same life).
            self._sig = sig
            self._fp = {}
            self._bits = {}
            self._probe = None
            self._order = [c.key for c in parse.cards]
            self._plan.clear()
        if (
            self._prev is not None
            and self._prev_player is not None
            and parse.player != self._prev_player
        ):
            # The cells the player now covers were visible last frame:
            # remember what lies under it so BFS can re-enter them later.
            self._under = {
                (r, c): int(self._prev[r, c])
                for r, c in self._player_cells(parse.player)
            }
        if self._explore_target is not None:
            cells = self._explore_target["cells"]
            if any(p in cells for p in self._player_cells(parse.player)):
                self._visited.add(self._explore_target["key"])
                self._explore_target = None
        pend = self._pending
        self._pending = None
        if pend is None or pend.get("kind") == "probe":
            return  # probe outcomes are handled by the probe machine
        changed = not self._field_equal(pend["pre"], g, parse)
        kind = pend["kind"]
        if kind == "move":
            if not changed:
                # The executor already retried the swallowed-step case, so
                # a still-frozen field is a real refusal: ban it.
                self._banned.add(pend["info"])
                self._plan.clear()
            elif parse.player != pend["expect_pos"]:
                self._plan.clear()
        elif kind == "click":
            key = pend["key"]
            entry = self._fp.get(key)
            if not changed:
                if entry is not None:
                    entry["fails"] = entry.get("fails", 0) + 1
                    if entry["fails"] >= 2:
                        self._distrust.add(key)
                self._plan.clear()
            elif entry is not None:
                newbit = self._bits.get(key, 0) ^ 1
                occl = set(self._player_cells(parse.player))
                ok = True
                for (r, c), (v0, v1) in entry["cells"].items():
                    if (r, c) in occl:
                        continue
                    if int(g[r, c]) != (v1 if newbit else v0):
                        ok = False
                        break
                if ok:
                    self._bits[key] = newbit
                else:
                    self._distrust.add(key)
                    self._plan.clear()
        elif kind == "tp":
            if not changed or parse.player == pend["from_pos"]:
                self._banned.add(("tp", pend["from_pos"]))
                self._plan.clear()

    # -- card fingerprinting (the dossier-endorsed click + re-click probe)

    def _card_by_key(self, parse: CardClimbParse, key: tuple) -> CardSpec | None:
        for card in parse.cards:
            if card.key == key:
                return card
        return None

    def _probe_step(self, parse: CardClimbParse, g: NDArray[np.int16]) -> Step | None:
        if self._probe is not None:
            probe = self._probe
            pre = probe["pre"]
            if probe["stage"] == 0:
                if self._field_equal(pre, g, parse) and np.array_equal(
                    pre[parse.row0 : parse.row1], g[parse.row0 : parse.row1]
                ):
                    # click changed nothing anywhere: inert (e.g. a locked
                    # card before its pickup, or L2's not-yet-earned card)
                    self._fp[probe["key"]] = {
                        "cells": {},
                        "ok": False,
                        "inert": True,
                        "moves_player": False,
                        "fails": 0,
                    }
                    self._probe = None
                else:
                    moved = parse.player != probe["player"]
                    occl = set(self._player_cells(parse.player)) | set(
                        self._player_cells(probe["player"])
                    )
                    cells: dict[tuple[int, int], tuple[int, int]] = {}
                    sub = np.nonzero(
                        pre[parse.row0 : parse.row1, : parse.sep]
                        != g[parse.row0 : parse.row1, : parse.sep]
                    )
                    for r, c in zip(*sub):
                        r, c = int(r) + parse.row0, int(c)
                        if (r, c) in occl:
                            continue
                        cells[(r, c)] = (int(pre[r, c]), int(g[r, c]))
                    probe["cells"] = cells
                    probe["moved"] = moved
                    probe["stage"] = 1
                    card = self._card_by_key(parse, probe["key"])
                    if card is None:
                        self._probe = None
                        return None
                    self._pending = {"kind": "probe"}
                    return Step(action=6, x=card.click[0], y=card.click[1])
            if probe["stage"] == 1:
                restored = self._field_equal(pre, g, parse)
                usable = restored and not probe["moved"] and bool(probe["cells"])
                self._fp[probe["key"]] = {
                    "cells": probe["cells"] if usable else {},
                    "ok": usable,
                    "inert": False,
                    "moves_player": probe["moved"],
                    "fails": 0,
                }
                self._probe = None
        for key in self._order:
            if key in self._fp or key in self._distrust:
                continue
            card = self._card_by_key(parse, key)
            if card is None:
                continue
            self._probe = {
                "key": key,
                "stage": 0,
                "pre": g.copy(),
                "player": parse.player,
            }
            self._pending = {"kind": "probe"}
            return Step(action=6, x=card.click[0], y=card.click[1])
        return None

    # -- BFS over (player position, card toggle bits)

    def _planable(self, parse: CardClimbParse) -> list[tuple]:
        keys = []
        for key in self._order:
            entry = self._fp.get(key)
            if (
                entry is None
                or not entry["ok"]
                or key in self._distrust
                or self._card_by_key(parse, key) is None
            ):
                continue
            keys.append(key)
        # ASSUMPTION (fixed disjoint slots, measured on L1-L3): cards with
        # overlapping fingerprints are dropped rather than modelled.
        cellsets = {k: set(self._fp[k]["cells"]) for k in keys}
        drop = set()
        for i, ka in enumerate(keys):
            for kb in keys[i + 1 :]:
                if cellsets[ka] & cellsets[kb]:
                    drop.add(ka)
                    drop.add(kb)
        keys = [k for k in keys if k not in drop]
        return keys[:_MAX_PLAN_CARDS]

    def _tp_edges(
        self, parse: CardClimbParse
    ) -> list[tuple[tuple[int, int], tuple[int, int], CardSpec]]:
        by_pair: dict[frozenset[int], list[tuple[int, int]]] = {}
        for pos, pair in parse.pads:
            by_pair.setdefault(pair, []).append(pos)
        edges = []
        for pair, poss in by_pair.items():
            if len(poss) != 2:
                continue
            card = next((c for c in parse.cards if c.colour in pair), None)
            if card is None:
                continue
            edges.append((poss[0], poss[1], card))
            edges.append((poss[1], poss[0], card))
        return edges

    def _explore_goals(
        self, parse: CardClimbParse, g: NDArray[np.int16]
    ) -> list[tuple[tuple, set]]:
        from scipy import ndimage

        row0, row1, sep = parse.row0, parse.row1, parse.sep
        fieldreg = g[row0:row1, :sep]
        mask = ~np.isin(fieldreg, (_FIELD_BG, _STRUCT, _PLAYER, _CARRIER))
        for entry in self._fp.values():
            for r, c in entry["cells"]:
                if row0 <= r < row1 and c < sep:
                    mask[r - row0, c] = False
        for (r, c), _pair in parse.pads:
            mask[r - row0 : r - row0 + 2, c : c + 2] = False
        labels, count = ndimage.label(mask)
        goals: list[tuple[tuple, set]] = []
        for index, sl in enumerate(ndimage.find_objects(labels), start=1):
            if sl is None:
                continue
            if (
                sl[0].stop - sl[0].start > _PICKUP_MAX_SPAN
                or sl[1].stop - sl[1].start > _PICKUP_MAX_SPAN
            ):
                continue
            cells = _blob_cells(labels, index, sl)
            if len(cells) > _PICKUP_MAX_CELLS:
                continue
            colour = int(fieldreg[cells[0]])
            key = (colour, sl[0].start + row0, sl[1].start)
            if key in self._visited:
                continue
            goals.append((key, {(r + row0, c) for r, c in cells}))
        return goals

    def _planned_step(
        self, parse: CardClimbParse, g: NDArray[np.int16]
    ) -> Step | None:
        if self._plan:
            item = self._plan[0]
            if item["pre"] == (parse.player, self._on_set()):
                self._plan.popleft()
                return self._emit(item, parse, g)
            self._plan.clear()
        plan = self._bfs(parse, g, explore=False)
        if plan is None:
            plan = self._bfs(parse, g, explore=True)
        if not plan:
            return None
        self._plan = deque(plan)
        item = self._plan.popleft()
        return self._emit(item, parse, g)

    def _emit(
        self, item: dict, parse: CardClimbParse, g: NDArray[np.int16]
    ) -> Step:
        pre = g.copy()
        if item["kind"] == "move":
            self._pending = {
                "kind": "move",
                "pre": pre,
                "info": (item["pre"][0], item["action"], item["pre"][1]),
                "expect_pos": item["post"][0],
            }
        elif item["kind"] == "click":
            self._pending = {"kind": "click", "pre": pre, "key": item["key"]}
        else:  # teleport
            self._pending = {"kind": "tp", "pre": pre, "from_pos": item["pre"][0]}
        return item["step"]

    def _bfs(
        self, parse: CardClimbParse, g: NDArray[np.int16], explore: bool
    ) -> list[dict] | None:
        row0, row1, sep = parse.row0, parse.row1, parse.sep
        base = g.copy()
        for (r, c) in self._player_cells(parse.player):
            base[r, c] = np.int16(self._under.get((r, c), _UNKNOWN))
        planable = self._planable(parse)
        # Static overlay: fingerprinted but unplanable cards still pin
        # their cells to the value of their current (absolute) bit.
        for key, entry in self._fp.items():
            if entry["ok"] and key not in planable:
                bit = self._bits.get(key, 0)
                for (r, c), (v0, v1) in entry["cells"].items():
                    base[r, c] = np.int16(v1 if bit else v0)
        fp_cells = {k: self._fp[k]["cells"] for k in planable}
        goal_cells: set = set()
        goals: list[tuple[tuple, set]] = []
        if explore:
            goals = self._explore_goals(parse, g)
            if not goals:
                return None
            goal_cells = set().union(*(cells for _k, cells in goals))
        grids: dict[int, NDArray[np.int16]] = {}
        onsets: dict[int, frozenset] = {}

        def occ(mask: int) -> NDArray[np.int16]:
            arr = grids.get(mask)
            if arr is None:
                arr = base.copy()
                for j, key in enumerate(planable):
                    bit = self._bits.get(key, 0) ^ ((mask >> j) & 1)
                    for (r, c), (v0, v1) in fp_cells[key].items():
                        arr[r, c] = np.int16(v1 if bit else v0)
                grids[mask] = arr
            return arr

        def on_of(mask: int) -> frozenset:
            got = onsets.get(mask)
            if got is None:
                got = frozenset(
                    key
                    for j, key in enumerate(planable)
                    if self._bits.get(key, 0) ^ ((mask >> j) & 1)
                )
                onsets[mask] = got
            return got

        def at_goal(pos: tuple[int, int]) -> bool:
            if explore:
                return any(p in goal_cells for p in self._player_cells(pos))
            return pos == parse.carrier

        tp_edges = self._tp_edges(parse)
        start = (parse.player, 0)
        prev: dict = {start: None}
        queue: deque = deque([start])
        found = None
        nodes = 0
        while queue:
            node = queue.popleft()
            nodes += 1
            if nodes > _MAX_BFS_NODES:
                return None
            pos, mask = node
            if at_goal(pos):
                found = node
                break
            arr = occ(mask)
            onset = on_of(mask)
            for action, (dr, dc) in _DELTAS.items():
                nr, nc = pos[0] + _STRIDE * dr, pos[1] + _STRIDE * dc
                if not (row0 <= nr and nr + 1 < row1 and 0 <= nc and nc + 1 < sep):
                    continue
                if (pos, action, onset) in self._banned:
                    continue
                block = arr[nr : nr + 2, nc : nc + 2]
                if (block == _FIELD_BG).any():
                    continue
                nxt = ((nr, nc), mask)
                if nxt not in prev:
                    prev[nxt] = (node, ("move", action))
                    queue.append(nxt)
            for j, key in enumerate(planable):
                cells = fp_cells[key]
                if any(p in cells for p in self._player_cells(pos)):
                    continue  # never drop or lift an item onto the player
                nxt = (pos, mask ^ (1 << j))
                if nxt not in prev:
                    prev[nxt] = (node, ("click", key))
                    queue.append(nxt)
            for pad_a, pad_b, card in tp_edges:
                if pos == pad_a and ("tp", pos) not in self._banned:
                    nxt = (pad_b, mask)
                    if nxt not in prev:
                        prev[nxt] = (node, ("tp", card.key))
                        queue.append(nxt)
        if found is None:
            return None
        # reconstruct
        chain: list[tuple] = []
        node = found
        while prev[node] is not None:
            parent, edge = prev[node]
            chain.append((parent, edge, node))
            node = parent
        chain.reverse()
        items: list[dict] = []
        for parent, (kind, info), child in chain:
            pre_state = (parent[0], on_of(parent[1]))
            post_state = (child[0], on_of(child[1]))
            if kind == "move":
                step = Step(action=info)
                items.append(
                    {
                        "kind": "move",
                        "action": info,
                        "step": step,
                        "pre": pre_state,
                        "post": post_state,
                    }
                )
            else:
                card = self._card_by_key(parse, info)
                if card is None:
                    return None
                step = Step(action=6, x=card.click[0], y=card.click[1])
                items.append(
                    {
                        "kind": "click" if kind == "click" else "tp",
                        "key": info,
                        "step": step,
                        "pre": pre_state,
                        "post": post_state,
                    }
                )
        if explore and items:
            end_pos = found[0]
            for key, cells in goals:
                if any(p in cells for p in self._player_cells(end_pos)):
                    self._explore_target = {"key": key, "cells": cells}
                    break
        return items

    def describe(self) -> dict:
        return {
            "kind": "fap_archetype",
            "name": self.name,
            "fingerprinted": len(self._fp),
            "banned": len(self._banned),
            "fly_content": "none; engineered scaffold per the first principle",
        }
