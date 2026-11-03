# FlyGI paper fact sheet

Release audit, 2026-11-03. The gateway, click-head, motion, association,
spectral and compass claims below were checked against saved run records
and implementation. Entries carried from the September and October
experiment logs retain their original protocols. W = WORKLOG.md,
L = LEAGUE.md, R = EXPERIMENTS.yaml.

## The system

- MaleCNS v1.0: 166,700 retained neurons. THREE edge counts, do not mix:
  unsigned graph 25,582,837; heuristic-signed build 24,559,055 (zeros
  1,023,782 outgoing edges of modulatory/unknown-transmitter neurons);
  modulator-preserving runtime 24,994,595. The graph DEPLOYED on Kaggle in
  notebooks v10 and v12 is the 24,994,595-edge modulator runtime (both
  FLYGI_PREFLIGHT logs read "166,700 nodes, 24,994,595 edges"); the
  six-zeros-era v3 notebook preflighted 24,559,055. [W]
- A directed edge identifies a connected neuron pair. Its observed
  magnitude is the number of anatomical contacts. The model assigns
  physiological sign, scaling and dynamics. The original rate graph uses
  signed, normalized log counts. The competition click predictor learns
  401 coefficients online. The class-2.5 visual model imports optical-flow
  training. Limit any frozen-parameter claim to the named component.
  [`src/flygi/connectome/build.py`, `src/flygi/controller/click_head.py`,
  `scripts/benchmarks/fc25_visual_ds.py`]
- Fidelity ladder: class 1 = full-graph float32 leaky-tanh rate dynamics
  (SciPy CSR, no dense matrix); class 2 = per-type LIF/graded on extracted
  subcircuits (MB: 627 PN / 4,064 KC / 2 graded APL / 97 MBON, 770,711
  signed-count edges; EB-PB ring: 148 neurons incl. both PEN populations;
  optic-lobe patch); class 2.5 = trained flyvis ensemble parameters with
  verified provenance for T4/T5. [W]
- Controls: exact degree-preserving rewires, interface-matched no-graph
  bypass, shuffled-credit/time, scrambled-encoder twins, engineered
  equivalents. The registered tests and their individual directions and
  pass bars are in EXPERIMENTS.yaml. [W,R]

## Kaggle submissions (real, scored)

- Six early 0.00s (latest ID 56563583; 56444435 ranked 3212/3215): root
  cause a construction crash invisible to exit codes — Swarm passes
  record=True, base Agent.__init__ calls start_recording() which reads
  agent.name before the subclass sets self._mode; AttributeError in the
  swarm thread, main.py exits 0, empty scorecard scores 0.00. Six
  submissions, zero actions ever played. Diagnosed 2026-09-26. [W]
- 56620463 (combo_light engineering baseline, notebook v10, source 8021d5c,
  accepted 2026-09-27 22:09:56 UTC): COMPLETE, 0.15.
- 56650224 (two FAP archetypes, v11, accepted 2026-09-28 19:08:50 UTC):
  COMPLETE, 0.15.
- 56683298 (thirteen archetypes, v12, accepted 2026-09-29 17:28:21 UTC):
  scored 0.15. [W]
- Local official competition-mode gateway ladder (matched 35-minute
  windows): 0.551859 (combo_light) -> 3.044167 (two archetypes) ->
  28.742260 (thirteen archetypes; full precision 28.742259837750854; 73
  levels, 20 scoring games, four full wins: tu93 9/9 in 185 actions, ft09
  6/6 in 80, ka59 7/7 in 275, sb26 8/8 in 124). All engineered scaffold;
  neuronal_dynamics_active=false in the three 0.15 agents. The tracked
  scorecards are `results/manifests/gateway_ab_off_20260928.json`,
  `gateway_ab_on_20260928.json` and `gateway_fap11_20260929.json`
  in the same directory. Their level counts are 10, 16 and 73. [W]
- The ladder's endpoint held against its own successor: the online search
  layer failed its preregistered gateway gate 28.459550 vs the 28.742260
  bar and did not ship. The 28.74 candidate led these tested configurations. [W]
