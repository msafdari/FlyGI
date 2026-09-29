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

def summary(gr, fr):
    bl = blocks(gr)
    c = sorted(k for k,v in bl.items() if 12 in v)
    boxes = sorted(k for k,v in bl.items() if 9 in v and 2 not in v)
    t = int((gr[63]==7).sum())
    return f'timer={t} score={fr.levels_completed} rival={c} boxes9={boxes}'

# 1) idle 28 so rival finishes both ferry runs and parks at (8,14)
for i in range(28): f = act(5)
g = grid_of(f)
print('after park:', summary(g, f), 'state', f.state)

# 2) plant box (5,5) into north socket (3,8): U4, bumpE, pick, U2, R3, drop
seq = [1,1,1,1, 4, 5, 1,1, 4,4,4, 5]
lab = ['U','U','U','U','bumpE','pick','U','U','R','R','R','drop']
for aid, l in zip(seq, lab):
    f = act(aid); g2 = grid_of(f)
    print(f'{l}: {diff(g,g2)} {summary(g2,f)}')
    g = g2
print('plug block (3,8) cells:'); show(g, 12, 16, 28, 40)

# 3) idle 34, watch rival
prev = None
for i in range(1, 35):
    f = act(5); g2 = grid_of(f)
    if g2 is None:
        print(f'idle{i}: EMPTY state={f.state} score={f.levels_completed}'); continue
    s = summary(g2, f)
    if s != prev: print(f'idle{i}: {s} state={f.state}')
    prev = s; g = g2
    if str(f.state) != 'GameState.NOT_FINISHED':
        print('TERMINAL'); break
print('final dock area:'); show(g, 24, 40, 48, 64)
