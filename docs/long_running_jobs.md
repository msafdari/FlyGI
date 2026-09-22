# Running long jobs on a laptop

FlyGI's experiments are hours long and run on a MacBook. This records what
actually happens, what was measured, and what to do about it.

## Does sleep kill a job?

No. macOS **suspends** processes on sleep and they continue on wake; nothing is
lost. A `nohup`-ed job also survives closing the terminal.

What does lose work:

- a reboot, a crash, or an out-of-memory kill;
- a job that dies partway through, because result artifacts were written only at
  the very end.

The second was the real exposure and is now fixed.

## Resumable runs

Both long jobs checkpoint continuously and can continue from the last completed
unit of work.

```bash
# Evaluation: every completed (seed, game) row is appended immediately.
uv run python scripts/evaluate_connectome.py --condition my-run --seeds 0 --games all \
  --action-budget 800 --checkpoint results/connectome_agent/my-run.rows.jsonl

# Interrupted? Re-run the identical command plus --resume. Completed rows are
# skipped, not repeated.
uv run python scripts/evaluate_connectome.py --condition my-run --seeds 0 --games all \
  --action-budget 800 --checkpoint results/connectome_agent/my-run.rows.jsonl --resume
```

```bash
make train-head          # writes a checkpoint after every CEM generation
make train-head-resume   # continues from the last completed generation
```

Delete the checkpoint to start fresh. The trainer refuses to resume a checkpoint
whose parameter count does not match the current `--feature-dim`, rather than
silently loading the wrong shape.

## Keeping the machine awake

`make train-head` wraps the run in `caffeinate -ims`: block idle sleep, keep
disks awake, and apply while on power. Note that **closing the lid still sleeps
an Apple Silicon laptop** unless an external display is attached. For an
overnight run, leave the lid open on power. Even if it does sleep, the job is
suspended rather than killed and resumes on wake.

## Free compute elsewhere

- **Kaggle notebooks** are the best option and the account is already set up:
  roughly 30 CPU hours per week, 12 hours per session. Running an experiment
  there consumes notebook quota, **not** competition submissions, which are a
  separate daily allowance. The compiled runtime is already a private Kaggle
  Dataset; the cached public games under `environment_files/` are about 3.9 MB
  and would need to be attached as a second dataset.
- **Google Colab** free tier works but idles out aggressively, which suits
  resumable jobs poorly.
- **GitHub Actions** is explicitly unsuitable here: the account's Actions
  minutes are a hard shared budget across private repositories, and a multi-hour
  sweep would consume it.

## Measured performance, and what is worth optimizing

The rate update is one sparse matrix-vector product over 24,559,055 edges.
Measured on this machine, single update: **39.11 ms**, about 25.6 updates per
second.

Batching several state vectors into one sparse-dense product, measured while two
evaluations were already running:

| Batch | Total | Per vector | Speedup per vector |
| ---: | ---: | ---: | ---: |
| 1 | 39.11 ms | 39.11 ms | 1.00x |
| 8 | 282.18 ms | 35.27 ms | 1.11x |
| 16 | 217.84 ms | 13.61 ms | 2.87x |
| 24 | 477.71 ms | 19.90 ms | 1.97x |

The numbers are noisy because the machine was loaded, but the shape is clear:
batching helps meaningfully from about 16 vectors, worth roughly **2-3x**, not
an order of magnitude. This matters for CEM training, where a whole population
can be advanced together, and not at all for a single agent playing one game.

Observed in earlier runs: three concurrent evaluations each sat at 58-59% CPU
rather than 100%. The workload is **memory-bandwidth bound**, not core bound, so
adding processes past about three gives little and batching is the better lever.

Not installed and not yet benchmarked: `torch` (an MPS backend might accelerate
sparse-dense products, though sparse support on MPS is historically patchy),
`mlx`, and `numba`. A dense GPU representation is impossible: 166,700 squared
float32 values is about 111 GB.

A further 2x is available by pruning small-magnitude edges, but that changes the
graph and would have to be declared and applied identically to every condition,
so it is a modeling decision rather than an optimization.
