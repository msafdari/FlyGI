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
print("at L8:", f.levels_completed, f.state)
def rep(f, label):
    try: gr = grid_of(f)
    except Exception:
        print(f"{label}: EMPTY {f.state}"); return
    ys,xs = np.where(gr==9); av=(int(ys.min()),int(xs.min())) if len(ys) else None
    ys,xs = np.where(gr==13); d=(int(ys.min()),int(xs.min())) if len(ys) else None
    ys,xs = np.where(gr==8); e8=(int(ys.min()),int(xs.min())) if len(ys) else None
    ys,xs = np.where(gr==15); fpix=list(zip(ys.tolist(),xs.tolist()))
    print(f"{label}: av={av} d={d} e8={e8} f={fpix} t={int((gr[63]==6).sum())} lv={f.levels_completed} {f.state}")
rep(f, "L8start")
for k in range(9):
    a = 4 if k%2==0 else 3
    f = act(a); rep(f, f"t{k+1} {'R' if a==4 else 'L'}")
    if str(f.state)=='GameState.GAME_OVER': print("DIED"); break
f = act(0); rep(f, "after RESET")
