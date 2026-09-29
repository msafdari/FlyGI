exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

def cc(g):
    out = {}
    for colr in (9, 11):
        cells = np.argwhere(g == colr)
        if len(cells) == 0: out[colr] = None; continue
        rows = np.bincount(cells[:,0], minlength=64)
        cols = np.bincount(cells[:,1], minlength=64)
        out[colr] = (int(np.argmax(rows)), int(np.argmax(cols)))
    return out

g = grid_of(env.observation_space)
# active cross is 9 initially. Move it to bottom-right clamp.
print("== down x8 ==")
for i in range(8):
    f = act(2); g = grid_of(f)
    print("down", i, cc(g)[9], summ(f)['score'])
print("== right x8 ==")
for i in range(8):
    f = act(4); g = grid_of(f)
    print("right", i, cc(g)[9], summ(f)['score'])
print("== left x18 ==")
for i in range(18):
    f = act(3); g = grid_of(f)
    print("left", i, cc(g)[9], summ(f)['score'])
