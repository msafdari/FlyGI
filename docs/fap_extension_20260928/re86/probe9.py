exec(open('/tmp/fap_ext/re86/drive.py').read())
import numpy as np

def zero(g):
    return [tuple(map(int, x)) for x in np.argwhere(g == 0)]

g = grid_of(env.observation_space)
# 9-cross (active) from (45,36) to (24,48): 7 ups, 4 rights
prog = [1]*7 + [4]*4
for a in prog:
    f = act(a); g = grid_of(f)
print("9-cross parked", summ(f), "zero at", zero(g))
# switch to b-cross
f = act(5); g = grid_of(f)
print("switched", summ(f), "zero at", zero(g))
# b-cross from (27,21) to (9,15): 6 ups, 2 lefts
for a in [1]*6 + [3]*2:
    f = act(a); g = grid_of(f)
    print("b act", a, summ(f), "zero", zero(g))
