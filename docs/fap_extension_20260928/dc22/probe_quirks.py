"""Quirk probes for dc22, run 2026-09-28 (second investigator).

Measures, in one offline session (seed derived_run_seeds(0, game_id)):
1. swallow quirk: is the first action after episode start / after RESET effect-free?
2. timer mode: does row 63 fill by action count or by wall clock?
3. timeout: idle at level 4 until the bar fills; what state results, and does
   RESET restore the level-4 start exactly?
"""
import sys, importlib.util, json, time
from pathlib import Path
import numpy as np

ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI'); sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b'] = b; spec.loader.exec_module(b)
from flygi.encoding.features import latest_grid

rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['dc22'])[0]
arc = b._new_offline_arcade(rt, ROOT/'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed, _ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)

def act(i, payload=None):
    a = rt.GameAction.from_id(i)
    if payload:
        a.set_data(payload)
    return env.step(a, data=payload or {}, reasoning=None)

def grid_of(fr):
    try:
        return np.asarray(latest_grid(fr), dtype=np.int16)
    except Exception:
        return None

def timer(gr):
    return int((gr[63] == 3).sum())

def render(gr, path):
    lines = ['    ' + ''.join(str(c % 10) for c in range(64))]
    for r in range(64):
        lines.append(f'{r:3d} ' + ''.join(format(int(v), 'x') for v in gr[r]))
    Path(path).write_text('\n'.join(lines) + '\n')

fr0 = env.observation_space
g0 = grid_of(fr0)
print('init state', fr0.state, 'score', fr0.levels_completed, 'timer', timer(g0))

# --- 1. swallow quirk -------------------------------------------------------
fr1 = act(1)
g1 = grid_of(fr1)
nd_first = int((g0[:63] != g1[:63]).sum())
fr = act(0)
gr = grid_of(fr)
reset_identical = bool(np.array_equal(gr[:63], g0[:63]))
fr2 = act(1)
g2 = grid_of(fr2)
nd_post_reset = int((gr[:63] != g2[:63]).sum())
print(f'SWALLOW: first-episode-action a1 changed {nd_first} non-timer cells; '
      f'reset restores playfield identically: {reset_identical}; '
      f'first-post-RESET a1 changed {nd_post_reset} cells')

# --- 2. timer mode ----------------------------------------------------------
fr = act(0)
gr = grid_of(fr)
t0 = timer(gr)
t_wall = time.time()
time.sleep(12)
fr = act(1)
gr = grid_of(fr)
t1 = timer(gr)
print(f'TIMER: after RESET timer={t0}; after 12.0s sleep + one action timer={t1}')
fr = act(2)
for i in range(9):
    fr = act(1 if i % 2 else 2)
gr = grid_of(fr)
t2 = timer(gr)
print(f'TIMER: after 10 rapid alternating actions timer={t2} (wall {time.time()-t_wall:.1f}s)')

# --- 3. run to level 4, then idle to timeout --------------------------------
fr = act(0)
prog = json.loads(Path('/tmp/fap_ext/dc22/prog_l123.json').read_text())
score = fr.levels_completed
for i, st in enumerate(prog, 1):
    fr = act(st['action'], {'x': st['x'], 'y': st['y']} if st['action'] == 6 else None)
    if fr.levels_completed != score:
        print(f'  main-run transition at step {i}: {score} -> {fr.levels_completed}')
        score = fr.levels_completed
print('reached score', fr.levels_completed, fr.state)
gL4 = grid_of(fr)
render(gL4, '/tmp/fap_ext/dc22/l4_initial.txt')

n = 0
t_start = time.time()
while str(fr.state) == 'GameState.NOT_FINISHED' and n < 400 and time.time() - t_start < 150:
    fr = act(1 if n % 2 else 2)
    n += 1
gr = grid_of(fr)
print(f'IDLE: after {n} idle actions ({time.time()-t_start:.1f}s) state={fr.state} '
      f'score={fr.levels_completed} timer={timer(gr) if gr is not None else None}')
if str(fr.state) != 'GameState.NOT_FINISHED':
    if gr is not None:
        render(gr, '/tmp/fap_ext/dc22/l4_timeout.txt')
    fr = act(0)
    gr2 = grid_of(fr)
    same = bool(np.array_equal(gr2[:63], gL4[:63]))
    print(f'RESTORE: after GAME_OVER, RESET -> state={fr.state} score={fr.levels_completed} '
          f'playfield identical to L4 start: {same} timer={timer(gr2)}')
