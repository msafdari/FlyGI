# FlyGI repository operating directive

These instructions apply to all work in this repository.

## Resume from the durable record

1. At the beginning of every work session, read `WORKLOG.md` before planning or
   editing.
2. After context compaction, rehydration, handoff, or uncertainty about prior
   work, reread `WORKLOG.md`, inspect `git status`, and inspect the latest Git
   commits before continuing. Do not reconstruct project status from memory.
3. Treat `WORKLOG.md` as the durable narrative record and Git history as the
   authoritative record of file changes. Reconcile any disagreement before
   proceeding.

## Keep the worklog current

1. Update `WORKLOG.md` after every meaningful milestone, design decision,
   external-data observation, validation result, blocker, or change to the next
   steps.
2. Record measured facts and exact commands or configurations when they matter
   for reproducibility. Clearly distinguish observed values from expected,
   inferred, or independently verified values.
3. Keep the current limitations and ordered next steps accurate. Remove or mark
   completed items instead of allowing stale plans to accumulate.
4. Never record credentials, access tokens, private keys, cookies, or other
   secrets in the worklog.

## Checkpoint and push periodically

1. Create small, coherent Git checkpoints throughout the work instead of one
   large final commit. A checkpoint is due after a verified sub-milestone and
   before beginning a materially different subsystem; during long work, do not
   allow more than roughly one hour of completed source work to remain only in
   the working tree.
2. Before each checkpoint, inspect the staged diff, run checks proportional to
   the change, update `WORKLOG.md`, and confirm that no secrets or large generated
   artifacts are staged.
3. Use descriptive commit messages and push completed checkpoints to the
   configured private `origin` regularly. Confirm that the local branch tracks
   the intended remote branch and that the push succeeded.
4. Do not rewrite or force-push shared history unless the user explicitly asks.
   Preserve unrelated user changes and never create an automatic commit from an
   unreviewed or failing tree.

## Prove the premise before building the thing

This repository has repeatedly produced working, well-tested components that
were never worth building. The cost is not the bugs, which are cheap to fix. The
cost is building five hundred lines to answer a question a thirty-line probe
answers.

Recorded instances, all from a single week:

- a coordinate head shipped in two competition submissions, with six passing
  tests, that explores **3.29x less than clicking at random** in the games where
  clicking is the only legal action;
- a 520-parameter trained head with a CEM trainer, parallel workers,
  checkpointing and an ablation harness, which turned out to have **zero
  held-out generalization** -- all of its gain sat on its own training games;
- a plasticity rule, its config, policy wiring, factory wiring and a
  falsification control, built before checking that the teaching gate could fire
  at all; on the real graph it moved **exactly zero weight**;
- a loop-escape layer calibrated carefully between three strengths, never once
  compared against having it switched off, until days later.

### The three rules

1. **Name the trivial alternative before writing the component.** Write down,
   in the plan, what the dumb version is -- random, constant, identity, absent --
   and the single command that compares against it. A component whose trivial
   alternative cannot be named is a component whose purpose is not understood.

2. **Kill the premise at the smallest scale that can kill it, first.** Before the
   full build, run the cheapest experiment that could show the idea does not
   work. Random parameters on held-out games. One rewarded update on the real
   graph. One game against chance. Minutes, not hours, and before the module
   exists.

3. **"It runs" is not a milestone.** A smoke test, a passing suite and a clean
   commit are not evidence that anything was gained. The milestone is "it beats
   the trivial alternative" or "it does not". Commit either; never commit the
   absence of the comparison as though it were progress.

### Why this is the fast path, not the careful one

Speed and rigor are not in tension here, and treating them as opposites is what
produced the list above. The controls in this project -- degree-preserving
nulls, the interface-matched bypass, the held-out split, the trace ablation --
were each cheap and each **found something real**. The expensive mistakes came
from building before checking, not from checking.

When urgency and a cheap check conflict, say so in one line and run the check.
It is almost always shorter than the build it protects.

### Correctness tests are not comparison tests

Tests asserting valid output, preserved invariants, finite activity and respected
masks establish that a component does not crash. They establish nothing about
whether it helps. Every component that changes behaviour needs at least one test
or recorded measurement against its trivial alternative, and that comparison
belongs in the same commit as the component.

## Keep large and external artifacts out of normal Git history

Do not commit raw MaleCNS downloads, compiled graph arrays, cached ARC games,
virtual environments, vendored checkouts, recordings, generated notebooks,
logs, credentials, caches, or build outputs. Keep the corresponding ignore rules
intact. Commit small source files, configs, tests, documentation, and reviewed
provenance records. If a deployment later needs binary assets, use a versioned
release asset or Kaggle Dataset with hashes rather than normal Git history.

Before every push, review at least:

```bash
git status --short --ignored
git diff --cached --check
git diff --cached --stat
```
