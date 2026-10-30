"""bp35 cell-level simulator + BFS solver.
Semantics transcribed from environment_files/bp35/0a0ad940/bp35.py (obfuscated source).
Names: door='qclfkhjnaac'(x), wall='xcjjwqfzjfe'(o), spike='ubhhgljbnpu'(v)/'hzusueifitk',
gem='fjlzdjxhant'(+), toggle_solid='yuuqpmlxorv'(1), toggle_open='oonshderxef'(2),
flood_row='aknlbboysnc'(m), flood_body='jcyhkseuorf'(w), spread='etlsaqqtjvn'(digit? per legend),
gravity_button='lrpkmzabbfa'.
Cell coords: row 0 = TOP of world. Balloon rises toward smaller row. Player fixed col slot=cell.
ASSUMPTION (verified against source): grids listed bottom-up in file then [::-1] applied,
so reversed list index = world row (0 = last written line = top padding).
"""
import re, json, sys
from collections import deque
from pathlib import Path

SRC = (Path(__file__).resolve().parents[3] / 'environment_files/bp35/0a0ad940/bp35.py').read_text()

WALL='o'; DOOR='x'; SPIKE='v'; GEM='+'; PLAYER='n'; TSOLID='1'; TOPEN='2'; FLOODM='m'; FLOODW='w'
NAME2CH = {
 'qclfkhjnaac':'x', 'xcjjwqfzjfe':'o', 'ubhhgljbnpu':'v', 'hzusueifitk':'v',
 'fjlzdjxhant':'+', 'player_right':'n', 'yuuqpmlxorv':'1', 'oonshderxef':'2',
 'aknlbboysnc':'m', 'jcyhkseuorf':'w', 'etlsaqqtjvn':'s', 'lrpkmzabbfa':'g',
}

def parse_grids():
    grids = {}
    for m in re.finditer(r'"(grid\d+)": qipeamczaw\(\s*\[(.*?)\]\[::-1\],\s*\{(.*?)\},', SRC, re.S):
        name = m.group(1)
        rows = re.findall(r'"([^"]*)"', m.group(2))
        legend_txt = m.group(3)
        legend = {}
        for lm in re.finditer(r'"(.)":\s*\[\s*"([a-z_]+)"\s*\]', legend_txt):
            legend[lm.group(1)] = NAME2CH.get(lm.group(2), '?')
        rows = rows[::-1]  # world row 0 = top
        grids[name] = (rows, legend)
    return grids

class Level:
    def __init__(self, rows, legend):
        self.h = len(rows); self.w = len(rows[0])
        self.cells = {}
        self.player = None
        self.gem = None
        self.flood_m = None
        for r, line in enumerate(rows):
            for c, ch in enumerate(line):
                if ch == ' ':
                    continue
                t = legend.get(ch, '?')
                if t == 'n':
                    self.player = (c, r); continue
                if t == 'm' and self.flood_m is None:
                    self.flood_m = r
                self.cells[(c, r)] = t
        assert self.player and '?' not in self.cells.values(), set(self.cells.values())

def passable(t):
    return t is None or t in ('2', 'm')  # empty, toggle-open, flood-row(passable per source)

def cell_at(level, st, pos):
    """Effective cell type under state st = (doors_removed, toggles_flipped, spreads_added)."""
    doors, flips, spreads = st
    if pos in spreads:
        return 's'
    t = level.cells.get(pos)
    if t == 'x' and pos in doors:
        return None
    if t in ('1', '2') and pos in flips:
        return '2' if t == '1' else '1'
    return t

def rise(level, st, pos):
    """fsvnqdbzrp from cell pos: returns (count, final_pos, gem, spike). dy=-1 (up)."""
    count = 0
    last = pos
    cur = (pos[0], pos[1] - 1)
    while passable(cell_at(level, st, cur)) and cur[1] >= 0:
        last = cur
        cur = (cur[0], cur[1] - 1)
        count += 1
    t = cell_at(level, st, cur) if cur[1] >= 0 else 'o'
    if t == '+':
        return (count + 1, cur, True, False)
    if t == 'v':
        return (count + 1, last, False, True)
    return (count, last, False, False)

