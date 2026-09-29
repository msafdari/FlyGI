import sys, importlib.util, copy, json
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

PREFIX = open('/tmp/fap_ext/ka59/base_seq5.txt').read().strip().split(',')
for tok in PREFIX:
    tok = tok.strip()
    if tok.startswith('c'):
        x, y = tok[1:].split(':'); act(env, 6, {'x': int(x), 'y': int(y)})
    else:
        act(env, int(tok))
fs = env.observation_space
print('prefix done:', fs.state, 'levels', fs.levels_completed)
assert fs.levels_completed == 5

# test deepcopy
try:
    env2 = copy.deepcopy(env)
    act(env2, 1)
    print('deepcopy works; original untouched:',
          np.array_equal(np.asarray(latest_grid(env.observation_space)),
                         np.asarray(latest_grid(env2.observation_space))) == False)
except Exception as ex:
    print('deepcopy FAILED:', ex); sys.exit(1)

def key_of(e):
    gr = np.asarray(latest_grid(e.observation_space), dtype=np.int16).copy()
    gr[63, :] = 0
    gr[gr == 12] = 13  # normalize c->d (clock phases collapse)
    return gr.tobytes()

start_key = key_of(env)
seen = {start_key}
q = deque([(env, [])])
best = None
nodes = 0
DEPTH = 70
while q:
    cur, path = q.popleft()
    if len(path) >= DEPTH:
        continue
    for aid in (1, 2, 3, 4):
        nxt = copy.deepcopy(cur)
        act(nxt, aid)
        f = nxt.observation_space
        nodes += 1
        if f.levels_completed > 5:
            print('SCORED with path', path + [aid]); best = path + [aid]; q.clear(); break
        if str(f.state) == 'GameState.GAME_OVER':
            continue
        k = key_of(nxt)
        if k in seen:
            continue
        seen.add(k)
        q.append((nxt, path + [aid]))
    if best:
        break
    if nodes % 2000 == 0 and nodes:
        print('nodes', nodes, 'frontier', len(q), 'depth', len(path))
    if nodes > 250000:
        print('node cap hit'); break
print('done: nodes stepped', nodes, 'unique states', len(seen), 'best', best)
