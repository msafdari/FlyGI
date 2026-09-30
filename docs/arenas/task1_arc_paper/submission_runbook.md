# ARC Prize 2026 Paper Track — submission runbook (user-executed)

Prepared 2026-09-30. This container has no Kaggle credentials and the
relevant pages are egress-blocked from it, so every step below is yours to
click; everything clickable has a prepared artifact in this directory.
Steps 0-2 resolve the register's OPEN assumptions (docs/arenas/
ASSUMPTIONS.md, AP-1..AP-9) — please report what you see so the register
gets updated.

## Step 0 — verify the rules once (10 minutes, do first)

Open both, from a normal browser:
- https://www.kaggle.com/competitions/arc-prize-2026-paper-track (Overview
  AND Rules tabs)
- https://arcprize.org/competitions/2026/paper

Confirm or correct, against the register:
1. AP-1: final writeup deadline — Kaggle reportedly says Nov 9, 2026
   23:59 UTC; one source says arcprize.org shows Nov 8. We plan to Nov 8.
2. AP-2: low-score code submissions are eligible ("need not achieve a high
   score").
3. AP-3: the writeup must come from the same account/team as the code
   submission (megusalexandrus).
4. AP-5: writeup requirements — <=1,500 words, Media Gallery, attached
   PUBLIC notebook, optional Project Link.
5. AP-4: open-source licensing wording — CC0 / MIT-0 for submitter-authored
   code (and by when: at submission vs before prize payment).
6. AP-9: whether the paper may document the EXISTING Sept submissions or
   a fresh linked submission is needed before Nov 2.

## Step 1 — join the Paper Track competition

From the megusalexandrus account: open the paper-track competition page,
click Join / accept rules. Do this well before 2026-10-26 (the entry
deadline on the code tracks; treat it as the safe bound for the paper track
too). You are already entered in arc-prize-2026-arc-agi-3.

## Step 2 — license decision (your call as copyright holder)

Prize eligibility reportedly requires CC0 or MIT-0 for submitter-authored
code; the repo is currently MIT. If you choose to relicense: say so and a
prepared LICENSE change + README note will be committed. If you prefer to
keep MIT: the writeup can still be submitted; prize eligibility is what is
at risk (per AP-4 — confirm exact wording in Step 0).

## Step 3 — make the repo public

Only after docs/arenas/task1_arc_paper/public_release_checklist.md is fully
checked off (secrets audit, README, data-licensing note, branch merge).
GitHub: Settings -> General -> Danger zone -> Change visibility -> Public.

## Step 4 — public notebook

Upload docs/arenas/task1_arc_paper/public_notebook.ipynb to Kaggle as a NEW
public notebook (this is the demonstrative walkthrough, not the competition
submission notebook). Verify it renders top to bottom, set visibility
Public, copy its URL.

## Step 5 — create the Writeup

On the Paper Track competition page: create a Kaggle Writeup.
- Title + subtitle: first lines of docs/arenas/task1_arc_paper/writeup.md.
- Body: paste the body of writeup.md (it is kept <=1,450 words so Kaggle's
  own counter has margin; if Kaggle's counter reads higher, trim the
  section marked OPTIONAL first).
- Media Gallery: upload the images in docs/arenas/task1_arc_paper/media/
  (cover first).
- Attached public notebook: the Step-4 URL.
- Project Link: https://github.com/msafdari/FlyGI (public by then).
- Link the code submission: reference submission 56683298 (thirteen
  archetypes, scored 0.15) — the writeup documents all three scored
  submissions but 56683298 is the primary.

## Step 6 — SUBMIT, not draft

Click Submit on the writeup before **2026-11-08 23:59 UTC** (conservative;
un-submitted drafts are not judged). Then tell this session the
confirmation state so WORKLOG records it.

## Step 7 — announce

After the repo is public and the writeup submitted: post the LinkedIn
article (linkedin_post.md) and the X post (x_post.md). Both end at the
GitHub repo.

## Dates

| 2026-10-26 | entry deadline (join everything before this) |
| 2026-11-02 | code-submission deadline (only relevant if Step 0 finds AP-9 wrong) |
| 2026-11-08 | our writeup deadline (conservative) |
| 2026-12-04 | winners announced |
