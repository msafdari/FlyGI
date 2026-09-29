exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

def cc(g):
    out = {}
    for colr in (9, 11):
        cells = np.argwhere(g == colr)
        if len(cells) == 0:
            out[colr] = None; continue
        rows = np.bincount(cells[:,0], minlength=64)
        cols = np.bincount(cells[:,1], minlength=64)
        r = int(np.argmax(rows)); c = int(np.argmax(cols))
        out[colr] = (r, c, int(len(cells)))
    z = np.argwhere(g == 0)
    out['z'] = [tuple(map(int, x)) for x in z]
    return out

def trow(g): return int((g[63] != 15).sum())

g = grid_of(env.observation_space)
# go to (36,48) then press 5
for a in [1,1,1,4,4,4,4,5]:
    f = act(a)
    g2 = grid_of(f)
    d = diff(g, g2)
    print("act", a, summ(f), cc(g2), "timer", trow(g2), "ndiff", len(d))
    if a == 5:
        for row in d[:40]: print("   ", row)
    g = g2

# now press up repeatedly to find clamping
print("=== press up 12x ===")
for i in range(12):
    f = act(1)
    g2 = grid_of(f)
    print("up", i, summ(f), cc(g2), "timer", trow(g2))
    g = g2
