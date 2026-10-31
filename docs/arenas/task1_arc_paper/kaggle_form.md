# Kaggle Writeup form — field-by-field paste guide

**TITLE/SUBTITLE AMENDED ON THE LIVE WRITEUP 2026-10-30 (user's call,
reach over gravitas; body unchanged, still Submitted, slug unchanged):**
Title (73/80): "We Wired a Whole Fly Brain into an AI Benchmark. Its
Own Shuffle Beat It." Subtitle (138/140): "166,700 neurons, 25M
connections, preregistered kill rules, one deployed survivor: the
fly's eye map. Every control and every kill public." Accuracy notes:
"its own shuffle beat it" carries the same scope as the original
subtitle's claim (the circuits tested in full scored below their
degree-preserving rewires); "25M connections" is the 24,994,595-EDGE
runtime (edges are connections, not synapses — do not write "25M
synapses"). The original title/subtitle below remain the record of
what was first submitted.

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

**RENDERER GOTCHA (measured 2026-10-30, fixed same day):** Kaggle's
writeup renderer treats SINGLE newlines inside paragraphs as hard line
breaks, so pasting the hard-wrapped writeup.md verbatim renders every
~75-char source wrap as a forced break (the user caught it on the live
page). The fix: paste an UNWRAPPED body — join lines within each
paragraph and list item, keep blank lines between blocks. The
submitted description was replaced with the token-identical unwrapped
form via "Update Submission" (still Submitted). Any future re-paste
must unwrap first.


**BODY AMENDED 2026-10-31 (user's call; the Biswas compass PASS added,
compensated by fact-gated trims — every changed sentence listed in the
2026-10-31 writeup-amendment WORKLOG entry; all numbers pass through
docs/social/FACTS.md).** The update is a full-body replacement via the
writeup editor ("Update Submission"; title, subtitle, slug, images,
links all unchanged). Unwrap before pasting, as below.

Paste the READY-MADE UNWRAPPED body: `kaggle_body_unwrapped.md` in this
directory, verbatim, whole file (generated from writeup.md,
token-identical, verified). It starts at "**One measured pair carries
the paper.**" and now ends with "is in the open repository." The body is
markdown (## headers, bold, numbered lists). Spaced em-dashes were
closed up (word — word -> word—word) so every word counter agrees; this
is typography only, no word changed.

Expected count: 1,461-1,463 words (wc -w vs naive whitespace split) —
~37 words under the 1,500 limit on any counter. If Kaggle's counter
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

- [x] Checklist reads 6 of 6, AND the gallery has the cover image, AND
  a public notebook is in Project Links (eligibility layer).
- [x] The MaleCNS CC BY 4.0 citation is on the Kaggle dataset
  description (AP-6/AP-16).
- [x] Submission ID 56683298 noted, ready for when the organizers ask.
- [x] The repo link opens logged out (repo is public).
- [x] The walkthrough notebook opens logged out.
- [x] Preview renders the body's headers and lists correctly.
- [x] Click **Submit**, not save-as-draft. One submission only. (DONE 2026-10-30; "Submitted!" banner.)
- [x] Tell the Claude session the confirmation state. (Recorded in WORKLOG 2026-10-30; DOI opt-in left unticked -- optional, one click until the deadline.)