def solve(level, max_actions=70, flood=False):
    """BFS: state = (player, frozen doors, frozen flips, frozen spreads, moves_flood_ticks).
    Actions: ('L',), ('R',), ('C', cx, cy). Click allowed only if target cell currently
    interactive AND on-screen relative to player row: -5 <= cy - py <= 4 (measured safe band;
    the one failed click was at cy = py - 6). Returns list of (action, meta) or None."""
    start = (level.player, frozenset(), frozenset(), frozenset())
    # flood state: levels 1-3; m-row rises 1 cell per 2 flood-advancing actions.
    # We track (m_row, parity). Kill when player row == m_row on a flood-advancing action.
    init = (start[0], start[1], start[2], start[3], level.flood_m if flood else -1, 0)
    prev = {init: None}
    q = deque([init])
    interactive = [p for p, t in level.cells.items() if t in ('x', '1', '2', 'g', 's')]
    while q:
        cur = q.popleft()
        (px, py), doors, flips, spreads, mrow, par = cur
        st = (doors, flips, spreads)
        succs = []
        # lateral moves
        for dx, act in ((-1, 'L'), (1, 'R')):
            tx = px + dx
            tpos = (tx, py)
            t = cell_at(level, st, tpos) if 0 <= tx < level.w else 'o'
            nm, npar = mrow, par
            if t == '+':
                succs.append((act, tpos, doors, flips, spreads, nm, npar, 'WIN')); continue
            if passable(t):
                cnt, fin, gem, spike = rise(level, st, tpos)
                if gem:
                    succs.append((act, fin, doors, flips, spreads, nm, npar, 'WIN')); continue
                if spike:
                    continue  # death
                if cnt == 0 and mrow >= 0:
                    npar = par + 1
                    if npar % 2 == 0:
                        nm = mrow - 1
                        if fin[1] >= nm:  # caught (player row == m row)
                            continue
                succs.append((act, fin, doors, flips, spreads, nm, npar, None))
            else:
                # bump
                nm, npar = mrow, par
                if mrow >= 0:
                    npar = par + 1
                    if npar % 2 == 0:
                        nm = mrow - 1
                        if py >= nm:
                            continue
                succs.append((act, (px, py), doors, flips, spreads, nm, npar, None))
        # clicks
        for (cx, cy) in interactive:
            if not (-5 <= cy - py <= 4):
                continue  # off safe screen band
            t = cell_at(level, st, (cx, cy))
            if t not in ('x', '1', '2', 'g', 's'):
                continue
            nd, nf, ns = doors, flips, spreads
            if t == 'x':
                nd = doors | {(cx, cy)}
            elif t in ('1', '2'):
                base = level.cells.get((cx, cy))
                if (cx, cy) in flips:
                    nf = flips - {(cx, cy)}
                else:
                    nf = flips | {(cx, cy)}
            elif t == 's':
                add = set()
                for ddx, ddy in ((-1,0),(1,0),(0,-1),(0,1)):
                    np_ = (cx+ddx, cy+ddy)
                    if 0 <= np_[0] < level.w and 0 <= np_[1] < level.h and cell_at(level, st, np_) is None:
                        add.add(np_)
                ns = spreads | add
            st2 = (nd, nf, ns)
            npos = (px, py); outcome = None
            if (cx, cy) == (px, py - 1):
                cnt, fin, gem, spike = rise(level, st2, (px, py - 1))
                if spike:
                    continue
                npos = fin
                if gem:
                    outcome = 'WIN'
            succs.append((('C', cx, cy), npos, nd, nf, ns, mrow, par, outcome))
        for entry in succs:
            act, npos, nd, nf, ns, nm, npar, outcome = entry
            key = (npos, nd, nf, ns, nm, npar)
            if key in prev:
                continue
            prev[key] = (cur, act)
            if outcome == 'WIN':
                # reconstruct
                path = [act]
                k = cur
                while prev[k] is not None:
                    k, a = prev[k]
                    path.append(a)
                return path[::-1]
            q.append(key)
    return None

def to_pixels(level, path):
    """Convert cell actions to ARC actions with screen coords.
    Player cell -> screen: player cell renders at rows 36-41; camera_y = py*6 - 36.
    Cell (cx, cy) centre pixel on screen: x = cx*6 + 3, y = (cy - py)*6 + 36 + 3.
    Track player position by resimulating."""
    st = (frozenset(), frozenset(), frozenset())
    pos = level.player
    out = []
    doors, flips, spreads = set(), set(), set()
    for act in path:
        if act in ('L', 'R'):
            out.append({'action': 3 if act == 'L' else 4})
            dx = -1 if act == 'L' else 1
            tpos = (pos[0] + dx, pos[1])
            t = cell_at(level, (frozenset(doors), frozenset(flips), frozenset(spreads)), tpos)
            if t == '+':
                pos = tpos
            elif passable(t):
                cnt, fin, gem, spike = rise(level, (frozenset(doors), frozenset(flips), frozenset(spreads)), tpos)
                pos = fin
        else:
            _, cx, cy = act
            x = cx * 6 + 3
            y = (cy - pos[1]) * 6 + 39
            assert 0 <= x <= 63 and 0 <= y <= 63, (x, y, act, pos)
            out.append({'action': 6, 'x': x, 'y': y})
            stf = (frozenset(doors), frozenset(flips), frozenset(spreads))
            t = cell_at(level, stf, (cx, cy))
            if t == 'x':
                doors.add((cx, cy))
            elif t in ('1', '2'):
                if (cx, cy) in flips: flips.discard((cx, cy))
                else: flips.add((cx, cy))
            elif t == 's':
                for ddx, ddy in ((-1,0),(1,0),(0,-1),(0,1)):
                    np_ = (cx+ddx, cy+ddy)
                    if cell_at(level, stf, np_) is None and 0 <= np_[0] < level.w:
                        spreads.add(np_)
            if (cx, cy) == (pos[0], pos[1] - 1):
                stf = (frozenset(doors), frozenset(flips), frozenset(spreads))
                cnt, fin, gem, spike = rise(level, stf, (cx, cy))
                pos = fin
    return out

if __name__ == '__main__':
    grids = parse_grids()
    print('grids:', {k: (len(v[0]), sorted(set(''.join(v[0])))) for k, v in grids.items()})
    results = {}
    for i in range(1, 10):
        g = grids.get(f'grid{i}')
        if not g:
            continue
        lv = Level(*g)
        flood = i <= 3
        path = solve(lv, flood=flood)
        if path is None:
            print(f'level {i}: NO SOLUTION found')
            continue
        pix = to_pixels(lv, path)
        results[i] = {'cells': [list(a) if isinstance(a, tuple) else a for a in path], 'pixels': pix,
                      'n_actions': len(path)}
        print(f'level {i}: {len(path)} actions: {path}')
    json.dump(results, open('/tmp/fap_ext/bp35/solutions.json', 'w'), indent=1)
