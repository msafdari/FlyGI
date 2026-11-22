# Compass label map: instrument-bug finding and amendment (2026-11-21)

**Status.** FROZEN on 2026-11-21 in the commit that adds this file, tagged
`compass-map-freeze-20261121`, BEFORE any compass instrument was run under
the amended map. What had already been seen under a corrected ordering, by
whom and how, is in section 9. That section matters: two of the re-runs
are confirmatory because of it.

It is AFTER data contact: every instrument below has a recorded outcome
under the registered map. The rule it is filed under is the one each
registration states for itself: "Changes after first data contact require a
recorded instrument-bug finding and a full re-run."

**Whose decisions these are.** The owner's go, verbatim, was "Yes, prepare
the compass amendment and re-run." Every specific decision in sections 7, 8
and 10 was made by the local session that wrote this file, under that one
line. The owner has not reviewed them one by one. They were frozen here and
not in the cloud design session that froze the earlier registrations,
because the go arrived here.

This file is the single record. The registrations it amends each carry a
dated pointer to it and are otherwise untouched:
`task9_cx_latent/killtest_design.md`, `task9_cx_latent/killtest_design_reopening.md`,
`task10_menu/killtest_design.md`, and the in-header preregistrations of
`scripts/benchmarks/cx_ring.py`, `scripts/benchmarks/fc2_eb_ring.py` and
`scripts/cx_scratchpad_premise.py`.

Tiers follow AGENTS.md. **Measured** is a number with its protocol.
**Established** is the literature or the connectome's own annotation, with
the source. **Assumed** is something we chose. **Inferred** names its bridge.
**Agent-reported** means a subagent of this session produced it and I did
not reproduce it.

**Terms.** A *ring position* is one of the sixteen 22.5 degree EPG sectors of
the ellipsoid body. The literature calls that sector a wedge. Earlier
documents here called it a half-wedge, and this file keeps that word where
it quotes or continues them. A *write wedge* is the 90 degree arc an
instrument drives. A *Biswas unit* is one of eight 45 degree groups. Under
the amended grouping a unit is two adjacent ring positions, and it is
offset by one position from the anatomical *tile* of Wolff and Rubin. A
write *follows* when its settled angle is within one ring position (22.5
degrees) of its own write angle and no other surviving write of the same
arm, at the same cell, grid point or configuration (on the settle map, of
the same write style), settled within half a position of it (section 8,
C7).

---

## 1. The finding

Nine compass scripts place each EPG cell on the ring from its bridge label
(`EPG(PB08)_L3` is left bridge half, glomerulus 3). The registered map,
assumption AC-1, was

    index = (glomerulus - 1) * 2 + (0 if L else 1),   angle = index * 22.5 deg

so L_k sat beside R_k. Its eight-unit version, assumption AC-B1, pooled L_k
with R_k.

In the fly the two bridge halves run round the ring in OPPOSITE directions.
L_k lies between R_(9-k) and R_(10-k). The registered map ran both halves
in the same direction, so it reflected the left half-ring relative to the
right one. Glomeruli 1 and 5 are the two fixed points of that reflection.
The other six left glomeruli were placed on the wrong side of the ring.

This is not a rotation of the ring. Each registration that stated a limit
for the map called it correct up to a fixed rotation (one said rotation or
reflection) and said no metric depended on that. A reflected half-ring is
outside that sentence, and it is not cancelled by any within-run
comparison.

**Measured, 2026-11-21** (`python scripts/arenas/compass_map_check.py`,
direct EPG to EPG synapse counts between different ring positions, 6,956
synapses, compared with 10,000 random placements of the sixteen labels,
seed 20261121; on the frozen revision of the script 13.7 s and 1.25 GB
peak, console record in
`results/arenas/compass_amendment_20261121/checks/`):

| Map | Share between ring neighbours | p against random maps | Share within two positions | p |
|---|---|---|---|---|
| Registered (AC-1) | 0.1872 | 0.197 | 0.3029 | 0.324 |
| Amended | 0.8170 | 0.0001 (the floor) | 0.9327 | 0.0001 |
| 10,000 random maps | mean 0.1329, 95th percentile 0.2550, maximum 0.4439 | | mean 0.2657, 95th percentile 0.4201, maximum 0.6180 | |

By this statistic the registered map is indistinguishable from dealing the
sixteen labels onto the ring at random.

Two cells of the same bridge half sit at the same ring distance under both
maps, so only cross-side count can tell the maps apart. Of the 5,765
cross-side synapses, 98.6% join ring neighbours under the amended map and
22.6% under the registered one (same run). The counts are whole-neuron
counts, but left and right EPG arbors meet only in the ellipsoid body, so
the cross-side count is ellipsoid-body coupling.

The same run, per left glomerulus: the two right glomeruli that receive the
most synapses from L_k are the two the amended map puts beside it for all
eight k. The registered map gets that right for k = 1 and 5 only. Example
rows (summed counts, pre L_k to post R_j): L8 sends 219 to R1 and 177 to R2
and 4 to R8. L7 sends 227 to R3 and 174 to R2 and 0 to R7. L2 sends 189 to
R8 and 132 to R7 and 0 to R2.

## 2. What was registered, verbatim

- Task 9 (`task9_cx_latent/killtest_design.md`, 2026-10-10): "Wedge
  coordinates: the cx_ring/cx_scratchpad mapping VERBATIM (AC-1) — instance
  regex `_([LR])(\d)`, index = (wedge-1)*2 + (0 if L else 1), angle = index
  * 22.5 deg; ESTABLISHED annotation, ASSUMED interleaving, correct up to a
  fixed rotation (which no metric below depends on)."
- `scripts/cx_scratchpad_premise.py` (2026-09-27), where the map was first
  typed: "ASSUMPTION: the standard mapping of 16 wedges onto 360 degrees
  (22.5 deg each, L and R interleaved); wrong only up to a fixed rotation,
  which cancels in an A-vs-B readback."
- `scripts/benchmarks/fc2_eb_ring.py` (2026-09-29): "wrong only up to a
  fixed rotation/reflection, which cancels in every within-run comparison."
- Task 10 section 3, AC-B1 as corrected 2026-10-31: "the convention is OURS
  -- unit = (instance digit - 1) mod 8, L/R merged ... the label-derived
  wedge stands in for their EB-innervation assignment, which needs
  morphology we do not load. Breaks: wedge-profile distortion. Canary: the
  published-r_a cross-check below."
- The class-3 registration (`killtest_design_reopening.md`) never states
  the map. The instrument carried it without an ASSUMPTION label.

Where the assumption was labelled, its stated limit ("up to a fixed
rotation") was the part that was wrong.

## 3. Evidence, by tier

**Established, literature** (each passage read at source on 2026-11-21):

- Hulse et al. 2021, eLife 10:e66039. The sixteen EPG wedges alternate
  between the right and the left bridge, and the two bridge bumps are
  offset by 22.5 degrees. R5 and L5 receive from adjacent wedges, and a
  bump centred on L5 sits between R5 and R4 on the right. Fig. 16B draws
  the ring and prints four wedge angles: L1 at 0, L7 at 90, L5 at 180, L3
  at 270. The full order of the sixteen wedges in that figure, clockwise
  from the 180 wedge, is L5, R4, L6, R3, L7, R2, L8, R1, L1, R8, L2, R7,
  L3, R6, L4, R5. That order is MY READING of the image (right-bridge
  wedges are hatched, and wedge colours match the glomerulus colours in
  the same panel), not a sentence of the paper.
- Wolff, Iyer and Rubin 2015, J Comp Neurol 523:997. One glomerulus per
  wedge. Left and right arbors alternate in the ellipsoid body. The left
  bridge half wraps the ellipsoid body clockwise and the right half
  counterclockwise. For cell types in glomeruli 1 to 8, tile regions and
  wedge regions coincide.
- Wolff and Rubin 2018, J Comp Neurol 526:2585, on the P-EG tile cell. Its
  eight tile pairs are G1R/G1L, G2R/G8L, G3R/G7L, G4R/G6L, G5R/G5L,
  G6R/G4L, G7R/G3L, G8R/G2L. By the Wolff 2015 sentence above these carry
  over to the EPG wedges. All eight are ring neighbours under the amended
  map. Under the registered map only G1R/G1L and G5R/G5L are.
- Turner-Evans et al. 2020, Neuron 108:145. Delta7 neurons are named after
  the two or three glomeruli that receive their axons. Ellipsoid-body EPG
  cells contact their neighbours (also Hulse et al. 2021, Fig. 17Ci).

**Established, connectome annotation.** 35 of the 42 MaleCNS Delta7
instance names join L_k with R_(9-k) (for example `L8R1R9`, `L7R2`,
`L1L9R8`), and the other 7 join L_k with R_(10-k). Both pairings are ring
neighbours under the amended map.

**Measured, this repository.** The table in section 1. The amended order is
also the best of all cyclic orders of the sixteen labels on that statistic
(agent-reported by two reviewers independently, from the same table: 5,683
synapses between neighbours, against 5,170 for the best order that
differs).

**Measured, the registered canaries.** The registrations attached two
checks to these assumptions. The Biswas cross-check fired: both fitted r_a
fell outside its 0.1 band. Stage A's context check had no threshold, so it
could not fire; its 46.6 degree reading is what a reflected half-ring gives
on a synthetic ring (INFERRED, bridge below). Both were read as
inconclusive:

- Stage A's blind spectral ordering check on AC-1 recorded a residual of
  46.6 degrees on 2026-10-10 and was recorded as "neither confirmed nor
  refuted". A perfect synthetic ring labelled in the anatomical order and
  read through the registered map gives 45.0 to 50.6 degrees on that check
  (the exact value depends on how the eigensolver picks a basis for two
  equal eigenvalues: 49.2 with numpy on this machine). Read through the
  right map the same ring gives 0 to 11.25 degrees. That is now a unit
  test, `test_registered_map_misreads_an_anatomically_labelled_ring`,
  which also pins the exact parts: bandedness 0.25 where the true value is
  1.0, mirror-peak 0.0625 where the true value is 1.0. INFERRED, bridge
  stated: that the 46.6 degree reading on the real graph was the same
  fault showing, assuming the real two-hop matrix behaves like the
  synthetic ring. The amended run measures it. The check had no
  threshold. That was the miss.
- The Biswas cross-check on AC-B1 fired on 2026-10-31 (fitted r_a 0.4221
  and 0.2132 against the published 0.548 and 0.437, both outside the 0.1
  band). The close recorded AC-B1 and AC-B2 as "the registered suspects,
  unresolved which". It was not followed up for three weeks.

**Measured, the source paper's own figure** (Biswas et al., bioRxiv
10.1101/2024.11.01.621596 version 2, Fig. 1g, whose caption says it shows
the EPG and Delta7 neurons of the male CNS dataset with estimated wedges
separated by thin grey lines; `python scripts/arenas/biswas_fig1g_check.py
--image <panel crop>`, on the frozen revision of the script 10.5 s and
1.32 GB peak, console record in
`results/arenas/compass_amendment_20261121/checks/`; the crop is page 2 of
the PDF rendered 7,200 pixels wide, 1,560 by 1,500 pixels, SHA-256
`1a988e383254839dee5c2aba099503fea739d439b43da1c8fc23102660801f97`, kept
locally and not in the repository):

- Unit SIZES. The separator lines fall at cells 6, 11, 17, 23, 29, 35, 40,
  46 and 51, 57, 61, 67, 73, 79, 83 on both axes, each within 0.11 of a
  cell from an integer position. So the paper's EPG units hold 6, 5, 6, 6,
  6, 6, 5, 6 neurons and its Delta7 units 5, 6, 4, 6, 6, 6, 4, 5.
- Unit MEMBERSHIP, cell block by cell block. The script reads the darkness
  of each of the 46 by 46 EPG cells and compares the figure's label-pair
  block means (256 of them) with the mean counts between the same label
  pairs in OUR compiled MaleCNS graph. It scores a declared family of 960
  orderings of the 46 EPG cells: one right and one left glomerulus per
  unit (every one of the 240 left-right matchings that give the figure's
  unit sizes), each label's cells contiguous, units in right-glomerulus or
  left-glomerulus order, either label first. Exactly one fits: R1 L8 R2 L7
  R3 L6 R4 L5 R5 L4 R6 L3 R7 L2 R8 L1, with a root-mean-square error of
  0.23 grey levels out of 255. The runner-up is at 9.16 and the worst at
  27.70. That ordering is the amended ring order, cut into the amended
  units.
- Outside the declared family (agent-reported by a reviewer, from the
  saved image and the saved 16 by 16 table): a search over all contiguous
  label orders, by hill climbing from 60 random starts, found nothing
  below 7.4 other than the amended order; the best of all 989 single-cell
  label swaps scores 2.95; and the amended order is also the best of all
  40,320 right-ordered matchings whatever their unit sizes.

So the EPG block of the published figure matches our counts block for
block, drawn in the amended ring order and grouped as L_k with R_(9-k). No
value fitted by the recipe enters this. The comparison itself fits one
grey-per-count scale per hypothesis; fixing that scale from the figure's
own colour bar instead (255 grey levels for about 94 counts) gives 0.25
for the same winner (agent-reported). It does rest on our counts and theirs
being the same data, which the 0.23 fit is itself the evidence for. The
figure's Delta7 block and cross blocks were compared by unit sizes only.

Sizes alone would not have identified the grouping. With the MaleCNS
per-glomerulus EPG counts (2, 2, 3, 3, 3, 3, 3, 4), of the sixteen regular
pairings only L_k with R_(9-k) gives 6, 5, 6, 6, 6, 6, 5, 6. The registered
pooling gives 4, 4, 6, 6, 6, 6, 6, 8 and the other neighbour pairing gives
4, 6, 6, 6, 6, 6, 6, 6. But 240 arbitrary matchings share the sizes. The
cell-by-cell comparison is what settles it.

