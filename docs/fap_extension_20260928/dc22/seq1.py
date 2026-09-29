import sys
sys.path.insert(0, '/tmp/fap_ext/dc22')
from session import *

fr = env.observation_space
print('init          ', json.dumps(brief(grid_of(fr), fr)))

CARD8 = {'x': 48, 'y': 19}
CARD9 = {'x': 48, 'y': 36}

seqs = {
  '8,8': [CARD8, CARD8],
  '8,9': [CARD8, CARD9],
  '9,9': [CARD9, CARD9],
  '9,8': [CARD9, CARD8],
  '8,9,8,9': [CARD8, CARD9, CARD8, CARD9],
}
for name, seq in seqs.items():
    fr = act(0)
    for i, p in enumerate(seq):
        fr = act(6, p)
        print(f'{name} step{i+1}   ', json.dumps(brief(grid_of(fr), fr)))
