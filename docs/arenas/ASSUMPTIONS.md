# Arena program — assumptions & hypotheses register

Living register per the program's operating rule 2. Statuses: OPEN (unchecked),
CONFIRMED (checked, holds), INVALIDATED (checked, fails — record consequence),
RETIRED (no longer load-bearing). Tiers: SOURCED (web, link-backed, primary
page unverified), ASSUMED (our choice), INFERRED (measurement + bridge),
MEASURED (checked in this repo/session). Update in place; never delete rows —
strike through and mark instead.

## Program-wide

| ID | Statement | Tier | Status | Check / consequence if wrong |
| --- | --- | --- | --- | --- |
| P-1 | This container has no Kaggle credentials and no compiled MaleCNS runtime; those steps are user-executed | MEASURED (2026-09-30: no ~/.kaggle, no data/processed) | CONFIRMED | Runbooks must be exact; if wrong, we can execute more ourselves |
| P-2 | Egress proxy blocks kaggle.com, arcprize.org, dsec.ifi.uzh.ch, download.ifi.uzh.ch, arxiv.org, mlcommons.org, brain-score.org, archive.ics.uci.edu, huggingface.co, neurobench.ai | MEASURED (agent fetch attempts, 2026-09-30) | CONFIRMED | Re-test per task; user may extend allowlist |
| P-3 | The user intends the FlyGI repo to become public (stated 2026-09-30: posts "lead to the FlyGI github repo where the findings and code is public") | user statement | CONFIRMED | The public-release step itself remains the user's action |

## Task 1 — ARC Paper Track (AP-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AP-1 | Paper deadline is 2026-11-09 23:59 UTC (Kaggle page); one extraction says arcprize.org shows 11-08. We plan to 2026-11-08 | SOURCED (2 extractions) | OPEN | USER: eyeball both pages once. If 11-08 is real, plan already safe |
| AP-2 | Low-score submissions are eligible ("code submission need not achieve a high score"); our 0.15 rows qualify | SOURCED (cross-confirmed 2+) | OPEN->high confidence | USER eyeball. If wrong, task collapses to arXiv+posts only |
| AP-3 | Writeup must be submitted from the same account/team as the code submission (megusalexandrus) | SOURCED | OPEN | USER confirms on rules tab; determines who clicks submit |
| AP-4 | Submitter-authored code must be open-sourced under CC0 or MIT-0 (plain MIT NOT listed as sufficient) | SOURCED | OPEN | USER decision to relicense; blocking for prize eligibility, not for submitting |
| AP-5 | Writeup requires <=1,500 words + Media Gallery + attached public notebook; optional Project Link | SOURCED | OPEN | Shapes all Task-1 artifacts; verify wording on rules tab |
| AP-6 | MaleCNS-derived compiled arrays may be redistributed via the existing Kaggle dataset and a public repo (data license permits) | ASSUMED (v8 dataset already public-facing on Kaggle infra; license text unverified) | OPEN | Check male-cns:v1.0 license/attribution terms before repo-public; if restrictive, ship code + build scripts, not arrays |
| AP-7 | "Progress" rubric criterion will score low (~1-2/5) for a biological-substrate paper; compensate on the other five | INFERRED (rubric text + precedent) | OPEN | Affects framing only |
| AP-8 | No pure negative-results paper has placed in the money; nulls must be controls inside a novel-method narrative, not the headline | SOURCED (2024+2025 winner lists) | CONFIRMED (as historical fact) | Framing rule for the writeup |
| AP-9 | A fourth code submission before 2026-11-02 is NOT required; existing three suffice | SOURCED | OPEN | If a fresh linked submission is required, user must re-run the v12 submit path before 11-02 |

