import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session import *

CARD8 = {'x': 48, 'y': 19}
CARD9 = {'x': 48, 'y': 36}

# cursor starts at pad cell (1,1) [rows40-41, cols10-11]. Moves: 1=up,2=down,3=left,4=right
moves_to = {
    (0,0): [1,3], (0,1): [1], (0,2): [1,4],
    (1,0): [3],   (1,1): [],  (1,2): [4],
    (2,0): [2,3], (2,1): [2], (2,2): [2,4],
}
for pos, mv in moves_to.items():
    fr = act(0)
    for m in mv:
        fr = act(m)
    g_before = grid_of(fr)
    fr = act(6, CARD8)
    g1 = grid_of(fr)
    nd = int((g_before != g1).sum())
    b = brief(g1, fr)
    print(f'pad{pos} then card8: ndiff={nd} stack_rows={[r for r,_ in b["stack"]]} bar={b["bar"]} score={b["score"]}')

# can the cursor leave the pad? push up 3 times
fr = act(0)
for i in range(4):
    fr = act(1)
    b = brief(grid_of(fr), fr)
    print('up x%d cursor=%s' % (i+1, b['cursor']))

# timer budget: spam moves until state changes
fr = act(0)
n = 0
while n < 200:
    fr = act(1 if n % 2 == 0 else 2)
    n += 1
    if str(fr.state) != 'GameState.NOT_FINISHED':
        break
g1 = grid_of(fr)
print('after', n, 'actions state', fr.state, 'score', fr.levels_completed,
      'timer', int((g1[63]==3).sum()) if g1 is not None else None)
if g1 is not None:
    render(g1, '/tmp/fap_ext/dc22/after_timeout.txt')
fr = act(0)
print('post-reset state', fr.state)
