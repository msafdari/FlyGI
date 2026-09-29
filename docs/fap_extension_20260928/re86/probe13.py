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
prog = L1 + L2
for i, a in enumerate(prog):
    f = act(a)
    if f.levels_completed > 0 and i < len(L1):
        pass
print("final", summ(f))
g = grid_of(f)
z = [tuple(map(int, x)) for x in np.argwhere(g == 0)]
print("zero", z)
render(g, '/tmp/fap_ext/re86/after_L2_attempt.txt')
from collections import Counter
print(Counter(int(v) for v in g.flatten()))
