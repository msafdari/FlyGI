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
def cblocks(gr):
    out=[]
    ys,xs = np.where(gr==12)
    seen=set()
    for y,x in zip(ys.tolist(), xs.tolist()):
        y0,x0 = y-(y%1), x  # find block top-left via clustering on 6-pitch: use min corner search
    # simpler: cluster into 3x3 blocks by top-left scan
    mask = (gr==12)|(gr==15)
    for y in range(62):
        for x in range(62):
            if mask[y,x] and not mask[y-1,x] and not mask[y,x-1]:
                blk = gr[y:y+3, x:x+3]
                loc = np.argwhere(blk==15)
                fac = None
                if len(loc): fac=(int(loc[0][0])-1, int(loc[0][1])-1)
                out.append(((y,x),fac))
    return out
def rep(f, label):
    try: gr = grid_of(f)
    except Exception:
        print(f"{label}: EMPTY lv={f.levels_completed} {f.state}"); return None
    ys,xs = np.where(gr==9); av=(int(ys.min()),int(xs.min())) if len(ys) else None
    print(f"{label}: av={av} c={cblocks(gr)} t={int((gr[63]==6).sum())} lv={f.levels_completed} {f.state}")
    return gr
L1=[4,2,2,4,1,4,2,2,3,3,2,4,4,2,4,1,4,2]; L2=[1,4,4,2,4,4,1,4,4,1]
L3 = [p for p in json.load(open('/tmp/fap_ext/tu93/programs_all.json')) if p['level']==3][0]['actions']
L4=[4,4,3,4,4,1,1,4,2,1,3,1,1,3,3,2,3]
for a in L1+L2+L3+L4: f = act(a)
rep(f,"L5start")
for k in range(16):
    a = 3 if k%2==0 else 4
    f = act(a); rep(f, f"t{k+1} {'L' if a==3 else 'R'}")
    if str(f.state)=='GameState.GAME_OVER': print("DIED"); break
f = act(0); rep(f, "after RESET")
