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
| P-2 | Egress proxy blocks kaggle.com, arcprize.org, dsec.ifi.uzh.ch, download.ifi.uzh.ch, arxiv.org, mlcommons.org, brain-score.org, archive.ics.uci.edu, huggingface.co, neurobench.ai | MEASURED (agent fetch attempts, 2026-09-30; curl 2026-10-01: dsec, download.ifi, drive.google.com, neuprint.janelia.org all HTTP 000; raw.githubusercontent.com 200) | CONFIRMED | Re-test per task; user may extend allowlist (environment settings -> Network access) |
| P-3 | The user intends the FlyGI repo to become public (stated 2026-09-30: posts "lead to the FlyGI github repo where the findings and code is public") | user statement | CONFIRMED | The public-release step itself remains the user's action |

## Task 1 — ARC Paper Track (AP-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AP-1 | Paper deadline is 2026-11-09 23:59 UTC (Kaggle page); one extraction says arcprize.org shows 11-08. We plan to 2026-11-08 | MEASURED 2026-10-02 (user eyeball, arcprize.org/competitions/2026/paper pasted verbatim): "November 8, 2026 - Papers due"; also "November 2, 2026 - Submissions due", results 12-04 | CONFIRMED (plan-safe at 11-08; what Kaggle displays is now immaterial — the stricter date is verified) | Plan to 2026-11-08 |
| AP-2 | Low-score submissions are eligible ("code submission need not achieve a high score"); our 0.15 rows qualify | MEASURED 2026-10-02 (user eyeball, same page, verbatim): "The code submission need not achieve a high score for the corresponding paper to be eligible" | CONFIRMED | Also verified verbatim: rubric = six equal 0-5 categories; "The submission's score will be used in the rubric's accuracy category" (0.15 anchors Accuracy low — consistent with AP-7's compensate-elsewhere framing) |
| AP-3 | Writeup must be submitted from the same account/team as the code submission (megusalexandrus) | MEASURED 2026-10-02 (Kaggle Rules tab, pasted verbatim by the user): §2.1.b "Team must match the team making a submission to either ARC-AGI-2 or ARC-AGI-3"; §3.5.a one unique Kaggle account per person | CONFIRMED | megusalexandrus (solo team) clicks submit; do not form or merge a team |
| AP-4 | Submitter-authored code must be open-sourced under CC0 or MIT-0 (plain MIT NOT listed as sufficient) | MEASURED 2026-10-02, all three sources now pasted by the user, reconciled: (1) arcprize.org 2026 overview, verbatim: "In order for a submission to be eligible, all code and methods authored by the submitter must be made open source under a permissive public domain license (eg. CC0 or MIT-0)" and "Participants must open source their solutions before receiving official private evaluation scores"; (2) Kaggle Rules §1.6/§2.5: winner grants the SPONSOR CC-BY 4.0 on winning — a separate, coexisting obligation; (3) neither Kaggle tab carries the CC0/MIT-0 wording, which is why the Rules-only reading missed it | CONFIRMED — the original sourcing was right; the 2026-10-02 Rules-only invalidation is itself invalidated. Plain MIT carries an attribution clause and is not a "public domain" license; the safe reading is that it does NOT qualify | DECISION REOPENED, the user's as copyright holder: relicense FlyGI-authored code to MIT-0 (recommended: minimal diff from MIT, drops only the attribution requirement) or CC0, BEFORE the repo goes public (~Nov 1). A prepared MIT-0 LICENSE commit lands on the user's go |
| AP-5 | Writeup requires <=1,500 words + Media Gallery + attached public notebook; optional Project Link | MEASURED 2026-10-02, BOTH sources now pasted by the user. The live FORM enforces six checklist items (title <=80, subtitle <=140, 560x280 card, track, description, project links). The OVERVIEW tab adds the eligibility layer, verbatim: "Your Writeup should not exceed 1,500 words. Submissions over this limit may be subject to penalty"; "The below assets must be attached to the Writeup to be eligible" — Media Gallery ("A cover image is required to submit your Writeup") and Public Notebook ("submitted as a public notebook in the Project Links field", no login/paywall); Project Link optional (its stated use: a PDF of the paper) | CONFIRMED in full (the earlier form-only reading that the gallery/notebook are optional is corrected: form-enforced and eligibility-required differ; satisfy both) | We already satisfy everything: body 1,448 words, cover + 3 figures for the gallery, public walkthrough notebook planned, repo as extra link |
| AP-6 | MaleCNS-derived compiled arrays may be redistributed via the existing Kaggle dataset and a public repo (data license permits) | MEASURED 2026-10-01: README.md records MaleCNS v1.0 is CC BY 4.0, with the required citation (doi:10.1016/j.cell.2026.08.015) and the derivative/non-endorsement disclaimer already in place | CONFIRMED (attribution travels with any public dataset/asset) | Keep the citation + CC-BY notice on the Kaggle dataset description when it goes public |
| AP-7 | "Progress" rubric criterion will score low (~1-2/5) for a biological-substrate paper; compensate on the other five | INFERRED (rubric text + precedent) | OPEN | Affects framing only |
| AP-8 | No pure negative-results paper has placed in the money; nulls must be controls inside a novel-method narrative, not the headline | SOURCED (2024+2025 winner lists) | CONFIRMED (as historical fact) | Framing rule for the writeup |
| AP-9 | A fourth code submission before 2026-11-02 is NOT required; existing three suffice | MEASURED 2026-10-02: arcprize says papers 'must be linked to a Kaggle code submission' (not 'new'); the live form has NO code-submission selector, so linkage is by team identity (Rules §2.1.b), the submission IDs named in the body, and a project link to the submission notebook | CONFIRMED (no fourth submission needed; linkage mechanics are known) | Link megusalexandrus/flygi-arc-agi-3 under Project Links; making it public is recommended, not required | [2026-10-02 later, Overview verbatim: "you will be asked to provide your submission ID to match your notebook to your submission" — linkage fully resolved; have 56683298 ready when asked.]
| AP-10 | The writeup should follow arcprize's "What to Include" shape: Abstract / Intro / Prior work / Approach / Results / Conclusion; "Don't report train set performance"; "shorter and clearer is always better" | MEASURED 2026-10-02 (user eyeball, pasted verbatim) | CONFIRMED as guidance; GAP FOUND: writeup.md has NO prior-work section and names no prior approach (grepped: zero mentions of CompressARC / connectome demos / counter-evidence lines), while Novelty is scored "relative to existing public research" | Claude-side revision owed, through the fact/tier gate, within the 1,500-word budget; also re-check Result-1 wording against the "train set performance" caution (local-vs-hidden framing is the finding itself, keep it, but label the sets plainly) |
| AP-11 | The paper track allows ONE writeup submission per team | MEASURED 2026-10-02 (Kaggle Rules, verbatim): §2.2.a "For Hackathons, each Team may submit one (1) Submission only"; §1 intro designates rubric-judged competitions as Hackathons | CONFIRMED | Treat SUBMIT as one-shot: click it only on the final version. Whether Kaggle lets a submitted writeup be edited before the deadline is unverified — do not rely on it |
| AP-12 | Making the repo public during the competition period is allowed but carries a Kaggle-side sharing condition | MEASURED 2026-10-02 (Kaggle Rules §3.6.b, verbatim): public sharing is permitted, but "you are required to share it on Kaggle.com on the discussion forum or notebooks associated specifically with the Competition"; shared code is deemed OSI-licensed, commercial use permitted (MIT qualifies). §3.6.a forbids PRIVATE sharing outside the team | CONFIRMED (our reading of the clause) | When the repo goes public (~Nov 1, inside both the ARC-AGI-3 period ending Nov 2 and the paper period ending Nov 8), post the repo link in the Paper Track discussion forum and the ARC-AGI-3 forum; the attached public notebook is the second Kaggle-side copy |
| AP-13 | Winner obligations, if we place, have short clocks | MEASURED 2026-10-02 (Kaggle Rules, verbatim): respond to the winner notification within 1 week (§3.8.b); return prize documents incl. W-9/W-8BEN within 2 weeks (§3.9.d, §2.8); deliver the code + documentation with reproduction instructions and a repository link (§2.5.b, §2.8.a); possible recorded call with the sponsor | CONFIRMED (dormant until 2026-12-04) | Repo reproduction instructions should be in good shape before Dec 4; watch the Kaggle account email after results |
| AP-14 | Every third-party open-source component used to generate the submission carries an OSI-approved, commercial-use-permitting license (Rules §3.6.c) | MEASURED 2026-10-02 (THIRD_PARTY_NOTICES.md read): ARC-AGI-3-Agents MIT, ARCEngine MIT, FrugalExplorer MIT-0 and Blind Squirrel MIT (ideas reimplemented, not vendored). One gap: the ARC-AGI-3 Kaggle Starter's pinned commit has no LICENSE file; FlyGI follows its workflow patterns and records the reference without asserting a license. It is the SPONSOR's own starter, so risk is low | OPEN (low risk) | If the sponsor ever asks, cite it as the sponsor-provided starter; Rules §2.5.a(2)-(3) exempt software we do not own | [2026-10-02 later, arcprize overview verbatim: third-party code must be "available under, at least, an open source license which allows public sharing (eg. Apache-2.0, GPLv3)" — every notice-listed component (MIT/MIT-0) clears that bar easily; the sponsor's own unlicensed starter remains the only residual and is the sponsor's.]
| AP-15 | The deadline is Nov 8 (arcprize.org) | MEASURED 2026-10-02: Kaggle is internally consistent at 2026-11-09 23:59 UTC (form: Nov 9 3:59 PM PST; Overview: "November 9, 2026 - Final Submission Deadline ... 11:59 PM UTC"); arcprize.org says Nov 8 | CONFIRMED two-source discrepancy, Kaggle self-consistent; the plan stays Nov 8 (safe under both) | No action; do not plan to Nov 9 |
| AP-16 | Attaching a private Kaggle resource to the writeup is consent to its publication | MEASURED 2026-10-02 (Overview, verbatim): "If you attach a private Kaggle Resource to your public Kaggle Writeup, your private Resource will automatically be made public after the deadline"; same for a private notebook in Project Links | CONFIRMED | If the private submission notebook megusalexandrus/flygi-arc-agi-3 is linked, it WILL go public after the deadline — so put the MaleCNS CC BY 4.0 citation on the private dataset's description BEFORE submitting (AP-6), in case the auto-publication cascades to attached resources |

## Task 2 — DSEC-Flow (AD-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AD-1 | Benchmark account requires an institutional email; gmail risky | SOURCED (sibling disparity page verbatim) | OPEN | User may need an academic address or organizer contact |
| AD-2 | Entries without an eventual report/paper are deleted after ~6 months | SOURCED | OPEN | Entry and report ship together |
| AD-3 | T4/T5 at class 2.5 (trained flyvis physiology) can produce direction estimates from event streams; frozen counts (DSI 0.042) cannot | MEASURED (repo, ARC context) + INFERRED (transfer to DSEC input) | OPEN (registered 2026-10-01 as H-T4T5-DSEC-DIRECTION; frozen design in task2_dsec_flow/killtest_design.md) | The kill test measures exactly this |
| AD-4 | Dense-flow decoding (sparse lattice -> 640x480 metric flow) can stay trivial plumbing (fixed linear readout + interpolation) without doing the intelligence | ASSUMED | OPEN (deferred: the kill test evaluates at column resolution; dense decoding is reached only on a pass) | Ablate decoder on null wiring; if decoder carries the result, record and stop |
| AD-5 | Driving-scene flow magnitudes exceed a single EMD's temporal band; multi-timescale sampling of the same circuit is required | INFERRED (literature) | OPEN (weakened 2026-10-01 by unit analysis: at the declared central-crop binning, ~10 px / 100 ms maps to ~3-15 col/s, bracketing the fc25 passing band 2.5-10 col/s; inference recorded in killtest_design.md, not relied on) | Label at the code site if built |
| AD-6 | Per-pixel running sum of signed event polarities within a flow window approximates log-luminance change and can serve as the L1/L2/L3 drive (no contrast-threshold constant) | ESTABLISHED (event generative relation, qualitative) + ASSUMED (raw sum as drive) | OPEN | Declared at the code site; if the circuit needs true luminance, this bridge is where the kill test dies for a non-fly reason — the twin/null arms share it, so attribution survives |
| AD-7 | Central 480x480 crop mapped isotropically onto the 13x13 input lattice preserves direction and is a fair eye-map-style downsampling | ASSUMED | OPEN | Identical for all arms; isotropy argued in killtest_design.md; evaluation restricted to the crop |
| AD-8 | fc25's measured per-subtype preferred directions on this patch are a valid fixed vote basis for a population-vector direction readout (no fitted parameters) | MEASURED (tiling, fc25 result) + ASSUMED (vote construction) | OPEN | DC cancellation argument recorded; per-column subtype coverage reported by the harness |

## Task 3 — FlyBench (AF-*)

| ID | Statement | Tier | Status | Check / consequence |
| --- | --- | --- | --- | --- |
| AF-1 | flybench MaleCNS (neuprint, >=5-syn, 176,422 neurons / 6.29M edges) and our compile (166,700 / 24.99M) are different compilations of the same source; results are not directly comparable across them | MEASURED (both repos read) | CONFIRMED | Any cross-claim states the substrate; consider running our params through THEIR build |
| AF-2 | neuprint.janelia.org is reachable from this container for the anonymous fetch | MEASURED 2026-10-01: HTTP 000 from the cloud container (re-confirmed at Task 3 open) | INVALIDATED (in-cloud) | FlyBench MaleCNS fetch must run locally or after an allowlist change; the toy suite needs no fetch |
| AF-3 | Our simulator stack can implement their Simulator/run->SimResult interface without violating their no-fitting-on-tasks rule (our calibrations were done on OUR protocols, not their tasks) | INFERRED + MEASURED (interface read at commit 3052ce5: open division requires n_free_parameters + fit_data <=300 chars, benchmark-fitted params ineligible) | OPEN | Declare n_free_parameters + fit_data explicitly; ask maintainer if ambiguous |
| AF-4 | Our graded-unit operating points (MB pass uses graded APL + threshold-calibrated KCs) can be expressed in their SPIKE-only SimResult (spike times + indices) via a declared conversion without the conversion doing the work | ASSUMED (from interface read, 2026-10-01) | OPEN | Label at the adapter code site; their shuffled-wiring controls run through the same conversion |
| AF-5 | flybench installs from PyPI | MEASURED 2026-10-01: NOT on PyPI (404); install is `pip install -e .` from the GitHub clone (v0.2.1, commit 3052ce5) | INVALIDATED (survey correction) | Runbooks say clone + editable install |
| AF-6 | The cloud container can run the flybench toy suite (needs no data fetch) | MEASURED 2026-10-01: first denied by the execution policy; the USER then explicitly authorized third-party execution, and the toy suite RUNS in-container (reference simulator: score 0.93, graded 0.94, 24/30 tasks, ~2 min) | CONFIRMED (under explicit user authorization, recorded in WORKLOG) | In-cloud Task 3 work may execute flybench; the neuprint fetch stays blocked (AF-2) |

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
