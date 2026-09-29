exec(open('/tmp/fap_ext/wa30/drive.py').read())

L1 = [1,1,5,1,3,1,5,3,3,3,1,5,2,4,4,4,4,1,5,4,4,4,1,5,2,3,3,5]
f = act(0)
for aid in L1:
    f = act(aid)
print('after L1 program: score', f.levels_completed, f.state)
g = grid_of(f)

chunks = {
 'D1': [4]*8 + [2]*5 + [3,5] + [3]*5 + [5],
 'D2': [4]*8 + [2,5] + [3]*8 + [5],
 'D3': [2]*3 + [4]*6 + [5] + [3]*7 + [1,5],
 'D4': [4] + [1]*5 + [4]*4 + [5] + [3]*8 + [2,2,4,5],
 'D5': [1] + [4]*9 + [5] + [3]*10 + [2,2,4,5],
 'D6': [2,2] + [4]*4 + [5,2] + [3]*3 + [1,5],
}

def pstate(gr):
    e = np.argwhere(gr==14)
    if len(e)==0: return 'no-player'
    r0,c0 = e[:,0].min(), e[:,1].min()
    return f'player block ({int((r0-1)//4)},{int(c0//4)})'

for name, seq in chunks.items():
    for aid in seq:
        f = act(aid)
    g = grid_of(f)
    print(f'{name}: score={f.levels_completed} state={f.state} {pstate(g)} timer7={int((g[63]==7).sum())}')
    if f.levels_completed > 1:
        print('LEVEL 2 FELL at chunk', name)
        break

show(g, 0, 64)
