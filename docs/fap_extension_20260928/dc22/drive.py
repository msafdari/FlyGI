import sys, importlib.util, json
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

def show_diff(g0, g1, label):
    if g0 is None or g1 is None:
        print(label, 'grid None'); return
    d = np.argwhere(g0 != g1)
    print(f'{label}: {len(d)} cells changed')
    if len(d) and len(d) <= 80:
        for (r, c) in d:
            print(f'  r{r} c{c}: {g0[r,c]:x} -> {g1[r,c]:x}')
    elif len(d):
        rows = sorted(set(int(r) for r, c in d)); cols = sorted(set(int(c) for r, c in d))
        print(f'  rows {rows[0]}-{rows[-1]} cols {cols[0]}-{cols[-1]}')

def render(gr, path):
    lines = []
    lines.append('    ' + ''.join(str(c % 10) for c in range(64)))
    for r in range(64):
        lines.append(f'{r:3d} ' + ''.join(format(int(v), 'x') for v in gr[r]))
    Path(path).write_text('\n'.join(lines) + '\n')

frame = env.observation_space
g0 = grid_of(frame)
print('initial', frame.state, frame.levels_completed, frame.available_actions)

# Probe each arrow action from fresh state, with RESET between
steps = []
for aid in (1, 2, 3, 4):
    fr = act(aid)
    g1 = grid_of(fr)
    show_diff(g0, g1, f'action {aid}')
    print('  state', fr.state, 'score', fr.levels_completed)
    fr = act(0)  # RESET
    g0r = grid_of(fr)
    if g0r is not None:
        same = np.array_equal(g0r, g0)
        print('  after reset identical to initial:', same)
        g0 = g0r
