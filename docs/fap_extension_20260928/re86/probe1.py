exec(open('/tmp/fap_ext/re86/drive.py').read())

f0 = env.observation_space
g0 = grid_of(f0)
print("initial", summ(f0))

# geometry of initial frame
for col in (9, 11):  # crosses
    pass
import numpy as np
for colr in (0, 4, 9, 11, 15):
    cells = np.argwhere(g0 == colr)
    print("colour", colr, "count", len(cells))

# box centers: find 3x3 colour-4 rings
fours = np.argwhere(g0 == 4)
seen = set()
for (r, c) in fours:
    # candidate top-left of ring
    r, c = int(r), int(c)
    if (r, c) in seen: continue
    sub = g0[r:r+3, c:c+3]
    if sub.shape == (3, 3) and (sub == 4).sum() == 8 and sub[1, 1] != 4:
        print("box top-left", (r, c), "center rc", (r+1, c+1), "center colour", int(sub[1, 1]))
        for dr in range(3):
            for dc in range(3):
                seen.add((r+dr, c+dc))

# swallow test: does first post-reset action change frame?
f1 = act(1)  # up
g1 = grid_of(f1)
d = diff(g0, g1)
print("after action1 (up):", summ(f1))
print("diff count", len(d) if isinstance(d, list) else d)
if isinstance(d, list):
    for row in d[:80]:
        print(row)
