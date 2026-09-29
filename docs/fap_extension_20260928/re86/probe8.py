exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np
HEX = "0123456789abcdef"
def render(g, path):
    lines = ["    " + "".join(str(c % 10) for c in range(64))]
    for r in range(64):
        lines.append(f"{r:3d} " + "".join(HEX[int(v) % 16] for v in g[r]))
    Path(path).write_text("\n".join(lines))

g = grid_of(env.observation_space)
for i in range(5):
    f = act(2); g = grid_of(f)
render(g, '/tmp/fap_ext/re86/down5.txt')
print("after 5 downs", summ(f))
f = act(2); g2 = grid_of(f)
render(g2, '/tmp/fap_ext/re86/down6.txt')
print("after 6th down", summ(f))
d = diff(g, g2)
print("ndiff", len(d))
for row in d[:80]: print("  ", row)
