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
    [3]*5 + [2]*2 + [4]*7 + [1]*11 + [5] + [2]*10 + [4]*7 + [1]*4 + [5] + [3]*15 + [2]*7 + [1] + [4]*8,
    [1]*5 + [4] + [4]*3 + [1]*6 + [4]*9 + [2]*10 + [5] + [2]*11 + [3]*6 + [1]*2 + [4]*6 + [1]*3 + [3]*2 + [1]*8 + [3]*10,
]
for P in PROGS:
    for a in P:
        f = act(a)
for a in [1]*14 + [2]*4 + [4]*8 + [2]*3 + [3]*3 + [1] + [4]*7:
    f = act(a)
render(grid_of(f), '/tmp/fap_ext/re86/L7_P1_end.txt')
for a in [5] + [1]*6 + [4]*2 + [1]*5 + [4]*4 + [1] + [2] + [3]*10:
    f = act(a)
render(grid_of(f), '/tmp/fap_ext/re86/L7_P2_end.txt')
print("done", f.levels_completed)
