import numpy as np, sys
gr = np.load(sys.argv[1])
hexd = '0123456789abcdef'
print('    ' + ''.join(str(c%10) for c in range(64)))
for r in range(64):
    print(f'{r:3d} ' + ''.join(hexd[v] if 0<=v<16 else '?' for v in gr[r]))
vals, cnts = np.unique(gr, return_counts=True)
print('census:', dict(zip([hexd[v] for v in vals], cnts.tolist())))
