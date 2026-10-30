import sys, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np, heapq
from collections import deque
from flygi.encoding.features import latest_grid
def grid_of(f): return np.asarray(latest_grid(f), dtype=np.int16)

DIRS = {1:(-1,0), 2:(1,0), 3:(0,-1), 4:(0,1)}

def parse_maze(gr):
    cells = np.argwhere((gr==0)|(gr==9)|(gr==14)|(gr==4)|(gr==8)|(gr==15))
    if len(cells)==0: return None
    r0, c0 = int(cells[:,0].min()), int(cells[:,1].min())
    rmax, cmax = int(cells[:,0].max()), int(cells[:,1].max())
    nr = (rmax - r0)//6 + 1; nc = (cmax - c0)//6 + 1
    start = goal = None; enemies = {}
    for i in range(nr):
        for j in range(nc):
            block = gr[r0+6*i:r0+6*i+3, c0+6*j:c0+6*j+3]
            vals = set(block.flatten().tolist())
            if 9 in vals: start = (i,j)
            if 14 in vals: goal = (i,j)
            if 8 in vals:
                fy, fx = None, None
                loc = np.argwhere(block==15)
                if len(loc):
                    dy, dx = int(loc[0][0])-1, int(loc[0][1])-1
                    enemies[(i,j)] = (dy,dx)   # facing unit vector
                else:
                    enemies[(i,j)] = None
    def door_open(i,j,di,dj):
        rr, cc = r0+6*i+3*di, c0+6*j+3*dj
        if not (0<=rr<64 and 0<=cc<64): return False
        return gr[rr,cc] == 2
    def is_room(i,j):
        if not (0<=i<nr and 0<=j<nc): return False
        v = gr[r0+6*i, c0+6*j]
        return v in (0,9,14,8,4) or int(gr[r0+6*i+1, c0+6*j+1]) in (0,9,14,8,15,4)
    return dict(r0=r0,c0=c0,nr=nr,nc=nc,start=start,goal=goal,enemies=enemies,
                door_open=door_open,is_room=is_room)

def solve(gr):
    m = parse_maze(gr)
    if m is None or m['start'] is None or m['goal'] is None: return None, m
    enemies = m['enemies']; door_open = m['door_open']
    start_state = (m['start'], frozenset())
    prev = {start_state: None}
    q = deque([start_state])
    goal_state = None
    while q:
        st = q.popleft()
        (i,j), dead = st
        if (i,j) == m['goal']: goal_state = st; break
        for a,(di,dj) in DIRS.items():
            ni,nj = i+di, j+dj
            if not door_open(i,j,di,dj): continue
            ndead = dead
            if (ni,nj) in enemies and (ni,nj) not in dead:
                fac = enemies[(ni,nj)]
                # entering the enemy's room: lethal if we come from the room it faces
                # i.e. our movement vector == opposite of facing means we entered from facing side
                if fac is not None and (di,dj) == (-fac[0],-fac[1]):
                    continue  # frontal entry = death (measured: facing-adjacent room is lethal anyway)
                ndead = dead | {(ni,nj)}
            # forbid rooms that a live enemy faces into (distance 1)
            lethal = False
            for e,fac in enemies.items():
                if e in ndead or fac is None: continue
                if (e[0]+fac[0], e[1]+fac[1]) == (ni,nj):
                    lethal = True; break
            if lethal: continue
            nst = ((ni,nj), ndead)
            if nst not in prev:
                prev[nst] = (st, a); q.append(nst)
    if goal_state is None: return None, m
    path = []; cur = goal_state
    while prev[cur] is not None:
        p,a = prev[cur]; path.append(a); cur = p
    return path[::-1], m

rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['tu93'])[0]
arc = b._new_offline_arcade(rt, ROOT/'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed,_ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)
def act(i):
    a = rt.GameAction.from_id(i)
    return env.step(a, data={}, reasoning=None)

f = env.observation_space
programs = []; total = 0
while f.levels_completed < 9 and str(f.state) not in ('GameState.WIN',) and total < 800:
    if str(f.state) == 'GameState.GAME_OVER':
        print("GAME_OVER — stopping"); break
    try: gr = grid_of(f)
    except Exception:
        f = act(1); total += 1; continue
    lv = f.levels_completed
    np.save(f'/tmp/fap_ext/tu93/level{lv+1}_start.npy', gr)
    path, m = solve(gr)
    en = {k: v for k,v in m['enemies'].items()} if m else None
    print(f"LEVEL {lv+1}: grid {m['nr']}x{m['nc']} start={m['start']} goal={m['goal']} enemies={en} path_len={len(path) if path else None}")
    if path is None:
        print("  NO PATH — stopping for manual look"); break
    before = lv; steps=[]; fell=False
    for a in path:
        f = act(a); total += 1; steps.append(a)
        if str(f.state)=='GameState.GAME_OVER': break
        if f.levels_completed > before or str(f.state)=='GameState.WIN':
            fell=True; break
    t = None
    try: t = int((grid_of(f)[63]==6).sum())
    except Exception: pass
    print(f"  executed {len(steps)}: fell={fell} lv={f.levels_completed} {f.state} timer={t}")
    programs.append({"level": before+1, "actions": steps, "fell": fell,
                     "levels_after": int(f.levels_completed), "state": str(f.state)})
    if not fell: break
print("FINAL:", f.levels_completed, f.state, "total actions:", total)
json.dump(programs, open('/tmp/fap_ext/tu93/programs_all.json','w'), indent=1)
