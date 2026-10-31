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

## Post numbers (added 2026-10-31; each verified against factsheet.md lines cited)

| Fact | Value | Source |
| --- | --- | --- |
| Local gateway ladder | 0.551859 -> 3.044167 -> 28.742260 (~52x; rounded 0.55 to 28.74 fine in posts) | factsheet.md:44-45 |
| MB one-shot association, real vs rewire | 0.600 vs 0.800 (rewire exceeds, p=0.0775 band miss on real) | factsheet.md:118 |
| T4/T5 motion decoding, real vs rewire | 0.3875 vs 0.4306 (rewire exceeds, p=0.97); engineered matcher 1.0000 | factsheet.md:126-128 |
| Eye map action cost | 2.59x human baseline vs 11.59x scrambled twin; 4.5x separation | factsheet.md:66 |
| "Abstention floor" plain gloss | 0.15 = what an agent earns when nothing it knows matches anything it sees. NEVER "the score for doing nothing": doing nothing (zero actions, the six crashes) scored 0.00 | factsheet + Leaderboard section above |
| Plain-English control gloss | degree-preserving rewire = "a scrambled copy of the wiring where every neuron keeps its number of connections"; use "scrambled"/"randomly rewired" in public copy, never bare "shuffle" | user style rule 2026-10-31 |

## Retracted

An earlier internal claim that the connectome reached level one "in far fewer
actions than random" came from comparing **scores on one game**, not measured
action counts, which were not being recorded at the time. Measured directly:
**fly 143.0 actions, random 144.0**. Indistinguishable. Random also completed
three times as often. **This must never appear in a post.**

## Claims that are never made

- that a fly understands ARC, or is reasoning;
- that the real **graph** beat any control **on ARC or any score** [scope
  AMENDED 2026-10-31, never deleted: as originally written this bullet said
  "any control", which was true until that date on the ARC/score record and
  remains true there — every score-side comparison isolating the real graph
  (degree-preserving null, rewired, shuffled) is null or favors the rewire
  (see `docs/arenas/SYNTHESIS.md`). The dated exceptions are off-score:
  the 2026-10-29 terminal bar-4 specificity (+0.2823 → +0.3135 vs FlyBench's
  own degree-preserving rewired control, inside a mechanism-transfer
  verdict) and the 2026-10-31 Biswas compass PASS (section below, which
  carries its own mandatory "given fitted per-type physiology" scope
  words). Neither touches ARC; 0-for-16 stands]. The two bounded
  fly-positives on the ARC side
  are encoder/anatomy-attributed, not graph-attributed: sg-bioeye-t4t5 HELPS
  (+0.0717 [+0.005,+0.156], p=0.070, borderline) vs its scrambled-ENCODER
  control, and the eye map's 2.59x-vs-11.59x action-cost separation vs its
  scrambled twin, from static anatomy;
- that any result here is zero-shot generality (training used public games);
- that other projects have no controls (at least one published a
  parameter-matched control that beat its own connectome condition).

## Harness sensitivity (added 2026-10-30; source: EXPERIMENTS.yaml H-ARC-HARNESS-SENSITIVITY close + the 2026-10-30 WORKLOG backfill)

- Positive-control reservoir (rho 0.9924, memory half-life 3 actions vs the
  real graph's 1): ARC score 0.0137 over 75 matched rows.
- vs eff-real-signed 0.0648: delta -0.0511, CI -0.153..+0.000.
- vs eff-null-degree-preserving 0.0079: delta +0.0058, CI +0.000..+0.017.
- Its matched-random twin (rho 0.1608): 0.0320; control vs twin -0.0183,
  CI -0.055..+0.000.
- Verdict: FLAT -- both decision CIs span zero; detection power ~ +0.1 score
  at 75 rows. Correct phrasing: "moved no score / did not separate", with CIs.
  NEVER "scored zero" (the score is 0.0137) and NEVER "~400x more state"
  (unsourced; the recorded numbers are rho and half-life above).

## The Biswas-fitted compass PASS (added 2026-10-31; source: EXPERIMENTS.yaml H-CX-BISWAS-FITTED close, bullet 6, + the 2026-10-31 WORKLOG entries, run record 0e80c2f)

| Fact | Value | Source |
| --- | --- | --- |
| Verdict | PASS (closed supported), exit 0, 10.7 s | run record |
| Scope words that MUST ride every sentence | "given fitted per-type physiology"; "the Biswas-fitted EPG–Delta7 realization"; "their published derivation recipe applied once to our counts" | frozen registration |
| Valid realizations on our counts | A_Delta=8 (r_a 0.4221) and A_Delta=6 (r_a 0.2132); A_Delta=4 none (reported) | run record |
| Bump test | G1 8/8 at both valid configurations; position error 0.0 deg at every write angle; retention 1.0 / 0.926 | run record |
| Null bar | all 3 degree-preserving rewires admit NO valid realization at any configuration (their attractor conditions have no solution on shuffled counts) | run record |
| Standing | the record's first hypothesis whose VERDICT is a biological-computation comparison of real wiring vs its degree-preserving null. Precedent that must accompany any "first" phrasing: H-FLYGI-FLYBENCH-TERMINAL (supported 2026-10-29) already beat FlyBench's own rewired control — itself degree-preserving — on its bar 4 (specificity +0.2823 → +0.3135), but as one bar inside a mechanism-transfer verdict | registry close |
| r_a cross-check | fitted 0.4221 / 0.2132 vs their published 0.548 / 0.437 — both OUTSIDE the 0.1 band; a flagged reading, never a verdict input | run record |

Never say: "we reproduced Biswas et al.'s realization" (the canary
fired: our counts fit a DIFFERENT member of their family); "the fly
can navigate / the connectome navigates" (one subcircuit held a bump
in darkness under their rate model — no velocity input was even
defined, G2 was non-decisional); "the connectome computes" without
the fitted-physiology qualifier (unfitted physiology measurably did
NOT, three model classes); "proves Duan/Fiete" (consistent with,
different dataset and protocol); any ARC implication (this result is
not score-adjacent; the 0-for-16 base rate is untouched).
