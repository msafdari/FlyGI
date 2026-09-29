import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session import *

CARD8 = {'x': 48, 'y': 19}
fr = act(0)
g = grid_of(fr)
print('r63 after reset:', ''.join(format(int(v),'x') for v in g[63][:20]))
for i in range(6):
    fr = act(1 if i%2 else 2)
    g = grid_of(fr)
    print(f'r63 after move{i+1}:', ''.join(format(int(v),'x') for v in g[63][:20]))
fr = act(6, CARD8)
g = grid_of(fr)
print('r63 after card8 :', ''.join(format(int(v),'x') for v in g[63][:20]))
fr = act(6, {'x':24,'y':20})
g = grid_of(fr)
print('r63 after b-click:', ''.join(format(int(v),'x') for v in g[63][:20]))
fr = act(6, {'x':24,'y':20})
g = grid_of(fr)
print('r63 after b-click2:', ''.join(format(int(v),'x') for v in g[63][:20]))
# also watch the far end of the row
print('r63 tail:', ''.join(format(int(v),'x') for v in g[63][44:]))
