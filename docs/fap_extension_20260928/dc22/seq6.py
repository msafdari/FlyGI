import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session import *

CARD8 = {'x': 48, 'y': 19}
CARD9 = {'x': 48, 'y': 36}
B_BTN = {'x': 24, 'y': 20}
POT = {'x': 26, 'y': 22}

def run(name, seq):
    fr = act(0)
    g_prev = grid_of(fr)
    for i, st in enumerate(seq):
        fr = act(6, st) if isinstance(st, dict) else act(st)
        g1 = grid_of(fr)
        nd = int((g_prev != g1).sum()) if (g1 is not None and g_prev is not None) else -1
        b = brief(g1, fr)
        stk = ''.join(sorted(set(v[0] for _, v in b['stack'] if not v.startswith('4'))))
        print(f'{name} s{i+1} nd={nd} stack_cols={stk} avail={fr.available_actions} score={b["score"]} state={b["state"]}')
        g_prev = g1

run('9out,8in,8click', [CARD9, CARD8, CARD8])
run('9out,8in,pot,b', [CARD9, CARD8, POT, B_BTN])
run('9out,potclick,b', [CARD9, POT, B_BTN])
run('empty stack? both out', [CARD9, POT])
