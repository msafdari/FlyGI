exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

L1 = [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2
L2 = [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7
for a in L1 + L2:
    f = act(a)
g = grid_of(f)
dots = [(6,6),(6,45),(15,51),(21,21),(27,9),(30,48),(33,33),(39,21)]
cells = set(map(tuple, np.argwhere(g == 8).tolist()))
cells |= set(map(tuple, np.argwhere(g == 0).tolist()))
for d in dots: cells.discard(d)
# remove X1 (center (48,18), arm 11) and line (row 45)
x1 = {(48,18)} | {(48+s*k, 18+t*k) for k in range(1,12) for s in (-1,1) for t in (-1,1)}
rest = {c for c in cells if c not in x1 and c[0] != 45}
print("rest n=", len(rest))
for rc in sorted(rest): print(rc)
# also line extent
line = sorted(c for (r,c) in cells if r == 45)
print("line row45 cols", line[0], "..", line[-1], "n=", len(line))
