exec(open('/tmp/fap_ext/wa30/drive.py').read())
import json
prog = json.load(open('/tmp/fap_ext/wa30/prog_l1_l2.json'))
f = env.observation_space
for st in prog: f = act(st['action'])
# replay probe12 prefix: R5 (2 wall bumps), 18 waits, U1,R2
for aid in [4,4,4,4,4] + [5]*18 + [1,4,4]:
    f = act(aid)
g = grid_of(f)

def pb(gr):
    e = np.argwhere(gr==14)
    return (int((e[:,0].min())//4), int(e[:,1].min()//4)) if len(e) else None

# player at (8,7). go pick box (5,5) from its west side, then push east into the wall
seq = [1,1,1,        # up to (5,7)
       1, 3,3,3,3,   # (4,7) then left to (4,3)
       2, 4,         # down (5,3), east arrival -> mark (5,5)? wait box at (5,5), player (5,4) after R
       5,            # pick
       4,4,4]        # carry east: box (5,6),(5,7),(5,8)=WALL?
for i,aid in enumerate(seq):
    f = act(aid); g2 = grid_of(f)
    print(f'{i}: a{aid} {diff(g,g2)} player={pb(g2)} timer={int((g2[63]==7).sum())} score={f.levels_completed}')
    g = g2
show(g, 16, 28)
