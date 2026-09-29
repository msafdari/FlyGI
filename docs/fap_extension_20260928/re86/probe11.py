exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np
from collections import Counter

def boxes(g):
    fours = np.argwhere(g == 4)
    out = []
    seen = set()
    for (r, c) in fours:
        r, c = int(r), int(c)
        if (r, c) in seen: continue
        sub = g[r:r+3, c:c+3]
        if sub.shape == (3,3) and (sub == 4).sum() == 8:
            out.append(((r+1, c+1), int(sub[1,1])))
            for dr in range(3):
                for dc in range(3):
                    seen.add((r+dr, c+dc))
    return out

def avatar_center(g, colr, zero_pos):
    cells = [tuple(map(int, x)) for x in np.argwhere(g == colr)]
    # X: center = point minimizing ... try: for X, arms satisfy |dr|==|dc|; for plus, dr==0 or dc==0
    # brute force: test each candidate center (including zero cell) for arm consistency
    cand = set(cells)
    if zero_pos: cand.add(zero_pos)
    best = None
    for (r0, c0) in cand:
        plus = sum(1 for (r, c) in cells if r == r0 or c == c0)
        xx = sum(1 for (r, c) in cells if abs(r - r0) == abs(c - c0))
        score = max(plus, xx)
        shape = 'plus' if plus >= xx else 'X'
        if best is None or score > best[0]:
            best = (score, (r0, c0), shape, len(cells))
    return best

# replay L1 program
L1 = [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2
for a in L1:
    f = act(a)
g = grid_of(f)
print("score", summ(f))
bx = boxes(g)
print("boxes:", bx)
z = [tuple(map(int, x)) for x in np.argwhere(g == 0)]
print("zero:", z)
for colr in (9, 12, 13):
    print("avatar", colr, avatar_center(g, colr, z[0] if z else None))

# measure movement of active avatar (c-X at zero): press 1 (up)
g0 = g
f = act(1); g1 = grid_of(f)
d = diff(g0, g1)
z1 = [tuple(map(int, x)) for x in np.argwhere(g1 == 0)]
print("after up: zero", z1, "ndiff", len(d))
f = act(3); g2 = grid_of(f)
z2 = [tuple(map(int, x)) for x in np.argwhere(g2 == 0)]
print("after left: zero", z2)
# undo
f = act(4); f = act(2)
z3 = [tuple(map(int, x)) for x in np.argwhere(grid_of(f) == 0)]
print("after undo: zero", z3)
