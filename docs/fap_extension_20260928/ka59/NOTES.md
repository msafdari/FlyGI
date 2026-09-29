# ka59-38d34dbb — FULL SOLVE (7/7 levels, GameState.WIN)

MEASURED end-to-end: `scripts/fap_program_premise.py --game ka59 --program /tmp/fap_ext/ka59/program_full_win.json`
=> steps_executed=321, score 0->7, final_state=GameState.WIN (seed protocol: derived_run_seeds(0, game_id), strict-offline arcade).

## Archetype: multi-body sokoban-with-launchers ("slot dock")

Every level: N objects, N shape-matched slots (4-colour outlines). The level falls the moment the
last slot's interior is exactly covered by its matching object. The goal display IS the slot
geometry itself (interior shape = object shape, on the same 3px lattice).

## Measured mechanics (all verified in-run)

- Grid = 64x64, one glyph per cell. Everything lives on a 3px tile lattice; the lattice offset
  varies per level (centres = 1 mod 3 on L1/L2/L5/L6/L7, = 0 mod 3 on L3/L4) — derive it from the
  selected object's centre.
- Colour roles (this game): 1=floor, 2=hard wall, f(15)=membrane, 4=slot outline (and timer row 63),
  e(14)=controllable-object ring, 0=selected-object centre, 5=never-selected centre,
  4=deselected centre (inside an e-ring), b(11)=boulder (push-only), c(12)/d(13)=geyser-block material.
- SELECTION: action 6 (click) on any centre pixel of an e-ring object selects it; arrows then drive
  that object 1 tile (3px) per action. Multiple drivable objects per level from L4 on. Clicks on
  anything else are no-ops. No swallow of the first post-reset action (measured L1).
- WALKING (selected object): blocked by 2, f, and other objects; passes freely OVER 4 slot walls.
  A 1xK object fits through a K'-wide gap only along the gap's axis (2x1 fits 1-tall doorways,
  1x2 fits 1-wide vertical gaps).
- CONTACT PUSH: driving into an occupied tile launches the whole contacted object (partial,
  one-tile contact suffices; pusher does not advance). LAUNCH RULE (the core physics):
  flight = 5 tiles (15px), then EXTENDED further until the object is fully clear of any f-membrane
  it overlaps, and TRUNCATED so it never overlaps a 2-wall (stop at the last valid position).
  Launches fly OVER 4-walls and f; they never cross 2. Objects in the flight path are PLOWED —
  carried ahead and deposited adjacent beyond the landing (chain works on drivable objects).
  Truncation is the designed alignment tool: pushes land objects dead-centre in slots via
  border stops (L3 b1: 5+5; L4 plus: 3-tile truncated + 4-tile truncated; L7 b: 5-truncated-to-5
  exact at (40,13)).
- GEYSER BLOCKS (c/d 6x6 blocks, from L5): they cycle d->c one pixel-row per k actions and reset
  to full d (cycle 18 actions on L6, ~6 on L7; cadence is action-count-driven, deterministic).
  At each cycle reset, any object standing in the block's open-face column band ("beam") is
  LAUNCHED away from the block: distance = minimal to fully clear the next f-membrane in that
  direction (NOT 5 tiles; measured L6 (40,28)->(28,28)). Beams do NOT act across an f-membrane
  (measured L7: b below the shelf never re-fired). Beam launches also plow blockers (measured L7).
  Geyser blocks are themselves contact-pushable (relocating the elevator is the L7 meta-puzzle);
  push-only like b-boulders, not selectable.
- TIMER: row 63, drains left<-right, 4->0. Drain rate is per level: 1 cell/action on L1,
  1 per 3 actions on L7 (budget 64 -> ~192 actions). Never hit GAME_OVER in the winning line.
  RESET (action 0) restores the current level start.
- Level transition: instant on last dock (2500-3500 cell diff), timer refills.

## Per-level solutions (verified; see programs_by_level.json for exact steps)

- L1 (12): push box right through f-gate (5-tile launch), click it, drive into right slot;
  click player object, drive into left slot. score 0->1.
- L2 (50): 4 objects/slots. Launch vertical domino Q and square R across the vertical membrane
  (drive R to the membrane edge first so the 5-tile flight lands clear); R launches Q up across
  the horizontal membrane; click-drive each into its shape-matched slot; 1x1 P docks last. 1->2.
