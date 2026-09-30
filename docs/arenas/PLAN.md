# Arena program plan — 2026-09-30

User directive (2026-09-30): execute all eight ranked arena tasks from
docs/next_arenas_survey_20260930.md, top rank first, one task finished
completely before the next; due-diligence check before each task; document
continuously (WORKLOG, periodic commits); track assumptions/hypotheses in
docs/arenas/ASSUMPTIONS.md. Task 1 must additionally yield a LinkedIn blog
post and an X post that lead to the FlyGI GitHub repo once public.

Due diligence base: ten-agent web verification run 2026-09-30 (workflow
wf_77415764-bf9; full reports in the session record). kaggle.com,
arcprize.org, dsec.ifi.uzh.ch, arxiv.org, mlcommons.org, brain-score.org,
archive.ics.uci.edu are egress-blocked from this container, so those facts
are SOURCED from search extraction, not primary pages — each is in the
assumptions register with a verification owner.

Standing constraints (measured this session): this cloud container has no
Kaggle credentials and no compiled MaleCNS runtime (data/processed absent).
Anything needing either is prepared here and executed by the user (or a
local machine), with an exact runbook.

## Hard calendar (all sourced unless marked)

| Date (UTC) | What | Task |
| --- | --- | --- |
| 2026-10-26 | ARC entry/team deadline (paper-track comp must be joined too) | 1 |
| 2026-11-02 | ARC final code-submission deadline | 1 |
| **2026-11-08/09** | **Paper Track writeup deadline (discrepancy; plan for 11-08)** | 1 |
| 2026-11-30 | IJCNN 2027 competition-proposal deadline | 8 |
| 2026-12-04 | ARC winners announced | 1 |
| ~Jan-Feb 2027 | Telluride 2027 call opens; CVPR 2027 challenge windows form | 8 |
| ~H1 2027 | MLPerf Tiny v1.5 window (inferred from cadence; join WG 8+ weeks early) | 7 |
| rolling | DSEC-Flow, FlyBench, NeuroBench leaderboard, Brain-Score, e-nose paper | 2-6 |

## Task 1 — ARC Prize 2026 Paper Track  [ACTIVE]

Due-diligence verdict: RELEVANT and eligible. "The code submission need not
achieve a high score"; our three COMPLETE 0.15 submissions (56620463,
56650224, 56683298, account megusalexandrus) satisfy the gate. Judged
artifact = Kaggle Writeup <=1,500 words + Media Gallery + attached PUBLIC
notebook + optional Project Link; judges Knoop & Chollet; six equal 0-5
criteria (Accuracy, Universality, Progress, Theory, Completeness, Novelty);
>4.5 average qualifies for the $375K Outstanding pool. Winner precedent:
CompressARC took 3rd at ~20% accuracy; bio-flavored entries (ARC-NCA, VSA)
placed; NO pure negative-results paper has ever placed -> frame as
novel-method-plus-rigorous-analysis, nulls as the evidentiary backbone, the
eye-map positive and the controls methodology as the spine.

Premise: the record is the paper. Trivial alternative: not writing it.
Kill test: user eyeballs the two rules pages once (deadline 11-08 vs 11-09,
media/notebook requirements, licensing wording) before we hard-commit.

Work breakdown (in-container unless marked USER):
1. Fact sheet verified against repo record (adversarial check, workflow).
2. Writeup: multi-angle drafts -> judge panel -> synthesis -> fact-check ->
   word-limit pass. Every claim tiered per AGENTS.md.
3. Figures + cover image for Media Gallery (dataviz discipline).
4. Public demonstration notebook (.ipynb, runnable narrative of methods and
   controls; adapted from the embedded-source path, no private assets).
5. Public-release package: README refresh, license decision (MIT -> MIT-0
   or CC0 — USER decision as copyright holder), secrets/PII audit, MaleCNS
   data-licensing note, repo-public step (USER).
6. LinkedIn article draft + X post draft pointing at the public repo.
7. Submission runbook (exact Kaggle clicks, same-account requirement,
   deadlines) (execution: USER).
Exit criteria: all seven artifacts committed; user has the runbook; posts
drafted; nothing left that this environment can do.

## Task 2 — DSEC-Flow (event-camera optical flow)  [QUEUED]

Confirmed open, rolling, auto-eval server. Floor on the board: MultiCM EPE
3.472 (model-free); SOTA ~0.66; E-RAFT 0.788. Submissions need an eventual
report (6-month deletion rule) and an institutional-email account (gmail is
a risk). Egress currently blocks dsec/download hosts -> data work runs on
the user's machine or after a proxy allowlist change. Claim tier available
to us: connectome-constrained + physiology-fitted (class 2.5), zero
task-trained — frozen counts (DSI 0.042) would measure noise and that is
pre-declared. Kill test BEFORE any plumbing: one training sequence (DSEC
train GT 3.7 GB, or MVSEC indoor_flying1 ~3.8 GB), T4/T5 vs event-count
argmax vs zero-flow/global-translation vs degree-preserving null. Ship only
if the circuit beats the trivial alternatives; a recorded loss is a
recordable result but not an entry.

## Task 3 — FlyBench  [QUEUED]

