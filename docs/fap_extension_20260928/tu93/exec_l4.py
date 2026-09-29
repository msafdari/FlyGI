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
names={0:'RESET',1:'UP',2:'DOWN',3:'LEFT',4:'RIGHT'}
def rep(f, label):
    try: gr = grid_of(f)
    except Exception:
        print(f"{label}: EMPTY lv={f.levels_completed} {f.state}"); return None
    def find(v):
        ys,xs = np.where(gr==v)
        return (int(ys.min()),int(xs.min())) if len(ys) else None
    print(f"{label}: av={find(9)} e8={find(8)} eC={find(12)} t={int((gr[63]==6).sum())} lv={f.levels_completed} {f.state}")
    return gr
L1=[4,2,2,4,1,4,2,2,3,3,2,4,4,2,4,1,4,2]; L2=[1,4,4,2,4,4,1,4,4,1]
L3 = [p for p in json.load(open('/tmp/fap_ext/tu93/programs_all.json')) if p['level']==3][0]['actions']
for a in L1+L2+L3: f = act(a)
rep(f,"L4start")
L4=[4,4,3,4,4,1,1,4,2,1,3,1,1,3,3,2,3]
for k,a in enumerate(L4):
    f = act(a)
    gr = rep(f, f"t{k+1} {names[a]}")
    if str(f.state)=='GameState.GAME_OVER':
        print("DIED at", k+1); break
    if f.levels_completed >= 4:
        print("LEVEL 4 FELL at step", k+1)
        if gr is not None: np.save('/tmp/fap_ext/tu93/level5_start.npy', gr)
        break
print("final:", f.levels_completed, f.state)
