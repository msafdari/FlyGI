import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session2 import *
from probe_l3 import to_l3, diff_groups

C8 = {'x': 52, 'y': 18}
C9 = {'x': 52, 'y': 27}
C6 = {'x': 52, 'y': 36}
CF = {'x': 52, 'y': 45}

fr = to_l3()
g_prev = grid_of(fr)

def step(st, note=''):
    global g_prev, fr
    fr = act(6, st) if isinstance(st, dict) else act(st)
    g1 = grid_of(fr)
    nd = int((g_prev[:63] != g1[:63]).sum())
    pp = player_pos(g1)
    p = (pp[0][0], pp[0][1]) if pp else None
    print(f'{note}: nd={nd} player={p} score={fr.levels_completed}')
    if isinstance(st, dict) and nd > 9:
        diff_groups(g_prev, g1, '   detail')
    g_prev = g1
    return g1

step(C9, 'C9 s9=1')
step(C8, 'C8 s8=1')
for i in range(4): step(3, f'left{i+1}')
for i in range(3): step(2, f'down{i+1}')
step(C8, 'C8 s8=0 (on d)')
for i in range(5): step(3, f'left{i+1}')
step(C9, 'C9 s9=0 (on plank)')
for i in range(3): step(3, f'left{i+1}')
step(C9, 'C9 s9=1 (on 2-block)')
for i in range(4): step(1, f'up{i+1}')
g1 = step(C6, 'C6 TELEPORT')
for i in range(3): step(1, f'up{i+1}')
for i in range(2): step(4, f'right{i+1}')
g1 = step(2, 'down onto pickup')
g1 = step(CF, 'CF click 1')
render(g1, '/tmp/fap_ext/dc22/l3_cardF1.txt')
g1 = step(CF, 'CF click 2')
