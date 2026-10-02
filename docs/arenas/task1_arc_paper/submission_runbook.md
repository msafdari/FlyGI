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

STATUS 2026-10-02: the user pasted arcprize.org's paper page and the full
Kaggle Rules tab. Resolved: AP-1 (papers due 2026-11-08), AP-2, AP-3 (team
must match the code-track team), AP-4 (INVALIDATED: the Kaggle winner
license is CC-BY 4.0, granted only on winning — no relicense needed to
submit). Still open, all on the Kaggle Overview tab / writeup form: AP-5
mechanics, AP-9 linking mechanics, and the AP-4 residual (any CC0/MIT-0
wording outside the Rules tab). New from the rules: ONE writeup submission
per team (AP-11), and public code sharing must also be posted on the
competition's Kaggle forum/notebooks (AP-12).
6. AP-9: whether the paper may document the EXISTING Sept submissions or
   a fresh linked submission is needed before Nov 2.

## Step 1 — join the Paper Track competition

From the megusalexandrus account: open the paper-track competition page,
click Join / accept rules. Do this well before 2026-10-26 (the entry
deadline on the code tracks; treat it as the safe bound for the paper track
too). You are already entered in arc-prize-2026-arc-agi-3.

## Step 2 — license (now OPTIONAL; no action required)

The Kaggle Rules (§1.6, §2.5, §2.8) set the winner license to CC-BY 4.0,
granted to the sponsor only if you win, as a condition of the prize. Our
reading (not legal advice): the repo can stay MIT — as sole copyright
holder you grant CC-BY 4.0 on the winning submission at that time — and
MIT already satisfies §3.6.b for publicly shared code. Relicensing is now
a preference, not a requirement. Only if the Overview tab or arcprize's
2026 overview page turns out to name CC0/MIT-0 does this become a decision
again.

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
