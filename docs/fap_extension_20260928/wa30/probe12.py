exec(open('/tmp/fap_ext/wa30/drive.py').read())
import json
prog = json.load(open('/tmp/fap_ext/wa30/prog_l1_l2.json'))
f = env.observation_space
for st in prog: f = act(st['action'])
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

def pb(gr):
    e = np.argwhere(gr==14)
    if len(e)==0: return None
    return (int((e[:,0].min())//4), int(e[:,1].min()//4))

# player starts L3 at block (9,4). Step 1: approach wall: R3 -> (9,7), then bump R into wall (9,8).
seq1 = [4,4,4, 4, 4]   # last two are wall bumps
for i,aid in enumerate(seq1):
    f = act(aid); g2 = grid_of(f)
    print(f'{i}: a{aid} {diff(g,g2)} player={pb(g2)} timer={int((g2[63]==7).sum())}')
    g = g2
# rival will have grabbed plug (3,8) ~a4 and be carrying east. Wait for it to take (8,8) (its 2nd target ~a21).
for i in range(18):
    f = act(5); g2 = grid_of(f); g = g2
bl = blocks(g)
print('after waits: rival/plug state:', [b for b in bl if any(v in b[1] for v in (12,5))], 'gap83:', [b for b in bl if b[0]==(3,8)], 'gap88:', [b for b in bl if b[0]==(8,8)])
# now try stepping up to (8,7) and bump east into regrown (8,8)
for aid in [1, 4, 4]:
    f = act(aid); g2 = grid_of(f)
    print(f'a{aid}: {diff(g,g2)} player={pb(g2)}')
    g = g2
print('gap88 now:', [b for b in blocks(g) if b[0] in ((8,8),(8,9))])
