exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

def cc(g):
    out = {}
    for colr in (9, 11):
        cells = np.argwhere(g == colr)
        if len(cells) == 0: out[colr] = None; continue
        rows = np.bincount(cells[:,0], minlength=64)
        cols = np.bincount(cells[:,1], minlength=64)
        out[colr] = (int(np.argmax(rows)), int(np.argmax(cols)), int(len(cells)))
    out['z'] = [tuple(map(int, x)) for x in np.argwhere(g == 0)]
    return out

g = grid_of(env.observation_space)
seq = [1,1,1,4,4,4,4,5] + [1]*9 + [2,2,2,4]
for a in seq:
    f = act(a)
    g = grid_of(f)
print("at b-dot", summ(f), cc(g))
# press 5 exactly on b-dot (9,24)
f = act(5)
g2 = grid_of(f)
d = diff(g, g2)
print("after 5", summ(f), cc(g2), "ndiff", len(d))
for row in d[:50]: print("  ", row)