The Delta7 units point the same way. The recipe derives each Delta7
neuron's unit from the EPG grouping. It gives Delta7 units of 5, 6, 4, 6,
6, 6, 4, 5 under the amended grouping, which equals the figure, against
1, 7, 4, 5, 7, 6, 5, 7 under the other neighbour pairing and 1, 5, 5, 5,
7, 6, 4, 9 under the registered one (measured in memory in the
unregistered check of 2026-11-21, output saved locally). The paper's text
speaks of compartments of "four to six" similar neurons, which the
registered grouping's Delta7 units of 1, 7 and 9 and its EPG unit of 8 do
not fit.

## 4. The amended map

Defined once, in `src/flygi/compass_map.py`:

    angle(R_k) = 22.5 + 45 (k - 1) deg        index(R_k) = (2 (k - 1) + 1) mod 16
    angle(L_k) = (360 - 45 (k - 1)) mod 360   index(L_k) = (-2 (k - 1)) mod 16
    unit(R_k)  = (k - 1) mod 8                unit(L_k)  = (8 - k) mod 8

Ring order by index 0 to 15: L1 R1 L8 R2 L7 R3 L6 R4 L5 R5 L4 R6 L3 R7 L2 R8.

| Label | EPG cells | Registered index | Registered angle | Amended index | Amended angle | Registered unit | Amended unit |
|---|---|---|---|---|---|---|---|
| R1 | 2 | 1 | 22.5 | 1 | 22.5 | 0 | 0 |
| R2 | 2 | 3 | 67.5 | 3 | 67.5 | 1 | 1 |
| R3 | 3 | 5 | 112.5 | 5 | 112.5 | 2 | 2 |
| R4 | 3 | 7 | 157.5 | 7 | 157.5 | 3 | 3 |
| R5 | 3 | 9 | 202.5 | 9 | 202.5 | 4 | 4 |
| R6 | 3 | 11 | 247.5 | 11 | 247.5 | 5 | 5 |
| R7 | 3 | 13 | 292.5 | 13 | 292.5 | 6 | 6 |
| R8 | 4 | 15 | 337.5 | 15 | 337.5 | 7 | 7 |
| L1 | 2 | 0 | 0 | 0 | 0 | 0 | 7 |
| L2 | 2 | 2 | 45 | 14 | 315 | 1 | 6 |
| L3 | 3 | 4 | 90 | 12 | 270 | 2 | 5 |
| L4 | 3 | 6 | 135 | 10 | 225 | 3 | 4 |
| L5 | 3 | 8 | 180 | 8 | 180 | 4 | 3 |
| L6 | 3 | 10 | 225 | 6 | 135 | 5 | 2 |
| L7 | 3 | 12 | 270 | 4 | 90 | 6 | 1 |
| L8 | 4 | 14 | 315 | 2 | 45 | 7 | 0 |

**No free choice in the sixteen-position map.** The right half keeps its
registered angle. The left half is reflected. The result agrees with the
four wedge angles Hulse et al. print in Fig. 16B (L1 0, L7 90, L5 180, L3
270) and with the order of all sixteen wedges read from that figure
(section 3). So the ring's rotation and direction are fixed by a published
figure and by the registration itself.

**What the nominal angles write.** Every right-centred angle keeps its
number AND its centre cell: 22.5 is R1, 112.5 is R3, 202.5 is R5, 292.5 is
R7, and the eight class-3 angles 22.5 + 45j are R1 to R8. That covers the
four seed angles of the class-1 and class-2 benchmarks, Stage B and the
seeding probe, the class-3 write and steering angles, and the scratchpad
script's two main-mode targets. What changes for them is which left cells
fall inside each 90 degree write wedge (for class 3, which writes a von
Mises profile over every EPG cell rather than a wedge, the left cells'
drive rates):

| Nominal angle | Registered write wedge (cells) | Amended write wedge (cells) |
|---|---|---|
| 22.5 | R8 L1 R1 L2 R2 (12) | R8 L1 R1 L8 R2 (14) |
| 112.5 | R2 L3 R3 L4 R4 (14) | R2 L7 R3 L6 R4 (14) |
| 202.5 | R4 L5 R5 L6 R6 (15) | R4 L5 R5 L4 R6 (15) |
| 292.5 | R6 L7 R7 L8 R8 (17) | R6 L3 R7 L2 R8 (15) |

**The one exception: the scratchpad settle map.** Its eight write angles are
0, 45, ..., 315, which are LEFT-centred. Six of them change centre cell
under the amended map. Only the 0 and 180 rows are like-for-like across the
two maps.

| Settle-map write angle | Registered centre | Amended centre | Registered wedge (cells) | Amended wedge (cells) |
|---|---|---|---|---|
| 0 | L1 | L1 | L8 R8 L1 R1 L2 (14) | L2 R8 L1 R1 L8 (14) |
| 45 | L2 | L8 | L1 R1 L2 R2 L3 (11) | L1 R1 L8 R2 L7 (13) |
| 90 | L3 | L7 | L2 R2 L3 R3 L4 (13) | L8 R2 L7 R3 L6 (15) |
| 135 | L4 | L6 | L3 R3 L4 R4 L5 (15) | L7 R3 L6 R4 L5 (15) |
| 180 | L5 | L5 | L4 R4 L5 R5 L6 (15) | L6 R4 L5 R5 L4 (15) |
| 225 | L6 | L4 | L5 R5 L6 R6 L7 (15) | L5 R5 L4 R6 L3 (15) |
| 270 | L7 | L3 | L6 R6 L7 R7 L8 (16) | L4 R6 L3 R7 L2 (14) |
| 315 | L8 | L2 | L7 R7 L8 R8 L1 (16) | L3 R7 L2 R8 L1 (14) |

**The eight-unit grouping (AC-B1 as amended).** L_k shares a unit with
R_(9-k): R_k goes to unit k-1 and L_k to unit 8-k. One formula is named
because the Delta7 assignment breaks exact ties toward the lowest unit
index, so equivalent relabelings could differ on a graph with exact ties.

**How the grouping was FOUND, and what it is ADOPTED on.** These are two
different things and both are stated.

- FOUND. Early on 2026-11-21 a subagent of this session was fact-checking
  a draft email to the source paper's authors. Between 00:02 and 00:21
  Pacific it wrote and ran six unregistered scripts that fitted the recipe
  in memory under three groupings (the registered one, L_k with R_(9-k),
  and L_k with R_(10-k)) and compared each fit with the published r_a.
  L_k with R_(9-k) matched the published values to print precision. A
  second subagent, fact-checking the other draft emails, independently
  fitted the recipe under L_k with R_(9-k) and reported the same match.
  Both reports reached the session at about 00:30, and I re-ran five of
  the first subagent's six scripts (all but `null_cap_check.py`) at 00:41
  to 00:45. That is how the grouping was
  noticed. So the frozen clause of the Task 10 registration, "Published
  values enter NOTHING but this comparison", was BREACHED in discovery,
  and the recipe has now been applied under three groupings (section 7,
  decision 9). Section 9 lists every number those looks produced.
- ADOPTED. On evidence that no fitted value of the recipe enters: the
  cell-by-cell match of the source figure (section 3), the Delta7
  instance names, and the anatomy. Anatomy alone excludes the registered
  pooling and does not choose between the two neighbour pairings (the
  anatomical tile is the OTHER one, L_k with R_(10-k)). The figure is what
  chooses.

**What still is an assumption.**

- ASSUMPTION: MaleCNS instance labels number the bridge glomeruli as the
  literature does (1 medial to 8 lateral, per half). What it would take to
  check it directly: morphology, which we do not load. What we have
  instead: the measured adjacency in section 1 and the figure match in
  section 3 are what that numbering predicts. What breaks if it is wrong:
  every position bar, decoded angle and ring statistic.
- ASSUMPTION: which bridge half MaleCNS calls L. Adjacency does not pin it.
  Datasets differ on it (Turner-Evans et al. 2020 note that the FAFB
  bridge labels are flipped relative to the hemibrain's). A wholesale swap
  of L and R reflects the amended ring (index i becomes (1 - i) mod 16)
  and leaves every unit pair unchanged, which is a unit test. No
  registered bar depends on a rotation sense, so nothing here rests on it.
  A statement about clockwise or counterclockwise in the fly would.
- ASSUMPTION (AC-B1a): that the source paper's units are the L_k with
  R_(9-k) pairs. The paper does not say so in words. Section 3 measures
  that its figure is drawn that way.
- Glomerulus 9: no EPG cell carries it (the four L9 and R9 cells are type
  EPGt, which exact type matching excludes), so no rule about it can move
  any result. For completeness the amended functions treat it as
  glomerulus 1 of the same half. That is Hulse et al.'s convention for the
  phase of bridge glomerulus 9. It is not where the EPGt cells arborize
  (their wedges lie between the glomerulus-8 and glomerulus-1 wedges), so
  the rule would have to be revisited before any instrument selected EPGt.

## 5. Scope

Every script in the repository that carried the map, and what its recorded
outcome was. All recorded outcomes below were produced on the reflected
left half-ring.

| Instrument | Hypothesis | Recorded outcome (registered map) | Re-run |
|---|---|---|---|
| `scripts/arenas/cx_biswas_killtest.py` | H-CX-BISWAS-FITTED | PASS 2026-10-31: r_a 0.4221 and 0.2132, canary fired, A_Delta=4 no valid fit, 0 of 3 rewires fit | yes |
| `scripts/arenas/cx_topology_killtest.py` | H-CX-RING-TOPOLOGY (Stage A) | PASS 2026-10-10: bandedness 0.5881 against null maximum 0.3376, mirror-peak 0.01445 against 0.00792 | yes |
| `scripts/arenas/cx_topology_nulls2.py` | H-STAGEA-NULL-DECOMPOSITION | Readings 2026-10-28: both weight families separate, sign family does not | yes |
| `scripts/arenas/cx_heading_killtest.py` | H-CX-HEADING-LATENT (Stage B, class 1) | BLOCKED 2026-10-10 at the precheck: retention 0.0000, circular variance 0.661 | only on a Stage A PASS |
| `scripts/arenas/cx_seeding_killtest.py` | H-CX-SEEDING-PROTOCOL (class 1) | KILL 2026-10-11: 0 of 8 real cells | only on a Stage A PASS |
| `scripts/arenas/cx_class3_killtest.py` | H-CX-CLASS3-COMPASS | KILL 2026-10-11: G1 at best 2 of 8, G2 false at all six points | only on a Stage A PASS |
| `scripts/benchmarks/cx_ring.py` | H-MODULE-VERDICT, class-1 ring benchmark | 2026-09-29: C1 0 of 21. C2 pass flag at 7 of 21, which the registry records as "4/21 live" | yes |
| `scripts/benchmarks/fc2_eb_ring.py` | H-MODULE-VERDICT, class-2 ring benchmark | 2026-09-29: fail, 0 calibration passes in 210 configurations | yes |
| `scripts/cx_scratchpad_premise.py` | H-CX-SCRATCHPAD | 2026-09-27: registered kill condition not met (0.85 against 0.6); closed refuted on the settle map, with the darkness accuracy (0.5) as its confirmation | yes, both modes |

**Not re-runnable.** The 2026-09-25 runs behind H-CX-RING-ATTRACTOR and
H-CX-CALIBRATION came from scripts that were never in git
(`task9_cx_latent/reopening_delta.md`). Their circular variances and
rotation signs are decode values. Which map they used cannot be read from
the repository. Their 2026-09-25 numbers get a dated note and nothing else.
The 2026-09-27 reinterpretation recorded on H-CX-RING-ATTRACTOR is decided
by rule P (section 10, item 9).

**Out of scope, with the reason.** `scripts/arenas/fb_topology_killtest.py`
(H-FB-COLUMNAR-TOPOLOGY) does not use this map. It has its own
glomerulus frame in which the two halves already run in opposite
directions, and its bar 1 uses no left or right label. The registered
wording of AC-FB2 says PFN glomeruli "sit in Stage-A's PB frame", which
was never true of the code. That wording gets a dated note. A separate,
unmeasured HYPOTHESIS about bar 2's frame direction is recorded in
section 14. It is not part of this amendment.

## 6. What changes and what does not

**Changes.** One thing: the function from an EPG bridge label to a ring
position.

- The map lives in one module, `src/flygi/compass_map.py`, which imports
  only the standard library. Five scripts call it where each used to type
  an inline expression (Stage B, class 3, the class-1 and class-2 ring
  benchmarks, the scratchpad script). The seeding probe, which had a
  second inline copy, now takes it from Stage B by import. Stage A and the
  Biswas instrument call it from the named function each already had. The
  null decomposition, which never had a map of its own, passes the choice
  through to Stage A.
- The map is a REQUIRED argument at every level. Nothing defaults to a map
  except the command-line flag, so a call that forgets it raises.
- Each script takes `--ring-map`. `amended` is the default. `registered`
  is the frozen expression and reproduces the registered run.
- Each script records the map in its JSON, and in its log where it writes
  one (three of the nine only print), and writes to a new default path
  (`<name>.amended_map.json`, or `<name>.registered_map.json` for a re-run
  of the registered path). The registered result files are not written by
  default any more (section 12). The scratchpad script's two modes used to
  share one default path. Each has its own now.
- A test fails if the frozen expression reappears VERBATIM in any script or
  module, if a map-carrying call omits the map, or if a flag-driven script
  hard-codes a map name. It does not catch a re-spelling of the rule or a
  call through an alias.
- In the script headers the frozen preregistration text is untouched and a
  dated AMENDMENT block is appended. Below those blocks, a few sentences
  that are not registration text were rewritten in place and are not
  bracketed: each header's "Output:" or "Writes" line, the docstrings of
  `wedge_index` and `epg_unit_from_instance`, and one code comment in the
  Stage B instrument.
- **Code text this file supersedes.** The nine instrument files and the
  helper were last edited at 03:54 Pacific, before the cell-by-cell figure
  measurement was reproduced in this repository (a reviewer's
  agent-reported reading of the figure had arrived at about 03:49), and
  were not edited afterwards, so that the registered-path reproductions of
  section 11 stay valid for the frozen files. The non-decisional C2 script
  and `scripts/arenas/compass_map_check.py` were last edited at 03:57, and
  `scripts/arenas/biswas_fig1g_check.py` at 04:02; no instrument imports
  any of the three. Two of their sentences are
  therefore weaker than section 3: the AMENDMENT block of
  `scripts/arenas/cx_biswas_killtest.py` says the grouping's "membership is
  inferred from the sizes", and the docstring of `src/flygi/compass_map.py`
  calls membership INFERRED. Section 3 supersedes both. One older sentence
  is wrong and is also left as frozen text: the docstring of `mirror_peak`
  in `scripts/arenas/cx_topology_killtest.py` says the statistic is
  "nonzero only when the hemispheres concentrate coupling at OPPOSITE
  offsets". It is not (section 8, C6). Two more sentences overstate and
  are also left as frozen text. The AMENDMENT blocks of seven instrument
  headers say the amended angles are "the wedge angles printed in Hulse et
  al. 2021 Fig. 16B", the helper's docstring says that figure "prints the
  wedge angles this map uses", and the `ring_map_description` string the
  helper writes into every amended JSON ends "Angles as printed in Hulse et
  al. 2021 Fig. 16B." The figure prints four of the sixteen; the other
  twelve come from the order read from it (section 3). And the helper's
  docstring says that until 2026-11-21 "nine scripts each carried their
  own copy" of the registered expression: eight did, because the null
  decomposition never had one.

**Does not change.** Everything else, in every instrument:

- every pass bar, kill rule, BLOCKED floor and verdict rule
- every null, every seed, every count of nulls
- every regime, grid, protocol, write angle, seed angle and duration
- how PEN cells are split (by side letter alone, as before)
- the Biswas recipe, both fits, the validity conditions, the cluster cap
  of 10, the tie rule, the G1 test and the published-value cross-check band
- the validation gates

The one status rule this file does change is the scratchpad's (section 7,
decision 11).

