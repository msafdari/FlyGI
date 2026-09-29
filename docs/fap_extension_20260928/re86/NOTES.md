# re86 mechanics notes (all MEASURED in offline arcade, seed = derived_run_seeds(0, 're86-8af5384d'))

## Verified result
program_L1_L6.json: 335 actions, score 0 -> 6 (of 8 win_levels), level_fell at steps
20/58/105/173/252/335. Reproduced twice via scripts/fap_program_premise.py.

## Core loop ("crosshair parking")
- Avatars are geometric outlines: plus (2 bars), X (diagonal arms), diamond (L1-ring),
  line (single bar), square/rect (wall outline). The colour-0 pixel marks the ACTIVE avatar.
- Action 5 cycles the active avatar (fixed cycle order). Actions 1-4 move the active avatar
  exactly 3 px. First post-reset action is NOT swallowed (measured: it moves and ticks timer).
- Dots = 3x3 colour-4 ring boxes with a coloured centre pixel. A level falls at the moment
  EVERY dot cell is overlapped by a cell of an avatar (colour rules: see below).
- Target derivation: for each avatar, the position where all its same-colour dots lie ON its
  outline: plus -> dots share centre row/col within arm length; X -> |dr|==|dc| <= arm;
  diamond -> |dr|+|dc| == radius; line -> same row within extent; rect -> dots on the wall
  rectangle (h+w conserved). All coordinates stay ≡ start mod 3.

## Level-specific mechanics (measured)
- L1 (2 plus avatars): park each at its dot intersection. Fell when 2nd parked.
- L2 (X, diamond, plus): same rule per shape.
- L3 (line, X arm-11, diamond r-12, all colour 8): unique dot partition; line col ambiguity
  (24 or 27) resolved: 27 worked.
- L4 adds PALETTE TILES: an avatar touching a tile's area with ANY cell is recoloured to the
  tile colour instantly (persists until next touch). Avatars must (apparently) match dot
  colour: parking without recolour did NOT fall the level; with c/e recolours it fell.
- L5 (3 avatars, 5 tiles, 10 dots, colours 9 & 8): two avatars recoloured to the same colour
  (9) is legal. Dots are NEVER consumed: covering 4/6 9-dots and nudging away left all boxes
  intact -> coverage must be simultaneous.
- L6 adds the SQUEEZE OBJECT (8x8 colour-1 hollow block at rows 28-35, cols 28-35):
  * rect avatar pressed against it deforms perimeter-conservingly: blocked wall stays,
    trailing wall advances +3, perpendicular dimension grows +3 (alternating sides).
    Deformation persists when moving away. Grid edges only clip (no deformation).
  * plus avatars are TWO INDEPENDENT RIGID BARS + centre marker: on each move every part
    translates 3 px unless ITS sweep hits an object cell, in which case that part stays.
    Bars therefore displace relative to each other (this is how L6's 9-plus covered
    dots on two separated lines: vbar col 12 rows 3-27 + hbar row 9 cols 6-30).
  * dots and other avatars do NOT block anything (measured: a-plus bar passed through
    parked square wall). The zero marker can get separated; it is cosmetic.
- L7 (a-plus arms 9, square 13x13, 7-plus arms 9/9/18/18; tiles 9,b,8,e,6; dots:
  8 x4 (9,9),(15,3),(15,36),(27,9); 9 x2 (18,57),(24,39); b x3 (30,45),(48,39),(48,51)):
  UNSOLVED. Exhaustive decomposition: under colour-matched simultaneous coverage every
  assignment is at least one line short (the square can complete NO colour group alone;
  8-quad needs col-9 line + a 34-span row-15 line; only the 7-plus hbar (37) spans it but
  the needed -3 relative offset is unreachable without raking multiple tiles at rows 2-6).
  Colour-blind models are also >= 1 line short. Falsified candidate mechanics: dot
  consumption per completed colour group (full 9-pair coverage by a 9-avatar changed
  nothing), action-5 latching, avatar-avatar blocking. Something else exists (untested:
  zero-cell as coverer, pushing the object, non-simultaneous latching under some condition).

## Timer
Row 63 (64 colour-15 cells), consumed right-to-left (15 -> 1), roughly one cell per two
actions (L1: 5 cells/8 actions incl. a reversal anomaly; L7: 27 cells/127 actions).
Exhaustion = GAME_OVER, restores the level's initial frame. RESET (0) restarts level.
Budget was never the binding constraint in L1-L6 (each level completed well under one life).

## Files
- program_L1_L6.json / program_L1.json ... program_L6.json: verified step lists.
- final_verify/, final_verify2/: official-instrument runs (score 0->6).
- L*/ *.txt: frame renders at key states; probe*.py: measurement scripts.
