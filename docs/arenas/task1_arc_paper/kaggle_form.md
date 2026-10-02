# Kaggle Writeup form — field-by-field paste guide

Mirrors the live form the user pasted on 2026-10-02 (Paper Track ->
Writeups -> New). Kaggle's submission checklist has six items: Title,
Subtitle, Card and Thumbnail Image, Submission Track, Project
Description, Project Links. All six must be complete before Submit
unlocks. The Media gallery, Files and DOI are optional.

**Deadline shown on the form:** Nov 9 2026, 3:59 PM PST, which is
2026-11-09 23:59 UTC (PST is UTC-8 after US DST ends on Nov 1).
arcprize.org says papers are due Nov 8. **Plan to Nov 8**, which is safe
under both. **Submit exactly once** (Rules §2.2.a, register AP-11).

---

## Basic details

**Title** (78 / 80 chars):

    The Grammar Scaffold Transferred Zero. The Fly's Eye Map Survived Its Control.

**Writeup URL** — click Edit, set the slug to:

    flygi-connectome-attribution-audit

**Subtitle** (139 / 140 chars):

    Auditing the 166,700-neuron MaleCNS fly connectome on ARC-AGI-3: both circuits tested in full scored below their degree-preserving rewires.

**Card and Thumbnail Image** (2:1): upload `media/card.png` (1120x560, a
sharp 2x render). If the uploader insists on exactly 560x280, use
`media/card_560x280.png` instead. The source is `media/card.html`.

**Submission Track:** Main Track (auto-selected; nothing to do).

## Media gallery (optional; not on the checklist; recommended)

Images, in this order:

1. `media/cover.png`
2. `media/fig1_ladder_vs_hidden.png`
3. `media/fig2_verdict_matrix.png`
4. `media/fig3_controls_both_ways.png`

Videos must be YouTube-hosted. There are none.

## Project Description

Paste everything in `writeup.md` **after** the `---` separator, i.e. the
body. It starts at "**One measured pair carries the paper.**" and ends
with "neuronal_dynamics_active=false." The body is markdown (## headers,
bold, numbered lists).

Expected count: 1,448 words by whitespace count. If Kaggle's counter
shows more than 1,500, stop and tell the Claude session; trims go
through the fact/tier gate, never ad hoc.

## Attachments -> Project links

The form has **no field for picking a code submission**. The paper is
linked to the code submission in three ways: (1) the Rules require the
same team for both (§2.1.b; you are the solo team megusalexandrus);
(2) the body names submissions 56620463, 56650224 and 56683298 in its
first paragraph; (3) the notebook that produced 56683298 is linked here.

Add these links (title -> URL):

1. **Source code (GitHub)** -> https://github.com/msafdari/FlyGI
   The repo must be public before you submit (release step, ~Nov 1).
2. **Public walkthrough notebook** -> the URL of the new public notebook
   you upload from `public_notebook.ipynb` (runbook Step 4).
3. **Submission notebook (produced 56683298)** ->
   https://www.kaggle.com/code/megusalexandrus/flygi-arc-agi-3
   It is currently PRIVATE. Making it public on release day is
   recommended, not required: it is the literal code behind the scored
   entry, and a public Kaggle notebook also meets Rules §3.6.b's
   Kaggle-side sharing condition. If you do, keep the MaleCNS CC BY 4.0
   citation in its description (AP-6). If you'd rather keep it private,
   leave this link out; the team rule + submission IDs still carry the
   linkage.

## Files (optional)

Nothing to upload: the code lives in the linked repo. (The limit is
100 MB; the compiled connectome arrays belong in a Kaggle Dataset
anyway, per AGENTS.md.)

## DOI Citation (optional; recommended)

**Opt in.** It's free, the DOI is minted after the competition ends,
and it gives the writeup a citable identifier alongside the repo's
CITATION.cff.

## Before clicking Submit

- [ ] Checklist reads 6 of 6.
- [ ] The repo link opens logged out (repo is public).
- [ ] The walkthrough notebook opens logged out.
- [ ] Preview renders the body's headers and lists correctly.
- [ ] Click **Submit**, not save-as-draft. One submission only.
- [ ] Tell the Claude session the confirmation state.
