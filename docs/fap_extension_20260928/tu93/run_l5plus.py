import sys, importlib.util, json
from pathlib import Path
ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI'); sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, '/tmp/fap_ext/tu93')
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from planner import plan
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
L1=[4,2,2,4,1,4,2,2,3,3,2,4,4,2,4,1,4,2]; L2=[1,4,4,2,4,4,1,4,4,1]
L3 = [p for p in json.load(open('/tmp/fap_ext/tu93/programs_all.json')) if p['level']==3][0]['actions']
L4=[4,4,3,4,4,1,1,4,2,1,3,1,1,3,3,2,3]
for a in L1+L2+L3+L4: f = act(a)
print("at L5:", f.levels_completed, f.state)
progs = {1:L1, 2:L2, 3:L3, 4:L4}
while f.levels_completed < 9 and str(f.state) != 'GameState.WIN':
    lv = f.levels_completed
    try: gr = grid_of(f)
    except Exception:
        f = act(1); continue
    np.save(f'/tmp/fap_ext/tu93/level{lv+1}_start.npy', gr)
    path, m = plan(gr)
    print(f"L{lv+1}: start={m['start']} goal={m['goal']} statics={m['statics']} movers={m['movers']} plan={path}")
    if path is None:
        print("NO PLAN — stop"); break
    steps = []; fell = False
    for a in path:
        f = act(a); steps.append(a)
        if str(f.state)=='GameState.GAME_OVER': break
        if f.levels_completed > lv or str(f.state)=='GameState.WIN': fell=True; break
    t = None
    try: t = int((grid_of(f)[63]==6).sum())
    except Exception: pass
    print(f"  -> fell={fell} lv={f.levels_completed} {f.state} timer_left={t} used {len(steps)} moves")
    if not fell:
        print("  program failed — stop for diagnosis"); break
    progs[lv+1] = steps
json.dump({str(k):v for k,v in progs.items()}, open('/tmp/fap_ext/tu93/programs_verified.json','w'), indent=1)
print("FINAL:", f.levels_completed, f.state)
