exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

def cross_centers(g):
    out = {}
    for colr in (9, 11):
        cells = np.argwhere(g == colr)
        if len(cells) == 0: continue
        rows = np.bincount(cells[:,0], minlength=64)
        cols = np.bincount(cells[:,1], minlength=64)
        # cross = long row + long col
        r = int(np.argmax(rows)); c = int(np.argmax(cols))
        if rows[r] > 5 and cols[c] > 5:
            out[colr] = (r, c, int(rows[r]), int(cols[c]))
    z = np.argwhere(g == 0)
    out['zero'] = [tuple(map(int, x)) for x in z]
    return out

def timer(g):
    row = g[63]
    return {int(v): int((row == v).sum()) for v in np.unique(row)}

g = grid_of(env.observation_space)
print("t0", cross_centers(g), timer(g))

seq = [1, 1, 1, 2, 3, 3, 4, 5]
for i, a in enumerate(seq):
    f = act(a)
    g2 = grid_of(f)
    d = diff(g, g2)
    print(f"step{i} act{a}", summ(f), "centers", cross_centers(g2), "timer", timer(g2), "ndiff", len(d))
    if a == 5:
        for row in d[:60]:
            print("   ", row)
    g = g2
