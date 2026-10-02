import sys, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
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
L8 = [4,4,1,1,3,4,4,4,3,3,2,2,3,1,1,4,4,4,1,1,1,3,3]
names={1:'U',2:'D',3:'L',4:'R'}
for k,a in enumerate(L8):
    f = act(a)
    st = str(f.state)
    if st=='GameState.GAME_OVER': print("DIED at", k+1); break
    if f.levels_completed > 7:
        print(f"LEVEL 8 FELL at step {k+1}")
        try:
            gr = grid_of(f); np.save('/tmp/fap_ext/tu93/level9_start.npy', gr)
            print("timer:", int((gr[63]==6).sum()))
        except Exception as e: print("no grid:", e)
        break
else:
    print("program exhausted:", f.levels_completed, f.state)
print("state:", f.levels_completed, f.state)
if f.levels_completed == 8:
    P['8'] = L8
    json.dump(P, open('/tmp/fap_ext/tu93/programs_verified.json','w'), indent=1)
