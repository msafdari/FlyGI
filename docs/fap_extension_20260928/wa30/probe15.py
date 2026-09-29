exec(open('/tmp/fap_ext/wa30/drive.py').read())
import json
prog = json.load(open('/tmp/fap_ext/wa30/prog_l1_l2.json'))
f = env.observation_space
for st in prog: f = act(st['action'])
print('after prefix: score', f.levels_completed, f.state)
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

def summary(gr, fr):
    bl = blocks(gr)
    c = sorted(k for k,v in bl.items() if 12 in v)          # rival
    p = sorted(k for k,v in bl.items() if 14 in v)          # player
    boxes = sorted(k for k,v in bl.items() if 4 in v and 9 in v)
    dockfill = sorted(k for k,v in bl.items() if k[1]>=13 and (4 in v or 12 in v))
    t = int((gr[63]==7).sum())
    return f'timer={t} score={fr.levels_completed} rival={c} boxes={boxes} dock_extra={dockfill}'

print('L3 start:', summary(g, f))
for i in range(1, 41):
    f = act(5)
    g2 = grid_of(f)
    if g2 is None:
        print(f'idle{i}: EMPTY state={f.state} score={f.levels_completed}')
        continue
    print(f'idle{i}: {summary(g2, f)} state={f.state}')
    g = g2
    if str(f.state) != 'GameState.NOT_FINISHED':
        print('TERMINAL'); break
