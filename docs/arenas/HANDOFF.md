# Arena program — session handoff (paused 2026-10-01)

The user paused the session that ran the arena program and asked for a
clean resume in a new session. This file is the resume point. Read in
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
| 2 | DSEC-Flow | **Claude-side COMPLETE (2026-10-01).** Kill test registered (H-T4T5-DSEC-DIRECTION, frozen), metrics + data-gated harness built and tested, runbook written. The measurement is the user's local run: docs/arenas/task2_dsec_flow/runbook.md. |
| 3 | FlyBench | **IN PROGRESS (2026-10-01).** Adapter kill test PASSED in-cloud (H-FLYGI-FLYBENCH-ADAPTER supported; user authorized third-party execution). MaleCNS rows are the user's local run: docs/arenas/task3_flybench/runbook.md. The calibrated-parameters design (AF-4) is registered next, before any build. |
| 4 | NeuroBench | pending |
| 5 | Brain-Score | pending |
| 6 | e-nose / gas drift | pending |
| 7 | MLPerf Tiny | pending |
| 8 | Community venues | pending (hard date: IJCNN 2027 competition proposals due 2026-11-30) |

### Task 1 — what exists, what the user still does

docs/arenas/task1_arc_paper/:
- `writeup.md` — the judged Kaggle Writeup: title, subtitle, 1,433-word
  body. Built by a draft/judge/synthesize/check workflow, then passed a
  fact gate, a tier gate, and a 23-finding outward-artifact compliance
  gate, with every finding applied.
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
  license (MIT stays: Kaggle winner license is CC-BY 4.0, granted only on winning — AP-4), the LEAGUE.md
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

- Every outward number must trace to a verified factsheet. Run an
  adversarial fact/tier gate before anything ships.
- The base rate for expected-tier score claims is **0 for 12** (as of
  2026-09-26; verified). Any stale "0 for 11" is a bug.
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
