# ls20 ("Locksmith"-style) — measured mechanics and verified programs

Game id ls20-9607627b, offline arcade, seed = derived_run_seeds(0, game_id). 7 win_levels.
All numbered claims below are MEASURED in runs whose frame dumps live in this directory
(probe_* subdirs), unless marked HYPOTHESIS.

## Verified programs (executed, score transitions observed)

Composite 226-action program completes levels 1-5 in one episode
(verified_programs.json; final clean run: score 0->1 @13, 1->2 @58, 2->3 @107,
3->4 @174, 4->5 @226):

- L1 (13):  3,3,3,1,1,1,1,4,4,4,1,1,1
- L2 (45):  4,1,1,1,1,1,1,4,4,4,2,2,2,2,2,2,2,2,3,3,4,1,4,1,2,1,1,1,1,1,1,1,3,3,3,3,3,3,3,2,2,2,2,2,2
- L3 (49):  1,1,1,1,1,1,1,1,3,2,2,2,2,3,3,2,4,4,2,2,2,1,1,1,1,1,1,4,2,2,4,4,4,4,1,1,1,3,2,1,2,4,2,2,2,2,2,2,2
- L4 (67):  3,3,3,2,3,2,3,3,2,3,3,2,2,2,3,1,2,3,4,4,4,2,1,3,3,3,3,1,1,1,1,1,4,4,1,4,4,4,2,4,4,4,1,1,1,3,3,1,2,1,2,1,2,1,4,2,3,2,3,3,3,4,1,1,3,3,3
- L5 (52):  1,3,1,1,3,3,3,4,3,4,3,4,4,4,3,2,2,3,3,3,3,1,1,2,3,3,4,2,4,2,2,2,2,4,2,1,2,3,4,1,2,2,4,2,4,4,4,4,4,4,4,1
- L6 partial (39, delivers box A, no score): 1,1,2,1,2,1,3,3,3,1,1,1,4,4,3,4,3,4,3,3,1,1,1,1,4,4,4,4,4,4,2,2,4,4,1,1,4,2,2

## Core rule (measured across levels 1-6)

The MOVER is the 5x5 two-tone tile (rows: 2x colour 12 over 3x colour 9), NOT the small
0/1 sprite. It moves one 5px cell per action (1=up,2=down,3=left,4=right) on a lattice
rows==0 (mod 5), cols==4 (mod 5). It carries an invisible 3x3 binary PATTERN with an INK
COLOUR, shown in the bottom-left display box (rows 53-62, cols 0-11; glyph at 2px/cell,
sample pixels (55,57,59)x(3,5,7); ink = the non-5 colour there).

GOAL: a 9x9 box (border colour 3, interior 5) shows a 3x3 glyph at its centre in some
ink colour. The key must be driven so its 5x5 fully covers the glyph-centre cell.
That final move is GATED: it only succeeds when carried pattern == glyph pattern
(cell-for-cell) AND carried ink == glyph ink (L3 and L6 measured colour-only refusals).
Success = level complete (score +1). Partial overlap cells next to the box are always
enterable; the refusal bump is free (no timer, no world tick).

Devices (each drawn as a sprite inside a floor cell; the key TRANSFORMS when key and
device occupy the same cell after a step):
- "R" rotator (0/1 arrow sprite '.0.|100|.1.'): pattern <- rot90 CLOCKWISE.
  Uniquely fits all measurements over 10+ collisions (L1-L6).
- "r" shifter (4x colour-0 zigzag sprite): pattern <- f(pattern), a fixed colour-independent
  bijection. Measured pairs (9-bit row-major): 010110011->111001101->110011101->010010111
  ->101101111->011101010->010110011 (a 6-cycle), and 101110011->111010010->111101101,
  101011110->100111100->111100111->010101011. f COMMUTES WITH ROTATION (verified on 6
  pairs), so reachable shapes = rotations of the 6-cycle = 24 patterns. Closed form unknown.
- "M" recolourer (3x3 multicolour sprite 9ee/908/cc8): ink <- next in cycle
  c(12) -> 9 -> e(14) -> 8 -> c. Shape untouched.
