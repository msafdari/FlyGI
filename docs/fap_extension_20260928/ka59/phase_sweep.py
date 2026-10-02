import sys, importlib.util, copy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
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
assert env.observation_space.levels_completed == 5
base = copy.deepcopy(env)

def grid(e):
    return np.asarray(latest_grid(e.observation_space), dtype=np.int16)

def block_desc(gr):
    # find c/d cells below row 44 (bottom block)
    cells = np.argwhere(((gr == 12) | (gr == 13)) & (np.arange(64)[:, None] >= 42))
    if len(cells) == 0:
        return 'GONE'
    rows = (cells[:, 0].min(), cells[:, 0].max())
    cols = (cells[:, 1].min(), cells[:, 1].max())
    ccount = int(((gr == 12) & (np.arange(64)[:, None] >= 42)).sum())
    return f'rows{rows} cols{cols} c={ccount}'

for phase in range(19):
    e = copy.deepcopy(base)
    for _ in range(phase):
        act(e, 1); act(e, 2)  # idle pair away from block (P at 49,52 -> up/down)
    # approach: P (49,52) -> (49,49)
    act(e, 3)
    g0 = grid(e)
    pre = block_desc(g0)
    act(e, 3)  # push left
    g1 = grid(e)
    post = block_desc(g1)
    # also push right variant from symmetric side? just left for now
    f = e.observation_space
    print(f'phase {phase:2d} (idle {2*phase}): pre[{pre}] -> post[{post}] state={f.state} lv={f.levels_completed}')
