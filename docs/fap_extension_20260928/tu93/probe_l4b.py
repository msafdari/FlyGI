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
def fresh():
    sc = arc.open_scorecard(tags=['diag'], opaque={})
    seed,_ = b.derived_run_seeds(0, g.game_id)
    return arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)
names={0:'RESET',1:'UP',2:'DOWN',3:'LEFT',4:'RIGHT'}
def report(env, f, label):
    try: gr = grid_of(f)
    except Exception:
        print(f"{label}: EMPTY lv={f.levels_completed} {f.state}"); return None
    def find(v):
        ys,xs = np.where(gr==v)
        return (int(ys.min()),int(xs.min())) if len(ys) else None
    ys,xs = np.where(gr==15); fpix=list(zip(ys.tolist(),xs.tolist()))
    print(f"{label}: av={find(9)} e8={find(8)} eC={find(12)} f={fpix} t={int((gr[63]==6).sum())} lv={f.levels_completed} {f.state}")
    return gr
L1=[4,2,2,4,1,4,2,2,3,3,2,4,4,2,4,1,4,2]; L2=[1,4,4,2,4,4,1,4,4,1]
L3 = [p for p in json.load(open('/tmp/fap_ext/tu93/programs_all.json')) if p['level']==3][0]['actions']
def run(env, seq, label):
    f = None
    for a in L1+L2+L3:
        aa = rt.GameAction.from_id(a); f = env.step(aa, data={}, reasoning=None)
    gr = report(env, f, f"{label} L4start")
    for k,a in enumerate(seq):
        aa = rt.GameAction.from_id(a); f = env.step(aa, data={}, reasoning=None)
        gr = report(env, f, f"{label} s{k+1} {names[a]}")
        if str(f.state)=='GameState.GAME_OVER':
            print(f"{label}: DIED at step {k+1}")
            if gr is not None: np.save(f'/tmp/fap_ext/tu93/{label}_death.npy', gr)
            return env, f
    return env, f
print("=== E1: R,R,R death capture ===")
e1, f1 = run(fresh(), [4,4,4], "E1")
print("=== E1b: RESET after death — what does it restore? ===")
aa = rt.GameAction.from_id(0); f1 = e1.step(aa, data={}, reasoning=None)
report(e1, f1, "E1 after RESET")
print("=== E2: col-45 bypass, stand at (2,4) then LEFT into (2,3) ===")
e2, f2 = run(fresh(), [4,4,4,4,1,1,1, 3], "E2")
