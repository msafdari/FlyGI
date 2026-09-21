# FlyGI

FlyGI is a reproducible experiment that connects the complete MaleCNS v1.0
fruit-fly central-nervous-system graph to the interactive ARC-AGI-3 benchmark.
The scientific question is deliberately narrower than the joke: when the
interface and compute budget are matched, does the biological wiring make useful
closed-loop computations more accessible than rigorous null graphs?

This checkout implements **Milestones 0–1 and the Milestone 2 backend**:
repository and ARC submission plumbing, MaleCNS source acquisition and
verification, sparse graph compilation, the frozen SciPy/CPU leaky-rate
backend, provenance manifests, and acceptance tests. Check `WORKLOG.md` for the
full-data Gate 1 status. The ARC encoder/decoder loop, learning, plasticity, and
biological-performance claims are not included yet.

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
make notebook
```

Do not treat the random-agent notebook as a FlyGI baseline. Before spending a
competition submission, follow the staged
[local acceptance gates](docs/local_acceptance_gates.md): first validate the
multi-seed chance-control evaluator, then the full-graph dynamics, and finally a
causally live connectome agent on all public games.

`make baseline-local` runs the chance control strictly offline on all 25 cached
public games with seeds `0..4` and an exact 80-action ceiling. It writes an
immutable, Git-ignored JSON result under `results/random_baseline/`, including
full action traces, official local scorecards, timing, failures, hashes, and a
deterministic replay check. A nonzero exit status means an engineering gate
failed; a zero or positive ARC score is not itself a pass/fail criterion.

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
