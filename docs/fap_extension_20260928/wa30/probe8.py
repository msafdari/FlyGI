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

for i in range(20):
    f = act(5); g2 = grid_of(f)
    ch = diff(g,g2)
    g = g2
    if i % 2 == 1 or 'NOCHANGE' in ch:
        print(f'idle {i}: {ch}')
        print('   ', [b for b in blocks(g) if b[0][0] not in (15,) and (12 in b[1] or 5 in b[1] or 3 in b[1])], 'timer', int((g[63]==7).sum()), 'score', f.levels_completed)
