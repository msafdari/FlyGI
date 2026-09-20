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
