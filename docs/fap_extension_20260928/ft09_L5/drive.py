"""ft09 level-5 investigation driver.

Reaches level 5 by auto-playing levels 1-4 with FapExecutor, then hands the
caller the live env plus helpers. Every probe run replays the (cheap,
deterministic) 1-4 prefix so probes are reproducible from the level-5 start
state.
"""
import sys, importlib.util, json
from pathlib import Path
import numpy as np

ROOT = Path('/Users/mustafasafdari/Documents/ChatGPT/FlyGI')
sys.path.insert(0, str(ROOT / 'src'))
spec = importlib.util.spec_from_file_location('b', ROOT / 'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec)
sys.modules['b'] = b
spec.loader.exec_module(b)

from flygi.encoding.features import latest_grid
from flygi.controller.fap_library import FapExecutor, Step

OUT = Path('/tmp/fap_ext/ft09')


def render_grid(array):
    array = np.asarray(array, dtype=np.int16)
    rows = ["".join(format(int(v) % 16, 'x') for v in row) for row in array]
    header = '    ' + ''.join(str(c % 10) for c in range(array.shape[1]))
    body = '\n'.join(f"{r:>3d} {line}" for r, line in enumerate(rows))
    counts = np.bincount(array.ravel(), minlength=16)
    census = ' '.join(f"{format(c, 'x')}:{int(n)}" for c, n in enumerate(counts) if n)
    return f"{header}\n{body}\ncolours {census}"


def diff_grids(a, bgrid):
    a = np.asarray(a); bgrid = np.asarray(bgrid)
    ys, xs = np.nonzero(a != bgrid)
    out = []
    for y, x in zip(ys, xs):
        out.append((int(y), int(x), int(a[y, x]), int(bgrid[y, x])))
    return out


class Session:
    def __init__(self, seed_index=0):
        rt = b.load_arc_runtime()
        g = b.discover_games(rt, ROOT / 'environment_files', ['ft09'])[0]
        arc = b._new_offline_arcade(rt, ROOT / 'environment_files')
        sc = arc.open_scorecard(tags=['diag'], opaque={})
        seed, _ = b.derived_run_seeds(seed_index, g.game_id)
        self.rt = rt
        self.env = arc.make(g.game_id, seed=seed, scorecard_id=sc,
                            save_recording=False, include_frame_data=False)
        self.frame = None
        self.actions_taken = []

    def act(self, i, payload=None):
        a = self.rt.GameAction.from_id(i)
        if payload:
            a.set_data(payload)
        self.frame = self.env.step(a, data=payload or {}, reasoning=None)
        self.actions_taken.append((i, payload))
        return self.frame

    def grid(self):
        return np.asarray(latest_grid(self.frame), dtype=np.int16)

    def status(self):
        f = self.frame
        return dict(state=str(f.state), score=f.levels_completed,
                    avail=[getattr(a, 'value', a) for a in f.available_actions])


def reach_level5(seed_index=0, max_steps=120, verbose=True):
    s = Session(seed_index)
    s.act(0)  # RESET to start
    ex = FapExecutor()
    stall = 0
    while len(s.actions_taken) < max_steps:
        if s.frame.levels_completed >= 4:
            break
        g = s.grid()
        ex.observe(g)
        step = ex.propose(g)
        if step is None:
            stall += 1
            if stall > 6:
                raise RuntimeError('executor abstained before level 5; score=%s' % s.frame.levels_completed)
            # nudge: re-observe same frame (executor stall logic) - just loop
            continue
        stall = 0
        before = s.frame.levels_completed
        if step.action == 6:
            s.act(6, {'x': step.x, 'y': step.y})
        else:
            s.act(step.action)
        if s.frame.levels_completed > before:
            ex.notify_level_advance()
        if str(s.frame.state) == 'GameState.GAME_OVER':
            raise RuntimeError('game over during auto-play')
    if s.frame.levels_completed < 4:
        raise RuntimeError('did not reach level 5 in %d steps' % max_steps)
    if verbose:
        print('reached level 5 in %d actions; status=%s' % (len(s.actions_taken), s.status()))
    return s


if __name__ == '__main__':
    s = reach_level5()
    g = s.grid()
    (OUT / 'level5_start.txt').write_text(render_grid(g))
    np.save(OUT / 'level5_start.npy', g)
    print(s.status())
    print('dumped level5 start grid')
