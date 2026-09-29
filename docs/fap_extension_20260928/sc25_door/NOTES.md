# sc25 levels 3-4 decoded and VERIFIED; level 5 mapped -- 2026-09-28

All numbers below are MEASURED in the strict-offline arcade, seed
`derived_run_seeds(0, "sc25-635fd71a")`, via /tmp/fap_ext/sc25/drive.py
(auto-plays L1-2 with FapExecutor in 22 actions, then executes a JSON
program with per-step 64x64 dumps). Runs: /tmp/fap_ext/sc25/run0..run17.

## Verified programs (from level entry; coordinates x=col, y=row)

**Level 3** (12 actions, levels_completed 2->3 observed on the final step,
run11; prefix re-verified identically in runs 12-17): L3_program.json
  click(30,50) click(30,55) RIGHT click(30,60)  <- punch 6-pattern, arming roll
  LEFT x3  DOWN x4  LEFT                        <- through opened door to dock

**Level 4** (25 actions, levels_completed 3->4 observed on the final step,
run16; re-verified run17): L4_program.json
  click(30,50) click(25,55) click(35,55) click(30,60)   <- f-diamond: die shrinks 4x4->2x2
  DOWN x5                                                <- align die rows 29-30 (key corridor)
  click(30,50) click(30,55) LEFT click(30,60)            <- 6-pattern, facing key: door opens
  DOWN x3  RIGHT x9                                       <- through right door into dock

## The door rule (the assigned question), measured

The d-coloured door dissolves at the moment the 6-pattern is COMPLETED on
the pip board, and only if the die's LAST SUCCESSFUL ROLL points it at the
level's key box (the small box holding a 2x2 colour-d block). Isolation on
level 3 (die start cols 35-38, key room due east at rows 22-25/cols 55-58):

- punch order T,C,B or C,T,B with NO roll: acceptance, door STAYS (runs 2, 6)
- last roll LEFT / UP / DOWN before completion: door STAYS (runs 8, 9, 10)
- last roll RIGHT (toward key) before completion: door + key box + key
  frame all dissolve to track colour 2 (runs 5, 7, 11)

Level 4 discriminates orientation-vs-line-of-sight: its key box hangs on a
2-tall corridor (rows 29-30) WEST of the chamber. Right-arming and
left-arming both FAIL while the die is off that corridor (runs 13, 14);
after rolling the shrunken die down to rows 29-30 and arming LEFT along
the corridor, completion opens door + key box (run 15). So the rule is
line-of-sight along the facing direction to the key box, not a fixed
direction. (Level 3 is consistent: the eastward ray runs through the
4-gate corridor rows 23-24 to the key room; the door there is elsewhere,
so the ray hits the KEY, and the door opens wherever it is.)

Post-acceptance rolls toward the key do NOT open the door (run 2 p004-5):
the check fires only on the completing click.

## Other mechanics, measured

- Click on a pip-board cell TOGGLES it: 0->e, e->0 (run1), and on blank
  boards 2->e, e->2 (runs 12-14). Acceptance fires the instant the punched
  set equals a displayed pattern, consumes it (cells -> 2), and is
  re-armable (the same pattern can be punched again later, run5 p005-6).
- Level 3's board PRE-MARKS the required pattern as 0-cells; levels 4-5
  boards start blank (all 2) and the patterns come only from the displays.
- f-coloured (15) diamond display {N,W,E,S} = SHRINK pattern: completion
  shrinks the die 4x4 -> 2x2 (run12 p016), no arming needed (fires with
  die anywhere). 6-coloured display = DOOR pattern (needs the ray).
- The die rolls by its own size: 4 px per action at 4x4, 2 px at 2x2.
  Faces re-orient to the last roll (right => a-left/9-right etc.). A
  blocked roll can rotate it in place once (run8 p010) or do nothing.
- Off-board clicks (door, key, gate, die, dock, background) are TOTAL
  no-ops: no frame change, no timer tick (run4). Free probing confirmed.
- Ramming the door does nothing (run3: three DOWN rolls flush against it).
- NO first-action swallow at level entry: the first click after entering
  levels 3, 4 and 5 took effect immediately (runs 1, 12, 17). The known
  sc25 swallow is per-RESET (episode start still swallowed; FapExecutor's
  retry absorbed it during auto-play). RESET mid-level not re-tested.
- Timer: cols 62-63 (colour e, 32 blocks of 2x2) drain top-down, FULLY
  RESET at each level entry. Drain over the 10 measured actions of run1
  matches cumulative floor(5i/8) blocks (ticks on actions 2,4,5,7,8,10),
  i.e. ~51 actions per level; blocked rolls sometimes tick, no-op clicks
  never do. GAME_OVER by exhaustion not reached in these runs.
- Dock entry = ordinary rolls into the 9-framed box's colour-a interior;
  the level completed ON the roll that put the die into the interior
  (L3: final LEFT; L4: 9th RIGHT), no extra merge roll needed this time.

## Level 5 (boundary, mapped but unsolved)

Board adds: a b-coloured pattern display {(0,0),(0,1),(1,1)}, TWO doors
stacked in the right shaft (d at rows 16-17 and c at rows 20-22, cols
51-54, gating the dock at top-right), a 6-framed box holding d (rows
11-14 cols 15-18), a 6-framed box holding c (rows 43-46 cols 3-6, with
colour-4 corner marks), and a b-marked gadget holding f pips (rows 38-41
cols 28-31). f-diamond completion still shrinks the die (run17 p041) AND
mutates the gadgets: two b marks vanished (b->5, rows 34/39 cols 50-55)
and four new f cells appeared (5->f, rows 37-42 cols 27-32) -- the
apparatus is stateful. Expected continuation (UNTESTED): punch 6-pattern
once per key box with line-of-sight to each (d-box then c-box) to open
both doors, plus an unknown role for the b-pattern; eleven-nulls base
rate applies.

## Files

- drive.py                 driver (auto-play L1-2, then program + dumps)
- L3_program.json          verified 12-action level-3 program
- L4_program.json          verified 25-action level-4 program
- prog_v*.json, run*/      all probe programs and per-step frame dumps
