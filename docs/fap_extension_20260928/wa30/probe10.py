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

L2 = ([3] + [2]*10 + [4]*9 + [1,5] + [3]*8 + [1,5]
      + [4]*11 + [1]*4 + [3,5] + [2]*3 + [3]*8 + [5])
for i,aid in enumerate(L2, start=1):
    f = act(aid)
    g2 = grid_of(f)
    if g2 is None:
        print(f'a{i} act{aid}: EMPTY state={f.state} score={f.levels_completed}')
        continue
    interesting = [b for b in blocks(g2) if any(v in b[1] for v in (0,14,12,5,3))]
    print(f'a{i} act{aid}: score={f.levels_completed} {f.state} timer={int((g2[63]==7).sum())} {interesting}')
    g = g2
    if f.levels_completed > 1:
        print('LEVEL 2 FELL at action', i)
        break
print()
print('final blocks:', blocks(g))
