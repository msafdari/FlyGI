exec(open('/tmp/fap_ext/wa30/drive.py').read())
L1 = [1,1,5,1,3,1,5,3,3,3,1,5,2,4,4,4,4,1,5,4,4,4,1,5,2,3,3,5]
f = env.observation_space
for aid in L1: f = act(aid)
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

prev_blocks = None
for i in range(80):
    f = act(5)
    g2 = grid_of(f)
    if g2 is None:
        print(f'action {i+1}: EMPTY FRAME state={f.state} score={f.levels_completed}')
        g = None
        continue
    bl = [b for b in blocks(g2) if 12 in b[1] or 5 in b[1] or 3 in b[1]]
    tk = int((g2[63]==7).sum()) if g2 is not None else -1
    if bl != prev_blocks or str(f.state) != 'GameState.NOT_FINISHED':
        print(f'a{i+1}: state={f.state} score={f.levels_completed} timer={tk} movers={bl}')
        prev_blocks = bl
    g = g2
    if str(f.state) not in ('GameState.NOT_FINISHED',):
        print('TERMINAL at action', i+1)
        break
print()
print('final blocks:', blocks(g) if g is not None else None)
