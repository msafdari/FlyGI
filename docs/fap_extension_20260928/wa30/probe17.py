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

def summary(gr, fr):
    bl = blocks(gr)
    c = sorted(k for k,v in bl.items() if 12 in v)
    boxes = sorted((k, v) for k,v in bl.items() if 9 in v and 2 not in v and 12 not in v)
    t = int((gr[63]==7).sum())
    return f'timer={t} score={fr.levels_completed} player={pb(gr)} rival={c} boxes={boxes}'

for i in range(28): f = act(5)
g = grid_of(f)
print('parked:', summary(g, f))

# A) crossing test at open south socket (8,8): to (8,7) then try east twice
for aid,l in [(1,'U'),(4,'R'),(4,'R'),(4,'R'),(4,'R-into-socket'),(4,'R-again')]:
    f = act(aid); g2 = grid_of(f)
    print(f'{l}: {diff(g,g2)} player={pb(g2)}')
    g = g2

# B) plant (5,5) into north socket, then STEP AWAY, watch rival
# player position depends on A; recompute route via pb
p = pb(g)
print('player now', p)
# route back to (5,4): generic walk
def walk(seq):
    global f, g
    for aid in seq:
        f = act(aid); g = grid_of(f)
# from wherever: go west to col4 then up to row5
r, c = p
seq = [3]*(c-4) if c>4 else [4]*(4-c)
seq += [1]*(r-5) if r>5 else [2]*(5-r)
walk(seq)
print('at', pb(g), 'expect (5,4)')
f = act(4); g = grid_of(f)   # bump-mark box (5,5)
f = act(5); g = grid_of(f)   # pick
walk([1,1,4,4,4])            # to (3,7), box at (3,8)
f = act(5); g = grid_of(f)   # drop
print('after drop:', summary(g, f))
f = act(3); g = grid_of(f)   # STEP AWAY west
print('stepped away:', summary(g, f))
prev = None
for i in range(1, 26):
    f = act(5); g2 = grid_of(f)
    if g2 is None:
        print(f'idle{i}: EMPTY state={f.state} score={f.levels_completed}'); continue
    s = summary(g2, f)
    if s != prev: print(f'idle{i}: {s} state={f.state}')
    prev = s; g = g2
    if str(f.state) != 'GameState.NOT_FINISHED':
        print('TERMINAL', f.state); break
# C) idle to timer exhaustion to observe terminal behaviour
for i in range(26, 90):
    f = act(5); g2 = grid_of(f)
    t = int((g2[63]==7).sum()) if g2 is not None else -1
    if g2 is None or t <= 2 or str(f.state) != 'GameState.NOT_FINISHED':
        print(f'late{i}: timer={t} state={f.state} score={f.levels_completed}')
    g = g2 if g2 is not None else g
    if str(f.state) != 'GameState.NOT_FINISHED':
        print('TERMINAL', f.state, 'score', f.levels_completed)
        break
print('post-terminal frame:')
g2 = grid_of(f)
if g2 is not None:
    print(summary(g2, f))
