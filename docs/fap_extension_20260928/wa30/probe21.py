exec(open('/tmp/fap_ext/wa30/drive.py').read())
import json

def pb(gr):
    e = np.argwhere(gr==14)
    return (int(e[:,0].min()//4), int(e[:,1].min()//4)) if len(e) else None

# 1) swallow test: fresh env -> RESET -> single move
f = act(0)
g = grid_of(f)
print('post-RESET player:', pb(g), 'score', f.levels_completed)
f = act(1); g2 = grid_of(f)
print('after first a1:', pb(g2), '(moved =', pb(g2) != pb(g), ') diff:', diff(g, g2))
f = act(1); g3 = grid_of(f)
print('after second a1:', pb(g3), 'diff:', diff(g2, g3))

# 2) RESET mid-level-2: replay L1 (score 1), take 5 L2 actions, then RESET
prog = json.load(open('/tmp/fap_ext/wa30/prog_l1.json'))
f = act(0)
for st in prog: f = act(st['action'])
print('after L1 replay: score', f.levels_completed, f.state)
for a in [3,2,2,2,2]: f = act(a)
g = grid_of(f)
print('mid-L2: score', f.levels_completed, 'player', pb(g), 'timer', int((g[63]==7).sum()))
f = act(0)
g2 = grid_of(f)
print('after RESET: score', f.levels_completed, 'player', pb(g2), 'timer', int((g2[63]==7).sum()), 'state', f.state)
