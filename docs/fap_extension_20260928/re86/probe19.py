exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

L1 = [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2
L2 = [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7
L3 = [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9
L4a = [1]*2 + [3]*13 + [5] + [2]*3 + [4]*5
for a in L1 + L2 + L3 + L4a:
    f = act(a)
g = grid_of(f)
# switch to plus, move right 1, check dot cells
f = act(5); print("switched, zero", [tuple(map(int,x)) for x in np.argwhere(grid_of(f)==0)])
f = act(4)
g2 = grid_of(f)
for dot in [(18,15),(30,27),(43,15)]:
    print("c-dot", dot, "colour now", int(g2[dot]))
print("score", f.levels_completed)
# move back left
f = act(3)
g3 = grid_of(f)
print("back on target, score", f.levels_completed)
# try parking plus center on the c tile interior (6,30): from (30,15): 8 ups, 5 rights
for a in [1]*8 + [4]*5:
    f = act(a)
g4 = grid_of(f)
z = [tuple(map(int,x)) for x in np.argwhere(g4==0)]
from collections import Counter
print("at c-tile?", z, "score", f.levels_completed, Counter(int(v) for v in g4.flatten()))
