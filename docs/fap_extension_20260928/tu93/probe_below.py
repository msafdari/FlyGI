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
    a = rt.GameAction.from_id(i)
    return env.step(a, data={}, reasoning=None)
names={0:'RESET',1:'UP',2:'DOWN',3:'LEFT',4:'RIGHT'}
def report(f, label):
    try: gr = grid_of(f)
    except Exception:
        print(f"{label}: EMPTY lv={f.levels_completed} {f.state}"); return None
    ys,xs = np.where(gr==9); av=(int(ys.min()),int(xs.min())) if len(ys) else None
    ys,xs = np.where(gr==8); en=(int(ys.min()),int(xs.min())) if len(ys) else None
    ys,xs = np.where(gr==15); fpix=list(zip(ys.tolist(),xs.tolist()))
    print(f"{label}: av={av} en={en} f={fpix} t={int((gr[63]==6).sum())} lv={f.levels_completed} {f.state}")
    return gr
for a in [4,2,2,4,1,4,2,2,3,3,2,4,4,2,4,1,4,2]: f = act(a)
report(f, "L2 start")
seq = [1,4,4,2,4,4, 2,2, 1]  # to (33,36) below enemy; wait x2 (DOWN blocked); push UP into it
for k,a in enumerate(seq):
    f = act(a)
    gr = report(f, f"s{k+1} {names[a]}")
    if str(f.state) == 'GameState.GAME_OVER':
        print("DIED at", k+1); break
