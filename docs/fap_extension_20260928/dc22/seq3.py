import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session import *

CARD8 = {'x': 48, 'y': 19}
CARD9 = {'x': 48, 'y': 36}
B_BTN = {'x': 24, 'y': 20}

def run(name, seq, render_last=None):
    fr = act(0)
    g_prev = grid_of(fr)
    for i, st in enumerate(seq):
        if isinstance(st, dict):
            fr = act(6, st)
        else:
            fr = act(st)
        g1 = grid_of(fr)
        nd = int((g_prev != g1).sum()) if (g1 is not None and g_prev is not None) else -1
        print(f'{name} step{i+1} ndiff={nd}', json.dumps(brief(g1, fr)))
        g_prev = g1
    if render_last and g_prev is not None:
        render(g_prev, render_last)

run('ordered 9,8,9', [CARD9, CARD8, CARD9, 1, B_BTN])
run('ordered 9,8,9 then cards again', [CARD9, CARD8, CARD9, CARD8])
