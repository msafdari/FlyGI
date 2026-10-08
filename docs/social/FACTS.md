# Verified facts for public posts

**Every number in any FlyGI post must appear here first.** If a claim is not on
this page with a source, it does not go out. This exists because the project has
already had to retract one public-sounding claim -- see *Retracted* below.

Last verified: 2026-09-22; Leaderboard section and the flagged rows
re-verified 2026-10-08 (pre-release audit) — other sections still carry
the 09-22 verification and must be re-checked against
docs/arenas/task1_arc_paper/factsheet.md before any post goes out.

## The system

| Fact | Value | Source |
| --- | ---: | --- |
| Neurons in the runtime graph | 166,700 | build manifest |
| Directed edges, signed runtime | 24,559,055 | build manifest |
| Directed edges, unsigned runtime | 25,582,837 | build manifest |
| Trainable parameters, submitted agent | **0** | interface record |
| Dataset | MaleCNS v1.0, released 2026-06-08 | `male-cns.janelia.org` |
| Paper | *Cell*, 2026-09-03, doi:10.1016/j.cell.2026.08.015 | publisher |
| Licence | CC BY 4.0 | publisher |

## Leaderboard

Re-verified 2026-10-08 against `docs/arenas/task1_arc_paper/factsheet.md`.

| Fact | Value | Source |
| --- | --- | --- |
| Six 0.00 submissions (`56444435` ranked 3212/3215; latest of the six `56563583`) | public score **0.00** each | factsheet.md |
| Root cause of all six 0.00s | construction crash — **zero actions ever played**, so any "action ceiling" explanation is wrong | factsheet.md |
| `56620463` (combo_light engineering baseline, notebook v10) | COMPLETE, **0.15** | factsheet.md |
| `56650224` (two FAP archetypes, notebook v11) | COMPLETE, **0.15** | factsheet.md |
| `56683298` (thirteen archetypes, notebook v12) | scored **0.15** | factsheet.md |
| Top of leaderboard, 2026-09-22 snapshot | 18.81 | WORKLOG.md |

The 0.15 runs are the engineered FAP-archetype scaffold with
`neuronal_dynamics_active=false`; their only fly content is the compiled
static retinotopic eye map (factsheet.md, claim boundaries).

`{{BEST_SCORE}}` and `{{BEST_RANK}}` are placeholders. **Do not fill them with a
local public-set number.** Only a completed Kaggle submission counts, because
every local gain so far has failed to transfer.

## The structural result (the one positive finding)

| Condition | Spectral radius |
| --- | ---: |
| Real signed connectome | **0.8289** |
| Degree-preserving null, seed 20260921 | 0.2360 |
| Degree-preserving null, seed 20260922 | 0.2348 |
| Degree-preserving null, seed 20260923 | 0.2219 |

Ratio **3.59x**, mean null 0.2309 ± 0.0078. Survives exact preservation of in-
and out-degree and of the weight multiset, against nulls retaining 0.51% of the
real edge set. **No ARC advantage has followed from it.**

## The negative results (the substance)

| Finding | Numbers |
| --- | --- |
| Random legal play outscores the connectome | 0.097568 vs 0.064751, 500 actions, 3 seeds |
| Real vs degree-preserving null on ARC score | mean diff −0.0569, 95% CI [−0.171, +0.000], p = 1.0000, 1 of 25 games |
| Interface-matched bypass ties the connectome | both 0.190476, each solving one game, different games |
| Our "smart" clicking vs random clicking | 72 vs 236 unique states, **3.29x worse**, in the 6 click-only games |
| Trained head, training games vs held out | 0.885805 vs **0.000000** |
| Trained head with the connectome zeroed | 0.283458 → **0.000000** |
| Public games solved by any condition, fly-agent era (as of 2026-09-22) | **5 of 25** |
| Dopaminergic edges our own config deleted | **129,132** into Kenyon cells, 3,195 into MBONs |

Era scope (added 2026-10-08): the games-solved row is a fly-agent-era fact.
The later engineered-scaffold era (FAP archetypes, dynamics off) recorded
four full game wins and 20 scoring games on the local competition-mode
ladder, and H-ONLINE-SEARCH's preregistered bar was met decisively, 11 of 25
games (sources: `docs/arenas/task1_arc_paper/factsheet.md`; WORKLOG.md
2026-09-30).

## Retracted

An earlier internal claim that the connectome reached level one "in far fewer
actions than random" came from comparing **scores on one game**, not measured
action counts, which were not being recorded at the time. Measured directly:
**fly 143.0 actions, random 144.0**. Indistinguishable. Random also completed
three times as often. **This must never appear in a post.**

## Claims that are never made

- that a fly understands ARC, or is reasoning;
- that the real **graph** beat any control: every comparison isolating the
  real graph (degree-preserving null, rewired, shuffled) is null or favors
  the rewire (see `docs/arenas/SYNTHESIS.md`). The two bounded fly-positives
  are encoder/anatomy-attributed, not graph-attributed: sg-bioeye-t4t5 HELPS
  (+0.0717 [+0.005,+0.156], p=0.070, borderline) vs its scrambled-ENCODER
  control, and the eye map's 2.59x-vs-11.59x action-cost separation vs its
  scrambled twin, from static anatomy;
- that any result here is zero-shot generality (training used public games);
- that other projects have no controls (at least one published a
  parameter-matched control that beat its own connectome condition).
