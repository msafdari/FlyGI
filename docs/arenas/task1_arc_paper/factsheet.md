# FlyGI paper fact sheet — VERIFIED 2026-09-30

Every line below survived a four-agent adversarial check against the durable
record (WORKLOG.md, LEAGUE.md, EXPERIMENTS.yaml, docs/) on 2026-09-30
(workflow wf_7e405dd9-8a8). Verdicts: all CONFIRMED except the corrections
applied inline. The writeup may cite ONLY facts from this sheet (or the
record directly, with the same discipline). Provenance key: W=WORKLOG.md,
L=LEAGUE.md, R=EXPERIMENTS.yaml.

## The system

- MaleCNS v1.0: 166,700 retained neurons. THREE edge counts, do not mix:
  unsigned graph 25,582,837; heuristic-signed build 24,559,055 (zeros
  1,023,782 outgoing edges of modulatory/unknown-transmitter neurons);
  modulator-preserving runtime 24,994,595. The graph DEPLOYED on Kaggle in
  notebooks v10 and v12 is the 24,994,595-edge modulator runtime (both
  FLYGI_PREFLIGHT logs read "166,700 nodes, 24,994,595 edges"); the
  six-zeros-era v3 notebook preflighted 24,559,055. [W]
- Fidelity ladder: class 1 = full-graph float32 leaky-tanh rate dynamics
  (SciPy CSR, no dense matrix); class 2 = per-type LIF/graded on extracted
  subcircuits (MB: 627 PN / 4,064 KC / 2 graded APL / 97 MBON, 770,711
  signed-count edges; EB-PB ring: 148 neurons incl. both PEN populations;
  optic-lobe patch); class 2.5 = trained flyvis ensemble parameters with
  verified provenance for T4/T5. [W]
- Controls: exact degree-preserving rewires, interface-matched no-graph
  bypass, shuffled-credit/time, scrambled-encoder twins, engineered
  equivalents; preregistered bands and kill rules in EXPERIMENTS.yaml. [W,R]

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
  neuronal_dynamics_active=false in every scored submission. [W]
- The ladder's endpoint held against its own successor: the online search
  layer failed its preregistered gateway gate 28.459550 vs the 28.742260
  bar and did not ship — the 28.74 candidate is the measured local ceiling
  of the non-LLM track. [W]
- Abstention floor 0.15 held three times => game-specific grammar transfer
  to the hidden set measured zero, three times. [W]

## Fly-positive results (measured)

- Eye-map substrate: 23,720 ol_intrinsic lamina/medulla interneurons carry
  the column assignments, spanning 892 occupied retinotopic columns
