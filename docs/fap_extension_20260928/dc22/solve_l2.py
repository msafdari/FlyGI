import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session2 import *

CARD_TOP = {'x': 52, 'y': 22}    # toggles 7-planks <-> 7-ladder(cols16-19)
CARD_MID = {'x': 52, 'y': 31}    # invisible 8-card (needs pickup)
CARD_BOT = {'x': 52, 'y': 40}    # 9-block side-dock <-> ladder(cols4-7 r32-39)

fr = to_l2()
g_prev = grid_of(fr)
log = []

def step(st, note=''):
    global g_prev
    if isinstance(st, dict):
        fr = act(6, st)
    else:
        fr = act(st)
    g1 = grid_of(fr)
    nd = int((g_prev[:63] != g1[:63]).sum())
    pp = player_pos(g1)
    p = (pp[0][0], pp[0][1]) if pp else None
    print(f'{note}: act={st} nd={nd} player={p} score={fr.levels_completed} state={fr.state}')
    g_prev = g1
    return fr, g1

# Phase 1: 9 -> ladder, descend, cross planks to 6-block
step(CARD_BOT, 'card9->ladder')
for i in range(5): step(2, f'down{i+1}')
for i in range(5): step(4, f'right{i+1}')
# Phase 2: planks -> 7-ladder (standing on 6-block), descend to pickup
step(CARD_TOP, 'planks->ladder')
for i in range(6): step(2, f'down{i+1}')
# Phase 3: back up, restore planks, cross left, climb, restore 9
for i in range(6): step(1, f'up{i+1}')
step(CARD_TOP, 'ladder->planks')
for i in range(5): step(3, f'left{i+1}')
for i in range(5): step(1, f'up{i+1}')
step(CARD_BOT, '9->sidedock')
for i in range(2): step(4, f'right{i+1}')
for i in range(3): step(1, f'up{i+1}')
for i in range(6): step(4, f'right{i+1}')
# Phase 4: unlockable 8-card
fr, g1 = step(CARD_MID, 'click 8-card (unlocked?)')
render(g1, '/tmp/fap_ext/dc22/l2_after_8card.txt')
for i in range(6): fr, g1 = step(1, f'up{i+1}')
render(g1, '/tmp/fap_ext/dc22/l2_final.txt')
print('FINAL score', fr.levels_completed, fr.state)
