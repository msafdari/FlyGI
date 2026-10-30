#!/usr/bin/env python
"""ls20 probe driver: execute an action sequence, print compact per-step summaries.

Usage: drive.py 4,4,1,2,...   (action ids; 0=RESET, 1=up,2=down,3=left,4=right,5=interact)
Optional second arg: dump directory to write full frame renders per step.
"""
import sys, json, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))
spec = importlib.util.spec_from_file_location('b', ROOT / 'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec)
sys.modules['b'] = b
spec.loader.exec_module(b)
import numpy as np
from flygi.encoding.features import latest_grid

HEX = '0123456789abcdef'


def render(grid):
    lines = []
    lines.append('    ' + ''.join(str(c % 10) for c in range(64)))
    for r in range(64):
        lines.append(f'{r:3d} ' + ''.join(HEX[int(v) & 15] for v in grid[r]))
    return '\n'.join(lines)


def glyph_of(grid, r0, r1, c0, c1, on=9):
    """Extract sub-rectangle, return set of coords with colour `on`."""
    sub = np.asarray(grid[r0:r1, c0:c1])
    return sorted((int(r), int(c)) for r, c in zip(*np.where(sub == on)))


def summarize(grid, prev):
    g = np.asarray(grid)
    s = {}
    # avatar: colours 0 and 1
    ys, xs = np.where((g == 0) | (g == 1))
    if len(ys):
        s['avatar'] = f'r{ys.min()}-{ys.max()} c{xs.min()}-{xs.max()}'
        r0, c0 = int(ys.min()), int(xs.min())
        pat = []
        for rr in range(r0, int(ys.max()) + 1):
            row = ''
            for cc in range(c0, int(xs.max()) + 1):
                v = int(g[rr, cc])
                row += str(v) if v in (0, 1) else '.'
            pat.append(row)
        s['avatar_pat'] = '|'.join(pat)
    else:
        s['avatar'] = None
    # goal box glyph (rows 9-15, cols 33-39 interior)
    s['goal9'] = glyph_of(g, 9, 16, 33, 40, on=9)
    # bottom-left display: rows 53-62, cols 1-10, colour 9 cells
    s['bl9'] = glyph_of(g, 53, 63, 1, 11, on=9)
    # timer bar: colour 11 in rows 60-63
    s['timer'] = int(np.sum(g[60:64, :] == 11))
    # lives: colour 8 cells rows 60-63
    s['lives8'] = int(np.sum(g[60:64, :] == 8))
    # marker tile colours around rows 45-49 cols 34-38
    s['marker'] = ''.join(HEX[int(v) & 15] for v in g[45:50, 36])
    if prev is not None:
        diff = np.argwhere(np.asarray(prev) != g)
        s['ndiff'] = len(diff)
        if len(diff):
            rs, cs = diff[:, 0], diff[:, 1]
            s['diffbox'] = f'r{rs.min()}-{rs.max()} c{cs.min()}-{cs.max()}'
    return s


def main():
    prog = [int(t) for t in sys.argv[1].split(',')] if len(sys.argv) > 1 and sys.argv[1] else []
    dumpdir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if dumpdir:
        dumpdir.mkdir(parents=True, exist_ok=True)

    rt = b.load_arc_runtime()
    g = b.discover_games(rt, ROOT / 'environment_files', ['ls20'])[0]
    arc = b._new_offline_arcade(rt, ROOT / 'environment_files')
    sc = arc.open_scorecard(tags=['diag'], opaque={})
    seed, _ = b.derived_run_seeds(0, g.game_id)
    env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)

    def act(i):
        a = rt.GameAction.from_id(i)
        return env.step(a, data={}, reasoning=None)

    frame = env.observation_space
    grid = np.asarray(latest_grid(frame), dtype=np.int16)
    prev = None
    s = summarize(grid, prev)
    print(f'[init] score={frame.levels_completed} state={frame.state} acts={frame.available_actions}')
    print(f'       {json.dumps(s)}')
    if dumpdir:
        (dumpdir / 'step_000.txt').write_text(render(grid))
    prev = grid
    for i, a in enumerate(prog, 1):
        frame = act(a)
        try:
            grid = np.asarray(latest_grid(frame), dtype=np.int16)
        except Exception as e:
            print(f'[{i:03d}] a={a} EMPTY-GRID ({e}) score={frame.levels_completed} state={frame.state}')
            continue
        s = summarize(grid, prev)
        print(f'[{i:03d}] a={a} score={frame.levels_completed} state={frame.state} acts={frame.available_actions}')
        print(f'       {json.dumps(s)}')
        if dumpdir:
            (dumpdir / f'step_{i:03d}.txt').write_text(render(grid))
        prev = grid


if __name__ == '__main__':
    main()
