exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np
from collections import Counter

PROGS = [
    [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2,
    [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7,
    [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9,
    [1]*10 + [3]*8 + [3]*5 + [2]*8 + [5] + [2]*12 + [4]*10 + [1]*9 + [3]*5,
    [3]*5 + [2]*2 + [4]*7 + [1]*11 + [5] + [2]*10 + [4]*7 + [1]*4 + [5] + [3]*15 + [2]*7 + [1] + [4]*8,
]
for P in PROGS:
    for a in P:
        f = act(a)
# active after L5 completion: cycle0 gave plus, so current active = square? verify:
g = grid_of(f)
print("zero now", [tuple(map(int,x)) for x in np.argwhere(g==0)])
def binfo(g):
    b = np.argwhere(g == 11)
    if len(b) == 0: return None
    return (int(b[:,0].min()), int(b[:,0].max()), int(b[:,1].min()), int(b[:,1].max()), len(b))
def oinfo(g):
    o = np.argwhere(g == 1)
    o = o[o[:,0] != 63]  # drop timer row
    if len(o) == 0: return None
    return (int(o[:,0].min()), int(o[:,0].max()), int(o[:,1].min()), int(o[:,1].max()), len(o))
print("b box", binfo(g), "obj box", oinfo(g))
for i, a in enumerate([1]*5 + [4]*6):
    f = act(a)
    g = grid_of(f)
    z = [tuple(map(int,x)) for x in np.argwhere(g==0)]
    print(i, "act", a, "zero", z, "b", binfo(g), "obj", oinfo(g), "score", f.levels_completed)
