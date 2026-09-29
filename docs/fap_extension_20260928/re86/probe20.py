exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np
HEX = "0123456789abcdef"
def render(g, path):
    lines = ["    " + "".join(str(c % 10) for c in range(64))]
    for r in range(64):
        lines.append(f"{r:3d} " + "".join(HEX[int(v) % 16] for v in g[r]))
    Path(path).write_text("\n".join(lines))

L1 = [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2
L2 = [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7
L3 = [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9
L4 = ([1]*10 + [3]*8 +            # plus -> c tile (6,30)
      [3]*5 + [2]*8 +             # plus -> target (30,15)
      [5] +                       # switch to X (21,24)
      [2]*12 + [4]*10 +           # X -> e tile (57,54)
      [1]*9 + [3]*5)              # X -> target (30,39)
for a in L1 + L2 + L3 + L4:
    f = act(a)
print("after L4", summ(f))
g = grid_of(f)
z = [tuple(map(int,x)) for x in np.argwhere(g==0)]
from collections import Counter
print("zero", z, Counter(int(v) for v in g.flatten()))
render(g, '/tmp/fap_ext/re86/after_L4.txt')
