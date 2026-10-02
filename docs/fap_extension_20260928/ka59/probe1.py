import sys, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from flygi.encoding.features import latest_grid
rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['ka59'])[0]
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

def diff(g0, g1, label):
    if g1 is None:
        print(label, ': EMPTY FRAME')
        return
    ch = np.argwhere(g0 != g1)
    print(label, f': {len(ch)} cells changed')
    if len(ch) and len(ch) <= 80:
        for r, c in ch:
            print(f'   ({r},{c}) {g0[r,c]:x}->{g1[r,c]:x}')
    elif len(ch):
        rows = sorted(set(int(r) for r,c in ch)); cols = sorted(set(int(c) for r,c in ch))
        print('   rows', rows[:20], 'cols', cols[:20])

f0 = env.observation_space
g0 = grid_of(f0)
print('initial', f0.state, f0.levels_completed, f0.available_actions)

# swallow test: does first post-reset action change the frame?
for aid, name in [(1,'up'),(2,'down'),(3,'left'),(4,'right')]:
    fr = act(0)  # RESET
    gr = grid_of(env.observation_space)
    same = np.array_equal(gr, g0)
    fr = act(aid)
    g1 = grid_of(env.observation_space)
    print(f'--- fresh reset (identical to initial: {same}); first action {name} ->', env.observation_space.state, "levels", env.observation_space.levels_completed)
    diff(gr, g1, f'  {name}')
