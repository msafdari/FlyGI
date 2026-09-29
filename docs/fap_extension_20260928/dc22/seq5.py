import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session import *

CARD8 = {'x': 48, 'y': 19}
CARD9 = {'x': 48, 'y': 36}

# 1) inspect all grids inside one step's frame (animation?)
fr = act(0)
fr = act(6, CARD8)
raw = fr.frame
print('frames in card8 step:', len(raw) if raw is not None else None)

# 2) for each config, idle until GAME_OVER; check score at the end
configs = {
    'stack {9,8,d}': [CARD8],
    'stack {8,d}': [CARD9, CARD8],
    'stack {9,d}': [],
    'stack {d}': [CARD9],
}
for name, seq in configs.items():
    fr = act(0)
    for p in seq:
        fr = act(6, p)
    n = len(seq)
    last_score = fr.levels_completed
    while n < 140 and str(fr.state) == 'GameState.NOT_FINISHED':
        fr = act(1 if n % 2 else 2)
        n += 1
        if fr.levels_completed != last_score:
            print(f'{name}: SCORE CHANGED at action {n}: {fr.levels_completed}')
            last_score = fr.levels_completed
    print(f'{name}: after {n} actions state={fr.state} score={fr.levels_completed}')
