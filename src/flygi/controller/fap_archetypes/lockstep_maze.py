"""tu93's archetype: lockstep maze with sentinel/patroller/chaser enemies.

Every mechanic encoded here is MEASURED in the tu93 dossier
(docs/fap_extension_20260928/tu93/NOTES.md) unless a comment says otherwise:
rooms are 3x3 colour-0 blocks on a 6-pixel pitch, colour-2 3x3 blocks between
two rooms are open doors, the avatar is a colour-9 block with a colour-4
mid-edge eye, the goal is a colour-14 room, row 63 is a colour-6 timer strip
depleting right to left (depleted pixels render 0), and the world advances
ONLY on the avatar's successful moves -- blocked moves freeze everything.
Enemy grammar, also measured: colour 8 = static sentinel (colour-15 mid-edge
eye = facing; faced adjacent room is lethal, side/back entry kills it),
colour 12 = patroller (1 room per world tick along its facing, flips at
walls; co-entry and swap-through are lethal, entering its vacated room is
safe), colour 13 = dormant chaser (sentinel rules until the avatar enters its
open-door line of sight, then the eye retracts and it trail-follows the
avatar with lag 2; death iff the avatar re-enters a room exactly 2 ticks
after leaving it).

This module is ENGINEERED SCAFFOLD, recorded as such per the repository
first principle: no fly neuron computes anything here. Its comparison
evidence is the executor-driven offline run against the dossier's verified
hand programs (9/9 levels, 187 actions, GameState.WIN).

The planner is a port of the dossier's verified planner2.py: BFS over
(room, previous room, tick, dead enemies, chaser states), with patroller
trajectories expanded as pure functions of the tick and the chaser reduced
to the forbid-previous-room rule that lag-2 trail-following implies on a
bipartite room lattice.

Per-life state kept on self (cleared in reset()): the avatar's own room
trail (the chaser's position is a function of it), the goal room, each
dormant chaser's facing (the eye retracts on trigger, one tick before the
chaser moves), persistent sentinel/dormant-chaser models, a stepped
patroller model, and a verified plan cache so the common turn costs no BFS.

The models exist because of a MEASURED rendering fact (live L5/L6 frames,
2026-09-28): each room renders exactly ONE sprite, so a patroller crossing
the goal room hides the 14 pixels completely, and a patroller crossing a
sentinel's room hides either the patroller (L6 tick 3) or the sentinel
(L6 ticks 4 and 8) for that tick. A parse of the current frame alone would
have concluded the sentinel was gone and walked into its faced room -- the
exact death measured before this model was added. Statics never move and
die only to the avatar's own side-entry, so their persistence rule is
grid-derived: a remembered sentinel leaves the model only when the avatar
occupies its room.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections import deque

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step

_BG = 5
_DOOR = 2
_TIMER = 6
_AVATAR = 9
_AVATAR_EYE = 4
_GOAL = 14
_SENTINEL = 8
_PATROLLER = 12
_CHASER = 13
_ENEMY_EYE = 15
# MEASURED (live L7 frame, 2026-09-28): triggering a chaser recolours its
# eye pixel from 15 to 11 (facing still readable) on the trigger tick; the
# eye disappears once it starts walking. 11 is accepted as an "armed" eye
# on any enemy block; on a chaser it is the definitive just-triggered mark.
_ARMED_EYE = 11

_PITCH = 6
_ROOM = 3

_CONTENT = (
    0, _AVATAR_EYE, _SENTINEL, _AVATAR, _ARMED_EYE,
    _PATROLLER, _CHASER, _GOAL, _ENEMY_EYE,
)
_BODY_ALLOWED = frozenset(_CONTENT) | {_BG, _DOOR}
# Measured block colour-sets across all nine level-start frames:
# {0}, {14}, {4,9}, {8,15}, {12,15}, {13,15}; a triggered chaser shows
# {13,11} (measured live), a chasing chaser drops its eye ({13}), and
# planner2 tolerated eyeless sentinels/patrollers ({8}, {12}).
_ROOM_SETS = (
    frozenset({0}),
    frozenset({_GOAL}),
    frozenset({_AVATAR}),
    frozenset({_AVATAR, _AVATAR_EYE}),
    frozenset({_SENTINEL}),
    frozenset({_SENTINEL, _ENEMY_EYE}),
    frozenset({_SENTINEL, _ARMED_EYE}),
    frozenset({_PATROLLER}),
    frozenset({_PATROLLER, _ENEMY_EYE}),
    frozenset({_PATROLLER, _ARMED_EYE}),
    frozenset({_CHASER}),
    frozenset({_CHASER, _ENEMY_EYE}),
    frozenset({_CHASER, _ARMED_EYE}),
)
# MEASURED (live L5 frame, 2026-09-28): a patroller crossing the goal room
# covers the 14 pixels COMPLETELY -- the block renders as an ordinary
# {12,15} patroller block. A goal-less parse is therefore legal exactly when
# an enemy that moves (patroller, or triggered chaser) is on the board; the
# goal room itself is carried as per-life memory from the frames where it
# was visible.

_DIRS: dict[int, tuple[int, int]] = {1: (-1, 0), 2: (1, 0), 3: (0, -1), 4: (0, 1)}

_NODE_CAP = 200_000
_MAX_HORIZON = 300


Room = tuple[int, int]


@dataclass
class MazeParse:
    r0: int
    c0: int
    rooms: frozenset[Room]
    doors: frozenset[frozenset[Room]]
    avatar: Room
    goal: Room | None  # None = goal pixels covered by an enemy this frame
    statics: dict[Room, tuple[int, int] | None]
    patrollers: list[tuple[Room, tuple[int, int] | None]]
    # (room, facing|None, armed): armed = 11-eye (just triggered, facing
    # still readable); facing None = eyeless (walking its chase).
    chasers: list[tuple[Room, tuple[int, int] | None, bool]]
    timer_pixels: int


def _eye_facing(block: NDArray[np.int16], eye: int) -> tuple[int, int] | None:
    """The eye pixel's mid-edge offset from the block centre, else None."""

    locs = np.argwhere(block == eye)
    if len(locs) != 1:
        return None
    dr, dc = int(locs[0][0]) - 1, int(locs[0][1]) - 1
    if abs(dr) + abs(dc) != 1:
        return None
    return (dr, dc)


