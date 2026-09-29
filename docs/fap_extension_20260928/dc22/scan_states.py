import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session import *

CARD8 = {'x': 48, 'y': 19}
CARD9 = {'x': 48, 'y': 36}

def scan_from(name, setup):
    hits = []
    fr = act(0)
    for p in setup:
        fr = act(6, p)
    base = grid_of(fr)
    count = 0
    for y in range(1, 63, 2):
        for x in range(1, 63, 2):
            fr = act(6, {'x': x, 'y': y})
            g1 = grid_of(fr)
            # ignore timer row in diff
            nd = int((base[:63] != g1[:63]).sum()) if g1 is not None else -1
            sc = fr.levels_completed
            st = str(fr.state)
            if nd > 0 or sc > 0 or st != 'GameState.NOT_FINISHED':
                hits.append((x, y, nd, sc, st))
            count += 1
            # re-establish base state
            fr = act(0)
            for p in setup:
                fr = act(6, p)
            base = grid_of(fr)
    print(f'--- scan {name}: {len(hits)} hits')
    for x, y, nd, sc, st in hits:
        print(f'  x={x:2d} y={y:2d} ndiff={nd} score={sc} state={st}')

scan_from('stack {8,d} (9out,8in)', [CARD9, CARD8])
scan_from('stack {9,8,d} (8in)', [CARD8])
scan_from('stack {d} (9out)', [CARD9])