## 7. Decisions recorded with this amendment

1. **The A_Delta = 4 validity condition stays as registered** (B-R9:
   denominator positivity on all eight rows). Changing which rows a
   validity condition covers is a change to the verdict logic, which this
   amendment does not touch. Section 14 records the open question it
   raises. A_Delta = 4 is not needed for a PASS.
2. **The null bar stays at three rewires** (seeds 4242 to 4244). A larger
   reading is added as non-decisional context (section 8, C2).
3. **One eight-unit grouping**, L_k with R_(9-k). The instrument does not
   run the other pairing. One declared convention per test, no sweeps.
4. **The sixteen-position map has no free parameter** (section 4).
5. **One helper.** The registered expression survives in exactly one
   place, as the `registered` branch.
6. **Stage B is re-run as the same registration**, under its own change
   rule (an instrument-bug finding and a full re-run). This is not one of
   the "reopening paths" its close note lists, which each need a new
   registration. No protocol, regime or bar is changed.
7. **Each amended instrument runs once, against the freeze.**
   `scripts/arenas/run_amended_once.sh` runs every amended instrument and
   enforces the following. The guarantee covers runs made through it, and
   rests on the operator never calling an instrument directly with the
   amended map, its default. A direct call with `--ring-map registered`
   writes only `<name>.registered_map.json`; it is the reproduction path of
   section 11 and cannot touch an amended slot.
   - *The eleven commands, verbatim.* It accepts only the eleven instrument
     commands of section 11, with no argument except `--settle-map` on the
     scratchpad script. No run through it can change the map, the output
     path, the grid, the trials or the config.
   - *Against the freeze.* It refuses to start unless every tracked file
     other than WORKLOG.md is identical to the tag
     `compass-map-freeze-20261121` and no untracked file sits under src/,
     scripts/, configs/, tests/ or docs/. If git cannot make either
     comparison, it refuses as well.
   - *Pinned inputs.* It refuses to start unless every file listed in
     `scripts/arenas/run_amended_once.inputs.sha256`, frozen with this
     file, matches its SHA-256: the eleven files of the compiled runtime,
     the raw MaleCNS pair table from which six of the eleven commands
     rebuild every synaptic weight, and the capture file (section 11).
   - *The Stage A gate* (decision 10). It refuses Stage B, the probe and
     class 3 unless a Stage A record has the line `VERDICT: PASS`.
   - *One run at a time.* It holds a lock for the whole run and refuses a
     second launch while one is going. A lock left by a wrapper that was
     killed is reported, not overridden, and is removed by hand once the
     instrument whose process ID it holds has exited.
   - *Prerequisites and resources first.* It checks the compiled runtime;
     that numpy, scipy, pandas, pyarrow and PyYAML import under the
     instrument's own environment (their versions go into the record); the
     capture file where one is read; and at least 1 GiB of free disk and at
     least 25% of system memory free. All of it is checked before it
     creates a record.
   - *An explicit environment.* The instrument runs with only PATH, HOME,
     `PYTHONPATH=src` and `PYTHONDONTWRITEBYTECODE=1` set, and the record
     says so. MEASURED at 14:22 Pacific on 2026-11-21, in a shell started
     the way the registered-path reproductions' shell was (this session's
     tool shell), with
     `env | grep -E '^(PYTHON|NPY_|OMP_|OPENBLAS_|MKL_|VECLIB_|FLYGI_|KAGGLE_|LANG=|LC_|LD_|DYLD_|VIRTUAL_ENV|CONDA)'`:
     only `PYTHONDONTWRITEBYTECODE=1` is set. That it was the same at
     04:02 is assumed.
   - *Once, keyed on the instrument.* Each record is named after its
     instrument, not by the operator. A first attempt is refused if the
     instrument already has a record (unless test 3 calls it a
     prerequisite exit, which is set aside first) or an amended-map output
     on disk.
   - *Finished, and the other classes, by ordered tests.* The wrapper
     decides each attempt by tests on its record's own lines, applied in
     this order, the first that matches deciding. A record can carry the
     marks of two classes (a traceback in a record with no exit status,
     for example), and the order settles it. These are the tests of the
     wrapper's `classify()`.
     1. *Finished*, an outcome: a line beginning `VERDICT: `, `BLOCKED: `
        or `BLOCKED (`; or, for the six instruments that print no verdict
        line (the C2 context nulls, the null decomposition, the two ring
        benchmarks and the scratchpad script's two modes), the wrapper's
        lines `# JSON written: ` and `# exit status: 0`, which it writes in
        that order once the instrument has exited. A record without both
        has not finished, whatever is on disk: an instrument whose wrapper
        was killed can still exit 0 and write its JSON, but its exit
        status is then never recorded. So if the wrapper is killed during
        a run, a verdict-line instrument whose verdict line still reaches
        the record has finished, and one of these six has not. Nothing that
        happens after an attempt has finished, an interrupt included,
        changes it.
     2. *Failure to finish*: a line beginning `# WATCHDOG KILL` (resident
        memory above 9 GB) or `# RESOURCE STOP` (free disk below 512 MiB or
        system memory free below 5% during the run), whatever else the
        record shows.
     3. *Prerequisite exit*: a line beginning `BLOCKED -- `, the line
        `# exit status: 3`, and no line beginning `# WRAPPER INTERRUPTED`.
        The instrument printed `BLOCKED -- ... cannot run here` and exited
        before opening its log, having computed nothing. It is neither an
        outcome nor a counted attempt: the record is set aside and the slot
        stays free. The wrapper that ran it sets it aside; if that wrapper
        died first, the next launch that takes the lock does, before it
        reads any record for its once-only checks, and says so in
        `launch.log`.
     4. *Abandoned after partial output*: a line beginning
        `# WRAPPER INTERRUPTED`, or no line beginning `# exit status: `, or
        exit status 129, 130, 131 or 143 (the instrument stopped by HUP,
        INT, QUIT or TERM). The attempt was stopped from outside before it
        finished, and the wrapper cannot tell by whom or what: an operator,
        a shutdown that signals the wrapper, or a crash of the machine. It
        earns no re-run.
     5. *Failure to finish*: anything else, such as an uncaught Python
        exception (a traceback and exit status 1), a native crash, or a
        SIGKILL of the instrument with no marker (exit status 137), which
        cannot be told apart from the system's own memory kill. It earns
        one re-run.

     So a traceback with no exit status is abandoned (test 4), and a
     watchdog kill or resource stop with no exit status is a failure to
     finish (test 2). Stopping a run before the instrument finishes, by
     TERM to the wrapper or to the instrument, by INT to the wrapper, or by
     HUP (INT and HUP only where the launch does not ignore them), abandons
     it; a SIGKILL or any other signal that kills the instrument is a
     failure to finish. The instrument itself ignores INT and QUIT, because
     bash starts it in the background, and HUP as well under the launch of
     section 11. The wrapper acts on a signal at its next check, within
     about 2 s: an interrupt is recorded only if the instrument was still
     alive then, and a signal it acts on after the instrument has exited
     changes nothing and is noted in `launch.log`; a signal that arrives
     while the trailer is written, or one the wrapper inherited as ignored
     (HUP under nohup), is neither acted on nor logged. The wrapper writes
     the class into the record. A record whose wrapper died has none, part
     or all of its trailer. It is not read, hashed or classified until its
     instrument (the process ID in the lock) has exited, and it is then
     classified by the same tests, in the same order. ASSUMPTION: the machine is not restarted, shut down or crashed
     during a run; any of those would leave an abandoned attempt.
     Automatic installation of macOS updates is on (MEASURED at 14:25 with
     `defaults read /Library/Preferences/com.apple.SoftwareUpdate
     AutomaticallyInstallMacOSUpdates`, which prints 1); the machine had
     been up since 2026-09-06.
   - *One re-run, only after a failure to finish, and as the next launch.*
     `--rerun` repeats the same command once, and only when the first
     record is a failure to finish whose command line is that command. The
     first attempt's outputs are moved, not overwritten. The re-run is the
     next launch: while any instrument's first record is a failure to
     finish and it has no re-run record, the wrapper refuses the first
     attempt of every other instrument (exit 90). It classifies each record
     by that record's own instrument, so a record whose wrapper died counts
     too. A failure to finish that is not re-run, because the runs stop or
     the outcomes are recorded before it is, is read as two failures to
     finish. The operator will have seen the failed attempt's partial
     output, and a SIGKILL of the instrument is recorded as a failure to
     finish, so declining the re-run gains nothing that stopping the
     attempt would not have: a re-run not taken is read as no verdict, as
     an abandoned attempt is (section 10). After the settle map, the last
     command of the order, exit 90 has no other first attempt left to
     refuse, so there the re-run is held only by the order and by that
     reading. A second failure to finish is "no verdict". Section 10 says
     how abandoned and no-verdict runs are written; neither is ever
     written as a clean "no verdict".
   - *Detached and logged.* Each run is launched detached from any
     terminal or tool call, in a session of its own (section 11 gives the
     command), so that no signal sent to the launching shell's process
     group reaches it. The wrapper writes every refusal, with its reason,
     and every start and end to
     `results/arenas/amended_runs_20261121/launch.log`, where each launch
     is checked. The operator waits for one run to end before starting
     the next.

   The wrapper was tested in throwaway repositories with stub instruments,
   by 204 scripted checks kept outside the repository: every
   reachable refusal path except the record-creation race (the runtime and
   capture presence checks are reached only through the pinned-hash
   check), including a git diff failure and a git ls-files failure; each classification, including an instrument stopped by TERM
   from inside and from outside and one killed by SIGKILL; six records
   that fit two classes, written by hand, each decided by the ordered
   tests; a wrapper killed while a no-verdict instrument runs on to exit 0
   with its JSON (abandoned) and one killed as soon as the exit status is
   written (finished, no re-run); a TERM that reaches the wrapper after
   the instrument has crashed, made its prerequisite exit, or finished
   (nothing changes, and `launch.log` notes it); a prerequisite exit
   left in place by a wrapper that died, on a first attempt and on a
   re-run, set aside at the next launch (and an owed re-run still the next
   launch); the gate; the lock, a stale lock and two launches
   0.3 s apart; a changed input and a missing pinned-input list; a freeze
   check that git cannot make; the explicit environment, and the package
   check made under it; the launch log; a re-run after a traceback, a
   native crash, a missing JSON, a SIGKILL, a watchdog kill and each
   resource stop (with the thresholds lowered in the throwaway copies
   only); a failure to finish holding every other first attempt until its
   re-run, and a second failure, an abandonment and a prerequisite exit
   not holding it; interrupts of the wrapper by TERM, by HUP and by
   killing it; and the launch of section 11, in a session of its own,
   finishing after the shell that started it had exited. All passed. A
   subset of these cases is in the suite as the 37 tests of
   `tests/test_run_amended_once.py`.
   **Between runs.** After each run, its console record, its JSON and its
   log (each where it exists) are hashed with SHA-256, and those hashes go
   into WORKLOG.md with the printed result lines. That one file is
   committed alone with `[skip ci]` before the next run starts. That is
   why WORKLOG.md is the one file the wrapper lets differ from the freeze.
8. **The base rate does not move.** No compass registration is
   score-adjacent, so the counter stays at 0 for 16 whatever the outcomes.
9. **"Applied once" no longer holds, and the close sentence says so.** The
   frozen recipe text reads "applied ONCE to our compiled counts, no
   retuning", and the hypothesis statement, premise and frozen close say
   "applied once". Regrouping the EPG cells changes no fitted quantity and
   no recipe step. But the recipe's output was compared with the published
   values under three groupings before one was adopted, so this file does
   not claim that either half of the clause still holds. The replacement
   close sentence for a PASS, written now: "Given fitted per-type
   physiology, the Biswas recipe applied to our MaleCNS counts under the
   amended EPG grouping gives an EPG-Delta7 realization that holds a
   position-faithful bump at [the configurations that pass], and none of
   the three registered degree-preserving rewires passes where it does."
   "Position-faithful" is kept only if every write of the Biswas set
   follows (section 8, C7). Otherwise "holds a position-faithful bump"
   becomes "holds a bump that meets the registered G1 position clause",
   and the final angles are quoted. If the run shows no valid fit on any
   rewire at any configuration, the last clause becomes "and none of the
   three registered degree-preserving rewires admits a valid fit at any
   configuration". The sentence goes on, each bracket filled from the
   run's JSON: "The recipe has been looked at under three EPG groupings in
   all. The instrument returned PASS under the registered grouping on
   2026-10-31. Applied by hand to the per-configuration results of an
   unregistered in-memory check, the verdict rule gives PASS under the
   other two as well. So across the three groupings tried the verdict is
   the same. The r_a values are not. Under the amended grouping this run
   gives r_a [`ra_cross_check.8.fitted_ra`] at A_Delta 8 and
   [`ra_cross_check.6.fitted_ra`] at A_Delta 6 (published 0.548 and
   0.437), and at A_Delta 4 [no valid fit, or a valid fit with r_a
   `ra_cross_check.4.fitted_ra` (published 0.391), as
   `real.configs.4.valid_fit` says]. The unregistered check gave 0.5480,
   0.4373 and no valid fit at A_Delta 4 under the amended grouping, and
   0.5510, 0.4836 and 0.3970 under the other neighbour pairing, within the
   registered 0.1 band at all three. The amended grouping was first
   noticed through its agreement with the published values at A_Delta 8
   and 6 in that check." A configuration with no valid fit in the run is
   named as such in its bracket. If C2 finds m above 0, the first sentence
   ends, after "passes where it does" (or "at any configuration"), with
   "; m of n further rewires (seeds 4265 to 4464) pass G1 at some
   configuration" (section 8, C2).
10. **The Stage A gate covers all of Task 9's dynamics.** The frozen text
    says a Stage A KILL "closes Task 9 with no dynamics built" and closes
    H-CX-HEADING-LATENT "not-pursued". The seeding probe and the class-3
    test are Task 9 instruments that exist only because Stage A passed. So
    all three (Stage B, the probe, class 3) are re-run only if Stage A is
    PASS under the amended map, and the wrapper refuses them otherwise
    (decision 7). The class-1 and class-2 ring benchmarks and the
    scratchpad script are not Task 9 instruments and are re-run whatever
    Stage A returns.
11. **The scratchpad's structural rule is replaced for status purposes.**
    The settle-map probe of 2026-09-27 carries this rule, in a code comment
    written after the first runs: "If the settled angle is independent of
    the write angle, the compiled ring sustains ACTIVITY but not POSITION
    -- a single fixed attractor, no memory substrate -- and H-CX-SCRATCHPAD
    is refuted structurally, visual drive unneeded." The hypothesis was
    closed "refuted structurally" by it, with the darkness accuracy as
    confirmation. The rule is qualitative and has no threshold. Read
    literally it was not even met on 2026-09-27: the settled angles took
    several values (90.0, and 198.5 to 222.7), not one. Its substance, that the ring does not return the
    written bit, is what the darkness arm of the same script measures. So
    for status purposes it is replaced by D (darkness accuracy at N = 50 at
    or below 0.6, section 10 item 9). The 0.6 threshold is the registered
    kill threshold, registered for the visual arm and applied here to the
    darkness arm, which the registration calls its "measured-positive
    replication arm". Applied to the 2026-09-27 record, D returns that
    record's own status (section 10). The structural rule's other use, the
    reinterpretation recorded on H-CX-RING-ATTRACTOR, is decided by rule P.
12. **Statements broader than their bars are narrowed on a PASS.** Five
    registry statements claim more than their bars measure.
    H-CX-RING-TOPOLOGY claims "opposite-signed left/right PEN_a offsets
    (the shifter)", which bar 2 does not show (section 8, C6).
    H-CX-CLASS3-COMPASS claims an "8-angle position continuum",
    H-CX-HEADING-LATENT a "heading CONTINUUM" and H-CX-SEEDING-PROTOCOL a
    "position-faithful" bump, and their position clauses can be met by a
    few fixed points (section 8, C7). H-CX-BISWAS-FITTED says "their
    published recipe applied once to our counts", which decision 9 no
    longer claims, and "a position-faithful heading bump", whose G1 clause
    is the class-3 clause verbatim and can be met the same way. On a PASS the verdict follows the bar, and the
    statement is narrowed, dated and in place, to what the bar measured:
    by the rules of C6 and C7, and for H-CX-BISWAS-FITTED by replacing
    "applied once to our counts" with "applied to our counts (looked at
    under three EPG groupings; amendment section 7, decision 9)" and,
    unless every write of the Biswas set follows (C7), "sustains a
    position-faithful heading bump" with "sustains a heading bump that
    meets the registered G1 position clause". The
    original wording is quoted verbatim in the dated bullet that records
    the narrowing.

