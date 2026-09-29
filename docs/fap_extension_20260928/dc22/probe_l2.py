import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session2 import *

fr = to_l2()
g0 = grid_of(fr)
fr = act(6, {'x': 52, 'y': 22})
g1 = grid_of(fr)
d = np.argwhere(g0[:63] != g1[:63])
items = {}
for (r, c) in d:
    key = (int(g0[r, c]), int(g1[r, c]))
    items.setdefault(key, []).append((int(r), int(c)))
print('card6 toggle diff:')
for (a, bb), cells in items.items():
    rows = sorted(set(r for r, _ in cells)); cols = sorted(set(c for _, c in cells))
    print(f'  {a:x}->{bb:x}: rows {rows[0]}-{rows[-1]} cols {cols[0]}-{cols[-1]} ({len(cells)} cells)')
render(g1, '/tmp/fap_ext/dc22/l2_after_card6.txt')
