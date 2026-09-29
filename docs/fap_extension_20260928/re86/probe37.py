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
# go to 7-plus (active cycles: a-plus -> square -> 7-plus)
f = act(5); f = act(5)
g = grid_of(f)
print("zero", [tuple(map(int,x)) for x in np.argwhere(g==0)])
# 7-plus at (54,24): route left-around to (18,30): 5 lefts, 13 ups, 7 rights, 1 down...
# simpler: measure press right here first: put it at (54,24) pressing UP into object? vertical arm col 24 rows 45-63; object cols 28-35 - no.
# Do the planned b-position: 5 lefts,13 ups -> (15,9); 7 rights -> (15,30); 1 down -> (18,30)
for a in [3]*5 + [1]*13 + [4]*7 + [2]:
    f = act(a)
g0 = grid_of(f)
z0 = [tuple(map(int,x)) for x in np.argwhere(g0==0)]
sev0 = np.argwhere(g0 == 7)
print("before press zero", z0, "7count", len(sev0))
f = act(2)
g1 = grid_of(f)
z1 = [tuple(map(int,x)) for x in np.argwhere(g1==0)]
d = diff(g0, g1)
print("after one down-press: zero", z1, "ndiff", len(d))
for row in d[:40]: print("  ", row)
