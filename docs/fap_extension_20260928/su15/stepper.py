"""Replay a click prefix (JSON list of [row,col] or ["a",id]) then print census each step.
Usage: stepper.py prefix.json [extra clicks as r:c args...]
"""
import sys, importlib.util, json
from pathlib import Path
ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI'); sys.path.insert(0, str(ROOT/'src'))
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

def components(gr, col):
    from scipy import ndimage
    mask = np.zeros_like(gr, bool)
    mask[10:63] = (gr[10:63] == col)
    lab, n = ndimage.label(mask, structure=np.ones((3,3)))
    out = []
    for i in range(1, n+1):
        ys, xs = np.where(lab == i)
        out.append((int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max()), len(ys)))
    return out

def census(tag, frame):
    gr = grid_of(frame)
    if gr is None:
        print(f'{tag}: EMPTY score={frame.levels_completed} state={frame.state}')
        return None
    timer = int((gr[63] == 0).sum())
    parts = []
    for col, name in ((10,'a1'),(6,'B2'),(15,'F3'),(11,'b4'),(12,'C5'),(8,'X6'),(7,'P!')):
        for (r0,r1,c0,c1,n) in components(gr, col):
            parts.append(f'{name}[{r0}-{r1},{c0}-{c1}]#{n}')
    print(f'{tag}: score={frame.levels_completed} state={str(frame.state).split(".")[-1]} timer={timer} | ' + ' '.join(parts))
    return gr

L1 = [(53,10),(47,16),(41,22),(35,28),(29,34),(23,40),(17,46)]
f = env.observation_space
for (r,c) in L1:
    f = act(6, {'x':int(c), 'y':int(r)})
f = act(1)
census('L2 start', f)

clicks = []
if len(sys.argv) > 1 and sys.argv[1].endswith('.json'):
    clicks += [tuple(t) for t in json.load(open(sys.argv[1]))]
    extra = sys.argv[2:]
else:
    extra = sys.argv[1:]
for s in extra:
    if s == 'R':
        clicks.append(('R',0))
    elif s == 'U':
        clicks.append(('U',0))
    else:
        r,c = s.split(':'); clicks.append((int(r),int(c)))

for i,(r,c) in enumerate(clicks):
    if r == 'R':
        f = act(0); tag = f'{i:02d} RESET'
    elif r == 'U':
        f = act(7); tag = f'{i:02d} UNDO'
    else:
        f = act(6, {'x':int(c), 'y':int(r)}); tag = f'{i:02d} click({r},{c})'
    gr = census(tag, f)
    if gr is None:
        f2 = act(1)
        gr = census(f'{i:02d}b after-act1', f2)

gr = grid_of(env.observation_space)
if gr is not None:
    with open('/tmp/fap_ext/su15/stepper_final.txt','w') as fh:
        for r in range(64):
            fh.write(f'{r:3d} ' + ''.join(format(int(v),'x') for v in gr[r]) + '\n')
