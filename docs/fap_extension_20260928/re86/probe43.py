exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

PROGS = [
    [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2,
    [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7,
    [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9,
    [1]*10 + [3]*8 + [3]*5 + [2]*8 + [5] + [2]*12 + [4]*10 + [1]*9 + [3]*5,
    [3]*5 + [2]*2 + [4]*7 + [1]*11 + [5] + [2]*10 + [4]*7 + [1]*4 + [5] + [3]*15 + [2]*7 + [1] + [4]*8,
    [1]*5 + [4] + [4]*3 + [1]*6 + [4]*9 + [2]*10 + [5] + [2]*11 + [3]*6 + [1]*2 + [4]*6 + [1]*3 + [3]*2 + [1]*8 + [3]*10,
]
for P in PROGS:
    for a in P:
        f = act(a)
# a-plus active at (48,12), square parked rows 45-57 cols 15-27.
g0 = grid_of(f)
def parts(g, colr):
    cells = np.argwhere(g == colr)
    from collections import Counter
    colcnt = Counter(int(c) for r, c in cells)
    rowcnt = Counter(int(r) for r, c in cells)
    return colcnt.most_common(2), rowcnt.most_common(2)
print("a-plus (10):", parts(g0, 10))
f = act(4)   # right: vbar col 12 -> 15 would overlap square wall
g1 = grid_of(f)
print("after right:", parts(g1, 10), "zero", [tuple(map(int,x)) for x in np.argwhere(g1==0)])
f = act(4)
g2 = grid_of(f)
print("after right2:", parts(g2, 10), "zero", [tuple(map(int,x)) for x in np.argwhere(g2==0)])
