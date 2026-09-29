"""General tu93 level planner: parse 64x64 frame -> maze + enemies -> time-expanded BFS."""
import numpy as np
from collections import deque

DIRS = {1:(-1,0), 2:(1,0), 3:(0,-1), 4:(0,1)}

def parse(gr):
    cells = np.argwhere((gr==0)|(gr==9)|(gr==14)|(gr==4)|(gr==8)|(gr==15)|(gr==12))
    r0, c0 = int(cells[:,0].min()), int(cells[:,1].min())
    rmax, cmax = int(cells[:,0].max()), int(cells[:,1].max())
    nr = (rmax-r0)//6 + 1; nc = (cmax-c0)//6 + 1
    start = goal = None; statics = {}; movers = []
    rooms = set()
    for i in range(nr):
        for j in range(nc):
            blk = gr[r0+6*i:r0+6*i+3, c0+6*j:c0+6*j+3]
            if blk.shape != (3,3): continue
            vals = set(blk.flatten().tolist())
            if vals == {5}: continue
            rooms.add((i,j))
            if 9 in vals: start = (i,j)
            if 14 in vals: goal = (i,j)
            fac = None
            loc = np.argwhere(blk==15)
            if len(loc): fac = (int(loc[0][0])-1, int(loc[0][1])-1)
            if 8 in vals: statics[(i,j)] = fac
            if 12 in vals: movers.append(((i,j), fac))
    def door(i,j,di,dj):
        rr, cc = r0+6*i+3*di, c0+6*j+3*dj
        if not (0<=rr<64 and 0<=cc<64): return False
        return gr[rr,cc] == 2 and (i+di, j+dj) in rooms
    return dict(r0=r0,c0=c0,nr=nr,nc=nc,rooms=rooms,start=start,goal=goal,
                statics=statics,movers=movers,door=door)

def mover_traj(m, mover, L=400):
    """Deterministic trajectory: list of (pos, facing) for ticks 0..L."""
    (pos, fac) = mover
    traj = [(pos, fac)]
    door = m['door']
    for _ in range(L):
        ni, nj = pos[0]+fac[0], pos[1]+fac[1]
        if door(pos[0], pos[1], fac[0], fac[1]):
            pos = (ni, nj)
        # flip if no onward door
        if not door(pos[0], pos[1], fac[0], fac[1]):
            fac = (-fac[0], -fac[1])
        traj.append((pos, fac))
    return traj

def plan(gr, max_t=200):
    m = parse(gr)
    assert m['start'] and m['goal'], (m['start'], m['goal'])
    trajs = [mover_traj(m, mv, max_t+1) for mv in m['movers']]
    door = m['door']
    st0 = (m['start'], 0, frozenset())
    prev = {(m['start'], 0, frozenset()): None}
    q = deque([st0])
    goal_state = None
    while q:
        st = q.popleft()
        (room, t, dead) = st
        if room == m['goal']: goal_state = st; break
        if t >= max_t: continue
        for a,(di,dj) in DIRS.items():
            if not door(room[0], room[1], di, dj): continue
            nroom = (room[0]+di, room[1]+dj)
            ndead = dead
            # static sentinels
            bad = False
            for spos, sfac in m['statics'].items():
                if spos in dead: continue
                if sfac is not None and (spos[0]+sfac[0], spos[1]+sfac[1]) == nroom:
                    bad = True; break            # faced room = lethal lunge
                if spos == nroom:
                    if sfac is not None and (di,dj) == (-sfac[0], -sfac[1]):
                        bad = True; break        # frontal entry = death
                    ndead = ndead | {spos}        # side/back entry = kill
            if bad: continue
            # movers at tick t -> t+1
            for tr in trajs:
                mp_old, _ = tr[t]; mp_new, _ = tr[t+1]
                if mp_new == nroom: bad = True; break             # co-entry / occupied
                if mp_old == nroom and mp_new == room: bad = True; break   # swap
            if bad: continue
            nst = (nroom, t+1, ndead)
            key = (nroom, t+1, ndead)
            if key not in prev:
                prev[key] = (st, a); q.append(nst)
    if goal_state is None: return None, m
    path = []
    cur = goal_state
    while prev[cur] is not None:
        p, a = prev[cur]; path.append(a); cur = p
    return path[::-1], m
