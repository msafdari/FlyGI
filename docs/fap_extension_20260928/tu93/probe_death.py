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
    a = rt.GameAction.from_id(i)
    return env.step(a, data={}, reasoning=None)
L1 = [4,2,2,4,1,4,2,2,3,3,2,4,4,2,4,1,4,2]
for a in L1: f = act(a)
def report(f, label):
    try:
        gr = grid_of(f)
    except Exception:
        print(f"{label}: EMPTY FRAME lv={f.levels_completed} {f.state}"); return None
    ys,xs = np.where(gr==9); av=(int(ys.min()),int(xs.min())) if len(ys) else None
    ys,xs = np.where(gr==8); en=(int(ys.min()),int(xs.min())) if len(ys) else None
    ys,xs = np.where(gr==15); fpix=list(zip(ys.tolist(),xs.tolist()))
    t = int((gr[63]==6).sum())
    print(f"{label}: avatar={av} enemy8={en} f={fpix} timer={t} lv={f.levels_completed} {f.state}")
    return gr
report(f, "L2 start")
names={1:'UP',2:'DOWN',3:'LEFT',4:'RIGHT'}
for k,a in enumerate([1,4,4,4,4,4,4,1]):
    f = act(a)
    gr = report(f, f"step{k+1} {names[a]}")
    if str(f.state) == 'GameState.GAME_OVER':
        print("DIED at step", k+1)
        if gr is not None: np.save('/tmp/fap_ext/tu93/death_frame.npy', gr)
        break
