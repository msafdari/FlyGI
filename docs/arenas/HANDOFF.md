# Arena program — living handoff and status

Opened as the handoff when the user paused the original arena session
(2026-10-01); maintained since as the program's living status file.
This file is the resume point. Read in
this order: WORKLOG.md (top entries) -> this file -> PLAN.md ->
ASSUMPTIONS.md. Branch: `claude/admiring-goldberg-wtqkbg` (all work
pushed; nothing lives only in the old session).

## The user's standing directive (2026-09-30)

Execute all eight ranked arenas in docs/next_arenas_survey_20260930.md,
top rank first; finish one task completely before the next; do a quick
due-diligence check before starting each task; document as you go
(WORKLOG, periodic commits and pushes); track assumptions and hypotheses
up front in docs/arenas/ASSUMPTIONS.md and update them (confirm,
invalidate, add) as work proceeds. Task 1 must also produce a LinkedIn
post and an X post that lead to the public FlyGI GitHub repo.

## Where each task stands

| # | Task | Status |
| --- | --- | --- |
| 1 | ARC Prize 2026 Paper Track | **Claude-side COMPLETE.** All artifacts in docs/arenas/task1_arc_paper/. Remaining steps are the user's (runbook steps 0-7). |
| 2 | DSEC-Flow | **COMPLETE WITH VERDICT (2026-10-02): kill test KILLED.** H-T4T5-DSEC-DIRECTION refuted on thun_00_a -- both frozen bars failed, the rewire beat the real wiring a third time, all arms near chance at the declared binning. No dense pipeline, no benchmark entry (per the frozen rule). Full record in EXPERIMENTS.yaml. |
| 3 | FlyBench | **COMPLETE WITH VERDICT (2026-10-03).** Adapter kill test PASSED (contract-level); first MaleCNS rows measured (unpinned, AF-7); calibrated arm KILLED — H-FLYGI-FLYBENCH-CALIBRATED refuted (activation subset moved +0.0002 vs the +0.02 bar; the gain landed in suppression, led by the one task the LK calibration directly targets). The UNIFORM row stands as the measured contribution: core 1.000 / hard 0.6044 / graded 0.711 / specificity +0.282 vs reference 0.5667 / 0.5366 / 0.639 / +0.184. Any flybench PR / verified-badge step is the USER's decision from that row. |
| 4 | NeuroBench | **T4/T5 LIMB COMPLETE WITH VERDICT (2026-10-03): kill test KILLED.** H-T4T5-DVS-GESTURE refuted on held-out subjects -- real T4/T5 far above chance but beaten by its own degree-preserving rewire in all 3 seeds AND by circuit-free event-count features (fourth consecutive rewire-over-real on this circuit). No NeuroBench integration built, per the frozen rule. **Keyword-FSCIL/MB limb CLOSED AS NOT PURSUED (2026-10-07)** via the dual close pre-stated in H-ALMB-GASDRIFT's registration: the MB lost its native-modality last stand (Task 6 KILL), so the audio limb — same machinery behind a larger encoder invention — has no remaining support; its hypothesis stays unmeasured. Task 4 is now fully closed. Full record in EXPERIMENTS.yaml + WORKLOG. |
| 5 | Brain-Score | **COMPLETE WITH VERDICT (2026-10-04): kill test KILLED.** H-EARLYFILTER-BRAINSCORE-V1 refuted — real 0.0690 cleared the floor AND doubled its own input passthrough (0.0330, the program's first dynamics arm to add anything over its encoder), but all three degree-preserving rewires scored at or above it (0.0735–0.0828). Fifth consecutive rewire-over-real on fc25-class circuits. No BrainModel submission, no account, per the frozen rule. Full record in EXPERIMENTS.yaml + WORKLOG. |
| 6 | e-nose / gas drift | **COMPLETE WITH VERDICT (2026-10-06): kill test KILLED.** H-ALMB-GASDRIFT refuted — real 0.4257 decisively above chance (p 5.2e-26) but below every degree-preserving rewire (0.4338–0.4854) and below the raw 16-sensor features (0.5022). Sixth consecutive rewire-over-real, first olfactory, exactly as the registration's stated literature prior predicted for the rewire bar. Scope correction recorded at close: the real-vs-scram gap (+4.4 pts) is encoder-invention variance (both maps are seeded inventions), not a wiring win. No benchmark entry; the dual close executed (see Task 4 row). Full record in EXPERIMENTS.yaml + WORKLOG. |
| 7 | MLPerf Tiny | **CALENDAR-GATED to 2027.** Next round ~early 2027 (inferred from cadence, unannounced); USER joins the working group >= 8 weeks before any deadline. |
| 8 | Community venues | **IJCNN 2027 competition proposal analyzed (2026-10-07): recommendation NO-GO** this cycle (task8_venues/ijcnn2027_go_no_go.md — solo operating commitment + calendar collision + participation risk; the public release + a paper buys most of the value). Better IJCNN vehicle: the regular paper, due 2027-01-31, decidable after the Dec 4 ARC results. Later windows stay live: Telluride 2027 (~Feb), CVPR 2027 event-vision / VAND 5.0 (Dec-Feb announcements), IJCNN 2028 competition if co-organizers appear. User has not yet decided. |
| 9 | CX latent state (off-survey, user go 2026-10-10) | **CLOSED (2026-10-11): structure yes, computation untestable at classes 1–2.** Stage A PASSED — the arena series' FIRST PASS: H-CX-RING-TOPOLOGY supported at the p-floor on both bars (bandedness 0.588 vs null max 0.338; PEN_a mirror-peak 0.0145 vs 0.0079; 200 rewires) — the first measured property of the real wiring its null cannot reproduce. Stage B BLOCKED at the AC-2 precheck and H-CX-HEADING-LATENT closed "null": the premise's two required properties were only ever measured in disjoint regime×protocol combinations (persistence at 2.0 wedge-write = fixed-point; steering at 1.5 visual-arc; no persistence at 1.5 wedge-write, two runs concurring). Reopening paths (explicit go + own registration each): class-3 CX, or a registered visual-arc reconciliation at 1.5. Records: EXPERIMENTS.yaml, task9_cx_latent/, SYNTHESIS addendum. **REOPENED and RE-CLOSED (2026-10-11, user go "do them both"): both paths registered jointly, built, run locally, both KILL — H-CX-SEEDING-PROTOCOL refuted (all 8 cells fail; 4 protocols land identically at gain 1.5, fixed-point mode at 2.0 — regime-bound, no class-1 re-registration licensed) and H-CX-CLASS3-COMPASS refuted with the validation gate passing on the verdict machine (published Pisokas fly bump reproduces, mean width 99.0 vs their 88.3; the standalone CX under the AC-6 mapping fails all 6 declared grid points — G1 best 2/8, steering never opposite-signed; in-situ class-3 behavior untested). NEW measured fact: at spiking fidelity the bump SURVIVES darkness (retention 0.94–0.997) but slides to a common region (~177–221°; errors 155–177°) — activity persistence without a position continuum (point-attractor reading INFERRED). The structure/function split is now measured at two fidelity classes. Rewires never ran in either (real failed first) — the null-bar record does not gain instances. Task 9 is CLOSED at every registered level; records: EXPERIMENTS.yaml, task9_cx_latent/, SYNTHESIS second addendum, WORKLOG eeb75b5 + close entry.** |
| 10 | Science menu (exhaustion audit, user go 2026-10-23) | **OPEN — registration stage.** 9-agent audit (2026-10-15) answered "have we used everything from the fly?": the tested record is deep but the exhausted object is one male's counts+signs, not the fly; full tiered record in task10_menu/exhaustion_audit.md. User go on ALL 7 items: reservoir positive control on ARC (instrument validity — protects the published nulls), class-3 T4/T5 (§7 item 1, reversal candidate), fitted per-type CX (Biswas/Duan-Fiete rung, declined before, strongest reversal candidate), FB structural probe (PFN/hDelta never touched), naturalistic-statistics task (explanation 3, zero tests), FlyBench mechanisms (terminal-aware placement + SFA), second null family (weight/sign shuffles). Due diligence running; registrations freeze before any instrument code; none score-adjacent (base rate 0 for 16 unchanged). |

### Task 1 — what exists, what the user still does

docs/arenas/task1_arc_paper/:
- `writeup.md` — the judged Kaggle Writeup: title, subtitle, 1,448-word
  body. Built by a draft/judge/synthesize/check workflow, then passed a
  fact gate, a tier gate, and an outward-artifact compliance gate, with
  every finding applied.
- `factsheet.md` — the VERIFIED fact base. Every number in every
  outward artifact must trace to it. It was checked against the durable
  record by a four-agent adversarial pass.
- `media/` — cover plus three figures (PNG at 2x, with HTML sources).
  Rendered with the headless Chromium at
  /opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
  (`--screenshot --force-device-scale-factor=2`).
- `public_notebook.ipynb`, `linkedin_post.md`, `x_post.md` — all three
  are compliance-gated. Posting waits until the repo is public.
- `submission_runbook.md` — the user's steps 0-7. Step 0 resolves the
  OPEN register rows AP-1..AP-5 and AP-9. Deadline: plan to 2026-11-08.
- `public_release_checklist.md` — the secrets/PII audit (clean), the
  license (relicensed to MIT-0 2026-10-02 per AP-4: arcprize requires CC0/MIT-0; the Kaggle winner CC-BY 4.0 grant is a separate, on-winning obligation), the LEAGUE.md
  regeneration (local), the merge to main, and the order of operations.

### Task 2 — DSEC-Flow: RESOLVED 2026-10-01 (section kept as history)

The next steps and the "reconcile first" item below were all executed on
2026-10-01 (WORKLOG entry of that date): the truncated draft became the
frozen registration docs/arenas/task2_dsec_flow/killtest_design.md
(directory settled, old task2_dsec/ removed), the metrics module and the
data-gated harness are built and tested, the runbook is written, and
H-T4T5-DSEC-DIRECTION is registered. What remains is the USER's local
kill-test run per runbook.md; the hypothesis closes from its JSON.

### Task 2 — DSEC-Flow: exact pause point (historical)

DONE:
- Due diligence (full detail in due_diligence_20260930.md, `dsec-flow`).
  The benchmark is open and rolling, with automatic evaluation. The
  floor on the board is MultiCM EPE 3.472 (model-free); state of the
  art is about 0.66; E-RAFT scores 0.788. Requirements: a report within
  about 6 months or the entry is deleted, and an institutional-email
  account. Submission is a 16-bit 3-channel 480x640 PNG per timestamp,
  KITTI encoding (flow*128 + 2^15), in the rectified left event-camera
  view, evaluated in alphabetical filename order.
- Measured egress from the cloud container (2026-10-01):
  dsec.ifi.uzh.ch, download.ifi.uzh.ch, drive.google.com (where the
  MVSEC data is hosted) and neuprint.janelia.org all failed (HTTP 000).
  raw.githubusercontent.com returned 200. The container also has no
  compiled MaleCNS runtime and no flyvis checkpoints. **So the kill
  test cannot run in the cloud container as configured.** The remedy is
  either to add those hosts to the environment's network allowlist
  (environment settings -> Network access) or to run the test on the
  user's local machine, where the runtime lives.
- Engine interface read, to ground the harness:
  `scripts/benchmarks/fc2_visual_ds.py` — `build_patch()` returns a
  dict with `matrix` (signed alpha-weighted CSR), `types`, `x`/`y`
  (hex-axial columns embedded in the plane, unit column spacing),
  `driven_mask` and the score indices. `GradedFlyvisNetwork` exposes
  `step(drive)`, `output()`, `set_state()` and `reset()`.
  `run_sweep(net, patch, polarity, direction_vec, speed, settled_state,
  score_idx)` shows the crossing-window readout pattern. `settle()`
  gives the baseline. Class-2.5 parameters come from
  `scripts/benchmarks/fc25_visual_ds.py` — `trained_table(fc2, params,
  which, uniform_tau)` and `trained_weight_matrix(...)`, reading
  docs/fidelity2/flyvis_trained_params.json. The passing configuration
  is in results/benchmarks/fc25_visual_ds.json, which exists on the
  local machine only.

NEXT (the plan at the moment of pause):
1. Write the connectome-independent half first and verify it in the
   cloud container with synthetic flow, since it needs no data. That
   half is `scripts/arenas/dsec_metrics.py`: EPE, angular error, the
   1/2/3PE outlier rates, the KITTI PNG encode/decode round trip, and
   the trivial baselines (zero flow, global translation from GT median,
   event-count argmax direction). Add tests.
2. Write `docs/arenas/task2_dsec_flow/killtest_design.md`. It covers
   the event -> retinotopic drive mapping (ASSUMPTION: event polarity
   maps to ON/OFF input types; time bins map to drive steps), the T4/T5
   crossing-window readout -> per-column direction, a deliberately
   trivial dense decoder (nearest-column, labelled ASSUMPTION AD-4), and
   the arms: real class-2.5 patch, degree-preserving rewired patch,
   uniform-tau twin, the trivial baselines, and an optional MultiCM
   reference. Freeze the pass/kill rule before any data is seen. The
   rule: the fly arm must beat event-count argmax AND the rewired patch
   on angular error, on one DSEC train sequence (or MVSEC
   indoor_flying1). Otherwise, record the limit and stop; no dense
   pipeline gets built.
3. Write the harness `scripts/arenas/dsec_killtest.py` against the real
   interfaces above (data-gated), plus a user runbook
   `docs/arenas/task2_dsec_flow/runbook.md`.
4. Register Task 2's hypothesis in EXPERIMENTS.yaml before any
   outcome, update ASSUMPTIONS.md (AD-1..AD-5), then make a WORKLOG
   entry and a commit.
Task 2 counts as "complete" once the harness, design, runbook and
registration are committed and the blocker is surfaced. Its
measurement runs wherever the data and runtime are reachable.

**Reconcile first:** `docs/arenas/task2_dsec/KILL_TEST.md` is a
TRUNCATED, UNREVIEWED draft of the kill-test registration. It ends
mid-sentence in the Arms list. It most likely came from an interrupted
turn whose file write finished anyway, and it was swept into the pause
commit. Its premise, data choice, pipeline and arms match next-step 2
above. The new session should review it, finish it (complete the arms
list and the frozen pass/kill rule), and settle on ONE Task-2 directory
(`task2_dsec/` or `task2_dsec_flow/`) before writing anything else.

### Tasks 3-8 — what due diligence already established

See PLAN.md (per-task premise, kill test, deliverables) and
due_diligence_20260930.md (full sourced detail). Each task still gets
its own quick due-diligence delta when it starts.

## Durable conventions established in this program

- The program-level synthesis of the completed sweep (Tasks 1-6, the
  seven rewire-over-real instances with their decompositions, the
  surviving positives, open explanations, and the record map) lives
  in docs/arenas/SYNTHESIS.md (2026-10-07). Read it before citing the
  program's arc anywhere.
- Every outward number must trace to a verified factsheet. Run an
  adversarial fact/tier gate before anything ships.
- The base rate for expected-tier score claims is **0 for 16** (as of
  2026-10-06; the 16th is H-ALMB-GASDRIFT, exactly as its own
  registration pre-stated). Any stale "0 for 15" or earlier is a bug.
- Required scope words: model (class-N) vs fly; connectome vs brain.
  Never "the fly" when the record is scoped to a circuit, task and
  fidelity class.
- Charts follow the dataviz skill: validate the palette with its
  script, render 2x through the headless Chromium above, then look at
  the PNG before shipping.
- Commits: small, pushed to `claude/admiring-goldberg-wtqkbg`, with
  the session attribution trailer the harness specifies.

## Not carried over (session-local, intentionally dropped)

Workflow run IDs (wf_77415764-bf9, wf_7e405dd9-8a8, wf_6cc4b6d7-f47)
resume only within the old session. Their substantive outputs are
already in the repo: the due-diligence record (this directory), the
verified factsheet, and the final writeup with all gate fixes applied.
The scratchpad held only drafts that were superseded by committed files.
