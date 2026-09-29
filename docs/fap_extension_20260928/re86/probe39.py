exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

PROGS = [
    [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2,
    [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7,
    [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9,
    [1]*10 + [3]*8 + [3]*5 + [2]*8 + [5] + [2]*12 + [4]*10 + [1]*9 + [3]*5,
    [3]*5 + [2]*2 + [4]*7 + [1]*11 + [5] + [2]*10 + [4]*7 + [1]*4 + [5] + [3]*15 + [2]*7 + [1] + [4]*8,
    [1]*5 + [4] + [4]*3 + [1]*6 + [4]*9 + [2]*10 + [5] + [2]*11 + [3]*6,
]
for P in PROGS:
    for a in P:
        f = act(a)

def pinfo(g, colr=9):
    cells = np.argwhere(g == colr)
    z = [tuple(map(int,x)) for x in np.argwhere(g==0)]
    rows = {}
    for r, c in cells:
        rows.setdefault(int(r), []).append(int(c))
    # horizontal bar = row with many cells; vertical bar = col with many
    from collections import Counter
    colcnt = Counter(int(c) for r, c in cells)
    rowcnt = Counter(int(r) for r, c in cells)
    vb_col, vb_n = colcnt.most_common(1)[0]
    hb_row, hb_n = rowcnt.most_common(1)[0]
    vb_rows = sorted(r for r, c in cells if c == vb_col)
    hb_cols = sorted(c for r, c in cells if r == hb_row)
    return dict(zero=z, vbar_col=vb_col, vbar_rows=(vb_rows[0], vb_rows[-1]), hbar_row=hb_row, hbar_cols=(hb_cols[0], hb_cols[-1]), n=len(cells))

g = grid_of(f)
print("at (48,30):", pinfo(g))
for k in range(2):
    f = act(1)
    g = grid_of(f)
    print(f"press up {k}:", pinfo(g))
for a in [4]*6 + [1]*3:
    f = act(a)
g = grid_of(f)
print("after r6 u3:", pinfo(g))
for k in range(2):
    f = act(3)
    g = grid_of(f)
    print(f"press left {k}:", pinfo(g))
for a in [1]*8 + [3]*10:
    f = act(a)
g = grid_of(f)
print("final park:", pinfo(g), "score", f.levels_completed)
