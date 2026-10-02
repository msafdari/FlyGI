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

def token_centre(gr):
    ys, xs = np.where(gr == 15)
    # exclude the header block rows 0-9
    keep = ys > 9
    ys, xs = ys[keep], xs[keep]
    if len(ys) == 0:
        return None
    return (int(round(ys.mean())), int(round(xs.mean())))

def fresh():
    f = act(0)
    return f, grid_of(f)

# Test 1: swallow check — fresh reset then first click on diamond centre
f, gr = fresh()
print('after reset: token at', token_centre(gr), 'score', f.levels_completed)
f = act(6, {'x':10, 'y':53}); gr2 = grid_of(f)
print('first-click diamond ->', token_centre(gr2), '(no swallow if moved)')

# Test 2: from home, which single first clicks work? (fresh reset each)
cands = [
    (57,6,'dash step1'), (55,8,'dash step2'), (53,10,'diamond ctr / step3'),
    (51,12,'dash step4'), (52,10,'diamond N'), (54,10,'diamond S'),
    (53,9,'diamond W'), (53,11,'diamond E'), (52,11,'line non-dash'),
    (58,5,'token cell itself'), (61,2,'below home off-path'),
]
print('--- single first-click scan from home (59,4) ---')
for (r,c,lab) in cands:
    f, gr = fresh()
    f = act(6, {'x':int(c), 'y':int(r)}); g2 = grid_of(f)
    tc = token_centre(g2) if g2 is not None else None
    print(f'click(row={r},col={c}) [{lab}] -> token {tc} score={f.levels_completed} state={f.state}')

# Test 3: after moving to diamond (53,10), find max forward reach
print('--- reach scan from (53,10) ---')
for (r,c,lab) in [(51,12,'1 step'), (49,14,'2 steps'), (47,16,'3 steps'), (45,18,'4 steps'),
                  (43,20,'5 steps'), (52,11,'adjacent non-dash'), (52,10,'1 up non-dash')]:
    f, gr = fresh()
    act(6, {'x':10,'y':53})
    f = act(6, {'x':int(c), 'y':int(r)}); g2 = grid_of(f)
    tc = token_centre(g2) if g2 is not None else None
    print(f'from (53,10) click(row={r},col={c}) [{lab}] -> token {tc} score={f.levels_completed}')
