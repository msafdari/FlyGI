# FlyGI

What survives when you scramble a fly's wiring? FlyGI compiles 166,700
reconstructed MaleCNS neurons into a network whose connection weights derive
from anatomical synapse counts. It tests what that wiring contributes under
declared neural dynamics, input mappings, and learning rules.

The two ARC circuit probes scored higher after rewiring. In a separate
compass experiment, a model built from real connection counts held an
initialized heading. The same fitting procedure found no valid model on
three rewires. The leaderboard agents used
the fly's static eye map with neuronal dynamics off. [Read the paper](https://www.kaggle.com/competitions/arc-prize-2026-paper-track/writeups/flygi-connectome-attribution-audit)
or [inspect the release evidence](docs/arenas/task1_arc_paper/factsheet.md).

## Everything goes through the fly, or nothing goes at all

This is the project's first principle and it outranks every other consideration
in this repository, including the score.

FlyGI exists to find out what the fly's innate wiring computes for free. A
component that produces a result *without* the connectome carrying it is not a
smaller version of that finding -- it is a different project wearing this one's
name. So:

1. **Every computation the agent depends on must be performed by fly neurons.**
   If a capability can be obtained by writing Python instead, writing the Python
   is a failure, not a shortcut. The controller diffing grids in Python while
   13,585 T4/T5 motion detectors sit unread is the canonical example of the
   mistake.
2. **Encoders, decoders and transformations exist only to make fly modules
   usable.** They are plumbing, and their job is to hand a fly circuit the kind
   of input it evolved to read and to take from it the kind of output it evolved
   to produce. They are not where the intelligence is allowed to live. Any
   parameter in the plumbing that starts doing real work is a bug.
3. **A circuit must be given input it can actually use before any claim is made
   about it.** Measured on 2026-09-23: the mushroom body was taught while
   receiving 0.00% of its input from any driven sensory population, and the
   motion and object detectors were evaluated on spatially scrambled input. Both
   produced nulls. Neither null was about the fly.
4. **When a fly module cannot do the job, say so plainly and stop** -- do not
   quietly substitute an engineered component and keep the name. A recorded
   limit of the connectome is a real result. A scaffold that scores while the
   connectome idles is not.

The test to apply before adding anything: *if the connectome were replaced by a
degree-preserving null tomorrow, would this component still work?* If yes, it is
not part of this project.


The founding question asks what the *frozen* wiring gives us for free.
Two companion tracks let us separate that claim from other ways anatomy can
help. Some circuit tests use parameters learned elsewhere or fitted to a known
function. The competition controller uses engineering and a static anatomical
map. An ARC score from that controller measures the deployed system. To
attribute a capability to active fly circuitry, we compare simulations in
which changing the wiring changes the result.

## Where the project landed

In the local competition gateway, adding thirteen hand-built strategies
raised the score from **0.55 to 28.74** in matched 35-minute windows. The last
agent cleared **73 levels and won four games**. Kaggle displayed **0.15, 0.15,
0.15** for submissions 56620463, 56650224, and 56683298. All three used
the static eye map with recurrent dynamics off. The aggregate scores give
no breakdown by strategy on hidden games. [Local scorecard](results/manifests/gateway_fap11_20260929.json)
· [Deployment switch](kaggle/agent/my_agent.py)

