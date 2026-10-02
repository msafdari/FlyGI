"""L4 card characterization for dc22 (second investigator, 2026-09-28).
Replays the verified 123-step program to reach level 4, then clicks each
candidate card region twice (toggle out / toggle back), diffing the grid.
"""
import sys, importlib.util, json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
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

def diff_groups(g0, g1, label):
    d = np.argwhere(g0[:63] != g1[:63])
    print(f'{label}: {len(d)} cells')
    items = {}
    for (r, c) in d:
        key = (int(g0[r, c]), int(g1[r, c]))
        items.setdefault(key, []).append((int(r), int(c)))
    for (a, bb), cells in sorted(items.items()):
        rows = sorted(set(r for r, _ in cells)); cols = sorted(set(c for _, c in cells))
        print(f'  {a:x}->{bb:x}: rows {rows[0]}-{rows[-1]} cols {cols[0]}-{cols[-1]} ({len(cells)})')

prog = json.loads(Path('/tmp/fap_ext/dc22/prog_l123.json').read_text())
fr = None
for st in prog:
    fr = act(st['action'], {'x': st['x'], 'y': st['y']} if st['action'] == 6 else None)
assert fr.levels_completed == 3, fr.levels_completed
print('at level 4, score', fr.levels_completed)
g0 = grid_of(fr)

for name, (x, y) in {'card6 (52,19)': (52, 19), 'cardB (46,28)': (46, 28),
                     'card2 (56,28)': (56, 28), 'card1? (52,45)': (52, 45)}.items():
    fr = act(6, {'x': x, 'y': y})
    g1 = grid_of(fr)
    diff_groups(g0, g1, f'click {name}')
    print('   state', fr.state, 'score', fr.levels_completed)
    fr = act(6, {'x': x, 'y': y})
    g2 = grid_of(fr)
    nd = int((g1[:63] != g2[:63]).sum())
    print(f'   re-click nd={nd}')
    g0 = g2