- L3 (51): plus-boulders (b, push-only). b2: one right-launch = exactly 5 tiles into the plus slot.
  b1: arm-adjacent notch push (pusher beside the arm, not behind the centre) left twice.
  P walks into its 1x1 slot. 2->3.
- L4 (43): launch helper e-object E down through the membrane; click E (second driver!) to push the
  plus-boulder up from the bottom room (truncated 5->(39,24) straddling the membrane is legal for
  landings clear of f? measured: extension carried it to (33,24), then truncated pushes 3 and 4
  dock it at (12,39) via stop-before-border); P and E walk into their 1x1 slots. 3->4.
- L5 (20): the tube: 12 ups pump/launch the c-d stack out through the overhead f-block
  (three-stage: compress, eject; stack lands membrane-clear above), climb out, walk right, drop
  into the slot. 4->5.
- L6 (45): geyser elevators. Push the bottom d-block left so its column is under the left room;
  ride its reset-beam up through the floor membrane; push b left (1 truncated tile) then up
  (truncated 4) into the plus slot; ride the ceiling block's down-beam back; push the bottom block
  right; ride up into the right room; walk into the 1x1 slot. 5->6.
- L7 (100): finale. P is 1x2, plus a 2x1 domino H (both clickable), b-plus, two geysers, three
  slots across 5 membrane-regions. P rides geyser-2's beam bottom->middle (t6 fire), climbs the
  1-wide gap into the top chamber; H rides at t25, walks the 1-tall doorway + shaft to top-right,
  pushes geyser-1 left into the chamber (flight PLOWS parked P westward - used deliberately);
  P loops under and pushes geyser-1 again into the top-left; b auto-rides its beam down through
  the shelf membrane to (25,13); H descends, pushes P down through the band membrane (truncated
  5-flight lands P EXACTLY in its 1x2 slot); H crosses the row-31 doorway, loops far west and
  approaches along row 22 to stand OVER b's left arm ((22,7),(22,10)) - the only legal push spot,
  since the shelf covers the top-arm approach - and pushes down: 5-tile truncated flight docks b
  at (40,13); H exits and docks in its own slot. 6->7 WIN.

## Parser sketch (how to detect + solve this archetype generically)

DETECT: 64x64, available_actions [1,2,3,4,6]; find 3px-lattice e-ring objects (rings of colour 14
with centre pixel 0/4/5), 4-colour closed outlines whose interior shapes (in tile units) biject to
object shapes; a full-width row of colour 4 at the border (timer). Background 1, walls 2, membranes
= large rectangular blobs of colour 15, boulders = plus-shaped colour-11 blobs, geysers = 6x6
c/d blobs.

DERIVE: build the tile graph (3px cells, offset from the selected centre mod 3). Solve a
multi-modal motion planning problem per object:
 1. walk moves (selected; blocked by 2/f/objects, free over 4);
 2. contact-push launches: 5 tiles + extend-past-f + truncate-before-2 + plow;
 3. beam rides: at deterministic action counts (block cycle), objects in a geyser's open-face
    column hop minimally across the adjacent membrane.
Match objects to equal-shaped slot interiors; order dockings so pushers retain access (helper
objects dock last). The designed alignments make greedy search practical: every needed landing is
either exact-5 or a truncation against a 2-border, so enumerate push spots (any free tile adjacent
to any object tile, including partial contact) and BFS/A* over the small tile state space;
frame-hash BFS over raw actions also works per level (L6 fell to a 45-deep BFS in ~35k nodes when
c/d clock phases are folded into the dedup key as depth mod cycle).

## Artifacts
- /tmp/fap_ext/ka59/program_full_win.json   (321 actions, official verify: score 7, WIN)
- /tmp/fap_ext/ka59/programs_by_level.json  (steps split per level)
- /tmp/fap_ext/ka59/full_win_seq.txt        (token form)
- /tmp/fap_ext/ka59/official_win/           (fap_program_premise dump of the verified run)
- /tmp/fap_ext/ka59/ka59-38d34dbb/000-initial.txt (initial frame render)
- probe scripts: probe1.py, probe2.py, bfs6.py, bfs7.py, phase_sweep.py; traces l6_trace.txt,
  l7a-d traces; bfs6_deep.log (L6 BFS transcript)
