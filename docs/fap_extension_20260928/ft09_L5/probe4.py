"""Probe 4 (level 6): measure the dot-direction flip rule, verify RESET
restores the level start, then execute the derived lights-out program.

HYPOTHESIS under test: a colour-6 sub-cell inside a tile is a FLIP MASK --
clicking the tile toggles itself plus the neighbours its 6-cells point at
(L5 checkered = 6s at all four edge-centres = flips all four orthogonal
neighbours, measured). L6 tiles all carry one 6 at north edge-centre.
Discriminator: click (2,3) which has plain tiles both north (1,3) and
south (3,3).
"""
import sys
sys.path.insert(0, '/tmp/fap_ext/ft09')
from drive import render_grid, diff_grids, OUT
from solve5 import solve_level5
import numpy as np

R6 = [6, 14, 22, 30, 38, 46]
C6 = [4, 12, 20, 28, 36, 44, 52]

def centre(i, j):
    return C6[j] + 3, R6[i] + 3

def tile_of(y, x):
    for i, r in enumerate(R6):
        if r <= y < r + 6:
            for j, c in enumerate(C6):
                if c <= x < c + 6:
                    return (i, j)
    return ('?', y, x)

s = solve_level5()
start6 = s.grid()

def click(i, j, tag=''):
    before = s.grid()
    sb = s.frame.levels_completed
    x, y = centre(i, j)
    s.act(6, {'x': x, 'y': y})
    st = s.status()
    after = s.grid()
    d = diff_grids(after, before)
    tiles = sorted({tile_of(yy, xx) for yy, xx, _, _ in d if yy < 60}, key=str)
    timer = [(yy, xx, o, n) for yy, xx, n, o in d if yy >= 60]
    adv = ' ***ADVANCE***' if st['score'] > sb else ''
    print(f"click {tag}({i},{j}) ndiff={len(d)} tiles={tiles} timer={timer} score={st['score']}{adv}")
    return st['score'] > sb

# 1. discriminator
click(2, 3, 'discriminator ')

# 2. reset, verify identity
s.act(0)
g = s.grid()
same = bool((g == start6).all())
print('after RESET: identical to level-6 start?', same, s.status())
if not same:
    d = diff_grids(g, start6)
    print('  reset diff count', len(d), d[:20])

# 3. derived program assuming NORTH-flip (click flips self + north tile).
# Per-column chain solve, bottom-up: c(bottom)=needed(bottom),
# c(i)=needed(i) XOR c(i+1). Clicks (any order; chains independent):
PROGRAM_NORTH = [
    (0, 0), (1, 0),          # col0
    (2, 1), (3, 1),          # col1
    (1, 2), (2, 2), (4, 2),  # col2
    (3, 3),                  # col3
    (1, 4), (3, 4),          # col4
    (3, 5), (4, 5),          # col5
    (4, 6),                  # col6
]
for (i, j) in PROGRAM_NORTH:
    if click(i, j):
        print('LEVEL ADVANCE at click', (i, j))
        break
print('final', s.status())
(OUT / 'probe4_final.txt').write_text(render_grid(s.grid()))
