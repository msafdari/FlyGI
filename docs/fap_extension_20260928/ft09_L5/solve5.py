"""Reusable: replay the verified 21-click level-5 program, return session at L6."""
import sys
sys.path.insert(0, '/tmp/fap_ext/ft09')
from drive import reach_level5, render_grid, OUT
import numpy as np

R = [4, 12, 20, 28, 36, 44, 52]
C = [6, 14, 22, 30, 38, 46, 54]

L5_PROGRAM = [
    (1, 2), (3, 2), (5, 4),
    (0, 2), (1, 1), (1, 3), (3, 1), (3, 3), (4, 4), (5, 3), (5, 5), (6, 4),
    (0, 3), (2, 1), (2, 3), (2, 5), (4, 1), (4, 3), (4, 5), (6, 1), (6, 3),
]


def solve_level5(s=None, verbose=False):
    if s is None:
        s = reach_level5(verbose=False)
    for (i, j) in L5_PROGRAM:
        assert s.frame.levels_completed == 4
        s.act(6, {'x': C[j] + 3, 'y': R[i] + 3})
    assert s.frame.levels_completed == 5, s.status()
    if verbose:
        print('level 5 solved; now', s.status(), 'actions', len(s.actions_taken))
    return s


if __name__ == '__main__':
    s = solve_level5(verbose=True)
    g = s.grid()
    (OUT / 'level6_start.txt').write_text(render_grid(g))
    np.save(OUT / 'level6_start.npy', g)
    print('dumped level 6 start')
