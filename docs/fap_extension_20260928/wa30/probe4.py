exec(open('/tmp/fap_ext/wa30/drive.py').read())

f = act(0)
g = grid_of(f)
seq = [1,1,5,1,3,1]   # touch box, pick up, up, left, up toward dock
for i,aid in enumerate(seq):
    f = act(aid); g2 = grid_of(f)
    print(f'{i}: a{aid}: {diff(g,g2)} score={f.levels_completed} state={f.state}'); g = g2
show(g, 20, 48)
print()
# try 5 (drop?) then up
for aid in (5,1,1):
    f = act(aid); g2 = grid_of(f)
    print(f'a{aid}: {diff(g,g2)} score={f.levels_completed} state={f.state}'); g = g2
show(g, 20, 48)
