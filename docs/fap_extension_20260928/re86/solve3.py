import itertools
dots = [(6,6),(6,45),(15,51),(21,21),(27,9),(30,48),(33,33),(39,21)]
LAT = [(r, c) for r in range(0, 64, 3) for c in range(0, 64, 3)]

def covered_line(t):
    r0, c0 = t
    return frozenset(d for d in dots if d[0] == r0 and abs(d[1]-c0) <= 21)

def covered_X(t):
    r0, c0 = t
    return frozenset(d for d in dots if abs(d[0]-r0) == abs(d[1]-c0) and 1 <= abs(d[0]-r0) <= 11)

def covered_diamond(t):
    r0, c0 = t
    return frozenset(d for d in dots if abs(d[0]-r0) + abs(d[1]-c0) == 12)

alldots = frozenset(dots)
line_opts = {}
x_opts = {}
dia_opts = {}
for t in LAT:
    for opts, fn in ((line_opts, covered_line), (x_opts, covered_X), (dia_opts, covered_diamond)):
        s = fn(t)
        if s:
            opts.setdefault(s, []).append(t)

sols = []
for sl, tl in line_opts.items():
    for sx, tx in x_opts.items():
        if sl & sx: continue
        for sd, td in dia_opts.items():
            if (sl | sx) & sd: continue
            if sl | sx | sd == alldots:
                sols.append((sorted(sl), tl, sorted(sx), tx, sorted(sd), td))
print("solutions:", len(sols))
for s in sols[:12]:
    print(" line dots", s[0], "targets", s[1])
    print("   X dots", s[2], "targets", s[3])
    print("   dia dots", s[4], "targets", s[5])
