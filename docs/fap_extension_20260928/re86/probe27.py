exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

def boxes(g):
    fours = np.argwhere(g == 4)
    out, seen = [], set()
    for (r, c) in fours:
        r, c = int(r), int(c)
        if (r, c) in seen: continue
        sub = g[r:r+3, c:c+3]
        if sub.shape == (3,3) and (sub == 4).sum() >= 6 and sub[1,1] != 4:
            out.append(((r+1, c+1), int(sub[1,1])))
            for dr in range(3):
                for dc in range(3): seen.add((r+dr, c+dc))
    return out

PROGS = [
    [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2,
    [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7,
    [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9,
    [1]*10 + [3]*8 + [3]*5 + [2]*8 + [5] + [2]*12 + [4]*10 + [1]*9 + [3]*5,
]
for P in PROGS:
    for a in P:
        f = act(a)
g = grid_of(f)
print("L5 boxes:", sorted(boxes(g)))
seq = [5,5] + [3]*15 + [2]*7 + [1] + [4]*8 + [1]
for a in seq:
    f = act(a)
g = grid_of(f)
print("after park+nudge boxes:", sorted(boxes(g)))
print("score", f.levels_completed)
# nudge far away: 3 more ups so vertical arm leaves (60,x) too? center (48,33)->(39,33): arm rows 25-53
for a in [1]*3:
    f = act(a)
g = grid_of(f)
print("after 3 more ups boxes:", sorted(boxes(g)), "score", f.levels_completed)
