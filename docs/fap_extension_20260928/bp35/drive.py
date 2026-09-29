"""Interactive prober for bp35. Usage: drive.py '<json list of steps>' [--render-every N]
Steps: {"action":i,"x":..,"y":..} ; action 0 = RESET.
Prints per-step: state, score, changed-cell summary, avatar bbox (colours 9/11), row63 census.
"""
import sys, json, importlib.util
from pathlib import Path
ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI')
sys.path.insert(0, str(ROOT / 'src'))
spec = importlib.util.spec_from_file_location('b', ROOT / 'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b'] = b; spec.loader.exec_module(b)
import numpy as np
from flygi.encoding.features import latest_grid

rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT / 'environment_files', ['bp35'])[0]
arc = b._new_offline_arcade(rt, ROOT / 'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed, _ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)

def act(i, payload=None):
    a = rt.GameAction.from_id(i)
    data = payload or {}
    if payload:
        a.set_data(payload)
    return env.step(a, data=data, reasoning=None)

def grab(frame):
    try:
        return np.asarray(latest_grid(frame), dtype=np.int16)
    except Exception:
        return None

HEX = '0123456789abcdef'
def render(grid, path):
    lines = ['    ' + ''.join(str(c % 10) for c in range(64))]
    for r in range(64):
        lines.append(f'{r:3d} ' + ''.join(HEX[v % 16] for v in grid[r]))
    vals, counts = np.unique(grid, return_counts=True)
    lines.append('colours ' + ' '.join(f'{HEX[v % 16]}:{c}' for v, c in zip(vals, counts)))
    Path(path).write_text('\n'.join(lines) + '\n')

def summarize(prev, cur, tag):
    out = {'tag': tag}
    if cur is None:
        out['grid'] = 'EMPTY'
        return out
    av = np.argwhere((cur == 9) | (cur == 11))
    if len(av):
        out['avatar'] = f'rows {av[:,0].min()}-{av[:,0].max()} cols {av[:,1].min()}-{av[:,1].max()}'
    r63 = cur[63]
    vals, counts = np.unique(r63, return_counts=True)
    out['row63'] = {HEX[v % 16]: int(c) for v, c in zip(vals, counts)}
    if prev is not None:
        d = np.argwhere(prev != cur)
        out['nchanged'] = len(d)
        if len(d):
            out['changed_bbox'] = f'rows {d[:,0].min()}-{d[:,0].max()} cols {d[:,1].min()}-{d[:,1].max()}'
            samp = {}
            for (r, c) in d[: 12]:
                samp[f'{r},{c}'] = f'{HEX[prev[r,c]%16]}->{HEX[cur[r,c]%16]}'
            out['sample'] = samp
    return out

steps = json.loads(sys.argv[1])
render_every = None
if '--render-every' in sys.argv:
    render_every = int(sys.argv[sys.argv.index('--render-every') + 1])
render_last = '--render-last' in sys.argv

frame = env.observation_space
prev = grab(frame)
print(json.dumps({'tag': 'init', 'state': str(frame.state), 'score': frame.levels_completed,
                  'avail': list(frame.available_actions)}))
if prev is not None:
    print(json.dumps(summarize(None, prev, 'init-grid')))
    render(prev, '/tmp/fap_ext/bp35/live_init.txt')

for idx, st in enumerate(steps):
    i = st['action']
    payload = None
    if i == 6:
        payload = {'x': st['x'], 'y': st['y']}
    frame = act(i, payload)
    cur = grab(frame)
    info = summarize(prev, cur, f'{idx:03d}-a{i}' + (f'({st.get("x")},{st.get("y")})' if payload else ''))
    info['state'] = str(frame.state); info['score'] = frame.levels_completed
    info['avail'] = list(frame.available_actions)
    print(json.dumps(info))
    if cur is not None:
        if render_every and (idx % render_every == render_every - 1):
            render(cur, f'/tmp/fap_ext/bp35/live_{idx:03d}.txt')
        prev = cur
if render_last and prev is not None:
    render(prev, '/tmp/fap_ext/bp35/live_last.txt')
