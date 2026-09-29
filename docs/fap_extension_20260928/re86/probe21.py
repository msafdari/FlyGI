exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

PROGS = [
    [1]*7 + [4]*4 + [5] + [1]*6 + [3]*2,
    [2]*10 + [3]*3 + [5] + [1]*7 + [3]*7 + [5] + [2]*2 + [3]*7,
    [1]*13 + [3] + [5] + [1]*8 + [4]*8 + [5] + [1]*6 + [3]*9,
    [1]*10 + [3]*8 + [3]*5 + [2]*8 + [5] + [2]*12 + [4]*10 + [1]*9 + [3]*5,
]
for P in PROGS:
    for a in P:
        f = act(a)
print("score", f.levels_completed)
# cycle to find actives
for k in range(4):
    f = act(5)
    g = grid_of(f)
    z = [tuple(map(int,x)) for x in np.argwhere(g==0)][0]
    print("cycle", k, "zero", z)
# active order back to b-X? current zero after 4 cycles
# find c-plus in the cycle: move to it
while True:
    g = grid_of(f)
    z = [tuple(map(int,x)) for x in np.argwhere(g==0)][0]
    if z == (33, 55): break
    f = act(5)
# move plus up 2 to reveal hidden dots
f = act(1); f = act(1)
g = grid_of(f)
for dot in [(33,57),(42,55)]:
    print("hidden dot", dot, "colour", int(g[dot]))
print("score", f.levels_completed)
# move back down 2
f = act(2); f = act(2)
print("restored, score", f.levels_completed)