## 8. Non-decisional context readings and wording rules, pre-stated

None of these can change a verdict.

- **C1, Stage A's blind ordering residual. Reported, with no reading.**
  Three reasons. Its value under a corrected order had already been
  agent-reported as 6.6 degrees before this file was written (section 9),
  so no band set now would be a test. On a perfect ring the value moves
  between 0 and 11.25 degrees with the eigensolver. And a reviewer's
  synthetic rings built with the fly's PEN geometry read about 7 to 34
  degrees under the RIGHT map and 45 to 51 under the wrong one
  (agent-reported, synthetic), so a cut as low as 22.5 would misfire on a
  right map and only a cut close to 45 could separate the two. The number
  is reported as it comes.
- **C2, more rewires for the fitted compass.**
  `scripts/arenas/cx_biswas_context_nulls.py` runs the instrument's own
  recipe on 200 further degree-preserving rewires, seeds 4265 to 4464,
  none of which has been looked at. The seeds are constants of the script,
  not flags. Reported as "k of n admit a valid fit at some configuration"
  and "m of n pass G1 at some configuration", where n leaves out any
  rewire on which the recipe raises (those are listed by seed). Any m
  above 0 is reported as a limit on the wiring-specificity sentence, in
  the fixed form decision 9 gives.
- **C3, the published-value cross-check.** Still reported with the
  registered sentence (within 0.1 is "consistent with their realization").
  On an amended run it is NOT an independent canary (section 9). A PASS is
  still never reported as a reproduction of their numeric realization.
- **C4, registered-path reproduction.** Run BEFORE this freeze, on the
  frozen instrument files: every instrument with `--ring-map registered`.
  Results in section 11.
- **C5, A_Delta = 4.** The instrument's JSON lists every candidate root and
  the first validity check it fails. That list is reported as it comes.
- **C6, what a Stage A PASS may be said to show.** Bar 2 is
  S = max over d = 1, ..., 7 of max(q_L(d) q_R(-d), q_L(-d) q_R(d)). It passes when
  p = (1 + the number of rewires with S at or above the real value)/201 is
  below 0.05, so up to 9 of the 200 rewires may sit at or above the real
  S. S is large for any two offset profiles that put mass at a mirrored
  pair of offsets, including identical, symmetric ones that do not lean
  either way; that is a property of the 2026-10-10 statistic, not of this
  amendment. And under the amended coordinates an offset of one position
  can arise from tile geometry alone (the left wedge always sits on the
  same side of its tile), with no PEN phase shift needed. That is INFERRED
  from the map, bridge: that PEN-mediated EPG to EPG coupling follows the
  anatomical tile, L_k with R_(10-k); a reviewer's synthetic rings agree
  (agent-reported). MEASURED on the
  2026-10-10 record: bar 2 passed (p = 1/201) while all four argmax
  offsets were 0 and both PEN_a mean offsets had the same sign (-0.198
  and -0.158). So a Stage A PASS is worded literally, with both p values
  as the JSON records them (`p_banded` and `p_mirror_peak`) and k =
  201 x `p_mirror_peak` - 1, the number of the 200 rewires at or above the
  real S (the JSON keeps only the null maximum, and p is (1 + k)/201):
  "the PEN-mediated EPG to EPG coupling is banded on the ring (p = ...
  against 200 degree-preserving rewires), and the left and right PEN_a
  halves put more joint mass on a mirrored pair of offsets than at least
  191 of those 200 rewires (k of 200 at or above it; p = ...)". It then
  adds exactly one clause, chosen by `real.offsets.PEN_a_L.mean_offset`
  and `real.offsets.PEN_a_R.mean_offset` in the JSON, and quotes both
  values in it:
  - if either is exactly 0: "a PEN_a mean offset is 0 (a and b); opposite
    lateralisation is not shown";
  - otherwise, if their signs are opposite: "and the two halves lean in
    opposite directions (mean offsets a and b), which the amended tile
    geometry alone could produce (inferred); a PEN shift is not separated
    from it";
  - otherwise: "both PEN_a mean offsets have the same sign (a and b);
    opposite lateralisation is not shown".
  Apart from the caveat in the second clause, it never says "shifter" and
  never claims a PEN shift. Tile geometry alone could produce opposite
  offsets of about one position (inferred, as above). A reviewer's
  synthetic rings
  give larger mean offsets with a PEN shift than without one
  (agent-reported), but no registered output of this instrument separates
  the two. The statement of H-CX-RING-TOPOLOGY is narrowed to the same
  words (decision 12).
- **C7, position clauses and fixed points.** The registered position
  clauses accept a settled angle within 45 degrees of the write angle, 45
  included, at write angles 45 degrees apart (class 3) or 90 apart (Stage
  B, the probe). A few fixed points can meet that. A remnant confined to
  one label decodes at exactly that label's angle. Under the amended map
  the class-3 write angles are the eight right-label angles, 45 degrees
  apart, so a remnant at one of them is within 45 degrees, inclusive, of
  three writes, and two such remnants 180 degrees apart could meet G1 at 6
  of 8. The seed angles of Stage B and the probe are four right-label
  angles 90 degrees apart, and a right-label remnant between two of them
  (R4 at 157.5, for example) is exactly 45 degrees from both.
  Single-label remnants are real: in the registered seeding record, at
  gain 2.0, the 112.5 write settled at exactly 90.0 with circular variance
  0.000. The verdicts follow the bars. The wording follows this rule.
  - *Follows.* Within a stated set of writes, a write follows when (a)
    its settled angle is within 22.5 degrees (one ring position) of its
    own write angle, 22.5 included, the distance rounded to 0.01 degrees,
    and (b) no other write of the same arm at the same cell, grid point or
    configuration (on the settle map, of the same write style) whose bump
    survived, whether or not it is in the set, settled within 11.25
    degrees (half a position) of its settled angle, 11.25 included, the
    distance rounded to 0.01 degrees, so one remnant cannot serve two
    writes. Distances are circular and are computed from the angles as the
    record holds them. A bump survived when its circular variance is at
    most 0.6 and, where the instrument records retention, its retention is
    at least 0.05; on the settle map, which records only a mass, when the
    write is alive.
    - The 22.5 calibration write of Stage B and the probe counts in (b),
      though it belongs to no set. In the probe it is the 22.5 row of each
      cell. In Stage B it is the precheck write, the only 22.5 write whose
      settled angle is recorded (the rate-calibration and tracking writes
      record none). Its settled angle is the `angle` on the
      `precheck (cal 22.5)` line, as printed to one decimal (the JSON does
      not hold it), and it survived whenever the run got past the
      precheck. Without it (b) could not bind in Stage B: in a PASS every
      held-out write is within 45 degrees of its own seed, so a write
      within 22.5 degrees of its seed is at least 22.5 degrees from every
      other held-out write.
    - The settle map has one arm, one operating point and no cells or grid
      points, so its write style takes the place of the cell, as the
      protocol does in the probe's cells. The other style's writes do not
      count in (b), the one at the same angle included, because a ring
      that holds position settles a write and its twin in the other style
      at the same place.

    Rule (a) counts a settle onto the adjacent position. That matters
    because a single-label remnant decodes exactly on a label angle, and
    under the amended map the left-label angles sit exactly halfway between
    right-label angles 45 degrees apart, and the reverse, so a
    nearest-write rule would score a ring that moves every write half a
    step the same way as eight ties. Rule (b) is what stops a few fixed
    points from counting. Class 2 is not worded by C7: section 10, item 8
    quotes its settled angles, and its `c1_pass` is read from the JSON as
    `fc2_eb_ring.py` computes it, registered on 2026-09-29 (each seed's
    settled angle nearest its own seed, a tie going to the first seed in
    list order; `c1_pass` also needs held-out persistence and four
    clusters).
  - *The sets, fixed now.* Biswas: at each configuration the close sentence
    names as passing, every G1 row of the REAL arm that passes G1's
    per-seed rule (finite, retention at least 0.05, circular variance at
    most 0.6, PVA error within 45 degrees); a row's write angle is its
    `seed_pva_deg` and its settled angle its `final_pva_deg`. Stage B: the
    three held-out writes of the REAL arm. The probe: in each decisive
    cell, every held-out write of the REAL arm that passes the cell's
    per-angle rule (retention at least 0.05, circular variance at most 0.6,
    settled angle within 45 degrees). Class 3: at each decisive grid point,
    every write of the REAL arm that passes the same per-angle rule. Class
    3 has no calibration write; its 22.5 write is a G1 write, and is in its
    set when it passes the per-angle rule, like the other seven. Rewired arms, cells, grid points and configurations that are not
    decisive or not passing, and the 22.5 calibration write of Stage B and
    the probe, belong to no set.
  - *The wording.* A PASS of Biswas, Stage B, the probe or class 3 is
    described as position-following, and its statement keeps "continuum"
    or "position-faithful", only if every write of every set follows.
    Otherwise the PASS sentence says "meets the registered position
    clause" (for Biswas, "meets the registered G1 position clause") and
    quotes the final angles, and the statement is narrowed to the same
    words (decision 12).

## 9. Disclosure: what had been seen before this freeze

Everything that could bias the amendment, stated plainly. Times are Pacific
on 2026-11-21.