- "O" refill ring (3x3 colour-11 ring): timer bar refills to full; ring consumed. One-shot.
- Conveyor strips (colour-1 5px line on a wall edge facing a floor cell): entering that
  cell flings the key away from the strip until it hits a wall (1 action, no chaining
  over other strips or gated boxes; door gates stop flings at the partial-overlap cell).

Timer: bar rows 61-62, cols 13-54 (42 columns), drains left->right per SUCCESSFUL action;
drain rate is per-level: L1 1 col, L2 2, L3 2, L4 1, L5 2, L6 1 (so 42 or 21 actions/life).
Lives: three 2x2 colour-8 blocks (rows 61-62, cols 55-63). Acting on an empty bar = death:
full level reset (key position, pattern, ink, devices, rings, boxes, patroller phases),
one life lost. Wall bumps cost timer but DO NOT advance the world (patrollers freeze).
Door-gate bumps cost nothing.

Level-6 novelties (all measured):
- Devices PATROL: r walks row 10 cols 14-34 (pingpong, period 8), M orbits a wall block
  counterclockwise (period 8), R pingpongs row 40 cols 14-34. Transforms fire on
  cell-sharing collisions timed mod 8 (phase = number of successful key moves since entry).
  In L5 the R device already patrolled a small period-4 loop (appears to "blink").
- TWO goal boxes. Box A (glyph 101110011 ink 8) verified: full entry with matching
  pattern+ink consumes the box (turns to open floor), no score. Box B (glyph 101010111
  ink 9) sits behind A. Its glyph shape is PROVABLY outside the 24-pattern reachable
  orbit (f commutes with rotation; also not in any mirror/transpose of the orbit), and
  its gate refused the reachable A-shape in all four inks (8,9,c,e measured). f and rot
  are colour-invariant (measured under all four inks). No hidden devices (frame variance
  scans), no swap-collisions (parity-impossible), death does not persist A's delivery.
  => Box B unopened; level 6 unsolved. Either an unobserved mechanic exists or the
  second-box rule differs from the first-box rule in a way not yet inferred.

## Not swallowed
The first post-reset action is executed normally (frame diff + timer tick on action 1
from a fresh episode). --wake 0 is correct for ls20.

## Parser sketch (how to detect the archetype and derive programs; ls20_parser.py implements
the detection half)

Detect:
1. 5px cell lattice: find the row/col offsets (mod 5) that make colour-4 runs align (here
   rows 0, cols 4). Classify each 5x5 block: all-4 = wall; all-3 = floor.
2. Key = 5x5 block '2 rows colour 12 + 3 rows colour 9'.
3. Goal boxes = 9x9 regions with colour-3 border and colour-5 interior; glyph = centre 3x3
   (non-5 pixels = 1), ink = that colour; goal CELL = the lattice cell centred on the glyph.
4. Bottom-left display (rows 53-62, cols 0-11): carried pattern at pixels (55,57,59)x(3,5,7),
   ink = its non-5 colour. Timer = colour-11 run in rows 61-62; lives = colour-8 blocks.
5. Devices by sprite signature inside floor cells: {0,1} arrow = rot-cw; 4x colour-0 = f;
   multicolour {9,14,0,8,12} = ink-cycler; colour-11 ring = refill; colour-1 5px edge
   strips on walls = conveyors (push away from strip). Watch ~8 consecutive frames to
   catch patrolling devices and their period/phase (they hide 3 of 4 frames if moving).

Derive (what solved L1-L5, mechanically):
1. Compute needed transform: find k (0-3) and number of f-applications m so that
   rot^k(f^m(carried)) == glyph, and ink distance d along c->9->e->8.
2. A* / hand-search over (cell, pattern, ink, rings-consumed, timer, world-phase):
   moves cost 1 timer tick (per-level rate), conveyor cells teleport, device collisions
   apply transforms (timed mod patrol period for moving devices), rings refill.
   Constraint: timer never empties before the next refill/goal; the bar-emptying action
   still executes.
3. Emit the action string; verify by replay (deterministic).

## Artifacts
- drive.py               deterministic replay driver (prints per-step state, dumps frames)
- ls20_parser.py         frame -> cell map/glyph/display parser
- verified_programs.json exact per-level action lists + composite + score steps
- probe_*/               frame dumps for every measurement cited above
