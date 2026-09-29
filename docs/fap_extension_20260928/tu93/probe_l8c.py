import sys, importlib.util, json
from pathlib import Path
ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI'); sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from flygi.encoding.features import latest_grid
def grid_of(f): return np.asarray(latest_grid(f), dtype=np.int16)
rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['tu93'])[0]
arc = b._new_offline_arcade(rt, ROOT/'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed,_ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)
def act(i):
    a = rt.GameAction.from_id(i); return env.step(a, data={}, reasoning=None)
P = json.load(open('/tmp/fap_ext/tu93/programs_verified.json'))
for lv in ['1','2','3','4','5','6','7']:
    for a in P[lv]: f = act(a)
def room(p):  # pixel top-left -> room coords with origin (14,14)
    return None if p is None else ((p[0]-14)//6, (p[1]-14)//6)
def rep(f, label):
    try: gr = grid_of(f)
    except Exception:
        print(f"{label}: EMPTY {f.state} lv={f.levels_completed}"); return None
    ys,xs = np.where(gr==9); av=(int(ys.min()),int(xs.min())) if len(ys) else None
    ys,xs = np.where(gr==13); d=(int(ys.min()),int(xs.min())) if len(ys) else None
    ys,xs = np.where(gr==8); s8=(int(ys.min()),int(xs.min())) if len(ys) else None
    print(f"{label}: av={room(av)} d={room(d)} s8={room(s8)} t={int((gr[63]==6).sum())} lv={f.levels_completed} {f.state}")
    return gr
names={0:'RESET',1:'U',2:'D',3:'L',4:'R'}
rep(f, "L8start")
# kill 8, trigger d, kite around loop CCW
seq = [4,4,1,1,3,  4,4,4,  3,3,2,2,3,1,1,4,2,2,3,1,1,4]
for k,a in enumerate(seq):
    f = act(a); rep(f, f"t{k+1} {names[a]}")
    if str(f.state)=='GameState.GAME_OVER': print("DIED at", k+1); break
    if f.levels_completed>7: print("FELL?!"); break
