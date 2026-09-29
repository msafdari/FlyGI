import sys, re
def load(path):
    rows=[]
    for line in open(path):
        m=re.match(r'^\s*(\d+) ([0-9a-f]{64})$', line)
        if m: rows.append(m.group(2))
    assert len(rows)==64, len(rows)
    return rows
g=load(sys.argv[1])
# legend row 1: entries are 6-wide runs of colour separated by 5
row=g[1]
ents=[]
c0=None; start=None
i=0
while i<64:
    ch=row[i]
    if ch not in '45':
        j=i
        while j<64 and row[j]==ch: j+=1
        ents.append((ch,i,j-1)); i=j
    else: i+=1
print("legend:", ents)
# find boxes: horizontal border runs (>=8 long) of same colour in rows 8..52
for r in range(8,53):
    i=0
    while i<64:
        ch=g[r][i]
        if ch not in '45' and ch!='0':
            j=i
            while j<64 and g[r][j]==ch: j+=1
            if j-i>=8: print(f"border row {r} colour {ch} cols {i}-{j-1}")
            i=j
        else: i+=1
# slots: 2x2 blocks of colour 2 anywhere rows 8..52
seen=set()
for r in range(8,52):
    for c in range(63):
        if g[r][c]=='2' and g[r][c+1]=='2' and g[r+1][c]=='2' and g[r+1][c+1]=='2' and (r-1,c) not in seen and (r,c-1) not in seen and (r-1,c-1) not in seen:
            seen.add((r,c)); print(f"slot mark at row {r} col {c}")
# solid 4x4 blocks (placed/prefilled) rows 8..52
for r in range(8,49):
    for c in range(61):
        ch=g[r][c]
        if ch in '45' or ch=='2' or ch=='0': continue
        ok=all(g[r+dr][c+dc]==ch for dr in range(4) for dc in range(4))
        if ok and (r-1<8 or g[r-1][c]!=ch) and (c-1<0 or g[r][c-1]!=ch):
            print(f"solid 4x4 {ch} at rows {r}-{r+3} cols {c}-{c+3}")
# hollow 4x4 (reference glyphs) rows 8..52: border ch, interior !=ch
for r in range(8,49):
    for c in range(61):
        ch=g[r][c]
        if ch in '4520': continue
        per=all(g[r][c+d]==ch and g[r+3][c+d]==ch for d in range(4)) and all(g[r+d][c]==ch and g[r+d][c+3]==ch for d in range(1,3))
        inner=all(g[r+dr][c+dc]!=ch for dr in (1,2) for dc in (1,2))
        if per and inner and (c==0 or g[r][c-1]!=ch) and g[r+1][c+1] in '45':
            print(f"hollow 4x4 {ch} at rows {r}-{r+3} cols {c}-{c+3}")
# buttons rows 57-60
row=g[58]; brow=g[57]
i=0
print("buttons (row57-60):")
while i<64:
    ch=brow[i]
    if ch not in '45' and ch!='2':
        j=i
        while j<64 and brow[j]==ch: j+=1
        if j-i==4:
            kind = 'solid' if g[58][i+1]==ch else 'hollow'
            print(f"  {ch} cols {i}-{j-1} {kind}")
        i=j
    else: i+=1
# timer row 53
print("timer row53:", g[53].count('2'), "remaining /", g[53].count('3'), "used")
