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

STATUS end of 2026-10-02 (all Step-0 questions now resolved; the
register rows carry the detail): AP-1 resolved (papers due 2026-11-08);
AP-2, AP-3 resolved (team must match the code-track team); AP-4
CONFIRMED — the CC0/MIT-0 open-sourcing clause is verbatim on
arcprize.org's 2026 overview (the earlier Rules-only INVALIDATED call
was itself reversed the same day; both reversals in the register), and
the MIT-0 relicense is already committed (Step 2 below, DONE);
AP-5 CONFIRMED in full from the Overview tab (writeup <= 1,500 words,
Media Gallery cover, public notebook via Project Links); AP-9 CONFIRMED
(no fourth submission needed; linkage mechanics known — kaggle_form.md
encodes them). From the rules: ONE writeup submission per team (AP-11);
public code sharing also posted on the competition forums (AP-12).

## Step 1 — join the Paper Track competition

From the megusalexandrus account: open the paper-track competition page,
click Join / accept rules. Do this well before 2026-10-26 (the entry
deadline on the code tracks; treat it as the safe bound for the paper track
too). You are already entered in arc-prize-2026-arc-agi-3.

## Step 2 — license: DONE 2026-10-02 (relicensed to MIT-0; kept as history)

The relicense landed on the user's "go MIT-0": LICENSE in the tree is
MIT No Attribution, with README and CITATION.cff updated (commit
be5912d; register AP-4). Nothing left to execute here. Original
reasoning preserved below.

The arcprize 2026 overview page (the user checked it; verbatim in
register AP-4) makes CC0/MIT-0 open-sourcing an ELIGIBILITY condition,
to be done before official evaluation. This coexists with the Kaggle
Rules' CC-BY 4.0 winner grant (that one binds only on winning). Plain
MIT has an attribution clause and is not a "public domain" license, so
the safe move is relicensing FlyGI-authored code to MIT-0 before the
repo goes public (~Nov 1). You are the copyright holder; a prepared
MIT-0 LICENSE commit (license text + README line; THIRD_PARTY_NOTICES
unchanged — third-party code keeps its own licenses, which clear
arcprize's Apache-2.0/GPLv3 floor) lands on your go.

## Step 3 — make the repo public

Only after docs/arenas/task1_arc_paper/public_release_checklist.md is fully
checked off (secrets audit, README, data-licensing note, branch merge).
GitHub: Settings -> General -> Danger zone -> Change visibility -> Public.

Then, same day (Rules §3.6.b, register AP-12): post the repo link in the
Paper Track competition's Discussion forum, and in the ARC-AGI-3
competition's forum (the shared code is that competition's code too). One
short post each, for example: 'FlyGI source is now public: <link> — the
connectome attribution audit behind submission 56683298.'

## Step 4 — public notebook

Upload docs/arenas/task1_arc_paper/public_notebook.ipynb to Kaggle as a NEW
public notebook (this is the demonstrative walkthrough, not the competition
submission notebook). Verify it renders top to bottom, set visibility
Public, copy its URL.

## Step 5 — create the Writeup

USE docs/arenas/task1_arc_paper/kaggle_form.md: it is the field-by-field
paste guide for the LIVE form (measured 2026-10-02: six required
checklist items, title <=80 chars, subtitle <=140, a 560x280 card image,
no code-submission selector, no notebook field — notebooks and the repo
go under Project Links). The bullets below are the original plan, kept
for history; where they differ, kaggle_form.md wins.

On the Paper Track competition page: create a Kaggle Writeup.
- Title + subtitle: first lines of docs/arenas/task1_arc_paper/writeup.md.
- Body: paste the body of writeup.md — everything after the `---`
  separator (1,448 words by whitespace count, 2026-10-02). If Kaggle's own
  counter reads above 1,500, stop and tell the session: trims go through
  the fact/tier gate, never ad hoc.
- Media Gallery: upload the images in docs/arenas/task1_arc_paper/media/
  (cover first).
- Attached public notebook: the Step-4 URL.
- Project Link: https://github.com/msafdari/FlyGI (public by then).
- Link the code submission: reference submission 56683298 (thirteen
  archetypes, scored 0.15) — the writeup documents all three scored
  submissions but 56683298 is the primary.

## Step 6 — SUBMIT, not draft — ONCE

Click Submit on the writeup before **2026-11-08 23:59 UTC** (verified on
arcprize.org; un-submitted drafts are not judged). The Rules allow ONE
submission per team (§2.2.a, register AP-11): submit only the final
version, and do not rely on editing it afterwards. Then tell this session the
confirmation state so WORKLOG records it.

## Step 7 — announce

After the repo is public and the writeup submitted: post the LinkedIn
article (linkedin_post.md) and the X post (x_post.md). Both end at the
GitHub repo.

## Dates

| 2026-10-26 | entry deadline — DONE (user joined the Paper Track 2026-10-02) |
| 2026-11-02 | code-submission deadline (only relevant if AP-9's linking check fails) |
| 2026-11-08 | papers due (verified, arcprize.org) |
| 2026-12-04 | results announced; if placed: respond within 1 week, prize docs within 2 weeks (AP-13) |
