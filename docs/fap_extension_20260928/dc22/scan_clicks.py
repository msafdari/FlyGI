import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session import *

# Scan clicks on a 2-cell lattice over the whole frame; report ndiff>1 hotspots.
fr = act(0)
g0 = grid_of(fr)
hot = {}
for y in range(1, 63, 2):
    for x in range(1, 63, 2):
        fr = act(6, {'x': x, 'y': y})
        g1 = grid_of(fr)
        nd = int((g0 != g1).sum()) if g1 is not None else -1
        sc = fr.levels_completed
        if nd > 1 or sc > 0 or str(fr.state) != 'GameState.NOT_FINISHED':
            hot[(x, y)] = (nd, sc, str(fr.state))
            fr = act(0)
            g0 = grid_of(fr)
        else:
            # timer advanced by 1; reset every 40 clicks to avoid timeout death
            pass
        # track timer: reset when close to full
        if int((grid_of(fr)[63] == 3).sum()) > 50:
            fr = act(0)
            g0 = grid_of(fr)
print('hotspots:')
for k, v in sorted(hot.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    print(f'  x={k[0]:2d} y={k[1]:2d} ndiff={v[0]} score={v[1]} state={v[2]}')