- LC lobula-columnar population as scored by the class-1 readout and
  benchmarks: 4,257 neurons (type prefix "LC"; EXPERIMENTS.yaml, the
  literal_rate_lc_readout config, and WORKLOG's readout table agree). [W,R]
  (photoreceptors carry none: 0 of 6,098). [W Phase 0]
- EYE MAP LOAD-BEARING (the one deployed fly component): metric is level-1
  per-completion action cost vs human baseline. Real retinotopic map 2.59x
  human baseline vs scrambled-map twin 11.59x — 4.5x efficiency separation
  attributable to retinotopy, identical machinery otherwise
  (sg-clickhead-retinotopic 0.3064, replicated 0.3058, vs permuted 0.1875).
  Gain concentrated where the offline premise predicted: r11l completions
  0.27-0.68x baseline, lp85 1.12-1.94x — the project's first sub-baseline
  completions. Boundary carried WITH the win: the same ladder failed BAR A
  on breadth (17 levels vs champion 21; 6-7 games vs 10), so the efficiency
  separation coexists with a measured breadth loss. Deployed as static
  anatomy metadata — no live dynamics. [W,R]
  The eye map's hidden-set contribution was never isolated: no
  scrambled-map control ever ran on Kaggle (the local league pair is the
  only measured comparison). [W,L]
- sg-bioeye-t4t5: +0.0717 [+0.005,+0.156] p=0.070, 22 vs 13 levels, 75
  matched rows, vs its scrambled control — the league's only HELPS;
  survived a hash-grade source audit; recorded as borderline at ship time.
  [L,W]
- Structural non-randomness: spectral radius 0.8289 vs 0.2219-0.2360 across
  three exact degree-preserving nulls (3.59x), at the deployed K=4,
  leak=0.3, gain=0.9 point; DN participation ratio 5.39 vs 14.33-18.54.
  The record's own caveat travels with it: "the strongest reproducible
  connectome result. It has not yet produced an ARC outcome advantage." [W]
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
  real 0.600 (band miss, p=0.0775); degree-preserving rewire 0.800 —
  HIGHER than real (sign test rewired>real p=0.996); shuffled-credit 0.400
  (real beats it, p=0.019 — the depression mechanism genuinely carries
  credit); matched one-shot perceptron 0.917. Scope verbatim: "what fails
  is the specific wiring's contribution and the expansion's fit to this
  stimulus statistics." [W,R]
- H-T4T5-CLASS25-MOTION refuted (ARC motion decode at validated class-2.5
  fidelity; 660 verified displacement events across 11 qualifying games;
  4 held-out games x 3 seeds): real 0.3875 held-out (above chance every
  seed); uniform-tau 0.3917 matches (p=0.94); degree-preserving rewire
  0.4306 exceeds (p=0.97); engineered shift-matcher 1.0000. [W,R]
- EB RING at two fidelities: class 1 — fixed-point attractor near 222 deg
  everywhere alive (settle map: robust point ~222 deg EPG mass ~0.21,
  vestigial ~90 deg mass 4e-4; writes on half the ring die; darkness
  A-vs-B decode exactly 0.5). Class 2 — 210 Shiu-canonical LIF configs,
  155 alive, EVERY one delocalized (min circvar 0.853 vs 0.6 band), all
  four seed angles settling at one fixed point (~192 deg); shuffled ring
  comparable. The compiled ring holds activity, not position. [W]
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
  games, outcomes converged anyway. [W,R]
- Teaching signal: 18 level advances vs 569 game-over frames across 75
  rows (~31:1). Depression-only plasticity gets no curriculum from 2
  positive examples. A property of the task signal, not the fly. [W]
- Track B trained head (520 params, CEM): genuinely connectome-dependent —
  trace ablation 0.2835 -> exactly 0.0000, unique observations 263.4 ->
  169.5 — and zero held-out generalization: 0.0000 on all 17 held-out
  games (training games 0.8858 vs untrained 0.5952; objective peaked at
  generation 16). [W]

## Interface lessons (the methods contribution)

- Class-1 verdict, stated as a theorem about the model class: no delay
  lines, no sparse-coding regime, no movable bump, anywhere in the swept
  gain x leak space (0/21 pass maps on T4/T5 DS, LC position, KC sparse,
  EB bump). "The class-1 verdict located the wall exactly." [W]
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
- EXPECTED-tier base rate: 0 for 13 on score-adjacent predictions (as of
  2026-10-03; twelfth recorded 2026-09-24, thirteenth 2026-10-03 =
  H-FLYGI-FLYBENCH-CALIBRATED, refuted on its frozen activation bar;
  "the measurements, as usual, all held"). [W,R]

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
  Algebras placed as runners-up; NO pure negative-results paper has ever
  placed in the money.
- Scope rule: facts about the world outside this repository are
  survey-dated claims ("found as of 2026-09-30"), never absolutes, and we
  did not survey non-connectome entrants for transfer measurements.

## Claim boundaries (must appear in any public artifact)

- Deployed agents' fly content = the compiled anatomical eye map only
  (static); neuronal dynamics OFF in all three 0.15 submissions.
- A leaderboard score establishes engineering, not fly computation.
- The connectome is anatomy, not a complete brain emulation. Nulls are
  about the model class at its fidelity, not the living fly — EXCEPT the
  two earned NOT-USEFUL verdicts, each with its scope: the MB for one-shot
  visual association on ARC at class-2 fidelity; T4/T5 for ARC motion
  decoding at validated class-2.5 fidelity. At class 1 the verdict was
  explicitly "NOT USEFUL: NONE — no prior null may be stated as a fact
  about the fly." Both earned verdicts required passed input gates. Scope
  words are part of the claim.
