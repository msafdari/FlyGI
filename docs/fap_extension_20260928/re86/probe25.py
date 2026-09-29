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
for a in [2]*4 + [3]*6:
    f = act(a)
g = grid_of(f)
print("tile9 parked: bcount", int((g==11).sum()), "9count", int((g==9).sum()))
for i, a in enumerate([1]*14 + [4]*7):
    f = act(a)
    g = grid_of(f)
    z = [tuple(map(int,x)) for x in np.argwhere(g==0)]
    print(i, "act", a, "zero", z, "b", int((g==11).sum()), "9", int((g==9).sum()))
