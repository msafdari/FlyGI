import sys, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from flygi.encoding.features import latest_grid
rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['tu93'])[0]
arc = b._new_offline_arcade(rt, ROOT/'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed,_ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)
def act(i, payload=None):
    a = rt.GameAction.from_id(i)
    if payload: a.set_data(payload)
    return env.step(a, data=payload or {}, reasoning=None)
def grid_of(frame):
    return np.asarray(latest_grid(frame), dtype=np.int16)

f0 = env.observation_space
g0 = grid_of(f0)
print("initial score", f0.score if hasattr(f0,'score') else None, "levels", f0.levels_completed, "state", f0.state)

def avatar_pos(gr):
    ys, xs = np.where(gr==9)
    if len(ys)==0: return None
    return (int(ys.min()), int(xs.min()))  # top-left of 3x3

def diff(a, bb):
    ys, xs = np.where(a!=bb)
    if len(ys)==0: return "NO CHANGE"
    return f"changed rows {ys.min()}-{ys.max()} cols {xs.min()}-{xs.max()} ({len(ys)} px)"

print("avatar at", avatar_pos(g0), "row63 unique:", np.unique(g0[63]))
# swallow test: first action after fresh open
f1 = act(2)  # down
g1 = grid_of(f1)
print("after DOWN(first):", diff(g0,g1), "avatar", avatar_pos(g1), "row63:", np.unique(g1[63], return_counts=True))
f2 = act(2)
g2 = grid_of(f2)
print("after DOWN(2nd):", diff(g1,g2), "avatar", avatar_pos(g2), "row63:", np.unique(g2[63], return_counts=True))
f3 = act(4)  # right
g3 = grid_of(f3)
print("after RIGHT:", diff(g2,g3), "avatar", avatar_pos(g3), "row63:", np.unique(g3[63], return_counts=True))
# save tile map of initial
np.save('/tmp/fap_ext/tu93/g0.npy', g0)
np.save('/tmp/fap_ext/tu93/g3.npy', g3)
