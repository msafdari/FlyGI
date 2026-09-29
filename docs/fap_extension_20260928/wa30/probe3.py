exec(open('/tmp/fap_ext/wa30/drive.py').read())

f = act(0)
g = grid_of(f)
# Reproduce: up, up -> adjacent to box, border now 3
for aid in (1,1):
    f = act(aid); g2 = grid_of(f)
    print(f'a{aid}: {diff(g,g2)}'); g = g2

# Now interact
f = act(5); g2 = grid_of(f)
print(f'a5: {diff(g,g2)} score={f.levels_completed}'); g = g2
show(g, 24, 44)

# Try moving up again (into box)
f = act(1); g2 = grid_of(f)
print(f'a1 into box: {diff(g,g2)} score={f.levels_completed}'); g = g2
show(g, 24, 48)

# Try moving left then up (go around)
for aid in (3,):
    f = act(aid); g2 = grid_of(f)
    print(f'a{aid}: {diff(g,g2)} score={f.levels_completed}'); g = g2
show(g, 24, 48)
