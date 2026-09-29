#!/usr/bin/env python
"""ls20 archetype parser: read a 64x64 frame dump (drive.py render format) and
emit a cell-level description of the maze.

Geometry constants (measured on levels 1-4, seed derived_run_seeds(0, ls20)):
- Maze lattice: 5x5 px cells, rows ≡ 0 (mod 5), cols ≡ 4 (mod 5).
- Colours: 3=floor, 4=wall, 5=chrome/interior, 11(b)=timer+refill rings,
  12(c)+9=key tile (2 rows c, 3 rows 9), 0/1=rotator sprite, 1=conveyor strip,
  {9,14,0,8,12} 3x3 = recolour device, 8=lives blocks (rows 61-62 right).
- Bottom-left box rows 53-62 cols 1-10: carried 3x3 pattern at 2px scale,
  sample px (55,57,59)x(3,5,7); its colour = carried ink colour.
- Goal box: 9x9 block border colour 3, interior 5, 3x3 glyph at centre
  rows +3..+5, cols +3..+5; glyph colour = required ink colour.
"""
import sys, re
import numpy as np

def load(path):
    rows = []
    for line in open(path):
        m = re.match(r'\s*(\d+) ([0-9a-f]{64})$', line)
        if m:
            rows.append([int(ch, 16) for ch in m.group(2)])
    return np.array(rows[:64], dtype=np.int16)

def parse(g):
    out = {}
    # carried pattern from bottom-left display
    pat, colors = [], set()
    for r in (55, 57, 59):
        row = []
        for c in (3, 5, 7):
            v = int(g[r, c])
            row.append(0 if v == 5 else 1)
            if v != 5:
                colors.add(v)
        pat.append(tuple(row))
    out['carried'] = tuple(pat)
    out['carried_color'] = colors.pop() if len(colors) == 1 else sorted(colors)
    out['lives'] = int((g[61, 55:64] == 8).sum() // 2)
    out['timer_cols'] = int((g[61, 13:55] == 11).sum())
    # key tile: 5x5 block, top 2 rows colour 12 over 3 rows colour 9
    key = None
    for R in range(0, 56, 5):
        for C in range(4, 60, 5):
            blk = g[R:R+5, C:C+5]
            if blk.shape == (5, 5) and (blk[0:2] == 12).all() and (blk[2:5] == 9).all():
                key = (R, C)
    out['key'] = key
    # goal box: find 9x9 with 3-border/5-interior and a glyph
    out['goal'] = None
    for R in range(0, 51):
        for C in range(0, 51):
            blk = g[R:R+9, C:C+9]
            border = np.concatenate([blk[0], blk[8], blk[1:8, 0], blk[1:8, 8]])
            if (border == 3).all() and (blk[1, 1:8] == 5).all():
                glyph, gcol = [], set()
                for dr in range(3):
                    row = []
                    for dc in range(3):
                        v = int(blk[3+dr, 3+dc])
                        row.append(0 if v == 5 else 1)
                        if v != 5:
                            gcol.add(v)
                    glyph.append(tuple(row))
                if any(any(r) for r in glyph):
                    out['goal'] = {'box_at': (R, C), 'glyph': tuple(map(tuple, glyph)),
                                   'color': gcol.pop() if len(gcol) == 1 else sorted(gcol)}
    # cells
    cells = {}
    for R in range(0, 56, 5):
        for C in range(4, 60, 5):
            blk = g[R:R+5, C:C+5]
            if blk.shape != (5, 5):
                continue
            vals = set(int(v) for v in blk.ravel())
            cell = None
            if vals == {4}:
                cell = None  # wall
            elif vals <= {3}:
                cell = 'floor'
            elif key == (R, C):
                cell = 'KEY'
            elif 11 in vals and 3 in vals:
                cell = 'ring'
            elif vals >= {9, 14, 8, 12}:
                cell = 'recolor'
            elif 0 in vals and 1 in vals:
                cell = 'rot'
            elif 0 in vals:
                cell = 'rot0?'   # sprite with only colour 0 -- semantics TBD
            elif 1 in vals and 3 in vals:
                cell = 'strip?'  # conveyor strip inside floor cell
            else:
                cell = '?' + ''.join(format(v, 'x') for v in sorted(vals))
            if cell:
                cells[(R, C)] = cell
    # conveyor strips on wall blocks: a full 5-run of colour 1 on a wall edge
    strips = []
    for R in range(0, 56, 5):
        for C in range(4, 60, 5):
            blk = g[R:R+5, C:C+5]
            if blk.shape != (5, 5) or (R, C) in cells:
                continue
            # edges of this wall block; push direction is away from the strip
            if (blk[4] == 1).all():
                strips.append(((R+5, C), 'S'))   # strip on south edge -> affects cell below, pushes S
            if (blk[0] == 1).all():
                strips.append(((R-5, C), 'N'))
            if (blk[:, 4] == 1).all():
                strips.append(((R, C+5), 'E'))
            if (blk[:, 0] == 1).all():
                strips.append(((R, C-5), 'W'))
    out['strips'] = strips
    out['cells'] = cells
    return out

def show(out):
    print('key at', out['key'], ' carried', out['carried'], 'color', out['carried_color'])
    print('goal', out['goal'])
    print('lives', out['lives'], 'timer_cols', out['timer_cols'])
    print('strips (cell, push-dir):', out['strips'])
    Rs = sorted({rc[0] for rc in out['cells']})
    for R in Rs:
        row = []
        for C in range(4, 60, 5):
            v = out['cells'].get((R, C))
            row.append({'floor': '.', 'ring': 'O', 'rot': 'R', 'rot0?': 'r', 'recolor': 'M',
                        'KEY': 'K'}.get(v, '#' if v is None else v) if v else '#')
        print(f'{R:3d} ' + ' '.join(f'{x:>2}' for x in row))
    print('     ' + ' '.join(f'{C:>2}' for C in range(4, 60, 5)))

if __name__ == '__main__':
    out = parse(load(sys.argv[1]))
    show(out)
