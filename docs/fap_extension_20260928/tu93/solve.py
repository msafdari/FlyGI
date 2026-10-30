import sys, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from collections import deque
from flygi.encoding.features import latest_grid

def grid_of(frame): return np.asarray(latest_grid(frame), dtype=np.int16)

def parse_maze(gr):
    # find room lattice: rooms are 3x3 at pitch 6. Find avatar(9) and e(14) and 0-rooms.
    # locate lattice origin from 0/9/14 cells
    cells = np.argwhere((gr==0)|(gr==9)|(gr==14)|(gr==4))
    r0, c0 = cells[:,0].min(), cells[:,1].min()
    # room grid size
    rmax, cmax = cells[:,0].max(), cells[:,1].max()
    nrows = (rmax - r0) // 6 + 1
    ncols = (cmax - c0) // 6 + 1
    rooms = {}
    for i in range(nrows):
        for j in range(ncols):
            v = gr[r0+6*i, c0+6*j]
            rooms[(i,j)] = int(v)
    def door_open(i,j,di,dj):
        # door pixel between room (i,j) and (i+di,j+dj)
        rr = r0 + 6*i + 3*di
        cc = c0 + 6*j + 3*dj
        return gr[rr, cc] == 2
    return r0, c0, nrows, ncols, rooms, door_open

def bfs_path(gr):
    r0,c0,nr,nc,rooms,door_open = parse_maze(gr)
    start = goal = None
    for (i,j),v in rooms.items():
        if v in (9,4): start=(i,j)
        if v==14: goal=(i,j)
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur==goal: break
        i,j = cur
        for a,(di,dj) in [(1,(-1,0)),(2,(1,0)),(3,(0,-1)),(4,(0,1))]:
            ni,nj = i+di, j+dj
            if 0<=ni<nr and 0<=nj<nc and (ni,nj) not in prev and door_open(i,j,di,dj):
                prev[(ni,nj)] = (cur, a)
                q.append((ni,nj))
    if goal not in prev: return None, start, goal, (nr,nc)
    path = []
    cur = goal
    while prev[cur] is not None:
        p,a = prev[cur]
        path.append(a); cur = p
    return path[::-1], start, goal, (nr,nc)

if __name__ == '__main__':
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
    g0 = grid_of(f)
    path, start, goal, shape = bfs_path(g0)
    print("maze shape", shape, "start", start, "goal", goal)
    print("path (actions):", path, "len", len(path) if path else None)
    # swallow test: first action = first path action (legal). Does avatar move?
    names={1:'UP',2:'DOWN',3:'LEFT',4:'RIGHT'}
    def av(gr):
        ys,xs = np.where(gr==9)
        return (int(ys.min()), int(xs.min())) if len(ys) else None
    prevg = g0
    timer = lambda gr: int((gr[63]==6).sum())
    print("timer px:", timer(g0))
    for k,a in enumerate(path):
        f = act(a)
        gg = grid_of(f)
        moved = av(gg) != av(prevg)
        print(f"step {k+1}: {names[a]} moved={moved} avatar={av(gg)} timer={timer(gg)} levels={f.levels_completed} state={f.state}")
        prevg = gg
        if f.levels_completed > 0:
            np.save('/tmp/fap_ext/tu93/level2_start.npy', gg)
            print("LEVEL FELL at step", k+1)
            break
    # dump level-2 frame if reached
    f = env.observation_space
    print("final levels:", f.levels_completed, "state:", f.state)
