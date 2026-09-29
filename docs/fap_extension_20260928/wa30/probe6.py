exec(open('/tmp/fap_ext/wa30/drive.py').read())

L1 = [1,1,5,1,3,1,5,3,3,3,1,5,2,4,4,4,4,1,5,4,4,4,1,5,2,3,3,5]
f = act(0)
for aid in L1:
    f = act(aid)
g = grid_of(f)

def blocks(gr):
    # map every 4x4-aligned object by sampling block grid
    out = []
    for br in range(16):
        for bc in range(16):
            v = gr[br*4:(br+1)*4, bc*4:(bc+1)*4]
            vals = set(int(x) for x in np.unique(v))
            if vals != {1} and br < 15:
                out.append(((br,bc), sorted(vals)))
    return out

D1 = [4]*8 + [2]*5 + [3,5] + [3]*5 + [5]
names = 'R R R R R R R R D D D D D L 5 L L L L L 5'.split()
for i,aid in enumerate(D1):
    f = act(aid); g2 = grid_of(f)
    d = diff(g,g2)
    e = np.argwhere(g2==14); r0,c0 = int(e[:,0].min()), int(e[:,1].min())
    print(f'{i:2d} {names[i]}: {d}   player rows{r0-1}-{r0+2} cols{c0}-{c0+3}  timer={int((g2[63]==7).sum())}')
    g = g2
print()
for b in blocks(g): print(b)
