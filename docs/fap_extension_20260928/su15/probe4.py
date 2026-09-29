import sys, importlib.util
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

L1 = [(53,10),(47,16),(41,22),(35,28),(29,34),(23,40),(17,46)]
f = env.observation_space
for (r,c) in L1:
    f = act(6, {'x':int(c), 'y':int(r)})
print('after L1 program: score', f.levels_completed, f.state, 'grid?', grid_of(f) is not None)

# try to surface the level-2 frame
for attempt in range(4):
    g2 = grid_of(f)
    if g2 is not None:
        break
    f = act(1)
    print('act(1):', f.levels_completed, f.state, 'grid?', grid_of(f) is not None)

g2 = grid_of(f)
if g2 is not None:
    with open('/tmp/fap_ext/su15/level2_initial.txt','w') as fh:
        fh.write('    ' + '0123456789'*7 + '\n')
        for r in range(64):
            fh.write(f'{r:3d} ' + ''.join(format(int(v),'x') for v in g2[r]) + '\n')
        import collections
        cen = collections.Counter(int(v) for v in g2.ravel())
        fh.write('colours ' + ' '.join(f'{k}:{v}' for k,v in sorted(cen.items())) + '\n')
    print('saved level2_initial.txt')
    dashes = sorted((int(r), int(c)) for r, c in zip(*np.where(g2 == 3)))
    print('colour-3 cells:', dashes)
    ys, xs = np.where(g2 == 15)
    print('f cells:', sorted(zip(ys.tolist(), xs.tolist())))
    zeros = sorted((int(r), int(c)) for r, c in zip(*np.where(g2[:63] == 0)))
    print('colour-0 above 63:', zeros)
    nines = np.argwhere(g2 == 9)
    if len(nines): print('ring bbox rows', nines[:,0].min(), nines[:,0].max(), 'cols', nines[:,1].min(), nines[:,1].max())
    print('row63:', ''.join(format(int(v),'x') for v in g2[63]))
