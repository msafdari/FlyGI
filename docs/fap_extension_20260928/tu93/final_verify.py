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

print("=== A: timer-death measurement on level 1 (blocked DOWN spam) ===")
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed,_ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)
def act(i):
    a = rt.GameAction.from_id(i); return env.step(a, data={}, reasoning=None)
n = 0
for k in range(80):
    f = act(2)  # blocked at L1 start
    n += 1
    if str(f.state) == 'GameState.GAME_OVER':
        print(f"GAME_OVER after {n} blocked actions (timer death)"); break
else:
    print("no timer death in 80 actions?!")
f = act(0)
gr0 = grid_of(f)
init = np.load('/tmp/fap_ext/tu93/level1_start.npy')
print("RESET-after-timer-death == initial frame:", bool((gr0==init).all()))

print("=== B: clean end-to-end replay of all 9 programs ===")
sc = arc.open_scorecard(tags=['diag'], opaque={})
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)
P = json.load(open('/tmp/fap_ext/tu93/programs_verified.json'))
transitions = []
total = 0
for lv in map(str, range(1,10)):
    before = env.observation_space.levels_completed
    tstart = int((grid_of(env.observation_space)[63]==6).sum())
    for a in P[lv]:
        f = act(a); total += 1
    tleft = None
    try: tleft = int((grid_of(f)[63]==6).sum())
    except Exception: pass
    transitions.append(dict(level=int(lv), steps=len(P[lv]), before=int(before),
                            after=int(f.levels_completed), state=str(f.state)))
    print(f"L{lv}: {len(P[lv])} steps, levels {before}->{f.levels_completed}, state={f.state}")
    assert f.levels_completed == int(lv), f"level {lv} did not fall!"
print("TOTAL steps:", total, "final state:", f.state)
json.dump(dict(programs={k:P[k] for k in map(str,range(1,10))}, transitions=transitions,
               total_steps=total, final_state=str(f.state)),
          open('/tmp/fap_ext/tu93/final_verified.json','w'), indent=1)
print("saved /tmp/fap_ext/tu93/final_verified.json")
