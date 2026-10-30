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

def report(tag, prev, frame):
    gr = grid_of(frame)
    if gr is None:
        print(f'{tag}: EMPTY-FRAME state={frame.state} score={frame.levels_completed}')
        return prev
    d = np.argwhere((gr != prev) if prev is not None else np.zeros_like(gr, bool))
    d = [t for t in d if t[0] != 63]
    print(f'{tag}: state={frame.state} score={frame.levels_completed} avail={frame.available_actions} ndiff(non-timer)={len(d)}')
    for (r, c) in d[:25]:
        print(f'   ({r},{c}) {prev[r,c]} -> {gr[r,c]}')
    return gr

frame = env.observation_space
gr = grid_of(frame)
print('initial score', frame.levels_completed, 'avail', frame.available_actions)

# Sequence of clicks to try; each is (x=col, y=row, label)
targets = [
    (12, 51, 'adjacent dash up-path'),
    (12, 51, 'same dash again (swallow test)'),
    (10, 53, 'avatar centre'),
    (8, 55, 'dash below avatar'),
    (4, 59, 'f-block bottom-left centre'),
    (30, 5, 'f-block header centre'),
    (49, 15, 'circle centre'),
    (11, 52, 'cell just above avatar (up)'),
    (10, 52, 'cell directly above avatar'),
]
for (x, y, label) in targets:
    frame = act(6, {'x': int(x), 'y': int(y)})
    gr = report(f'click({x},{y}) {label}', gr, frame)

# also test action 7
try:
    frame = act(7)
    gr = report('action7', gr, frame)
except Exception as e:
    print('action7 raised:', e)
