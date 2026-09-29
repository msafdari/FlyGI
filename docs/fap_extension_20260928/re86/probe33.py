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
    b = b[mask]
    return dict(rows=(int(b[:,0].min()), int(b[:,0].max())), cols=(int(b[:,1].min()), int(b[:,1].max())), n=int(len(b)))
seq = [1]*5 + [4] + [4,4,4] + [1,1] + [2]
labels = ["up"]*5 + ["right(approach)"] + ["right SQUEEZE"]*3 + ["up (move away)"]*2 + ["down"]
g = grid_of(f)
print("start", binfo(g))
for a, lab in zip(seq, labels):
    f = act(a)
    g = grid_of(f)
    print(lab, binfo(g), "zero", [tuple(map(int,x)) for x in np.argwhere(g==0)], "score", f.levels_completed)
