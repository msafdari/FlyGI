# Task 4 (NeuroBench) — DVS Gesture kill-test runbook (user-executed)

> **EXECUTED 2026-10-03 — VERDICT KILL.** H-T4T5-DVS-GESTURE refuted (real below its
> degree-preserving rewire in all 3 seeds AND below circuit-free event-count
> features); Task 4 fully closed 2026-10-07 (Keyword-FSCIL/MB limb closed as not
> pursued via the dual close pre-stated in H-ALMB-GASDRIFT's registration). Records:
> EXPERIMENTS.yaml and WORKLOG.md. Body preserved as the pre-run record: "expect 9
> passed" predates the instrument fix efd06a9 (the suite now collects 11 tests), and
> the session-branch pull line will not resolve once the release merges to main. (killtest_design.md, H-T4T5-DVS-GESTURE)
and its instrument is data-gated: the cloud container has neither the
dataset (hosts egress-blocked) nor the compiled runtime. The decision
deliberately does NOT use the neurobench package — nothing new to
install beyond what the Task-2/3 runs already needed (sklearn included,
from the motion arm).

## 0. Preconditions (~1 min)

```bash
cd <FlyGI repo root>
git pull origin claude/admiring-goldberg-wtqkbg
python scripts/arenas/dvs_killtest.py        # expect BLOCKED with exactly
                                             # ONE missing line: --data-root
PYTHONPATH=src python -m pytest tests/test_dvs_killtest.py -q   # expect 9 passed
```

## 1. Download DVS128 Gesture (~2.4 GB, one-time)

From IBM's official DVS128 Gesture Dataset page (research.ibm.com —
accept their terms; the file is `DvsGesture.tar.gz`). Extract OUTSIDE
the repo tree. The extracted directory must contain
`trials_to_train.txt`, `trials_to_test.txt`, the `*.aedat` files and
their `*_labels.csv` companions — that is the layout the harness reads.

## 2. The one command

```bash
python scripts/arenas/dvs_killtest.py --data-root <extracted DvsGesture dir>
```

Expected cost: the trial parse prints per-file sanity stats first (the
AEDAT 3.1 reader is ours — validated on synthetic bytes in-cloud; if a
real file trips the out-of-frame sanity flag at more than a trickle,
stop and report rather than pushing through). Then ~2 simulated arms
over the train-union + test windows, plus 3 rewired instances — order
30-90 min and a few GB RAM, single process.

PASS / KILL / BLOCKED is frozen; the script exits 0 / 1 / 3. All three
are valid outcomes — no retries, no tuning on a KILL.

## 3. Report back

`results/arenas/dvs_killtest.json` (gitignored — paste it), plus: the
per-seed accuracy lines the run prints (real / twin / null /
event_count), the drive-norm scalar, any parser sanity flags, and the
branch tip if you committed an instrument fix. Claude-side then closes
H-T4T5-DVS-GESTURE either way; on KILL, Task 4's T4/T5 limb ends with
no NeuroBench integration built and the Keyword-FSCIL/MB limb needs
your explicit go (its priors are in the delta doc); on PASS, the
NeuroBench harness integration gets its own registered design next.
