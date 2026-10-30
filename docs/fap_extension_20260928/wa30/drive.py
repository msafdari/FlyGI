import sys, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from flygi.encoding.features import latest_grid

rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['wa30'])[0]
arc = b._new_offline_arcade(rt, ROOT/'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed,_ = b.derived_run_seeds(0, g.game_id)
b._seed_process_for_environment(seed)
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

def diff(g0, g1):
    if g0 is None or g1 is None: return 'EMPTY'
    if g0.shape != g1.shape: return f'SHAPE {g0.shape}->{g1.shape}'
    ch = np.argwhere(g0 != g1)
    if len(ch)==0: return 'NOCHANGE'
    rows = sorted(set(int(r) for r,c in ch)); cols = sorted(set(int(c) for r,c in ch))
    return f'{len(ch)} cells changed rows {rows[0]}-{rows[-1]} cols {cols[0]}-{cols[-1]}'

def show(gr, r0=0, r1=64, c0=0, c1=64):
    hexd = '0123456789abcdef'
    for r in range(r0, r1):
        print(f'{r:3d} ' + ''.join(hexd[int(v)&15] for v in gr[r][c0:c1]))

def state(frame):
    return dict(state=str(frame.state), score=frame.levels_completed, avail=sorted(a.value if hasattr(a,'value') else a for a in frame.available_actions))
