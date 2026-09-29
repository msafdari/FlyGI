exec(open('/tmp/fap_ext/wa30/drive.py').read())
import json
prog = json.load(open('/tmp/fap_ext/wa30/prog_l1_l2.json'))
f = env.observation_space
for st in prog: f = act(st['action'])
g = grid_of(f)

def blockmap(gr):
    out = {}
    for br in range(16):
        for bc in range(16):
            if br == 15: continue
            v = gr[br*4:(br+1)*4, bc*4:(bc+1)*4]
            vals = frozenset(int(x) for x in np.unique(v))
            if vals != {1}:
                out[(br,bc)] = vals
    return out

recorded = []
state = {'f': f, 'g': g}
def do(aid):
    state['f'] = act(aid)
    state['g'] = grid_of(state['f'])
    recorded.append(aid)
    return state['f']

def socket_free(bc_key):
    bm = blockmap(state['g'])
    vals = bm.get(bc_key, frozenset({1}))
    # free when it is wall speckle (1,2) not a box (4/9 etc.)
    return not any(v in vals for v in (4,9,5,0,3))

def wait_socket(bc_key, maxwait=30):
    n = 0
    while not socket_free(bc_key) and n < maxwait:
        do(5); n += 1
    return n

# Phase A (measured): plant (5,5) into north socket (3,8)
for aid in [1,1,1,1]: do(aid)
wait_socket((3,8))          # north plug must be gone (rival takes it ~a4)
for aid in [4,5,1,1,4,4,4,5]: do(aid)
print('A done: len', len(recorded), 'score', state['f'].levels_completed, 'timer', int((state['g'][63]==7).sum()))

# Phase B: fetch (4,2), plant into south socket (8,8)
for aid in [3,3,3,3,3,3,2,4,5]: do(aid)   # to (3,1), D1 (4,1), bumpE, pick
for aid in [4,4,4,4,4]: do(aid)           # R5: player (4,6), box (4,7)
for aid in [2,2,2,2]: do(aid)             # D4: player (8,6), box (8,7)
wait_socket((8,8))
for aid in [4,5]: do(aid)                 # push into socket, drop
print('B done: len', len(recorded), 'score', state['f'].levels_completed, 'timer', int((state['g'][63]==7).sum()))

# Phase C: fetch (11,3), plant into south socket again
for aid in [3,3,3,3,3]: do(aid)           # L5: (8,2)... player at (8,7)->(8,2)
for aid in [2,2,2]: do(aid)               # D3: (11,2)
for aid in [4,5]: do(aid)                 # bumpE mark, pick
for aid in [4,4,4]: do(aid)               # R3: player (11,6), box (11,7)
for aid in [1,1,1]: do(aid)               # U3: player (8,6), box (8,7)
wait_socket((8,8))
for aid in [4,5]: do(aid)                 # plant
print('C done: len', len(recorded), 'score', state['f'].levels_completed, 'timer', int((state['g'][63]==7).sum()))

# Now idle until rival docks everything or terminal
for i in range(40):
    do(5)
    sc = state['f'].levels_completed
    st_ = str(state['f'].state)
    if sc > 2 or st_ != 'GameState.NOT_FINISHED':
        print('EVENT at idle', i, st_, 'score', sc)
        break
print('final: score', state['f'].levels_completed, state['f'].state, 'actions', len(recorded))
json.dump(recorded, open('/tmp/fap_ext/wa30/l3_recorded.json','w'))
bm = blockmap(state['g']) if state['g'] is not None else {}
print('final blocks:', sorted((k, sorted(v)) for k,v in bm.items()))
