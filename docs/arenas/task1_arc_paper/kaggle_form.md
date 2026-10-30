# Kaggle Writeup form — field-by-field paste guide

Mirrors the live form AND the Overview tab, both pasted by the user on
2026-10-02. Two layers of "required": the form's checklist enforces six
items before Submit unlocks (Title, Subtitle, Card and Thumbnail Image,
Submission Track, Project Description, Project Links); the Overview tab
makes two more things ELIGIBILITY requirements even though the checklist
does not enforce them — a Media Gallery with a cover image, and your
code as a public notebook in Project Links. Satisfy all of it. The word
limit is verbatim: "Your Writeup should not exceed 1,500 words.
Submissions over this limit may be subject to penalty." (Body: 1,485.)

**Deadline:** Kaggle is internally consistent at 2026-11-09 23:59 UTC
(form and Overview agree); arcprize.org says Nov 8. **Plan to Nov 8**,
safe under both. **Submit exactly once** (Rules §2.2.a, register AP-11).

**Auto-publication warning (Overview, verbatim):** "If you attach a
private Kaggle Resource to your public Kaggle Writeup, your private
Resource will automatically be made public after the deadline." Linking
the private submission notebook is therefore consent to it going public
— see Project links below.

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

## Media gallery (REQUIRED for eligibility — Overview: "A cover image
is required to submit your Writeup"; the form checklist just doesn't
enforce it)

Images, in this order (cover first — it is the required cover image):

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

Per the Overview tab, Project Links is where your code notebook goes:
"Your code should be submitted as a public notebook in the Project
Links field." The form has no code-submission selector; linkage is (1)
the same-team rule (§2.1.b; you are the solo team megusalexandrus),
(2) the submission IDs named in the body's first paragraph, and (3) the
Overview's note under Accuracy: "you will be asked to provide your
submission ID" — when asked, give **56683298**.

Add these links (title -> URL):

1. **Public walkthrough notebook** (satisfies the required public
   notebook) -> the URL of the new public notebook you upload from
   `public_notebook.ipynb` (runbook Step 4). Must open logged out.
2. **Source code (GitHub)** -> https://github.com/msafdari/FlyGI
   The repo must be public before you submit (release step, ~Nov 1).
3. **Submission notebook (produced 56683298)** ->
   https://www.kaggle.com/code/megusalexandrus/flygi-arc-agi-3
   Currently PRIVATE. Linking it means it is AUTOMATICALLY MADE PUBLIC
   after the deadline (Overview, verbatim; register AP-16) — which we
   want anyway, so prefer making it public yourself on release day
   (also meets Rules §3.6.b). Either way, BEFORE submitting put the
   MaleCNS CC BY 4.0 citation on the private dataset
   megusalexandrus/flygi-malecns-runtime's description (AP-6), in case
   auto-publication cascades to the notebook's attached dataset.

## Files (optional)

Nothing to upload: the code lives in the linked repo. (The limit is
100 MB; the compiled connectome arrays belong in a Kaggle Dataset
anyway, per AGENTS.md.)

## DOI Citation (optional; recommended)

**Opt in.** It's free, the DOI is minted after the competition ends,
and it gives the writeup a citable identifier alongside the repo's
CITATION.cff.

## Before clicking Submit

- [ ] Checklist reads 6 of 6, AND the gallery has the cover image, AND
  a public notebook is in Project Links (eligibility layer).
- [ ] The MaleCNS CC BY 4.0 citation is on the Kaggle dataset
  description (AP-6/AP-16).
- [ ] Submission ID 56683298 noted, ready for when the organizers ask.
- [ ] The repo link opens logged out (repo is public).
- [ ] The walkthrough notebook opens logged out.
- [ ] Preview renders the body's headers and lists correctly.
- [ ] Click **Submit**, not save-as-draft. One submission only.
- [ ] Tell the Claude session the confirmation state.
