import sys, importlib.util, json
from pathlib import Path
ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI'); sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, '/tmp/fap_ext/tu93')
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from planner2 import plan, parse
from flygi.encoding.features import latest_grid
def grid_of(f): return np.asarray(latest_grid(f), dtype=np.int16)
gr = np.load('/tmp/fap_ext/tu93/level9_start.npy')
m = parse(gr)
print("start", m['start'], "goal", m['goal'])
print("statics", m['statics'])
print("movers", m['movers'])
print("chasers", m['chasers'])
path, m = plan(gr)
print("plan:", path, "len", len(path) if path else None)
if path is None:
    sys.exit("NO PLAN")
rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['tu93'])[0]
arc = b._new_offline_arcade(rt, ROOT/'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed,_ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)
def act(i):
    a = rt.GameAction.from_id(i); return env.step(a, data={}, reasoning=None)
P = json.load(open('/tmp/fap_ext/tu93/programs_verified.json'))
for lv in ['1','2','3','4','5','6','7','8']:
    for a in P[lv]: f = act(a)
print("at L9:", f.levels_completed, f.state)
names={1:'U',2:'D',3:'L',4:'R'}
for k,a in enumerate(path):
    f = act(a)
    st = str(f.state)
    try:
        gg = grid_of(f)
        ys,xs = np.where(gg==9); av=((int(ys.min())-10)//6,(int(xs.min())-9)//6) if len(ys) else None
        ys,xs = np.where(gg==13); d=((int(ys.min())-10)//6,(int(xs.min())-9)//6) if len(ys) else None
        t=int((gg[63]==6).sum())
    except Exception: av=d=t=None
    print(f"t{k+1} {names[a]}: av={av} d={d} t={t} lv={f.levels_completed} {st}")
    if st=='GameState.GAME_OVER': print("DIED at", k+1); break
    if st=='GameState.WIN' or f.levels_completed >= 9:
        print("WIN / LEVEL 9 FELL at step", k+1); break
print("FINAL:", f.levels_completed, f.state)
if f.levels_completed >= 9 or str(f.state)=='GameState.WIN':
    P['9'] = path[:k+1]
    json.dump(P, open('/tmp/fap_ext/tu93/programs_verified.json','w'), indent=1)
