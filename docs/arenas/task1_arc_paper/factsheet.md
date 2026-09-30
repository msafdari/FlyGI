# FlyGI paper fact sheet (DRAFT — every line must be verified against the repo record before use)

Provenance key: W=WORKLOG.md, L=LEAGUE.md, R=EXPERIMENTS.yaml. Line refs are
approximate (verify by grep, not line number).

## The system
- MaleCNS v1.0: 166,700 retained neurons; signed deployed graph 24,559,055
  directed edges; modulator-preserving runtime 24,994,595 edges. [W "Immutable
  data and runtime identity"]
- Full sparse compilation, float32 leaky-tanh rate dynamics (class 1); class-2
  per-type LIF/graded on extracted subcircuits (MB 627 PN/4,064 KC/2 APL/97
  MBON, 770,711 signed-count edges; EB-PB ring 148 neurons; optic-lobe patch);
  class-2.5 trained flyvis ensemble parameters for T4/T5. [W class-2 program]
- Controls used throughout: exact degree-preserving rewires, interface-matched
  no-graph bypass, shuffled-credit/time, scrambled-encoder twins, engineered
  equivalents; preregistered bands and kill rules in EXPERIMENTS.yaml.

## Kaggle submissions (real, scored)
- 56444435, 56459984: 0.00 (2026-09-22 era). Six total 0.00s early; six-zeros
  root cause = record=True construction crash (agents took zero actions),
  diagnosed 2026-09-26. [W]
- 56620463 (combo_light engineering baseline, v10 notebook): COMPLETE, 0.15.
- 56650224 (two FAP archetypes, v11): COMPLETE, 0.15.
- 56683298 (thirteen archetypes, v12, 2026-09-29 17:28 UTC): scored 0.15.
- Local official competition-mode gateway (35-min window): 0.551859
  (combo_light) -> 3.044167 (two archetypes) -> 28.742260 (thirteen
  archetypes; 73 levels, four full game wins). All engineered scaffold;
  neuronal_dynamics_active=false. [W]
- LB context: abstention floor 0.15 held three times => game-specific grammar
  transfer to hidden set measured zero, three times.

## Fly-positive results (measured)
- Eye map load-bearing: real retinotopic map completes level 1 at 2.59x human
  baseline vs scrambled-map twin 11.59x — 4.5x efficiency separation, identical
  machinery. Deployed (static anatomy metadata; no live dynamics). [W
  H-CONSEQUENCE-COUPLING day one]
- sg-bioeye-t4t5: +0.0717 [+0.005,+0.156] p=0.070 vs scrambled control — the
  league's only HELPS. [L]
- Structural: spectral radius 0.8289 vs 0.2219-0.2360 across three exact
  degree nulls (3.59x), survives exact in/out-degree preservation. [W]
- KC sparse coding validated at class 2: held-out median active fraction
  0.0741 in [0.03,0.15]; APL densification control +0.0098 (load-bearing);
  trivial alternatives 1.0000 dense; 10/12 configs pass. [W]
- T4/T5 DS validated at class 2.5: DSI 0.3216 (band >=0.30), T4 tiles four
  directions; attribution: trained per-pair strengths carry it (frozen 0.042;
  uniform-tau at trained strengths 0.3365). [W]
- MB reach test: MBON-lesion changes DN readout by 22.286% magnitude, 92.2%
  of entries. [W]

## Fly-negative results (earned, control-backed)
- H-MB-CLASS2-ASSOCIATION (refuted): held-out one-shot association — real MB
  0.600 (band miss, p=0.0775); degree-preserving rewire 0.800 (HIGHER);
  shuffled-credit 0.400 (real beats, p=0.019 — mechanism carries credit);
  matched one-shot perceptron 0.917. Input gates passed (PN share of KC drive
  62-87% vs 5% bar). [W]
- H-T4T5-CLASS25-MOTION (refuted): held-out ARC motion decode — real 0.3875
  (above chance every seed); uniform-tau 0.3917 (matches); degree-preserving
  rewire 0.4306 (exceeds); engineered shift-matcher 1.0000. [W]
- EB ring: class 1 fixed point ~222 deg everywhere alive; class 2: 210
  Shiu-canonical LIF configs, 155 alive, EVERY one delocalized (min circvar
  0.853 vs 0.6 band), all four seed angles -> one fixed point (~192 deg);
  shuffled ring comparable. Holds activity, not position, at two fidelities. [W]
- LC: class-1 object-position code sign-INVERTED at all 21 grid points (best
  rho -0.203 vs band +0.50); recognizer premise killed (real LC 0.438 / LH
  0.520 vs scrambled 0.510/0.579, chance 0.5, leave-one-game-out). [W]
- H-FLYHASH-STATE-KEY refuted; H-MBON-DAN-METAPLASTICITY null (gate delta
  crushed ~250-500x, plateaus); H-EFFERENCE null; taxis null; 4 learning
  nulls (sparse/dense/fair/dense-balanced); H-JEPA-SPONTANEOUS null
  (shuffled-time control +0.038 = real arm's own number).
- Teaching-signal fact: 18 level advances vs 569 game-overs across 75 rows
  (~31:1); depression-only plasticity gets no curriculum. [W]
- Track B trained head: connectome-dependent (trace ablation 0.2835 -> 0.0000)
  and zero held-out generalization (0.0000 on all 17 held-out games). [W]

## Interface lessons (the methods contribution)
- Class-1 verdict located the wall: no delay lines, no sparse-coding regime,
  no movable bump anywhere in the swept operating space — a theorem about the
  model class, not the fly. [W Requirement 1 RESULT]
- Given-usable-input rule: MB was taught with 0.00% sensory drive; T4/T5/LC
  evaluated on spatially scrambled input — nulls that were never about the
  fly. [AGENTS.md 2026-09-23 measurement]
- Coordinate-convention defect shipped in two submissions with six passing
  tests; random-clicking comparison found it (3.29x less exploration). [W]
- Partial-lead collapse observed three times (41-row +10.6% -> 0). [W]
- Expected-tier base rate: 0/11 (now 0/12?) on score predictions — VERIFY the
  current count before use; W says "eleven straight nulls" at AGENTS.md
  writing and "inference-failure number twelve" on 2026-09-24.

## Claim boundaries (must appear in any public artifact)
- Deployed agent's fly content = compiled anatomical eye map only (static);
  neuronal dynamics OFF in all three 0.15 submissions.
- A leaderboard score establishes engineering, not fly computation.
- Connectome is anatomy, not a complete brain emulation; nulls are about the
  model class at its fidelity, not the living fly, except where controls
  earned the NOT-USEFUL verdict (MB, T4/T5).
