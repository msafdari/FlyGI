exec(open('/tmp/fap_ext/wa30/drive.py').read())
import json
prog = json.load(open('/tmp/fap_ext/wa30/prog_l1_l2_l3.json'))
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

def summary(gr, fr):
    bl = blocks(gr)
    riv = sorted(k for k,v in bl.items() if 12 in v)
    bx = sorted((k, v) for k,v in bl.items() if 9 in v and 2 not in v and 12 not in v)
    return f'timer={int((gr[63]==7).sum())} score={fr.levels_completed} player={pb(gr)} rival={riv} boxes={bx}'

# replicate probe19 prefix: 8 idles, then plant box (10,6) into left wall (10,5)
for i in range(8): f = act(5)
for a in [2,2,3,5,3]: f = act(a)
g = grid_of(f)
print('planted-held:', summary(g, f))
f = act(5); g = grid_of(f)     # drop
print('dropped:', summary(g, f))
f = act(4); g = grid_of(f)     # step away east
print('released:', summary(g, f))
prev = None
for i in range(1, 41):
    f = act(5); g2 = grid_of(f)
    s = summary(g2, f)
    if s != prev: print(f'idle{i}: {s}')
    prev = s; g = g2
    if str(f.state) != 'GameState.NOT_FINISHED':
        print('TERMINAL', f.state); break
