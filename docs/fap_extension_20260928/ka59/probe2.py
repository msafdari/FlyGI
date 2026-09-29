import sys, importlib.util
from pathlib import Path
ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI'); sys.path.insert(0, str(ROOT/'src'))
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

def grid_of():
    try:
        return np.asarray(latest_grid(env.observation_space), dtype=np.int16)
    except Exception:
        return None

def render(gr, path):
    with open(path, 'w') as fh:
        fh.write('    ' + ''.join(str(c % 10) for c in range(64)) + '\n')
        for r in range(64):
            fh.write(f'{r:3d} ' + ''.join(f'{v:x}' for v in gr[r]) + '\n')

def summarize(gr, prev, label):
    fs = env.observation_space
    ch = np.argwhere(prev != gr) if prev is not None and gr is not None else []
    # locate player (centre 0) and box (centre 5)
    p0 = np.argwhere(gr == 0); p5 = np.argwhere(gr == 5)
    p0 = [tuple(x) for x in p0 if x[0] < 60]
    p5 = [tuple(x) for x in p5 if x[0] < 60]
    print(f'{label}: state={fs.state} levels={fs.levels_completed} changed={len(ch)} player0@{p0} box5@{p5}')
    return gr

import json
seq = sys.argv[1] if len(sys.argv) > 1 else '4,4,4,4,4'
names = {1:'up',2:'down',3:'left',4:'right'}
prev = grid_of()
summarize(prev, None, 'init')
for k, tok in enumerate(seq.split(',')):
    tok = tok.strip()
    if tok.startswith('c'):
        x, y = tok[1:].split(':')
        act(6, {'x': int(x), 'y': int(y)})
        lbl = f'{k:02d} click({x},{y})'
    else:
        aid = int(tok)
        act(aid)
        lbl = f'{k:02d} {names.get(aid, tok)}'
    gr = grid_of()
    if gr is None:
        print(f'{lbl}: EMPTY frame, state={env.observation_space.state}')
        continue
    prev = summarize(gr, prev, lbl)
render(prev, '/tmp/fap_ext/ka59/last_frame.txt')
print('final render -> /tmp/fap_ext/ka59/last_frame.txt')
