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
seq = [5,5] + [3]*15 + [2]*7 + [1] + [4]*8
for a in seq:
    f = act(a)
g = grid_of(f)
print("parked", [tuple(map(int,x)) for x in np.argwhere(g==0)], "score", f.levels_completed,
      "9count", int((g==9).sum()), "ccount", int((g==12).sum()))
f = act(1)  # nudge up
g = grid_of(f)
print("after nudge score", f.levels_completed, "9count", int((g==9).sum()))
for dot in [(45,33),(60,33),(51,23),(51,45),(6,21),(6,38)]:
    print("dot", dot, int(g[dot]))
render(g, '/tmp/fap_ext/re86/L5_after_plus_park.txt')
