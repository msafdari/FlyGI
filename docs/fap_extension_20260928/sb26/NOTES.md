# sb26 ("recursive sequence builder") — SOLVED, all 8 levels, GameState.WIN

Verified end-to-end: /tmp/fap_ext/sb26/p_full.json (124 steps) replayed from scratch ->
score 0->8, final_state GameState.WIN (run_final/). Deterministic offline arcade, seed via
derived_run_seeds(0, game_id); game_id sb26-7fbdac44.

## Mechanics (all MEASURED unless noted)
- available_actions always [5,6,7]. Only 6 (click) and 5 (interact=SUBMIT) needed. 7 never used.
- First post-reset action is NOT swallowed (run1: very first click drew a selection border). --wake 0.
- Screen: legend band rows 0-7 (colour-5 band, hollow 6x6 squares = target sequence, read left->right);
  play area rows ~12-47 with outlined boxes; timer row 53 (64 cells colour 2); button tray rows 57-60.
- Click a tray button -> selected (0-coloured border, free). Click a slot (2x2 colour-2 mark) -> places
  the selected tile as 4x4, consumes the button (leaves 2x2 remnant), costs 1 timer tick (row 53
  rightmost 2->3). Clicks on background / slot with no selection: no-op, no tick (run3 steps 5-6).
  Wrong submit (action 5): rejected silently, costs 1 tick (run12 step 122). Correct submit: level falls.
- Timer: 64 ticks per level, fresh at each level start (measured at levels 2..8 starts). Budget never
  stressed: worst level uses 9 ticks incl. submit. GAME_OVER never reached; RESET never needed
  (RESET-restores-level-start is from the brief, not exercised here).
- Solid 4x4 tray button = colour literal. Hollow 4x4 tray button = REFERENCE to the box outlined in
  that colour. Boxes may come pre-filled with literals or references. Root box = the one whose four
  corners carry colour-0 L-marks (all levels).

## The rule (measured across 8 levels)
Legend sequence = FLATTEN(root box), where flatten walks the box's elements left-to-right:
literal -> its colour; reference -> flatten(referenced box); a reference back to a box already on the
expansion stack contributes NOTHING (cycle-cut) but its slot must still be filled (level 8: identical
board with that slot empty was rejected; with hollow-8 placed it WON). Every slot filled and every
button used exactly once in all 8 levels. Fill slots to make flatten(root)=legend, press 5.

## Levels (all verified, score transition observed in my own runs)
1. legend 9,e,b,f; one box [4 slots] -> fill 9,e,b,f; submit. 0->1 (run5)
2. legend c,f,8,9,e,b,6; root 8-box [_,_,refE,_] prefilled, e-box 4 slots -> root [c,f,.,6], e-box [8,9,e,b]. 1->2 (run6)
3. legend 8,e,f,b,6,9,c; root [_,refE,_,ref9,_] prefilled; e-box 2 slots, 9-box 2 slots -> root [8,.,b,.,c], e=[e,f], 9=[6,9]. 2->3 (run7)
4. legend b,8,e,9,6,c,f; root 5 empty slots; e-box [e(prefilled),_,_]; tray has hollow-e -> root [b,8,refE,c,f], e=[e,9,6]. 3->4 (run8)
5. legend 6,e,8,8,e,8,8,b,f (9 entries); root 5 slots; 9-box 3 slots; TWO hollow-9 buttons ->
   root [6,ref9,ref9,b,f], 9=[e,8,8] (repeated expansion). 4->5 (run9)
6. legend 9,b,b,c,f,f,e,6,6; root 8-box 3 slots; e/9/c boxes each [own colour prefilled,_,_] ->
   root [ref9,refC,refE], 9=[9,b,b], c=[c,f,f], e=[e,6,6]. 5->6 (run10)
7. legend 8,9,e,b,e,9,8 (palindrome); stacked boxes; e-box [_,b,_] -> depth-2 nesting:
   root [8,ref9,8], 9=[9,refE,9], e=[e,b,e]. 6->7 (run11)
8. legend 8,b,c,9,e,f; root 8-box 4 slots, 9-box 4 slots, hollow-8 AND hollow-9 in tray ->
   root [8,b,c,ref9], 9-box [9,e,f,ref8]; ref8 is a back-edge, expands to nothing. 7->8 WIN (run_final)
   (Same fill with 9-box slot4 EMPTY and hollow-8 unused: rejected — run12.)

## Files
- p_full.json          verified 124-step full-game program
- p1..p12.json         incremental probe programs
- run*/                frame dumps per run (text renders + per-step state)
- parse.py             structural frame parser used for levels 5-8
- drive8.py            interactive candidate tester for level 8 (cand1 won immediately)
- level8_winner.json   winning level-8 decomposition
