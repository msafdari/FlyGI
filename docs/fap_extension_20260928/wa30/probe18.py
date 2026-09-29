exec(open('/tmp/fap_ext/wa30/drive.py').read())
import json
prog = json.load(open('/tmp/fap_ext/wa30/prog_l1_l2.json'))
f = env.observation_space
for st in prog: f = act(st['action'])

def blocks(gr):
    out = {}
    for br in range(16):
        for bc in range(16):
            if br == 15: continue
            v = gr[br*4:(br+1)*4, bc*4:(bc+1)*4]
            vals = frozenset(int(x) for x in np.unique(v))
            if vals != frozenset({1}):
                out[(br,bc)] = tuple(sorted(vals))
    return out

def pb(gr):
    e = np.argwhere(gr==14)
    return (int(e[:,0].min()//4), int(e[:,1].min()//4)) if len(e) else None

rec = []
st = {'f': f, 'g': grid_of(f)}
def do(aid):
    st['f'] = act(aid); st['g'] = grid_of(st['f']); rec.append(aid)
    return st['f']

def socket_free(blk):
    v = blocks(st['g']).get(blk, (1,))
    return set(v) <= {1,2}

def status(tag):
    g = st['g']; f = st['f']
    bl = blocks(g)
    riv = sorted(k for k,v in bl.items() if 12 in v)
    bx = sorted(k for k,v in bl.items() if 9 in v and 2 not in v and 12 not in v)
    print(f'{tag}: n={len(rec)} timer={int((g[63]==7).sum())} score={f.levels_completed} '
          f'state={f.state} player={pb(g)} rival={riv} boxes={bx}')

# P1-P4: box (5,5) -> north socket (3,8)
for a in [1,1,1,1]: do(a)
for a in [4,5]: do(a)              # mark, pick (carry E)
for a in [1,1,4,4]: do(a)          # to (3,6), box (3,7)
while not socket_free((3,8)) and len(rec) < 40:
    do(3); do(4)                   # shuffle-wait carrying
do(4)                              # plant: player (3,7), box (3,8)
do(5); do(2)                       # drop, step away S -> (4,7)
status('boxA planted')

# P5-P8: box (4,2) -> south socket (8,8)
for a in [2,3,3,3,3,3,3,1]: do(a)  # (4,7)->(5,7)->(5,1)->(4,1)
for a in [4,5]: do(a)              # mark, pick
for a in [2,2,2,2]: do(a)          # (8,1), box (8,2)
for a in [4,4,4,4]: do(a)          # (8,5), box (8,6)
do(4)                              # (8,6), box (8,7)
while not socket_free((8,8)) and len(rec) < 80:
    do(3); do(4)
do(4)                              # plant
do(5); do(1)                       # drop, step away N -> (7,7)
status('boxB planted')

# P9-P11: box (11,3) -> south socket (8,8) (wait for rival to clear it)
for a in [3,3,3,3,3]: do(a)        # (7,2)
for a in [2,2,2,2]: do(a)          # (11,2)
for a in [4,5]: do(a)              # mark, pick
for a in [1,1,1]: do(a)            # (8,2), box (8,3)
for a in [4,4,4,4]: do(a)          # (8,6), box (8,7)
shuffles = 0
while not socket_free((8,8)) and shuffles < 40:
    do(3); do(4); shuffles += 1
    if str(st['f'].state) != 'GameState.NOT_FINISHED': break
status('pre-plant C')
do(4)                              # plant
do(5); do(1)                       # drop, step away
status('boxC planted')

# P12: idle until terminal or score change
for i in range(70):
    do(5)
    f = st['f']
    if f.levels_completed > 2 or str(f.state) != 'GameState.NOT_FINISHED':
        status(f'EVENT idle{i}')
        break
status('final')
json.dump(rec, open('/tmp/fap_ext/wa30/l3_attempt2.json','w'))
g = st['g']
if g is not None:
    hexd='0123456789abcdef'
    for r in range(0,64):
        row = ''.join(hexd[int(v)&15] for v in g[r])
        if set(row) != {'1'}: print(f'{r:3d} {row}')