## Task 2 — DSEC-Flow (AD-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AD-1 | Benchmark account requires an institutional email; gmail risky | SOURCED (sibling disparity page verbatim) | OPEN | User may need an academic address or organizer contact |
| AD-2 | Entries without an eventual report/paper are deleted after ~6 months | SOURCED | OPEN | Entry and report ship together |
| AD-3 | T4/T5 at class 2.5 (trained flyvis physiology) can produce direction estimates from event streams; frozen counts (DSI 0.042) cannot | MEASURED (repo, ARC context) + INFERRED (transfer to DSEC input) | OPEN | The kill test measures exactly this |
| AD-4 | Dense-flow decoding (sparse lattice -> 640x480 metric flow) can stay trivial plumbing (fixed linear readout + interpolation) without doing the intelligence | ASSUMED | OPEN | Ablate decoder on null wiring; if decoder carries the result, record and stop |
| AD-5 | Driving-scene flow magnitudes exceed a single EMD's temporal band; multi-timescale sampling of the same circuit is required | INFERRED (literature) | OPEN | Label at the code site if built |

## Task 3 — FlyBench (AF-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AF-1 | flybench MaleCNS (neuprint, >=5-syn, 176,422 neurons / 6.29M edges) and our compile (166,700 / 24.99M) are different compilations of the same source; results are not directly comparable across them | MEASURED (both repos read) | CONFIRMED | Any cross-claim states the substrate; consider running our params through THEIR build |
| AF-2 | neuprint.janelia.org is reachable from this container for the anonymous fetch | ASSUMED | OPEN | Test at task start; else user machine |
| AF-3 | Our simulator stack can implement their Simulator/run->SimResult interface without violating their no-fitting-on-tasks rule (our calibrations were done on OUR protocols, not their tasks) | INFERRED | OPEN | Declare n_free_parameters + fit_data explicitly; ask maintainer if ambiguous |

## Task 4 — NeuroBench (AN-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AN-1 | Leaderboard acceptance is maintainer-gated and has only ever ingested paper-baseline or challenge rows; a cold entry is a negotiation | SOURCED (commit history) | OPEN | Budget an email + report; no leaderboard promise |
| AN-2 | DVS Gesture readout can stay a linear map over T4/T5 population activity | ASSUMED | OPEN | Null + event-count controls in the kill test |

## Task 5 — Brain-Score (AB-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AB-1 | Any fly-neuropil -> V1/V2/V4/IT layer map is an invention (no homology); auto-select is the less-assumptive option but still encodes it | ASSUMED (structural) | CONFIRMED (as an assumption we accept) | Record the choice in WORKLOG either way |
| AB-2 | Submission makes the model code public immediately (PR into brain-score/vision) | SOURCED | OPEN | Sequence after repo-public decision |
| AB-3 | Compiled arrays can be served to their sandbox via a public versioned URL | SOURCED (their convention) + ASSUMED (our hosting) | OPEN | Needs AP-6 resolved first |

## Task 6 — e-nose (AE-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AE-1 | Sensor-channel -> ORN/glomerulus assignment (16 or 62 channels onto ~50 classes) is an invention | ASSUMED (structural) | CONFIRMED (as an assumption; control = permuted/random maps) | Scrambled-encoder control mandatory |
| AE-2 | UCI drift corpus has class-correlated batch artifacts (Dennler 2022); UCI-only headlines are attackable | SOURCED | CONFIRMED (as literature fact) | Pair with Sci Data 2025 dataset |
| AE-3 | AL gain-control transfers to MOX drift robustness | INFERRED (established AL biology + untested bridge) | OPEN | This IS the experiment |

## Task 7 — MLPerf Tiny (AM-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AM-1 | v1.5 window lands ~H1 2027 (inferred from annual cadence; unannounced) | INFERRED | OPEN | USER joins working group early; watch group channels |
| AM-2 | The AD entry must run the actual circuit on-MCU; a distilled surrogate is a different project | first principle | CONFIRMED (rule) | If it cannot fit, record the limit and stop |

## Task 8 — Venues (AV-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AV-1 | IJCNN 2027 competition proposals due 2026-11-30; entering (not proposing) is our default posture | SOURCED + program decision | OPEN | USER may choose to propose; that is an organizing commitment |
| AV-2 | All 2027 window dates are projections from prior cycles until calls open | SOURCED/INFERRED | CONFIRMED (as projections) | Scheduled re-checks in the monitoring calendar |
