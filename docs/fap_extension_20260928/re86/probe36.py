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

def ticks(g):
    return int((g[63] != 15).sum())

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

phases = [
    ("a-plus squeeze+park", [4]*11 + [1]*5 + [3]*3 + [1]*5 + [3]*7 + [1] + [2] + [4]*8),
    ("switch", [5]),
    ("square", [1]*6 + [4]*2 + [1]*5 + [4]*4 + [1] + [2] + [3]*10),
    ("switch", [5]),
    ("7plus as 8", [3]*5 + [1]*13 + [4]*9 + [3]*2),
    ("7plus as b", [3] + [4] + [2] + [2]*3 + [4]*8 + [2]*7 + [3]*3),
]
for name, seq in phases:
    for i, a in enumerate(seq):
        f = act(a)
        if str(f.state) not in ("GameState.NOT_FINISHED",):
            print("STATE", f.state, "at", name, i)
            break
        if f.levels_completed >= 7:
            print("LEVEL 7 FELL during", name, "step", i)
            break
    g = grid_of(f)
    z = [tuple(map(int,x)) for x in np.argwhere(g==0)]
    print(name, "done: score", f.levels_completed, "zero", z, "ticks", ticks(g), "boxes", len(boxes(g)), sorted(boxes(g)))
    if f.levels_completed >= 7: break
