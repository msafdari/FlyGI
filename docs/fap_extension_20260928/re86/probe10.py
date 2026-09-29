exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np
HEX = "0123456789abcdef"
def render(g, path):
    lines = ["    " + "".join(str(c % 10) for c in range(64))]
    for r in range(64):
        lines.append(f"{r:3d} " + "".join(HEX[int(v) % 16] for v in g[r]))
    Path(path).write_text("\n".join(lines))

L1 = [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2
for a in L1:
    f = act(a)
g = grid_of(f)
print("after L1 prog", summ(f))
render(g, '/tmp/fap_ext/re86/level2_start.txt')
from collections import Counter
print(Counter(int(v) for v in g.flatten()))
