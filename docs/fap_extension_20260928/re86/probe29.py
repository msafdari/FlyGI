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
print("score", f.levels_completed)
g = grid_of(f)
# cycle avatars
for k in range(3):
    f = act(5)
    g = grid_of(f)
    print("cycle", k, "zero", [tuple(map(int,x)) for x in np.argwhere(g==0)])
# active should be b-square again after 2 cycles if 2 avatars
# drive square toward the 1-object: from (48,15) go up 5 (48->33), right 6 (15->33)
prev = g
for i, a in enumerate([1]*5 + [4]*6):
    f = act(a)
    g = grid_of(f)
    z = [tuple(map(int,x)) for x in np.argwhere(g==0)]
    cnt = Counter(int(v) for v in g.flatten())
    print(i, "act", a, "zero", z, "b:", cnt[11], "1:", cnt[1], "9:", cnt[9], "score", f.levels_completed)
    prev = g
