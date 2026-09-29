exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

def cross_centers(g):
    out = {}
    for colr in (9, 11):
        cells = np.argwhere(g == colr)
        if len(cells) == 0:
            out[colr] = None
            continue
        rows = np.bincount(cells[:,0], minlength=64)
        cols = np.bincount(cells[:,1], minlength=64)
        r = int(np.argmax(rows)); c = int(np.argmax(cols))
        out[colr] = (r, c, int(rows[r]), int(cols[c]), int(len(cells)))
    z = np.argwhere(g == 0)
    out['zero'] = [tuple(map(int, x)) for x in z]
    return out

def boxes(g):
    fours = np.argwhere(g == 4)
    out = []
    seen = set()
    for (r, c) in fours:
        r, c = int(r), int(c)
        if (r, c) in seen: continue
        sub = g[r:r+3, c:c+3]
        if sub.shape == (3,3) and (sub == 4).sum() == 8 and sub[1,1] != 4:
            out.append(((r+1, c+1), int(sub[1,1])))
            for dr in range(3):
                for dc in range(3):
                    seen.add((r+dr, c+dc))
    return out

def trow(g):
    row = g[63]
    return int((row != 15).sum())

g = grid_of(env.observation_space)
print("t0 centers", cross_centers(g), "boxes", boxes(g), "timer used", trow(g))

# drive 9-cross to (36,48): 3 ups then 4 rights
seq = [1,1,1,4,4,4,4]
for i, a in enumerate(seq):
    f = act(a)
    g2 = grid_of(f)
    d = diff(g, g2)
    interesting = [x for x in d if x[0] != 63 and not (x[2] in (5,9,0) and x[3] in (5,9,0))]
    print(f"step{i} act{a}", summ(f), cross_centers(g2)[9], cross_centers(g2)['zero'], "timer", trow(g2), "ndiff", len(d), "boxes", boxes(g2))
    if interesting:
        print("   interesting:", interesting[:30])
    g = g2