1. **00:02 to 00:30, two fact-check subagents** of this session, checking
   the draft outreach emails, looked at corrected orderings.
   - The first (the compass-and-preprint emails) wrote and ran six
     unregistered scripts between 00:02 and 00:21. They fitted the Biswas
     recipe in memory under three groupings with the instrument's own
     functions: the registered grouping, L_k with R_(9-k), and L_k with
     R_(10-k). They also ran 20 extra rewires (4245 to 4264), lifted the
     cluster cap, examined the A_Delta = 4 root, read the unit sizes of the
     paper's Fig. 1g, and compared the count profile with the paper's Fig.
     5d. One script, `null_cap_check.py` (the registered grouping with the
     cap lifted), was run only by that subagent and its output was not
     kept.
   - The second (the flyvis and MaleCNS emails) fitted the recipe under
     L_k with R_(9-k) on the real graph and the three registered rewires
     and reported r_a 0.548034 and 0.437279, no valid fit at A_Delta = 4,
     and none on the rewires. It also reported that under an ordering with
     L_k next to R_(9-k) the Stage A bandedness is 0.8505, the blind
     ordering residual falls to 6.6 degrees, and the maximum over 200
     rewires is 0.334, computed in memory with the Stage A script's own
     functions on the registered seeds. That ordering is a whole-ring
     reflection of the amended index, to which bandedness and the residual
     are invariant. It gave Delta7 input-profile correlations of each L_k
     group with R_(9-k) (0.57 to 0.88, against -0.18 to 0.42 for R_k). A
     reviewer found in its transcript that it had also scored a second
     candidate order (0.655, 26.9 degrees) and did not report it.
   - I did not reproduce the Stage A numbers. CONSEQUENCE: Stage A's bar 1
     is effectively known, and the amended Stage A run is CONFIRMATORY for
     bar 1. Only bar 2, the mirror-peak, is unseen. C1 is not a blind
     reading.
2. **00:41 to 00:45, I re-ran five of the first subagent's six scripts,
   all but `null_cap_check.py`** (the
   WORKLOG entry of 1:00 AM; outputs kept under
   `results/arenas/unregistered_checks/epg_lr_pairing_20261121/`). Under
   L_k with R_(9-k): r_a 0.5480 and 0.4373 against the published 0.548
   and 0.437, G1 8 of 8 at both, Delta7 unit sizes 5, 6, 4, 6, 6, 6, 4, 5,
   no valid fit at A_Delta = 4 under the registered all-rows condition (a
   root whose active-row-only r_a is 0.3909, published 0.391, is rejected
   by that condition), and no valid fit on rewires 4242 to 4244 or on the
   twenty extra seeds. Under L_k with R_(10-k): r_a 0.5510, 0.4836 and
   0.3970, valid with G1 8 of 8 at all three configurations, no valid fit
   on rewires 4242 to 4244. Under the registered grouping, on the twenty
   extra seeds, one rewire (4257) had a valid A_Delta = 8 fit that failed
   G1 0 of 8. CONSEQUENCE: the amended Biswas outcome had been computed
   three times before the freeze: by two subagents of this session and by
   the session itself. The amended Biswas run is
   CONFIRMATORY, its r_a agreement is not independent evidence for the
   grouping, and the grouping was found through the published values
   (section 4).
3. **Between 02:30 and 04:00, before the freeze**, I measured the
   map-against-wiring numbers of section 1 and the figure comparison of
   section 3. Both use the direct EPG to EPG counts. The Biswas
   instrument's C_EE block is built from the same counts. Stage A's
   statistic is the two-hop coupling through PEN and is a different
   quantity. Both checks were re-run once on their final file revisions at
   10:37 and reproduced their results exactly.
4. **Between 02:58 and 04:45, before the freeze**, every instrument was run
   with `--ring-map registered` (C4, section 11). These are reproductions
   of recorded outcomes on the registered map. They show nothing about the
   amended map.
5. A pure-arithmetic illustration (no network, no data) showed that under
   the registered map a bump with both halves active decodes near 180
   degrees or its opposite wherever it really is. It predicts nothing
   about any re-run. It is used for one thing: the class-3 close sentence
   ("the compiled MaleCNS CX synapse counts do not carry the compass in the
   STANDALONE 148-neuron circuit", held in EXPERIMENTS.yaml) is held, not
   quoted as a result, until the re-run (section 10, item 6).
6. The reviewers' synthetic-ring analyses behind C1 and C6 are
   agent-reported and synthetic. They changed wordings here and no bar.
   In the second review a reviewer also executed the never-run code paths
   of Stage B, the probe, class 3 and the context-null script on
   synthetic graphs (no real data) to look for crashes. It found none.
7. **Three plumbing checks on real data, with no result computed.** The
   null-arm code of Stage B, the seeding probe and class 3 has never
   executed on real data, because it runs only when a real arm passes.
   Before the freeze I checked that it can run at all. Each check wrote no
   bump, decoded nothing and printed only whether the build succeeded.
   (a) One `cx_block_rewire` call on the full graph with a non-registered
   seed, timed and measured for memory (3.9 s, 2.38 GB). (b) A rate
   network built from that rewired graph and stepped once at gain 1.5 and
   2.0, and the class-3 engine built on a rewired subcircuit and stepped
   20 times. (c) The three rewired full graphs Stage B and the probe use,
   with the registered seeds 4242, 4243 and 4244, each built and given a
   rate network, with no step taken (17 to 21 s each, 2.07 GB peak). The
   rewired graph does not depend on the label map.
8. **Not seen by anyone:** any dynamics instrument under the amended map
   (Stage B, the seeding probe, class 3, the class-1 and class-2 ring
   benchmarks, the scratchpad script), Stage A's mirror-peak under the
   amended map, and the null-decomposition readings. A reviewer searched
   this session's transcripts and its subagents' for such runs and found
   none. Nothing outside this session was searched.

## 10. Order of runs and the pre-stated reading of every outcome

The registered-map outcome of each instrument stays in the record as
history, marked as produced on the reflected left half-ring. The
amended-map outcome becomes the standing result of the hypothesis, read by
the unchanged rule.

**Order.** Biswas, C2, Stage A, the null decomposition, then (only on a
Stage A PASS) Stage B, the seeding probe and class 3, then the class-1 ring
benchmark, the class-2 ring benchmark and the scratchpad script, main mode
then settle map. A re-run that a failure to finish earns comes straight
after it (section 7, decision 7). The amended runs close with the dated
WORKLOG entry that records their outcomes.

**Rules that apply to every instrument.**

- The record of an outcome is the console record, plus the log and the JSON
  where the script writes them. A verdict is a printed `VERDICT: PASS` or
  `VERDICT: KILL` line. A block is a printed line beginning `BLOCKED: ` or
  `BLOCKED (` (the second is Stage B's labelled rate guard), or the line
  `VERDICT: BLOCKED`, which is the Biswas instrument's form; several
  BLOCKED exits write no JSON. The six instruments that print no verdict
  line (the C2 context nulls, the null decomposition, the two ring
  benchmarks and the scratchpad script's two modes) have finished when
  their record has the wrapper's lines `# JSON written: ` and
  `# exit status: 0` (section 7, decision 7), and are read from their
  JSON, as below. The exit status alone is not the record: an uncaught
  exception also exits 1, the KILL code.
- What counts as finished, failed or abandoned is section 7, decision 7,
  by its ordered tests. The wrapper writes each attempt's classification
  into its record. A record whose wrapper died has none, part or all of its
  trailer; it is not read until its instrument has exited, and it is then
  classified by decision 7's ordered tests and hashed into the WORKLOG as
  it stands (a prerequisite exit it holds is set aside by the next launch
  that takes the lock, decision 7). A
  failure to finish (a crash, a watchdog kill or a resource stop) is not
  an outcome and earns one re-run, which is the next launch. A run that
  stops on the rate engine's error for a non-finite state counts as a
  crash: the engine raises on such a state, so the registered instability
  floor cannot be counted.
- A prerequisite exit (`BLOCKED -- ... cannot run here`, printed before
  the log opens, with nothing computed) is neither an outcome nor a
  counted attempt, and it is not read as a block. Several registrations
  list "runtime absent" among their BLOCKED floors. That floor says the
  instrument cannot run on the host, which is not a property of the
  hypothesis, and the wrapper checks the same prerequisites before any
  record exists.
- **Abandoned.** An attempt that decision 7's ordered tests classify as
  abandoned (its wrapper was interrupted, its instrument exited 129, 130,
  131 or 143, in practice stopped by TERM or by HUP, or its wrapper died
  without recording an exit, with no watchdog kill or resource stop
  recorded) is "abandoned after
  partial output", whoever or whatever stopped it: the wrapper cannot tell
  an operator from a shutdown or a crash of the machine. It earns no
  re-run and ends with no verdict. An attempt that has finished stays an
  outcome whatever happens to it afterwards.
- The non-decisional scripts (C2 and the two read-only checks) never
  change a status, whatever they return.
- **No verdict.** If an instrument returns BLOCKED, fails to finish twice
  (a failure to finish that is not re-run counts as two), is abandoned, is
  not re-run because the Stage A gate closed, or is not run to an outcome
  by the close of the amended runs, then the only verdict on record for
  its hypothesis is one measured on a mislabelled ring. The status becomes
  `invalidated`, the registry's word for a test later shown unsound, with
  the note saying why. When the outcome is two failures to finish or an
  abandoned attempt, the note quotes, beside the status word, every
  instrument output line of the attempt or attempts: the lines after
  `# ---- output ----` up to `# ---- end of output ----` or, where a
  record has none, to the end of the record as hashed into the WORKLOG.
  Where those run past 40 lines in a record, it gives that record's
  SHA-256 from the WORKLOG and quotes every one of its lines that contains
  a digit. A BLOCKED outcome is recorded with its BLOCKED line, and a
  closed gate with the gate's reason. So no such outcome reads as a clean
  "no verdict". Two exceptions. H-CX-HEADING-LATENT stays `null` as
  recorded on 2026-10-10 (that record's usage: untestable under the
  registered protocol). The two ring benchmarks feed H-MODULE-VERDICT, a
  program-level hypothesis over every module: for them, no verdict marks
  that benchmark's own ellipsoid-body ring entries of the 2026-09-29
  program (for class 1, its C1, C2 and visual-drive entries)
  `invalidated` in that record's note, and its status does not change.

**Per instrument.**

1. **Biswas (H-CX-BISWAS-FITTED).** PASS: status stays `supported`, the
   numbers become the amended ones, the close is the sentence of decision
   9, worded as C7 says, and the statement is narrowed as decision 12
   says. KILL: `refuted`. BLOCKED, including the registered "no valid fit
   at any configuration" floor: the no-verdict rule. Any difference from
   the unregistered check is reported in the brackets of decision 9's
   sentence. Whatever the outcome, the two 2026-10-31 sentences "our
   counts fit a DIFFERENT member of their realization family" and
   "count-export differences are a further unverified candidate", which
   describe the mis-grouped fit, are withdrawn, and the amended run's
   `ra_cross_check` is quoted in their place.
2. **Stage A (H-CX-RING-TOPOLOGY).** PASS: status stays `supported`, with
   the amended numbers and the statement narrowed as C6 says. KILL on
   either bar: `refuted`, the 2026-10-10 PASS is recorded as measured on a
   mislabelled ring, Task 9 closes as its frozen text says, and
   H-CX-HEADING-LATENT is recorded "not-pursued". BLOCKED: the no-verdict
   rule, and the gate stays closed.
3. **Null decomposition (H-STAGEA-NULL-DECOMPOSITION).** Run whatever
   Stage A returns. It is a refinement with readings and no verdict, as
   registered. The six readings are replaced by the amended ones, and the
   decomposition sentence is rewritten from them by this template, one
   clause per statistic (bandedness, mirror-peak). The within-pre weight
   family is primary (AC-N1): if it separates at p < 0.05, the statistic
   "depends on how weight magnitudes are assigned within presynaptic
   columns, not on edge placement alone"; if not, it "is carried by edge
   placement" (inferred; the AC-N4 bridge is the invariant set). The
   global weight family's reading and p follow in parentheses. The sign
   family: if it separates, the statistic "depends on the sign pattern";
   if not, it "is not carried by the sign pattern"; if NA, "the sign
   family is NA". For a statistic on which Stage A does not separate from
   its rewires, or every statistic if Stage A has no verdict, the clause
   is "not applicable". A family that is blocked or not applicable is
   reported as such, and the sentence covers the families read. The status
   stays `supported`: it records that the decomposition was carried out.
   If every family is blocked (exit 3), the no-verdict rule.
4. **Stage B (H-CX-HEADING-LATENT).** BLOCKED at the precheck or the rate
   guard: status stays `null` as recorded on 2026-10-10, now on the
   amended map, and
   AC-2's invalidation stands there too. PASS: `supported`, worded and
   with its statement narrowed as C7 says. KILL: `refuted`, tested and
   failed. Gate closed: recorded "not-pursued", status `null`.
5. **Seeding probe (H-CX-SEEDING-PROTOCOL).** KILL: `refuted` stands, and
   so does "no class-1 Stage-B re-registration is licensed". PASS:
   `supported`, worded and with its statement narrowed as C7 says, and by
   the probe's own frozen rule a
   Stage-B re-registration with the passing protocol is licensed. That
   re-registration is NOT made here. It needs the owner's go and its own
   registration. If Stage B itself returned a PASS or a KILL on the
   amended map, that verdict stands for H-CX-HEADING-LATENT, and the
   probe's rule only says whether a second Stage B with the probe's
   protocol may be registered. BLOCKED, or the gate closed: the no-verdict
   rule. When the gate closes, the reopening registration's own change
   rule ("a full re-run") is not met, which is the reason for
   `invalidated`.
6. **Class 3 (H-CX-CLASS3-COMPASS).** KILL: `refuted` stands, on the
   amended map, and the held close sentence is re-instated, dated, as
   exactly "the compiled MaleCNS CX synapse counts do not carry the
   compass in the STANDALONE 148-neuron circuit, on the amended map,
   scoped as registered (standalone circuit, AC-6 mapping, the declared
   grid)" (the clause the registry holds, with the registered scope). The
   2026-10-11 close's "no position continuum, no opposite-signed steering,
   at any declared scale" and the 2026-10-11 close note's description of
   the run are not re-instated: they describe the registered-map run. In their place the dated bullet quotes, from the
   amended JSON, each grid point's `g1_n_pass` and `g2` and every `nulls`
   entry's `g1_n_pass`. PASS: `supported`, scoped as
   registered (standalone circuit, AC-6 weights, the declared grid),
   worded and with its statement narrowed as C7 says, and the held close
   sentence is withdrawn. BLOCKED, or the gate closed: the no-verdict
   rule, for the same change-rule reason as the probe. On any no-verdict
   outcome the held close sentence is withdrawn.
7. **Class-1 ring benchmark (`cx_ring.py`).** Reported as on 2026-09-29:
   the C1 pass count of 21, the C2 pass count of 21 with the settled mass
   beside each pass, and the visual map. The header's note that a C2 pass
   at settled mass near zero is re-ignition is quoted once, as the
   header's general sentence beside the masses, and no single pass is
   labelled by it. In the registry sentence's "bump-under-visual-drive
   0/21", "0/21" is replaced by the number of grid points whose
   `visual_aux.survived_visual` is true, with each one's gain, leak and
   `c2.settled_mass` beside it (on 2026-09-29 that number was 1, not 0:
   section 14, item 7). The
   registry's "4/21 live" for C2, whose cut was never written down
   (section 14, item 7), is replaced by that C2 count with the settled
   mass beside each pass. Requirement 1 of the module-verdict program says
   "a published-result benchmark passing somewhere" on the grid and does
   not say which of C1 and C2. On 2026-09-29, C2 passes without a C1 pass
   did not carry the module. OUR READING, chosen now: requirement 1 is met
   only at a grid point where C1 and C2 both pass. If such a point exists,
   that is recorded, the module's later requirements are owed, and nothing
   more is run here. In the registry sentence "EB persistent localized
   bump 0/21 (fixed point, not a bump)", "0/21" is replaced by the amended
   C1 count. C1 passes when a single seed persists, so a pass cannot by
   itself contradict "fixed point". The parenthetical is withdrawn only
   if, at some grid point where C1 passes, at least two seeds pass C1's
   per-seed rule and every one of them follows (C7; the set is those
   seeds, at the four seed angles 22.5, 112.5, 202.5 and 292.5).
   Otherwise it stays, on the amended map. Either way the 2026-09-29
   decode ("fixed-point attractor near 222 deg everywhere alive", in the
   2026-09-29 WORKLOG entry and the `class1_reference` string of
   `fc2_eb_ring.py`; the registry record has no 222 decode) is replaced
   by the amended record's own values, with no summary phrase: for every
   grid point, each seed's `c1.per_angle[*].final_angle` with its
   retention and final circular variance, quoted as a table in the dated
   bullet.
8. **Class-2 ring benchmark (`fc2_eb_ring.py`).** Read from its verdict
   block and its selected configuration, by its registered header. The
   first of these that applies is the reading, and no later one applies.
   (a) The selected configuration is labelled "best-approach (NO cal
   pass)": by the header's own rule the benchmark "FAILS at C1-formation",
   whatever `passed` and `attribution_holds` say. If `passed` is true, it
   is quoted as that configuration's scored result, not as a pass.
   (b) `passed` is false: the benchmark fails at held-out scoring. The
   reading names which of these, under `networks.real.scored`, were not
   met: `c1_heldout_persist_pass`, `position.follows_seed_all4`,
   `position.n_distinguishable_positions` (at least 4) and
   `c2_heldout_pass`.
   (c) `attribution_holds` is false: passed but not attributed to the
   anatomy, quoting the shuffled-ring angles whose `persist_pass` is true.
   It is not a PASS, so requirement 1 is not met by it, and it is not read
   as a fail.
   (d) Otherwise: a PASS. It is recorded, the module's later requirements
   are owed, and nothing more is run here.

   The registry sentence "position-independence now measured at TWO
   fidelity classes" rests on both ring benchmarks, so it is withdrawn if
   either no longer supports it: if item 7 withdraws "(fixed point, not a
   bump)", if the class-2 real network's `c1_pass` is true under any
   selection, or if class 1 has no verdict. In every reading, nothing else of the 2026-09-29 sentence
   ("fails decisively (210 configs, every live one delocalized at one
   ~192-deg fixed point ...)") is carried over. Its counts were produced
   by that run, and calibration is map-dependent, so the selected
   configuration and the number of stages run may differ from 2026-09-29.
   That is a stated consequence. Its place is taken by the amended
   record's own values for the real network, with no summary phrase: for
   each calibration stage that ran, the rows run and the rows with
   `cal_pass` true; the rows alive (`final_mass` above the script's 1e-9
   floor), how many of them have `final_circvar` at or below 0.6, and the
   smallest `final_circvar` among them; the selected configuration (stage,
   `e_scale`, `i_ratio`, `tonic`, label); and
   `networks.real.scored.position.settled_angles`, quoted in full. The
   calibration rows are called delocalized only if no alive row has
   `final_circvar` at or below 0.6. "Decisively" is not used.

   MEASURED: applied to the 2026-09-29 record
   (`results/arenas/registered_runs_preserved_20261121/benchmarks__fc2_eb_ring.json`),
   this rule returns reading (a), FAILS at C1-formation, with the figures
   of that record (the WORKLOG of that day gave 210 configurations, 155
   alive and 0.853): 35, 105 and 70 rows; 0 calibration passes
   in each; 155 alive, none at or below 0.6 (smallest 0.853); selected
   stage 3 (`e_scale` 0.0055, `i_ratio` 12, `tonic` 0.175); settled angles
   191.31, 190.91, 194.68 and 193.05. The 155 alive calibration rows
   settled from 192.7 to 276.4 degrees, 7 of them within 22.5 degrees of
   192, so "every live one ... at one ~192-deg fixed point" was broader
   than its measurement even then. It is not repeated.
9. **Scratchpad script (H-CX-SCRATCHPAD).** Three numbers are read, all
   from the script's own JSON.
   - K, the registered kill condition: visual accuracy at N = 50 at or
     below 0.6.
   - D, the darkness arm the registration calls its replication arm:
     darkness accuracy at N = 50 at or below 0.6. It replaces the
     qualitative structural rule for status purposes (section 7, decision
     11).
   - P, position-following on the settle map: in at least one write
     style, at least 6 of the 8 writes follow (C7), the set being that
     style's writes that are alive (settled mass above the script's 1e-9
     floor). Each style is scored on its own: rule (b) compares a write only
     with the other live writes of its style, and no write of the other
     style counts, the one at the same angle included. 6 of 8 is the
     class-3 G1 bar. C7's rule (b) is what stops a
     few fixed points from meeting P. Its rule (a) counts a ring that
     moves each write onto an adjacent position: the settle map writes at
     the eight left-label angles, and a right-label remnant decodes
     exactly halfway between two of them.

   Status: if K is met, `refuted`, as registered. Otherwise if D is met,
   `refuted` stands: the ring does not return the written bit even in
   darkness. Otherwise the premise-killer did not kill, and the status
   returns to `open`. `Open` is used because the registry has no word for
   "survived its premise test": it is not support, and the hypothesis was
   never tested beyond the premise. P does not enter this status, because
   one bit needs two states, not a continuum. P decides one other thing:
   the 2026-09-27 reinterpretation recorded on H-CX-RING-ATTRACTOR
   ("fixed-point attraction, not a ring continuum"). If P holds, that
   reinterpretation is marked superseded on the amended map, and the
   settled angles of the following writes of every style in which P holds
   are quoted in its place. If not, it stands, and the amended settle-map
   table (for each style and write angle, the settled angle and the mass)
   is quoted in place of "near 222" and "near 90". P is read whenever the
   settle map finishes, whatever the main mode returns. If the main mode
   yields no verdict, the no-verdict rule applies to H-CX-SCRATCHPAD. If
   the settle map yields none, P is not read and the reinterpretation
   stands as history, with the decode caveat: its angles are decode values
   under the registered map. When it yields none by two failures to finish
   or an abandoned attempt, the dated note that says so on
   H-CX-RING-ATTRACTOR quotes the output lines of the attempt or attempts
   as the no-verdict rule defines, although no status word changes. The settle-map table is reported in full with
   the caveat of section 4: only its 0 and 180 rows write the same centre
   cell as the 2026-09-27 table.

   MEASURED: applied to the 2026-09-27 record, this rule returns that
   record's own status and reading. K is not met (visual accuracy 0.85), D
   is met (darkness accuracy 0.5), so `refuted`. P is not met: 0 of 8
   writes follow in either style (6 and 5 writes alive). The 90 write
   settled at 90.0, its own position, but so did the 45 write (and, in
   the drive style, the 135 write). The 225 write settled near 222.6, and
   so did the 180 write, within 0.03 degrees of it. The other live writes
   settled 42.6 to 71.5 degrees from their own. So the reinterpretation
   stands. Counting the other style's writes in rule (b) as well also gives
   0 of 8, so this record does not test that choice. Under the
   nearest-write rule this file used before its third review the count was
   2 of 8, with the same reading.

