# tu93 mechanics notes (all values MEASURED in-session unless marked otherwise)

Game: tu93-0768757b. 9 levels, all solved offline; full-game replay = 187 actions,
final state GameState.WIN (see final_verified.json).

## Archetype: lockstep maze with sentinel/patroller/chaser enemies

- 64x64 frame, background colour 5. Rooms are 3x3 pixel blocks on a 6-pixel
  pitch (rooms at lattice points, colour 0). Colour-2 3x3 blocks between two
  rooms are OPEN DOORS; background 5 between rooms = wall.
- Avatar: 3x3 colour-9 block with one colour-4 pixel on the edge facing its last
  entry direction. Moves exactly one room per action through an open door;
  blocked moves do nothing to the world.
- Goal: colour-14 ("e") 3x3 room. Walking onto it completes the level instantly.
- Actions: only 1..4 (up/down/left/right). No click. First post-reset action is
  NOT swallowed (measured: fresh episode, first RIGHT moved the avatar).

## Timer

- Row 63 = 64 colour-6 pixels, depleting right to left; every action (including
  blocked ones) costs budget. Level-1 life measured at exactly 50 actions
  (timer GAME_OVER after 50 blocked moves). Pixel cost per action varies by
  level (~1.28 px on L1/L5/L8; ~3.2 px on L4 -> ~20-action life on L4).
- GAME_OVER (timer or enemy) ends the episode; RESET (action 0) then restores
  the CURRENT level start at 100% pixel identity, levels_completed preserved,
  full timer, enemies re-homed. Probing is therefore cheap.

## World tick rule (the key mechanic)

Enemies advance only when the avatar makes a SUCCESSFUL move. Blocked moves
freeze the world (measured 10+ ticks, L2/L4/L8). Consequence: parity of the
world state is locked to the count of successful moves.

## Enemy types (colour = type)

1. Colour 8 = static sentinel. One colour-15 ("f") eye pixel on mid-edge =
   facing. Never moves on its own. Entering its FACED adjacent room = death
   (it lunges; co-entry). Entering ITS room from any non-faced side = the 8
   dies and the avatar takes the room. Standing 2+ rooms away in its facing
   line is safe (measured L2).
2. Colour 12 = patroller. Moves 1 room per world tick along its facing axis
   through open doors; on arriving at a wall its facing flips immediately
   (f-pixel flips edge). Period = 2*(corridor_length-1). Patrollers pass
   through each other and through the goal room. Avatar dies on co-entry
   (avatar and patroller entering the same room in the same tick). Entering a
   room the patroller just vacated is safe (measured repeatedly).
3. Colour 13 = dormant chaser. Sits still like an 8 until the avatar enters
   its facing line of sight (open-door line; trigger measured at distance 2).
   Distance-1 entry = lunge death, like the 8. When triggered, the eye pixel
   retracts and it walks its LOS to the trigger room, then TRAIL-FOLLOWS the
   avatar's exact path with lag 2 (chaser@tick k = avatar@tick k-2; verified
   over 12+ consecutive ticks on L8 and all 29 ticks of L9). It never gives
   up. Death iff the avatar re-enters a room exactly 2 ticks after leaving it.
   Because the maze is bipartite, a chased avatar can never change phase
   parity; all timing must be done with 4+-cycles. A dormant chaser can be
   killed by side/back entry into its room, same rule as the 8.

## Level inventory and solving idea

- L1: plain 6x6 maze, BFS. 18 moves.
- L2: one static 8 in the only corridor; loop around via row 2, kill it from
  below. 10 moves.
- L3: three static 8s; BFS avoiding faced rooms, side-kills allowed. 19 moves.
- L4: static 8 + first patroller (col corridor, period 8); thread the patrol,
  kill the 8, tight ~20-action budget. 17 moves.
- L5: four patrollers (periods 10,14,4; two share the goal column and pass
  through the goal room). Time-expanded BFS. 29 moves.
- L6: six statics + two patrollers. 28 moves.
- L7: one static. 14 moves.
- L8: first chaser (guards the only corridor to the goal) + one static:
  pre-kill the static, trigger the chaser, run one 6-room loop so it follows,
  dash up the vacated corridor. 23 moves.
- L9: chaser + three patrollers (periods 8,4,6) + two statics covering each
  other and the goal room: kill (6,3)-8 side-on, then (5,3)-8 from below, then
  enter goal ("targets in order"). First move necessarily triggers the chaser.
  29 moves.

## Verified programs (fresh episode, seed = derived_run_seeds(0, game_id))

Actions: 1=up 2=down 3=left 4=right. Each list completed its level
(levels_completed incremented) in the clean end-to-end replay:

L1: 4 2 2 4 1 4 2 2 3 3 2 4 4 2 4 1 4 2
L2: 1 4 4 2 4 4 1 4 4 1
L3: 1 1 4 1 3 3 1 3 3 2 4 2 3 3 3 2 4 2 4
L4: 4 4 3 4 4 1 1 4 2 1 3 1 1 3 3 2 3
L5: 3 3 3 4 3 3 3 3 3 2 1 2 1 2 1 2 1 2 2 2 4 2 2 4 4 4 1 1 3
L6: 3 3 2 1 2 1 2 2 3 3 4 4 4 2 2 3 2 3 1 2 3 1 1 3 1 1 1 3
L7: 4 4 4 2 2 4 1 4 1 1 1 4 2 2
L8: 4 4 1 1 3 4 4 4 3 3 2 2 3 1 1 4 4 4 1 1 1 3 3
L9: 3 3 1 1 4 2 2 3 1 1 4 1 1 4 4 4 2 2 4 2 3 2 3 2 2 3 3 1 4

## Generic parser/solver (implemented: planner.py / planner2.py in this dir)

1. Detect archetype: find colours {0,2,9,14} in 3x3 blocks on a 6-pitch
   lattice; row 63 all-6 timer strip; available_actions == [1,2,3,4].
2. Lattice origin = min (row,col) over cells coloured 0/4/8/9/12/13/14/15.
   Room (i,j) at pixels (r0+6i, c0+6j); door(i,j,di,dj) open iff pixel
   (r0+6i+3di, c0+6j+3dj) == 2 and target lattice point is a room.
3. Read avatar (9), goal (14), enemies (8/12/13) + facing from the f-pixel
   offset inside the block (relative to block centre).
4. Patroller trajectories are pure functions of tick count; chaser position is
   a pure function of the avatar's own path. So plan with BFS over
   (room, prev_room, tick, dead_statics, chaser_state) with the lethality
   rules above; execute open-loop. ~200-tick horizon and LCM dedup suffice.

## Session hygiene

All artifacts under /tmp/fap_ext/tu93/. No repo files touched, no git
commands run. Environment driven only via the offline arcade
(evaluate_random_baseline helpers), deterministic seed 0-derived.
