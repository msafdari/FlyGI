import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session import *

CARD8 = {'x': 48, 'y': 19}
CARD9 = {'x': 48, 'y': 36}
B_BTN = {'x': 24, 'y': 20}
POT_BORDER = {'x': 22, 'y': 18}
D_LAYER = {'x': 19, 'y': 31}
STACK9 = {'x': 19, 'y': 21}
BAR2 = {'x': 9, 'y': 31}
PANTRY9 = {'x': 9, 'y': 35}

def run(name, seq):
    fr = act(0)
    g_prev = grid_of(fr)
    for i, p in enumerate(seq):
        fr = act(6, p)
        g1 = grid_of(fr)
        nd = int((g_prev != g1).sum()) if g1 is not None else -1
        print(f'{name} step{i+1} ndiff={nd}', json.dumps(brief(g1, fr)))
        g_prev = g1

run('A: 8 then b', [CARD8, B_BTN])
run('B: 8 then pot border', [CARD8, POT_BORDER])
run('C: 8 then d-layer', [CARD8, D_LAYER])
run('D: 8 then stack9', [CARD8, STACK9])
run('E: 8 then bar2', [CARD8, BAR2])
run('F: 8 then pantry9 slot', [CARD8, PANTRY9])
