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

def snapshot(gr):
    out = {}
    for col in (10, 6, 15, 11):
        cells = [(int(r),int(c)) for r,c in np.argwhere(gr[10:63] == col)]
        cells = [(r+10,c) for r,c in cells]
        out[col] = cells
    return out

def show(tag, frame):
    gr = grid_of(frame)
    if gr is None:
        print(f'{tag}: EMPTY score={frame.levels_completed} state={frame.state}')
        return None
    s = snapshot(gr)
    tok = None
    for col in (11, 15, 6):
        if s[col]:
            rs = [r for r,_ in s[col]]; cs = [c for _,c in s[col]]
            tok = (col, min(rs), max(rs), min(cs), max(cs), len(s[col]))
            break
    print(f'{tag}: score={frame.levels_completed} state={frame.state} token={tok} a-cells={s[10]} timer={int((np.asarray(grid_of(frame))[63]==0).sum())}')
    return gr

L1 = [(53,10),(47,16),(41,22),(35,28),(29,34),(23,40),(17,46)]
f = env.observation_space
for (r,c) in L1:
    f = act(6, {'x':int(c), 'y':int(r)})
f = act(1)
gr = show('L2 start', f)

# test: is the player fixed? click bg near a far a-cell pair
gr2 = grid_of(act(6, {'x':15,'y':56}))
d = [(int(r),int(c)) for r,c in np.argwhere(gr2 != gr) if r != 63]
print('click (56,15) far bg diff:', d[:12])

clicks = [
    (37,41,'eat food 1'),
    (37,35,'hop W'),
    (37,29,'hop W'),
    (37,23,'hop W'),
    (37,18,'eat food 2 (37,18)'),
    (41,16,'eat food 3 (41,16)'),
    (47,15,'hop S'),
    (53,14,'hop S'),
    (55,14,'eat food 4 (55,14)'),
    (57,16,'eat food 5 (57,16)'),
    (57,22,'hop E'),
    (57,28,'hop E'),
    (57,34,'hop E'),
    (57,40,'hop E'),
    (56,46,'hop E'),
    (56,47,'eat food 6 (56,47)'),
    (54,50,'eat food 7 (54,50)'),
]
f = env.observation_space
for (r,c,lab) in clicks:
    f = act(6, {'x':int(c), 'y':int(r)})
    gr = show(f'click({r},{c}) {lab}', f)
    if gr is None:
        break
# save final frame
gr = grid_of(env.observation_space)
if gr is not None:
    with open('/tmp/fap_ext/su15/level2_after_tour.txt','w') as fh:
        for r in range(64):
            fh.write(f'{r:3d} ' + ''.join(format(int(v),'x') for v in gr[r]) + '\n')
