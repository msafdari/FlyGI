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
    [3]*5 + [2]*2 + [4]*7 + [1]*11 + [5] + [2]*10 + [4]*7 + [1]*4 + [5] + [3]*15 + [2]*7 + [1] + [4]*8,
    [1]*5 + [4] + [4]*3 + [1]*6 + [4]*9 + [2]*10 + [5] + [2]*11 + [3]*6 + [1]*2 + [4]*6 + [1]*3 + [3]*2 + [1]*8 + [3]*10,
]
for P in PROGS:
    for a in P:
        f = act(a)
for a in [1]*14 + [2]*4 + [4]*8 + [2]*3 + [3]*3 + [1] + [4]*7:
    f = act(a)
g = grid_of(f)
print("parked, boxes:", sorted(boxes(g)), "score", f.levels_completed)
f = act(5)
g = grid_of(f)
print("after 5:", sorted(boxes(g)), "score", f.levels_completed,
      "zero", [tuple(map(int,x)) for x in np.argwhere(g==0)])
f = act(5)
g = grid_of(f)
print("after 5,5:", sorted(boxes(g)), "score", f.levels_completed)