def _parse_maze(grid: NDArray[np.int16]) -> MazeParse | None:
    """Strict structural parse of the lockstep-maze grammar; None = abstain.

    Every check below is part of the archetype's measured signature; the
    point of the strictness is that no other game's frames can false-match
    (the hidden-set lesson). All coordinates are derived from the frame --
    the lattice origin is the min row/col over content pixels.
    """

    if grid.shape != (64, 64):
        return None
    timer = grid[63]
    n6 = int((timer == _TIMER).sum())
    # Timer strip: a contiguous colour-6 prefix from column 0, 0 elsewhere.
    if n6 < 1 or not (timer[:n6] == _TIMER).all() or not (timer[n6:] == 0).all():
        return None
    body = grid[:63]
    if int(body.min()) < 0 or int(body.max()) > 15:
        return None
    census = np.bincount(body.ravel(), minlength=16)
    if int(census.argmax()) != _BG:
        return None
    if any(census[v] and v not in _BODY_ALLOWED for v in range(16)):
        return None
    content = np.isin(body, _CONTENT)
    rows, cols = np.nonzero(content)
    if rows.size < 18:  # at least an avatar block and a goal block
        return None
    r0, c0 = int(rows.min()), int(cols.min())
    rmax, cmax = int(rows.max()), int(cols.max())
    # Every content pixel sits in the room band of the 6-pitch lattice.
    if ((rows - r0) % _PITCH >= _ROOM).any() or ((cols - c0) % _PITCH >= _ROOM).any():
        return None
    # Every door pixel sits in exactly one inter-room band, inside the extent.
    drows, dcols = np.nonzero(body == _DOOR)
    if drows.size:
        if drows.min() < r0 or dcols.min() < c0 or drows.max() > rmax or dcols.max() > cmax:
            return None
        in_row_band = (drows - r0) % _PITCH < _ROOM
        in_col_band = (dcols - c0) % _PITCH < _ROOM
        if not (in_row_band ^ in_col_band).all():
            return None
    nr = (rmax - r0) // _PITCH + 1
    nc = (cmax - c0) // _PITCH + 1
    rooms: set[Room] = set()
    avatar: Room | None = None
    goal: Room | None = None
    statics: dict[Room, tuple[int, int] | None] = {}
    patrollers: list[tuple[Room, tuple[int, int] | None]] = []
    chasers: list[tuple[Room, tuple[int, int] | None, bool]] = []
    for i in range(nr):
        for j in range(nc):
            block = body[r0 + _PITCH * i : r0 + _PITCH * i + _ROOM,
                         c0 + _PITCH * j : c0 + _PITCH * j + _ROOM]
            if block.shape != (_ROOM, _ROOM):
                if (np.isin(block, _CONTENT)).any():
                    return None  # content block clipped by the frame edge
                continue
            values = frozenset(int(v) for v in np.unique(block))
            if values == {_BG}:
                continue
            if _BG in values or _DOOR in values:
                return None  # partial block or door bleeding into a room slot
            room = (i, j)
            if values == {_GOAL}:
                if goal is not None:
                    return None
                goal = room
            elif values not in _ROOM_SETS:
                return None
            rooms.add(room)
            if _AVATAR in values:
                if avatar is not None:
                    return None
                eye = _eye_facing(block, _AVATAR_EYE)
                if _AVATAR_EYE in values and eye is None:
                    return None
                avatar = room
            if _SENTINEL in values:
                statics[room] = (
                    _eye_facing(block, _ENEMY_EYE) or _eye_facing(block, _ARMED_EYE)
                )
            if _PATROLLER in values:
                patrollers.append((
                    room,
                    _eye_facing(block, _ENEMY_EYE) or _eye_facing(block, _ARMED_EYE),
                ))
            if _CHASER in values:
                armed = _ARMED_EYE in values
                facing = _eye_facing(block, _ARMED_EYE if armed else _ENEMY_EYE)
                chasers.append((room, facing, armed))
    if avatar is None or len(rooms) < 4:
        return None
    if goal is None and not (patrollers or chasers):
        # Only a moving enemy can cover the goal room (measured on L5).
        return None
    # Doors: each colour-2 patch must be a full 3x3 block joining two rooms.
    doors: set[frozenset[Room]] = set()
    for i, j in rooms:
        for di, dj in ((0, 1), (1, 0)):
            other = (i + di, j + dj)
            region = body[r0 + _PITCH * i + _ROOM * di : r0 + _PITCH * i + _ROOM * di + _ROOM,
                          c0 + _PITCH * j + _ROOM * dj : c0 + _PITCH * j + _ROOM * dj + _ROOM]
            if region.size == 0 or not (region == _DOOR).any():
                continue
            if region.shape != (_ROOM, _ROOM) or not (region == _DOOR).all():
                return None
            if other not in rooms:
                return None
            doors.add(frozenset({(i, j), other}))
    if not doors:
        return None
    if drows.size and int(drows.size) != len(doors) * _ROOM * _ROOM:
        return None  # a door patch not sitting between two rooms
    return MazeParse(
        r0=r0, c0=c0, rooms=frozenset(rooms), doors=frozenset(doors),
        avatar=avatar, goal=goal, statics=statics, patrollers=patrollers,
        chasers=chasers, timer_pixels=n6,
    )


