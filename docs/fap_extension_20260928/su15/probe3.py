import sys, importlib.util, json
from pathlib import Path
ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI'); sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from flygi.encoding.features import latest_grid
rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['su15'])[0]
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

def token_centre(gr):
    ys, xs = np.where(gr == 15)
    keep = ys > 9
    ys, xs = ys[keep], xs[keep]
    if len(ys) == 0: return None
    return (int(round(ys.mean())), int(round(xs.mean())))

frame = env.observation_space
gr = grid_of(frame)
# exact geometry of the initial frame
dashes = sorted((int(r), int(c)) for r, c in zip(*np.where(gr == 3)))
print('colour-3 cells (row,col):', dashes)
ring = np.argwhere(gr == 9)
print('ring bbox rows', ring[:,0].min(), ring[:,0].max(), 'cols', ring[:,1].min(), ring[:,1].max())
zeros = sorted((int(r), int(c)) for r, c in zip(*np.where(gr[:63] == 0)))
print('colour-0 cells above row 63:', zeros)

# metric disambiguation: from (53,10) after first hop, click (45,14): dr=8 -> should fail if Chebyshev
act(6, {'x':10,'y':53})
f = act(6, {'x':14,'y':45}); g2 = grid_of(f)
print('metric test click(45,14) dr8 dc4 ->', token_centre(g2))
f = act(6, {'x':16,'y':46}); g2 = grid_of(f)  # (46,16): dr7 dc6 from (53,10) -> fail if Chebyshev<=6
print('metric test click(46,16) dr7 dc6 ->', token_centre(g2))
f = act(6, {'x':16,'y':47}); g2 = grid_of(f)  # (47,16): Chebyshev 6
print('metric test click(47,16) dr6 dc6 ->', token_centre(g2))

# now continue the run up to the socket
hops = [(41,22),(35,28),(29,34),(23,40),(17,46),(15,48)]
for (r,c) in hops:
    f = act(6, {'x':int(c), 'y':int(r)}); g2 = grid_of(f)
    tc = token_centre(g2) if g2 is not None else None
    print(f'hop click({r},{c}) -> token {tc} score={f.levels_completed} state={f.state}')
    if g2 is None:
        print('   empty frame; state', f.state)

# dump final frame
g2 = grid_of(env.observation_space)
if g2 is not None:
    np.save('/tmp/fap_ext/su15/after_hops.npy', g2)
    with open('/tmp/fap_ext/su15/after_hops.txt','w') as fh:
        for r in range(64):
            fh.write(''.join(format(int(v),'x') for v in g2[r]) + '\n')
print('final score', env.observation_space.levels_completed, env.observation_space.state)
