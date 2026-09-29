# su15 (su15-1944f8ab) — mechanics dossier and verified programs

Everything below is MEASURED in the strict-offline arcade, seed 0 (derived_run_seeds(0, game_id)),
unless marked HYPOTHESIS. Coordinates are (row, col) in 64x64; program JSON uses x=col, y=row.

## Verdict
- win_levels = 9. VERIFIED: levels 1-7 fall to the single 97-action program
  `/tmp/fap_ext/su15/program_L1toL7.json` (score 0 -> 7 in one clean run of
  `scripts/fap_program_premise.py`; level boundaries at steps 7, 22, 39, 50, 71, 90, 97).
- Level 8 not completed (~10 choreography attempts); mechanics fully mapped, blocker documented.

## Architecture (matches the dead-game archetype)
- Timer: row 63, 64 colour-0 cells, consumed right-to-left ~3 cells per 2 actions (~42 actions/life).
  Refused clicks cost extra (2-8 cells) but FREEZE the world. RESET refills.
- Header rows 0-9 (colour 4 band): row 1-2 = stage legend as 2x2 chips (grows per level:
  a(10), 6, f(15), b(11), c(12), 8, then 7/e(14)/d(13)); rows 3-6 cols >=30 = GOAL DISPLAY:
  the exact multiset of final shapes to build (3x3 f / 4x4 b / 5x5 c blocks), plus the predator
  zigzag glyph when predators are present.
- First post-reset action is NOT swallowed (measured: first click acts).
- RESET (action 0) mid-level restarts the level (fresh timer, 100% restore — measured).
  QUIRK: RESET issued as the very first action after entering a new level resets the WHOLE GAME.
- Action 7 = UNDO: rewinds the entire world state one action, INCLUDING predator moves and kills.
  Timer is not refunded but undo itself is free => the game is solvable by search-with-rollback.

## Core rule (levels 2+): merge-and-deliver
- Creatures form a size ladder: 1x1 colour10 -> 2x2 colour6 -> 3x3 colour15 -> 4x4 colour11
  -> 5x5 colour12 -> 7x7 colour8. Mass in 1x1-units: 1,2,4,8,16,32 (each merge pairs two).
- CLICK SEMANTICS (measured):
  * If >=2 same-stage creatures are within Euclidean 8.00 of the click, ALL of them are pulled
    to the click and fuse into ONE next-stage creature there (8.00 in, 8.06 out; 3-way merges
    happen — keep unintended third wheels >8.06 from any merge click).
  * Else the single nearest creature within move range relocates to the click (2x2 lands with
    bottom-right at click; odd sizes centre on it; 4x4 spans click-2..click+1).
    Move ranges: 2x2 <=7.9; 3x3 <=9.2; 4x4 <=8.9; 5x5 >=8.06 (7.6 routinely); 7x7 >=11.2.
  * A move landing too close (~<7-8) to another creature is REFUSED (world freezes, timer penalty).
- DELIVERY: build the goal multiset, then move each finished shape onto a 9x9 colour-9 disc;
  overlap (even partial) suffices. Level completes the INSTANT the last goal shape touches its
  disc, and the player's move resolves BEFORE enemy moves (my-move-first preempts kills).
  Wrong discs exist: L6's SE disc did not complete (NW did); L8's 2-row top "sliver" discs do
  not complete. Docked pieces remain vulnerable to predators.

## Predators (colour-7 zigzag, 8 cells in a 4x5 bbox)
- Hunt the nearest stage>=2 creature at ~4 cells/click (occasional dives/pounces up to ~12 when
  far or row/col-aligned); when only 1x1s exist they hunt and EAT those (unit destroyed).
- Contact degrades a creature ONE stage (half its mass is eaten) and flings the remnant ~8-11
  cells away opposite the predator. 7x7 -> 5x5 -> 4x4 chewing is the intended SOURCE of goal
  shapes in L6-L8 (goal glyph shows the predator as the tool).
- Several levels budget spare mass exactly for predator losses (L5: 12 units vs goal 8, two preds).
- Safety numbers: a sitting piece survives a click iff predator centre-gap >= ~8.5
  (4 move + ~4.5 contact radius); a piece that moves every click is safe (my-move-first).

## Level-by-level (all completions observed in-run; program file = the verified splice)
1. Dashed colour-3 diagonal path, 3x3 colour-15 token at bottom (home (58-60,3-5)), colour-9 ring
   with 3x3 colour-3 socket top-right, 0-diamond waypoint on the path. Click successive points
   along the path (hop <= E9.2, on/off path both work). Score ticks when the token reaches the
   ring entrance dash (17,46). 7 clicks.
2. Eight 1x1 colour-10 creatures + filled 9-disc; goal 4x4: pair-merge 4x, 2x2-merge 2x, 3x3-merge,
   dock the 4x4 on the disc. 14 clicks.
3. 6x 1x1 + 3x 2x2; goal = 4x4 AND 3x3, two discs; build both, dock both (completes on 2nd dock).
   17 clicks.
4. Eight 1x1 + ONE predator; goal 4x4 (mass exact, zero losses allowed): assemble the west line
   while the predator crosses; form F3b at the both-within-8 midpoint of the south pair;
   long-range b4 merge (gap 15.3 <= 16 works: both pieces within 8 of one click); dock. 11 clicks.
5. 4x 1x1 + 4x 2x2 + TWO predators; goal 4x4 (4 spare units): let predators eat the two remnant
   1x1s, converge four 2x2s bottom-centre, flee-south F3 merges, b4 north sprint to top disc.
   21 clicks (verified splice includes the undo-cleaned line).
6. No small creatures: one 7x7 colour-8 block + 1 predator + 2 discs; goal = 4x4 (+pred glyph):
   WAIT while the predator chews 7x7 -> 5x5 -> 4x4, steal the 4x4, dock at the NW disc
   (SE disc does not complete). 19 clicks incl. 8 waits.
7. 2 ready 4x4s + 7x7 + THREE predators; goal = TWO 4x4s: predator chews the 7x7 to the 2nd b4
   for free; dock east b4 mid-march, approach NW disc from the east away from the incoming
   predator; completes when the 2nd b4 touches its disc (partial overlap). 7 clicks.
8. UNSOLVED. 2x b4 + 7x7 + THREE predators; goal = TWO 5x5s; discs: bottom-left + bottom-right
   real, two 2-row top slivers are DECOYS (docking there does not complete). Working line:
   merge b4+b4 -> C5a; predator chews 7x7 -> C5b; C5a must cross to BR along rows 54-58 while
   C5b (spawn pre-aggroed by its chewer) docks BL; the two sprints collide in time — each piece
   tolerates <=2-3 stationary clicks and one click moves one piece. Discovered levers: X6 is
   movable (range >=11) to shift chew timing/spawn point; C5 hops up to 8.06 work; undo enables
   search. A solution likely exists (schedule search with rollback); ~10 lines tried, all one to
   two clicks short. Timer forces a level RESET between long attempts.

## Files
- program_L1toL7.json — the verified 97-action program (actions: 96 clicks + one action-1 tick).
- verify/, verify2/ — official-runner dumps of the verification run.
- stepper.py / stepper2.py — replay-prefix instruments (stepper2 replays the L1-L7 program then
  applies r:c click args, R=reset, U=undo; prints per-click component census + predator tracks).
- probe*.py, *.out, level2_initial.txt, after_hops.txt, adj/ far/ circ/ — early forensics.
