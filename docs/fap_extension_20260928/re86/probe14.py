exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

L1 = [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2
L2 = [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7
for a in L1 + L2:
    f = act(a)
print("score", f.levels_completed)
g = grid_of(f)

def boxes(g):
    fours = np.argwhere(g == 4)
    out, seen = [], set()
    for (r, c) in fours:
        r, c = int(r), int(c)
        if (r, c) in seen: continue
        sub = g[r:r+3, c:c+3]
        if sub.shape == (3,3) and (sub == 4).sum() == 8:
            out.append(((r+1, c+1), int(sub[1,1])))
            for dr in range(3):
                for dc in range(3): seen.add((r+dr, c+dc))
    return out
print("boxes", boxes(g))

# cycle avatars: record zero position sequence
centers = []
for k in range(6):
    f = act(5)
    g = grid_of(f)
    z = [tuple(map(int, x)) for x in np.argwhere(g == 0)][0]
    centers.append(z)
    print("cycle", k, "zero", z, "score", f.levels_completed)
