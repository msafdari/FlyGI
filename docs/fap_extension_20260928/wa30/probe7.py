exec(open('/tmp/fap_ext/wa30/drive.py').read())

# Match premise harness: NO initial reset. Run L1 program, then inspect L2 start,
# then take single moves and watch the c mover.
L1 = [1,1,5,1,3,1,5,3,3,3,1,5,2,4,4,4,4,1,5,4,4,4,1,5,2,3,3,5]
f = env.observation_space
for aid in L1:
    f = act(aid)
print('after L1: score', f.levels_completed, f.state)
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

print('L2 start blocks:', blocks(g))
print('timer7:', int((g[63]==7).sum()))

# watch mover for 6 idle-ish actions (use 5 = no-op interact away from boxes? player next to nothing)
for i in range(6):
    f = act(5); g2 = grid_of(f)
    print(f'idle a5 #{i}: {diff(g,g2)}')
    g = g2
print('blocks now:', blocks(g))
print('timer7:', int((g[63]==7).sum()))
