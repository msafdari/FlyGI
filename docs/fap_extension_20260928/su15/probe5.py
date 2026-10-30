import sys, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from flygi.encoding.features import latest_grid
rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['su15'])[0]
arc = b._new_offline_arcade(rt, ROOT/'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed,_ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)

def act(i, payload=None):
    a = rt.GameAction.from_id(i)
    if payload: a.set_data(payload)
    return env.step(a, data=payload or {}, reasoning=None)

def grid_of(frame):
    try:
        return np.asarray(latest_grid(frame), dtype=np.int16)
    except Exception:
        return None

def diff(tag, prev, frame, show=30):
    gr = grid_of(frame)
    if gr is None:
        print(f'{tag}: EMPTY score={frame.levels_completed} state={frame.state}')
        return prev
    d = [(int(r),int(c)) for r,c in np.argwhere(gr != prev) if r != 63]
    print(f'{tag}: score={frame.levels_completed} avail={frame.available_actions} ndiff={len(d)}')
    for (r,c) in d[:show]:
        print(f'   ({r},{c}) {prev[r,c]} -> {gr[r,c]}')
    return gr

L1 = [(53,10),(47,16),(41,22),(35,28),(29,34),(23,40),(17,46)]
f = env.observation_space
for (r,c) in L1:
    f = act(6, {'x':int(c), 'y':int(r)})
f = act(1)  # surface level 2 frame
gr = grid_of(f)
print('level2 avail:', f.available_actions, 'score', f.levels_completed)

gr = diff('click disc centre (27,33)', gr, act(6, {'x':33,'y':27}))
gr = diff('click (30,33) lower disc', gr, act(6, {'x':33,'y':30}))
gr = diff('click a-cell (37,41)', gr, act(6, {'x':41,'y':37}))
gr = diff('click bg (35,35)', gr, act(6, {'x':35,'y':35}))
gr = diff('action 7', gr, act(7))
gr = diff('click a-cell (40,37)', gr, act(6, {'x':37,'y':40}))
gr = diff('click bg near disc (33,38)', gr, act(6, {'x':38,'y':33}))
