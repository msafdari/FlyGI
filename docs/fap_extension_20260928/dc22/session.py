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

def summarize(gr, fr=None):
    out = {}
    out['timer'] = int((gr[63] == 3).sum())
    out['dashes_col32'] = int((gr[10:54, 32] == 0).sum())
    # stack column cols 18-21, rows 18-53: runs of non-background
    col = gr[16:54, 18]
    runs = []
    r = 16
    while r < 54:
        v = int(gr[r, 18])
        v2 = int(gr[r, 19])
        r += 1
    # simpler: describe rows 16..53 at cols 18-21 as string per 1 row
    stack = []
    for r in range(16, 54):
        seg = ''.join(format(int(v), 'x') for v in gr[r, 18:22])
        stack.append(seg)
    out['stack_col18_21'] = stack
    bar = []
    for r in range(30, 34):
        bar.append(''.join(format(int(v), 'x') for v in gr[r, 8:22]))
    out['bar_r30_33'] = bar
    chk = []
    for r in range(34, 38):
        chk.append(''.join(format(int(v), 'x') for v in gr[r, 8:14]))
    out['r34_37_c8_13'] = chk
    out['right_zero_cells'] = int((gr[10:54, 34:64] == 0).sum())
    # cursor on board
    e = np.argwhere(gr[38:44, 8:14] == 14)
    out['cursor'] = [[int(r)+38, int(c)+8] for r, c in e[:1]]
    if fr is not None:
        out['state'] = str(fr.state); out['score'] = fr.levels_completed
    return out

def brief(gr, fr=None):
    s = summarize(gr, fr)
    # compress stack: unique non-'4444' rows
    stk = [(i+16, v) for i, v in enumerate(s['stack_col18_21']) if v != '4444']
    return {'timer': s['timer'], 'dashes': s['dashes_col32'], 'stack': stk,
            'bar': s['bar_r30_33'][0], 'chk': s['r34_37_c8_13'][0:2],
            'zeros_right': s['right_zero_cells'], 'cursor': s['cursor'],
            'state': s.get('state'), 'score': s.get('score')}

if __name__ == '__main__':
    fr = env.observation_space
    print('init', json.dumps(brief(grid_of(fr), fr)))