def _step_patroller(
    pos: Room, fac: tuple[int, int], doors: frozenset[frozenset[Room]]
) -> tuple[Room, tuple[int, int]]:
    """One world tick of the measured patroller rule: advance through an open
    door along the facing, then flip the facing immediately on a wall."""

    ahead = (pos[0] + fac[0], pos[1] + fac[1])
    if frozenset({pos, ahead}) in doors:
        pos = ahead
    ahead = (pos[0] + fac[0], pos[1] + fac[1])
    if frozenset({pos, ahead}) not in doors:
        fac = (-fac[0], -fac[1])
    return pos, fac


def _los(
    home: Room, fac: tuple[int, int], doors: frozenset[frozenset[Room]]
) -> frozenset[Room]:
    """Open-door line of rooms in the facing direction, nearest first."""

    out: list[Room] = []
    cur = home
    while frozenset({cur, (cur[0] + fac[0], cur[1] + fac[1])}) in doors:
        cur = (cur[0] + fac[0], cur[1] + fac[1])
        out.append(cur)
    return frozenset(out)


class LockstepMazeArchetype:
    """Parser + BFS planner for the lockstep maze; one step per call."""

    name = "lockstep_maze"

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear all per-life state (called on RESET and level advance)."""

        self._origin: tuple[int, int] | None = None
        self._trail: list[Room] = []
        self._goal: Room | None = None
        self._chaser_facings: dict[Room, tuple[int, int]] = {}
        self._statics_model: dict[Room, tuple[int, int] | None] = {}
        self._chasers_dormant: dict[Room, tuple[int, int]] = {}
        self._chase_active = False
        self._pat_model: list[tuple[Room, tuple[int, int]]] | None = None
        self._plan_actions: list[int] = []
        self._plan_rooms: list[Room] = []
        self._plan_alive: list[frozenset[Room]] = []
        self._expected_room: Room | None = None
        self._expected_alive: frozenset[Room] | None = None

    # ------------------------------------------------------------- contract

    def match(self, grid: NDArray[np.integer]) -> MazeParse | None:
        parse = _parse_maze(np.asarray(grid, dtype=np.int16))
        if parse is None:
            return None
        if parse.goal is None and self._goal is None:
            # A covered goal is only workable with a within-life memory of
            # where the goal was; without one this frame is unplannable.
            return None
        return parse

    def next_actions(self, parse: MazeParse, grid: NDArray[np.integer]) -> list[Step]:
        del grid  # the parse already carries everything derived from it
        moved = self._update_life_state(parse)
        goal = parse.goal if parse.goal is not None else self._goal
        if goal is None:
            return self._drop_plan()
        patrollers, from_model = self._reconcile_patrollers(parse)
        if patrollers is None:
            return self._drop_plan()
        alive_now = frozenset(self._statics_model) | frozenset(self._chasers_dormant)
        if (
            self._plan_actions
            and moved
            and parse.avatar == self._expected_room
            and alive_now == self._expected_alive
            and not self._chase_active  # replan every turn while chased
            and (from_model or not patrollers)
        ):
            return self._emit()
        return self._replan(parse, goal, patrollers)

    # ------------------------------------------------------ per-life memory

    def _update_life_state(self, parse: MazeParse) -> bool:
        """Track the avatar trail (world tick = successful move), the goal
        room, the persistent enemy models, and the stepped patroller model."""

        if self._origin is not None and self._origin != (parse.r0, parse.c0):
            self.reset()  # a different board without a reset notification
        self._origin = (parse.r0, parse.c0)
        moved = False
        if not self._trail:
            self._trail = [parse.avatar]
        elif parse.avatar != self._trail[-1]:
            if frozenset({parse.avatar, self._trail[-1]}) not in parse.doors:
                # The avatar teleported: an unnotified life boundary.
                self.reset()
                self._origin = (parse.r0, parse.c0)
                self._trail = [parse.avatar]
            else:
                moved = True
                self._trail.append(parse.avatar)
                if self._pat_model is not None:
                    self._pat_model = [
                        _step_patroller(pos, fac, parse.doors)
                        for pos, fac in self._pat_model
                    ]
        if parse.goal is not None:
            self._goal = parse.goal
        # Sentinels: persist while hidden under a crossing patroller; they
        # only die to the avatar's own entry into their room.
        for room, fac in parse.statics.items():
            if fac is not None or room not in self._statics_model:
                self._statics_model[room] = fac
        self._statics_model.pop(parse.avatar, None)
        # Dormant chasers: persist likewise; an armed (11) eye or an eyeless
        # 13 anywhere means a chase is on.
        for room, fac, armed in parse.chasers:
            self._statics_model.pop(room, None)  # a 13 is never an 8
            if fac is not None and not armed:
                self._chaser_facings[room] = fac
                self._chasers_dormant[room] = fac
            else:
                if fac is not None:
                    self._chaser_facings[room] = fac
                self._chase_active = True
                self._chasers_dormant.pop(room, None)
        self._chasers_dormant.pop(parse.avatar, None)
        return moved

    def _reconcile_patrollers(
        self, parse: MazeParse
    ) -> tuple[list[tuple[Room, tuple[int, int]]] | None, bool]:
        """Prefer the stepped model when the grid confirms its positions
        (two patrollers passing through each other render as one block and
        lose their separate eyes); otherwise re-read facings from the eyes;
        otherwise abstain rather than guess a trajectory."""

        grid_rooms = sorted(room for room, _ in parse.patrollers)
        if not parse.patrollers and self._pat_model is None:
            self._pat_model = []
            return [], True
        if self._pat_model is not None:
            model_rooms = sorted(pos for pos, _ in self._pat_model)
            if model_rooms == grid_rooms:
                return list(self._pat_model), True
            # MEASURED (L6): a patroller crossing a sentinel's room can be
            # the hidden sprite that tick, and two patrollers passing
            # through each other collapse into one block -- so the grid can
            # UNDERCOUNT patrollers. Keep the stepped model whenever every
            # visible patroller is where the model predicts one.
            if set(grid_rooms) <= set(model_rooms):
                return list(self._pat_model), True
        if len(set(grid_rooms)) == len(grid_rooms) and all(
            fac is not None for _, fac in parse.patrollers
        ):
            fresh = [(room, fac) for room, fac in parse.patrollers if fac is not None]
            self._pat_model = fresh
            return list(fresh), False
        return None, False

    # -------------------------------------------------------------- planner

    def _drop_plan(self) -> list[Step]:
        self._plan_actions = []
        self._plan_rooms = []
        self._plan_alive = []
        self._expected_room = None
        self._expected_alive = None
        return []

    def _emit(self) -> list[Step]:
        action = self._plan_actions.pop(0)
        self._expected_room = self._plan_rooms.pop(0)
        self._expected_alive = self._plan_alive.pop(0)
        return [Step(action=action)]

    def _replan(
        self,
        parse: MazeParse,
        goal: Room,
        patrollers: list[tuple[Room, tuple[int, int]]],
    ) -> list[Step]:
        self._drop_plan()
        infos = []
        for room, fac in self._chasers_dormant.items():
            infos.append(dict(
                home=room, facing=fac,
                faced=(room[0] + fac[0], room[1] + fac[1]),
                los=_los(room, fac, parse.doors), state0=0,
            ))
        if self._chase_active:
            armed = [(r, f) for r, f, a in parse.chasers if a and f is not None]
            eyeless = [r for r, f, _ in parse.chasers if f is None]
            if armed:
                # Triggered this tick, still at home with the armed (11) eye
                # showing the facing: it enters its faced room next tick.
                room, fac = armed[0]
                infos.append(dict(
                    home=room, facing=None,
                    faced=(room[0] + fac[0], room[1] + fac[1]),
                    los=frozenset(), state0=1,
                ))
            else:
                # Mid-chase (possibly hidden under a patroller this tick):
                # its position is the avatar's own room of two ticks ago,
                # and its co-entry rule reduces to forbidding prev.
                home = eyeless[0] if eyeless else (
                    self._trail[-3] if len(self._trail) >= 3 else parse.avatar
                )
                infos.append(dict(
                    home=home, facing=None, faced=None,
                    los=frozenset(), state0=2,
                ))
        prev_root = self._trail[-2] if len(self._trail) >= 2 else None
        # Timer bound: every action costs >= 1 timer pixel (measured minimum
        # 1.28 px/action), so the remaining pixels cap any survivable plan.
        horizon = min(_MAX_HORIZON, parse.timer_pixels)
        statics = dict(self._statics_model)
        path = _plan_route(parse, goal, statics, patrollers, infos, prev_root, horizon)
        if not path:
            return []
        static_rooms = frozenset(statics)
        chaser_homes = [info["home"] for info in infos]
        for action, state in path:
            _, _, _, dead, cds = state
            alive = (static_rooms - dead) | frozenset(
                home for idx, home in enumerate(chaser_homes) if cds[idx] == 0
            )
            self._plan_actions.append(action)
            self._plan_rooms.append(state[0])
            self._plan_alive.append(alive)
        return self._emit()


def _plan_route(
    parse: MazeParse,
    goal: Room,
    statics: dict[Room, tuple[int, int] | None],
    patrollers: list[tuple[Room, tuple[int, int]]],
    chaser_infos: list[dict],
    prev_root: Room | None,
    horizon: int,
) -> list[tuple[int, tuple]] | None:
    """BFS over (room, prev room, tick, dead enemies, chaser states).

    A direct port of the dossier's verified planner2.py: patroller positions
    are pure functions of the tick; a chasing chaser occupies the avatar's
    room of two ticks ago, so co-entry is exactly ``next == prev``; a
    dormant chaser is a sentinel whose line of sight arms the chase.
    Returns [(action, state_after)], shortest in moves, or None.
    """

    doors = parse.doors
    rooms = parse.rooms
    trajs: list[list[Room]] = []
    for pos, fac in patrollers:
        traj = [pos]
        p, f = pos, fac
        for _ in range(horizon + 1):
            p, f = _step_patroller(p, f, doors)
            traj.append(p)
        trajs.append(traj)
    track_prev = bool(chaser_infos)
    track_t = bool(trajs)

    def make_key(state: tuple) -> tuple:
        cur, prv, t, dead, cds = state
        return (cur, prv if track_prev else None, t if track_t else 0, dead, cds)

    root = (parse.avatar, prev_root, 0, frozenset(), tuple(i["state0"] for i in chaser_infos))
    root_key = make_key(root)
    prev_map: dict[tuple, tuple | None] = {root_key: None}
    queue = deque([(root, root_key)])
    nodes = 0
    goal_key = None
    while queue:
        state, key = queue.popleft()
        cur, prv, t, dead, cds = state
        if cur == goal:
            goal_key = key
            break
        if t >= horizon:
            continue
        for action, (di, dj) in _DIRS.items():
            nxt = (cur[0] + di, cur[1] + dj)
            if nxt not in rooms or frozenset({cur, nxt}) not in doors:
                continue
            ndead = dead
            ncds = list(cds)
            ok = True
            for room, fac in statics.items():
                if room in ndead:
                    continue
                if fac is not None and (room[0] + fac[0], room[1] + fac[1]) == nxt:
                    ok = False  # the faced adjacent room: lunge death
                    break
                if room == nxt:
                    if fac is not None and (di, dj) == (-fac[0], -fac[1]):
                        ok = False  # frontal entry
                        break
                    ndead = ndead | {room}  # side/back entry kills it
            if not ok:
                continue
            for traj in trajs:
                if traj[t + 1] == nxt or (traj[t] == nxt and traj[t + 1] == cur):
                    ok = False  # co-entry, or swap-through
                    break
            if not ok:
                continue
            for idx, info in enumerate(chaser_infos):
                cstate = cds[idx]
                if cstate == 0:
                    if nxt == info["faced"]:
                        ok = False  # lunge, same as a sentinel
                        break
                    if nxt == info["home"]:
                        facing = info["facing"]
                        if facing is not None and (di, dj) == (-facing[0], -facing[1]):
                            ok = False
                            break
                        ncds[idx] = 3  # killed from the side/back
                        ndead = ndead | {info["home"]}
                    elif nxt in info["los"]:
                        ncds[idx] = 1  # entered its line of sight: triggered
                elif cstate == 1:
                    # One tick after the trigger the chaser enters its faced
                    # room; from then on it is on the avatar's lag-2 trail.
                    if info["faced"] is not None and nxt == info["faced"]:
                        ok = False
                        break
                    ncds[idx] = 2
                elif cstate == 2:
                    if prv is not None:
                        if nxt == prv:
                            ok = False  # re-entering after exactly 2 ticks
                            break
                    elif nxt == info["home"] or frozenset({info["home"], nxt}) in doors:
                        # ASSUMPTION (unknown-history fallback): seated
                        # mid-chase with no trail memory, the chaser's next
                        # room is unknown but door-adjacent to it; forbid
                        # that neighbourhood for the first planned tick.
                        ok = False
                        break
            if not ok:
                continue
            nstate = (nxt, cur, t + 1, ndead, tuple(ncds))
            nkey = make_key(nstate)
            if nkey in prev_map:
                continue
            prev_map[nkey] = (key, action, nstate)
            nodes += 1
            if nodes > _NODE_CAP:
                return None
            queue.append((nstate, nkey))
    if goal_key is None:
        return None
    path: list[tuple[int, tuple]] = []
    walk = goal_key
    while prev_map[walk] is not None:
        parent_key, action, state = prev_map[walk]
        path.append((action, state))
        walk = parent_key
    return path[::-1]
