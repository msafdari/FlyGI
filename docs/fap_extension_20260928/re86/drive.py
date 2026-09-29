import sys, importlib.util, json
from pathlib import Path
ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI'); sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from flygi.encoding.features import latest_grid

rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['re86'])[0]
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

def diff(g0, g1):
    if g0 is None or g1 is None: return "one grid None"
    ch = np.argwhere(g0 != g1)
    out = []
    for (r, c) in ch:
        out.append((int(r), int(c), int(g0[r, c]), int(g1[r, c])))
    return out

def summ(frame):
    return dict(state=str(frame.state), score=frame.levels_completed, avail=frame.available_actions)
