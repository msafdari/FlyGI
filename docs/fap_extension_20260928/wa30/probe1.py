exec(open('/tmp/fap_ext/wa30/drive.py').read())

# Fresh episode: does the first action change the frame? Map each action from a fresh reset.
f0 = act(0)  # RESET to get a clean start
g0 = grid_of(f0)
print('after RESET:', state(f0))

for aid in (1,2,3,4,5):
    fr = act(0)
    gbase = grid_of(fr)
    f1 = act(aid)
    g1 = grid_of(f1)
    print(f'action {aid} (first post-reset): {diff(gbase, g1)}  state={state(f1)}')
    # second same action
    f2 = act(aid)
    g2 = grid_of(f2)
    print(f'action {aid} (second):          {diff(g1, g2)}  state={state(f2)}')
