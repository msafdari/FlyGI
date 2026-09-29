exec(open('/tmp/fap_ext/wa30/drive.py').read())
import json
prog = json.load(open('/tmp/fap_ext/wa30/prog_l1_l2.json'))
f = env.observation_space
for st in prog: f = act(st['action'])
print('reached L3: score', f.levels_completed)
g = grid_of(f)

def blocks(gr):
    out = []
    for br in range(16):
        for bc in range(16):
            if br == 15: continue
            v = gr[br*4:(br+1)*4, bc*4:(bc+1)*4]
            vals = set(int(x) for x in np.unique(v))
            if vals != {1}:
                out.append(((br,bc), sorted(vals)))
    return out

prev = None
for i in range(1, 90):
    f = act(5)
    g2 = grid_of(f)
    if g2 is None:
        print(f'a{i}: EMPTY state={f.state} score={f.levels_completed}')
        continue
    bl = [b for b in blocks(g2) if any(v in b[1] for v in (12,5,3,0)) and 14 not in b[1]]
    tk = int((g2[63]==7).sum())
    if bl != prev:
        print(f'a{i}: timer={tk} score={f.levels_completed} {bl}')
        prev = bl
    g = g2
    if str(f.state) != 'GameState.NOT_FINISHED':
        print('TERMINAL', f.state, 'at', i); break
print('final:', blocks(g) if g is not None else None)