**Public claims.** The locked paper says the compass lost under three
model classes and then passed under the fitted one, and that the fitted
parameters differed from the authors' values. Whatever the re-runs return
is reported in a dated correction, including outcomes that leave the
earlier story standing and outcomes that undo it. Ordinal sentences
("first PASS", "three classes failed") are rewritten from the amended
record at the close, with the registered-map history kept beside them.

**How the amended outputs enter the public record.** Result files are
git-ignored. After each run the console record, the JSON and the log
(each where it exists) are hashed with SHA-256 into the WORKLOG with the
printed result lines, and that WORKLOG change is committed alone before the
next run (section 7, decision 7). At the close the amended outputs are
copied to `results/manifests/compass_amended_20261121/`, which is tracked.

## 11. Commands, the acceptance results, and the resource rule

From the repository root, with `PYTHONPATH=src` and the project virtual
environment. Unit tests first:

    python -m pytest tests/test_compass_map.py tests/test_cx_topology_killtest.py \
        tests/test_stagea_nulls2.py tests/test_cx_biswas_killtest.py \
        tests/test_cx_biswas_context_nulls.py tests/test_cx_heading_killtest.py \
        tests/test_cx_seeding_killtest.py tests/test_cx_class3_killtest.py \
        tests/test_run_amended_once.py -q

The amended runs, each through the once-only wrapper, in this order (the
default map is the amended one, and the wrapper accepts these eleven
commands and nothing else):

    scripts/arenas/run_amended_once.sh scripts/arenas/cx_biswas_killtest.py
    scripts/arenas/run_amended_once.sh scripts/arenas/cx_biswas_context_nulls.py
    scripts/arenas/run_amended_once.sh scripts/arenas/cx_topology_killtest.py
    scripts/arenas/run_amended_once.sh scripts/arenas/cx_topology_nulls2.py
    # the next three only on a Stage A PASS (the wrapper refuses them otherwise)
    scripts/arenas/run_amended_once.sh scripts/arenas/cx_heading_killtest.py
    scripts/arenas/run_amended_once.sh scripts/arenas/cx_seeding_killtest.py
    scripts/arenas/run_amended_once.sh scripts/arenas/cx_class3_killtest.py
    scripts/arenas/run_amended_once.sh scripts/benchmarks/cx_ring.py
    scripts/arenas/run_amended_once.sh scripts/benchmarks/fc2_eb_ring.py
    scripts/arenas/run_amended_once.sh scripts/cx_scratchpad_premise.py
    scripts/arenas/run_amended_once.sh scripts/cx_scratchpad_premise.py --settle-map

Each is launched detached, in a session of its own, for example as

        nohup perl -MPOSIX -e 'fork and exit; POSIX::setsid() > 0 or die "setsid: $!"; exec @ARGV or die "exec: $!"' \
        <command> >/dev/null 2>&1 &

macOS has no setsid(1), and the fork keeps setsid from failing when an
interactive shell has made the job a process-group leader. POSIX::setsid
returns -1 on failure, which Perl counts as true, hence the "> 0". A run left in
the session of the shell or tool call that started it can be stopped by a
signal sent to that session's process group. The wrapper writes every
refusal, with its reason, and every start and end to
`results/arenas/amended_runs_20261121/launch.log`, where each launch is
checked. The next starts only after this one's record ends in its
`# CLASSIFICATION` line or, if its wrapper died, after its instrument has
exited and the record has been classified by decision 7's ordered tests;
the stale lock is then removed by hand. The one re-run that a failure to
finish earns is the same command with `--rerun` placed before the script,
and it is the next launch: the wrapper refuses every other instrument's
first attempt until it has been made (decision 7).

**C4, registered-path reproduction, MEASURED before the freeze.** Each
instrument was run with `--ring-map registered` on its frozen file and
compared with its registered record (the preserved files of section 12, or
the tracked manifest where one exists).

| Instrument | Compared with | Result | Time | Peak memory |
|---|---|---|---|---|
| `cx_biswas_killtest.py` | the 2026-10-31 JSON, every field | identical | 10 s | 1.25 GB |
| `cx_topology_killtest.py` | the 2026-10-10 JSON, every field | identical | 27 s | 1.28 GB |
| `cx_topology_nulls2.py` | the 2026-10-28 JSON, every field | identical | 13 s | 1.28 GB |
| `cx_heading_killtest.py` | the 2026-10-10 log (a block at the precheck writes no JSON) | identical lines: retention 0.0000, circular variance 0.661, angle 352.1, BLOCKED | 13 s | 0.50 GB |
| `cx_seeding_killtest.py` | the 2026-10-11 JSON, every field | identical | 446 s | 0.50 GB |
| `cx_class3_killtest.py` | the 2026-10-11 JSON, every field | identical | 989 s | 1.11 GB |
| `cx_ring.py`, grid point 2.0/0.3 only | that row of the tracked 2026-09-29 manifest | identical | 31 s | 0.57 GB |
| `fc2_eb_ring.py`, full | the 2026-09-29 JSON, every field | identical | 503 s | 1.11 GB |
| `cx_scratchpad_premise.py`, main mode | the 2026-09-27 JSON | identical | 501 s | 0.48 GB |
| `cx_scratchpad_premise.py --settle-map` | the tracked 2026-09-27 manifest | identical | 52 s | 0.48 GB |

