import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session2 import *

L2 = json.loads(Path('/tmp/fap_ext/dc22/prog_l2.json').read_text())

def to_l3():
    fr = act(0)
    fr = play(L1)
    assert fr.levels_completed == 1
    fr = play(L2)
    assert fr.levels_completed == 2, fr.levels_completed
    return fr

def diff_groups(g0, g1, label):
    d = np.argwhere(g0[:63] != g1[:63])
    print(f'{label}: {len(d)} cells')
    items = {}
    for (r, c) in d:
        key = (int(g0[r, c]), int(g1[r, c]))
        items.setdefault(key, []).append((int(r), int(c)))
    for (a, bb), cells in sorted(items.items()):
        rows = sorted(set(r for r, _ in cells)); cols = sorted(set(c for _, c in cells))
        print(f'  {a:x}->{bb:x}: rows {rows[0]}-{rows[-1]} cols {cols[0]}-{cols[-1]} ({len(cells)})')

if __name__ == '__main__':
    fr = to_l3()
    g0 = grid_of(fr)
    for name, (x, y) in {'card8': (52, 18), 'card9': (52, 27), 'card6': (52, 36), 'card-invis': (52, 45)}.items():
        fr = act(6, {'x': x, 'y': y})
        g1 = grid_of(fr)
        diff_groups(g0, g1, f'{name} click')
        print('   player', player_pos(g1)[:1], 'score', fr.levels_completed)
        fr = act(6, {'x': x, 'y': y})
        g2 = grid_of(fr)
        d2 = int((g1[:63] != g2[:63]).sum())
        print(f'   re-click nd={d2}')
        g0 = g2
