exec(open('/tmp/fap_ext/wa30/drive.py').read())
import collections

def objects(gr):
    # summarize: player block (colour 14/0), boxes (4/9), dock (9-border,2), timer row
    out = {}
    for col,name in ((14,'player_e'),(0,'player_0'),(4,'box4'),(9,'nine'),(2,'two'),(7,'timer7')):
        pos = np.argwhere(gr==col)
        if len(pos):
            out[name] = (int(pos[:,0].min()), int(pos[:,0].max()), int(pos[:,1].min()), int(pos[:,1].max()), len(pos))
    return out

f = act(0)
g0 = grid_of(f)
print('start objects:', objects(g0))

# move up 5 times, print object summary each time
seq = [1,1,1,1,1]
g_prev = g0
for i,aid in enumerate(seq):
    f = act(aid)
    g1 = grid_of(f)
    print(f'step {i} action {aid}: {diff(g_prev,g1)} score={f.levels_completed} state={f.state}')
    print('  objects:', objects(g1))
    g_prev = g1
print()
show(g_prev, 20, 64)
