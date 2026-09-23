# FlyGI repository operating directive

These instructions apply to all work in this repository.

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

## State every claim at its tier

The claims in this repository that later needed reverting were never the
measurements; they were the bridges built on top of them. The record, audited
2026-09-23: statements of the form "I measured X under protocol Y" have held
essentially without exception, statements of the form "X, therefore Y" account
for every reversal (the binding-budget inference, the 41-row partial, the
gain-2.7 sweep run on unrepresentative input), and statements about what a
change will do to the score are 0 for 11.

So every claim carries its tier, in the same sentence that makes it:

- **Measured** -- this number, this protocol, stated together. Trustworthy at
  face value, and the tier to prefer when writing headlines.
- **Inferred** -- a measurement plus an untested bridge. Say the bridge out
  loud ("assuming exploration predicts conversion"), because the bridge is the
  part that fails.
- **Expected** -- a prediction about score or outcome. Always accompanied by
  the base rate, which at the time of writing is eleven straight nulls.

The headline sentence never carries broader scope than the measurement under
it: "the agent was action-blind" when only the connectome was measured is how
a true finding becomes a retraction. Scope words -- agent, connectome, circuit,
readout -- are part of the claim, not decoration.

This is a precision rule, not a tone rule. Enthusiasm is wanted; it just has
to be spent on the tier the evidence bought.

## Label every assumption where it lives

Any code written on a hypothesis or an assumption must say so, in a comment at
the place the assumption is encoded, and again in `WORKLOG.md` so it is visible
without reading the source. This is not a documentation preference. An
unlabelled assumption is indistinguishable from a measured fact six weeks later,
and this repository has already spent days on results that turned out to rest on
one.

Use the words. A comment that begins **ASSUMPTION** or **HYPOTHESIS** is
greppable; a comment that merely explains the code is not. State what was
assumed, what it would take to check it, and what breaks if it is wrong.

Distinguish three things explicitly, because they are routinely conflated:

- **Measured** -- observed in this repository, with the number and the command.
- **Established** -- taken from the literature or the connectome's own
  annotations, with the source.
- **Assumed** -- chosen by us because something had to be chosen. This includes
  every mapping from an ARC quantity onto a fly quantity, all of which are
  inventions until shown otherwise.

A declared assumption that turns out wrong is an ordinary cost of research. An
undeclared one that turns out wrong discredits everything measured downstream of
it, because no reader can tell which results depended on it.

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
