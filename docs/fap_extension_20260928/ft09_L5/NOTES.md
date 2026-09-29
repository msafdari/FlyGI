# ft09 — FULL WIN, 6/6 levels in 81 actions (levels 5-6 newly decoded)

Investigation date 2026-09-28, offline arcade, seed_index 0
(`derived_run_seeds(0,'ft09')`). All claims below are MEASURED in this
session unless marked otherwise; execution log: `final_run.py` ->
`programs.json` (score transitions 0->1->...->6 at actions 5, 12, 26, 47,
68, 81; final `GameState.WIN`).

## Level 5's actual rule (the assigned question)

The old claim "level 5 satisfies the two-sided glyph rule yet does not
fall" was evaluated with the WRONG PALETTE. Measured on level 5:

1. **Palette comes from the top-right indicator pair**: two stacked 4x4
   off-lattice blocks (L5: e over f; L6: b over e). These are the level's
   two tile colours; the TOP block is the colour every board tile starts
   at (n=2 levels). Glyph centres are drawn in palette colours (L5 has
   both e- and f-centred glyphs).
2. **Two-sided glyph rule, unchanged**: glyph 0-cells prescribe the
   glyph's centre (marked) colour, 2-cells the other palette colour, at
   the corresponding tile of the glyph's 3x3 neighbourhood. **3-cells are
   new in L5/L6: they mark neighbourhood positions that are not
   prescribable** (off-lattice, absent, or occupied by another glyph) —
   verified 100% consistent across all 12 glyphs of L5+L6, including
   every overlap between neighbouring glyphs.
3. **Flip-mask tiles (the stacked second mechanic)**: a board tile's
   interior colour-6 sub-cells are a FLIP MASK. Clicking a board tile
   toggles its own palette phase AND the phase of each orthogonal
   neighbour board tile its 6-cells point at (edge-centre sub-cell
   (0,1)=N, (1,0)=W, (1,2)=E, (2,1)=S). Flips aimed at glyphs or absent
   positions are dropped (measured: L5 checkered click next to glyph F
   flipped 3 neighbours not 4; L6 click under glyph flipped self only).
   - L5: plain tiles (no 6s) toggle self only; three "checkered" tiles
     (6s at all four edge-centres) toggle self + all four orthogonal
     neighbours. A checkered tile's own displayed phase = its non-6
     colour, and it satisfies a prescription with that phase.
   - L6: EVERY tile carries one 6 at north edge-centre -> click toggles
     self + north neighbour (direction discriminated by clicking (2,3),
     which flipped (2,3)+(1,3), not (3,3)).
4. **Win check is immediate**: the level falls on the click that makes
   every glyph prescription hold. Unprescribed tiles are free (L5 tile
   (2,2) ended at the non-target-relevant colour; win still fired).
5. Clicks on glyphs, background, or the indicator are REFUSED and freeze
   the world completely — not even a timer tick (free probing).

Why the FapExecutor cycled on L5 (measured mechanism): it parses the
6-masked checkered tiles as GLYPHS (non-uniform sub-blocks), which (a)
poisons the program with an all-8-neighbours->f pseudo-prescription and
(b) means the checkered tiles themselves are never clicked, so the three
f-phase-required checkered positions can never be satisfied.

## Verified programs (executed, transitions observed)

`programs.json` holds the exact step lists. Summary (all action 6 clicks
at tile centres, after one initial RESET):
- L1-4: FapExecutor auto-play, 4+7+14+21 clicks (46 + RESET = 47 actions).
- L5 (21 clicks): click the three checkered tiles once each ((1,2),(3,2),
  (5,4) on lattice rows [4,12,20,28,36,44,52] x cols [6,14,22,30,38,46,54]),
  then 9 repair clicks back to e, then 9 clicks setting f-prescribed
  tiles. Score 4->5 on the 21st click.
- L6 (13 clicks): per-column triangular lights-out solve of the north-dot
  chains (lattice rows [6,14,22,30,38,46] x cols [4,12,20,28,36,44,52]):
  c(bottom)=needed(bottom), c(i)=needed(i) XOR c(i+1), chains broken at
  glyphs/absences. Score 5->6 on the 13th click, state WIN.

## Quirks

- **No post-reset swallow** (confirms prior record): first click after
  RESET has full effect (probe4: post-reset click ndiff=32).
- **Timer**: row 63 starts as 64 c-pixels each level; pixels flip c->b
  right-to-left on effective actions n=2,3 (mod 4) within the level
  (measured across two independent click sequences). Refused actions do
  not tick. RESET (action 0) restores the LEVEL start at 100% identity,
  timer included. Timer death not reached this session; prior ft09 record
  says the timer kills the life (GAME_OVER -> level restart).
- available_actions is always [6] (click-only game).

## Parser/planner sketch (for the library extension)

1. Detect the 8-pitch lattice of 6x6 tiles (2x2-uniform sub-blocks,
   separator ring) — offsets differ per level, detect from data.
2. Classify each tile: uniform -> plain board tile; cells within
   {0,2,3}+one palette colour at centre -> GLYPH; two colours with 6s at
   edge-centre positions -> board tile with flip mask (6 positions ->
   direction set). The current phase of a masked tile is its non-6 colour.
3. Palette: the two stacked 4x4 blocks at an off-lattice corner
   (top-right so far); fallback: plain-tile colours + glyph centres.
4. Prescriptions: per glyph, 0->marked, 2->other, 3->skip (and validate
   3s point only at non-prescribable positions; abstain otherwise).
5. Plan: needed(t) = current phase != prescribed; solve A c = needed over
   GF(2) where column c(t) toggles t plus its mask-directed present board
   neighbours; unprescribed tiles are free rows. L5 instance: click each
   phase-wrong masked tile once, then repair plain tiles. L6 instance:
   per-column back-substitution. Toggle effects commute (XOR), so click
   order within a solution is irrelevant (INFERRED from involution +
   statelessness; executed order was masked-tiles-first).
6. Win: score increments on the completing click; no submit action.

## Artifacts

- drive.py (session driver), solve5.py (L5 replay), probe1/2/4.py
  (measurement scripts), final_run.py (clean verification)
- level5_start.txt/.npy, level6_start.txt/.npy, probe1_out.txt,
  probe1_final.txt, probe2_final.txt, probe4_final.txt
- programs.json — the verified per-level programs + transitions
