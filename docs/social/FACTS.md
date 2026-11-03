# Verified facts for public posts

**Every number in any FlyGI post must appear here first.** If a claim is not on
this page with a source, it does not go out. This exists because the project has
already had to retract one public-sounding claim -- see *Retracted* below.

The 2026-11-03 release audit checked the figures below against the
competition-mode gateway scorecards, local trial rows, registered
circuit results and implementations. Older snapshot dates are identified
where relevant. Number definitions and the public click-trial extract are in
[`factsheet.md`](../arenas/task1_arc_paper/factsheet.md).

## The system

| Fact | Value | Source |
| --- | ---: | --- |
| Neurons in the runtime graph | 166,700 | build manifest |
| Directed edges, earlier heuristic-signed research graph | 24,559,055 | results/manifests/degree_preserving_comparison_20260921.json |
| Directed edges, modulator-preserving deployment runtime | 24,994,595 (about 25 million connected neuron pairs) | v10/v12 runtime preflight in WORKLOG.md |
| Directed edges, unsigned runtime | 25,582,837 | build manifest |
| Competition click predictor | 401 coefficients learned online from click outcomes | src/flygi/controller/click_head.py |
| Numeric weights in research models | anatomical contact counts with model-specific sign and scaling | src/flygi/connectome/build.py |
| Motion model | pretrained flyvis cell-type parameters plus a readout trained on training games | scripts/benchmarks/fc25_visual_ds.py and t4t5_motion_arm.py |
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

The 0.15 runs are the baseline controller and two successors with
game-specific rules. All three had `neuronal_dynamics_active=false`.
The compiled static retinotopic eye map made anatomical information
available to the learned click head.

`{{BEST_SCORE}}` and `{{BEST_RANK}}` are placeholders. **Do not fill them with a
local public-set number.** Only a completed Kaggle submission counts, because
the three submissions establish only their reported public scores.

## Structural result on the earlier 24,559,055-edge graph

| Condition | Spectral radius |
| --- | ---: |
| Real heuristic-signed connectome | **0.8289** |
| Degree-preserving null, seed 20260921 | 0.2360 |
| Degree-preserving null, seed 20260922 | 0.2348 |
| Degree-preserving null, seed 20260923 | 0.2219 |

Ratio **3.59x**, mean null 0.2309 ± 0.0078. Survives exact preservation of in-
and out-degree and of the weight multiset, against nulls retaining 0.51% of the
real edge set. The statistic describes the matrix. The leaderboard agent
loaded a different graph and disabled its dynamics.

## The negative results (the substance)

| Finding | Numbers |
| --- | --- |
| Random legal play outscores the connectome | 0.097568 vs 0.064751, 500 actions, 3 seeds |
| Degree-preserving null minus real on ARC score | mean diff −0.0569, 95% CI [−0.171, +0.000], p = 1.0000 (LEAGUE.md, eff-null-degree-preserving vs eff-real-signed) |
| Interface-matched bypass ties the connectome | both 0.190476, each solving one game, different games |
| Coordinate head vs random clicking | 72 vs 236 mean unique observations, about 3.29 times as many with random clicking, six click-only games |
| Trained head, training games vs held out | 0.885805 vs **0.000000** |
| Trained head with the connectome zeroed | 0.283458 → **0.000000** |
| Public games reaching at least one level across the early fly-agent conditions (2026-09-22 snapshot) | **5 of 25** |
| Dopaminergic edges our own config deleted | **129,132** into Kenyon cells, 3,195 into MBONs |

Era scope (added 2026-10-08): the games-solved row is a fly-agent-era fact.
The later engineered-scaffold era (FAP archetypes, dynamics off) recorded
four full game wins and 20 scoring games on the local competition-mode
ladder. The later online-search premise found first-level programs on
11 of 25 games, but the integrated agent failed its battery and gateway
promotion gates (H-ONLINE-SEARCH, WORKLOG.md 2026-09-30).

## Numbers for the release

