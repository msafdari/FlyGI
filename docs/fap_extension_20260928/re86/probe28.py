exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np
HEX = "0123456789abcdef"
def render(g, path):
    lines = ["    " + "".join(str(c % 10) for c in range(64))]
    for r in range(64):
        lines.append(f"{r:3d} " + "".join(HEX[int(v) % 16] for v in g[r]))
    Path(path).write_text("\n".join(lines))

PROGS = [
    [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2,
    [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7,
    [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9,
    [1]*10 + [3]*8 + [3]*5 + [2]*8 + [5] + [2]*12 + [4]*10 + [1]*9 + [3]*5,
]
for P in PROGS:
    for a in P:
        f = act(a)
L5 = ([3]*5 + [2]*2 + [4]*7 + [1]*11 +      # X -> 9 tile touch -> (15,30)
      [5] +                                  # -> diamond
      [2]*10 + [4]*7 + [1]*4 +               # diamond -> 8 touch at (48,51) -> (36,51)
      [5] +                                  # -> plus
      [3]*15 + [2]*7 + [1] + [4]*8)          # plus -> 9 touch at (54,9) -> (51,33)
for i, a in enumerate(L5):
    f = act(a)
    if f.levels_completed >= 5:
        print("LEVEL FELL at step", i, "of", len(L5))
        break
print("final", summ(f))
g = grid_of(f)
render(g, '/tmp/fap_ext/re86/after_L5.txt')
from collections import Counter
print(Counter(int(v) for v in g.flatten()))
print("zero", [tuple(map(int,x)) for x in np.argwhere(g==0)])
