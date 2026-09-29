import sys, importlib.util, copy
from collections import deque
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

def act(e, i, payload=None):
    a = rt.GameAction.from_id(i)
    if payload: a.set_data(payload)
    return e.step(a, data=payload or {}, reasoning=None)

PREFIX = open('/tmp/fap_ext/ka59/base_seq6.txt').read().strip().split(',')
for tok in PREFIX:
    tok = tok.strip()
    if tok.startswith('c'):
        x, y = tok[1:].split(':'); act(env, 6, {'x': int(x), 'y': int(y)})
    else:
        act(env, int(tok))
fs = env.observation_space
print('prefix done:', fs.state, 'levels', fs.levels_completed, flush=True)
assert fs.levels_completed == 6

def grid(e):
    return np.asarray(latest_grid(e.observation_space), dtype=np.int16)

def key_of(e, depth):
    gr = grid(e).copy()
    gr[63, :] = 0
    gr[gr == 12] = 13
    return (gr.tobytes(), depth % 18)

def click_other(e):
    # click the deselected e-object: find a 5-pixel (centre colour of unselected)
    gr = grid(e)
    cells = np.argwhere(gr == 5)
    if len(cells) == 0:
        return False
    r, c = cells[0]
    act(e, 6, {'x': int(c), 'y': int(r)})
    return True

start_key = key_of(env, 0)
seen = {start_key}
q = deque([(env, [])])
best = None
nodes = 0
DEPTH = 62
BRANCHES = [1, 2, 3, 4, 'click']
while q:
    cur, path = q.popleft()
    if len(path) >= DEPTH:
        continue
    for aid in BRANCHES:
        nxt = copy.deepcopy(cur)
        if aid == 'click':
            if not click_other(nxt):
                continue
        else:
            act(nxt, aid)
        f = nxt.observation_space
        nodes += 1
        if f.levels_completed > 6:
            print('SCORED with path', path + [aid], flush=True)
            print('final state', f.state, flush=True)
            best = path + [aid]; q.clear(); break
        if str(f.state) == 'GameState.GAME_OVER':
            continue
        k = key_of(nxt, len(path) + 1)
        if k in seen:
            continue
        seen.add(k)
        q.append((nxt, path + [aid]))
    if best:
        break
    if nodes % 5000 == 0 and nodes:
        print('nodes', nodes, 'frontier', len(q), 'depth', len(path), 'seen', len(seen), flush=True)
    if nodes > 900000:
        print('node cap hit', flush=True); break
print('done: nodes', nodes, 'unique', len(seen), 'best', best, flush=True)
