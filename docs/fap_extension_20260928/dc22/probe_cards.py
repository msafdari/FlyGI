import sys, importlib.util
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
from flygi.encoding.features import latest_grid

rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['dc22'])[0]
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

def render(gr, path):
    lines = ['    ' + ''.join(str(c % 10) for c in range(64))]
    for r in range(64):
        lines.append(f'{r:3d} ' + ''.join(format(int(v), 'x') for v in gr[r]))
    Path(path).write_text('\n'.join(lines) + '\n')

fr = act(6, {'x': 48, 'y': 19})
render(grid_of(fr), '/tmp/fap_ext/dc22/after_click_card8.txt')
print('card8 click:', fr.state, fr.levels_completed)
fr = act(0)
fr = act(6, {'x': 48, 'y': 36})
render(grid_of(fr), '/tmp/fap_ext/dc22/after_click_card9.txt')
print('card9 click:', fr.state, fr.levels_completed)