"Identical" means equal once run-time fields (elapsed time, peak memory)
and the keys this amendment adds (`ring_map`, `ring_map_description`,
`epg_unit_sizes`) are set aside. For the scratchpad main mode the
`write_scale` key is also set aside, because the 2026-09-27 file predates
it. These ten runs were made between 04:02 and 04:45 Pacific on
2026-11-21, after the last change to any of the nine registered instrument
files or to the helper (03:54) and before this freeze. Later edits before the freeze touched only
files no instrument imports: the C2 script and the two read-only check
scripts (03:57 and 04:02), their outputs, the wrapper and its pinned-input
list, the tests and the documents. An earlier round of six, on the
code as it stood before the first review, gave the same result and is
superseded.

So the registered path is MEASURED to reproduce the registered record for
all nine instruments. The limit: for the class-1 benchmark that is one of
its 21 grid points. The other 20 use the same angle array.

**Resource rule** (16 GB machine, ceiling 11.2 GB for any job). Runs are
sequential, one process at a time: the wrapper holds a lock for the whole
run and refuses a second launch. It refuses to start a run with less than
1 GiB of disk free or less than 25% of system memory free
(`kern.memorystatus_level`, the figure `memory_pressure` prints), and
writes both values into the record. During a run it kills
the instrument above 9 GB resident, and stops it if free disk falls below
512 MiB or system memory free below 5%. The runs themselves write a few
megabytes. At the freeze: free disk 3.24 GiB and system memory free 55% (`df -k` and `memory_pressure`, 16:40 Pacific). Measured peaks: 0.5 GB for the full-graph loaders,
1.3 GB for the subcircuit extraction, and 2.4 GB for one `cx_block_rewire`
call on the full graph, the code path that had never run on real data.
Stage B and the probe keep up to three rewired full networks at once, at
about 0.2 GB each (agent-reported by the reviewer who ran those paths on
synthetic graphs).

**Pinned inputs.** `scripts/arenas/run_amended_once.inputs.sha256` lists
the SHA-256 of the eleven files under
`data/processed/male-cns-v1.0/literal-rate-signed-modulators/` (the
graph, groups, manifest, node metadata and retinotopy, and the
degree-preserving null of 2026-09-21 stored beside them), of the raw
MaleCNS pair table
`data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather`, and of
the capture file `results/diagnostics/recognizer_frames.npz`. The pair
table is pinned because `extract_subcircuit` rebuilds the signed synapse
counts from it by default: Biswas, C2, Stage A, the null decomposition,
class 3 and the class-2 ring benchmark take every weight from it and read
only `node_metadata.npz` of the compiled runtime. The wrapper refuses a
run if any of the thirteen differs or is missing. MEASURED: the twelve
values of the fourth review were computed with `shasum -a 256` at 12:35
Pacific on 2026-11-21 and the pair table's at 14:29, from files last
modified between 2026-09-19 and 2026-09-27, and `shasum -a 256 -c` on the
list passed for all thirteen at 14:29. The pair table's value equals the
source hash that the compiled runtime's `manifest.json` records for its
weights (1,051,241,946 bytes), so it is the table the runtime was compiled
from. INFERRED, bridge: unchanged modification times mean unchanged bytes,
so the registered-path reproductions of this section read the files
pinned here.

## 12. Preservation of the registered runs

The registered result files are local and git-ignored and are the only
full-precision record of the registered outcomes. Before any run they were
copied, read-only, to `results/arenas/registered_runs_preserved_20261121/`,
with `/` in each path written as `__`. SHA-256 of each, which also equals
the hash of the original file:

    1f1b407bc2b02ce07fcdecc52f0cc122b098188b60a6af2e5b48118a6f1d29aa  arenas__cx_biswas_killtest.json
    886da7e8aeb443c3ccfaab56db9191a18cc4193be62759c2778ea2564dbbbdc2  arenas__cx_biswas_killtest.log
    892d2c5dd48aaa0ebcb36afaa0e2a8e9f050ca3b6bd8424b0670b1de222ed485  arenas__cx_class3_killtest.json
    491ad9301c1ec901f1563f8aa8ac2535ed00448599f5613afa8e654ec51ed430  arenas__cx_class3_killtest.log
    0a372c0db5bf7abeee37c6c3af1b798afad0aab5ac71cdf71d85899fabc3931a  arenas__cx_heading_killtest.log
    a4cbd39a8bb6209865164bd444179a3f48b659881059eee87dcdc9c294cb7d17  arenas__cx_seeding_killtest.json
    5ef13f7046a29f08639f3fdd9f9dd50c44290ab7ef95b00084a599ad83feb07a  arenas__cx_seeding_killtest.log
    3389c5e421916da66062b765a44d432b9a28838ad29fd5652c2b9df2f7b36892  arenas__cx_topology_killtest.json
    33dd3f84b1d82ffb40dc5d56e06b088826257102e133265147877a00e215c404  arenas__cx_topology_killtest.log
    f46f1ae870ee64c47158f0f1402ac242fe7a3c4a11bdb3aa532cd99d7c1229ec  arenas__cx_topology_nulls2.json
    c5ad91f922fe6e0181252fd2929d30f4dcde6eb53a67e9b262282c2b1309c744  arenas__cx_topology_nulls2.log
    272550f5d917115d8321776e34e2745c2b33a99baaa1a67e4fc51cee471b75e4  benchmarks__cx_ring.json
    8fa165ec42a59a1ad32733764f5234a9a831d62261307fdc4e0377db54e26017  benchmarks__fc2_eb_ring.json
    52286e01a34fe6d1b596a0bdbde333a417f0435a9408fafcebc36efbe6b61f5d  benchmarks__fc2_eb_ring.log
    9969d918f3dd84efce48d8b26715e82019c8a6b81913daae916b8f56605226e5  cx_scratchpad_premise.json

The class-1 and class-2 benchmark JSONs and the settle map also have
tracked copies under `results/manifests/`.

The local evidence behind sections 1, 3 and 11 is git-ignored too, and is
recorded here by SHA-256 (paths under `results/arenas/`): the figure crop,
the two check outputs of section 1 and section 3 as re-run at 10:37 with
their console records, the same checks' outputs from before that re-run,
and the console records of the ten registered-path reproductions with the
chain log that ran them.

    1a988e383254839dee5c2aba099503fea739d439b43da1c8fc23102660801f97  compass_amendment_20261121/biswas_v2_fig1g_crop.png
    36a91a8b758d509c52f78cbd8f492778a2e992ad02f6c743584d818b1e226f4e  compass_map_check.json
    9f282d7e6dafb6c8cb40be233837508b261e2b8bc37bdd2b3561ff5aeba89f3a  compass_amendment_20261121/checks/compass_map_check.console.txt
    866f6557777badae77098031a4a8e52a7565628eadaf197d9bce3e381bb801cd  biswas_fig1g_check.json
    d3245f5bbbe916f7b51fb7ae7c5c4767336cb105801214431ee2b281400e65bb  compass_amendment_20261121/checks/biswas_fig1g_check.console.txt
    29aff9d28dd2f790c7a62fff274d70a4a5a7a25ed9859c2108969086c275ac07  compass_amendment_20261121/checks/compass_map_check.before_rerun.json
    2396ff95937c6003097db7e750055505545abc50c2dc2e643f9280398222351c  compass_amendment_20261121/checks/biswas_fig1g_check.before_rerun.json
    3a3381e560ad778f61feeae3f545bf95ca773de0c660440cc8c81e2c6841b294  compass_amendment_20261121/acceptance/cx_biswas_killtest.txt
    98582f540b38abf12028d248c9d56f4c7ba2188d9ec2f7f497d50abab9fa4499  compass_amendment_20261121/acceptance/cx_topology_killtest.txt
    f952376fc08c4ba42ccc39befc24161d3728c5d97f9483f87e087c0a5ac6e6b0  compass_amendment_20261121/acceptance/cx_topology_nulls2.txt
    99a19195ba03de54b456258c6db6fb849ee7927ce5e9b602c02679b0a8cd4b52  compass_amendment_20261121/acceptance/cx_heading_killtest.txt
    7fd078e90280721b5e40b127689ee84ccb39defc75b68dc0069cc8901dbe255c  compass_amendment_20261121/acceptance/cx_seeding_killtest.txt
    4e2ac5b974b559c5b3a293d259df2c93033d195e3bc2fad2ea9f12f78f4e4590  compass_amendment_20261121/acceptance/cx_class3_killtest.txt
    58dfbb1f004a4ab5101da3af5572825a08f4bc2da089666c4e0fda727a06b736  compass_amendment_20261121/acceptance/cx_ring_point.txt
    dc3946fe0c5a99808c9e16cec11c216fd9cb4e2b5bd77b9fc18f49d2f9e9d916  compass_amendment_20261121/acceptance/fc2_eb_ring.txt
    9253bd9a3a67429aa477ee2723aa81214ee5f9995c30424dedea9faa27031f63  compass_amendment_20261121/acceptance/cx_scratchpad_main.txt
    678d4c404a55a698505c7b3cbd0545e46cfde5eac18023803f594b8d31f07f88  compass_amendment_20261121/acceptance/cx_scratchpad_settle.txt
    f4e0211583cb82f7a85b389209b7628a7620456c7397c92c1affe3474c084150  compass_amendment_20261121/acceptance/_chain.txt

## 13. Tests added with the amendment

Correctness tests do not show that a change helps, so the comparison tests
are named here. Each fails on the pre-amendment code.

- `test_registered_map_misreads_an_anatomically_labelled_ring`: a perfect
  ring with anatomical labels reads as bandedness 1.0 under the amended
  map and 0.25 under the registered one, with the blind ordering 45 to 51
  degrees off.
- `test_amended_grouping_gives_the_source_figure_unit_sizes` and
  `test_of_the_sixteen_regular_pairings_only_one_gives_the_figure_sizes`.
- `test_amended_map_agrees_with_hulse_2021_fig16b`,
  `test_amended_map_puts_each_left_wedge_between_the_right_neighbours`,
  `test_wolff_rubin_tile_pairs_under_the_two_maps`,
  `test_a_wholesale_left_right_swap_only_mirrors_the_amended_ring`,
  `test_right_centred_angles_keep_their_centre_cell_left_centred_do_not`.
- `test_registered_ring_index_is_the_frozen_expression_verbatim` and its
  unit twin: the registered path is the frozen expression.
- `test_the_map_is_a_required_argument_of_every_helper`,
  `test_the_map_is_a_required_argument_at_every_level`,
  `test_every_call_that_carries_a_map_names_it_explicitly` and
  `test_the_guard_would_catch_a_dropped_or_hard_coded_map`: no silent
  default and no hard-coded map in a flag-driven script.
- `test_the_helper_imports_nothing_but_the_standard_library`: the helper
  imports with numpy, scipy and pandas unavailable, so an instrument's
  BLOCKED exit for a missing package stays reachable.
- `test_every_compass_script_takes_the_map_from_the_one_helper` and
  `test_no_other_script_or_module_carries_a_verbatim_copy_of_the_map`.

Every validation gate these instruments had was blind to the map: each
built its synthetic ring with the inverse of the instrument's own parser,
or used a fixture with its own geometry. The recorded measurements against
the trivial alternatives are `scripts/arenas/compass_map_check.py`
(registered map and random maps) and `scripts/arenas/biswas_fig1g_check.py`
(960 alternative orderings). The once-only wrapper is tested by the 37
tests of `tests/test_run_amended_once.py`, which build a throwaway
repository with stub instruments; the fuller harness, kept outside the
repository, is described in section 7, decision 7.

MEASURED, the full suite on the final code, tests and registry (`python -m pytest -q` under `env -i` with `PYTHONPATH=src`, 16:36 to 16:40 Pacific on 2026-11-21; only the freeze-time values in the documents and one test docstring were filled in afterwards): 1041 passed, 15 skipped, 1 failed. The failure is `tests/test_league.py::test_the_real_registry_is_coherent`, which rejects the status `blocked` of H-T4T5-NATSTAT-DIRECTION (section 14, item 10). It failed before this amendment, which does not touch it.

## 14. Found while mapping or reviewing, NOT part of this amendment

Open items for the owner. None is acted on here.

1. **B-R9 may be stricter than the source paper.** INFERRED, bridge: our
   coarse-grained matrices match the authors' closely enough for two
   denominators to share a sign. The paper's valid A_Delta = 4 point
   (Supplementary Fig. S3c, read from the figure by a subagent) coincides
   with our root that has negative denominators on two inactive rows. If
   so, the registered all-rows condition rejects the paper's own solution.
   Revisiting it needs its own registration.
2. **Fan-shaped body, bar 2.** HYPOTHESIS, from labels and code only, not
   measured on weights: the instrument's glomerulus frame may run opposite
   to the direction the PFN column labels suggest, so bar 2 may have
   measured bilateral symmetry of two broad profiles and not opposite
   concentrated offsets. A reviewer notes that under the hemibrain mapping
   in Hulse et al. the frame runs WITH the column numbers, so the
   hypothesis needs the MaleCNS column labels to run the other way. A
   read-only table of the one-hop FC from PFN block by column would
   settle it.
3. **The mirror-peak statistic** (C6) does not by itself show opposite
   lateralisation or a PEN shift, in Stage A or in the fan-shaped-body
   instrument that imports it, and its docstring says it does.
4. **The 2026-10-10 Stage A close supported a statement broader than its
   bar.** The statement claims "opposite-signed left/right PEN_a offsets
   (the shifter)". MEASURED on that record: both PEN_a mean offsets had
   the same sign (-0.198 and -0.158) and every argmax offset was 0. The
   narrowing rule of decision 12 applies to the amended run; the
   2026-10-10 record is history.
5. **Registered position clauses can be met by a few fixed points** (C7).
   The class-3 registration says G1 "kills the fixed-point mode". Under
   the amended map two single-label remnants could meet it. C7 governs
   the wording of any PASS; the bars are unchanged.
