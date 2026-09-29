"""Probe 1: click semantics on level 5.

Clicks: background, plain e tile, checkered e/6 tile, a glyph tile, an
f-centred glyph tile. Diff after each; watch timer row 63 and indicator.
"""
import sys
sys.path.insert(0, '/tmp/fap_ext/ft09')
from drive import reach_level5, render_grid, diff_grids, OUT
import numpy as np

s = reach_level5(verbose=False)
g0 = s.grid()
log = []

def probe(name, x, y):
    before = s.grid()
    s.act(6, {'x': x, 'y': y})
    after = s.grid()
    d = diff_grids(after, before)
    st = s.status()
    # summarize diff by region
    print(f"== {name}: click(x={x},y={y}) state={st['state']} score={st['score']} ndiff={len(d)}")
    if len(d) <= 60:
        for (yy, xx, new, old) in d:
            print(f"   ({yy},{xx}) {old:x}->{new:x}")
    else:
        # group by rows
        rows = sorted({yy for yy, _, _, _ in d})
        print(f"   rows touched: {rows}")
        from collections import Counter
        c = Counter((old, new) for _, _, new, old in d)
        print(f"   transitions: {dict(((f'{o:x}->{n:x}', v) for (o, n), v in c.items()))}")
    return d

probe('background', 2, 60)          # empty background area
probe('background2', 2, 60)         # repeat: does refusal freeze world?
probe('plain e tile (2,0)', 9, 23)  # lattice row2 col0, far from glyphs? (adjacent to C at (3,0))
probe('checkered tile (1,2)', 25, 15)
probe('plain e tile (2,6)', 57, 23) # top-right area tile
probe('glyph D itself', 41, 31)
probe('f-glyph C itself', 9, 31)
probe('indicator e block', 55, 1)
probe('indicator f block', 55, 5)

gN = s.grid()
(OUT / 'probe1_final.txt').write_text(render_grid(gN))
print('final status', s.status())
