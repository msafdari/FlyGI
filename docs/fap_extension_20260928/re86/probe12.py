exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

L1 = [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2
for a in L1:
    f = act(a)
g = grid_of(f)
dcells = sorted(tuple(map(int, x)) for x in np.argwhere(g == 13))
print("d cells:", dcells)
# cycle through avatars with 5 and read zero position each time
for k in range(4):
    f = act(5)
    g = grid_of(f)
    z = [tuple(map(int, x)) for x in np.argwhere(g == 0)]
    print("after 5 x", k+1, "zero:", z, "score", f.levels_completed)