Confirmed active; we would be external contributor #1. Path: pip install,
`flybench run -c toy` (~2 min), then MaleCNS via anonymous
`flybench fetch-neuprint` (~5 min; egress to neuprint.janelia.org untested)
and `flybench build`. Open division custom Simulator interface; declare
n_free_parameters and fit_data; PR one results JSON; "verified" badge
requires the maintainer to rerun our stack -> keep it pip-installable.
Substrate caveat: flybench MaleCNS = 176,422 neurons / 6.29M edges at >=5
synapses; ours = 166,700 / 24.99M — same source, different compilations;
reconcile before any cross-claim. Targets: first VERIFIED MaleCNS rows; our
Litwin-Kumar-calibrated MB vs their PN-broadcast finding; their terminal-
synapse + SFA mechanisms fed back into our ring/MB sweeps.

## Task 4 — NeuroBench  [QUEUED]

No active challenge (THOR 2026 closed July/Aug; next edition unannounced).
Leaderboard has never taken a cold self-submission — it is maintainer-
curated; every accepted row has an arXiv report. Plan: DVS Gesture (native
T4/T5 fit, no leaderboard — result is a report + example PR) and/or Keyword
FSCIL (MB fit, encoder risk, leaderboard exists). ESN precedent legitimizes
fixed-recurrence + linear readout. Kill test: harness metrics on one task
offline vs degree-preserving null + event-count features before anything
else. Engagement via neurobench@googlegroups.com with the report.

## Task 5 — Brain-Score  [QUEUED]

Rolling, free, MIT runs compute. Pure-NumPy precedent on the live board
(pixels, gabor, hmax) — wrapper feasibility settled. Submission = public
GitHub PR (zip auto-converts); no private path. Model = activations model
over named fly populations as layers; region map either explicit (labelled
ASSUMPTION) or Brain-Score auto-select (records the assumption implicitly —
choice goes in WORKLOG). Kill test: local pre-score via pip
brainscore_vision on one public V1 benchmark: fly vs pixels vs
degree-preserving null. Needs the compiled runtime -> user machine likely.

## Task 6 — e-nose / gas-sensor drift  [QUEUED]

No open competition (DREAM 3 nonexistent; 2026 conference windows passed) —
deliverable is a paper + public repo. UCI drift corpus has a published
integrity critique (Dennler 2022): never headline UCI-only; pair with the
2025 Sci Data one-year MOX dataset (no baselines yet — we can define the
protocol, every choice labelled). Near-competitor exists (Aug 2026
engineered olfactory SNN, arXiv 2608.24288): our claim is the MEASURED
connectome, head-to-head with that paper. Honest-protocol UCI numbers sit
~48-75%. Kill test: UCI batch-1 through compiled AL/MB with a fixed random
channel->glomerulus map: (i) nonzero driven fraction, (ii) KC separation of
6 gases vs same readout on raw features.

## Task 7 — MLPerf Tiny  [QUEUED]

v1.4 published July 2026 (an individual submitter exists — path is real);
v1.5 unannounced, inferred H1 2027. Requirements: free membership + working
group joined >=8 weeks before deadline (USER: join early), CLA, MLCommons
Runner, Cortex-M class DUT + energy monitor hardware (~$100-900). Open
division admits arbitrary models; AD reference ~0.80 AUC, target 0.85.
Constraint: the MCU port must BE the circuit, not a distilled surrogate.
Kill test: MB novelty circuit on ToyADMOS offline vs the reference
autoencoder and a trivial distance-to-normals baseline.

## Task 8 — Community venues  [QUEUED]

Near-term hard date: IJCNN 2027 competition PROPOSALS due 2026-11-30
(proposing = organizing burden — USER decision; default posture: enter,
not propose). Telluride 2027: dates fixed Jun 27-Jul 16; call ~Jan-Feb
2027 (USER: subscribe to neuromorphs-announce). CVPR 2027: event-vision
workshop 6th edition expected (challenges ~Feb-Mar 2027); VAND 5.0
projected Apr-May 2027 (weak fit — only if MB kill tests pass). NeurIPS
2027 call ~Feb-Mar 2027. Deliverable: monitoring calendar with scheduled
check-in triggers + a one-page application kit per venue.

## Operating rules for the whole program

1. Every task opens with a due-diligence delta check and closes with a
   WORKLOG entry, commit, and push. No more than ~an hour of work sits
   uncommitted.
2. Every mapping from an external quantity onto a fly quantity is an
   ASSUMPTION in docs/arenas/ASSUMPTIONS.md at birth, updated on
   confirm/invalidate, never silently dropped.
3. Kill tests run before builds, against named trivial alternatives; a
   failed kill test ends the task with a recorded verdict (that is a
   completed task, not an abandoned one).
4. Claim tiers in every outward artifact; the deployed-fly-content boundary
   (static eye map only; dynamics OFF in scored submissions) appears in
   every public statement. Expected-tier statements carry the 0-for-12 base
   rate (canonical count as of 2026-09-26; verified 2026-09-30).
5. Outward-facing steps (Kaggle actions, repo-public, license change,
   posting, account creation, emails to maintainers) are prepared here,
   executed by the user.
