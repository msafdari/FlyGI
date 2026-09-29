exec(open('/tmp/fap_ext/wa30/drive.py').read())
import json
prog = json.load(open('/tmp/fap_ext/wa30/prog_l1_l2_l3.json'))
f = env.observation_space
for st in prog: f = act(st['action'])
print('L4 start: score', f.levels_completed, f.state)
g = grid_of(f)

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

def summary(gr, fr):
    bl = blocks(gr)
    riv = sorted(k for k,v in bl.items() if 12 in v)
    bx = sorted(k for k,v in bl.items() if 9 in v and 2 not in v and 12 not in v)
    return f'timer={int((gr[63]==7).sum())} score={fr.levels_completed} player={pb(gr)} rival={riv} boxes={bx}'

# 1) watch rivals for 8 idles
prev = None
for i in range(8):
    f = act(5); g2 = grid_of(f)
    s = summary(g2, f)
    if s != prev: print(f'idle{i}: {s}')
    prev = s; g = g2

# 2) wall-plant test: pick box (10,6) from its east side, push west into wall col5
for aid,l in [(2,'D'),(2,'D'),(3,'bumpW'),(5,'pick'),(3,'push-into-wall')]:
    f = act(aid); g2 = grid_of(f)
    print(f'{l}: {diff(g,g2)} player={pb(g2)}')
    g = g2
bl = blocks(g)
print('wall blocks (10,5),(11,6),(10,6):', {k: bl.get(k) for k in [(10,5),(11,6),(10,6),(10,7)]})
# 3) try pushing down into bottom wall with same box if still carried
for aid,l in [(2,'D-carry'),(2,'D-into-bottom-wall')]:
    f = act(aid); g2 = grid_of(f)
    print(f'{l}: {diff(g,g2)} player={pb(g2)}')
    g = g2
bl = blocks(g)
print('blocks near bottom wall:', {k: v for k,v in bl.items() if k[0] in (10,11) and 4 <= k[1] <= 11})
print(summary(g, f))
