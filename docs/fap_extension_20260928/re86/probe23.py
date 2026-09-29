exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np
from collections import Counter

PROGS = [
    [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2,
    [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7,
    [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9,
    [1]*10 + [3]*8 + [3]*5 + [2]*8 + [5] + [2]*12 + [4]*10 + [1]*9 + [3]*5,
]
for P in PROGS:
    for a in P:
        f = act(a)
# active: b-X at (42,24). Recolour to 9 via tile (54,6)
for a in [2]*4 + [3]*6:
    f = act(a)
g = grid_of(f)
print("at tile9?", [tuple(map(int,x)) for x in np.argwhere(g==0)],
      "counts b/9:", int((g==11).sum()), int((g==9).sum()), "score", f.levels_completed)
# to (12,27): 14 ups, 7 rights
for a in [1]*14 + [4]*7:
    f = act(a)
g = grid_of(f)
print("parked (12,27)?", [tuple(map(int,x)) for x in np.argwhere(g==0)], "score", f.levels_completed)
print("dot (6,21) cell colour:", int(g[6,21]))
# nudge away and check consumption
f = act(2)
g = grid_of(f)
print("after nudge, dot (6,21):", int(g[6,21]), "score", f.levels_completed, "9count", int((g==9).sum()))
