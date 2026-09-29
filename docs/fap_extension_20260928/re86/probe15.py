exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np
from collections import deque

L1 = [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2
L2 = [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7
for a in L1 + L2:
    f = act(a)
g = grid_of(f)
print("score", f.levels_completed)

# avatar cells: colour 8 cells NOT inside a 4-ring box (dot centers)
dots = [(6,6),(6,45),(15,51),(21,21),(27,9),(30,48),(33,33),(39,21)]
cells = set(map(tuple, np.argwhere(g == 8).tolist()))
cells |= set(map(tuple, np.argwhere(g == 0).tolist()))  # active center
for d in dots: cells.discard(d)

centers = [(45,30), (48,18), (48,45)]
for (r0, c0) in centers:
    # classify by counting cells on plus arms vs X arms vs diamond ring
    on_row = sorted(c for (r, c) in cells if r == r0)
    on_col = sorted(r for (r, c) in cells if c == c0)
    diag = [(r, c) for (r, c) in cells if abs(r-r0) == abs(c-c0) and r != r0]
    print("center", (r0, c0))
    print("  row cells cols", on_row[:5], "...", on_row[-5:], "n=", len(on_row))
    print("  col cells rows", on_col, "n=", len(on_col))
    print("  diag n=", len(diag))
    if diag:
        dists = sorted(abs(r-r0) for (r, c) in diag)
        print("  diag dists max", dists[-1], "quadrant counts:",
              sum(1 for (r,c) in diag if r<r0 and c<c0), sum(1 for (r,c) in diag if r<r0 and c>c0),
              sum(1 for (r,c) in diag if r>r0 and c<c0), sum(1 for (r,c) in diag if r>r0 and c>c0))
    ring = [(r, c) for (r, c) in cells if abs(r-r0)+abs(c-c0) > 0 and abs(r-r0)+abs(c-c0) == 9]
    print("  L1ring9 n=", len(ring))
