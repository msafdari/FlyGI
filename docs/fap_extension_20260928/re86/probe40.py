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

def run(seq):
    global f
    for a in seq:
        f = act(a)
        if f.levels_completed >= 7:
            return True
    return False

phases = [
    ("P1 a-plus 9-pair", [1]*14 + [2]*4 + [4]*8 + [2]*3 + [3]*3 + [1] + [4]*7),
    ("sw", [5]),
    ("P2 square 8-trio", [1]*6 + [4]*2 + [1]*5 + [4]*4 + [1] + [2] + [3]*10),
    ("sw", [5]),
    ("P3 7plus 8 dot", [3]*5 + [1]*13 + [4]*9 + [3]),
    ("P4 7plus b setup", [3]*2 + [2] + [4]*9 + [2]*10 + [3]*3 + [2]*7),
]
fell = False
for name, seq in phases:
    fell = run(seq)
    g = grid_of(f)
    print(name, "score", f.levels_completed, "boxes", len(boxes(g)), sorted(boxes(g))[:12])
    if fell: break

if not fell:
    # adaptive: read vbar top at col 45 (colour 11 cells, rows>=32 to skip dot (30,45))
    g = grid_of(f)
    col45 = sorted(int(r) for r in np.argwhere(g[:,45] == 11).flatten() if r >= 32)
    print("col45 b-cells rows", col45)
    if col45:
        top = col45[0]
        k = (top - 30) // 3
        print("vbar top", top, "ups needed", k)
        fell = run([1]*k)
        g = grid_of(f)
        print("after ups: score", f.levels_completed, "boxes", sorted(boxes(g)))
print("FINAL score", f.levels_completed, "state", f.state)
