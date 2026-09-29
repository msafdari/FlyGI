"""Clean end-to-end verification: RESET, auto-play L1-4 via FapExecutor
(logging its emitted steps per level), then the derived L5 (21 clicks) and
L6 (13 clicks) programs. Expect score 0->6 and GameState.WIN. Writes
programs.json with per-level step lists and observed transitions.
"""
import sys, json
sys.path.insert(0, '/tmp/fap_ext/ft09')
from drive import Session, render_grid, OUT
from flygi.controller.fap_library import FapExecutor
import numpy as np

R5 = [4, 12, 20, 28, 36, 44, 52]; C5 = [6, 14, 22, 30, 38, 46, 54]
R6 = [6, 14, 22, 30, 38, 46]; C6 = [4, 12, 20, 28, 36, 44, 52]

L5 = [(1,2),(3,2),(5,4),(0,2),(1,1),(1,3),(3,1),(3,3),(4,4),(5,3),(5,5),(6,4),
      (0,3),(2,1),(2,3),(2,5),(4,1),(4,3),(4,5),(6,1),(6,3)]
L6 = [(0,0),(1,0),(2,1),(3,1),(1,2),(2,2),(4,2),(3,3),(1,4),(3,4),(3,5),(4,5),(4,6)]

s = Session()
s.act(0)  # RESET starts the episode
per_level = {}   # level (1-based target) -> list of steps
transitions = []

ex = FapExecutor()
level = 0
steps_this = []
while s.frame.levels_completed < 4:
    g = s.grid()
    ex.observe(g)
    st = ex.propose(g)
    assert st is not None, 'executor abstained during L1-4'
    before = s.frame.levels_completed
    if st.action == 6:
        s.act(6, {'x': st.x, 'y': st.y})
        steps_this.append({'action': 6, 'x': st.x, 'y': st.y})
    else:
        s.act(st.action)
        steps_this.append({'action': st.action})
    after = s.frame.levels_completed
    if after > before:
        transitions.append((before, after, len(s.actions_taken)))
        per_level[after] = steps_this
        steps_this = []
        ex.notify_level_advance()

# Level 5
steps_this = []
for (i, j) in L5:
    x, y = C5[j] + 3, R5[i] + 3
    before = s.frame.levels_completed
    s.act(6, {'x': x, 'y': y})
    steps_this.append({'action': 6, 'x': x, 'y': y})
    if s.frame.levels_completed > before:
        transitions.append((before, s.frame.levels_completed, len(s.actions_taken)))
per_level[5] = steps_this
assert s.frame.levels_completed == 5, s.status()

# Level 6
steps_this = []
for (i, j) in L6:
    x, y = C6[j] + 3, R6[i] + 3
    before = s.frame.levels_completed
    s.act(6, {'x': x, 'y': y})
    steps_this.append({'action': 6, 'x': x, 'y': y})
    if s.frame.levels_completed > before:
        transitions.append((before, s.frame.levels_completed, len(s.actions_taken)))
per_level[6] = steps_this

print('FINAL', s.status(), 'total actions', len(s.actions_taken))
print('transitions (score_before, score_after, at_action):', transitions)
out = {
    'game': 'ft09', 'seed_index': 0,
    'final_state': s.status(), 'total_actions': len(s.actions_taken),
    'score_transitions': transitions,
    'programs': {str(k): v for k, v in sorted(per_level.items())},
    'note': 'L1-4 steps are FapExecutor-derived (glyph_miniature); '
            'L5/L6 steps are the hand-derived two-sided flip-mask programs. '
            'Initial action 0 (RESET) precedes level 1.',
}
(OUT / 'programs.json').write_text(json.dumps(out, indent=1))
print('wrote programs.json; per-level click counts:',
      {k: len(v) for k, v in sorted(per_level.items())})
