# Task 5 (Brain-Score) — V1 kill-test runbook (user-executed)

> **EXECUTED 2026-10-04 — VERDICT KILL.** H-EARLYFILTER-BRAINSCORE-V1 refuted;
> Task 5 closed COMPLETE WITH VERDICT 2026-10-06 with no BrainModel submission
> built. Records: EXPERIMENTS.yaml and WORKLOG.md. The body below is preserved as
> written before the run; the session-branch pull line is historical and will not
> resolve once the release merges to main.

The kill test is registered (killtest_design.md,
H-EARLYFILTER-BRAINSCORE-V1) and its instrument is data-gated: the
cloud container has neither the compiled runtime nor the
brainscore-vision package (its hosts are egress-blocked). Unlike
Tasks 2 and 4 there is no dataset to download by hand — the benchmark
fetches its own stimuli and neural data on first load.

## 0. Preconditions (~1 min)

```bash
cd <FlyGI repo root>
git pull origin claude/admiring-goldberg-wtqkbg
python scripts/arenas/brainscore_killtest.py      # expect BLOCKED; the
                                                  # missing lines should
                                                  # include brainscore_vision
PYTHONPATH=src python -m pytest tests/test_brainscore_killtest.py -q  # 8 passed
```

## 1. Install brainscore-vision (one-time; your machine, your call)

This is a NEW third-party package execution — the AF-6 authorization
covered flybench only, so installing and running this one is
explicitly your decision. It is heavy (torch>=2.6, torchvision,
opencv, psycopg2-binary among 29 deps) and wants Python >= 3.11.
A separate venv keeps it out of the repo environment:

```bash
python3.12 -m venv ~/venvs/brainscore && source ~/venvs/brainscore/bin/activate
pip install brainscore-vision
pip install pyarrow scipy scikit-learn   # the repo's own needs, if absent
```

## 2. The one command

```bash
python scripts/arenas/brainscore_killtest.py
```

First run downloads the FreemanZiemba2013public stimuli + assembly
(their loaders, their S3). Then one settle + 6 simulated arms (real,
twin, 3 rewires — each a few hundred constant-drive stimuli, order
minutes each) plus the passthrough arm, and SIX benchmark metric calls
(their PLS + CV; the regression cache under ~/.result_caching makes
re-runs cheap). Expect tens of minutes end to end, a few GB RAM.

PASS / KILL / BLOCKED is frozen; the script exits 0 / 1 / 3. All
three are valid outcomes — no retries, no tuning on a KILL, no second
benchmark. An API-mismatch BLOCKED (the package's interfaces drift)
is a plumbing report, not a verdict: paste the log and I fix the
adapter, decision rules untouched, before any verdict-relevant number
is computed.

## 3. Report back

`results/arenas/brainscore_killtest.json` (gitignored — paste it),
plus: the per-arm center/error lines the run prints, the lattice line
(columns, scored early-filter cell count, pixels-assigned fraction),
the visual-degrees value it resolved, any unstable fractions, and the
branch tip if you committed an instrument fix. Claude-side then closes
H-EARLYFILTER-BRAINSCORE-V1 either way; on KILL, Task 5 ends with no
BrainModel submission built; on PASS, the full-eye scaling and the
actual submission get their own registered design next.
