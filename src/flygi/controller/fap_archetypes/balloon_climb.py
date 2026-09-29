"""bp35's balloon-corridor archetype: windowed world model + exact-rule BFS.

Every mechanic encoded here is MEASURED in the bp35 dossier
(docs/fap_extension_20260928/bp35/: bp35_mechanics_verified.json, solver.py,
prog_l1234.json executed live for score 0->4) or ESTABLISHED by reading the
game's own obfuscated source (environment_files/bp35/0a0ad940/bp35.py),
which the dossier already used as its semantic reference:

  * The world is 11 columns of 6x6-pixel cells; the camera never moves
    horizontally and follows the player vertically, drawing the player's
    cell at screen rows 36-41 while the balloon rises and rows 26-31 after
    a gravity flip.  Row 63 is the action-budget bar and increments on
    EVERY action, which makes it an exact readout of the game's own
    flood-parity counter (both count actions 3/4/6; we never emit 7).
  * A lateral move into a passable cell (air, toggle-open) rises (falls,
    when gravity is flipped) until blocked; a blocking spike kills, a
    blocking gem wins, and a spike/gem directly beyond the entered cell
    counts as blocking too.  A move into a solid cell bumps in place.
  * Clicking a door removes it, a toggle flips solid<->open, a spread cell
    grows blockers into its empty 4-neighbours, and a gravity button
    (single use, clickable anywhere on screen) flips the global rise/fall.
    Clicking the cell directly ahead (above while rising) launches the
    player through it along a path computed on the PRE-click state -- the
    source evaluates the launch eagerly, before the removal/flip callbacks
    run.  A gravity click launches from the new-direction neighbour unless
    that neighbour is a wall, door, toggle-solid, spread or gravity cell.
  * Levels 1-3 flood from below: the kill row rises one cell per two
    zero-rise/bump lateral moves whose post-action counter is even, and we
    reuse the dossier solver's (verified, strictly conservative) kill rule.

Renderer grammar (sprite palette lifted from the source's sprite table and
confirmed against the dossier's live frame dumps): air = colour 10, walls =
colour 5 with colour-3 sprinkles at in-cell offsets (1,2)/(4,1)/(5,4),
door = colour-14 blob, toggle-solid = colour-12 blob, toggle-open = five
colour-12 dots, gravity = colour-8 blob, spread = colour-15 blob with
colour-3 corners, spikes = colour-15 body with an (11,0,11) tip row, gem =
colour-7 plus, flood = colour-15 wave/bubble patterns, player = six
colour-9 pixels plus two colour-11 pips.

This module is ENGINEERED SCAFFOLD, recorded as such per the repository
first principle: no fly neuron computes anything here.

Planner: everything is derived from the current grid.  The camera shows
only ~11 of up to ~46 world rows, so the archetype accumulates a world map
per life (registered window-by-window against what it has already seen)
and BFS-plans on it with the exact rules above; moves whose rise path runs
into never-seen cells are "frontier" moves, taken only when no fully-known
progressing move exists.  Because the game is deterministic per level, a
death replays identically: reset() stashes the fatal (frame, action) pair
and the next life on the same level (recognised by its byte-identical
first frame) bans it and keeps the previously mapped geometry.

ASSUMPTION (labelled): keeping the per-LEVEL geometry cache and death bans
across reset() goes beyond plain per-life state.  It is keyed by the
level's first-frame bytes, so it can never leak onto a different board
(different bytes -> different key), and it only ever contains classes read
from grids of this same level.  What breaks if the engine were
nondeterministic per level: the cache key would never re-match and the
archetype would simply re-explore from scratch, which is the no-cache
behaviour.

Off-archetype boards abstain: match() requires the six-pixel colour-9
avatar diamond with its two colour-11 pips sitting exactly on the 36- or
26-row camera line, the bp35 colour census (no colours 1/2/4/6/13), a
valid budget bar in row 63, at least one exact wall-sprinkle cell and a
window that classifies into the sprite grammar.

MEASURED (offline arcade, derived_run_seeds(0), FapExecutor seating,
2026-09-28): levels 1-6 completed in 222 driver steps (the dossier's
verified hand programs covered levels 1-4).  Level 7 is the recorded
limit: its gravity-column toggle labyrinth hides every exploration
frontier ~10 actions behind a wall of ~10^5 equally-priced toggle-subset
states, and the weighted-A* ordering exhausts its budget before reaching
one; the module then burns lives without progress.  A search that
understands rises as single actions (macro moves) is the known next step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

# --------------------------------------------------------------- constants
# Grammar constants, all ESTABLISHED from the game source's sprite table
# and confirmed on the dossier's live frame dumps.  Board-instance data
# (level layouts, absolute coordinates, action scripts) is deliberately
# absent: the dossier's verified programs are test oracles only.

_TILE = 6
_WORLD_COLS = 11
_UP_PLAYER_ROW = 36  # player cell's top screen row while rising
_DOWN_PLAYER_ROW = 26  # ... after a gravity flip (camera = 6*py - 26)

_ALLOWED = frozenset({0, 3, 5, 7, 8, 9, 10, 11, 12, 14, 15})
_FORBIDDEN_COLOURS = (1, 2, 4, 6, 13)

# cell classes (single chars, matching the dossier solver's vocabulary)
_WALL = "o"
_AIR = "."
_DOOR = "x"
_TSOLID = "1"
_TOPEN = "2"
_GRAVITY = "g"
_SPREAD = "s"
_SPIKE = "v"
_GEM = "+"
_FLOOD_M = "m"  # flood surface
_FLOOD_W = "w"  # flood body
_UNKNOWN = "?"
_PLAYER = "n"

_PASSABLE = frozenset({_AIR, _TOPEN})
_INTERACTIVE = frozenset({_DOOR, _TSOLID, _TOPEN, _GRAVITY, _SPREAD})
# Cells through which a gravity-flip launch refuses to start (source
# exclusion list: wall, door, toggle-solid, spread, gravity).
_GRAV_NO_LAUNCH = frozenset({_WALL, _DOOR, _TSOLID, _SPREAD, _GRAVITY})

# avatar sprite: colour-9 pixel offsets relative to their own bounding-box
# top-left, for the right- and left-facing sprites, plus the colour-11 pip
# offsets relative to the same corner.
_NINE_RIGHT = frozenset({(0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 1)})
_PIPS_RIGHT = ((1, 2), (2, 2))
_NINE_LEFT = frozenset({(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0)})
_PIPS_LEFT = ((1, -1), (2, -1))

# wall cell template: colour 5 with sprinkles of colour 3.
_WALL_CELL = np.full((6, 6), 5, dtype=np.int16)
for _r, _c in ((1, 2), (4, 1), (5, 4)):
    _WALL_CELL[_r, _c] = 3

_ANCHOR_ROW = 100  # arbitrary world-row origin for a life's first frame
_MAX_SEARCH_STATES = 400000
_MAX_REG_SHIFT = 40
# Per-turn search budget (wall clock).  Levels 1-6 never reach it (the
# whole six-level run plans in under two seconds); it only bounds the
# no-candidate searches on level 7+, where the soft 40% exit and the burn
# memo keep repeated turns cheap.
_PLAN_DEADLINE_S = 6.0
_H_WEIGHT = 4  # weighted-A* greed: f = depth + _H_WEIGHT * h


def _classify_cell(
    block: NDArray[np.int16], sprite_row0: int, full: bool
) -> str:
    """Classify one cell's visible pixel block into the sprite grammar.

    ``sprite_row0`` is the sprite row the block's first pixel row shows
    (0 for full cells, >0 for the bottom-partial slice under a flipped
    camera).  Sampling skips the cell's first pixel row/column when it is
    sprite row/col 0, because 7x7 sprites bleed one row/column of colour 5
    into the next cell.
    """

    counts = np.bincount(block.ravel(), minlength=16)
    if counts[9]:
        return _PLAYER
    if counts[14]:
        return _DOOR
    if counts[12]:
        return _TSOLID if counts[12] >= 8 else _TOPEN
    if counts[8]:
        return _GRAVITY
    if counts[7]:
        return _GEM
    if counts[15]:
        if counts[11] or counts[0]:
            return _SPIKE
        if counts[3]:
            return _SPREAD
        if not full:
            # A 15-only partial slice may be a spike body with its tip row
            # out of view; deadly-until-proven-otherwise is the safe read.
            return _SPIKE
        # flood surface has its wave in the bottom row only; body is full.
        if counts[15] <= 12 and not (block[:4] == 15).any():
            return _FLOOD_M
        return _FLOOD_W
    # bleed-free interior for the uniform classes
    inner = block[(1 if sprite_row0 == 0 else 0) :, 1:]
    if inner.size == 0:
        return _UNKNOWN
    if (inner == 10).all():
        return _AIR
    values = set(np.unique(inner).tolist())
    if values <= {3, 5}:
        return _WALL
    if values <= {5, 10}:
        # gem cell's bottom slice (5-ring over air) or similar mixtures
        return _UNKNOWN
    return _UNKNOWN


def _read_budget(row63: NDArray[np.int16]) -> tuple[int, int] | None:
    """Decode the budget bar: (actions_used, level_action_limit) or None.

    Levels 1-6 fill colour 15 up to 64; levels 7-9 fill colour 7 then
    overwrite with 15 past 64; level 10 adds a colour-5 layer past 128
    (read from the source's interface renderer).
    """

    values = set(np.unique(row63).tolist())
    if not values <= {0, 5, 7, 15}:
        return None
    n15 = int((row63 == 15).sum())
    n7 = int((row63 == 7).sum())
    n5 = int((row63 == 5).sum())
    filled = n15 + n7 + n5
    if filled and (row63[:filled] == 0).any():
        return None  # fill must be a prefix
    if (row63[filled:] != 0).any():
        return None
    if n5:
        if not n15 and not n7:
            return None  # a bare colour-5 prefix is not a budget bar
        return (128 + n5, 192)
    if n7 and n15:
        return (64 + n15, 128)
    if n7:
        return (n7, 128)
    return (n15, 64)


@dataclass
class BalloonParse:
    """One parsed camera window."""

    pos: tuple[int, int]  # (col, world row) in this life's anchor frame
    grav_up: bool
    budget_used: int
    budget_limit: int
    cells: dict[tuple[int, int], str]  # (col, dr rel. player) -> class
    key: bytes


@dataclass
class _Outcome:
    """Simulated result of one action under the exact movement rules."""

    kind: str  # 'move' | 'bump' | 'win' | 'frontier' | 'noop'
    pos: tuple[int, int]
    s_row: int | None
    parity: int
    deltas: frozenset
    grav_up: bool
    frontier_row: int | None = None
    flood_tick: bool = False  # a flood advance fired (or would have, were
    # the surface known): zero-rise/bump lateral at even post-parity


class BalloonClimbArchetype:
    """bp35: climb the balloon corridor to the gem, level by level."""

    name = "balloon_climb"

    def __init__(self) -> None:
        self._clear_life()
        # Per-LEVEL knowledge, keyed by the level's byte-identical first
        # frame; survives reset() -- see the module docstring's labelled
        # ASSUMPTION.  Bounded to the game's own level count.
        self._level_cache: dict[bytes, dict[str, Any]] = {}
        self._pending_death: tuple[bytes, bytes, tuple] | None = None

    # ----------------------------------------------------------- lifecycle

    def _clear_life(self) -> None:
        self._anchored = False
        self._pos: tuple[int, int] | None = None
        self._grav_up = True
        self._world: dict[tuple[int, int], str] = {}
        self._world_initial: dict[tuple[int, int], str] = {}
        self._flood_row0: int | None = None
        self._advances = 0
        self._cache_ok = True
        self._life_index = 1
        self._fingerprint: bytes | None = None
        self._last_parse: BalloonParse | None = None
        self._last_key: bytes | None = None
        self._last_real_emit: tuple[bytes, tuple] | None = None
        self._traps: set[tuple[tuple[int, int], bool]] = set()
        self._predicted: _Outcome | None = None
        # clicks whose predicted cell change did not materialize, keyed by
        # ((col, row), screen_y): never re-proposed this life
        self._failed_clicks: set[tuple[tuple[int, int], int]] = set()
        self._last_click: tuple[tuple[int, int], int, str, str] | None = None
        self._burn_memo: tuple | None = None

    def reset(self) -> None:
        """Clear all per-life state (RESET or level advance).

        A death is only distinguishable from a level advance at the NEXT
        frame (same-level restarts replay the byte-identical first frame),
        so the last emitted action is stashed and banned there.
        """

        if self._fingerprint is not None and self._last_real_emit is not None:
            # stash the last real (non-burn) action: if the next frame shows
            # this same level restarting, that action preceded the death
            self._pending_death = (
                self._fingerprint,
                self._last_real_emit[0],
                self._last_real_emit[1],
            )
        else:
            self._pending_death = None
        self._clear_life()

    # ------------------------------------------------------------- parsing

    def _find_avatar(
        self, grid: NDArray[np.int16]
    ) -> tuple[int, int, bool] | None:
        """Locate the player sprite: (cell_col, cell_row_screen, grav_up)."""

        nine = np.argwhere(grid == 9)
        if nine.shape[0] != 6:
            return None
        r0 = int(nine[:, 0].min())
        c0 = int(nine[:, 1].min())
        offsets = frozenset(
            (int(r) - r0, int(c) - c0) for r, c in nine.tolist()
        )
        if offsets == _NINE_RIGHT:
            pips = _PIPS_RIGHT
            cell_col = c0 - 2  # right sprite's 9-bbox starts at cell col +2
        elif offsets == _NINE_LEFT:
            pips = _PIPS_LEFT
            cell_col = c0 - 3  # left sprite's 9-bbox starts at cell col +3
        else:
            return None
        for dr, dc in pips:
            rr, cc = r0 + dr, c0 + dc
            if not (0 <= rr < 64 and 0 <= cc < 64) or grid[rr, cc] != 11:
                return None
        cell_row = r0 - 1
        if cell_col % _TILE or not 0 <= cell_col <= 60:
            return None
        if cell_row == _UP_PLAYER_ROW:
            return (cell_col // _TILE, cell_row, True)
        if cell_row == _DOWN_PLAYER_ROW:
            return (cell_col // _TILE, cell_row, False)
        return None

    def _parse_window(
        self, grid: NDArray[np.int16], grav_up: bool
    ) -> dict[tuple[int, int], str]:
        """Classify every visible cell, keyed by (col, row rel. player)."""

        cells: dict[tuple[int, int], str] = {}
        if grav_up:
            row_blocks = [(6 * k, 6, k - 6, 0) for k in range(10)]
            row_blocks.append((60, 3, 4, 0))  # bottom partial: sprite rows 0-2
        else:
            row_blocks = [(0, 2, -5, 4)]  # top partial: sprite rows 4-5
            row_blocks += [(6 * k + 2, 6, k - 4, 0) for k in range(10)]
        for sy, height, dr, sprite_row0 in row_blocks:
            for col in range(_WORLD_COLS):
                sx = col * _TILE
                width = min(_TILE, 64 - sx)
                block = grid[sy : sy + height, sx : sx + width]
                full = height == 6 and width == 6
                cells[(col, dr)] = _classify_cell(block, sprite_row0, full)
        return cells

    def match(self, grid: NDArray[np.integer]) -> BalloonParse | None:
        frame = np.asarray(grid, dtype=np.int16)
        if frame.shape != (64, 64):
            return None
        key = frame.tobytes()
        if self._last_parse is not None and key == self._last_key:
            return self._last_parse
        if frame.min() < 0 or frame.max() > 15:
            return None
        counts = np.bincount(frame.ravel(), minlength=16)
        if counts[9] != 6 or counts[11] < 2 or counts[10] < 8:
            return None
        if any(counts[c] for c in _FORBIDDEN_COLOURS):
            return None
        if counts[5] < 100:
            return None
        budget = _read_budget(frame[63])
        if budget is None:
            return None
        avatar = self._find_avatar(frame)
        if avatar is None:
            return None
        col, _, grav_up = avatar
        cells = self._parse_window(frame, grav_up)
        full_classes = [
            cls
            for (c, dr), cls in cells.items()
            if c < 10 and (-6 if grav_up else -4) <= dr <= (3 if grav_up else 5)
        ]
        unknown = sum(1 for cls in full_classes if cls == _UNKNOWN)
        if unknown > max(2, len(full_classes) // 10):
            return None
        if cells.get((col, 0)) != _PLAYER:
            return None
        if sum(1 for cls in cells.values() if cls == _PLAYER) != 1:
            return None
        # at least one pixel-exact wall cell (the strongest texture check)
        if not self._has_wall_cell(frame, grav_up, cells):
            return None
        parse = self._update_tracking(frame, key, col, grav_up, cells, budget)
        self._last_key = key
        self._last_parse = parse
        return parse

    def _has_wall_cell(
        self,
        frame: NDArray[np.int16],
        grav_up: bool,
        cells: dict[tuple[int, int], str],
    ) -> bool:
        for (col, dr), cls in cells.items():
            if cls != _WALL or col >= 10:
                continue
            if grav_up:
                if not -6 <= dr <= 3:
                    continue
                sy = (dr + 6) * _TILE
            else:
                if not -4 <= dr <= 5:
                    continue
                sy = (dr + 4) * _TILE + 2
            block = frame[sy : sy + 6, col * _TILE : col * _TILE + 6]
            if np.array_equal(block, _WALL_CELL):
                return True
        return False

    # ---------------------------------------------------------- world model

    def _cell_at(
        self, deltas_lookup: dict[tuple[int, int], str], cell: tuple[int, int]
    ) -> str:
        c, r = cell
        if c < 0 or c >= _WORLD_COLS:
            return _WALL
        override = deltas_lookup.get(cell)
        if override is not None:
            return override
        return self._world.get(cell, _UNKNOWN)

    def _ingest(self, cells: dict[tuple[int, int], str]) -> None:
        assert self._pos is not None
        _, py = self._pos
        for (c, dr), cls in cells.items():
            if cls == _UNKNOWN:
                continue
            wr = py + dr
            record = _AIR if cls == _PLAYER else cls
            self._world[(c, wr)] = record
            if (c, wr) not in self._world_initial and cls != _PLAYER:
                # Col-0 flood cells move (the walking kill-row sprite), so
                # they are not part of the cached static geometry.
                if not (c == 0 and record in (_FLOOD_M, _FLOOD_W)):
                    self._world_initial[(c, wr)] = record
        # flood bookkeeping: the surface row (cols 1-10) is static; the
        # col-0 surface sprite IS the current kill row when visible.
        m_rows = [
            py + dr
            for (c, dr), cls in cells.items()
            if cls == _FLOOD_M and c > 0
        ]
        if m_rows and self._flood_row0 is None:
            self._flood_row0 = min(m_rows)
        walker = [
            py + dr
            for (c, dr), cls in cells.items()
            if cls == _FLOOD_M and c == 0
        ]
        if walker and self._flood_row0 is not None:
            self._advances = max(
                self._advances, self._flood_row0 - min(walker)
            )

    def _register(
        self,
        cells: dict[tuple[int, int], str],
        predicted_rows: list[int],
    ) -> int | None:
        """Find the player's world row by aligning the window to the map."""

        def score(py: int) -> tuple[int, int, int]:
            same = diff = compared = 0
            for (c, dr), cls in cells.items():
                if cls in (_UNKNOWN, _PLAYER):
                    continue
                known = self._world.get((c, py + dr))
                if known is None:
                    continue
                compared += 1
                if known == cls:
                    same += 1
                elif {known, cls} <= {_FLOOD_M, _FLOOD_W, _AIR}:
                    pass  # the col-0 flood walker legitimately moves
                else:
                    diff += 1
            return (same - 2 * diff, diff, compared)

        def valid(py: int) -> bool:
            s, d, n = score(py)
            return n >= 6 and d <= max(2, n * 3 // 20)

        for py in predicted_rows:
            if valid(py):
                return py
        assert self._pos is not None
        base = self._pos[1]
        scored = []
        for d in range(-_MAX_REG_SHIFT, _MAX_REG_SHIFT + 1):
            py = base + d
            if valid(py):
                scored.append((score(py)[0], py))
        if not scored:
            return None
        scored.sort(reverse=True)
        if len(scored) > 1 and scored[0][0] - scored[1][0] < 3:
            return None
        return scored[0][1]

    def _update_tracking(
        self,
        frame: NDArray[np.int16],
        key: bytes,
        col: int,
        grav_up: bool,
        cells: dict[tuple[int, int], str],
        budget: tuple[int, int],
    ) -> BalloonParse:
        budget_used, budget_limit = budget
        if not self._anchored:
            self._anchored = True
            self._grav_up = grav_up
            self._pos = (col, _ANCHOR_ROW)
            self._fingerprint = key
            cached = self._cache_entry(key)
            if cached["initial"]:
                self._world = dict(cached["initial"])
                self._world_initial = dict(cached["initial"])
                self._flood_row0 = cached["flood_row0"]
                self._traps = set(cached["traps"])
            cached["lives"] += 1
            self._life_index = cached["lives"]
            if (
                self._pending_death is not None
                and self._pending_death[0] == key
            ):
                # the previous life died on this same level: ban its last
                # real action at the exact frame it was emitted from
                entry = self._cache_entry(key)
                entry["banned"].add(
                    (self._pending_death[1], self._pending_death[2])
                )
            self._pending_death = None
            self._ingest(cells)
            self._sync_cache()
            return BalloonParse(
                pos=self._pos,
                grav_up=grav_up,
                budget_used=budget_used,
                budget_limit=budget_limit,
                cells=cells,
                key=key,
            )
        # mid-life frame: place it via prediction, falling back to search
        assert self._pos is not None
        predicted_rows: list[int] = []
        if self._predicted is not None and self._predicted.kind != "frontier":
            predicted_rows.append(self._predicted.pos[1])
        elif self._predicted is None:
            predicted_rows.append(self._pos[1])
        py = self._register(cells, predicted_rows)
        if py is None:
            # lost the anchor (a long blind rise past everything known):
            # restart the map from here; the cache stays read-only.
            self._world = {}
            self._world_initial = {}
            self._cache_ok = False
            self._flood_row0 = None
            self._advances = 0
            py = _ANCHOR_ROW
        self._pos = (col, py)
        self._grav_up = grav_up
        self._predicted = None
        self._ingest(cells)
        # click verification: a click whose predicted cell change did not
        # materialize is recorded and never re-proposed this life
        if self._last_click is not None:
            cell, y, pre_cls, want_cls = self._last_click
            dr = cell[1] - py
            observed = cells.get((cell[0], dr))
            if observed is not None and observed != _UNKNOWN:
                obs = _AIR if observed == _PLAYER else observed
                if obs == pre_cls and obs != want_cls:
                    self._failed_clicks.add((cell, y))
        self._last_click = None
        self._sync_cache()
        return BalloonParse(
            pos=self._pos,
            grav_up=grav_up,
            budget_used=budget_used,
            budget_limit=budget_limit,
            cells=cells,
            key=key,
        )

    def _cache_entry(self, key: bytes) -> dict[str, Any]:
        return self._level_cache.setdefault(
            key,
            {"initial": {}, "flood_row0": None, "banned": set(),
             "traps": set(), "lives": 0},
        )

    def _sync_cache(self) -> None:
        if not self._cache_ok or self._fingerprint is None:
            return
        entry = self._cache_entry(self._fingerprint)
        entry["initial"].update(self._world_initial)
        if self._flood_row0 is not None:
            entry["flood_row0"] = self._flood_row0
        if len(self._level_cache) > 16:
            self._level_cache.pop(next(iter(self._level_cache)))

    # ------------------------------------------------------------ simulator

    def _rise(
        self,
        deltas: dict[tuple[int, int], str],
        start: tuple[int, int],
        grav_up: bool,
    ) -> tuple[str, tuple[int, int], int]:
        """The source's rise/fall from an entered cell.

        Returns (kind, landing, count): kind 'land'|'win'|'death'|'frontier'.
        The scan starts BEYOND ``start`` (the entered/launched-through
        cell), exactly like the source's traversal.
        """

        dy = -1 if grav_up else 1
        count = 0
        last = start
        cur = (start[0], start[1] + dy)
        while True:
            cls = self._cell_at(deltas, cur)
            if cls == _UNKNOWN:
                return ("frontier", cur, count)
            if cls in _PASSABLE:
                last = cur
                cur = (cur[0], cur[1] + dy)
                count += 1
                continue
            if cls == _GEM:
                return ("win", cur, count + 1)
            if cls == _SPIKE:
                return ("death", last, count + 1)
            return ("land", last, count)

    def _sim_move(
        self,
        pos: tuple[int, int],
        grav_up: bool,
        deltas: dict[tuple[int, int], str],
        s_row: int | None,
        parity: int,
        dx: int,
    ) -> _Outcome | None:
        """One lateral move under the exact rules; None prunes the branch."""

        target = (pos[0] + dx, pos[1])
        cls = self._cell_at(deltas, target)
        parity += 1
        frozen = frozenset(deltas.items())
        if cls == _UNKNOWN:
            return _Outcome(
                "frontier", pos, s_row, parity, frozen, grav_up,
                frontier_row=target[1],
            )
        if cls == _GEM:
            return _Outcome("win", target, s_row, parity, frozen, grav_up)
        if cls in _PASSABLE:
            kind, landing, count = self._rise(deltas, target, grav_up)
            if kind == "frontier":
                return _Outcome(
                    "frontier", pos, s_row, parity, frozen, grav_up,
                    frontier_row=landing[1],
                )
            if kind == "death":
                return None
            if kind == "win":
                return _Outcome("win", landing, s_row, parity, frozen, grav_up)
            tick = count == 0 and parity % 2 == 0
            if tick and s_row is not None:
                new_s = s_row - 1
                if landing[1] >= new_s:
                    return None  # flood catches the player (solver's rule)
                s_row = new_s
            return _Outcome(
                "move", landing, s_row, parity, frozen, grav_up,
                flood_tick=tick,
            )
        # bump against a solid cell
        tick = parity % 2 == 0
        if tick and s_row is not None:
            new_s = s_row - 1
            if pos[1] >= new_s:
                return None
            s_row = new_s
        return _Outcome(
            "bump", pos, s_row, parity, frozen, grav_up, flood_tick=tick
        )

    def _click_band(self, grav_up: bool) -> tuple[int, int]:
        # On-screen click rows relative to the player: rising camera
        # -6..+4 (y=3..63), flipped camera -4..+5 (y=5..59).  The dossier
        # logged ONE failed click at cy-py = -6, but a direct probe on
        # 2026-09-28 (level 6's top gravity button, clicked at y=3 from six
        # cells below) measured the flip landing, so the failure was
        # situational.  The planner still keeps the extreme -6 row for
        # gravity buttons only (see _plan): level 6 needs it, while opening
        # it to every door/toggle explodes the click branching and starved
        # the search on level 2.  A click that IS swallowed is recorded by
        # the verification in _update_tracking and never re-proposed.
        return (-5, 4) if grav_up else (-4, 5)

    def _click_allowed(
        self, dy: int, cls: str, grav_up: bool
    ) -> bool:
        band_lo, band_hi = self._click_band(grav_up)
        if band_lo <= dy <= band_hi:
            return True
        return grav_up and dy == -6 and cls == _GRAVITY

    def _sim_click(
        self,
        pos: tuple[int, int],
        grav_up: bool,
        deltas: dict[tuple[int, int], str],
        s_row: int | None,
        parity: int,
        cell: tuple[int, int],
    ) -> _Outcome | None:
        cls = self._cell_at(deltas, cell)
        if cls not in _INTERACTIVE:
            return None
        parity += 1  # clicks advance the counter but never the flood
        new_deltas = dict(deltas)
        launch_deltas = deltas
        new_grav = grav_up
        if cls == _DOOR:
            new_deltas[cell] = _AIR
        elif cls == _TSOLID:
            new_deltas[cell] = _TOPEN
        elif cls == _TOPEN:
            new_deltas[cell] = _TSOLID
        elif cls == _SPREAD:
            # the source adds the neighbour blockers eagerly (they DO block
            # the launch) but removes the clicked cell in a later callback
            new_deltas[cell] = _AIR
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nb = (cell[0] + dx, cell[1] + dy)
                nb_cls = self._cell_at(deltas, nb)
                if nb_cls == _AIR:
                    new_deltas[nb] = _SPREAD
                elif nb_cls == _UNKNOWN:
                    # cannot know whether a blocker appears there; keep it
                    # unknown so any traversal through it stays a frontier
                    pass
            launch_deltas = dict(new_deltas)
            launch_deltas[cell] = _SPREAD  # still present at launch time
        elif cls == _GRAVITY:
            new_grav = not grav_up
            new_deltas[cell] = _AIR
        # canonicalize: a toggle flipped back to its base-map state must not
        # linger as a ghost delta, or every flip-flop mints a "new" state
        if new_deltas.get(cell) == self._world.get(cell):
            new_deltas.pop(cell, None)
        # launch: computed on the PRE-click state (the source evaluates the
        # traversal before the removal/flip callbacks run)
        dy = -1 if new_grav else 1
        ahead = (pos[0], pos[1] + dy)
        launch = False
        if cls == _GRAVITY:
            ahead_cls = self._cell_at(launch_deltas, ahead)
            if ahead_cls == _UNKNOWN:
                return _Outcome(
                    "frontier", pos, s_row, parity,
                    frozenset(new_deltas.items()), new_grav,
                    frontier_row=ahead[1],
                )
            launch = ahead_cls not in _GRAV_NO_LAUNCH
        elif cell == ahead:
            launch = True  # the clicked cell is never a wall here
        new_pos = pos
        if launch:
            kind, landing, _ = self._rise(launch_deltas, ahead, new_grav)
            if kind == "frontier":
                return _Outcome(
                    "frontier", pos, s_row, parity,
                    frozenset(new_deltas.items()), new_grav,
                    frontier_row=landing[1],
                )
            if kind == "death":
                return None
            new_pos = landing
            if kind == "win":
                return _Outcome(
                    "win", landing, s_row, parity,
                    frozenset(new_deltas.items()), new_grav,
                )
        return _Outcome(
            "move" if new_pos != pos else "noop",
            new_pos, s_row, parity, frozenset(new_deltas.items()), new_grav,
        )

    # -------------------------------------------------------------- planner

    def _reveal_counter(self):
        """Per-state count of never-seen cells a state's camera would show."""

        if not self._world:
            return lambda row, grav_up: 11 * 11
        rows = [r for (_, r) in self._world]
        lo, hi = min(rows) - 12, max(rows) + 12
        unknown = {r: _WORLD_COLS for r in range(lo, hi + 1)}
        for (_, r) in self._world:
            if lo <= r <= hi:
                unknown[r] -= 1

        def count(row: int, grav_up: bool) -> int:
            a, b = (row - 6, row + 4) if grav_up else (row - 5, row + 5)
            total = 0
            for rr in range(a, b + 1):
                total += unknown.get(rr, _WORLD_COLS)
            return total

        return count

    def _plan(self, parse: BalloonParse) -> list[tuple]:
        """Weighted best-first search to the gem, else explore.

        Returns the chosen action path (list of ('L',) / ('R',) /
        ('C', c, r) tuples); an empty list means burn an action.  When no
        complete path to a known gem exists, the planner heads for the
        nearest state whose camera would reveal never-seen cells, and only
        when no such safe state exists does it take the nearest "frontier"
        action (one whose rise runs into unknown cells).
        """

        import heapq
        import time as _time

        assert self._pos is not None
        root_pos = self._pos
        root_grav = self._grav_up
        # a burn loop leaves the world model untouched, so its search
        # outcome cannot change: decide once, then keep burning cheaply
        burn_memo_key = (
            root_pos, root_grav, len(self._world), self._advances,
            len(self._failed_clicks),
        )
        if self._burn_memo == burn_memo_key:
            return []
        root_s = (
            self._flood_row0 - self._advances
            if self._flood_row0 is not None
            else None
        )
        root_parity = parse.budget_used
        banned: set = set()
        if self._fingerprint in self._level_cache:
            banned = {
                step
                for (fb, step) in self._level_cache[self._fingerprint]["banned"]
                if fb == parse.key
            }
        base_interactive = [
            cell for cell, cls in self._world.items() if cls in _INTERACTIVE
        ]
        gem = next(
            (cell for cell, cls in self._world.items() if cls == _GEM), None
        )
        reveal = self._reveal_counter()
        root_reveal = reveal(root_pos[1], root_grav)
        # The search is drawn toward the gem when one is known AND toward
        # the exploration frontier: rows holding never-seen cells adjacent
        # to known non-wall cells (a known gem can still be unreachable in
        # the mapped part, so exploration must keep pulling).  A balloon
        # only travels with gravity, so rows on the wrong side of the
        # player attract only when an unused gravity button is known.
        reachable = frozenset(
            {_AIR, _TOPEN, _DOOR, _TSOLID, _GRAVITY, _SPREAD, _GEM,
             _FLOOD_M}
        )
        has_gravity_button = any(
            cls == _GRAVITY for cls in self._world.values()
        )
        rows = set()
        for (c, r), cls in self._world.items():
            if cls not in reachable:
                continue
            for dc, dr in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nb = (c + dc, r + dr)
                if 0 <= nb[0] < _WORLD_COLS and nb not in self._world:
                    rows.add(nb[1])
        attractor_rows = sorted(rows)

        def heuristic(pos: tuple[int, int], grav_up: bool) -> int:
            best = None
            if gem is not None:
                best = abs(gem[0] - pos[0]) + abs(gem[1] - pos[1])
            for r in attractor_rows:
                ahead = r <= pos[1] if grav_up else r >= pos[1]
                if not ahead and not has_gravity_button:
                    continue
                d = abs(r - pos[1])
                if best is None or d < best:
                    best = d
            return 0 if best is None else best

        def parity_key(parity: int, s_row: int | None) -> int:
            # parity only matters while the flood is live
            return parity & 1 if s_row is not None else 0

        def run_search(max_dc: int, deadline_s: float) -> dict[str, Any]:
            """One weighted best-first pass; ``max_dc`` caps the click
            column distance (1 = normal canonical set, 0 = own-column-only
            fallback whose small branching dives much deeper)."""

            root_key: tuple = (
                root_pos, root_grav, frozenset(), root_s,
                parity_key(root_parity, root_s),
            )
            parents: dict[tuple, tuple | None] = {root_key: None}
            depth: dict[tuple, int] = {root_key: 0}
            counter = 0
            heap: list = [
                (_H_WEIGHT * heuristic(root_pos, root_grav), 0, root_key, {})
            ]
            win_key: tuple | None = None
            death_action: tuple | None = None  # root action that dies at once
            # (depth, tiebreak, state key, extra risky action | None)
            frontier_best: tuple | None = None
            reveal_best: tuple | None = None

            def rebuild(key: tuple) -> list[tuple]:
                path: list[tuple] = []
                cur = key
                while parents[cur] is not None:
                    cur, act = parents[cur]
                    path.append(act)
                return path[::-1]

            now = _time.monotonic()
            deadline = now + deadline_s
            soft_deadline = now + 0.4 * deadline_s
            popped = 0
            while heap and win_key is None and popped < _MAX_SEARCH_STATES:
                _, _, key, deltas = heapq.heappop(heap)
                popped += 1
                if popped % 256 == 0:
                    t = _time.monotonic()
                    if t > deadline:
                        break
                    if t > soft_deadline and (
                        reveal_best is not None or frontier_best is not None
                    ):
                        break  # no win in sight: take the exploration lead
                pos, grav_up, _, s_row, _ = key
                parity = depth[key] + root_parity
                actions: list[tuple] = [("L",), ("R",)]
                gravity_cells: list[tuple[int, tuple[int, int]]] = []
                seen_cells: set[tuple[int, int]] = set()
                # Cap gravity flips per plan: with dozens of buttons the
                # up-down yo-yo mints endless cheap states.  Replanning
                # after every executed step resets the cap, so longer flip
                # sequences still happen across turns.
                flips_left = 3 - sum(
                    1
                    for cell in deltas
                    if self._world.get(cell) == _GRAVITY
                )
                # ASSUMPTION (canonical click ordering): a door/toggle/
                # spread click is generated only from a column-adjacent
                # position (|dc| <= max_dc <= 1).  Click bands constrain
                # ROWS only, so a farther click can be deferred until the
                # player walks column-adjacent at the same row -- every
                # route measured so far (levels 1-7, incl. the verified
                # programs) clicks this way.  What breaks if wrong: a level
                # needing a >=2-column remote click never plans it and the
                # level stalls; the trade buys the branching cut that makes
                # the toggle labyrinths searchable at all.
                for cell in base_interactive:
                    if cell in deltas:
                        continue
                    cls = self._world[cell]
                    if not self._click_allowed(
                        cell[1] - pos[1], cls, grav_up
                    ):
                        continue
                    seen_cells.add(cell)
                    if cls == _GRAVITY:
                        rank = abs(cell[1] - pos[1]) * 16 + abs(
                            cell[0] - pos[0]
                        )
                        gravity_cells.append((rank, cell))
                    elif abs(cell[0] - pos[0]) <= max_dc:
                        actions.append(("C", cell[0], cell[1]))
                for cell, cls in deltas.items():
                    if cls in _INTERACTIVE and cell not in seen_cells:
                        if abs(cell[0] - pos[0]) <= max_dc and (
                            self._click_allowed(
                                cell[1] - pos[1], cls, grav_up
                            )
                        ):
                            actions.append(("C", cell[0], cell[1]))
                if self._life_index > 1 and len(actions) > 1:
                    # deterministic per-life variety: rotating the
                    # expansion order changes the equal-f (LIFO) dives, so
                    # a re-run life explores a different branch
                    rot = self._life_index % len(actions)
                    actions = actions[rot:] + actions[:rot]
                if gravity_cells and flips_left <= 0:
                    gravity_cells = []
                if gravity_cells:
                    # All non-adjacent gravity buttons act identically
                    # (global flip), differing only in which one is spent.
                    # Trying every one turns k successive flips into an
                    # exponential family of used-button subsets (level 7
                    # has a whole column of them), so when buttons are
                    # plentiful only the nearest is spent; with at most two
                    # in band the choice is kept exact.
                    gravity_cells.sort()
                    keep = (
                        [cell for _, cell in gravity_cells]
                        if len(gravity_cells) <= 2
                        else [gravity_cells[0][1]]
                    )
                    for cell in keep:
                        actions.append(("C", cell[0], cell[1]))
                for action in actions:
                    if action[0] == "C":
                        _, y = self._click_xy(
                            action[1], action[2], pos, grav_up
                        )
                        if ((action[1], action[2]), y) in self._failed_clicks:
                            continue
                    if depth[key] == 0 and self._action_step_key(
                        action, root_pos, root_grav
                    ) in banned:
                        continue
                    if action[0] in ("L", "R"):
                        out = self._sim_move(
                            pos, grav_up, deltas, s_row, parity,
                            -1 if action[0] == "L" else 1,
                        )
                    else:
                        out = self._sim_click(
                            pos, grav_up, deltas, s_row, parity,
                            (action[1], action[2]),
                        )
                    if out is None:
                        if depth[key] == 0 and death_action is None:
                            death_action = action
                        continue
                    if (
                        out.kind != "win"
                        and (out.pos, out.grav_up) in self._traps
                    ):
                        continue  # a previous life proved this a trap
                    if out.kind == "frontier":
                        cand = (depth[key] + 1, counter, key, action)
                        counter += 1
                        if frontier_best is None or cand[0] < frontier_best[0]:
                            frontier_best = cand
                        if gem is None:
                            break  # no gem in sight: any probe will do
                        continue
                    new_key = (
                        out.pos, out.grav_up, out.deltas, out.s_row,
                        parity_key(out.parity, out.s_row),
                    )
                    if new_key in parents:
                        continue
                    parents[new_key] = (key, action)
                    depth[new_key] = depth[key] + 1
                    if out.kind == "win":
                        win_key = new_key
                        break
                    counter += 1
                    # LIFO tie-break: equal-f states expand depth-first,
                    # diving down corridors instead of enumerating subsets
                    heapq.heappush(
                        heap,
                        (
                            depth[new_key]
                            + _H_WEIGHT * heuristic(out.pos, out.grav_up),
                            -counter,
                            new_key,
                            dict(out.deltas),
                        ),
                    )
                    if reveal(out.pos[1], out.grav_up) > root_reveal:
                        cand = (depth[new_key], counter, new_key, None)
                        if reveal_best is None or cand[0] < reveal_best[0]:
                            reveal_best = cand
                        if gem is None:
                            break  # no gem in sight: go and look from there
                else:
                    continue
                if gem is None and (reveal_best or frontier_best):
                    break
            best = reveal_best if reveal_best is not None else frontier_best
            return {
                "win_path": rebuild(win_key) if win_key is not None else None,
                "best_path": (
                    rebuild(best[2]) + ([best[3]] if best[3] else [])
                    if best is not None
                    else None
                ),
                "death_action": death_action,
                "exhausted": not heap and popped < _MAX_SEARCH_STATES,
                "stats": {
                    "popped": popped,
                    "states": len(parents),
                    "max_depth": max(depth.values()) if depth else 0,
                    "win": win_key is not None,
                    "candidate": best is not None,
                },
            }

        result = run_search(1, _PLAN_DEADLINE_S)
        if result["win_path"] is None and result["best_path"] is None and (
            not result["exhausted"]
        ):
            # the full canonical set drowned in toggle subsets: retry with
            # own-column clicks only, whose branching dives far deeper
            lite = run_search(0, _PLAN_DEADLINE_S)
            if lite["win_path"] or lite["best_path"]:
                result = lite
        self._plan_stats = result["stats"]
        remaining = parse.budget_limit - 1 - parse.budget_used
        if result["win_path"] is not None:
            if len(result["win_path"]) <= remaining:
                self._burn_memo = None
                return result["win_path"]
            # cannot finish on this budget: burn into a fresh, mapped life
            self._burn_memo = burn_memo_key
            return []
        if remaining < 4:
            self._burn_memo = burn_memo_key
            return []
        if result["best_path"] is None:
            # No win, no unseen cells, no frontier in everything searched.
            if result["exhausted"] and self._cache_ok and (
                self._fingerprint is not None
            ):
                # proven trap: the whole reachable set is barren, so later
                # lives must route around this position (recording it on a
                # merely budget-capped search was tried on 2026-09-28 and
                # poisoned level 7's chokepoints -- proofs only)
                self._cache_entry(self._fingerprint)["traps"].add(
                    (root_pos, root_grav)
                )
                self._traps.add((root_pos, root_grav))
            if result["death_action"] is not None:
                # burning cannot change the world, so this life is spent
                # either way: die now and give the next life its budget
                self._burn_memo = None
                return [result["death_action"]]
            self._burn_memo = burn_memo_key
            return []
        self._burn_memo = None
        return result["best_path"]

    # ------------------------------------------------------------- emission

    def _action_step_key(
        self, action: tuple, pos: tuple[int, int], grav_up: bool
    ) -> tuple:
        if action[0] == "L":
            return (3,)
        if action[0] == "R":
            return (4,)
        _, c, r = action
        x, y = self._click_xy(c, r, pos, grav_up)
        return (6, x, y)

    def _click_xy(
        self, c: int, r: int, pos: tuple[int, int], grav_up: bool
    ) -> tuple[int, int]:
        dy = r - pos[1]
        y = dy * _TILE + (39 if grav_up else 29)
        y = min(max(y, 0), 62)  # row 63 is the budget bar; 62 maps the same
        return (c * _TILE + 3, y)

    def _to_step(self, action: tuple, parse: BalloonParse) -> Step:
        if action[0] == "L":
            return Step(action=3)
        if action[0] == "R":
            return Step(action=4)
        _, c, r = action
        x, y = self._click_xy(c, r, parse.pos, parse.grav_up)
        return Step(action=6, x=x, y=y)

    def _burn_step(self, parse: BalloonParse) -> Step:
        """A guaranteed no-op: click the player's own cell (its sprite list
        matches no click handler), spending budget toward a fresh life."""

        c, r = parse.pos
        x, y = self._click_xy(c, r, parse.pos, parse.grav_up)
        return Step(action=6, x=x, y=y)

    def next_actions(
        self, parse: BalloonParse, grid: NDArray[np.integer]
    ) -> list[Step]:
        """One step per call: the world only changes when we act, but
        single-step emission lets every action be verified, re-planned and
        (after a death) banned at its exact frame."""

        path = self._plan(parse)
        burn = not path
        self._last_click = None
        if burn:
            step = self._burn_step(parse)
            self._predicted = _Outcome(
                "noop",
                parse.pos,
                (
                    self._flood_row0 - self._advances
                    if self._flood_row0 is not None
                    else None
                ),
                parse.budget_used + 1,
                frozenset(),
                parse.grav_up,
            )
        else:
            action = path[0]
            step = self._to_step(action, parse)
            root_s = (
                self._flood_row0 - self._advances
                if self._flood_row0 is not None
                else None
            )
            if action[0] in ("L", "R"):
                out = self._sim_move(
                    parse.pos, parse.grav_up, {}, root_s,
                    parse.budget_used, -1 if action[0] == "L" else 1,
                )
            else:
                out = self._sim_click(
                    parse.pos, parse.grav_up, {}, root_s,
                    parse.budget_used, (action[1], action[2]),
                )
            self._predicted = out
            if action[0] == "C" and out is not None:
                cell = (action[1], action[2])
                pre = self._cell_at({}, cell)
                want = dict(out.deltas).get(cell)
                if want is not None and want != pre:
                    _, y = self._click_xy(
                        cell[0], cell[1], parse.pos, parse.grav_up
                    )
                    self._last_click = (cell, y, pre, want)
            if out is not None and out.kind != "frontier":
                # apply this action's own world edits so the next frame's
                # registration compares against the post-click state
                for cell, cls in out.deltas:
                    self._world[cell] = cls
                if out.flood_tick:
                    # count the game's flood advances from life start even
                    # while the surface is still off-screen, so a late
                    # first sighting still yields the right kill row
                    self._advances += 1
        step_key = (
            (step.action,) if step.action != 6 else (6, step.x, step.y)
        )
        if not burn:
            self._last_real_emit = (parse.key, step_key)
        return [step]

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "fap_archetype",
            "name": self.name,
            "anchored": self._anchored,
            "fly_content": "none; engineered scaffold",
        }
