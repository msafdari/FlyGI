# Task 6 (e-nose) — gas-drift MB kill-test runbook (user-executed)

> **EXECUTED by the user 2026-10-06 — VERDICT KILL (exit 1).** H-ALMB-GASDRIFT
> refuted; closed 2026-10-07, and the pre-stated dual close of the Task 4
> Keyword-FSCIL/MB limb executed the same day. Records: EXPERIMENTS.yaml and
> WORKLOG.md. The body below is preserved as written before the run; the
> session-branch pull line is historical and will not resolve once the release
> merges to main.

The kill test is registered (killtest_design.md, H-ALMB-GASDRIFT) and
its instrument is data-gated: the cloud container has neither the
compiled runtime, nor the fc2_kc_sparse passing result, nor the UCI
corpus (archive.ics.uci.edu is egress-blocked there). No new Python
packages beyond what the repo's own benchmarks already use (pyarrow,
scipy, sklearn) — nothing to authorize this time.

## 0. Preconditions (~1 min)

```bash
cd <FlyGI repo root>
git pull origin claude/admiring-goldberg-wtqkbg
python scripts/arenas/gasdrift_killtest.py       # expect BLOCKED; among the
                                                 # missing lines: --data-root
PYTHONPATH=src python -m pytest tests/test_gasdrift_killtest.py -q  # 9 passed
```

## 1. Download the UCI drift corpus (~70 MB zipped, one-time)

UCI ML repository, dataset 224 ("Gas Sensor Array Drift Dataset",
Vergara et al. 2012). Extract OUTSIDE the repo tree; the directory
must contain `batch1.dat` .. `batch10.dat`. (If your download is the
"at different concentrations" variant, dataset 270, the files carry
the same names and the parser reads both label dialects.)

## 2. The one command

```bash
python scripts/arenas/gasdrift_killtest.py --data-root <dir> --workers 8
```

Cost, declared in the registration: ~10 s per spiking sample
single-process, so the 5 simulated arms over ~480 samples plus per-arm
calibration project to ~7-8 h at --workers 1 and ~1 h at --workers 8
(the pool is decision-neutral: per-sample Poisson seeds are fixed, so
results are identical at any worker count). The per-arm calibration
lines print early — if a calibration misses its target the script
exits BLOCKED (3) before burning the full budget.

PASS / KILL / BLOCKED is frozen; exits 0 / 1 / 3. All three are valid
outcomes — no retries, no tuning on a KILL, no second corpus. A KILL
also closes the Task 4 Keyword-FSCIL/MB limb as not pursued (the dual
close is pre-stated in the registration and the hypothesis entry).

## 3. Report back

`results/arenas/gasdrift_killtest.json` (gitignored — paste it), plus:
the per-batch class lines from loading, the trainable-class set, the
per-arm calibration lines (theta / alpha / cal_median / hit_target),
the per-arm mean-over-batches and drift-curve lines, wall time and
worker count, and the branch tip if you committed an instrument fix.
Claude-side then closes H-ALMB-GASDRIFT either way and, on KILL,
executes the pre-stated dual close of the Task 4 MB limb.