| Fact | Value | Source |
| --- | --- | --- |
| Local gateway ladder, same 25 games and 35-minute budget | 0.551859, 3.044167, 28.742260 (about 52-fold). Levels 10, 16, 73. Four full games won on the last rung. | results/manifests/gateway_ab_{off,on}_20260928.json and gateway_fap11_20260929.json |
| Displayed hidden score | 0.15 for the baseline, 0.15 with two grammars, 0.15 with thirteen. Both additions yield zero displayed gain. A grammar that abstains passes control back to the baseline. Rule activation and per-game transfer remain unknown. | WORKLOG.md submission IDs above and src/flygi/controller/fap_library.py |
| MB one-shot visual association accuracy | 0.600 real vs 0.800 rewired. One-sided p=0.0775 tests real above chance. One-sided p=0.996 tests real above rewire. Shuffled credit 0.400 (real above shuffled p=0.019). Perceptron 0.917. | results/manifests/verdict_program_20260930/mb_association.json |
| T4/T5 direction-decoding accuracy | 0.3875 real vs 0.4306 rewired. One-sided p=0.97 tests real above rewire. The engineered matcher verified the labels and therefore scored 1.0000 by construction. 660 events total over train and test, four held-out games per split. | results/manifests/verdict_program_20260930/t4t5_motion_arm.json |
| One local click game, r11l | Real map cleared level one in 57, 6 and 15 official actions for seeds 0–2. With the map scrambled the controller timed out, then used 199 and 255. Human reference 22. | factsheet.md, eye-map audit extract |
| Eye-map aggregate | Same 25 games × three seeds, mean score 0.3064 real vs 0.1875 scrambled. First-level successes 17/75 vs 16/75. Across each arm's own successes the ordinary median normalized costs were 2.59 vs 10.32. Across 14 shared successes the median within-pair cost ratio was 1.06. | factsheet.md, eye-map audit extract |
| Plain-English control gloss | degree-preserving rewire = "a scrambled copy of the wiring where every neuron keeps its number of connections"; use "scrambled"/"randomly rewired" in public copy, never bare "shuffle" | user style rule 2026-10-31 |

## Retracted

An earlier internal claim that the connectome reached level one "in far fewer
actions than random" came from comparing **scores on one game**, not measured
action counts, which were not being recorded at the time. Measured directly:
**fly 143.0 actions, random 144.0**. Indistinguishable. Random also completed
three times as often. **This must never appear in a post.**

## Claims that are never made

- that a fly understands ARC, or is reasoning;
- that active recurrent fly dynamics earned a hidden ARC score increase;
- that an approximately fourfold ratio of medians on different sets of
  successful trials describes a fourfold paired improvement. The click
  head used the historical transposed coordinate indexing in both arms
  and learned online. Both local arms ran a connectome tiebreak and
  the static map permutation was the intervention;
- that the score of 0.15 establishes how many hidden rules activated,
  a contest-wide floor or what every abstaining agent earns;
- that the project is training-free. External fitted vision parameters,
  trained readouts, the learned click head and fitted compass have
  different training histories;
- that all other comparisons favored rewiring. The encoder intervention
  sg-bioeye-t4t5 gave +0.0717 [+0.005,+0.156], p=0.070, and the off-score
  FlyBench terminal test improved the specificity contrast from +0.2823
  to +0.3135 against the supplied rewire. That rewire did not receive the
  terminal intervention. See `docs/arenas/SYNTHESIS.md`;
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
- Verdict: FLAT. Both decision CIs include zero. The estimated detection
  floor was roughly +0.1 score on this protocol. The harness did not
  detect a gain with the positive control.
  NEVER "scored zero" (the score is 0.0137) and NEVER "~400x more state"
  (unsourced; the recorded numbers are rho and half-life above).

## The Biswas-fitted compass PASS (added 2026-10-31; source: EXPERIMENTS.yaml H-CX-BISWAS-FITTED close, bullet 6, + the 2026-10-31 WORKLOG entries, run record 0e80c2f)

| Fact | Value | Source |
| --- | --- | --- |
| Verdict | PASS (closed supported), exit 0, 10.7 s | run record |
| Model | From 46 EPG + 42 Delta7 cells, pool anatomical counts into 8 + 8 population units, impose rotational symmetry, fit cell-type gains to the ring-attractor conditions using Biswas et al.'s published derivation recipe. The registered scope is “given fitted per-type physiology.” | scripts/arenas/cx_biswas_killtest.py, unit_count_matrix and run_configuration |
| Valid realizations on our counts | A_Delta=8 (r_a 0.4221) and A_Delta=6 (r_a 0.2132); A_Delta=4 none (reported) | run record |
| Bump retention | Directly initialize the derived activity pattern, integrate in darkness for 100 time constants. At both valid configurations it retained all 8 symmetry-related headings with drift rounding to 0.0 degrees. Retention 1.0 / 0.926. | scripts/arenas/cx_biswas_killtest.py, simulate_g1 and run record |
| Null bar | The same fitting procedure found zero valid fits across the three tested degree-preserving rewires at any declared configuration. This is a finite search. | run record |
| Standing | the record's first hypothesis whose VERDICT is a biological-computation comparison of real wiring vs its degree-preserving null. Precedent that must accompany any "first" phrasing: H-FLYGI-FLYBENCH-TERMINAL (supported 2026-10-29) already beat FlyBench's own rewired control — itself degree-preserving — on its bar 4 (specificity +0.2823 → +0.3135), but as one bar inside a mechanism-transfer verdict | registry close |
| r_a cross-check | fitted 0.4221 / 0.2132 vs their published 0.548 / 0.437 — both OUTSIDE the 0.1 band; a flagged reading, never a verdict input | run record |

The measured endpoint is retention in this reduced, fitted model. Navigation,
updating heading during turns, the living circuit's physiology and
training a random network are different questions. Describe the earlier
three model classes by their specific initialization failures or drift.
The compass comparison took place outside ARC. The score-adjacent
prediction record remains 0 for 16.