6. **The rate engine raises on a non-finite state**, so the registered
   instability floor of the rate instruments (more than 20% of runs
   unstable) cannot be counted. Pre-existing. Section 10 reads such a stop
   as a crash.
7. `results/benchmarks/cx_ring.json` has `survived_visual` true at gain
   1.2, leak 0.6 (settled mass 1.8e-6), while the WORKLOG and the registry
   say 0 of 21. The registry's "4/21 live" for C2 used a cut that was
   never written down: the seven pass flags have settled masses 2.4e-8,
   1.8e-6, 0.0039, 0.132, 0.138, 0.194 and 0.368.
8. The class-3 registry text says steering was "never opposite-signed" and
   retention "0.94-0.997". The log shows opposite signs below threshold at
   three grid points and the JSON retention range is 0.882 to 1.031.
9. The class-3 registration says G2 runs "from two settled states". The
   code applies the PEN drive straight after the write.
10. `tests/test_league.py` does not accept the status `blocked`.
11. AGENTS.md records the 2026-09-23 scrambled-input fault. Whether it
    gains a sentence about this one is the owner's decision.
12. **A 64-bit `PYTHONHASHSEED` leaks into the test process.**
    `scripts/evaluate_random_baseline.py` (`_seed_process_for_environment`)
    and `src/flygi/seed.py` (`seed_everything`) set `PYTHONHASHSEED` to a
    value up to 2^64 - 1 in the running process, and Python accepts 0 to
    4294967295 only. MEASURED on 2026-11-21: after
    `tests/test_random_baseline.py` runs in the suite, the test process
    holds `PYTHONHASHSEED=10293151656857611613`, and a Python interpreter
    started from it exits at startup with a fatal error. It made 12 of the
    wrapper's tests fail in one full run, until they were given an
    explicit environment. Pre-existing. It cannot reach the amended runs:
    no instrument calls either function or starts a subprocess, and the
    wrapper runs each instrument under `env -i`. `src/flygi/seed.py` is
    imported by two instruments through `flygi.arc.factory`, so it is not
    edited here.
13. The class-2 registry sentence "every live one delocalized at one
    ~192-deg fixed point" joins two measurements of 2026-09-29: 155 alive
    calibration rows, none at or below circular variance 0.6, settling from
    192.7 to 276.4 degrees, and the four scored seed angles of the selected
    configuration, 190.9 to 194.7 degrees. The WORKLOG entry of that day
    states them separately. Section 10 item 8 does not carry it over.

## 15. Review record

Every round below was run by subagents of the session that wrote this
file. No one outside that session has reviewed it.

**Round 1**, three reviewers in parallel (registration integrity, code
correctness, anatomy and evidence), read-only and forbidden to run any
instrument: 5 blockers, 8 majors, 15 minors, and no code bug. The blockers
were all in the text. The agent-reported 6.6 degree residual had been left
out of the disclosure while a 22.5 degree reading band was being set for
it. The registered-map acceptance runs had been made before the freeze and
described as after it. The file said the grouping was not chosen by the
published r_a, when it had been found through it. No rule turned the
scratchpad re-run into a status. And "write angles keep their centre
cells" was false for the settle map. Each is fixed above. Two design
changes came from the majors: the Stage A gate now covers the probe and
class 3 (decision 10), and a Stage A PASS is no longer worded as
demonstrating the PEN shift. A reviewer's cell-by-cell reading of the
source figure became `scripts/arenas/biswas_fig1g_check.py`.

**Round 2** was cut off by a monthly spend limit after about 19 minutes,
and the three reviewers returned nothing. Their computed outputs were
recovered from their transcripts: the section 1 numbers, the section 4
tables, the figure comparison and the spectral ranges, each recomputed
independently and matching. None had raised a finding.

**Round 2, retried**, three reviewers with a probe call first and findings
written to disk as found: 0 blockers, 7 majors, 17 minors. The majors, and
what changed then:
- Rule P could be met by two fixed points. It was given the fc2 "follows"
  clause (replaced again in round 3, below).
- The scratchpad status rule replaced the registered structural rule
  without naming it. It is now decision 11, with the rule quoted.
- The disclosure understated the two subagents' authorship and the number
  of looks at the amended Biswas outcome. Section 9 now lists them.
- Some ring-benchmark outcomes had no reading or a wrong one. Section 10
  items 7 and 8 now state them, with class 2 read by its own registered
  flags, and the no-verdict rule has an exception for the program-level
  hypothesis.
- The wrapper did not check the freeze and could not coexist with the
  WORKLOG updates required between runs. It was made to compare every
  tracked file except WORKLOG.md with the freeze tag, to refuse
  `--ring-map` and `--output`, to allow one re-run after a crash, kill or
  interrupt, and to keep the first attempt's partial outputs (rewritten
  in round 3, below).
- The Stage A PASS sentence still claimed opposite lateralisation. It was
  made literal and conditioned on the signs of the mean offsets (C6).
- The minors were fixed in wording, or, where they concerned frozen
  instrument text, recorded in section 6.

While fixing these, I found that four registry statements claim more than
their bars measure, and wrote decision 12 and C7.

**Round 3**, one reviewer on everything changed after round 2, read-only:
5 blockers, 8 majors, 12 minors. The blockers, and what changed:
- The wrapper's once-only rule was keyed on a free-text label, so a
  finished instrument could run again under a throwaway label. Records
  are now named after the instrument (decision 7).
- The wrapper passed every flag except two, so a smoke or subset run
  (`--smoke`, `--points`, `--trials`, `--config`) would have run and used
  up the slot. It now accepts the eleven commands of section 11 and no
  other argument.
- The wrapper and section 10 disagreed on what an outcome is: a native
  crash was refused its re-run, a verdict followed by a teardown
  traceback was treated as a crash, and the prerequisite exit had three
  readings. "Finished" is now defined positively, and the prerequisite
  exit is neither an outcome nor a counted attempt (decision 7, section
  10).
- C6's sentence said "than any of 200 degree-preserving rewires", but bar
  2 passes with up to 9 rewires at or above the real value. It now says
  "than at least 191 of those 200 rewires (k of 200 at or above it; p =
  ...)", with three literal clauses for the signs of the mean offsets.
- C7 did not say which writes it covers and gave ties no tolerance, so
  float rounding could decide it. It now defines "follows" once (within
  one ring position of the write, no remnant shared within half a
  position) and fixes the set of writes for each instrument.
The majors: an operator interrupt counted as "not an outcome", so two
interrupts after a visible KILL would have given `invalidated` (now
"abandoned by the operator after partial output", with no re-run and the
printed lines quoted); rule P scored a consistent half-step settle as 0
of 8 (C7's new rule counts it, and scores the 2026-09-27 settle map 0 of
8, the same reading as before); class 1's "(fixed point, not a bump)"
would have been withdrawn on any C1 pass (now only with two following
seeds), and the "TWO fidelity classes" sentence ignored class 1 (now tied
to both benchmarks); decision 12 left "applied once" in the Biswas
statement (now narrowed on a PASS); the Task 10 pointer quoted a
different close sentence (now verbatim); the Task 9 pointer kept
"continuum" in its fallback (now "meets the registered position
clause"); three places said the verdict "does not depend on the
grouping" (now "across the three groupings tried"); and the disclosure
said six scripts were re-run where five were. The twelve minors were
fixed in wording. The rewritten wrapper was tested as decision 7
describes.

**Round 4**, one reviewer on everything changed after round 3, read-only:
0 blockers, 2 majors, 11 minors. The majors, and what changed:
- A direct kill of the instrument process, not of the wrapper, was
  recorded as a failure to finish and earned a re-run. An instrument exit
  of 129, 130, 131 or 143 with no watchdog or resource marker is now
  abandoned; a SIGKILL (137) stays a failure to finish, because it cannot
  be told apart from the system's memory kill.
- C7's rule (b) compared a write only with the writes in its set, so a
  write captured by another write's remnant could go unseen. Every
  surviving write of the same arm and cell or grid point now counts, in
  the set or not.
The minors: two launches 0.3 s apart could both run (now a lock held for
the whole run, and the record created with noclobber); refusals vanished
under a redirect to /dev/null (now written to `launch.log`); three
readings left their wording to after the data (items 7, 8 and 9 of
section 10 now name the fields); the test-coverage sentence overclaimed;
nothing pinned the inputs or the environment (now the pinned-input list
and `env -i`); the abandoned summaries contradicted "finished first"; the
no-verdict quoting rule did not say which lines; C6's opposite-sign clause
had no caveat; item 1 of section 10 did not state the decision-12
narrowing; and the 03:54 claim of section 6 covered files edited later.
While fixing these I found that a 64-bit `PYTHONHASHSEED` left by an
earlier test stops every new Python interpreter started from the test
process (section 14, item 12).

**Round 5**, three reviewers in parallel (the run procedure; whether every
pre-stated reading is mechanical; consistency, tiers and pronouns across
all files), seven of the eleven blockers and majors then checked by a
separate verifier told to refute it: 2 blockers, 9 majors and 40 minors
as raised. Of the
seven checked, three were confirmed and four confirmed in part, with two
severities changed: the trailer-order finding became a major and the
order-of-tests finding a minor. Of the four majors left unchecked, two
repeated checked ones, one overlapped a minor, and I checked the fourth
myself (the Biswas finding below). What changed:
- The re-run a failure to finish earns was optional and untimed, so it
  could be declined after the partial output had been seen, leaving the
  registered-map status standing. It is now the next launch: the wrapper
  refuses every other first attempt until it is made (exit 90), and a
  failure that is not re-run is read as two (decision 7, section 10). An
  instrument not run to an outcome by the close is read by the no-verdict
  rule.
- "Finished" for the six no-verdict instruments rested on two trailer
  lines written on either side of a find and the output hashes, so a
  wrapper killed between them left a finished run that earned a second
  run. The JSON line now comes first, and the text states the rule by the
  record's lines.
- The raw MaleCNS pair table, from which six commands take every weight,
  was not pinned. It is now (thirteen files), and the package check runs
  under the instrument's own environment, with the versions written into
  the record.
- C7 was open in four places: whether Stage B's calibration write counts
  in rule (b) (it does, at the angle its precheck line prints; without it
  rule (b) cannot bind in Stage B); whether the settle map's other write
  style counts (it does not); what happens at exactly 11.25 degrees
  (included, rounded to 0.01); and why the Biswas G1 clause, the class-3
  clause verbatim, kept "position-faithful" unchecked (it no longer does:
  C7 has a Biswas set).
- The class-2 non-PASS reading carried counts produced by the 2026-09-29
  run and had two branches that could both apply. Section 10 item 8 is now
  an ordered list with named fields.
Also fixed, though raised as or made minor: decision 9's PASS sentence
wrote down numbers the run had not produced (its brackets are now filled
from the run's JSON), and decision 7 did not say in what order its classes
are tested (it now lists the wrapper's five tests in order). Among the
other minors: a TERM that reached the wrapper after the instrument had
exited turned a crash or a prerequisite exit into "abandoned" (fixed in
the wrapper); the freeze check passed when git failed (now refused); a
record whose wrapper died could be read while its orphaned instrument was
still writing to it (now read only after that instrument exits); the
prescribed launch stayed in the launching shell's process group (now a
session of its own); "abandoned by the operator" is renamed "abandoned
after partial output", because a shutdown or a crash of the machine
leaves the same record; the null decomposition's sentence, the class-1
visual count, the class-3 held sentence and rule P's quoted angles now
have fixed forms; and quotations, tiers and wording were corrected across
the pointers, the registry and the WORKLOG. The wrapper was retested by
the 175 scripted checks and 36 tests of decision 7 and section 13, all
passed.

**Round 6**, three reviewers in parallel on the round-5 changes only (the
wrapper's code, text against code with a checklist of all 51 round-5
findings, and the changed readings), then a verifier told to refute each
blocker or major: 0 blockers, 4 majors and 15 minors as raised; the
verifiers confirmed one major and made the other three minors. The major:
a class-1 no verdict left two readings for the class-2 sentence
"position-independence now measured at TWO fidelity classes", and left
class 1's visual-drive entry un-invalidated. Both are now stated (section
10, item 8 and the no-verdict exception). Among the minors: a prerequisite
exit left in place by a wrapper that died blocked its slot for good (the
next launch now sets it aside, under the lock, and says so in
`launch.log`); the class-3 sentence re-instated on a KILL had no fixed
text (now quoted exactly, with the 2026-10-11 run's description left
out); decision 7 claimed that taking the re-run is not a choice, which is
false after the last command of the order (now stated as it is); the
instrument ignores INT and QUIT, and HUP under the prescribed launch, so
naming them as ways to stop it was wrong; the launch command's
`setsid() or die` could never fire (now `> 0 or die`); a signal that
finds the instrument already exited now leaves a line in `launch.log`;
and quotation, count and copy fixes in the registry, the three pointers,
the runbooks, the WORKLOG and this record. The wrapper was retested then and again after round 7.

**Round 7**, two reviewers on the round-6 changes only (the wrapper's
code and tests; the text across every file that restates a changed rule),
with a verifier for any blocker or major: 0 blockers, 0 majors, 14 minors,
several raised by both. All were fixed in wording, except one log line and
two added checks: the class-3 sentence re-instated on a KILL keeps the
registered scope; the sentence on which signals stop a run names INT to
the wrapper and HUP where the launch does not ignore them; `launch.log`
notes a signal the wrapper acts on after the instrument has exited (its
text now says the signal may have arrived up to 2 s earlier), and the text
no longer claims it notes one that arrives while the trailer is written;
the set-aside is described as done by the next launch that takes the
lock, and the once-only sentences name that exception; a dead wrapper's
record may hold none, part or all of its trailer; the sweep's two
refusals are now exercised; and copy fixes in the WORKLOG and the
registry. The wrapper was retested by the 204 scripted checks and
37 tests of decision 7 and section 13, all passed.

Rounds 1 to 6 each found a blocker or a major; round 7, on the round-6
changes only, found neither. A wider review could still find more.
