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

This checkout implements **Milestones 0–3 and part of Milestone 4**: repository
and ARC submission plumbing, MaleCNS acquisition and verification, unsigned and
heuristic-signed sparse graph compilation, the frozen SciPy/CPU leaky-rate
backend, a live seeded closed loop from ARC frame to legal ARC action through
the full 166,700-neuron graph, seeded directed degree-preserving nulls, an
interface-matched no-recurrent-graph bypass, a score-blind sampler calibration,
fail-closed Kaggle packaging, provenance manifests, and 189 tests. Learning
(Track B) and plasticity (Track C) are not implemented.

**Current results, in short.** The agent works and is not better than a bypass.
Gate 2 passed on all 25 public games with zero trainable parameters. The real
signed graph and the interface-matched bypass scored an identical mean of
0.190476, each completing one level in one game out of 25; the degree-preserving
null scored zero; the random control scored 0.050626. The connectome agent
explores *less* than chance. Separately, the real graph does separate cleanly
from its degree-preserving nulls on dynamical measures — spectral radius 0.8289
against 0.2309 ± 0.0078 over three seeds, a ratio of 3.59 — but that structural
difference produced no ARC advantage. A post-hoc engineering repair now uses
seeded scale-aware action/coordinate sampling and grounded click exploration;
the score-blind calibration froze action temperature 0.15 and coordinate
temperature 0.20 before the next full score-bearing gate. No leaderboard
submission has been made and no biological advantage is claimed. See
[WORKLOG.md](WORKLOG.md).

See [WORKLOG.md](WORKLOG.md) for the latest reproducible checkpoint, measured
full-data results, current limitations, and ordered next steps.

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

Code is MIT-licensed; see [LICENSE](LICENSE). MaleCNS data is not redistributed
here and remains subject to its CC-BY terms. Upstream ARC components retain their
own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
