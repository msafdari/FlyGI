"""tu93 planner v2: statics(8), patrollers(12), trail-chasers(13)."""
import numpy as np
from collections import deque

DIRS = {1:(-1,0), 2:(1,0), 3:(0,-1), 4:(0,1)}

def parse(gr):
    cells = np.argwhere((gr==0)|(gr==9)|(gr==14)|(gr==4)|(gr==8)|(gr==15)|(gr==12)|(gr==13))
    r0, c0 = int(cells[:,0].min()), int(cells[:,1].min())
    rmax, cmax = int(cells[:,0].max()), int(cells[:,1].max())
    nr = (rmax-r0)//6 + 1; nc = (cmax-c0)//6 + 1
    start = goal = None; statics = {}; movers = []; chasers = []
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
            if 13 in vals: chasers.append(((i,j), fac))
    def door(i,j,di,dj):
        rr, cc = r0+6*i+3*di, c0+6*j+3*dj
        if not (0<=rr<64 and 0<=cc<64): return False
        return gr[rr,cc] == 2 and (i+di, j+dj) in rooms
    return dict(r0=r0,c0=c0,nr=nr,nc=nc,rooms=rooms,start=start,goal=goal,
                statics=statics,movers=movers,chasers=chasers,door=door)

def mover_traj(m, mover, L):
    (pos, fac) = mover
    traj = [(pos, fac)]
    door = m['door']
    for _ in range(L):
        if door(pos[0], pos[1], fac[0], fac[1]):
            pos = (pos[0]+fac[0], pos[1]+fac[1])
        if not door(pos[0], pos[1], fac[0], fac[1]):
            fac = (-fac[0], -fac[1])
        traj.append((pos, fac))
    return traj

def los(m, pos, fac):
    """Open-door line of rooms in facing direction, nearest first."""
    out = []
    cur = pos
    while m['door'](cur[0], cur[1], fac[0], fac[1]):
        cur = (cur[0]+fac[0], cur[1]+fac[1])
        out.append(cur)
    return out

def plan(gr, max_t=300, modL=None):
    m = parse(gr)
    assert m['start'] and m['goal']
    trajs = [mover_traj(m, mv, max_t+2) for mv in m['movers']]
    door = m['door']
    # only support 0 or 1 chaser (levels seen so far)
    assert len(m['chasers']) <= 1
    ch = m['chasers'][0] if m['chasers'] else None
    ch_los = los(m, ch[0], ch[1]) if ch else []
    if modL is None: modL = 24*7*5   # generous cycle for dedup of patroller phase
    # state: (cur, prev, t, dead_statics, dstate) ; dstate: 0 dorm,1 justtrig,2 chase,3 dead
    st0 = (m['start'], None, 0, frozenset(), 0 if ch else 3)
    prev = {(m['start'], None, 0, frozenset(), 0 if ch else 3): None}
    q = deque([st0])
    goal_state = None
    while q:
        st = q.popleft()
        (cur, prv, t, dead, dstate) = st
        if cur == m['goal']: goal_state = st; break
        if t >= max_t: continue
        for a,(di,dj) in DIRS.items():
            if not door(cur[0], cur[1], di, dj): continue
            nxt = (cur[0]+di, cur[1]+dj)
            ndead = dead; nds = dstate
            bad = False
            # statics
            for spos, sfac in m['statics'].items():
                if spos in dead: continue
                if sfac is not None and (spos[0]+sfac[0], spos[1]+sfac[1]) == nxt:
                    bad = True; break
                if spos == nxt:
                    if sfac is not None and (di,dj) == (-sfac[0], -sfac[1]): bad = True; break
                    ndead = ndead | {spos}
            if bad: continue
            # patrollers
            for tr in trajs:
                mp_old,_ = tr[t]; mp_new,_ = tr[t+1]
                if mp_new == nxt: bad = True; break
                if mp_old == nxt and mp_new == cur: bad = True; break
            if bad: continue
            # chaser
            if ch and dstate == 0:  # dormant: acts like a static sentinel
                cpos, cfac = ch
                faced = (cpos[0]+cfac[0], cpos[1]+cfac[1])
                if nxt == faced: continue           # lunge = death
                if nxt == cpos:
                    if (di,dj) == (-cfac[0], -cfac[1]): continue
                    nds = 3                          # killed it
                elif nxt in ch_los:                  # deeper LOS: trigger the chase
                    nds = 1
            elif ch and dstate == 1:  # just triggered: chaser now enters its faced room
                cpos, cfac = ch
                faced = (cpos[0]+cfac[0], cpos[1]+cfac[1])
                if nxt == faced: continue
                nds = 2
            elif ch and dstate == 2:  # chasing with lag 2: it moves to our room of 2 ticks ago
                if nxt == prv: continue              # return-after-2 = co-entry
            nst = (nxt, cur, t+1, ndead, nds)
            key = (nxt, cur, (t+1) % modL if (t+1)>=modL else t+1, ndead, nds)
            if key not in prev:
                prev[key] = (st, a); q.append(nst)
    if goal_state is None: return None, m
    path = []; curst = goal_state
    while prev[(curst[0], curst[1], curst[2]%modL if curst[2]>=modL else curst[2], curst[3], curst[4])] is not None:
        p, a = prev[(curst[0], curst[1], curst[2]%modL if curst[2]>=modL else curst[2], curst[3], curst[4])]
        path.append(a); curst = p
    return path[::-1], m