- The grammar-free controller and both grammar-equipped successors each
  displayed 0.15 on Kaggle. The local score increased about 52-fold and
  the displayed hidden score did not increase. The comparison supplies
  no per-game activation or effect estimates. The baseline plays actions
  and continues to do so when a grammar abstains. [W,
  `src/flygi/controller/fap_library.py`]

## Fly-positive results (measured)

- Eye-map substrate: 23,720 ol_intrinsic lamina/medulla interneurons carry
  the column assignments, spanning 892 occupied retinotopic columns
  (photoreceptors carry none: 0 of 6,098). [W Phase 0]
- LC lobula-columnar population as scored by the class-1 readout and
  benchmarks: 4,257 neurons (type prefix "LC"; EXPERIMENTS.yaml, the
  literal_rate_lc_readout config, and WORKLOG's readout table agree). [W,R]

### Eye-map action audit

- **Eye map in the learned click controller.** Across the same 25 public
  games and three seeds, the anatomical and permuted arms averaged 0.3064
  and 0.1875 in the 600-action evaluation. They cleared the first level
  on 17/75 and 16/75 rows across six and seven distinct games. The
  anatomical arm's 17 levels also missed the incumbent's breadth gate
  (21 levels, ten games). Both arms use the historical transposed
  coordinate convention and the same online logistic head. Both local
  arms kept the real-connectome tiebreak active. Their only configuration
  difference affecting behavior is the map permutation.
  There is no hidden-set map ablation. [H-CONSEQUENCE-COUPLING,
  `configs/clickhead_retinotopic{,_permuted}.yaml`,
  `src/flygi/controller/click_head.py`]
- On **r11l**, the anatomical arm cleared level one in **57, 6 and 15
  official actions** in seed order. The scrambled arm timed out at the
  600-action budget, then used **199 and 255**. The human reference is
  22 actions. Official actions include resets. This is a per-game example.
- **Across successes**, the ordinary medians of first-level actions
  divided by each game's human reference are **2.59091 and 10.31818**.
  The completed game/seed sets differ. The old 11.59 used only the upper
  middle scrambled observation. Its middle pair is 199/22 and 255/22.
  A fourfold per-run speed claim would misstate the comparison. On the
  14 game/seed pairs both completed, the median of the paired
  scrambled/anatomical cost ratios is **1.05924** (nine cheaper with
  anatomy, one tie, four costlier). This paired statistic also excludes
  incomplete runs.

  Audit extract below. Each triplet gives official first-level actions for
  seeds 0, 1 and 2. A dot means no level one within 600 actions. The other
  17 games had no completions in either arm.

  | Game | Human reference | Anatomical | Scrambled |
  | --- | ---: | --- | --- |
  | ar25 | 32 | ·, ·, · | ·, ·, 557 |
  | lf52 | 32 | ·, ·, · | 432, ·, · |
  | lp85 | 17 | 16, 16, 19 | 17, 17, 19 |
  | m0r0 | 30 | 393, 393, 388 | 415, 415, 265 |
  | r11l | 22 | 57, 6, 15 | ·, 199, 255 |
  | sp80 | 39 | 510, ·, 510 | ·, ·, · |
  | tn36 | 32 | 46, 49, 49 | 50, 40, 40 |
  | vc33 | 7 | 72, 114, 242 | 344, 134, 124 |

  Source on the verdict machine: `results/connectome_agent/sg-clickhead-retinotopic.rows.jsonl.gz`
  (SHA-256 `e1e652d6f167f6460e889cbcf2455f1246043c16ef9b6a48d13effeae4ed0238`)
  and `sg-clickhead-permuted.rows.jsonl.gz`
  (`2adf8e74f2942d20048ec607eba0690179030b24edb88630e81e3843d6a82112`).
  Filter `official.levels_completed > 0`, divide the first
  `official.runs[0].level_actions` entry by the first
  `level_baseline_actions` entry and apply the ordinary median.
  The separate deadline variant gave 0.3058 vs 0.1875 and 14/75
  completions in each arm.

### Circuit and graph measurements

- sg-bioeye-t4t5: +0.0717 [+0.005,+0.156] p=0.070, 22 vs 13 levels, 75
  matched rows, vs its scrambled control — the league's only HELPS;
  survived a hash-grade source audit; recorded as borderline at ship time.
  [L,W]
- Structural non-randomness: estimated spectral radius of the earlier
  24,559,055-edge heuristic-signed matrix was 0.8289 vs 0.2219-0.2360
  across three exact degree-preserving nulls (3.59x their mean). This
  is a matrix statistic. The distinct 24,994,595-edge deployment used
  modulator-preserving weights. DN participation ratio on the earlier
  protocol was 5.39 vs 14.33-18.54.
  The record's own caveat travels with it: "the strongest reproducible
  connectome result. It has not yet produced an ARC outcome advantage."
  [`results/manifests/degree_preserving_comparison_20260921.json`]
- Harness-sensitivity bound (measured 2026-10, H-ARC-HARNESS-SENSITIVITY,
  FLAT): the validated long-memory positive-control reservoir (rho 0.9924,
  half-life 3 actions) scored 0.0137 on the full eff- protocol — both
  decision CIs span zero (vs real -0.0511, CI -0.153..0.000; vs
  degree-preserving null +0.0058, CI 0.000..+0.017); detection power
  ~ +0.1 score at 75 rows. Class-1 ARC real-vs-null results read as
  interface-bounded: the registered test did not detect a gain at that
  resolution. The other arenas have separate checks and endpoints. [W]
- KC SPARSE CODING VALIDATED at class 2: held-out median active fraction
  0.0741 in the [0.03, 0.15] band; APL densification control +0.0098
  (load-bearing exactly on dense stimuli, Lin-consistent); both trivial
  alternatives 1.0000 dense; 10/12 configs pass, the two failures the
  doc's predicted weak-APL corner. Mechanism: threshold + claw coincidence
  + graded APL. [W]
- T4/T5 DS VALIDATED at class 2.5: pooled median DSI 0.3216 (band >=0.30);
  T4 tiles four directions, T5 three; trained flyvis ensemble parameters
  with verified provenance. Attribution two-sided: trained per-pair
  strengths carry the pass (frozen counts 0.042; uniform-tau at trained
  strengths 0.3365 — type-mean taus add nothing). [W]
- MB reach: zeroing MBON outputs changes the DN readout by 22.286% of its
  magnitude, touching 92.2% of entries (20 turns). Caveat: measured at
  gain 2.7, an operating point later superseded (the gain-2.7 sweep ran on
  unrepresentative input; re-swept to 2.0 on correlated frames) — cite as
  "MB output reaches the readout", not as a number at the deployed point.
  [W, AGENTS.md]

## Fly-negative results (earned, control-backed)

- H-MB-CLASS2-ASSOCIATION refuted (one-shot visual association, class-2
  MB, calibrated KC code, input gates PASSED — PN share of KC drive 62-87%
  vs 5% bar; 450 presentations, 5 disjoint held-out games x 3 seeds):
  real 0.600 (one-sided binomial test against chance, p=0.0775);
  degree-preserving rewire 0.800 (one-sided sign test for **real > rewire**,
  p=0.996); shuffled-credit 0.400
  (real beats it, p=0.019 — the depression mechanism genuinely carries
  credit under this protocol); matched one-shot perceptron 0.917. Why
  the rewired arm scored higher remains an inference.
  [`results/manifests/verdict_program_20260930/mb_association.json`]
- H-T4T5-CLASS25-MOTION refuted (ARC motion decode at validated class-2.5
  fidelity; 660 verified displacement events across 11 qualifying games;
  4 held-out games x 3 seeds): real 0.3875 held-out (above chance every
  seed); uniform-tau 0.3917, degree-preserving rewire 0.4306,
  engineered shift-matcher 1.0000 by construction (the same matcher
  verified the event labels). The one-sided tests for real above
  each of the first two controls gave p=0.94 and p=0.97 respectively.
  Four games were held out per seed and the splits overlap. The full
  set of 660 events includes training and test examples.
  [`results/manifests/verdict_program_20260930/t4t5_motion_arm.json`]
- EB RING at two fidelities: class 1 — fixed-point attractor near 222 deg
  everywhere alive (settle map: robust point ~222 deg EPG mass ~0.21,
  vestigial ~90 deg mass 4e-4; writes on half the ring die; darkness
  A-vs-B decode exactly 0.5). Class 2 — 210 Shiu-canonical LIF configs,
  155 alive, EVERY one delocalized (min circvar 0.853 vs 0.6 band), all
  four seed angles settling at one fixed point (~192 deg); shuffled ring
  comparable. These tests cover the declared class-1 and class-2 models.
  The class-3 spiking test sustained a bump but drifted to one region
  from different headings. [W]
- **Fitted compass, separate from ARC.** Following the Biswas et al.
  derivation, 46 EPG and 42 Delta7 neurons contribute anatomical contact
  counts to 16 rate units. The model averages equivalent locations around
  the ring, then fits type-pair gains to attractor conditions. Two of three
  configurations on the real counts held an initialized heading in
  darkness for 100 time constants at eight symmetry-related positions
  (error 0.0 degrees to the reported precision). The same search found
  no valid fit for three degree-preserving rewires. There was no
  velocity input or sensory write. The fitted shape coefficients 0.4221
  and 0.2132 differ from the paper's 0.548 and 0.437. The first verdict
  in this project decided by this biological-computation comparison is
  distinct from the earlier FlyBench terminal result, whose specificity
  bar also used a degree-preserving rewire. [H-CX-BISWAS-FITTED,
  `scripts/arenas/cx_biswas_killtest.py`, WORKLOG.md run record 0e80c2f]
- LC: class-1 object-position code SIGN-INVERTED at all 21 grid points
  (Spearman rho -0.203 best to -0.314, band >= +0.50; valid-pair fraction
  1.00 everywhere — not degeneracy; best single type LC11 0.243).
  Recognizer premise killed: held-out dead-vs-live, real LC 0.438 / LH
  0.520 vs scrambled 0.510/0.579, raw grid-block histogram baseline 0.415,
  chance 0.5. [W]
- H-FLYHASH-STATE-KEY refuted (real PN->KC expansion + WTA as ARC state
  keys). H-MBON-DAN-METAPLASTICITY null: weights move 3.4-61 absolute,
  MBON activity diverges up to 50%, then the MBON->DAN stage crushes it
  ~250-500x — gate delta 4e-5..2e-3 vs never-learned counterfactual,
  plateauing; bounded convergence, no compounding. H-EFFERENCE null. Taxis
  null. H-JEPA-SPONTANEOUS null (shuffled-time control +0.038 = the real
  arm's own number — static structure, not prediction). [W,R]
- THREE learning nulls of increasing strength (invalid signal -> fair
  sparse -> dense balanced action-dependent) bracket MB plasticity; the
  dense null verified live, not a dead switch: dense_reinforcement=true,
  only 5/75 replay hashes match the sparse arm, behaviour changed on 70/75
  game/seed rows, outcomes converged anyway. [W,R]
- Teaching signal: 18 level advances vs 569 game-over frames across 75
  rows (~31:1). Depression-only plasticity gets no curriculum from 2
  positive examples. A property of the task signal, not the fly. [W]
- Track B trained head (520 params, CEM): genuinely connectome-dependent —
  trace ablation 0.2835 -> exactly 0.0000, unique observations 263.4 ->
  169.5. It scored 0.0000 on all 17 held-out
  games (training games 0.8858 vs untrained 0.5952; objective peaked at
  generation 16). [W]

## Interface lessons (the methods contribution)

- No tested class-1 gain/leak grid point passed the registered checks
  for T4/T5 direction selectivity, LC position, KC sparsity or the EB
  bump (21 configurations). This is a finite sweep. [W]
- Given-usable-input rule (AGENTS.md, measured 2026-09-23): the MB was
  taught while receiving 0.00% of its input from any driven sensory
  population; motion/object detectors were evaluated on spatially
  scrambled input. Both produced nulls. Neither null was about the fly.
- COORDINATE-HEAD defect (branch order: deterministic novelty-centroid
  before the temperature-controlled sampler): shipped in both early
  competition submissions with six passing tests, "none comparing it
  against clicking at random." Random explores 3.29x more (236 vs 72 mean
  unique observations) in the six click-only games; centroid OFF recovered
  coverage ~fourteen-fold (r11l 96 -> 1,383 cells) and matched random.
  NOTE: distinct from H-COORDINATE-CONVENTION (the later x/y-flattening
  replay hypothesis, refuted by its own robustness bar). [W]
- Phase 0 tested the standing excuse directly: the first retinotopic
  encoder (space preserved, colour destroyed) made the agent worse on
  every axis (0.190476 -> 0.003156) — "the first direct test of the
  excuse, and the excuse did not survive it cleanly." The bio-eye fix
  (space AND categorical colour) then measured null on score. [W]
- Partial-lead collapse, three occurrences; canonical case: a 41-row
  seed-ordered partial read +10.6% and +3 levels, erased entirely at 75
  rows; third occurrence +0.072 at 59 rows erased by the final 16.
  Verbatim rule: "Partial matrices from a seed-ordered run are not small
  versions of the result; they are a biased sample of it." Enforced in
  code (scripts/league.py). [W]
- Mechanical load-bearing is not score load-bearing: fly_decisive_rate
  24.7-37.2% of turns, delta vs champion +0.0000 (zero-width CI) on the
  reclick seat. [W]
- Self-labelling matters: preflight had mislabelled combo_light
  "controller-fly"; the 2026-09-26 audit made the adapter report
  controller-light / deploy_fly_tiebreak=false /
  neuronal_dynamics_active=false machine-readably. [W]
- EXPECTED-tier base rate: 0 for 16 on score-adjacent predictions (as of
  2026-10-06; fifteenth = H-EARLYFILTER-BRAINSCORE-V1, refuted on the
  rewire bar after clearing floor and passthrough; sixteenth =
  H-ALMB-GASDRIFT, refuted on the rewire and raw bars after clearing
  chance decisively). The current denominator refers to the registered
  score-adjacent predictions in `docs/arenas/SYNTHESIS.md`. [W,R]

## External context (SOURCED — dated survey, in-repo)

From docs/next_arenas_survey_20260930.md (two-agent web survey, 2026-09-30):
- A September-2026 wave of ~50+ public MaleCNS/FlyWire game demos exists
  (Doom, Mario 64, Beat Saber, trading, chess); the public critique of the
  wave: "most demos are a frozen graph plus a hand-written readout"
  (Mineault, neuroai.science).
- Zero connectome-based or fly-circuit attempts were found on any ARC
  version as of 2026-09-30.
- At least one wave demo (fly-hero) ran real/shuffled-wiring controls on
  its plasticity — but with a trained readout, and without
  validate-at-fidelity or input-gate stages; the survey found NO demo
  running all three stages (validate, gate inputs, test vs controls)
  together.
- Three published lines cut against innate-wiring usefulness (survey,
  2026-09-30; sources in docs/next_arenas_survey_20260930.md): "digital
  sphinx" (Tuthill lab, bioRxiv 2026.03.20.713233) — a worm connectome +
  trained mapping produces realistic fly walking; fly-hero
  (github.com/bsgelman/fly-hero) — dopamine-RPE learning needs real wiring
  (99.3% vs 21.9% shuffled) but a TRAINED readout hits 100% on a random
  network; connectome-reservoir benchmarks (arXiv:2609.30508 and others) —
  randomized nulls often match or beat real wiring.
- ARC Paper Track precedent (due_diligence_20260930.md, sourced from
  2024+2025 winner lists): CompressARC ("ARC-AGI Without Pretraining",
  Liao & Gu) took 3rd in 2025 at ~20% ARC-AGI-1 accuracy with 76K
  parameters; biologically-flavored entries ARC-NCA and Vector Symbolic
  Algebras placed as runners-up. The dated review did not identify a
  pure negative-results paper among those two years' winners.
- Scope rule: facts about the world outside this repository are
  survey-dated claims ("found as of 2026-09-30"), never absolutes, and we
  did not survey non-connectome entrants for transfer measurements.

## Claim boundaries (must appear in any public artifact)

- Deployed agents' fly content = the compiled anatomical eye map only
  (static); neuronal dynamics OFF in all three 0.15 submissions.
- A leaderboard score establishes engineering, not fly computation.
- Nulls describe each model on its specific task. Two experiments
  passed their input gates and then missed their advantage bars:
  class-2 MB one-shot visual association on ARC and class-2.5 T4/T5
  motion decoding on ARC frames. These outcomes leave the properties
  of living circuits and equally trained random networks open.
