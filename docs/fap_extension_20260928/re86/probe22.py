exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

PROGS = [
    [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2,
    [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7,
    [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9,
    [1]*10 + [3]*8 + [3]*5 + [2]*8 + [5] + [2]*12 + [4]*10 + [1]*9 + [3]*5,
]
for P in PROGS:
    for a in P:
        f = act(a)
# select c-plus: 5,5
f = act(5); f = act(5)
g = grid_of(f)
print("zero", [tuple(map(int,x)) for x in np.argwhere(g==0)])
# verify vertical bar col of plus: count c (12) per column
ccells = np.argwhere(g == 12)
import collections
colcnt = collections.Counter(int(c) for r, c in ccells)
print("c col counts (top5)", colcnt.most_common(5))
f = act(1); f = act(3)
g = grid_of(f)
print("zero now", [tuple(map(int,x)) for x in np.argwhere(g==0)])
for dot in [(33,57),(42,54)]:
    print("hidden dot", dot, "colour", int(g[dot]))
print("score", f.levels_completed)
