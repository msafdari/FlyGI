exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

PROGS = [
    [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2,
    [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7,
    [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9,
    [1]*10 + [3]*8 + [3]*5 + [2]*8 + [5] + [2]*12 + [4]*10 + [1]*9 + [3]*5,
    [3]*5 + [2]*2 + [4]*7 + [1]*11 + [5] + [2]*10 + [4]*7 + [1]*4 + [5] + [3]*15 + [2]*7 + [1] + [4]*8,
]
for P in PROGS:
    for a in P:
        f = act(a)
def binfo(g):
    b = np.argwhere(g == 11)
    mask = ~(((b[:,0] == 30) | (b[:,0] == 57)) & ((b[:,1] == 45) | (b[:,1] == 54)))
    b = b[mask]  # drop the four b-dots
    return (int(b[:,0].min()), int(b[:,0].max()), int(b[:,1].min()), int(b[:,1].max()), len(b))
g = grid_of(f)
print("start b ring", binfo(g), "zero", [tuple(map(int,x)) for x in np.argwhere(g==0)])
for i, a in enumerate([3]*8):
    f = act(a)
    g = grid_of(f)
    print(i, "left:", binfo(g), "zero", [tuple(map(int,x)) for x in np.argwhere(g==0)])
for i, a in enumerate([4]*4):
    f = act(a)
    g = grid_of(f)
    print(i, "right:", binfo(g), "zero", [tuple(map(int,x)) for x in np.argwhere(g==0)])
