# FlyGI

FlyGI is a reproducible experiment that connects the complete MaleCNS v1.0
fruit-fly central-nervous-system graph to the interactive ARC-AGI-3 benchmark.
The scientific question is deliberately narrower than the joke: when the
interface and compute budget are matched, does the biological wiring make useful
closed-loop computations more accessible than rigorous null graphs?

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


**The essence of the project, stated plainly: what computation does the fly's
innate wiring give us for free?** Not a network trained on the fly's shape, not
a network initialized from the connectome and then fitted -- the measured
synaptic graph itself, frozen, with its evolved modules doing whatever they
already do. The mushroom body's 4,064 Kenyon cells and 97 MBONs, the central
complex's ring attractor, the optic lobe's 892 retinotopic columns: these
circuits were shaped over roughly 400 million years for foraging, navigation and
learning in a real world. The question is how much of that transfers, unpaid, to
a benchmark nobody evolved for.

This is why every engineered component in this repository is on probation. A
scaffold that scores well while the connectome sits inert is a negative result
about the fly, however good it looks on a leaderboard. Whatever the agent scores,
the number that matters is the gap between the real graph and a degree-preserving
rewiring of it, because that gap is the only part that anatomy can claim.

## Where the project landed

Every circuit faced the same preregistered protocol — validate its biology at
a declared fidelity class, gate its input, then test on ARC against controls
(exact degree-preserving rewires, scrambled twins, bypasses, engineered
equivalents). The per-module verdicts, all measured:

| Circuit | Verdict |
| --- | --- |
| Eye map (static retinotopy) | **USEFUL, deployed** — level-1 action cost 2.59x human baseline vs 11.59x for its scrambled twin (4.5x), the one fly component in every scored submission |
| T4/T5 motion (13,585 neurons) | **NOT USEFUL** for ARC motion decoding at validated class-2.5 fidelity — real 0.3875 vs its own rewire 0.4306; engineered matcher 1.0000 |
| Mushroom body (4,064 KC) | **NOT USEFUL** for one-shot ARC association at class-2 fidelity — real 0.600 vs its own rewire 0.800; matched perceptron 0.917 |
| EB ring (compass) | UNVALIDATABLE at classes 1–2 — holds activity, not position (all 155 alive LIF configs delocalized) |
| LC object code | UNVALIDATABLE at class 1 — position code sign-inverted at all 21 operating points |

Kaggle record: six early 0.00s (a construction crash — zero actions played),
then three COMPLETE submissions (56620463, 56650224, 56683298) all scoring
**0.15**, the abstention floor, while the engineered grammar scaffold grew the
matched local gateway ~52-fold (0.551859 → 28.742260) — game-specific grammar
transfer to the hidden set measured zero, three times. Neuronal dynamics were
OFF in every scored run; a leaderboard score establishes engineering, not fly
computation.

After the ARC arm, the same preregistered rewire-control protocol ran on five
external arenas (2026-09-30 to 10-07): DSEC event-camera flow direction,
flybench, DVS128 gesture, Brain-Score V1, and UCI gas-sensor drift. Within
that program a degree-preserving rewire met or beat the real wiring six
consecutive times (seven registered instances counting the 2026-09-29 MB
association arm): H-T4T5-DSEC-DIRECTION, H-FLYGI-FLYBENCH-CALIBRATED,
H-T4T5-DVS-GESTURE, H-EARLYFILTER-BRAINSCORE-V1 and H-ALMB-GASDRIFT were
refuted, and one result was supported — the flybench adapter contract
(H-FLYGI-FLYBENCH-ADAPTER). Two measured positives rode along: on Brain-Score
V1 the early-filter dynamics roughly doubled the predictivity of their own
input (0.0690 vs 0.0330 — the first arm where a simulated circuit beat its
encoder), and the uniform flybench adapter rows beat the reference
configuration on all four summary rows. Our expected-tier score predictions
stand at 0 for 16; the measurements held. The full program synthesis —
instances, positives, open explanations, falsifiers — is
[docs/arenas/SYNTHESIS.md](docs/arenas/SYNTHESIS.md).

Full narrative: [WORKLOG.md](WORKLOG.md); every arm and verdict:
[LEAGUE.md](LEAGUE.md) and [EXPERIMENTS.yaml](EXPERIMENTS.yaml); the ARC Prize
2026 Paper Track writeup and figures:
[docs/arenas/task1_arc_paper/](docs/arenas/task1_arc_paper/).

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
