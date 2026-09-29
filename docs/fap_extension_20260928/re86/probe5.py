exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

HEX = "0123456789abcdef"
def render(g, path):
    lines = ["    " + "".join(str(c % 10) for c in range(64))]
    for r in range(64):
        lines.append(f"{r:3d} " + "".join(HEX[int(v) % 16] for v in g[r]))
    Path(path).write_text("\n".join(lines))

def cc(g):
    out = {}
    for colr in (9, 11):
        cells = np.argwhere(g == colr)
        if len(cells) == 0: out[colr] = None; continue
        rows = np.bincount(cells[:,0], minlength=64)
        cols = np.bincount(cells[:,1], minlength=64)
        out[colr] = (int(np.argmax(rows)), int(np.argmax(cols)), int(len(cells)))
    out['z'] = [tuple(map(int, x)) for x in np.argwhere(g == 0)]
    return out

g = grid_of(env.observation_space)
seq = [1,1,1,4,4,4,4,5] + [1]*9
for a in seq:
    f = act(a)
    g = grid_of(f)
print("end", summ(f), cc(g))
render(g, '/tmp/fap_ext/re86/after_b_up.txt')

# move b-cross back down to row 9 (on the row of two b dots), then to (9,24)
for a in [2,2,2,4]:
    f = act(a)
    g = grid_of(f)
    print("act", a, summ(f), cc(g))
render(g, '/tmp/fap_ext/re86/b_at_9_24.txt')
# now b center should be (9,24) = exactly on b-dot (9,24)!