| Experiment | Measured result under its protocol |
| --- | --- |
| Eye map in a click predictor | On the public game `r11l`, the real and scrambled maps cleared level 1 in **6 vs 199 actions** on one paired seed and **15 vs 255** on another. On the third seed only the real map cleared, in 57 actions. Across all 75 runs per map, 17 real-map and 16 scrambled-map runs cleared a first level. The comparison used the same historical coordinate convention in both arms. [Paired action counts and protocol](docs/arenas/task1_arc_paper/factsheet.md#eye-map-action-audit) |
| T4/T5 motion | With trained flyvis parameters, the simulated visual patch passed its direction-selectivity check. Held-out ARC displacement decoding scored **38.75%** for the real wiring and **43.06%** for the rewire. The matcher used to define the labels scored 100% by construction. [Motion record](results/manifests/verdict_program_20260930/t4t5_motion_arm.json) |
| Mushroom body | Held-out one-shot ARC visual association scored **60%** with the real wiring and **80%** after rewiring the tested projections. Scrambling the teaching signal scored 40%. A perceptron on the same input scored 91.7%. [Association record](results/manifests/verdict_program_20260930/mb_association.json) |
| Compass anatomy | Ring bandedness measured **0.5881** on the real counts. The maximum across 200 degree-preserving rewires was **0.3376**. In a separate structural test the fan-shaped body's directional geometry also exceeded the 200 rewires. [Structural protocols](docs/arenas/task9_cx_latent/killtest_design.md) · [Follow-up tests](docs/arenas/task10_menu/killtest_design.md) |
| Compass dynamics | The first three model classes failed their heading-retention criteria. A later model pooled 46 EPG and 42 Delta7 neurons into 16 units, enforced rotational symmetry, and fitted coupling gains to Biswas et al.'s attractor equations. **Two of three** configurations held an initialized pattern for all eight rotations in darkness, with drift rounding to 0.0°. The same search found **zero valid fits on three rewires**. The fitted parameters differed from the paper's. Sensory acquisition and steering were outside this retention test. [Protocol](docs/arenas/task10_menu/killtest_design.md) · [Simulation](scripts/arenas/cx_biswas_killtest.py) |
| LC object position | The class-1 readout gave a negative position correlation at all 21 tested operating points. The ARC task comparison stopped at that validation check. [Circuit record](results/manifests/verdict_program_20260930/visual_motion.json) |

The whole-graph ARC interface also failed to distinguish a validated
long-memory reservoir on its registered score comparisons. At roughly +0.1
score sensitivity, the ARC nulls bound what that interface could detect.
The external benchmarks ask different questions. On Brain-Score V1, the
visual circuit raised predictivity over its own input (0.0690 vs 0.0330),
and all three rewires matched or exceeded it. On FlyBench, applying
terminal-aware synapse placement improved the real circuit's registered
metrics. The rewire did not receive that treatment, leaving the interaction
between placement and topology open. Across the program, the register counts
**16 score-related predictions and zero successes**. [Arena synthesis](docs/arenas/SYNTHESIS.md)
· [Experiment registry](EXPERIMENTS.yaml)

The [worklog](WORKLOG.md) records what ran and when. The [league](LEAGUE.md)
reports comparisons, and the [paper materials](docs/arenas/task1_arc_paper/)
contain the figures and release copy.

## Quick start

Python 3.12 and [`uv`](https://docs.astral.sh/uv/) are required.

```bash
uv sync --extra dev
uv run pytest
uv run flygi --help
uv run flygi validate all
```

`validate all` is presence-aware and reports absent large assets without
pretending they were checked. Use `uv run flygi validate all --require-data`
for a fail-closed full-data validation.

The three upstream MaleCNS files total about 1.2 GB. They are never downloaded
during tests and are ignored by Git. To fetch them intentionally:

```bash
uv run flygi data fetch --release male-cns:v1.0 --config configs/literal_rate.yaml
uv run flygi graph build --config configs/literal_rate.yaml
uv run flygi validate all --require-data
```

The first command streams files to temporary partial paths, calculates SHA-256,
and records source metadata. Supply known hashes to make acquisition fail closed;
see [data/README.md](data/README.md). The build command validates actual Feather
schemas before interpreting any column and refuses to overwrite an existing
runtime asset.

The full-connectome dynamics gate is intentionally separate from unit tests
because its 10,000-step stability run takes minutes on a laptop:

```bash
make benchmark-full-graph
```

It hash-checks and loads the compiled graph once, exercises the exact declared
rate equation, checks deterministic CPU execution and descending-neuron input
sensitivity, runs 10,000 internal steps, and profiles `K = 1, 2, 4, 8`. The
immutable detailed result is written beneath the Git-ignored `results/dynamics/`
tree. No machine-dependent speed threshold is used as a correctness criterion.

## ARC-AGI-3 workflow

The Kaggle adapter follows the official starter contract at pinned upstream
revision `eeb1535404f321d280a8f9194bbc1d7aca5f05fc`:

```bash
make setup
make play-local GAME=ls20
make verify-local
make baseline-local
make calibrate-sampler
make connectome-local
make notebook
```

Do not treat a successful packaging notebook as a scored FlyGI result. Before
spending a competition submission, follow the staged
[local acceptance gates](docs/local_acceptance_gates.md): first validate the
multi-seed chance-control evaluator, then the full-graph dynamics, and finally a
causally live connectome agent on all public games.

`make baseline-local` runs the chance control strictly offline on all 25 cached
public games with seeds `0..4` and an exact 80-action ceiling. It writes an
immutable, Git-ignored JSON result under `results/random_baseline/`, including
full action traces, official local scorecards, timing, failures, hashes, and a
deterministic replay check. A nonzero exit status means an engineering gate
failed; a zero or positive ARC score is not itself a pass/fail criterion.

`make calibrate-sampler` ranks a fixed three-point sampler grid using only
behavioral and engineering measurements; score and level progress are excluded.
`make connectome-local` then runs the frozen signed policy on all 25 cached games
and five seeds with the exact 80-action ceiling.

Kaggle submission requires accepting the competition rules and adding a local
token; no credentials belong in Git. See [kaggle/README.md](kaggle/README.md).

## Data and claims

MaleCNS v1.0 was released on 2026-06-08; its Cell paper was published on
2026-09-03. The Male CNS dataset is a collaboration among FlyEM at HHMI Janelia,
the University of Cambridge Department of Zoology, the MRC Laboratory of
Molecular Biology, and Google Research, and is licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Publications should
cite *Sexual dimorphism in the complete connectome of the Drosophila male central
nervous system*, [doi:10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015).
FlyGI runtime assets are modified derivatives and are neither an official release
nor endorsed by the data creators.

FlyGI records observed counts from the source tables instead of baking
community-reported counts into validation. A graph that runs is not evidence that
a fly understands ARC, and a score is not attributed to biological topology
without degree-preserving and parameter-matched controls.

- Dataset: <https://male-cns.janelia.org/download/>
- ARC-AGI-3 Kaggle starter: <https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter>
- Experiment details: [docs/experiment.md](docs/experiment.md)
- Modeling limits: [docs/modeling_assumptions.md](docs/modeling_assumptions.md)

## License

Code is licensed under MIT No Attribution (MIT-0); see [LICENSE](LICENSE).
MaleCNS data is not redistributed
here and remains subject to its CC-BY terms. Upstream ARC components retain their
own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
