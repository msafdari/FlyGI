import sys, importlib.util, json
from pathlib import Path
ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI'); sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from collections import deque
from flygi.encoding.features import latest_grid

def grid_of(frame): return np.asarray(latest_grid(frame), dtype=np.int16)

def parse_maze(gr):
    cells = np.argwhere((gr==0)|(gr==9)|(gr==14)|(gr==4))
    if len(cells)==0: return None
    r0, c0 = int(cells[:,0].min()), int(cells[:,1].min())
    rmax, cmax = int(cells[:,0].max()), int(cells[:,1].max())
    nrows = (rmax - r0) // 6 + 1
    ncols = (cmax - c0) // 6 + 1
    rooms = {(i,j): int(gr[r0+6*i, c0+6*j]) for i in range(nrows) for j in range(ncols)}
    def door_open(i,j,di,dj):
        return gr[r0+6*i+3*di, c0+6*j+3*dj] == 2
    return r0, c0, nrows, ncols, rooms, door_open

def bfs_path(gr):
    parsed = parse_maze(gr)
    if parsed is None: return None, None, None, None
    r0,c0,nr,nc,rooms,door_open = parsed
    start = goal = None
    for (i,j),v in rooms.items():
        if v in (9,4): start=(i,j)
        if v==14: goal=(i,j)
    if start is None or goal is None: return None, start, goal, (nr,nc)
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur==goal: break
        i,j = cur
        for a,(di,dj) in [(1,(-1,0)),(2,(1,0)),(3,(0,-1)),(4,(0,1))]:
            ni,nj = i+di, j+dj
            if 0<=ni<nr and 0<=nj<nc and (ni,nj) not in prev and door_open(i,j,di,dj):
                prev[(ni,nj)] = (cur, a); q.append((ni,nj))
    if goal not in prev: return None, start, goal, (nr,nc)
    path = []; cur = goal
    while prev[cur] is not None:
        p,a = prev[cur]; path.append(a); cur = p
    return path[::-1], start, goal, (nr,nc)

rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['tu93'])[0]
arc = b._new_offline_arcade(rt, ROOT/'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed,_ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)
def act(i):
    a = rt.GameAction.from_id(i)
    return env.step(a, data={}, reasoning=None)

programs = []
f = env.observation_space
level = 0
total_actions = 0
while level < 9 and str(f.state) != 'GameState.WIN' and total_actions < 600:
    try:
        gr = grid_of(f)
    except Exception as e:
        print("empty frame, nudging with UP"); f = act(1); total_actions += 1; continue
    np.save(f'/tmp/fap_ext/tu93/level{level+1}_start.npy', gr)
    path, start, goal, shape = bfs_path(gr)
    print(f"LEVEL {level+1}: shape={shape} start={start} goal={goal} path_len={len(path) if path else None}")
    if path is None:
        print("NO PATH FOUND — dumping and stopping"); break
    steps = []
    fell = False
    before = f.levels_completed
    for a in path:
        f = act(a); total_actions += 1
        steps.append(a)
        if f.levels_completed > before:
            fell = True; break
        if str(f.state) == 'GameState.WIN':
            fell = True; break
    timer_px = None
    try:
        gg = grid_of(f); timer_px = int((gg[63]==6).sum())
    except Exception: pass
    print(f"  executed {len(steps)} steps; levels={f.levels_completed} state={f.state} fell={fell} timer_after={timer_px}")
    programs.append({"level": level+1, "actions": steps, "fell": fell,
                     "score_after": int(f.levels_completed), "state": str(f.state)})
    if not fell:
        print("  program exhausted without level fall — stopping for diagnosis"); break
    level = f.levels_completed

print("FINAL:", f.levels_completed, f.state, "total_actions:", total_actions)
json.dump(programs, open('/tmp/fap_ext/tu93/programs_all.json','w'), indent=1)
