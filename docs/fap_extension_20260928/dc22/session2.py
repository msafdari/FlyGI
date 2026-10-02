import sys, importlib.util, json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
from flygi.encoding.features import latest_grid

rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['dc22'])[0]
arc = b._new_offline_arcade(rt, ROOT/'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed,_ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)

def act(i, payload=None):
    a = rt.GameAction.from_id(i)
    if payload: a.set_data(payload)
    return env.step(a, data=payload or {}, reasoning=None)

def grid_of(frame):
    try:
        return np.asarray(latest_grid(frame), dtype=np.int16)
    except Exception:
        return None

def render(gr, path):
    lines = ['    ' + ''.join(str(c % 10) for c in range(64))]
    for r in range(64):
        lines.append(f'{r:3d} ' + ''.join(format(int(v), 'x') for v in gr[r]))
    Path(path).write_text('\n'.join(lines) + '\n')

L1 = json.loads(Path('/tmp/fap_ext/dc22/prog_l1.json').read_text())

def play(seq):
    fr = None
    for st in seq:
        if st['action'] == 6:
            fr = act(6, {'x': st['x'], 'y': st['y']})
        else:
            fr = act(st['action'])
    return fr

def to_l2():
    fr = act(0)
    return play(L1)

def show_diff(g0, g1, label, skip_timer=True):
    top = 63 if skip_timer else 64
    d = np.argwhere(g0[:top] != g1[:top])
    print(f'{label}: {len(d)} cells changed (excl timer)')
    if len(d) and len(d) <= 100:
        # group into bboxes by connected colour runs: just print unique (r ranges, c ranges, from, to)
        items = {}
        for (r, c) in d:
            key = (int(g0[r, c]), int(g1[r, c]))
            items.setdefault(key, []).append((int(r), int(c)))
        for (a, bb), cells in items.items():
            rows = sorted(set(r for r, _ in cells)); cols = sorted(set(c for _, c in cells))
            print(f'  {a:x}->{bb:x}: rows {rows[0]}-{rows[-1]} cols {cols[0]}-{cols[-1]} ({len(cells)} cells)')

def player_pos(gr):
    e = np.argwhere(gr == 14)
    return [(int(r), int(c)) for r, c in e]

if __name__ == '__main__':
    fr = to_l2()
    print('level2 reached, score', fr.levels_completed)
    g0 = grid_of(fr)
    # probe the three cards
    for name, (x, y) in {'card6-top': (52, 22), 'card-invis-mid': (52, 31), 'card9-bot': (52, 40)}.items():
        fr = act(6, {'x': x, 'y': y})
        g1 = grid_of(fr)
        show_diff(g0, g1, f'click {name} ({x},{y})')
        print('   state', fr.state, 'score', fr.levels_completed, 'player', player_pos(g1))
        # undo by clicking again if it toggled
        fr = act(6, {'x': x, 'y': y})
        g2 = grid_of(fr)
        show_diff(g1, g2, f'  re-click {name}')
        g0 = g2
