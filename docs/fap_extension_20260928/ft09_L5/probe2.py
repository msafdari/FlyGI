"""Probe 2: execute the derived two-sided {e,f} prescription program.

Derived target (palette e/f from the top-right indicator pair; glyph centre
= marked colour; 0-cells -> marked, 2-cells -> other, 3-cells -> positions
that are absent or occupied by glyphs -- all verified consistent across the
8 glyphs):
  e: (0,2)(1,1)(1,3)(2,0)(2,4)(2,6)(3,1)(3,3)(3,5)(4,0)(4,4)(5,1)(5,3)(5,5)(6,2)(6,4)
  f: (0,3)(2,1)(2,3)(2,5)(4,1)(4,3)(4,5)(6,1)(6,3) plus checkered (1,2)(3,2)(5,4) in f-phase
Mechanics measured in probe1: plain click toggles self; checkered click
toggles own phase + 4 orthogonal plain neighbours.
Program: click 3 checkered tiles once each, then repair/set plain tiles.
"""
import sys
sys.path.insert(0, '/tmp/fap_ext/ft09')
from drive import reach_level5, render_grid, diff_grids, OUT
import numpy as np

R = [4, 12, 20, 28, 36, 44, 52]
C = [6, 14, 22, 30, 38, 46, 54]

def centre(i, j):
    return C[j] + 3, R[i] + 3  # x, y

def tile_of(y, x):
    for i, r in enumerate(R):
        if r <= y < r + 6:
            for j, c in enumerate(C):
                if c <= x < c + 6:
                    return (i, j)
    return None

program = [
    ('checkered', (1, 2)), ('checkered', (3, 2)), ('checkered', (5, 4)),
    # repair to e
    ('to_e', (0, 2)), ('to_e', (1, 1)), ('to_e', (1, 3)), ('to_e', (3, 1)),
    ('to_e', (3, 3)), ('to_e', (4, 4)), ('to_e', (5, 3)), ('to_e', (5, 5)),
    ('to_e', (6, 4)),
    # set to f
    ('to_f', (0, 3)), ('to_f', (2, 1)), ('to_f', (2, 3)), ('to_f', (2, 5)),
    ('to_f', (4, 1)), ('to_f', (4, 3)), ('to_f', (4, 5)), ('to_f', (6, 1)),
    ('to_f', (6, 3)),
]

s = reach_level5(verbose=False)
steps_log = []
for k, (tag, (i, j)) in enumerate(program):
    x, y = centre(i, j)
    before = s.grid()
    score_before = s.frame.levels_completed
    s.act(6, {'x': x, 'y': y})
    st = s.status()
    if st['state'] == 'GameState.WIN' or st['score'] > score_before:
        print(f"step {k} {tag} {(i,j)} -> SCORE {score_before}->{st['score']} state={st['state']}")
        steps_log.append((k, tag, (i, j), 'ADVANCE'))
        break
    after = s.grid()
    d = diff_grids(after, before)
    tiles = sorted({tile_of(yy, xx) for yy, xx, _, _ in d if yy < 60}, key=str)
    timer = [(yy, xx, o, n) for yy, xx, n, o in d if yy >= 60]
    print(f"step {k:2d} {tag:9s} {(i,j)} ndiff={len(d)} tiles={tiles} timer={timer} score={st['score']}")
    steps_log.append((k, tag, (i, j), len(d)))

print('final', s.status())
g = s.grid()
(OUT / 'probe2_final.txt').write_text(render_grid(g))
