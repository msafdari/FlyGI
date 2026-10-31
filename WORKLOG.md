# FlyGI durable worklog

## H-CX-BISWAS-FITTED registry close executed: supported -- and the Task-10 menu is COMPLETE -- 2026-10-31

Cloud-side close of the run recorded in the entry below (local run
0e80c2f; every number cited in the registry traces there). Registry
status open -> supported, bullet 6 carries the full measured record
and the close at the frozen scope: GIVEN FITTED PER-TYPE PHYSIOLOGY
-- their exact threshold-linear form, their derivation recipe applied
once to our compiled counts -- the Biswas-fitted EPG-Delta7
realization of the standalone MaleCNS CX sustains a position-faithful
heading bump that its degree-preserving rewires do not.

Superlative, checked against the whole registry before writing: this
is the record's FIRST BIOLOGICAL-COMPUTATION PASS AGAINST THE
DEGREE-PRESERVING NULL. (H-FLYGI-FLYBENCH-TERMINAL was a functional
win but a mechanism transfer on FlyBench's benchmark with FlyBench's
own rewired-control metric; H-APL restored sparsity with no rewire
bar; Stage-A/FB are structural.) Not score-adjacent; 0-for-16
untouched.

Two attribution clarifications on the entry below, dated here rather
than edited there: (1) the frozen registration names AC-B1
(label-derived wedges) and AC-B2 (whole-brain vs ROI-restricted
counts) as the r_a-divergence suspects; the entry's "expected under
AF-7's measured export drift" is a further INFERRED candidate whose
bridge is untested -- the registry carries the frozen attribution.
(2) "Duan/Dong/Fiete's necessity claim, reproduced" overstates: their
claim is hemibrain, different protocol; ours is CONSISTENT WITH it
(inferred across datasets), recorded at that tier in SYNTHESIS.

One mechanistic note for readers: G1's identical per-angle rows (err
0.0 deg at every write angle) are the expected signature of the
recipe's exact circulant symmetrization -- the simulated realization
is 8-fold symmetric by construction -- not a metric defect; the
class-3 contrast (155-177 deg errors) came from an unfitted,
unsymmetrized spiking system on the same subcircuit.

Record propagation: killtest_design section-3 close note; runbook
banner (MENU COMPLETE) + 3b closed; SYNTHESIS record map + closing
paragraph (the structure/function ladder, each rung at its tier);
HANDOFF row 10; ASSUMPTIONS AC-B1..B5 annotated with run outcomes
(the AC-B1/AC-B2 canary FIRED and is recorded as such); README EB
ring row updated from "Structure PASS, computation KILL" to the
two-sided result; docs/social/FACTS.md gains the Biswas section with
never-say rules. LEAGUE.md's Biswas row is now knowingly stale
("open"; regenerated locally before this close) -- same deferral as
natstat, one local command, noted in runbook 5c/3b.

## H-CX-BISWAS-FITTED: PASS -- the program's first computation-level wiring win, given fitted per-type physiology -- 2026-10-31

The user ran the final menu item on claude/cool-meitner-x8e79i (35/35
tests first; instrument untouched; 10.7 s, exit 0). The close
sentence, scope frozen in the registration: GIVEN FITTED PER-TYPE
PHYSIOLOGY -- Biswas et al.'s exact threshold-linear form with their
published derivation recipe applied once to our compiled counts --
the standalone MaleCNS CX sustains a position-faithful heading bump
that its degree-preserving rewires do not.

MEASURED: in-cloud-pattern gate passed locally (published-realization
recovery r_a 0.5 exact; synthetic G1 8/8; uniform can-fail control
true; 34 algebra identities). Composition exact (148 =
46/20/22/42/18); EPG 46/46 wedge-labelled, wedge sizes
[4,4,6,6,6,6,6,8]. REAL wiring: A_Delta=8 valid fit (r_a 0.4221,
unique candidate, all 8 attractor checks true), G1 8/8 with err 0.0
deg AT EVERY WRITE ANGLE, circvar 0.234, retention 1.0; A_Delta=6
valid fit (r_a 0.2132), G1 8/8, err 0.0 deg everywhere, circvar
0.245, retention 0.926; A_Delta=4 no valid fit (reported). NULLS: all
three rewires (4242-4244) admit NO valid fit at ANY config -- their
published attractor conditions have no solution on shuffled counts --
so G1 fails everywhere; the specificity is carried by the fit
algebra itself. G2 non-decisional as frozen (their model defines no
rotation input). CONTEXT, reported: fitted r_a on our counts differs
from their published realization (0.4221 vs 0.548 at A_Delta=8;
0.2132 vs 0.437 at 6; cross-check "consistent: false") -- expected
under AF-7's measured export drift (annotations + signed weights
differ from their snapshot); the verdict does not rest on matching
their numbers, only on their form + recipe.

The structure/function split now reads, with every tier in place: the
counts carry the ring topology (Stage A, p 0.005); unfitted
physiology cannot compute with it (classes 1-3, all measured); FITTED
per-type physiology can, and the computation is wiring-specific
(this result) -- Duan/Dong/Fiete's necessity claim, reproduced on
MaleCNS with Biswas algebra. Registry close is the cloud side's step.
LEAGUE.md regenerated here with the natstat BLOCKED row (score rows
intact). JSON gitignored at results/arenas/cx_biswas_killtest.json.


## Biswas adversarial review: two pre-data-contact blockers found and fixed; instrument re-validated -- 2026-10-31

Three-reviewer workflow (equations re-read from the uploaded PDF at
source, code vs the frozen registration, record sweep) ran BEFORE the
local measurement -- the fourth straight review pass to catch real
blockers (17, 37, 31, now 9 findings). Confirmed and fixed same day,
all pre-data-contact (the measurement never ran on the defective
instrument):

- BLOCKER 1 (fit/sim mismatch): C^EIE was computed from the RAW unit
  blocks and then distance-averaged; the paper computes it from the
  circulant-SYMMETRIZED blocks ("the corresponding count vector
  c^EIE from the first column"; Supp Fig S1). MEASURED consequence on
  a structured toy: the fit certified rel residual 8e-9 while the
  simulated system sat 8.7e-3 off the branch (~10,000x FIT_RTOL_SYM)
  -- a validity certificate for a system G1 never integrated. Fixed
  at the root; regression test asserts pre-symmetrizing the inputs
  changes nothing at all three configurations.
- BLOCKER 2 (recipe misread): the freeze said "mirror-averaging
  only" for A_Delta=6,4, but B.38/E.97 define mirror symmetry of the
  EFFECTIVE matrix; the paper symmetrizes the counts ONCE (circulant)
  for all three realizations, the mirror asymmetry arising solely
  from the active-z restriction in C^EIE. Corrected in place, dated,
  in killtest_design.md section 3.
- MAJORS: fit_mirror now refines the minimal-residual point of EACH
  candidate cluster (per-slice local minima clustered across
  adjacent gamma_II slices, cap 10) and filters invalid roots after,
  per their Methods (B-R9); the LM feasibility domain now matches
  the rows the six parameters read -- MEASURED regression: inflated
  inactive-row self-loops no longer strand LM on the 1e6 plateau
  (equations solve to 3.9e-16, validity then correctly fails
  full-row positivity). B-R8 records the mirror sign checks, with
  gamma^II <= TOL_DRIVE at the published 0 boundary.
- GOOD NEWS FINDING: AC-B4's placement is CORROBORATED at figure
  level -- their Fig 4f/g schematics and Fig 4i predictions (z = 0
  exactly at units 4-5 for A_Delta=6, 3-6 for A_Delta=4, verified at
  400 dpi) match the registered choice. ASSUMPTIONS.md updated.
- RECORD FIXES: runbook top banner (natstat CLOSED; 3b the one
  remaining command), HANDOFF row 10 Biswas tail, SYNTHESIS record
  map, AC-B1 wording (the convention is ours; label rotation now
  measured exactly immaterial), 1-based/0-based unit numbering
  clarifier, and the LEAGUE.md regeneration deferral now stated in
  runbook 5c (regenerate LOCALLY; the cloud container lacks the
  results/ checkpoints and would drop the measured score rows).

POST-FIX, MEASURED in-cloud: gate passes unchanged (recovery r_a to
4.8e-9, synthetic G1 8/8, can-fail holds, 34 identities); synthetic
A_Delta=6 mirror root pinned UNCONDITIONALLY at r_a 0.21607
(residual 3.9e-16, 1 cluster); the same synthetic has no A_Delta=4
realization (10 clusters refined, all filtered -- the filter working,
never a crash); 35 tests pass. The local run command is runbook 3b.

## Biswas instrument LANDED and gate-validated in-cloud; one local command pair remains -- 2026-10-31

scripts/arenas/cx_biswas_killtest.py + tests/test_cx_biswas_killtest.py
(32 tests) built against the frozen numeric completion, committed
AFTER the registration commit. MEASURED in-cloud, all on synthetic
constructions (no MaleCNS data exists here): the amended gate passes
-- synthetic recovery r_a 0.5 to 4.8e-9 and gammas to ~1e-9 relative
(rel residual 1.2e-8 vs the 1e-6 floor), synthetic G1 8/8 (retention
~1.000, PVA err 0.0; the fixed-active-set Jacobian carries exactly
the two marginal family modes, all other eigenvalues Re < 0),
uniform counts yield NO valid fit (the gate can fail), 34 analytic
identities pass, and the mirror algebra at the known gamma*
reproduces the symmetric branch parameters to 1e-9 (equation
residuals ~1e-16); fit_mirror end-to-end 0.3 s on the 100^3 grid.
Build-time operationalizations B-R1..7 dated in killtest_design.md
(exactness floors, TOL_DRIVE for the identically-zero A.31 drive,
canonical mirror placement, the empty-Delta7-unit rule: fit-fail on
rewires / BLOCKED floor on real, the gamma^EIE quadratic count-scale
covariance, sigma=1 + candidate multiplicity). Full in-cloud suite:
666 passed, 17 skipped; the only failures are the pre-existing
python-3.12-only controller files (PEP 695 syntax in
src/flygi/controller/scene.py; this container runs 3.11, the verdict
machine runs 3.12) -- untouched by this change. Registry bullet 4,
runbook section 3b (the run command pair), SYNTHESIS pointer updated.
NOTE, branch: this resumed cloud session pushes to
claude/cool-meitner-x8e79i, which fast-forwards from
claude/admiring-goldberg-wtqkbg's tip 449a9e4 -- the local session
must fetch/checkout that branch (exact commands in the hand-off
message) rather than plain git pull.

## Biswas numeric completion FROZEN from the uploaded v2 PDF; instrument build follows -- 2026-10-31

The user uploaded the Biswas et al. v2 PDF (bioRxiv
10.1101/2024.11.01.621596v2, 63 pp) directly into the cloud session,
resolving the egress block. Read in full in-cloud: main text +
Methods, Appendices A-I, Tables 1-2 (the tables are reference maps to
equations: Table 1 = A.10/A.13, B.44/B.48, B.54, A.21/B.50,
A.26/B.55; Table 2 = A.35/B.63, C.82, C.81). The dated NUMERIC
COMPLETION is now frozen in killtest_design.md section 3 -- BEFORE
any instrument code, per the partial-freeze rule: model form,
coarse-graining recipe, both gamma-fit procedures (fully-symmetric
r_a scan + mirror-symmetric grid+LM), validity conditions, the
amended in-cloud gate (synthetic recovery + can-fail control; the
published r_a values 0.548/0.437/0.391 enter only a data-contact
consistency reading), the G1 rate-model mapping, the completed null
bar, BLOCKED floors incl. the recipe-transfer-limit close, and
assumptions AC-B1..5 (also in ASSUMPTIONS.md). Scope inherited from
their paper and said plainly: the realization is EPG+Delta7 only;
PEN/PEG stay unused; close sentences scope to "the Biswas-fitted
EPG-Delta7 realization derived once from our compiled counts".
Registry bullet 3 added (H-CX-BISWAS-FITTED stays open until the
run). NEXT: build scripts/arenas/cx_biswas_killtest.py + tests
against this frozen text, then the one local run command.

## Natstat run 3 COMPLETE AND VALID: G0 passes, G1 at chance -- H-T4T5-NATSTAT-DIRECTION closes BLOCKED (AB-4 convention limit, ANS-5 negative) -- 2026-10-31

Third local run (record = the user's pasted gate lines + g1 JSON,
banked here; 211.3 s; exit 3). En route, the first attempt crashed AT
the G1 call with OverflowError: the exact sign test computed 2.0**n
as a float, which overflows past n~1023, and G1 runs at n=1,152.
Fixed under the registered plumbing allowance (commit 449a9e4):
integer 2**n, exact at any magnitude and bit-identical at every small
n any prior harness ran (DSEC 33, DVS 18, CX 18 cells -- no recorded
verdict changes); the identical latent bug fixed in dsec_killtest.py;
regression test at n=1152; 48/48 tests. No verdict-relevant quantity
existed at the crash.

MEASURED (completed run): corpus van_hateren 60 images, checksums
verified against the first-contact pin; contrast calibration gamma
8.0 (p95 |drive| 0.5000); scramble selftest ok (worst amplitude rel
err 3.53e-16). G0 PASSES: v2 median DSI 0.3355 (band 0.3216 +/-
0.02), tiling exact False -> tie-aware pass True -- the amendment
behaved as designed on the same 0.2% T5a tie. 1,152 eval items (48
images x 8 directions x 3 speeds; 384 items/speed at 442/221/111
frames; 74.3/46.1/35.5 s), unstable fraction 0.0. G1 FAILS ON THE
MEASUREMENT: median absolute heading error 90.90846603116665 deg vs
the 90.0 deg chance floor; exact sign test 572 of 1,152 items below
chance, p 0.6045519607913874. Verdict line: BLOCKED, floor 3 (G1):
REAL-natural did not beat the 90-deg chance floor (usable-input
gate).

CLOSE (the sentence pre-stated in killtest_design.md section 5 BEFORE
this run, applied unchanged): H-T4T5-NATSTAT-DIRECTION is BLOCKED as
a measured convention limit -- the AB-4-class drive convention did
not feed the circuit usable input for natural movies (ANS-5 resolved
in the negative). MEASURED, the pair that defines the limit: through
the same stimulus path the same circuit decodes moving-edge direction
in band (G0 0.3355; T4/ON 0.3192, T5/OFF 0.3434) and natural-movie
direction at exactly chance (90.91 deg vs the 90 deg floor, p 0.605,
zero unstable). The convention, not the simulation, is where the
information dies. That is a statement about the convention -- not
about natural-scene statistics, not about T4/T5, not about the fly --
and never a statistics verdict: the 2x2 (bars B1/B2) never ran. No
fourth run.

## natstat run 3 COMPLETE AND VALID: G0 passes, G1 fails on the measurement -- H-T4T5-NATSTAT-DIRECTION closes BLOCKED per the pre-stated contingency -- 2026-10-31

Run 3 took two attempts, both recorded. FIRST ATTEMPT crashed AT the
G1 call with OverflowError: the exact sign test computed 2.0**n as a
FLOAT, which overflows past n~1023, and this instrument's G1 runs at
n=1,152 eval items. No verdict-relevant quantity existed at the crash
(the G1 statistic itself died), so the registered plumbing-fix
allowance applied: fixed to integer 2**n (exact int/int division at
any magnitude; bit-identical at every small n any prior harness ran --
DSEC 33, DVS 18, CX 18 -- so no recorded verdict changes), the same
latent bug fixed in dsec_killtest.py's copy, regression test added at
n=1152 (48/48 pass), committed 449a9e4, and run 3 completed.

THE COMPLETED RUN (211.3 s; corpus checksums verified vs the pin;
calibration gamma 8.0 p95 0.5000; scramble selftest 3.5e-16):
- G0 PASS: pooled v2 median DSI 0.3355 (band 0.3216 +/- 0.02), T4-on
  0.3192 / T5-off 0.3434, tie-aware tiling clause per cb62674.
- Real/natural arms simulated in full: 1,152 items (48 images x 8
  directions x 3 speeds), ZERO unstable.
- G1 FAIL, measured: median angular error 90.91 deg vs the 90.0 deg
  chance floor; one-sided sign test p 0.605 (572/1152 below chance).
  The decode sits exactly at chance.

CLOSE, per the contingency pre-stated in the registration BEFORE this
run: G0-passes-but-G1-fails means the AB-4 drive convention does not
feed the circuit usable input for NATURAL movies -- a measured
convention limit (ANS-5 resolved negative), never a statistics
verdict. H-T4T5-NATSTAT-DIRECTION closes BLOCKED; NO FOURTH RUN. The
sharp measured pair this leaves: through the SAME stimulus path, the
same circuit decodes moving-edge direction in band (G0) and natural-
movie direction at exactly chance (G1) -- the convention, not the
simulation, is where the information dies. Registry close is the
cloud side's step. JSON gitignored at
results/arenas/natstat_killtest.json.


## Natstat run 2: luminance fix CONFIRMED on the verdict machine; residual G0 failure ruled an argmax tie and amended -- 2026-10-31

Second local run (record = the user's pasted gate lines + JSON, banked
here): 36/36 tests first; exit 3 at G0 in 20.0 s; corpus checksums
verified vs the first-contact pin. MEASURED: pooled v2 DSI 0.1763 ->
0.3355 (band 0.3216 +/- 0.02 -- PASSED), T4/ON 0.3192, T5/OFF 0.3434,
defined fraction 1.0, per-subtype DSIs T4a 0.2156 / T4b 0.1772 / T4c
0.4495 / T4d 0.4293 / T5a 0.2044 / T5b 0.2077 / T5c 0.3213 / T5d
0.4531. The 587b40d fix did exactly what its drive-level measurement
predicted. G0's sole remaining failure: tiling-exact, entirely T5a --
measured +y vs reference -x at direction totals +y 1.3388 / -x 1.3361
/ +x 0.8915 / -y 0.8844 (a 0.2% top-two margin on the near-isotropic
weakest subtype); the other seven tile exactly. G1 reported failed
alongside, as in run 1 (g1 numeric block not yet banked -- requested
with the next report).

DISPOSITION (cloud-side, dated amendment in killtest_design.md +
in-code): gate-operationalization defect, the THIRD recorded instance
of the argmax-degeneracy class (Stage-A shifter p 0.459; measureBump1
45-deg quanta; this 0.2% tie). The tiling clause is now tie-aware at
G0_TIE_MARGIN 0.98, derived from the measured post-fix drive-residual
bound (~2% crossing transients), not tuned; tiling_exact stays in the
record; genuine flips and total-less mismatches still fail. Tests 36
passed (4 tie-case assertions added). FULL third run required.
PRE-STATED before that run: if G0 passes and G1 still fails, the
registered convention-limit close applies (AB-4 drive unusable for
natural movies; ANS-5 negative; BLOCKED, never a statistics verdict).

## natstat re-run after the luminance fix: BLOCKED again at G0, now by ONE near-tie subtype (T5a argmax, 0.2% margin) -- 2026-10-31

The user re-ran per the cloud instruction (36/36 tests first; corpus
checksums VERIFIED against the first-contact pin; calibration gamma
8.0 p95 0.5000; scramble selftest 3.5e-16; 20.0 s to the gate). The
587b40d luminance fix WORKED for the magnitude: G0 pooled v2 median
DSI is now 0.3355 -- INSIDE the 0.3216 +/- 0.02 band (was 0.1763) --
with T4-on 0.3192 and T5-off 0.3434 both healthy and defined fraction
1.0. G0 still fails, on its OTHER clause: tiling exact = False.

MEASURED, the whole failure is one subtype: T5a reads preferred +y
where the fc25 reference tiling says -x, and its direction totals are
a photo finish -- +y 1.3388 vs -x 1.3361, a 0.2% margin (next: +x
0.8915, -y 0.8844; subtype DSI 0.2044, 61 cells). The other seven
subtypes match the reference exactly (T4a-d and T5b-d, margins
comfortable). T4 and T5 each show 4 distinct preferred directions.
G1 reported failed alongside, as before.

Disposition is the cloud side's call under the frozen registration:
either a residual small path discrepancy (T5a is the weakest-DSI
OFF subtype and sits nearest isotropy) or a gate-operationalization
issue -- "exact tiling" rests on an argmax that a 0.2% tie can flip,
the same degeneracy class the Stage-A shifter amendment documented.
No local changes to the instrument; JSON gitignored at
results/arenas/natstat_killtest.json.


## RELEASED AND SUBMITTED (early): repo public, writeup in -- recorded cloud-side 2026-10-31

The local session executed the full release 2026-10-31 (its commits
956a1af..78ef486 carry the mechanics; this entry banks the hand-off
facts the registry and HANDOFF cite). Repo PUBLIC at
github.com/msafdari/FlyGI (MIT-0, main default; GitHub secret
scanning 0 alerts; local gitleaks history scan clean). FLAT downgrade
verified in all five named files pre-release; LEAGUE regenerated with
the reading note, all four checklist verifications passed. Forum
posts live same day (Rules 3.6.b / AP-12): Paper Track discussion
754287, ARC-AGI-3 discussion 754288. Dataset flygi-malecns-runtime
carries the CC BY 4.0 attribution + citation. Walkthrough notebook
public (kaggle.com/code/megusalexandrus/
flygi-what-a-fly-connectome-computes-for-free). WRITEUP SUBMITTED
once (AP-11): kaggle.com/competitions/arc-prize-2026-paper-track/
writeups/flygi-connectome-attribution-audit, body verbatim 1,484
words, submission notebook linked private under AP-16
(auto-publication at deadline is the operative path; Kaggle locks
visibility flips until close). DOI opt-in ticked; Zenodo repo-DOI
parked as TODO. Two post-submit amendments recorded in
kaggle_form.md: the unwrap-before-paste rendering gotcha, and the
punched-up title/subtitle ("We Wired a Whole Fly Brain into an AI
Benchmark. Its Own Shuffle Beat It."). TERMINOLOGY RULE from the
local session, now enforced: 24,994,595 is EDGES -- write
"connections", never synapses (instagram.md's "24.5 million
synapses" corrected to "25 million connections" with this entry).

REMAINING: natstat local re-run (fix landed 587b40d; runbook 5b);
Biswas numeric completion (needs the v2 Methods text -- extraction
ask sent); Dec 4 results; IJCNN decision after.


## Post-release bookkeeping: DOI opt-in DONE (user); Zenodo repo-DOI parked as TODO -- 2026-10-30

- The writeup's "Opt in to DOI creation" box is ticked (user's click;
  the DOI mints after the competition ends).
- TODO (user, "a bit later", no deadline): mint a repo DOI -- enable
  FlyGI at zenodo.org -> GitHub, then cut a GitHub release; Zenodo
  mints the DOI (checklist's optional item, CITATION.cff already
  carries the citation metadata).
- OPEN THREADS, all cloud-side next: (1) natstat stimulus-path fix
  (T5-off lead), then the local re-run here (corpus pinned, one
  command); (2) Biswas numeric completion (recipe re-derivation; four
  PDFs local); (3) confirmation that the Task-10 hypothesis closes
  landed in the registry.


## Writeup title/subtitle punched up on the live submission (user's call); still Submitted -- 2026-10-30

At the user's request (max reach for investors/recruiters/
collaborators, no fibbing), the submitted writeup's title and subtitle
were replaced via "Update Submission" -- body untouched, slug
unchanged, banner still "Submitted!":
- TITLE: "We Wired a Whole Fly Brain into an AI Benchmark. Its Own
  Shuffle Beat It." (73/80) -- same truth value as the original
  subtitle's measured claim (both fully-tested circuits scored below
  their degree-preserving rewires).
- SUBTITLE: "166,700 neurons, 25M connections, preregistered kill
  rules, one deployed survivor: the fly's eye map. Every control and
  every kill public." (138/140). Corrected en route: the draft said
  "25M synapses"; the 24,994,595 figure counts EDGES (connections),
  so "connections" it is.
Four options were offered (including keep-as-was); the user chose the
declarative-conflict form. The original judge-calibrated pair is
preserved in kaggle_form.md as the first-submission record.


## Writeup formatting fix: unwrapped the hard-wrapped body (words unchanged); still Submitted -- 2026-10-30

The user spotted forced line breaks on the rendered writeup. CONFIRMED
on the live page: Kaggle's renderer treats single newlines inside
paragraphs as hard breaks, so writeup.md's ~75-char source wrapping
rendered as ragged forced breaks (first paragraph ended with the lone
word "control."). FIX: regenerated the body with a markdown-aware line
joiner -- paragraphs and list items joined to single lines, block
structure untouched -- verified token-identical (1,484 words, same
word stream, zero internal paragraph newlines), replaced the Project
Description, and saved via "Update Submission" (NOT "Unsubmit and Save
as Draft"). Verified after: paragraphs flow to full column width and
the banner still reads "Submitted!". writeup.md in the repo keeps its
hard wrap (GitHub renders it correctly); the gotcha + unwrap rule is
recorded in kaggle_form.md's Project Description section. The forum
posts and dataset description were authored unwrapped and were never
affected.


## WRITEUP SUBMITTED (AP-11, the submit-once step): "Submitted!" confirmed -- 2026-10-30

Executed per kaggle_form.md field by field, via the user's Chrome
session. Final URL (slug set per the guide):
kaggle.com/competitions/arc-prize-2026-paper-track/writeups/flygi-connectome-attribution-audit

Pre-submit verifications, all passed: body 1,484 words (< 1,500);
media present (card.png accepted at 1120x560; gallery = cover + 3
figures, cover first; empty default video slot deleted); checklist
6 of 6 PLUS the eligibility layer (cover image in gallery, public
walkthrough notebook in Project Links); repo and walkthrough notebook
both open logged out (HTTP 200); preview rendered headers/lists/body
end-to-end. Project Links as registered: (1) Public walkthrough
notebook, (2) Source code (GitHub), (3) Submission notebook (produced
56683298) -- linked PRIVATE under the AP-16 auto-publication consent;
Kaggle's own dialog confirmed "Submitting this writeup will make the
notebook public once the competition ends," and a pre-submit attempt
to flip it public directly was refused by Kaggle's lock-until-close
("Making this notebook public will be locked until the competition
ends"), so AP-16 is the operative path, prerequisite (dataset CC BY
citation) already in place.

CONFIRMATION STATE: banner "Submitted! You can make changes until the
deadline (Nov 9, 2026 at 3:59 PM PST)". Title, subtitle, and body
exactly the committed writeup.md; nothing was trimmed (no over-limit
counter fired). ONE divergence from the guide: the optional DOI
opt-in checkbox is NOT ticked (the session's action classifier
blocked the repeated checkbox clicks; one manual click on the edit
page enables it any time before the deadline). Nothing else remains:
this closes the release + submission sequence. Record of changes
stays open until the deadline but none are planned.


## RELEASE COMPLETE: repo public, both forum posts live, dataset attributed, notebook public -- 2026-10-30

Executed after the user's visibility flip, via the user's Chrome
session (Google SSO, no credentials handled):
- GitHub secret scanning + push protection ENABLED on the public
  repo; alerts 0 (confirming the clean local gitleaks history scan).
- Dataset megusalexandrus/flygi-malecns-runtime: description now
  carries the CC BY 4.0 attribution, the MaleCNS citation
  (doi:10.1016/j.cell.2026.08.015) and the non-endorsement
  disclaimer, verbatim from data/README.md. License field was already
  CC BY 4.0. Stays private until the submission publishes it.
- Public notebook (runbook step 4): public_notebook.ipynb imported,
  Quick Save Version 1, visibility Public, renders top to bottom.
  URL: kaggle.com/code/megusalexandrus/flygi-what-a-fly-connectome-computes-for-free
  (Kaggle title capped at 50 chars: "FlyGI: what a fly connectome
  computes for free"; the notebook's own H1 is unchanged.)
- AP-12 forum posts, verbatim from kaggle_forum_posts.md with
  REPO_LINK = github.com/msafdari/FlyGI: Paper Track discussion
  754287; ARC-AGI-3 discussion 754288. Same day as the flip, per
  Rules 3.6.b.
- Checklist: all boxes ticked except the optional Issues template
  (explicitly non-blocking).
STILL OPEN, deliberately: the Writeup submit-once step (kaggle_form.md
+ runbook steps 5-6) before Nov 8 23:59 UTC (Kaggle shows the
deadline as Nov 9, 3:59 PM PST). The in-progress draft banner on the
Paper Track page is the existing draft; nothing was submitted.


## PUBLIC RELEASE EXECUTED through the visibility flip -- repo is live; Kaggle steps await the user's session -- 2026-10-30

The release checklist ran in order on the machine holding
results/connectome_agent. MEASURED at each gate:
- LEAGUE.md regenerated; all four verifications passed (FLAT reading
  note in the header; hypothesis table matches the registry; both
  reservoir rows complete at 75; zero missing rows).
- FLAT downgrade verified in all five named files; no surviving claim
  that the harness could have registered an advantage (the two grep
  hits are the explicit disclaimer and the tie description).
- THIRD_PARTY_NOTICES completed: two tracked derivatives were
  unlisted and are now entered -- flyvis pretrained-parameter
  summaries (MIT, TuragaLab/flyvis) and the Pisokas 2020 fixture
  (MIT, johnpi/eLife_Pisokas_Heinze_Webb_2019, SPDX via GitHub API).
- Branch merged to main as ordinary merge 2b0fa84 (one WORKLOG
  conflict; resolved keeping the full record under main's widened
  compaction note); merged suite 921 passed.
- Secret scan, both halves: local history-level gitleaks 8.30.1 over
  all 322 commits (42 MB) -- no leaks; after the flip, GitHub secret
  scanning + push protection enabled, alerts = 0.
- VISIBILITY FLIPPED BY THE USER (the auto-mode classifier correctly
  reserved the irreversible step): https://github.com/msafdari/FlyGI
  is PUBLIC, MIT-0, default branch main.

REMAINING (user's Kaggle session required; no local kaggle.json, and
credentials are not mine to enter): the two release-day forum posts
(drafts in kaggle_forum_posts.md, {{REPO_LINK}} ->
https://github.com/msafdari/FlyGI), the CC BY 4.0 attribution +
MaleCNS citation on the flygi-malecns-runtime dataset page (text from
data/README.md section "Attribution and license"), and the
public_notebook.ipynb upload (runbook step 4). The Writeup stays
untouched until its submit-once step before Nov 8, 23:59 UTC.


## Run-record backfill: the pasted Task-10 run JSONs banked into the durable record -- 2026-10-30

PROVENANCE, stated first: every number below was pasted verbatim into
the session by the user on 2026-10-29 from the gitignored local
results (results/arenas/*.json and the verdict-script outputs). The
2026-10-29 registry closes cited several of these values while the
five WORKLOG run entries carried only headline numbers -- the
adversarial close review (47 agents, run 2026-10-29) correctly
flagged every such value as untraceable from the repo alone. This
entry banks them so the registry is self-tracing. Nothing here is a
new measurement; it is the hand-off record, recorded. All 37
confirmed review findings (3 clusters of blockers: untraced numbers,
the false zero-fixes claim, stale/contradictory release prose incl.
the social drafts and the non-actionable LEAGUE checklist item) are
applied in the commit this entry ships in.

- RESERVOIR (H-ARC-HARNESS-SENSITIVITY), full-precision compare
  outputs: positive-control 0.0137; vs eff-real-signed -0.051064,
  CI [-0.153193, +0.000000]; vs eff-null-degree-preserving +0.005814,
  CI [+0.000000, +0.017443]; matched-random twin 0.0320, control vs
  twin -0.018334, CI [-0.055001, +0.000000]. LEAGUE regenerated in
  commit c3ec5bd (the 2026-10-29 close bullet's pointer to 95914f7
  is corrected in the registry today).
- DECOMPOSITION (H-STAGEA-NULL-DECOMPOSITION) JSON: real bandedness
  0.5881 / mirror 0.01445; null maxes per family: within-pre
  0.50366/0.01523, global 0.51038/0.01552, sign 0.64245/0.01914;
  p 0.00498/0.00995 (both weight families), 0.43781/0.82587 (sign);
  fraction_magnitudes_changed 0.93704 (within-pre) / 0.96038
  (global); fraction_signs_changed 0.3899 over 148 sign-bearing
  columns; all invariants valid; elapsed 22.9 s.
- FB (H-FB-COLUMNAR-TOPOLOGY) JSON: subcircuit 1,399 nodes / 85,353
  signed edges; real bar1 antipodal 0.40548, bar2 mirror 0.01458
  (one-hop masses L 30.075 / R 28.315); null maxes 0.18682 /
  0.01286; p 0.00498 both; context vDelta antipodal 0.00041, PFL
  mirror 0.02168; coverage FC 1.0, hDelta 1.0, labelled-PFN 0.98788;
  column_counts FC 9 / hDelta 12 / vDelta 10 / PFNa 9 / PFNd 8 /
  PFNm_a 9 / PFNm_b 9 / PFNv 9; irregular_flagged all 0;
  consensus_nt_audit "all columnar types 100% acetylcholine";
  163.4 s.
- NATSTAT (H-T4T5-NATSTAT-DIRECTION) first-run JSON: gates
  {scramble true, g0 false, g1 false}; G0 band_v2 pooled median DSI
  0.17634, T4/ON 0.31583 (4 distinct preferred), T5/OFF 0.11562,
  defined fraction 1.0, T5 distinct 3; scramble worst amplitude rel
  err 3.5e-16; calibration chosen_gamma 8.0 / p95 0.5; elapsed_s
  20.6 TOTAL (the run entry's "5.8 s" was the measurement segment --
  both are true; the registry cites 20.6 s total from this JSON).
  The OFF-edge localization was the close-time LEAD from this channel
  split; it has since been MEASURED cloud-side (commit 587b40d: the
  drive boundary sat at fc2-native +0.5 exactly; OFF scored windows
  at positive lamina drive).
- T4T5 CLASS-3 (H-T4T5-CLASS3-DS) JSON/printout: sign audit 35,041
  curated edges, 0 flipped; gate A per-speed preferred-direction
  table [2.0, 3.0, 2.0] with preferred == designed 12/12; AT-2
  coverage 132/320 pairs at 0.9786 synapse mass; calibration 18
  gains 1e-05..3000, ALL STABLE, median evoked 0.000 Hz at every
  gain; gate B fc25 reference 0.32157.
- FLYBENCH MECHANISMS (H-FLYGI-FLYBENCH-SFA / -TERMINAL)
  verdict-script JSONs, n_shared_checks 149 (58 activation / 91
  suppression). METRIC NOTE, load-bearing: the verdict script's
  hard_graded is computed over the 149 SHARED checks and differs by
  construction from the run-headline "hard" tier (uniform row
  headline 0.6044; SFA run headline 0.6276; terminal run headline
  0.6418) -- the registered bars run on the VERDICT SCRIPT's values.
  SFA: hard_graded uniform 0.6078476716360247 -> 0.6304517572540541
  (delta +0.0226040856180294); activation_mean 0.7113888474695774 ->
  0.710560086550812 (-0.000828760918765381); overall graded
  0.6940025391943447; specificity 0.26838624338624334; core 0.8000;
  run 7/30. TERMINAL: hard_graded 0.6078476716360247 ->
  0.6444645432726246 (+0.03661687163659988); activation_mean ->
  0.7155087815384199 (+0.004119934068842479); suppression_mean
  0.7013620129934217; overall 0.7621652165934433; specificity
  0.3135251322751323; core 1.0000; run 11/30.
- BISWAS fetch details (files at ~/datasets/biswas_papers/):
  biswas2024_v2.pdf (v2 posted 2026-03-08, 63 pp incl. supplement;
  the MaleCNS version; recipe in Methods "Constructing
  connectome-derived ring attractors"; vectors only in the p7
  figure; no code/data-availability statement; their 1e6-parameter
  sweeps amplitude-matched to the MaleCNS vectors, p13);
  biswas_nsf_par.pdf (v1, 47 pp, NO MaleCNS content);
  biswas2026_followup.pdf (31 pp, hemibrain-only, text-searched);
  duan_fiete_2025.pdf FETCHED (v1 2025-05-29, 11 pp, hemibrain,
  carries the necessity claims; NeurIPS poster 115017, OpenReview
  zn4F6os6cq, no code link) -- the earlier rate-limit note is
  superseded; the fetch completed.


## Natstat OFF-edge instrument bug: found, measured, fixed; full re-run required -- 2026-10-29

G0 did exactly its job. The defect (dated finding in
docs/arenas/task10_menu/killtest_design.md; code-site comments at the
fix): natstat's drive->external boundary applied INPUT_DRIVE to the
AB-4 mid-gray-centered contrast instead of ABSOLUTE luminance.
MEASURED on the registered 169-column lattice, all 24 polarity x
direction x speed combinations: the composite drive sat at exactly
fc2-native +0.5 at every plateau and settle sample; worst-column
time-integrated divergence 4.887 a.u.s; the OFF item's entire scored
v2 window ran at POSITIVE lamina drive, outside fc2's native -1..0
envelope -- matching the measured G0 channel split (T4/ON 0.31583 in
band, T5/OFF 0.11562). INFERRED, bridge at the code site: the relu
floor absorbed the shift on the ON side; the OFF release increment
had no ceiling and doubled. FIX: one pure helper external_from_drive
= INPUT_DRIVE x (drive + MID_GRAY), routed through the three (only)
network-input call sites; the ANS-1/AE-1 single-shared-map guarantee
is preserved and now explicit. Post-fix: plateau/settle divergence
0.0 exactly; residual = the declared OP-5 pixel-sampling transient
(worst-column integral 0.132 a.u.s, 37x down). Four regression tests
added, EACH verified to fail on the pre-fix code -- including the
composite-path ON and OFF drive-equality tests the original
encoder-only test lacked (why it missed the bug: it asserted the
encoder's mid-gray-centered values in isolation, which were exactly
where the bug lived). Suites: natstat 36 passed; joint with
fb/dsec/brainscore/t4t5 109 passed. Registry bullet + runbook 5b
(re-run instructions) added. Per the frozen rule the FULL protocol
re-runs locally; the drive-level equality is MEASURED, the DSI
consequence is the re-run's to measure (Expected-tier statements
inherit the 0-for-16 base rate).


## Task 10 CLOSED cloud-side: six verdicts in the registry; ARC null prose downgraded before release -- 2026-10-29 [headline corrected 2026-10-30: six, not seven -- natstat's G0 BLOCK is an instrument statement, never a verdict]

Cloud-side close of the seven local runs (records 3313458..95914f7).
Registry: H-ARC-HARNESS-SENSITIVITY refuted (FLAT per the frozen
reading); H-STAGEA-NULL-DECOMPOSITION supported (the Stage-A PASS is
placement+magnitudes, not signs -- the pre-registered bridge's OTHER
branch realized); H-FB-COLUMNAR-TOPOLOGY supported (the program's
second structural PASS, both bars at the 200-null floor; AC-FB1/5/6
confirmed on the compiled runtime); H-T4T5-CLASS3-DS "null"
(blocked-closed: zero evoked spiking at every declared gain -- the
opposite class-3 failure mode to the CX; scope AT-1/AT-2 carried;
reopening path = new drive-convention registration);
H-FLYGI-FLYBENCH-SFA refuted (hard-tier gain bought by breaking core
1.000 -> 0.800 and the overall floor); H-FLYGI-FLYBENCH-TERMINAL
supported (first functional mechanism win; every bar; specificity
+0.2823 -> +0.3135; FlyBench scope only); H-T4T5-NATSTAT-DIRECTION
stays open (G0 did its job; OFF-edge stimulus-path instrument bug
localized, cloud-side fix in flight); H-CX-BISWAS-FITTED stays open
(fetch complete; RECIPE not tables; the 2026 follow-up is
hemibrain-only -- runbook guess corrected; completion = extract the
v2 Methods recipe + Table-1 conditions, derive the vectors from our
counts).

THE RELEASE-BLOCKING ITEM EXECUTED: the frozen FLAT consequence --
class-1 ARC null prose downgraded in docs/controls.md (measured
outcome + weakened tie reading + power floor), docs/experiment.md
(claim-boundary addition), EXPERIMENTS.yaml eff-row and reservoir
condition notes (render into LEAGUE.md on the user's local
regeneration), factsheet.md and writeup.md (harness-sensitivity
bound); public_release_checklist.md gained a verification item. The
published reading everywhere: under this interface no tested graph --
engineered or biological -- moved official score; power floor ~ +0.1
at 75 rows. Arena rewire instances untouched.

SYNTHESIS: Task-10 addendum (four map-moving results) + six record-map
rows. ASSUMPTIONS: 13 rows annotated with run outcomes (notably
AF-11 split FALSE-for-SFA / TRUE-for-terminal; AC-N4's other branch;
AT-2 exercised-blocked).

NEXT: (1) natstat OFF-edge fix lands with a recorded instrument-bug
finding; user re-runs natstat only. (2) Biswas numeric completion
from the v2 Methods (extraction pending), then the instrument.
(3) USER CALENDAR: Nov-1 release sequence now includes verifying the
FLAT downgrade (checklist); Kaggle writeup once before Nov 8
23:59 UTC; Dec 4 results; IJCNN decision after.


## Task 10 item 5: natstat BLOCKED at G0 -- the new stimulus path does not reproduce fc25's reference (plumbing, not a verdict) -- 2026-10-29

Exit 3 in 5.8 s of measurement; 31/31 unit tests first [annotation 2026-10-30: the suite collected 32 at that commit; 31 was a transcription slip -- and 20.6 s was the run's total elapsed, 5.8 s the measurement segment, per the backfill]. The gate
sequence worked exactly as registered: corpus loaded (60 van Hateren
images, sha256 checksums PINNED AT FIRST CONTACT to
results/arenas/natstat_corpus_checksums_van_hateren.json -- now the
pin for every future run); contrast calibration hit its target
(gamma 8.0, p95 |column drive| 0.5000); scramble-integrity selftest
exact (amplitude rel err 3.5e-16, decorrelated). Then G0 FAILED:
fc25's moving-edge result reproduces at median v2 DSI 0.1763 through
the NEW stimulus path, against the required 0.3216 +/- 0.02 (tiling
exact). G1 reported failed alongside (REAL-natural did not beat the
90-deg chance floor) -- consistent with the same path defect.

Scope, precise: this is an INSTRUMENT statement. The same reference
reproduced at 0.32157 through the t4t5-class3 instrument's path the
same day, so the defect is localized to natstat's new stimulus
machinery (binning/travel/windowing), not to the patch, the fc25
result, or the corpus. Nothing about natural statistics was measured;
the 2x2 never ran. Fix is cloud-side (adapter plumbing before any
verdict-relevant quantity, the registered allowance); the corpus +
checksum pin and the calibration curve are banked for the re-run.

MENU STATE after this entry: item 1 FLAT (release downgrade
triggered), item 2 readings complete, item 4 PASS, item 7 SFA KILL /
terminal PASS, item 6 BLOCKED (no spiking operating point), item 5
BLOCKED (G0 plumbing), item 3 fetches complete (recipe documented;
numeric completion = re-derive from our MaleCNS data or the
supplement page). Hypothesis closes are the cloud side's steps.

## Task 10 item 6: t4t5 class-3 BLOCKED -- no operating point exists (zero evoked spikes at every gain) -- 2026-10-29

Exit 3, instrument statement, never a fly verdict; 27/27 unit tests
first. GATE A passed locally (idealized spiking delay-line: median
DSI 1.0000, TF optimum at the interior 1 Hz point, equalized-arm
collapse 0.0000 -- the model class can express DS). GATE B passed
(patch dims 2,701/507/498/169 exact; sign audit 0 curation flips --
measured MaleCNS consensus NT agrees with the curated table for every
patch type; fc25 class-2.5 reference reproduced at 0.32157 vs 0.3216
+/- 0.02). AT-2 coverage 132/320 pairs trained, synapse mass 0.9786.

THEN THE CALIBRATION: median evoked T4/T5 rate 0.000 Hz at EVERY one
of the 18 gains spanning 1e-5 to 3000 (both polarities) -- BLOCKED:
"no stable nonzero gain on the calibration grid". MEASURED absence,
scope exact: at Kakaria/Pisokas-pinned spiking physiology with the
AC-6 per-class scales, the compiled MaleCNS optic-lobe patch produces
zero evoked spiking in the scored T4/T5 population at any global
drive scale, so the DS question cannot be posed at this fidelity. The
companion result to the CX class-3 run (there the counts spiked but
lost position; here the columnar patch never fires at all). No grid,
no rewires, no verdict; H-T4T5-CLASS3-DS disposition (BLOCKED-as-wall
vs re-registration) is the cloud side's call.

## Task 10 item 7: SFA KILLED, TERMINAL PASSED -- the program's first functional mechanism win, specificity intact -- 2026-10-29

Both mechanism arms run (3 seeds, rewired control, unpinned MaleCNS,
like-for-like with the stored uniform baseline malecns_flygi.json;
19/19 gates passed first under the flybench venv). One at a time, as
registered. JSONs gitignored (malecns_sfa.json,
malecns_terminal.json).

SFA ARM: KILL. core 0.8000 / hard 0.6276 / graded 0.6940 /
specificity +0.2684, 7/30. Bars: hard_improves TRUE (+0.0226),
activation holds, specificity holds, overall FAILS (0.6940 < 0.701)
-- and core dropped 1.0 -> 0.8. MEASURED shape: spike-frequency
adaptation buys hard-tier dynamics by breaking a core task and the
overall floor. The frozen bars refuse the trade.

TERMINAL ARM: PASS -- ALL FOUR BARS HOLD. core 1.0000 / hard 0.6418
(bar delta +0.0366) / graded 0.7622 (uniform 0.7113; floor held with
+0.051 to spare [annotation 2026-10-30: +0.051 is the delta over the uniform row's 0.7113; the margin over the registered 0.701 floor is +0.061]) / specificity +0.3135 (uniform +0.2823), 11/30 tasks
(uniform 9). Suppression also up (0.639 -> 0.701), activation up
(+0.004). MEASURED, scope held tight: weighting the compiled MaleCNS
counts by flybench's shipped per-terminal table improves the
characterization score on every frozen bar while the rewired control
still collapses (specificity GREW). This is the program's first
functional mechanism PASS on an external benchmark. It is a claim
about the terminal-weighted count matrix on FlyBench's tasks -- not
about ARC, and not about any other mechanism. Hypothesis closes
(H-FLYGI-FLYBENCH-SFA refuted, H-FLYGI-FLYBENCH-TERMINAL supported)
are the cloud side's step; a combined SFA+terminal arm is NOT run
(registered rule: combined only if both singles pass; SFA failed).

## Task 10 item 1: reservoir positive control is FLAT -- certification claim KILLED; release-prose downgrade triggered for 11-01 -- 2026-10-29

Both arms complete (75 rows each, 25 games x seeds 0-2 x 500 actions,
exit 0 both; pace matched A-RES-3 after startup). MEASURED means:
reservoir-positive-control 0.0137 (1 level), reservoir-matched-random
0.0320 (3 levels); comparators, previously measured: eff-real-signed
0.0648, eff-null-degree-preserving 0.0079.

THE FROZEN READING (clustered bootstrap, 5000 resamples, matched
pairs, full precision):
- positive-control vs eff-real-signed: -0.0511, CI [-0.1532, +0.0000]
- positive-control vs eff-null-degree-preserving: +0.0058,
  CI [+0.0000, +0.0174]
- context, vs its matched-random twin: -0.0183, CI [-0.0550, 0.0000]
Both decision CIs span zero => FLAT (KILL for the certification
claim). The dynamically-validated edge-of-chaos reservoir (rho
0.9924, memory half-life 3x the real graph's) moved official score
not at all -- and does not even separate from its rho-0.16 dumb twin.
A-RES-2's warning is the measured story: ARC level-1 completion does
not pay for cross-action neural memory under this interface.

CONSEQUENCE, frozen in the registration and now TRIGGERED: the
published class-1 ARC nulls downgrade from "the real wiring conferred
no advantage under this interface" to "under an interface in which no
tested graph -- including one tuned into the known-good long-memory
reservoir regime -- moved official score, the real wiring also did
not." This caveat must land in docs/experiment.md, docs/controls.md,
LEAGUE.md's real-vs-null/bypass prose, and the task1_arc_paper
factsheet/writeup BEFORE the 2026-11-01 release (cloud-side close +
edits per the division of labor; this entry is the measured record).
POWER FLOOR, also frozen: comparator CI half-widths are +/-0.07-0.19
at 75 rows, so FLAT means "no detected advantage at roughly the
+0.1-score resolution", and the old "cannot register an advantage
that ANY graph could confer" prose weakens to that measured form.
The seven rewire-parity instances, the retinotopy positive and the
structural separations are untouched (each carried its own measured
positive).

LEAGUE.md regenerated with both rows (league verdicts: null / null).

## Task 10 session 1: items 2 + 4 run (nulls2 readings; FB PASS), corpora + papers fetched; reservoir arm 1 in flight -- 2026-10-28

Preconditions: pull to 6e35fa6; full suite 917 passed / 15 skipped;
test_stagea_nulls2 11 passed.

ITEM 1 (reservoir control, release-gating): arm 1
(reservoir-positive-control, edge_of_chaos seed-20260922, 3 seeds x
all games x 500 actions) launched and in flight. MEASURED pace after
startup ~1.4 min/row => ~1.75 h/arm, consistent with A-RES-3's 0.148
s/action; no re-plan needed. Early seed-0 rows score 0.0 with action
entropies ~2.0-2.5 (alive, not scoring -- consistent with the dead
regime registration note).

ITEM 2 (H-STAGEA-NULL-DECOMPOSITION): READINGS COMPLETE, exit 0,
22.9 s, 600 nulls. MEASURED per family (real bandedness 0.5881,
mirror 0.01445): weight_within_pre SEPARATES (p 0.005 / 0.010);
weight_global SEPARATES (p 0.005 / 0.010); sign shuffles DO NOT
separate (p 0.438 / 0.826; null band max 0.642 exceeds real). Stage
A's ring signature lives in edge placement + magnitudes, not in the
sign pattern. Refinement only; no verdict changes.

ITEM 4 (H-FB-COLUMNAR-TOPOLOGY): PASS, exit 0, 163.4 s -- the
SECOND structural PASS. Synthetic Hulse gate passed locally (ideal at
the floor on both bars, its rewire kills both: antipodal p 0.677,
mirror p 0.294). Subcircuit 1,399 nodes / 85,353 signed edges;
column_counts exactly AC-FB1 (FC 9 / hDelta 12 / vDelta 10; PFNa 9,
PFNd 8, PFNm_a 9, PFNm_b 9, PFNv 9); coverage 1.0 / 1.0 / 0.988.
MEASURED vs 200 rewires: bar1 hDelta antipodal 0.4055, bar2 PFN L/R
mirror 0.0146, both p 0.00498 (the floor). Context (non-decisional):
vDelta antipodal 0.0004 (absent, as Hulse predicts for the
within-column type), PFL mirror 0.0217.

ITEM 5 CORPUS: van Hateren imk00001-60.iml fetched from the
pirsquared.org mirror to ~/datasets/vanhateren -- all 60 files
exactly 3,145,728 bytes.

ITEM 3 FETCHES (papers to ~/datasets/biswas_papers): (1)
biswas2024_v2.pdf = Biswas/Stanoev/Romani/Fitzgerald v2 (posted
2026-03-08, 63 pp, includes supplement) -- the MaleCNS version;
biswas_nsf_par.pdf = the 2024-11-01 v1 (47 pp) which contains NO
MaleCNS content (MaleCNS arrived in v2; provenance point). (2)
biswas2026_followup.pdf = Hulse/Aneesh/Romani 2026, "Hidden
symmetries..." (31 pp) -- contains NO MaleCNS realizations (hemibrain
only; the runbook's guess that MaleCNS realizations live here is
refuted by text search). (3) Duan/Dong/Fiete: NeurIPS 2025 poster
115017 metadata captured (title "From Synapses to Dynamics: ...",
OpenReview id zn4F6os6cq, no code link on the page); the bioRxiv PDF
is still Cloudflare-rate-limited (1015) -- retry pending. KEY READING
for the registration: biswas2024_v2 gives a DERIVATION RECIPE, not a
printed parameter table -- coarse-grain MaleCNS EPG/Delta7 counts to
wedge/glomerulus blocks (Delta7 assigned to glomerulus by maximal
cumulative output), four 5D synapse-count vectors c_EE/c_EI/c_IE/c_II
with one gamma scale per block submatrix, ring-attractor conditions
per their Table 1 (p42); the numeric MaleCNS vectors appear only in
figures (p7), there is no code/data availability statement in the
PDF, and sampled-parameter sweeps were amplitude-matched to the
MaleCNS vectors (p13). Numeric completion will need either
re-derivation from our own MaleCNS data per the recipe, or the
supplement page (fetch currently 429-limited).

Remaining this session: arm 2 + LEAGUE rows (after arm 1), FlyBench
SFA + terminal, t4t5 class-3, natstat (corpus ready).

## Task 10 OPENED: exhaustion audit recorded; user go on the full science menu -- 2026-10-23

Context: on 2026-10-15 the user asked whether the program has used
"everything possible from the fly (latent world models, ODEs, the
works)". A 9-agent audit (5 map lenses + 4 adversarial gap lenses)
answered against the record at c1505c0; the condensed, tiered record
is docs/arenas/task10_menu/exhaustion_audit.md. On 2026-10-23 the
user gave the go on ALL menu items: (1) reservoir positive control on
ARC, (2) class-3 T4/T5, (3) fitted per-type CX (Biswas/Duan-Fiete
configuration), (4) FB structural probe, (5) naturalistic-statistics
task, (6) FlyBench's terminal-aware placement + SFA mechanisms,
(7) second null family (weight/sign shuffles).

House pattern applies: due diligence (7-agent sweep, running) ->
joint frozen registrations BEFORE any instrument code -> instruments
with in-cloud validation gates -> user runs locally. None of the
items is score-adjacent; every Expected-tier prior inherits the
0-for-16 base rate (docs/arenas/SYNTHESIS.md).

NEXT: registrations from the diligence results; items whose
diligence comes back needs-fetch or blocked are recorded as such,
not silently dropped.

UPDATE same day — DILIGENCE LANDED AND THE JOINT FREEZE IS IN
(docs/arenas/task10_menu/due_diligence.md + killtest_design.md, one
commit, before any instrument code). Verdicts: 6 of 7
ready-to-register; Biswas fitted-CX is needs-fetch (paper absent
from the container, every serving host proxy-denied — MEASURED;
pre-commitments frozen blind, numeric completion after the user
fetches 3 documents, list in the design doc). Eight hypotheses
registered: H-ARC-HARNESS-SENSITIVITY (+ reservoir-positive-control
and reservoir-matched-random condition rows, regime gain0.9-dead for
the league's cross-regime rule), H-T4T5-CLASS3-DS (with the recorded
absence finding: no published spiking motion detector exists — gate
A engine-capacity + gate B continuity stand in), H-CX-BISWAS-FITTED
(partial), H-FB-COLUMNAR-TOPOLOGY (FB composition frozen from an
in-cloud ANNOTATION-ONLY download; weights table untouched, decision
statistics outcome-blind), H-T4T5-NATSTAT-DIRECTION,
H-FLYGI-FLYBENCH-SFA, H-FLYGI-FLYBENCH-TERMINAL,
H-STAGEA-NULL-DECOMPOSITION (refinement, never a reopening).
27 new assumption rows (A-RES-1..4, AT-1..2, AC-FB1..6, ANS-1..5,
AF-9..13, AC-N1..4). NEXT: instruments, in the declared order —
nulls2 module, FB probe, SFA/terminal adapters, class-3 T4/T5,
natstat harness; reservoir needs no instrument (launch of existing
machinery). Reservoir runs FIRST locally, before the 2026-11-01
release.

UPDATE same day — INSTRUMENTS LANDING. (1) nulls2 built and pushed
(24e7c71): weight/sign shuffle generators + invariants, decomposition
runner on Stage-A machinery verbatim, 9 tests with both dissociation-
gate directions MEASURED through the real rewire machinery
(magnitude-tuned synthetic: real bandedness 0.639 vs null max 0.327,
p at the floor; topology-banded jittered ring: weight family inert,
rewire separates); controls.md rows closed to implemented+validated.
(2) FB probe built (fb_topology_killtest.py, 14 tests): mirror_peak
reused by identity from Stage A (asserted); synthetic Hulse-motif
gate MEASURED both directions at 200 nulls in-cloud (ideal p 0.004975
= floor on both bars; rewired ideal 0.677/0.294, both bars dead);
main re-runs the gate at 200 nulls before any data contact; BLOCKED
in-cloud as designed. Operationalizations recorded in the module
(antipode sector = circular distance in [160,180]; Bar-2 on the
Stage-A 16-bin offset frame via a circulant whose offset_profile is
exactly the histogram — Stage-A semantics reused, not retuned).
(3) natstat harness built (natstat_killtest.py, 31 tests): frozen
van Hateren list imk00001..imk00060 sha256-pinned; scramble/
translation/AD-8 gates all asserted in-cloud; exact binomial sign
test pinned in-module (no scipy drift); B1/B2 verdict logic
unit-tested on all paths; BLOCKED in-cloud naming the four missing
local pieces. Joint suite: 79 passed. (4) The first build pass lost
the class-3-T4/T5 and FlyBench-mechanisms agents to a usage-credit
outage mid-flight; their partial artifacts were moved OUT of the tree
(scratchpad/partials) and the two builds are re-running clean from
the frozen registrations. Runbook sections 4-5 appended.

UPDATE same day — INSTRUMENT STAGE COMPLETE. The rebuilt pair landed
and was verified (orchestrator re-ran every suite): (5) t4t5 class-3
instrument (t4t5_class3_killtest.py, 27 tests, ~100 s): GATE A
MEASURED PASSING IN-CLOUD — the idealized spiking delay-line
correlator reaches median DSI 1.0000 with the TF optimum at 1.0 Hz
and collapses to 0.0000 with equalized arms (robust at three more
seeds) — so the spiking model class CAN express the delay code and a
local KILL would be about the counts; unitary-PSC equivalence
asserted numerically (rel 1e-6) against the validated CX template
incl. a 133 ms kernel; engine = TemplateLIF + per-type taus +
two-state exponential synapses + signed drive. (6) FlyBench
mechanisms (spiking.py default-off SFA + two adapter classes +
flybench_mechanisms_verdict.py, 19 tests, ~150 s): SFA off-switch
BIT-IDENTICAL to the pre-extension engine (asserted vs a frozen copy
of the 08fac61 step); Benda-Herz closed form within tolerance
(unadapted 200.0 vs analytic 191.7 Hz; adapted 81.0 vs fixed point
81.01; ISI 5.5 -> 12.0 ms); toy-suite equivalence vs flybench's own
simulators both mechanisms (SFA deltas same direction as theirs;
terminal within declared engine differences); shipped terminal table
asserted to sum to exactly 3,782,429. Build-time operationalizations
recorded as a dated pre-data-contact note in killtest_design.md
(T4/T5 R1-R6 incl. the R2 double-filtering risk, arm-symmetric; the
SFA state-dependent forced-pulse compensation, measured necessary;
the natstat anchor marked SOURCED non-decisional). Full joint suite
in-cloud: 46 + 32 natstat/regression green; every data-gated main
BLOCKS exit 3. Runbook sections 6-7 + the suggested overall order
appended. ALL SEVEN MENU ITEMS DELIVERED (six runnable now, Biswas
awaiting the user fetch). The ball is with the local host; the
reservoir control runs FIRST, before the 2026-11-01 release.

## Task 9 FULLY CLOSED: both reopening hypotheses refuted in the registry; synthesis updated -- 2026-10-11

Cloud-side close of the two local KILLs (run record: the entry below,
commit eeb75b5). Changes, all propagated the same day:

- EXPERIMENTS.yaml: H-CX-SEEDING-PROTOCOL -> refuted (regime-bound,
  not protocol-bound; the frozen decision rule licenses NO class-1
  Stage-B re-registration). H-CX-CLASS3-COMPASS -> refuted, with the
  verdict-machine gate pass recorded first (the engine reproduces
  the published Pisokas fly bump where the verdict was produced, so
  the KILL is about the counts, not the engine). Both run bullets
  carry tiers: MEASURED numbers verbatim from the run record;
  INFERRED readings (landscape-decides; point-attractor-not-ring)
  with their bridges stated; the class-3 close scoped to the
  declared AC-6 mapping and the AC-8 standalone circuit.
- SYNTHESIS.md: second Task-9 addendum. The headline: the
  structure/function split is now measured at TWO fidelity classes
  of the same circuit, with DIFFERENT failure modes (class 1: the
  rate bump dies; class 3: the spiking bump persists at retention
  0.94-0.997 but slides to a common region, ~177-221 deg, errors
  155-177 deg; the point-attractor reading is INFERRED).
  Record map extended with the four Task-9 hypotheses. Noted
  explicitly: the null-bar record does NOT gain instances from these
  runs -- in both, the real arm failed before any rewire ran.
- ASSUMPTIONS.md: AC-6 and AC-8 annotated EXERCISED (mapping usable
  -- stable everywhere; scope carried into the close sentences).
  AC-7 stands CONFIRMED.
- HANDOFF row 9: REOPENED and RE-CLOSED; Task 9 is closed at every
  registered level.

No further Task-9 work is queued. The live reopening-shaped question
that remains in the record is SYNTHESIS section 7 item 1 (class-3 on
a killed circuit, T4/T5 named), which now carries the CX precedent
that fidelity CHANGES the failure mode; it runs only on an explicit
go.

## Task 9 reopening: BOTH kill tests run -- probe KILL, class-3 KILL (gate passed; the counts hold activity but not position) -- 2026-10-11

The user ran both reopening instruments in the registered order
(probe first). 13/13 and 22/22 unit tests; no instrument changes
needed; zero instability in every arm of both runs. JSONs gitignored
at results/arenas/cx_{seeding,class3}_killtest.json.

PROBE (H-CX-SEEDING-PROTOCOL): KILL, exit 1, 422.8 s. All 8 real
cells fail the cell rule; rewires therefore never ran (frozen
evaluation order). MEASURED pattern across cells: at gain 1.5 every
protocol (P1-P4, including the 100-step write, the scale-3 write and
direct state injection) lands at the same held-out errors
(~121/149/59 deg) with circvar ~0.66-0.68 -- the landscape, not the
write, decides where mass sits; at gain 2.0 all protocols reproduce
the known fixed-point mode (112.5 -> circvar 0.000 err 22.5; others
circvar ~0.83). Stage B's failure was NOT protocol-bound: no
re-registration of class-1 Stage B is licensed.

CLASS-3 (H-CX-CLASS3-COMPASS): KILL, exit 1, 990.4 s. The
validation gate PASSED LOCALLY first -- the Pisokas 60-neuron
idealized fly circuit reproduces in this engine on this machine
(pass=True, mean width 99.0 deg, matching the in-cloud measurement;
per-seed retentions 0.97-0.99, errors 15-41 deg) -- so the verdict
is valid, not blocked. On the real MaleCNS counts, all 6 declared
grid points fail: G1 best 2 of 8 angles (bar: >= 6), G2 steering
never opposite-signed (best L -8.0/R -8.3 deg/s same-signed at 0.5x;
near-zero at 1.0x/2.0x). Rewires never ran (no real-passing points).
MEASURED failure mode, and it is NEW: retention at the grid points
is HIGH (0.94-0.997 -- the spiking bump persists through darkness)
but position-unfaithful -- final angles cluster at ~177-221 deg
regardless of the write angle (errors 155-177 deg). At class-1 rate
dynamics the bump died; at class-3 spiking fidelity it survives but
slides to a common attractor basin. Activity persistence without a
position continuum.

THE SCOPED STATEMENT this pair buys (the registration's own words):
at the model class where idealized fly topology is PUBLISHED to work
-- and reproduces in our engine -- the compiled MaleCNS synapse
counts do not carry the compass: no continuum (G1), no opposite
steering (G2), at any declared scale. Combined with Stage A (the
topology IS in the counts, p 0.005 against 200 rewires) the
structure/function split is now measured at two fidelity classes:
the wiring carries ring-compass STRUCTURE its nulls cannot fake, and
does not COMPUTE heading with it at either tested physiology.
Hypothesis closes (both) are the cloud side's step per the
registration.

## Task 9 reopening: BOTH instruments BUILT; class-3 engine REPRODUCES the published fly bump (gate PASS, estimator amendment recorded) -- 2026-10-11

Both registered instruments now exist, tested, with the class-3
validation gate green in-cloud. The user runs the PROBE FIRST
(runbook updated with both commands).

- CLASS-3 ENGINE VALIDATED (scripts/arenas/cx_class3_killtest.py +
  fixture tests/data/pisokas_fly_connectivity.npz + 22 tests).
  MEASURED, in-cloud, published Pisokas 60-neuron fly circuit,
  declared seeds 7-11: retention 0.968-0.987, PVA err 14.6-41.4 deg,
  circvar 0.382-0.549, bump width per-seed {90, 135, 90, 90, 90},
  MEAN 99.0 deg vs their Table-1 88.3 (one estimator quantum = 45
  deg); stable at 3 s, and in earlier diagnostics at 10 s. To our
  knowledge from the registered sweep this is the first
  spiking-tier reproduction of their fly bump in this repository's
  stack; it validates the INSTRUMENT only -- nothing about MaleCNS
  is claimed.
- GATE AMENDMENT (dated, PRE-DATA-CONTACT; full record in
  killtest_design_reopening.md): the first width operationalization
  (per-cell E-PG fraction above half max) MEASURED 160 deg on a bump
  that is otherwise healthy, failing the 60-120 band. Reading their
  published code ESTABLISHED the Table-1 width is a different
  object: measureBump1 on the raster's first 8 columns = the LEFT-
  hemisphere P-ENs (matrix layout [P-EN 16, P-EG 18, E-PG 18,
  Delta7 8]), threshold (max-min)/2, width (k-1)/8 x 360 deg --
  45-deg-QUANTIZED -- averaged over trials, on a 100 ms window; the
  von Mises drive is sampled at the 8 EB column angles and applied
  identically to both 9-cell E-PG hemisphere blocks (9th cell
  duplicates column 1). The gate now uses their estimator, their
  window, their column geometry, and a trial MEAN over declared
  seeds; the 60-120 band and every other bar are unchanged; no
  MaleCNS-facing bar (G1/G2/null) uses the width estimator. The
  crude-estimator 160-deg reading is recorded as an instrument-
  fidelity error, not an engine failure.
- PROBE BUILT (scripts/arenas/cx_seeding_killtest.py + 13 tests):
  imports the Stage-B module and calls its machinery directly, so
  loading/drive/read are verbatim by construction. Frozen 8-cell
  grid (2 points x 4 protocols), position-faithful cell rule,
  rewires only at real-passing cells, tracking context at decisive
  cells. Stub-network end-to-end: perfect-memory stub passes the
  cell rule under all 4 protocols, decaying stub fails. BLOCKED
  in-cloud as designed (exit 3, runtime absent).
- Registry updated (both hypotheses carry the instrument-built
  evidence; class-3 carries the amendment). Suites: 22 + 13 new
  tests pass; Stage-A/B suites still pass (15).

NEXT: user runs cx_seeding_killtest.py locally FIRST, reports JSON;
then cx_class3_killtest.py (either probe outcome). Cloud side closes
each hypothesis from the reports.

## Task 9 reopening: BOTH kill tests jointly REGISTERED (probe + class-3), literature pinned -- 2026-10-11

The literature sweep landed (3 agents, zero errors; sources
code-verified where stated) and both registrations froze in one
commit (docs/arenas/task9_cx_latent/killtest_design_reopening.md):

- H-CX-SEEDING-PROTOCOL (class-1 probe): frozen 4-protocol x 2-point
  set (P1 cx_ring wedge-write as the measured-dead reproduction
  control; P2 sustained write; P3 scale-3 write; P4 direct state
  injection), position-faithful cell pass rule, rewire wiring bar at
  real-passing cells, all cells reported. Tracking at passing cells
  is context only -- the heading-latent verdict would belong to a
  re-registered Stage B.
- H-CX-CLASS3-COMPASS: Kakaria/Pisokas template-LIF physiology,
  code-verified values (the sweep CAUGHT a paper-vs-code parameter
  discrepancy -- paper Cm 2 nF / Rm 10 MOhm vs code 20 nF / 1 MOhm,
  same tau_m, 10x current gain; we pin the CODE set with the code's
  optimized fly class weights, extracted from their published
  MATLAB: 99.968 / 47.917 / 6.072 / -35.677 / -19.336). Weight
  mapping AC-6 (class-mean-matched scales, heterogeneity preserved,
  nothing fitted); declared 6-point grid; G1 8-angle continuum +
  persistence, G2 opposite steering; rewires must fail G1 at every
  real-passing point. IN-CLOUD VALIDATION GATE: the engine must
  reproduce the published Pisokas 60-neuron fly bump before any data
  contact.
- PRECEDENT, from the sweep (absence finding, stated): connectome-
  weighted fly CX bumps exist only at rate tier with FITTED per-type
  parameters (Biswas 2024 bioRxiv, incl. exact MaleCNS realizations;
  Duan, Dong & Fiete NeurIPS 2025, tuning shown necessary on
  hemibrain); NO spiking/conductance connectome-weighted bump is
  published anywhere. H-CX-CLASS3-COMPASS targets exactly that gap
  with pinned (unfitted) parameters.
- AC-6..AC-8 registered. Neither hypothesis is score-adjacent.

NEXT: build both instruments (probe reuses the Stage-B machinery;
class-3 engine must pass the Pisokas validation gate in-cloud), then
the user runs the probe first.

## Task 9 reopening: due diligence recorded; joint registration pending the literature sweep -- 2026-10-11

User go on BOTH reopening paths. Due diligence first
(docs/arenas/task9_cx_latent/reopening_delta.md), with two new
findings: (1) the verdict program's cx_ring grid survives as TRACKED
provenance (git 09a998a) and is stronger than the Stage-B close knew
-- wedge-write C1 persistence fails at EVERY grid point including
gain 2.0 (best retention 0.0177), while C2 opposite steering PASSES
at 1.5/0.3 and 2.0/0.3; the ONLY persistence measurement in the
record is the Sept-25 arc-seeded run. (2) The arc protocol is
UNREPRODUCIBLE from the committed record -- its scripts never existed
in git; only registry prose and local JSONs survive. The probe
therefore freezes a DECLARED 4-protocol x 2-operating-point set with
pre-stated pass rules instead of claiming to replicate a lost
protocol. The class-3 registration pins its parameter table from a
running literature sweep (Pisokas 2020 / Kakaria 2017 / other CX
models; whether any CONNECTOME-WEIGHTED fly CX has ever sustained a
bump is the precedent question). Both registrations freeze in ONE
commit when the sweep lands; no instrument code before that commit.

## Task 9 CLOSED: structure yes, computation untestable at classes 1-2; AC-2 invalidated -- 2026-10-11

Cloud-side close of the Stage-B BLOCKED (local record below at commit
dcedb9f; the local session's reconciliation against cx_ring.json is
confirmed and adopted):

- EXPERIMENTS.yaml: H-CX-HEADING-LATENT -> "null" with two bullets --
  the BLOCKED record (precheck 0.0000/0.661 reproducing the grid's
  0.0003/0.713 almost exactly; instrument not suspected) and the
  close: UNVALIDATABLE at class-1 under the registered protocol,
  untested rather than refuted. The reconciled record shows the
  premise's two required properties measured only in DISJOINT
  regime x protocol combinations: persistence at gain 2.0 wedge-write
  (fixed-point), opposite-signed steering at gain 1.5 VISUAL-ARC
  seeding, no persistence at gain 1.5 wedge-write (two independent
  runs). Class-2 delocalized everywhere.
- DUE-DILIGENCE MISS, OWNED: the Stage-B registration read the regime
  sweep's persistence (circvar 0.52 at 1.5) as protocol-portable.
  cx_ring.py's committed header flags that anchor as "agreement
  expected in sign pattern, not numerically", and the grid's
  contradicting wedge-write rows were in the durable (local-only)
  record. The gate the registration DID carry (AC-2 precheck ->
  BLOCKED) is what contained the cost: 14.4 s, no arm evaluated, no
  verdict-relevant quantity computed.
- ASSUMPTIONS: AC-2 -> INVALIDATED with the measured numbers and the
  protocol-portability flaw named. killtest_design.md gains a dated
  Stage-B close note (frozen text untouched). HANDOFF row 9 ->
  CLOSED. SYNTHESIS gains a dated Task-9 addendum: Stage A is a
  second anatomy-tier positive (the permutation IS detectably
  special, structurally); what still has no measured win is the
  permutation DOING anything at simulable fidelity -- the
  fidelity-ceiling explanation sharpens, and the CX moves ahead of
  T4/T5 as the class-3 candidate (structural PASS + persistence
  separation + the concrete visual-arc-vs-wedge-write protocol
  question).

REOPENING PATHS, each needing an explicit user go and its own
registration: (a) class-3 CX fidelity; (b) a cheap registered
visual-arc-seeding reconciliation at gain 1.5 with pre-stated pass
rules (settles whether seeding, not regime, decides persistence).
Neither runs on my initiative -- an unregistered operating-point
search is tuning-to-pass.

## Task 9 Stage B: BLOCKED at the AC-2 precheck -- and the durable record says the gate was never passable -- 2026-10-10

The user ran the Stage-B heading-latent kill test (7/7 unit tests
first; full graph loaded, 166,700 nodes in 1.4 s; 14.4 s wall, peak
RSS 0.50 GB). Exit 3, BLOCKED, NOT a verdict; no JSON written, no
calibrated-rates or per-arm lines reached. The printed precheck:

  precheck (cal 22.5): retention 0.0000, circvar 0.661, angle 352.1
  BLOCKED: calibration-angle persistence precheck failed (AC-2)

RECONCILED against the durable record before reporting, per the
operating directive: results/benchmarks/cx_ring.json's class-1 grid
already contains the same regime (gain 1.5, leak 0.3, angle 22.5):
retention 0.0003, final_circvar 0.713, final angle 349.6,
angle_pass FALSE -- and every other gain-1.5 leak row fails
persistence the same way. The Stage-B instrument therefore
REPRODUCED the prior measurement almost exactly (0.0000/0.661/352.1
vs 0.0003/0.713/349.6; small deltas consistent with the protocols'
window differences). MEASURED tier, both runs agree: at gain 1.5 /
leak 0.3 the compiled CX does not retain a seeded bump through 2 s of
darkness. What failed to hold is the AC-2 gate's premise that the
measured steering regime also persists headings -- steering was
measured there; persistence never was, and the grid says it fails
there. The instrument is not suspected: it refused, before burning
the budget, to evaluate a premise in a regime whose required
property does not hold, which is exactly its declared BLOCKED
contract.

Disposition is the cloud side's call per the registration (any
amendment needs a recorded finding; this entry is that finding's
local half). No instrument changes made locally; nothing in the
frozen bars touched.

## Task 9 Stage A CLOSED: SUPPORTED -- the arena series' FIRST PASS; Stage-B instrument built -- 2026-10-10

Cloud-side close of the user's Stage-A run (record below, commit
2530194; instrument ran unmodified):

- EXPERIMENTS.yaml: H-CX-RING-TOPOLOGY open -> SUPPORTED, with the
  MEASURED bullet: bandedness 0.5881 vs null max 0.3376 and PEN_a
  mirror-peak 0.01445 vs null max 0.00792, each p 0.00498 (the floor
  at 200 nulls); coverage 1.0 everywhere; 30.6 s. The first measured
  property of the real fly wiring that its own degree-preserving null
  cannot reproduce, and the program's first PASS. SCOPE: structural
  only. Context behaved exactly as the pre-data amendment predicted
  (argmax degenerate on the real sparse profiles; PEN_b weaker at
  0.00706; blind spectral ordering 46.6 deg off the anatomical one --
  AC-1's interleaving stays OPEN, annotated; no bar depended on it).
- ASSUMPTIONS: AC-1 annotated with the measured coverage and spectral
  residual; AC-4 -> EXERCISED, USABLE (the gate fired twice before
  data contact, then the real run separated at the p-floor).
- STAGE-B INSTRUMENT BUILT against its registration (frozen in the
  same commit as Stage A's, untouched since the PASS):
  scripts/arenas/cx_heading_killtest.py -- cx_ring loading/drive/read/
  rotation conventions verbatim at gain 1.5 / leak 0.3; AC-2
  persistence precheck on the calibration angle; ONE labeled
  instrument-level guard added at build time (same-signed or
  sub-threshold calibrated rates BLOCK: the command integral is
  undefined without a signed rate basis); CX-block-only rewires
  (AC-5) via cx_block_rewire, unit-tested to touch nothing outside
  the 148x148 block and to preserve in/out degrees inside it; the 3
  preregistered sequences (seed 20261010) and the command-integral
  decode, with the registration's singular "rotation-rate
  calibration" operationalized as the REAL arm's rates defining every
  arm's ground truth (documented in the docstring: an arm that cannot
  steer accumulates error against the commanded trajectory). 7/7
  tests in-cloud; exits 3 BLOCKED here as designed. Runbook Stage-B
  section added.

NEXT: user runs Stage B locally (~1 h); cloud closes
H-CX-HEADING-LATENT either way.

## TASK 9 STAGE A: PASS -- the CX ring topology survives its own rewire null (first PASS in the arena series) -- 2026-10-10

The user ran the Stage-A structural kill test (seconds of real
metrics, 200 degree-preserving rewires in 21.8 s; 30.6 s total;
results/arenas/cx_topology_killtest.json, gitignored). Preconditions:
8/8 unit tests; no instrument changes needed locally.

VALID, not blocked: subcircuit composition exact (148 = 46 EPG +
20 PEN_a + 22 PEN_b + 42 Delta7 + 18 PEG); wedge coverage 1.0 for
EPG, 1.0 for PEN_a, 1.0 for PEN_b; groups PEN_a 10L/10R,
PEN_b 11L/11R; all-PEN two-hop weight nonzero.

MEASURED, against 200 degree-preserving rewires of the full
subcircuit (seeds 4242+0..199), empirical one-sided p = (1+k)/201:
- BANDEDNESS: real 0.5881 vs null MAX 0.3376 -- real exceeds every
  null; p 0.00498 (the floor). Bar 1 HOLDS.
- SHIFTER (mirror-peak statistic, amended 2026-10-10 BEFORE any data
  contact after the synthetic-ring gate measured the frozen argmax
  statistic anti-informative -- the amendment, its sequence and its
  synthetic validation are in killtest_design.md): PEN_a S 0.01445
  vs null MAX 0.00792 -- exceeds every null; p 0.00498. Bar 2 HOLDS.
- Context, non-decisional: PEN_b mirror-peak 0.00706 (below the
  PEN_a signal -- consistent with PEN_b's weaker shifter role);
  argmax offsets all 0/invalid (exactly the degeneracy the amendment
  documented); blind spectral ordering residual 46.6 deg vs the
  anatomical wedge order.

VERDICT: PASS, exit 0 -- the first registered PASS in this program's
arena series, and the first structural property of the real wiring
that its own degree-preserving null cannot reproduce. Scope words,
carefully: this is a STRUCTURAL result about the EPG<->PEN coupling
matrix under the anatomical wedge ordering. It licenses building
Stage B (H-CX-HEADING-LATENT, already frozen in the same
registration commit) and claims nothing yet about dynamics or
function -- Stage B is where the wiring either computes a heading
latent or does not. Stage-B instrument build is the cloud side's
step per the registration.

## Task 9 Stage A: instrument BUILT; shifter statistic amended PRE-DATA-CONTACT by its own validation gate -- 2026-10-10

scripts/arenas/cx_topology_killtest.py, with the whole decision
pipeline a pure function so the AC-4 synthetic gate could validate it
end-to-end in-cloud -- including through the REAL
degree_preserving_rewire machinery -- before any data contact. The
gate earned its keep immediately, twice:

- MEASURED: the frozen shifter statistic |argmax_L - argmax_R| is
  anti-informative -- on a perfect synthetic +/-1 compass, real S 2.0
  vs rewired-null argmax pairs up to 14.0 (p 0.459): it rewards
  randomness. A first replacement (mass-weighted mean-offset
  separation) was also measured weak (null max 5.4, p 0.230).
- ADOPTED, recorded as a dated amendment in killtest_design.md and
  the registry (both still pre-data-contact): the MIRROR-PEAK
  statistic -- normalized positive offset profiles q_L, q_R; S =
  max_d max(q_L(d) q_R(-d), q_L(-d) q_R(d)), d in 1..7;
  chirality-free, nonzero only for opposite-offset concentration.
  MEASURED on the gate: real 1.0000 vs null max 0.107 (median 0.025),
  p 0.0099 at 100 nulls. Argmax and mean offsets stay as reported
  context.
- Also caught by the gate's first run: a test-fixture bug (dense
  noise made the synthetic graph complete -> zero legal
  degree-preserving swaps); noise now jitters existing edges only.
- Tests: 8/8 in-cloud (wedge-parser AC-1 mapping, metric mechanics,
  mirror-peak semantics, full-pipeline PASS on the synthetic ring +
  KILL on its rewire through the frozen bars, BLOCKED coverage and
  degeneracy paths, frozen constants). The script exits 3 BLOCKED
  in-cloud (runtime absent), as designed.
- Runbook: docs/arenas/task9_cx_latent/runbook.md. Stage A costs the
  user seconds-to-minutes locally; no downloads, no new packages.

NEXT: user runs Stage A and reports the JSON; on PASS the Stage-B
(H-CX-HEADING-LATENT) instrument is built against its already-frozen
registration; on KILL, Task 9 closes with no dynamics built.

## Task 9 (off-survey): CX latent-state kill tests REGISTERED, both stages jointly frozen -- 2026-10-10

User asked whether the fly connectome could be shown to carry a latent
representation / world model of the physical environment, and said go.
Due diligence first (docs/arenas/task9_cx_latent/due_diligence_delta
.md): the question is PARTIALLY measured and the record is the
program's richest -- the CX owns the one anatomy-specific dynamical
separation ever measured here (gain-2.0 persistence: real mass 0.27
for 120+ darkness steps vs null dead by t=40), steering works at
whole-network gain 1.5 (opposite signs, circvar 0.52) but cannot be
transplanted (H-CX-CALIBRATION refuted), position storage FAILED at
gain 2.0 (two fixed points, H-CX-SCRATCHPAD) and was NEVER measured at
1.5, and class-2 LIF delocalized at all 155 configs (fc2_eb_ring).
Scope fixed at registration: the testable claim is a HEADING latent
(AC-3), never "a world model of the physical environment."

Both stages frozen in ONE commit (so neither can be tuned on the
other; docs/arenas/task9_cx_latent/killtest_design.md):
- H-CX-RING-TOPOLOGY (Stage A, structural, instrument builds now):
  ring bandedness + opposite-signed left/right PEN_a shifter offsets
  under the cx_ring verbatim wedge mapping (AC-1), vs 200
  degree-preserving rewires, empirical p < 0.05 both bars. The
  program's FIRST registration whose priors favor PASS (the measured
  persistence separation; Hulse 2021 ESTABLISHED structure).
- H-CX-HEADING-LATENT (Stage B, dynamical, instrument ONLY after a
  Stage-A PASS): continuum across held-out angles + tracking of
  integrated PEN commands at the measured gain-1.5/leak-0.3 regime,
  real vs CX-block rewires x3 (AC-5), calibration-angle persistence
  precheck as the AC-2 BLOCKED gate. Engineered 2-variable integrator
  = ceiling context, not a bar.

Neither is score-adjacent (the 0-for-16 counter does not apply and is
not incremented). Assumption rows AC-1..AC-5 registered. HANDOFF row
9 added. NEXT: build the Stage-A instrument + synthetic-ring tests
(in-cloud), runbook; user runs Stage A locally (seconds-to-minutes);
on PASS, Stage-B instrument builds against the frozen design.

## Pre-release audit COMPLETE: all 68 verified findings applied -- 2026-10-08

Part 2 (this checkpoint) closes the audit: docs/experiment.md,
controls.md, modeling_assumptions.md and data_provenance.md brought
from their 2026-09-21-era blanket claims to the measured current state
(nine scored submissions named with the construction-crash root cause;
the two bounded fly-positives stated with their encoder/anatomy
attribution; the real remaining gaps listed -- weight/sign shuffles,
>=10 seeded nulls, reservoir ARC runs; the completed acquisition
recorded from the tracked manifest with its expected_sha256-null
caveat). The docs/social kit is posting-safe: social_announcement.md
carries a SUPERSEDED banner (its 3,052 / 0.01 / 3050-3212 figures were
never in the durable record and are flagged non-reusable; the
unanchorable "163 teams" row was dropped rather than re-written);
FACTS.md's leaderboard section rebuilt to the nine-submission record
with a dynamics-off note and a dated re-verification line (other
sections still carry their 09-22 verification and say so); all drafts
recast to past tense scoped to the controlled runs; longform's
unanchored 389,471 deleted (390,272 anchors); the
no-other-study-ran-controls title option replaced with a self-scoped
one; README caveat guards {{BEST_SCORE}} insertion.

AUDIT TOTALS: 86 agents (8 sweep groups, per-finding adversarial
verification), 68 confirmed / 10 rejected as dated-record false
positives; 7 blockers among the confirmed, all fixed; plus the
fresh-clone test fix (6 runtime-data tests skip-guarded). One finding
is a USER step on the release checklist: regenerate LEAGUE.md on the
machine with the local result bundles (the 10-02 snapshot predates
five closed hypotheses). Commits: 8958404 (test guards), 8c1be1c
(part 1), this one (part 2). Suites green in-cloud after every batch.

## Pre-release audit IN PROGRESS: 68 verified findings, part 1 of fixes checkpointed -- 2026-10-08

An 86-agent adversarially-verified audit swept every shipping document
(8 sweep groups -> per-finding skeptic verification; 68 confirmed, 10
rejected as dated-record false positives). Also fixed first: six tests
requiring gitignored runtime data failed on fresh clones -- skip-guarded
(commit 8958404); full suite 756 passed / 23 skipped / 0 failed
in-cloud. This checkpoint carries the completed fix groups (blockers
first: linkedin_post 0-for-12 -> 0-for-16; HANDOFF/PLAN "MIT stays" ->
MIT-0 per AP-4's reconciled reading; kaggle_submission.md preflight
edge-count pinned per lineage, 24,994,595 for the deployed v10/v12,
and the adapter-contract section now names the deployed dynamics-off
mode; README landing section carried through the arena-program close
with a SYNTHESIS link; AGENTS.md/PLAN base-rate rules now point at the
living counter; SYNTHESIS seven-instances-six-registrations correction,
dead task2_dsec/ path, and IJCNN no-go status; executed-KILL banners on
all five task runbooks; AP-7 reworded off its unfalsifiable score
prediction; AV-1 annotated; task4 registration's seeds-line
discrepancy reconciled in a dated post-verdict note; due-diligence
absolute paths made repo-relative; three instrument docstrings label
their operationalizations). Remaining in flight: docs/experiment.md /
controls.md / modeling_assumptions.md / data_provenance.md and the
docs/social kit; the closeout entry lands with that final group. The
LEAGUE.md regeneration (needs local result bundles) is added to the
release checklist as a user step.

## Task 8: IJCNN 2027 competition proposal -- analyzed, recommendation NO-GO -- 2026-10-07

User asked for the go/no-go. The call was re-verified today (SOURCED:
4-page PDF due 2026-11-30; notification 12-15; launch 2027-01-01;
entries close 02-28; competition papers 04-01; conference June 14-18
2027, Cape Town; organizers may not compete; regular papers due
2027-01-31). Full analysis:
docs/arenas/task8_venues/ijcnn2027_go_no_go.md.

RECOMMENDATION: NO-GO on proposing a competition this cycle. The one
honest candidate ("Beat the Null" on the public MIT-0 harnesses) fits
the science, but an accepted proposal is a solo Jan-Jun 2027
operating commitment (hosting multi-GB arrays, live support, paper
shepherding, Cape Town presence) colliding with the Task 1 calendar,
with real under-participation risk, and the public release + a paper
buys most of the value for none of the tail. The better IJCNN
vehicle is the REGULAR PAPER (6 IEEE pages, due 2027-01-31 -- after
the Dec 4 ARC results; the synthesis is already paper-shaped); that
decision can wait until after Dec 4 at no cost. Reconsider the
competition format for IJCNN 2028 / Telluride 2027 / CVPR 2027
windows if the release brings co-organizers. A minimum GO path is
recorded in the doc in case the user overrides.

## Program synthesis written: docs/arenas/SYNTHESIS.md -- 2026-10-07

User chose option 1 after the Task 6 close. The completed sweep now
has a single tiered synthesis document, every number traced to
EXPERIMENTS.yaml / WORKLOG / the factsheet (no new measurement):

- The central MEASURED result as a seven-row table: every registered
  degree-preserving-rewire comparison since 2026-09-29 (MB
  association, ARC motion, DSEC, DVS, Brain-Score V1, gas drift) with
  the real-vs-rewire numbers and the per-test context arms.
- The measured positives collected in one place: the eye-map anatomy
  separation (2.59x vs 11.59x), dynamics-over-input (0.069 vs 0.033),
  the working DAN-gated credit mechanism (0.600 vs shuffled 0.400,
  p=0.019), twin-below-real tau structure, the flybench uniform row,
  and the far-above-chance codes everywhere.
- The INFERRED synthesis with its bridge stated: benchmark metrics
  reward the population transformation, which lives in degree
  sequences + weight distributions + cell-type parameters -- all
  rewire-invariant; the surviving wins are an index, a mechanism, a
  parameter set and a transformation, never the permutation. Claim
  boundaries carried: model-class-at-fidelity (not the fly); the
  literature SPLIT (PN->KC null is Caron/LK's own prediction; T4/T5
  null is NOT Maisak's -- the recorded falsifier is a class-3
  reversal there); the measured ~4-point encoder-map noise; the
  alpha~0 AE-3 caveat.
- Open alternative explanations (fidelity ceiling / readout mismatch
  / task statistics), with the MB association native-readout evidence
  already bearing on the second.
- The method record (0 for 16 score-adjacent; the older broader
  counter disambiguated; five builds prevented; four pre-data-contact
  instrument catches; two pre-verdict API fixes) and the ordered list
  of measurements that would move the synthesis (class-3 on T4/T5
  first).
- Record map table: all eight hypothesis IDs -> verdict -> location.

HANDOFF conventions now point at the synthesis as the required read
before citing the program's arc. Dates cross-checked against the
registry (adapter supported 2026-10-01 per its updated field).

## Task 6 CLOSED with verdict; DUAL CLOSE executed (Task 4 MB limb ends); base rate 0 for 16 -- 2026-10-07

Cloud-side close of the KILL recorded below, per the runbook's
division of labor:

- EXPERIMENTS.yaml: H-ALMB-GASDRIFT open -> REFUTED, with the
  MEASURED evidence bullet (all numbers, the alpha~0 calibration
  fact, zero exceptions, 76 min at --workers 8). YAML re-validated.
- THE PRE-STATED DUAL CLOSE EXECUTED: the Task 4 Keyword-FSCIL/MB
  limb is CLOSED AS NOT PURSUED, exactly as H-ALMB-GASDRIFT's
  registration bound it (inferred bridge: same AL->KC machinery,
  native modality, smaller encoder invention -- the audio hypothesis
  stays unmeasured). Task 4 is now fully closed. HANDOFF rows 4 and 6
  updated.
- SCOPE CORRECTION, recorded in the close (the dated run entry below
  stands as written, annotated here): the run entry's "scrambled-
  glomeruli control: real WINS" over-scopes. Both encoder maps are
  seeded arbitrary permutations (the design's own SCRAM framing), so
  the +4.4-point real-vs-scram gap is MEASURED encoder-invention
  variance, not a real-wiring-beats-scrambled finding -- no real
  feature->glomerulus correspondence exists to scramble. What it does
  establish: the circuit's output depends materially on the invented
  assignment, and single-map numbers carry ~4 points of map noise
  (which also bounds how hard any one rewire gap, +0.8 to +6.0, can
  be read). The decisive real-vs-rewire comparison was map-matched;
  the KILL is unaffected. AE-1 annotated accordingly; AE-3 -> NOT
  SUPPORTED as tested (with the alpha~0 caveat: the gain-control
  bridge was tested with the knob near off); AE-4 -> exercised,
  usable.
- Base rate 0 for 15 -> 0 for 16 (the sixteenth is H-ALMB-GASDRIFT,
  as its registration pre-stated) propagated to HANDOFF conventions,
  the task1 factsheet row, and the writeup closing sentence (body
  re-counted: 1,448 words, unchanged).

PROGRAM STATE AFTER THIS CLOSE: Tasks 1-6 are done (1 awaiting the
user's calendar steps; 2, 3-calibrated, 4-both-limbs, 5, 6 closed
with verdicts). The runnable arena sweep is complete: six consecutive
rewire-over-real across visual AND olfactory circuits, with two
measured positives along the way (Task 5: dynamics beat their own
input; Task 3: the uniform adapter row). What remains is
calendar-gated: Task 7 (MLPerf Tiny, ~early 2027, working-group
membership) and Task 8 (community venues; nearest date IJCNN 2027
competition proposals due 2026-11-30), plus the user's Task 1 dates
(release ~Nov 1, Kaggle submit before Nov 8 23:59 UTC).

## Task 6: gas-drift MB kill test RUN -- verdict KILL (real beats scrambled glomeruli, loses to every rewire and to raw features) -- 2026-10-06

The user ran the one registered command (UCI 224 corpus, batch1..10
under ~/datasets/gasdrift/Dataset; results/arenas/gasdrift_killtest
.json + console log, gitignored). No instrument fixes were needed --
the test ran out of the box. Disk for the corpus came from clearing
this session's own closed Task-5 artifacts (~/venvs/brainscore 1.8 GB,
~/.brainio 1.2 GB, ~/.result_caching; re-creatable from the Task-5
entry if Brain-Score work ever reopens).

VALID, not blocked: all 10 batches parsed (per-batch class lines in
the log), trainable classes [1-6], train 90 / test 305 across batches
2-10; subcircuit 4,790 nodes (627 PN / 4,064 KC / 2 APL / 97 MBON),
162 glomerular types, w_scale 0.05762; ALL FIVE calibrations
hit_target=True (cal_median 0.0866-0.1040 in the band); ZERO
exceptions in every arm; 4,562.9 s wall at --workers 8 (declared ~1 h,
observed 76 min), peak RSS 1.22 GB.

MEASURED, mean-over-batches (pooled n=305; chance 1/6):
- real   0.4257 (129/305)  curve .543 .500 .433 .467 .417 .528 .278 .278 .389
- scram  0.3817 (115/305)  (scrambled-glomeruli control: real WINS)
- null0  0.4338 (131/305), null1 0.4854 (146/305), null2 0.4648
  (140/305) -- every degree-preserving rewire beats real
- raw    0.5022 (149/305)  (circuit-free comparator: beats everything)

THE FROZEN BARS: above-chance HOLDS (p 5.2e-26); beats-rewire FAILS
in all three seeds; beats-raw FAILS. VERDICT: KILL, exit 1. SIXTH
consecutive rewire-beats-real, now on the olfactory side. The new
decomposition this adds: the real PN->KC map DOES carry structure the
scrambled-glomerulus control destroys (0.426 vs 0.382) -- the fly's
glomerular fan-in is not nothing -- but a degree-preserving shuffle
preserves whatever the metric rewards and adds a little, and the raw
16x8 sensor features beat every spiking arm. Per the registration the
cloud side closes H-ALMB-GASDRIFT and executes the pre-stated dual
close of the Task 4 Keyword-FSCIL/MB limb. Expected-tier base rate:
0 for 16.

## Task 6: gas-drift MB kill test REGISTERED and BUILT (data-gated) -- 2026-10-06

User chose option 1 (Task 6 as the MB's last stand, one kill test
settling both open MB premises). Registration FIRST (H-ALMB-GASDRIFT,
open; docs/arenas/task6_enose/killtest_design.md -- frozen with the
moved priors AND the literature's own prediction on its face: Caron
2013 / Litwin-Kumar 2017 say PN->KC is near-random, so a bar-2 KILL is
the ESTABLISHED expectation, not a surprise; commit 769e0d8 carries
the due-diligence delta + registration alone), instrument second:

- scripts/arenas/gasdrift_killtest.py: UCI drift corpus, TRAIN batch 1
  (15/class seeded) / TEST batches 2-10 (6/class/batch), trainable
  classes derived from batch 1; frozen encoder (AE-1/AE-4: rank-CDF
  fit on TRAIN only, ENCODER_SEED permutation onto glomerular types,
  5-100 Hz PN rates, Poisson paired across arms); fc2_kc_sparse
  machinery verbatim at its passing config (asserted against
  verdict.pass_configs), theta AND alpha recalibrated per arm by the
  LK recipe verbatim on a seeded CAL_N=8 TRAIN subset (rewired arms
  calibrate fresh); run_sample = run_trial with the binary member
  mask generalized to the affine continuous drive; arms real /
  rewire x3 / raw-feature probe / scrambled-encoder context;
  --workers N process pool (decision-neutral: per-sample seeds
  fixed); BLOCKED on floors, any calibration miss, >5% exceptions.
- Two review catches BEFORE any data contact: (1) the alpha-balance
  feedback must read the ARM's own APL->KC block, not the real
  circuit's (a rewired arm has different APL edges); (2) Subcircuit
  is a frozen dataclass -- matrix swaps go through
  dataclasses.replace.
- tests/test_gasdrift_killtest.py: 9 tests -- the load-bearing one
  asserts run_sample EXACTLY reproduces fc2_kc_sparse.run_trial
  (same Poisson stream, same spike counts) at binary levels on a toy
  spiking network, plus parser dialects, rank-CDF saturation
  semantics, seeded encoder, split floors/caps, PASS + three KILL
  verdict paths, frozen constants, cloud BLOCKED listing.
- MEASURED in-cloud: 9/9 new (41/41 across the four kill-test
  suites, venv312); the script exits 3 BLOCKED here listing
  --data-root among the missing prerequisites.
- Runbook: docs/arenas/task6_enose/runbook.md. No new third-party
  packages this time. Declared cost ~7-8 h at --workers 1, ~1 h at
  --workers 8.

NEXT: user runs the one command locally and reports the JSON; cloud
closes H-ALMB-GASDRIFT either way. On KILL, the pre-stated dual close
also ends the Task 4 Keyword-FSCIL/MB limb as not pursued. 0 for 16
would be the base-rate count if the premise fails (pre-stated).

## Task 5 CLOSED with verdict; base rate 0 for 15 propagated -- 2026-10-06

Cloud-side close of the KILL recorded below, per the runbook's
division of labor:

- EXPERIMENTS.yaml: H-EARLYFILTER-BRAINSCORE-V1 open -> REFUTED, with
  the MEASURED evidence bullet carrying the per-arm centers/errors,
  the two-bars-cleared-for-the-first-time note (floor AND
  passthrough), the all-three-rewires-at-or-above-real failure, the
  fifth-consecutive count, and the two pre-verdict plumbing fixes
  (vendored brainio import; 0-d object-array time_bins). YAML
  re-validated.
- ASSUMPTIONS.md: AB-2/AB-3 -> MOOT (no submission on a KILL, so the
  rows never get exercised); AB-4 -> EXERCISED, USABLE (the declared
  convention produced above-floor predictivity and doubled its own
  passthrough -- the KILL came from the rewire bar, not a dead
  frontend; whether another convention reorders real vs rewire stays
  an open structural assumption). Rows annotated in place, never
  deleted.
- HANDOFF.md: Task 5 row -> COMPLETE WITH VERDICT.
- Expected-tier base rate 0 for 14 -> 0 for 15 (the fifteenth is
  H-EARLYFILTER-BRAINSCORE-V1, exactly as its registration
  pre-stated) propagated to the three outward carriers: HANDOFF
  conventions, task1 factsheet row, task1 writeup closing sentence.
  Writeup body re-counted: 1,448 words, unchanged. Dated historical
  "0 for 14" mentions left as written.

Per the frozen rule: no BrainModel submission, no account, no further
Brain-Score work. The program-level finding sharpens to: five
consecutive rewire-over-real on fc25-class circuits, with Task 5
adding the first MEASURED case where the dynamics beat their own
input -- the transformation is worth something; the specific wiring
is what keeps failing to be.

NEXT (user decision): Task 6 (e-nose / UCI gas drift) is next in
program order, but it is MB-dependent and inherits the MB's weak
priors (association rewire loss; calibrated flybench arm refuted) --
same priors gate the still-parked Task 4 Keyword-FSCIL/MB limb. The
options are a Task 6 due-diligence delta, an explicit MB-limb go, or
a re-rank of what remains (Tasks 6-8).

## Task 5: Brain-Score V1 kill test RUN -- verdict KILL (dynamics beat their input; the wiring still loses to its rewire) -- 2026-10-04

Environment first: brainscore-vision cannot install on Python 3.12 /
macOS arm64 (every version pins eva-decord, which ships no cp312 arm64
wheel -- MEASURED against PyPI); installed into ~/venvs/brainscore on
a uv-managed CPython 3.11.14 instead (torch 2.14.1). Disk for the
install + the benchmark's 1.33 GB assembly came from the user deleting
~/datasets/DvsGesture (4.9 GB, their call, re-downloadable per the
Task-4 entry).

Two plumbing BLOCKEDs before any verdict-relevant quantity, each fixed
at the API-contact line and recorded (the registered allowance):
1. brainscore-vision 2.3.22 no longer depends on standalone brainio --
   the module is vendored at
   brainscore_core.supported_data_standards.brainio. Import fallback
   added.
2. The benchmark hands time_bins as [array((50, 200), dtype=object)]
   -- a 0-d object ndarray per bin; tuple(b) raised "iteration over a
   0-d array". start_recording now unwraps 0-d arrays via .item().
   The declared contract (identical features per requested bin) is
   unchanged.

THE RUN (FreemanZiemba2013public.V1-pls, their PLS/CV/ceiling code
verbatim, locally): valid, not blocked -- 135 stimuli (floor 100),
visual degrees 4.0, lattice 169 columns / 1,046 scored early-filter
cells of 2,701 / pixels assigned 0.441, ZERO unstable presentations in
every arm, 75.9 s end to end after the one-time 1.33 GB data fetch,
peak RSS 2.38 GB.

MEASURED, ceiled centers (error = their reported estimate):
- real          0.0690 +/- 0.0201
- twin          0.0697 +/- 0.0209  (context: decides nothing; ~= real)
- passthrough   0.0330 +/- 0.0193
- rewire seeds  0.0828 / 0.0756 / 0.0735

THE FROZEN BARS: above-floor HOLDS (0.0690 - 0.0201 > 0); beats-
passthrough HOLDS -- the program's FIRST arm where the dynamics add
predictivity over their own input (0.069 vs 0.033, roughly double);
beats-rewire FAILS in ALL THREE seeds (every shuffle scores at or
above real). VERDICT: KILL, exit 1. FIFTH consecutive
rewire-beats-real on fc25-class circuits. The sharpened reading this
adds: what the metric rewards is the dynamics' temporal/nonlinear
transformation, which survives degree-preserving shuffling intact --
the specific early-filter wiring contributes nothing this benchmark
can see. Per the registration: no BrainModel submission, no account,
no further Brain-Score work; the hypothesis close in EXPERIMENTS.yaml
is the cloud side's step. Expected-tier base rate: 0 for 15.

## Task 5: Brain-Score V1 kill test REGISTERED and BUILT (data-gated) -- 2026-10-04

User said go. Registration FIRST (H-EARLYFILTER-BRAINSCORE-V1, open;
docs/arenas/task5_brainscore/killtest_design.md -- frozen with the
moved priors stated on its face; commit e89eb70 carries the
registration alone, before any instrument code), instrument second:

- scripts/arenas/brainscore_killtest.py: ONE public benchmark
  (FreemanZiemba2013public.V1-pls, their metric/ceiling/CV verbatim,
  locally); scored population = INPUT_TYPES cells in the central 9x9
  hex window (T4/T5 excluded -- they have their four results); ONE
  declared drive convention (AB-4: grayscale -> pure-numpy bilinear
  128x128 -> DSEC identity-crop column means -> contrast about
  mid-gray, constant 250 ms + 250 ms tail through L1/L2/L3 at
  INPUT_DRIVE -1.0, no sweep); fc25 trained_subset passing config
  verbatim; arms real / twin (context) / rewire per seed (4242
  convention) / input-passthrough; minimal BrainModel adapter with
  the two declared plumbing assumptions (visual_degrees = the
  benchmark's own; identical features per requested time bin) and
  per-arm identifiers so their regression cache cannot collide
  across arms; ApiMismatch and package failures exit BLOCKED (3),
  never a verdict.
- tests/test_brainscore_killtest.py: 8 tests on the pure plumbing
  (grayscale variants, deterministic bilinear resize, the declared
  column-drive convention incl. the empty-column ASSUMPTION branch,
  hex-window inversion, tolerant Score extractor across the API
  shapes, PASS + three KILL verdict paths + missing-error and
  missing-seed handling, frozen constants, cloud BLOCKED listing).
- MEASURED in-cloud: 8/8 new tests pass (32/32 with the DSEC + DVS
  suites, venv312); the script exits 3 BLOCKED here listing
  brainscore_vision among the missing prerequisites.
- Instrument bug caught by its own unit test BEFORE any data contact:
  inverting the hex embedding moves a boundary cell at exactly
  |dh| = 4 to 4 + O(eps), dropping it from the scored window;
  build_patch selects on raw hex coords and never faces this. Fixed
  with a 1e-9 tolerance, commented at the site.
- Runbook: docs/arenas/task5_brainscore/runbook.md. The
  brainscore-vision install is the user's own call (AF-6 covered
  flybench only); no dataset download by hand -- the benchmark
  fetches its own data on first load.

NEXT: user runs the one command locally and reports the JSON; cloud
closes H-EARLYFILTER-BRAINSCORE-V1 either way. On KILL, Task 5 ends
with no submission built. 0 for 15 would be the base-rate count if
the premise fails (pre-stated in the registration).

## Task 5 (Brain-Score): due diligence delta OPEN, kill test sketched, awaiting go -- 2026-10-04

Per program order after the Task 4 close (the Keyword-FSCIL/MB limb
stays gated), the next ranked arena's premise was re-verified from the
cloud before anything is built
(docs/arenas/task5_brainscore/due_diligence_delta.md):

- SOURCED today: submission still open and automated (website zip ->
  Jenkins PR, or direct GitHub PR; scored on their OpenMind cluster);
  brainscore-vision 2.3.22 on PyPI (2026-06-09, Python >=3.11, heavy
  torch-shaped deps); a limited PUBLIC benchmark pool (e.g.
  MajajHong2015public.IT-pls) is scorable locally without submitting.
- MEASURED container reachability: brain-score.org 000, readthedocs
  egress-blocked, pypi.org 200 -- data acquisition presumed local-side
  again.
- Moved priors stated on the delta's face: base rate 0 for 14; rewire
  over real 4 consecutive on T4/T5; the one surviving fly-positive
  (eye map, 4.5x vs scrambled) won as STATIC ANATOMY, not dynamics --
  the survey line bundles both, and the kill test must split them.
  Lamina/medulla early filters have never been tested against their
  own rewire; that is the open question.
- New assumption rows AB-4 (static image -> change-native frontend
  drive convention is an invention; fix one, declare, no sweep) and
  AB-5 (platform-alive facts, sourced) added to the register.
- Kill-test sketch (NOT registered yet): early-filter population
  features vs raw pixels AND vs degree-preserving rewire on one public
  benchmark, their metric code verbatim, locally, before any
  BrainModel wrapper or submission plumbing. Registration follows the
  user's go. AF-6's in-container authorization is NOT assumed to
  extend to brainscore-vision.

USER DECISION PENDING: go on Task 5 as sketched, or an explicit go on
the Task 4 MB limb, or a re-rank.

## Task 4 CLOSED (T4/T5 limb) with verdict; base rate 0 for 14 propagated -- 2026-10-04

Cloud-side close of the KILL recorded below, per the runbook's
division of labor:

- EXPERIMENTS.yaml: H-T4T5-DVS-GESTURE open -> REFUTED, with the
  MEASURED evidence bullet carrying the per-seed numbers, both failed
  sign tests, the twin-below-real attribution note, and the
  pre-verdict instrument fix (efd06a9). YAML re-validated.
- ASSUMPTIONS.md: AN-2 OPEN -> INVALIDATED, annotated in place (the
  linear readout works far above chance; it just does not earn the
  specific wiring its keep -- rewire and event counts both beat it).
- HANDOFF.md: Task 4 row -> T4/T5 LIMB COMPLETE WITH VERDICT; the
  Keyword-FSCIL/MB limb stays gated on the user's explicit go.
- Expected-tier base rate 0 for 13 -> 0 for 14 (the fourteenth is
  H-T4T5-DVS-GESTURE, exactly as its registration pre-stated)
  propagated to the three outward carriers: HANDOFF conventions,
  task1 factsheet row, task1 writeup closing sentence. Writeup body
  re-counted: 1,448 words, unchanged (the swap is count-neutral).
  Dated historical "0 for 13" mentions (frozen registration, earlier
  worklog entries, AN-2's preserved prior text) left as written.

Per the frozen rule, no NeuroBench harness integration is built. Next
arena decision is the user's: Task 5 (Brain-Score) per program order,
or an explicit go on the Keyword-FSCIL/MB limb, or a re-rank given
the fourth consecutive rewire-over-real result.

## Task 4: DVS Gesture kill test RUN -- verdict KILL (real loses to its rewire AND to event counts) -- 2026-10-03

The user ran the one registered command on the fixed instrument
(results/arenas/dvs_killtest.json + .log, gitignored). Valid, not
blocked: 1,176 train / 288 test trials parsed (floors 600/150), ZERO
out-of-frame parser flags over all 122 files, ZERO unstable windows in
every arm, 453.5 s wall, peak RSS 2.39 GB (the pre-fix projection was
~21 GB; the estimate of ~2.5 GB held). Drive norm (seed-0 cal subset,
50 trials): 1.4130. Train union 876 trials; test subjects user24-29.

MEASURED, per seed (pooled test accuracy; chance 1/11):
- seed 0: real 0.4097, twin 0.3993, null 0.4410, event_count 0.4722
- seed 1: real 0.3889, twin 0.3750, null 0.4236, event_count 0.4444
- seed 2: real 0.4271, twin 0.4132, null 0.4653, event_count 0.5035

THE FROZEN BARS: bar 1 HOLDS (real above chance all seeds, worst
p 2.6e-42); bars 2 and 3 FAIL -- real loses to its own
degree-preserving rewire in ALL THREE seeds (sign test over 18
subject x seed cells: real better on 5, p 0.985) and to the
circuit-free event-count features in all three (better on 4 of 16,
p 0.989). VERDICT: KILL, exit 1. Attribution context: twin
(uniform-tau) sits BELOW real in every seed, so the temporal
heterogeneity is doing something -- just nothing the rewire does not
do better. This is the FOURTH consecutive result on this circuit
where the specific T4/T5 wiring is beaten by a degree-preserving
shuffle of itself (ARC motion, DSEC real, DSEC uniform-tau context,
now DVS Gesture). Per the registration: Task 4's T4/T5 limb closes
with no NeuroBench integration built; the Keyword-FSCIL/MB limb needs
the user's explicit go. Hypothesis close in EXPERIMENTS.yaml is the
cloud side's step per the runbook; this entry is the measured record.

## Task 4: instrument memory fix BEFORE the first run (measured 21 GB -> ~2.5 GB) -- 2026-10-03

Local preconditions passed as registered (BLOCKED with exactly the one
--data-root line, exit 3; 9/9 unit tests). Dataset downloaded from
IBM's official Box folder (DvsGesture.tar.gz, 2,938,955,106 bytes;
license CC BY 4.0, attribution IBM Research), stream-extracted to
~/datasets/DvsGesture: 122 .aedat + 122 _labels.csv pairs, both split
files, 4.9 GB.

MEASURED before launching, per the resource rule: load_split holds
every file's raw events as int64/float64 (32 B/event; one 42.3 MB file
parsed to 0.168 GB in 0.4 s), projecting to ~21 GB across the 5.3 GB
of AEDAT -- unrunnable on the 16 GB host. The sample file showed 0.0%
out-of-frame events. Patch dims for the arithmetic: 2,701 nodes, 507
driven, 498 scored, 169 columns.

THE FIX (semantics-preserving memory layout, no decision-rule contact;
scripts/arenas/dvs_killtest.py): (1) load_split takes a binner and
stores each trial's (signed, counts) window tensors (~0.4 MB/trial),
dropping raw events file by file; (2) drives_and_ec returns the
(k, n_sub, 169) normalized cumulative grids instead of dense
(k, n_sub, 2701) tensors, which were zero off driven_idx; (3) simulate
expands one sub-window at a time via the new expand_subwindow_drive
into a reused (n_nodes, m) buffer. Identical binning calls on identical
inputs and an elementwise-identical drive expansion, so downstream
numbers are bit-identical to the registered pipeline -- asserted by two
new unit tests (dense-layout equivalence; binner receives exactly the
filtered events the eager path stored). 11/11 tests; the BLOCKED
precondition line is unchanged. No verdict-relevant quantity was
computed before this fix (data contact so far: the one-file RAM/parse
measurement and its out-of-frame fraction).

## Task 4: DVS Gesture kill test REGISTERED and BUILT (data-gated) -- 2026-10-03

User said proceed. Registration FIRST (H-T4T5-DVS-GESTURE, open;
docs/arenas/task4_neurobench/killtest_design.md -- frozen with the
moved priors stated on its face), instrument second:

- scripts/arenas/dvs_killtest.py: our own AEDAT 3.1 polarity reader
  (spec-exact bit layout, validity mask, timestamp overflow, foreign
  packets skipped; validated on synthetic packed bytes); the dataset's
  OWN subject split read verbatim; 6x250 ms windows per trial; DSEC
  binning imported and reused on the identity 128-crop; fixed 10 ms
  sub-windows (no dt sweep); one drive-norm scalar from a seeded
  TRAIN calibration subset; fc2 settle-stream-tail batched across all
  windows; arms real / twin / per-seed rewire / circuit-free
  event-count features; t4t5-motion-style probe (3-fold CV on TRAIN);
  the frozen three-bar verdict assembled mechanically
  (chance-in-all-seeds, beats-rewire, beats-event-count; paired sign
  tests over subject x seed cells + pooled majority). Data gate
  verified in-cloud (exit 3 naming the measured missing pieces).
- 9 unit tests (tests/test_dvs_killtest.py): parser round trip,
  validity/overflow/foreign-packet handling, truncated-tail safety,
  window placement incl. short trials, event-count features, exact
  binomial, PASS + three KILL paths of the verdict, frozen constants.
- Runbook: docs/arenas/task4_neurobench/runbook.md (download, the one
  command, 30-90 min local, report-back protocol). The neurobench
  package is never executed for this decision.

NEXT: the user's local run decides. On KILL, Task 4's T4/T5 limb closes
with no NeuroBench integration built; the Keyword-FSCIL/MB limb then
needs an explicit go. On PASS, the harness integration gets its own
registered design.

## TASK 3 CLOSED; base rate propagated; Task 4 (NeuroBench) OPENS -- 2026-10-03

The local session's verdict run closed H-FLYGI-FLYBENCH-CALIBRATED
refuted (its two WORKLOG entries below carry the numbers; registry has
the evidence block). Cloud-side reconciliation on top: HANDOFF Task-3
row -> COMPLETE WITH VERDICT (the UNIFORM row stands as the measured
contribution; any flybench PR / verified-badge step is the user's
decision from that row); the canonical expected-tier base rate moved to
0 for 13 and is propagated to the three outward-facing carriers --
HANDOFF's conventions line, the factsheet row (with the thirteenth
named), and the writeup's closing sentence (word count unchanged at
1,448; the factsheet is the trace). Per the program order, Task 4
(NeuroBench) opens with its due-diligence delta next.

## Task 4 (NeuroBench) OPENED: delta measured; priors moved; decision surfaced -- 2026-10-03

Full record: docs/arenas/task4_neurobench/due_diligence_delta.md.
MEASURED: neurobench 2.3.0 IS on PyPI (torch-shaped deps, gdown);
neurobench.ai / research.ibm.com / dropbox.com egress-blocked in-cloud
(drive.google.com already was) -- datasets are local-side; in-cloud
install/run of the neurobench package is a NEW third-party execution
awaiting the user's nod (AF-6 covered flybench). THE IMPORTANT DELTA is
internal: since the 2026-09-30 survey ranked DVS Gesture a "native
T4/T5 fit", this program refuted T4/T5 on ARC frames AND on
event-camera input, with the rewire beating real wiring three
consecutive times (base rate 0 for 13). Gesture classification is a
different computation (stated in the delta doc -- the kill test is not
pre-decided), but the expected-tier prior is materially worse than at
ranking. NEXT: register the DVS kill test (DSEC-pattern arms: real /
uniform-tau / rewire / event-count features, frozen bars) and build its
data-gated instrument -- unless the user, reading the moved priors,
chooses to skip or re-rank Task 4. AN-2 annotated; AN-3/AN-4 added.

## TASK 3 CLOSED WITH VERDICT: calibrated arm KILLED by the frozen bars; H-FLYGI-FLYBENCH-CALIBRATED refuted -- 2026-10-03

The user ran the calibrated MaleCNS arm locally (runbook section 3:
malecns_minecraft config, 3 seeds, rewired control, --jobs 6, unpinned
build; results/arenas/malecns_calibrated.json, gitignored like the
other rows). One instrument bug found and fixed en route (below). The
registered premise -- biological calibration buys back the activation
checks -- is REFUTED; the uniform row stands as Task 3's measured
contribution, per the registration.

MEASURED, the calibrated row: core 1.000 / hard 0.6194 / graded 0.7445
(CI95 [0.7414, 0.7481]) / specificity vs rewired +0.295 / 10 of 30
tasks passed (uniform: 1.000 / 0.6044 / 0.7113 / +0.282 / 9). Every
passing task fails on shuffled wiring. Skips identical to the uniform
run -- the known four plus gf_free_route_to_ttmn and closed_loop_escape
(both flygym/torch, also skipped in the uniform run; nothing new).
Cost: 79.5 min wall at --jobs 6, peak RSS 679 MB.

Calibration sidecar facts (healthy, not blocked): real wiring alpha
1.826, achieved KC sparseness 0.0750 (band midpoint exactly), tau
table resolved for 36,822 of 176,422 neurons, 4 graded units (APL/CT1),
4,064 KCs; rewired control calibrated FRESH on its own wiring (alpha
1.780, sparseness 0.0750), so the specificity number carries no
threshold-mismatch artifact. Two calibrations total, as designed. (The
on-disk sidecar's "applied: false" is a write-order quirk -- the cache
file is saved before _apply() updates the in-memory dict; the run
numbers differ from uniform throughout, so application is not in
doubt. Cosmetic; left unfixed post-measurement deliberately.)

THE VERDICT (mechanical, frozen bars): KILL. Bar 1 FAILS -- mean
graded over the 58 shared activation checks moved +0.0002 against a
required +0.02. Bars 2 and 3 HOLD (overall 0.7445 >= 0.701;
specificity +0.295 >= +0.252). The decomposition is the AF-8 story
repeated at higher fidelity: the calibration's entire gain landed in
the suppression/ratio class (mean 0.639 -> 0.685), almost all of it
mb_sparseness_apl 0.625 -> 1.000 -- the one task the LK calibration
directly targets -- while the activation subset it was built to buy
back did not move, and the flagged water-response loss stayed at 0 Hz.
The instrument did what it was designed to do: it refused to credit a
win in the class the premise was not about.

INSTRUMENT BUG, found before recording, fixed, regression-tested
(scripts/arenas/flybench_calibrated_verdict.py): shared checks were
keyed on the FULL description string, which embeds flybench's volatile
"[N/3 seeds, sd S]" annotation, so every check the calibration moved
silently left the shared set -- the first verdict ran on 66 of 149
checks, i.e. almost only unmoved ones (a near-tautology). Fixed to key
on the annotation-stripped identity (flybench diff's own convention);
corrected run shares 149/149 checks. The KILL holds under BOTH keyings
(delta +0.0005 buggy, +0.0002 corrected), so no conclusion changed --
but the corrected audit list is the one of record. Test:
test_moved_checks_stay_shared_despite_annotation_drift.

Registry: H-FLYGI-FLYBENCH-CALIBRATED -> refuted, evidence block
carries the numbers. Expected-tier base rate is now 0 for 13.

## Task 3: the flagged bootstrap-CI oddity RESOLVED (instrument, not data) -- 2026-10-03

The 2026-10-02 flag ("point estimate -0.070 outside the reported CI
[-0.062, -0.045]") is resolved. MEASURED, by reading flybench's diff
command and recomputing from the two stored JSONs:

- The point estimate is real: mean stored-graded difference
  reference-minus-FlyGI over the 149 shared checks = -0.0696.
- The CI is also real but covers a DIFFERENT estimator: flybench
  diff's "seed-bootstrap" re-grades resampled per-seed values through
  plain graded_from_margin(margin_of(...)), which ignores the
  saturated/floored flags that zero a check's stored graded score. On
  9 of the 149 checks (6 reference, 3 FlyGI -- pn_transfer_function,
  da1_sparseness, steering_dna02_vs_dna01) the stored graded is 0.0
  (non-diagnostic signal) while the re-grade is nonzero. The
  re-graded full-sample mean is -0.0546, which sits INSIDE the
  reproduced CI [-0.062, -0.045] (center -0.0540). So: a consistent
  CI around an estimator that is not the headline statistic -- a
  flybench instrument inconsistency, not a transcription error and
  not a problem with our rows.
- A CI consistent with the headline statistic, stated with what is
  resampled: bootstrap over CHECKS (resample the 149 paired
  per-check differences of stored graded values, 10,000 resamples)
  gives 95% CI [-0.112, -0.030], containing -0.0696. The
  seed-resampling CI cannot be computed consistently without
  reimplementing flybench's saturation/floor logic, so the
  check-resampling CI is the one to quote.
- Context number from the same recompute: P(reference better on a
  random shared check) = 0.446 -- consistent with AF-8's finding that
  our net win is concentrated, not uniform.

Outward text should quote: mean graded difference reference-minus-ours
-0.070 over 149 shared checks, 95% CI [-0.112, -0.030] (bootstrap over
checks), P(reference better) 44.6%.

## Task 3: calibrated adapter BUILT and exercised; one instrument bug caught by its test -- 2026-10-03

H-FLYGI-FLYBENCH-CALIBRATED's instrument is implemented and pushed;
the MaleCNS measurement is the user's run (runbook section 3).

- scripts/arenas/flygi_flybench_adapter.py gains FlyGICalibratedAdapter
  (engine UNMODIFIED, all composition): fc2 tau table verbatim (slow
  150 / Tm9 200, the dossier anchor, ASSUMPTION-labelled), graded
  APL/CT1 via the benchmark's own selectors with a declared
  rate-equivalence bridge (5 Hz/mV, ASSUMED), and LK-style per-KC
  thresholds (mu + alpha*sigma, alpha bisected to the 0.075 literature
  midpoint) calibrated on seeded random subsets of the KCs' OWN
  presynaptic partners -- never a benchmark stimulus. File-cached per
  wiring (shared across --jobs workers). Reuse policy, each branch
  labelled: identical wiring and jitter-same-pattern reuse; SILENCED
  variants reuse the intact thresholds (acute shibire -- recalibrating
  would partially cancel the manipulation under test); genuinely
  different wirings (the rewired CONTROL above all) calibrate fresh on
  their own wiring, so specificity carries no threshold-mismatch
  artifact.
- BUG CAUGHT BY ITS OWN UNIT TEST before any measurement: the
  silenced-variant predicate checked zeroed ROWS of the engine's
  transposed matrix -- i.e. incoming synapses -- while silence_neurons
  zeroes OUTGOING (columns of the transpose). Fixed to compare in CSC
  space; the test now also asserts APL-silenced toy variants reuse the
  intact thresholds.
- scripts/arenas/flybench_calibrated_verdict.py applies the FROZEN
  bars mechanically (activation +0.02 / overall >=0.701 / specificity
  >=+0.252; split = exceed-and-not-ratio, audit list printable;
  BLOCKED from calibration sidecars scoped by n_neurons).
- Tests: 9 in tests/test_flybench_calibrated.py (alpha search, reuse
  predicates, toy-level calibration + determinism + cache round trip +
  silenced reuse, split classification, all four verdict outcomes,
  frozen-constant assertions).
- MEASURED, toy exercise: verify-adapter clean on the calibrated
  class; full toy suite completes with calibration + graded + silenced
  paths engaged -- 0.91 / graded 0.93 / 22 of 30 (uniform class: 0.90
  / 0.92 / 21). Design-doc amendment recorded OPENLY at build time:
  the toy carries KC/APL/tau-table type names by construction, so the
  registered byte-identity toy bar applies to the uniform class only;
  the calibrated class's toy bar is the calibration-exercise check.
  The three frozen MaleCNS bars are untouched.

## Task 3: calibrated-parameters design REGISTERED (before build) -- 2026-10-02

H-FLYGI-FLYBENCH-CALIBRATED registered, frozen design in
docs/arenas/task3_flybench/calibrated_design.md. Premise: the class-2
calibration ingredients (fc2 tau table by literature class, graded
APL/CT1 internal to the adapter, LK-style KC thresholds calibrated on
seeded NON-TASK random PN drives) buy back the activation checks
without surrendering suppression or specificity. Trivial alternative:
our own measured uniform row. Bars frozen: activation-subset mean
+>=0.02, overall graded >=0.701, specificity >=+0.252; mechanical
activation/suppression split from task YAML; BLOCKED on near-zero
type-name coverage. Next cloud-side: implement the calibrated table +
calibration hook in the adapter (engine unmodified; toy regression =
byte-identical fallback) with tests; the measurement is the user's
local run, same pattern as before.

## Task 3: first MaleCNS rows MEASURED (unpinned); engine beats reference on net -- 2026-10-02

The user executed the Task-3 runbook locally. Instrument surprise first,
measured and banked (AF-7): a fresh anonymous neuPrint fetch reproduces
the pinned COUNTS exactly (176,422 / 6,287,789) but not the pinned
FINGERPRINT (annotations + signed weights drift on re-export), so both
rows ran --allow-unpinned and are marked unpinned; the runbook was
corrected en route (0323fdb). Toy sanity reproduced the cloud result
(verify-adapter clean; core 5/5, graded ~0.99).

THE ROWS (malecns_minecraft.yaml config, 3 seeds, rewired control;
JSONs local at results/arenas/malecns_{reference,flygi}.json):
- reference LIF g0.65: core 0.5667 / hard 0.5366 / graded 0.639 /
  specificity vs rewired +0.184. Core matches their recorded row
  EXACTLY (drift check passes on core); hard differs from their 0.5798
  -- annotation drift in hard-tier selectors suspected.
- FlyGI class-2 engine (Shiu constants): core 1.000 / hard 0.6044 /
  graded 0.711 / specificity +0.282.
Diff over 149 shared checks: mean graded reference-minus-ours -0.070,
seed-bootstrap CI [-0.062, -0.045] AS REPORTED (flagged: the point
estimate sits outside the reported interval -- user to re-check which
statistic the CI covers before this number goes in any outward text).
Our engine is reliably better on net AND more wiring-specific (+0.282
vs +0.184).

HONESTY NOTE, the design input (new AF-8): the win decomposes
asymmetrically -- our biggest gains are SUPPRESSION checks where the
reference saturates (292 Hz -> 0), and our one big loss is an
ACTIVATION check (water response 95.8 -> 0 Hz). A globally quieter
engine wins suppression cheaply, so activation checks are the
discriminating set for the calibrated-parameters step. Skips recorded:
egg_laying_ovidn (flywire-only), halt_walk_off (selector matches no
MaleCNS neurons -- their README predicted male-name gaps),
embodied/closed-loop (flygym not installed). AF-4 part-resolved
structurally: graded units are internal to the adapter; the spike-only
contract holds unless a readout population is declared graded.

## TASK 2 CLOSED WITH VERDICT: DSEC kill test KILLED -- H-T4T5-DSEC-DIRECTION refuted -- 2026-10-02

The user ran the frozen kill test locally (thun_00_a; one instrument
fix en route, e6477dd: DSEC events are Blosc-compressed, the harness
now imports hdf5plugin). Valid, not blocked: 33/33 usable eval windows
(threshold 30), 0 unstable, 66 s. MEASURED: eval median per-window mean
angular error -- real 81.36 deg, uniform-tau 78.09, rewired(mean)
78.85, event-centroid comparator 81.88, GT-median global direction
65.36. Both frozen bars FAILED (real<comparator p=0.364; real<rewired
p=0.982). Registry closed refuted, with the honest reading at tier:
every arm sits near the 90-deg chance line at this binning -- the
oracle single global direction beats all per-column estimates -- so no
arm extracts usable per-column direction here, and within that the
degree-preserving rewire beats the real wiring for the THIRD
consecutive time across tasks (MB association, ARC motion, DSEC
direction). Per the registration: recorded class-2.5 limit on
event-camera input at the declared binning; no dense pipeline, no
benchmark account (AD-1/AD-2 retired), no entry. Task 2 is COMPLETE
per operating rule 3 -- a failed kill test is a completed task.

## Task 1: quality pass over the writeup + all visual assets -- 2026-10-02

User-directed review ("make sure they're up to snuff"), every rendered
asset eyeballed and every figure number re-traced to the factsheet.
Found and fixed:

- COVER BUG (shipping-blocking): the title wrapped to a second line and
  COLLIDED with the subtitle -- present in the shipped cover.png since
  2026-10-01. Fixed (one-line title at 34px, subtitle cleared),
  re-rendered at 2x, eyeballed clean.
- fig3 semantic fix: in the trained-head panel the held-out measurement
  was colored GRAY, which the legend defines as "control" -- it is our
  component's honest held-out score, not a control. Both trained-head
  dots are now blue per the legend's own definition. Also trimmed the
  dead band at the canvas bottom (1600 -> 1380 px tall).
- fig2's "4,257 neurons" (LC) had no factsheet row -- the number is
  solid (EXPERIMENTS.yaml, literal_rate_lc_readout config, WORKLOG
  readout table) and now traces: factsheet row added.
- writeup.md: two ragged source lines from the edit rounds rewrapped
  (no word changed; body stays 1,448).

Verified clean, no action: fig1 (ladder vs hidden -- all six numbers,
submission IDs, legend, scope footer), fig2 (all verdict-matrix numbers
match writeup + factsheet), card.png (legible at thumbnail scale),
writeup end-to-end read (no seams, boundaries intact). Palette: the
figure palette passes the dataviz validator's CVD/normal-vision/contrast
checks; the gray slot intentionally fails the chroma floor because
controls are DELIBERATELY recessive gray with every dot direct-labeled
-- recorded as the accepted deviation.

## Task 1: relicensed to MIT-0 on the user's go -- 2026-10-02

"go MIT-0" (the user, copyright holder). LICENSE is now the MIT No
Attribution text with the same copyright line; README's license sentence
and CITATION.cff's license field (SPDX MIT-0) updated;
THIRD_PARTY_NOTICES deliberately untouched (third-party code keeps its
own MIT/MIT-0 licenses, clearing arcprize's public-sharing floor for
3rd-party code). AP-4 closed. The last ARC-side prerequisite that was
Claude-or-user decision-shaped is done; what remains on Task 1 is pure
execution (release ~Nov 1, submit by Nov 8 per kaggle_form.md).

## Task 1: arcprize overview checked -- the CC0/MIT-0 requirement is REAL; AP-4 re-reversed -- 2026-10-02

The user pasted the last unchecked source, arcprize.org's general 2026
overview. It carries the clause the Kaggle Rules do not, verbatim: "all
code and methods authored by the submitter must be made open source
under a permissive public domain license (eg. CC0 or MIT-0)", as an
ELIGIBILITY condition, "before receiving official private evaluation
scores". Reconciliation of all three sources, now each read in full:
arcprize's CC0/MIT-0 = eligibility open-sourcing to the world; Kaggle's
CC-BY 4.0 = the winner's separate grant to the sponsor; the Kaggle tabs
simply never carry the first clause -- which is exactly how yesterday's
Rules-only reading went wrong. AP-4: back to CONFIRMED as originally
sourced; the one-day invalidation is itself invalidated and both moves
are recorded in the register row (the register's never-delete rule is
why this whiplash stays visible). Plain MIT has an attribution clause
and is not "public domain"; the safe reading is it does NOT qualify.

CONSEQUENCE, reopened for the user (copyright holder): relicense
FlyGI-authored code to MIT-0 (recommended -- minimal diff) or CC0
BEFORE the repo goes public (~Nov 1). Prepared commit on their go.
Third-party components are unaffected: arcprize's floor for 3rd-party
code is "allows public sharing (eg. Apache-2.0, GPLv3)" and every
notice-listed piece is MIT/MIT-0. Also re-confirmed on the same page:
papers due Nov 8; no-internet evaluation (our submissions complied).
Runbook Step 2 and the release checklist flipped back accordingly.

## Task 1: Kaggle OVERVIEW tab measured; eligibility layer corrected -- 2026-10-02

The user pasted the Overview tab (submission requirements + evaluation).
Register deltas, all banked:

- AP-5 CONFIRMED IN FULL, and my form-only reading corrected: the form's
  checklist and the ELIGIBILITY requirements differ. The Overview makes
  the Media Gallery (with a required cover image) and the public code
  notebook (via Project Links) conditions of eligibility even though the
  form checklist does not enforce them. The 1,500-word limit + penalty
  wording is now verbatim-measured (we are at 1,448).
- AP-4 residual nearly closed: the Overview also contains NO CC0/MIT-0
  wording. Only arcprize.org's general 2026 overview page remains
  unchecked; MIT stays.
- AP-9 fully resolved: "you will be asked to provide your submission ID"
  (Accuracy criterion note) -- have 56683298 ready.
- AP-15 updated: Kaggle is internally consistent at 2026-11-09 23:59 UTC
  (form + Overview agree); arcprize still says Nov 8; plan stays Nov 8.
- NEW AP-16 (auto-publication): a private Kaggle resource attached to
  the writeup "will automatically be made public after the deadline."
  Linking the private submission notebook = consent to publication, so
  prefer making it public deliberately on release day, and put the
  MaleCNS CC BY 4.0 citation on the private dataset's description
  BEFORE submitting (AP-6) in case publication cascades.

kaggle_form.md corrected to carry both layers (gallery/notebook now
marked required; submission-ID and dataset-citation items added to the
pre-Submit checklist). No artifact changed: we already satisfied every
requirement; this pass was about knowing it rather than assuming it.

## Task 1: the LIVE Kaggle writeup form measured; artifacts brought to spec -- 2026-10-02

The user opened the real New Writeup form and pasted it verbatim. Three
assumptions moved, two artifacts were produced, one was fixed:

- AP-5 part-INVALIDATED: the six REQUIRED checklist items are Title
  (<=80), Subtitle (<=140), Card/Thumbnail Image (560x280), Track
  (auto), Project Description, Project Links. The Media gallery and
  file uploads are OPTIONAL, there is NO notebook-attachment field
  (notebooks go under Project Links), and no word limit is displayed
  (keeping <=1,500 anyway; the penalty wording from the extraction is
  unverified).
- AP-9 CONFIRMED with mechanics: no code-submission selector exists;
  linkage = same team (Rules 2.1.b) + the submission IDs named in the
  body + a Project Link to the submission notebook.
- NEW AP-15: the form shows Nov 9 2026 3:59 PM PST (= 11-09 23:59 UTC)
  vs arcprize's Nov 8 -- a confirmed two-source discrepancy; the plan
  stays 11-08.
- FIXED: the writeup subtitle was 322 chars against the form's 140 cap.
  Rewritten to 139, scope words kept ("both circuits tested in full
  scored below their degree-preserving rewires"); title already fits
  (78/80). Body untouched (1,448 words).
- NEW media/card.html + card.png (1120x560 at 2x) + card_560x280.png:
  the required 2:1 card image, cover-palette hex motif, rendered through
  the headless Chromium and eyeballed.
- NEW kaggle_form.md: field-by-field paste guide (slug, card, gallery
  order, description paste boundary, the three Project Links incl. the
  currently-private submission notebook megusalexandrus/flygi-arc-agi-3
  with a recommended-not-required make-public note, DOI opt-in, and the
  pre-Submit checklist). submission_runbook.md Step 5 now defers to it.

## Public-release hygiene: personal paths + email scrubbed, CITATION.cff set -- 2026-10-02

User direction: apply best practice (remove local /Users/... paths, set
the citation). Measured sweep: 76 lines in 56 tracked files embedded
/Users/<username>/...; one tracked doc carried the user's personal
email. Done, category by category, and verified:

- 47 archived probe/solver scripts in docs/fap_extension_20260928/ now
  resolve ROOT = Path(__file__).resolve().parents[3] (portable; logic
  unchanged). Verified: all compile; root resolves to the repo root for
  every one. Nothing imports them (docstring references only).
- JSON records (integration_reports.json, completion_reports.json) and
  results/manifests/{dynamics_regime_20260921,positive_control_regime_
  20260922}.json now carry repo-relative paths; hashes and values
  unchanged; nothing in the code reads these files (grepped).
- LATENT BUG FIXED: tests/test_fap_arch_crosshair_parking.py hardcoded
  its fixture's absolute path, so off the original machine its
  frame-bank negative audit silently SKIPPED. Now repo-relative like its
  siblings. Measured: with a synthetic bank at the repo path the test
  RUNS and passes; without one it skips cleanly.
- CLAUDE_CODE_REFACTOR_HANDOFF.md paths made generic; the personal email
  in docs/arenas/due_diligence_20260930.md replaced (the release
  checklist's "no emails" sweep predated that file).
- CITATION.cff: author Mustafa Safdari (alias msafdari -- the name every
  commit is already authored under; no email), repository link, MaleCNS
  paper as a reference. cffconvert: valid against schema 1.2.0.
- Not done, deliberately: history rewrite (AGENTS.md forbids force-push
  of shared history without an explicit ask; old paths only expose the
  username, which equals the public author name already on every
  commit).

ENVIRONMENT NOTE: the cloud container's default python3 is 3.11, but
the repo requires 3.12 (PEP 695 syntax in src/flygi/controller/scene.py),
so repo tests must run under 3.12 here (uv venv in the session
scratchpad). PRE-EXISTING (identical on the untouched tree, verified by
stash): 4 fap_arch tests (merge_deliver x2, pip_door x2) hard-fail with
FileNotFoundError when results/diagnostics/recognizer_frames.npz is
absent -- they lack the skip guard their siblings use. Under 3.12 the
fap_arch + dsec families: 199 passed, 8 skipped, those 4 failed.
FIXED same day at the user's direction: those 4 tests now carry the
siblings' skipif guard (module-level `needs_recognizer_frames`). Measured
under 3.12: fresh-clone state 199 passed, 12 skipped, 0 failed; with a
synthetic bank present all 4 RUN (the su15 positive test correctly fails
on blank frames -- the guard hides nothing when the data exists). On the
user's machine, where the real bank lives, behavior is unchanged.

## Task 1: Kaggle Rules read; license requirement reversed -- 2026-10-02

The user JOINED the Paper Track on Kaggle (entry deadline 2026-10-26
retired) and pasted the full Kaggle Rules tab verbatim. Measured against
the register:

- AP-4 INVALIDATED as sourced. The rules name the winner license as
  CC-BY 4.0 (§1.6, §2.5), granted "if you are a Competition winner" as a
  condition of the prize (§2.8). CC0/MIT-0 -- what our 2026-09-30 search
  extraction reported -- appears nowhere in the rules text. Consequence:
  no relicense is needed to submit; the repo stays MIT (our reading, not
  legal advice; MIT also meets §3.6.b's OSI/commercial-use condition).
  Residual: the CC0/MIT-0 wording may live on the Kaggle Overview tab or
  arcprize's general 2026 overview page, which were not pasted.
- AP-3 CONFIRMED: "Team must match the team making a submission to either
  ARC-AGI-2 or ARC-AGI-3" (§2.1.b).
- AP-5 still OPEN but located: the rules defer to "the requirements
  stated on the Competition Website" (Overview tab).
- NEW, all CONFIRMED from the text: AP-11 one writeup submission per
  team (§2.2.a) -- SUBMIT is one-shot; AP-12 public code sharing during
  the competition period must also be posted on the competition's Kaggle
  forum/notebooks (§3.6.b) -- a forum post with the repo link is now a
  release-day step; AP-13 winner clocks (respond in 1 week, prize docs
  in 2 weeks, code + reproduction docs). AP-14 (low risk, OPEN): every
  third-party component in THIRD_PARTY_NOTICES.md is MIT/MIT-0 except
  the sponsor's own Kaggle starter, whose pinned commit has no LICENSE
  file.

Docs brought in line: submission_runbook.md (status block, Step 2 now
optional, forum-post step, one-shot SUBMIT warning, dates table, and a
stale instruction removed -- it told the user to trim a section "marked
OPTIONAL" that the writeup does not have), public_release_checklist.md,
PLAN.md, HANDOFF.md.

## Task 1: Prior-work section added to the writeup under gates -- 2026-10-02

The user eyeballed arcprize.org/competitions/2026/paper (pasted
verbatim): AP-1 CONFIRMED (papers due 2026-11-08 -- the plan date is
now verified), AP-2 CONFIRMED verbatim, AP-9 raised to high confidence
("linked to", not "new"), and new AP-10 found a real gap -- the
What-to-Include guidance lists Prior work and the Novelty rubric scores
against existing public research, while writeup.md named no prior
approach. Revision applied at the user's direction: a ~100-word Prior
work section (demo wave; the three published counter-evidence lines;
CompressARC 2025 3rd at ~20% on ARC-AGI-1; ARC-NCA/VSA placement; no
pure negative-results paper in the money, 2024-2025 winner lists), with
offsetting trims (sg-bioeye-t4t5 borderline sentence removed to the
factsheet only; parentheticals compressed; no number changed). Factsheet
External-context extended so every new claim traces. TWO GATES run as
independent agents: compliance regression (1 finding: restore "compiled"
+ "min" in the EB-ring sentence -- applied) and fact/tier (7 findings,
all qualifier/scope restorations: "most"/none-ran-all-three on the wave,
"often matching or beating", ARC-AGI-1 + 2025 qualifiers on CompressARC,
"pure ... in the money (2024-2025 winner lists)" dated, "of this
non-LLM track" restored, "min" circvar, click-only-games scope -- all
applied). Body 1,470 -> 1,448 words (target <=1,450; Kaggle cap 1,500).
Remaining Kaggle-side unknowns for the user's browser check: AP-3,
AP-4 (license wording + when it binds), AP-5 mechanics, AP-9 linking
mechanics.

## Task 3: adapter kill test PASSED both bars, zero free parameters -- 2026-10-01

H-FLYGI-FLYBENCH-ADAPTER: open -> supported, measured minutes after
registration (registry entry has every number; compressed here). Our
class-2 SpikingNetwork, UNMODIFIED, behind flybench's contract via
scripts/arenas/flygi_flybench_adapter.py (plumbing only, all declared
in killtest_design.md): verify-adapter "conforms: no defects", and the
five canonical core reflexes PASS on the toy at the DERIVED unit
bridge w_scale = w_syn*gain/tau_m -- no gain sweep, no fitted
parameter anywhere. Seed guard: --tier core --seeds 3 = 5/5, graded
0.99 [0.99, 0.99]. Full-suite context: ours 0.90/0.92/21-of-30 vs
reference 0.93/0.94/24-of-30; the three lost tasks (EPG ring bump
never ignites, APL sparsification ratio 1.03 vs 1.14, one steering
rate at 4.07 vs bar 5) are all sustained-activity-flavored, matching
the declared differences (no delay line, dt 0.5 vs 0.1 ms,
current-based synapse) -- and the ring loss echoes this repo's own
two-fidelity-class bump verdict. One check gained (PN transfer stays
under the 170 Hz bar where the reference saturates to 272). SCOPE:
contract-level, synthetic toy, no fly claim.

Task 3 remaining, in order: (a) MaleCNS rows -- neuprint fetch is
local-only (AF-2); the natural next artifact is a Task-3 runbook for
the user's local fetch + build + our-adapter run with their
shuffled-wiring controls; (b) the scientific heart, our
Litwin-Kumar-calibrated MB parameters vs their PN-broadcast finding,
needs its own registered design first (AF-4 spike-conversion question
included); (c) any submission (PR, verified badge) is the user's
outward step. The adapter commit is the checkpoint before (a).

OPERATIONAL NOTE 2026-09-28, widened 2026-09-30: disk-space compaction
gzips every file over 10MB anywhere under results/ (2.7GB -> ~0.4GB;
evidence preserved, nothing deleted). Paired-comparison scripts reading
arms' .rows.jsonl / result .json must gunzip them first. Stale Kaggle
staging copies (kaggle/dist/dataset-loopescape, dataset-submit) were
deleted; scripts/package_kaggle_dataset.py regenerates staging.

This is the compact operational record for FlyGI. The detailed chronological
diary from repository creation through the second Kaggle submission remains
recoverable from Git history at commit `c3774e2`; it was deliberately pruned on
2026-09-22 so future sessions can recover the actual project state quickly.

Read this file before planning or editing. Reconcile it with `git status`, the
latest commits, active processes, and immutable result artifacts after every
handoff or context reset. Update it after each meaningful result, decision,
blocker, submission, or change in ordered next work. Never record secrets.

## Task 3 (FlyBench) OPENED: due-diligence delta measured; execution is user-side -- 2026-10-01

Opened immediately after Task 2 closed, per the program order. Full
record: docs/arenas/task3_flybench/due_diligence_delta.md. Measured:

- flybench is NOT on PyPI (404) -- survey corrected; install is
  `pip install -e .` from the GitHub clone (read-only cloned in-cloud:
  v0.2.1, commit 3052ce5). The project moved since the survey:
  terminal-aware LIF is a second verified mechanism row, a flyvis-eye
  task showed the reference loom escape was hand-fed, and a closed-loop
  escape task exists that nobody passes. Our MB-calibration angle
  remains unclaimed.
- neuprint.janelia.org still HTTP 000 in-cloud (AF-2 stands).
- NEW measured blocker: this environment's execution policy DENIES
  installing/running third-party code, so even the no-fetch toy suite
  cannot be verified here. Reading the clone is permitted and the
  adapter-relevant interface facts are recorded (Simulator(connectome,
  params).run -> SPIKE-only SimResult; verify-adapter CLI; open
  division wants n_free_parameters + fit_data, benchmark-fitted params
  ineligible). New rows AF-4..AF-6.

DECISION RESOLVED same day: the USER explicitly authorized third-party
execution in this container ("Do #2. I authorize."). Measured
immediately after: `pip install -e .` works, `flybench toy` builds the
3,792-neuron / 45,343-edge synthetic connectome, and `flybench run -c
toy` completes in ~2 min with the REFERENCE simulator at score 0.93 /
graded 0.94 / 24 of 30 tasks (6 skipped: toy has no nerve-cord
readouts; flygym/flyvis extras not installed). AF-6 flipped to
CONFIRMED-under-authorization. The adapter kill test is registered
BEFORE any adapter code: docs/arenas/task3_flybench/killtest_design.md
+ EXPERIMENTS.yaml H-FLYGI-FLYBENCH-ADAPTER (open) -- premise: our
class-2 SpikingNetwork, UNMODIFIED, behind their Simulator contract
with declared plumbing only (derived unit bridge w_scale =
w_syn*gain/tau_m, shared Shiu constants, suprathreshold-pulse emulation
of their forced Poisson stimuli); trivial alternative: their reference
LIF's measured toy row; PASS = verify-adapter zero defects AND the five
canonical core reflexes pass at the derived w_scale (fallback: the
reference's own declared gain-sweep freedom, 1 free parameter).
neuprint stays blocked (AF-2), so MaleCNS rows remain local-only
regardless.

## Task 2 (DSEC-Flow): registered, built, data-gated -- COMPLETE cloud-side -- 2026-10-01

Resumed in a new session per the pause entry below; HANDOFF.md's resume
order followed exactly. All four of its Task-2 next steps are done and
pushed (branch claude/admiring-goldberg-wtqkbg):

- RECONCILED first, as flagged: the truncated, unreviewed
  docs/arenas/task2_dsec/KILL_TEST.md draft is superseded by the
  complete, FROZEN registration docs/arenas/task2_dsec_flow/
  killtest_design.md (directory settled as task2_dsec_flow/, parallel
  to task1_arc_paper/; old directory removed). Frozen before any data
  contact: arms (real / uniform-tau twin / 3x degree-preserving rewire
  / zero-flow EPE-context / GT-median context / event-centroid-shift
  KILL COMPARATOR / lattice cross-correlation ceiling), the pass/kill
  rule (real must beat event-argmax AND the rewire on per-window mean
  2D angular error, one-sided paired sign tests p<0.05 plus lower
  medians), the 250-window cap with temporal 20% calibration prefix,
  the BLOCKED-vs-KILL distinction (<30 evaluable eval windows = not a
  verdict), and the dt grid {10,20,50,100} ms with per-arm matched
  calibration freedom. Registered as EXPERIMENTS.yaml
  H-T4T5-DSEC-DIRECTION (open); ASSUMPTIONS.md gained AD-6 (polarity
  running-sum as pseudo-luminance), AD-7 (central-crop isotropic
  binning), AD-8 (fc25-measured subtype preferred directions as the
  fixed vote basis) and updated AD-3..AD-5.
- scripts/arenas/dsec_metrics.py -- the connectome-independent half,
  MEASURED in-cloud on synthetic flow: 6/6 selftest checks, 19 tests.
  EPE / 2D+3D angular error / 1-2-3PE, the DSEC-KITTI 16-bit flow-PNG
  codec in pure numpy+zlib (round trip exact to the 1/128 px quantum,
  all five PNG filters), zero-flow and GT-median baselines. numpy +
  stdlib only, so the local run needs no imaging dependency.
- scripts/arenas/dsec_killtest.py -- the data-gated harness against
  the real fc2/fc25 interfaces (build_patch, GradedFlyvisNetwork,
  trained_weight_matrix/trained_table, verbatim trained_subset gain,
  degree_preserving_rewire). MEASURED in-cloud: it exits 3 with a
  BLOCKED report correctly naming this container's missing
  prerequisites (compiled runtime, fc25 results file, h5py/pyarrow,
  data root) -- the egress blocker recorded in the pause entry stands.
  Its 13 pure-plumbing tests (geometry, binning, comparators, vote DC
  cancellation, GT gates, exact sign test, frozen-constant assertions)
  pass; 32 total across both Task-2 suites.
- docs/arenas/task2_dsec_flow/runbook.md -- the user's local steps:
  precondition check, ~4 GB single-sequence download (thun_00_a
  primary), the one command, and the report-back protocol.

Task 2 is COMPLETE by the HANDOFF definition (harness, design, runbook,
registration committed; blocker surfaced). The MEASUREMENT is the
user's local run; on report-back the hypothesis closes from the JSON
(supported / refuted / blocked) and the registry + this file update.
Expected tier, base rate stated: 0 for 12, and the nearest precedent
(H-T4T5-CLASS25-MOTION) measured the rewire ABOVE real on ARC frames.
Next per the program order: Task 3 (FlyBench) opens with its
due-diligence delta.

## SESSION PAUSED for resume elsewhere -- 2026-10-01

The user paused the arena-program session and will resume in a new one.
RESUME FROM docs/arenas/HANDOFF.md. It records the exact pause point:
Task 1 is complete on the Claude side and the user's runbook steps are
pending. Task 2 (DSEC-Flow) has its due diligence done and its build
paused.

Task 2 measured blocker (2026-10-01): the cloud container's egress
returned HTTP 000 for dsec.ifi.uzh.ch, download.ifi.uzh.ch,
drive.google.com (MVSEC) and neuprint.janelia.org. GitHub raw returned
200. The container also lacks the compiled runtime and the flyvis
checkpoints. So the DSEC kill test runs on the local machine, or in the
cloud after a network-allowlist change. The planned next steps are
recorded in HANDOFF.md: build and verify the connectome-independent
metrics/baselines module in the cloud, freeze the kill-test design and
pass/kill rule, write the data-gated harness against the fc2/fc25
interfaces, write the runbook, and register the hypothesis.

The full ten-agent due-diligence record is now preserved in the repo as
docs/arenas/due_diligence_20260930.md. It previously existed only in
session temp files.

## Task 1 (ARC Paper Track): full package built -- 2026-10-01

The complete submission package is in docs/arenas/task1_arc_paper/,
produced under adversarial verification at every stage:

- factsheet.md: every number checked against the durable record by a
  four-agent pass (wf_7e405dd9-8a8); corrections applied (base rate is
  0-for-12; coordinate-HEAD vs H-COORDINATE-CONVENTION disambiguated;
  three learning nulls, not four; partial-lead phrasing; NOT-USEFUL
  fidelity scoping). Record hygiene fixed en route: the registry's
  duplicate status key on H-MB-CLASS2-ASSOCIATION removed (YAML parses,
  status=refuted); LEAGUE.md's stale H-EFFERENCE row flagged for local
  regeneration; AP-6 CONFIRMED (MaleCNS is CC BY 4.0 per README).
- writeup.md: the judged artifact (title + subtitle + 1,429-word body),
  built by a 9-agent workflow (three angles, three judge lenses,
  synthesis, two gates: wf_6cc4b6d7-f47); all four gate findings applied.
  Headline: "The Grammar Scaffold Transferred Zero. The Fly's Eye Map
  Survived Its Control."
- media/: cover + three figures (ladder-vs-hidden, verdict matrix,
  controls-both-ways), palette-validated, rendered 2x from committed HTML
  sources; all numbers from the factsheet.
- public_notebook.ipynb: 9-cell public companion (narrative + RECORD
  dict + ladder chart + guarded spectral-radius reproduction cell).
- linkedin_post.md + x_post.md: announcement drafts, posting gated on
  repo-public.
- submission_runbook.md + public_release_checklist.md: the user-executed
  half (this container has no Kaggle credentials and the rules pages are
  egress-blocked). Step 0 verifies the OPEN register rows (deadline
  11-08 vs 11-09, CC0/MIT-0 wording, same-account rule). README's stale
  milestone-era results section replaced with the current verdict matrix
  and submission record.

Remaining on Task 1, all user-side: runbook steps 0-7 (verify rules,
join paper-track comp, license decision, repo public, notebook upload,
writeup submit before 2026-11-08, posts). Claude-side artifacts are
complete pending one final outward-artifact compliance check in flight.

## ARENA PROGRAM OPENED: plan + assumptions register committed -- 2026-09-30

User directive: execute all eight ranked arenas from
docs/next_arenas_survey_20260930.md, top rank first, one at a time, with
due diligence before each, continuous documentation, and tracked
assumptions. Task 1 (ARC Paper Track) must also yield LinkedIn + X post
drafts leading to the (to-become-public) GitHub repo.

Due diligence ran first: a ten-agent web-verification workflow
(wf_77415764-bf9), all ten arenas checked. Plan: docs/arenas/PLAN.md.
Register: docs/arenas/ASSUMPTIONS.md. The findings that reshape the work:

- Paper Track judged artifact is a <=1,500-word KAGGLE WRITEUP with a
  required Media Gallery and attached PUBLIC notebook, linked to a real
  code submission, from the SAME account (megusalexandrus). "The code
  submission need not achieve a high score" -- our three 0.15s qualify.
  Deadline 2026-11-09 per Kaggle (one source says 11-08; planning to
  11-08). Prize eligibility wants CC0/MIT-0 on submitter code -- current
  LICENSE is plain MIT; relicensing is the user's call. Precedent:
  CompressARC placed 3rd at ~20% accuracy; no pure negative-results paper
  has ever placed -- nulls go in as controls, not the headline.
- DSEC-Flow: open, rolling; floor on the board is MultiCM EPE 3.47; 6-month
  report-or-deleted rule; institutional-email account requirement.
- FlyBench: we would be external contributor #1; MaleCNS fetch is
  anonymous via neuprint; verified-badge requires maintainer-rerunnable
  stack; substrate differs from ours (176,422/6.29M vs our 166,700/24.99M).
- NeuroBench: no active challenge; leaderboard is maintainer-gated
  (relationship, not API). Brain-Score: rolling, pure-NumPy precedent
  (pixels/gabor/hmax live on the 2026 board), submission = public PR.
- e-nose: no open competition anywhere; paper route; UCI corpus has a
  published integrity critique (Dennler 2022); Aug-2026 engineered
  olfactory-SNN paper is the near-competitor.
- MLPerf Tiny: v1.4 done July 2026, v1.5 unannounced (~H1 2027 inferred);
  an individual submitter exists, path is real; join WG 8+ weeks early.
- NEW hard date the survey missed: IJCNN 2027 competition PROPOSALS due
  2026-11-30 (Cape Town, Jun 2027; scope includes neuromorphic + embodied).

Container constraints measured: no Kaggle credentials, no compiled MaleCNS
runtime -- all Kaggle/browser/outward steps are prepared here, executed by
the user via runbooks. Task 1 is ACTIVE; next entry when its artifacts land.

## Fly-limit question answered; external survey recorded -- 2026-09-30

The user asked whether anything else is extractable from the fly and, if the
limit is reached, which other challenges/benchmarks the fly could enter. Full
answer with tiers and links: docs/next_arenas_survey_20260930.md. Compressed:

- ON ARC, THE LIMIT IS MEASURED, NOT ASSUMED. Two earned fly-negatives (MB
  association, T4/T5 motion decode -- both validated, both lost to their
  degree-preserving rewires), the rest of the inventory closed by benchmark
  failure or no-native-mapping, and the score track's non-LLM levers
  exhausted by preregistered gates. Remaining fly-side levers are science,
  not score: class-3 ingredients (see FlyBench below) and LC at class 2.
- SOURCED (two-agent web survey, 2026-09-30): a Sept-2026 viral wave of
  ~50+ "MaleCNS plays Doom/Mario/Beat Saber" projects commoditized the game
  demo; NOBODY is on ARC (FlyGI appears unique); nobody anywhere holds a
  control-backed "untrained innate wiring does useful task work" claim, and
  three published lines cut against it (digital sphinx, fly-hero's
  random-network readout, connectome-reservoir nulls). Our audited record --
  positives AND negatives -- is therefore the asset.
- FLYBENCH (github.com/brandoncho369/flybench, VERIFIED by local clone):
  36 pre-registered reflex tasks on FlyWire+MaleCNS with shuffled-wiring
  controls, same epistemics as this repo, aimed at biology not tasks. Its
  no-free-parameter mechanisms (terminal-aware synapses: MaleCNS core tier
  0.57->0.90; spike-frequency adaptation) are exactly "physiological
  ingredients outside the swept space" -- the registered reopen condition
  for our ring verdict. Its PN-broadcast finding predicts plain LIF cannot
  sparse-code the AL; our Litwin-Kumar-calibrated pass is the counterpoint.
- RANKED NEXT ARENAS (top of eight; details+kill tests in the doc):
  1) ARC Prize 2026 Paper Track (sourced deadline 2026-11-09, re-verify) --
  near-zero build, the record is the paper; 2) DSEC-Flow event-camera
  optical flow (standing; T4/T5's native input; claim must be tiered
  "connectome-constrained, physiology-fitted", frozen counts are DSI 0.042);
  3) submit to FlyBench; 4) NeuroBench; 5) Brain-Score oddball; 6) e-nose /
  gas-sensor drift for AL+MB. Not worth doing: more game demos, robotics
  stacks, LLM leaderboards.

Arena choice and any LLM-hybrid scope decision remain the user's. No code,
config, or experiment changed in this checkpoint.

## Search layer: gated and NOT shipped; queue complete -- 2026-09-30

The full gate sequence ran: gate (a) FAILED at 600-action rows (six
measured losses -- the layer burned budget on unfinishable searches),
one mechanism-targeted amendment was registered and implemented
(budget-aware engagement, immutable numbers untouched), the battery
byte-identity re-run PASSED perfectly (75/75 rows identical to fap11,
zero engagements), and the GATEWAY GATE FAILED at 28.459550 vs the
28.742260 bar (engaged searches cost more than they won in the
35-minute window). Per the registration -- no further amendments --
the layer does not ship. It stays in the tree, default-off, as a
measured component: real mechanism, harmless idle, unprofitable in the
measurable window; the uncapped-rerun upside is expected-tier only.
With this, the score track's non-LLM levers are exhausted by
measurement: three 0.15 submissions killed grammar transfer, and the
one transferable mechanism failed its own preregistered gate. What
remains score-side is the LLM-hybrid scope decision (the user's) or
banking 0.15. En route, two harness repairs: the macOS tmp reaper had
gutted /tmp/flygi_rerun (rebuilt from vendor + slim registration), and
an adapter NameError in the budget wiring that 708 tests missed
because no smoke test drives choose_action's turn path with a live
policy (fixed, noted as a coverage gap).

## H-ONLINE-SEARCH layer BUILT; cd82 and sp80 convert offline -- 2026-09-30

The preregistered consequence of the 11/25 premise result is implemented:
`src/flygi/controller/search_layer.py` (OnlineSearchLayer, the FAP executor's
seating protocol, consulted by `policy.py` only AFTER the FAP override
abstains; engineered scaffold, no fly content). Knob `controller.search_layer`
(default false, byte-identical off and while idle -- unit-measured) is wired
through the config loader, `scripts/evaluate_state_graph.py`,
`kaggle/agent/my_agent.py` (FLYGI_PREFLIGHT `search_layer` field, FLYGI_DIAG
counters) and policy diagnostics (`search_engaged_turns`,
`search_programs_found`, `search_errors`, `search_banned`). New configs:
`configs/combo_fap_search.yaml`, `configs/combo_light_fap_search.yaml`
(one-line deltas). Tests: `tests/test_search_layer.py` (21); full suite 705
passed.

Preregistered numbers implemented as immutable: engage after 75 observed
turns without a level advance, <= 1,500 emitted actions per level then
permanent abstention for that level, click cap 12. Mechanism notes, all
labelled at the code site:

- ASSUMPTION: observe() calls approximate reconciled turns; the stuck counter
  restarts on level advances ONLY. The build directive's suggested
  approximation (also restart on forced resets) was tried first and REFUTED
  by measurement: sp80's champion dies every ~31 turns, so that counter never
  reached 75 in 2,600 actions; the preregistered signal is "no level advance
  for 75 reconciled turns" and a forced reset is not an advance.
- Replay is skipped whenever the live state's fingerprint equals the next
  target's (same state identity as the instrument). This is what fits the
  budget: offline cd82 needed 2,411 env steps under replay-per-branch;
  online conversion took ~1,151 emitted actions.
- ASSUMPTION: the timer border-line rule is learned passively from the
  champion's own pre-engagement transitions instead of the instrument's
  24-step seeded walk. Check: learned masks matched the instrument's on all
  four probed games (cd82 rows [63], sp80 rows [0], lp85 cols [0], s5i5
  rows [63]).
- Wake handling: the first post-reset step is re-emitted once when the
  masked state did not change (the instrument's probe-once wake, expressed
  under the search's state identity).
- MEASURED: the engine accepts a voluntary RESET on active frames while
  never listing action 0 in available_actions (offline arcade probe).

MEASURED (scratch policy-style loop, minimal ControllerConfig + the layer
only -- no click head, tags, FAP or fly -- seed 0, 2,600-action budget):

- cd82: level 1 at action 1,226 (engaged at 75; program found and banked;
  0 errors, 0 drifts). The known-findable 5-step program converts ONLINE.
- sp80: level 1 at action 727 (13 deaths absorbed mid-search).
- vc33, lp85: level 1 fell to the bare champion before engagement mattered;
  on lp85 level 2 the layer engaged, spent exactly 1,500, abstained
  permanently, zero errors.
- s5i5: budget-exhausted without a find (offline needed 11,993 env steps;
  unreachable at 1,500). Of the gate's currently-dead candidates: cd82
  converts, sp80 converted here, s5i5 does not, and sk48 (121,981 offline
  steps) will not.

BLOCKER for gate (a): `evaluate_random_baseline.evaluate_one` treats a
voluntary RESET as protocol-illegal and fails the row (measured: the engine
itself accepts it), so the 75-row battery cannot run with search_layer=true
until that Gate-0 legality contract is amended (one declared change, outside
this build's allowed edit surface). Verification above therefore used a
scratch policy-style loop (env.step directly), not evaluate_one. Next:
amend the harness rule, then run the preregistered battery + gateway gates
vs sg-combo-fap11.

## Ring-test PEN pattern bug fixed — 2026-09-30

`tests/test_subcircuit.py` (TestRealRing) selected the EB-PB ring with exact
patterns `("EPG", "PEN_a", "PEN_b", "Delta7", "PEG")`. `select_nodes` matches
with `fnmatch.fnmatchcase` and the MaleCNS type names are `PEN_a(PEN1)` /
`PEN_b(PEN2)`, so both PEN patterns matched ZERO nodes: the "ring" the test
verified was 106 neurons (46 EPG + 42 Delta7 + 18 PEG) with no PEN cells,
and it passed anyway because it only asserted node-count consistency,
nnz > 1000, and the sign conventions. MEASURED 2026-09-29 (recorded in the
scripts/benchmarks/fc2_eb_ring.py registration header, which flagged the
discrepancy): corrected patterns `("EPG", "PEN_a*", "PEN_b*", "Delta7",
"PEG")` select 148 neurons, adding 20 PEN_a(PEN1) + 22 PEN_b(PEN2), all
acetylcholine/excitatory.

Fixed 2026-09-30: the test now uses the wildcard patterns, asserts
130 <= node_count <= 170 (148 in this compilation), and asserts both PEN
populations are non-empty and 100% acetylcholine, so a regression to the
PEN-less selection fails loudly. Blast-radius audit (code reading, this
date):

- scripts/benchmarks/fc2_eb_ring.py used the corrected patterns from
  registration onward — the class-2 EB verdict (FAILED, 148-neuron ring)
  is unaffected.
- Class-1 scripts/benchmarks/cx_ring.py matches exact full type names
  (`types == "PEN_a(PEN1)"`) on the full graph — unaffected.
- src/flygi/arc/factory.py compass gain (H-CX-CALIBRATION) uses
  `np.char.startswith`, and the prefix "PEN_a" DOES match "PEN_a(PEN1)" —
  unaffected. (Noted while auditing: its "EPG" prefix also catches the 4
  EPGt cells, a known difference from the fc2 registered member list; left
  as-is.)
- The only artifacts resting on the PEN-less selection were the test
  itself and this file's "ring anatomy verified" phrase (2026-09-29 Engine
  status), now annotated in place. No repo doc carries a "106-neuron ring"
  claim elsewhere (grepped 106 / Delta7 / PEN_a across md/yaml/docs).

Executed locally 2026-09-30 (user-run, reported back to the session; the
cloud container itself has no data/processed runtime): the fixed test file
from this branch, run from the repo root against the local runtime, passed
all 3 tests -- the 148-neuron selection, the non-empty cholinergic PEN
populations, and the sign conventions all hold on the real data.

## Thirteen-archetype candidate SUBMITTED: 56683298 — 2026-09-29 17:28 UTC

The user explicitly requested submission of the current COMPLETE candidate,
while Claude Code continues independent work. The submission snapshot is
`ec014da3db77f19e5a9d4787fd2e6926a91217e1`, exported with `git archive` to
`/private/tmp/flygi-submit-20260929.TryXTD/`. Build, test, and upload from
that isolated snapshot only; do not capture subsequent edits, touch Claude's
processes, or include `.fly-or-fake-work/`. No policy/config tuning is part
of this operation. The completed gate is the recorded 35-minute official
competition-mode result 28.742259837750854, 73 levels, four full wins.

Measured remote checks: submissions 56620463 and 56650224 are both COMPLETE
at 0.15. The private runtime dataset is still version 8. Its downloaded
`controller.yaml` is byte-identical to the frozen `combo_light_fap.yaml`
(SHA-256 `639f94494cfca094181cbbeef19916baa52f5643a394767b5d7568f01096672d`),
and its config SHA-256 is
`3d5d17bfcdfeaba40437d899a5ef7149f7ca9aeaef7aca609eb1563fb46a9d38`.
No dataset re-upload was needed; the hosted notebook preflight verified
these assets. The first unversioned provenance download returned 404; the
explicit version-8 request succeeded. Credentials were not logged.

Validation before submission: frozen-source tests, embedded-source/asset
verification, then a private notebook upload and the ordinary hosted
preflight. The archive excludes ignored fixtures;
its first suite run had seven missing-fixture failures and seven skips.
The existing recognizer-frame and retinotopy NPZ fixtures were copied into
the temporary snapshot for a rerun; no source changes were made. The rerun
passed **672 tests in 47.58 seconds** (`PYTHONPATH=<snapshot>/src
<repo>/.venv/bin/python -m pytest -q --tb=short`, in the snapshot).

Measured package audit: all 73 embedded Python files match the frozen
source and embedded manifest hashes; all thirteen archetypes instantiate
from the extracted embedded source with the downloaded hosted controller.
Every hosted dataset provenance digest matches the corresponding local
runtime/config. Notebook SHA-256:
`4e2ca946ea5f2cd685af2209b0340a900b94c673ba117c8ccddd4fd116860756`;
embedded zip SHA-256:
`3ffcb05533f76aeaad632dfb09f970524a12c1fa3efe2f6672e2a3297991b3ae`.
The existing notebook in the shared checkout is stale (two-archetype
source); it is deliberately untouched and MUST NOT be used for this upload.

Kaggle accepted the isolated notebook upload as private CPU,
internet-disabled **version 12**, with no invalid sources or upload error.
Dataset version 8 was reused; no dataset was changed. The hosted ordinary
run completed successfully. Downloaded notebook cell sources match the
frozen notebook exactly; `FLYGI_PREFLIGHT` reports verified=true,
mode=controller-light, fap_library=true, deploy_fly_tiebreak=false,
neuronal_dynamics_active=false, 166,700 nodes, 24,994,595 edges, K=4,
deadline 100, legacy_xy_flat, and retino_tags. Verified array hashes match
the hosted dataset provenance. The ordinary output is the expected 1x4
placeholder parquet, NOT a hidden-game score.

Hosted log SHA-256:
`d8bce9baeee9af7654f763d2b540a86d300dc570679e66c1a2118f46f280fc94`;
placeholder SHA-256:
`71bfd543030e339d87bd9ff744d466218398a1259650b2c255626d27049c88bb`.
Evidence downloads remain under the temporary snapshot's `hosted-assets/`,
`hosted-v12/`, and `hosted-output/`; Kaggle v12 is the durable hosted source.

**Submitted exactly once:** Kaggle returned submission **56683298** for
notebook v12 at `2026-09-29 17:28:21.193 UTC`. An independent status query
confirms `SubmissionStatus.PENDING`, empty public score, and no error.
Executed the authenticated Python
API equivalent of `kaggle competitions submit arc-prize-2026-arc-agi-3
-k megusalexandrus/flygi-arc-agi-3 -v 12 -f submission.parquet -m <description>`
via `api.competition_submit_code(...)`. The description explicitly names
the thirteen Python archetypes, neuronal dynamics OFF, source ec014da,
672 tests, local gateway 28.742260, dataset v8, and unknown hidden transfer.
DO NOT retry this submission. No subsequent Claude source changes or
untracked files entered the uploaded snapshot.

Claim boundary: this is the explicitly authorized ENGINEERING candidate
(thirteen Python archetype parsers/planners plus controller-light, neuronal
dynamics OFF), not evidence of connectome computation. Hidden transfer and
a new leaderboard score are unknown. Next: check submission 56683298 on a
future status request, report the hidden score separately from the local
28.7423, and leave Claude's ongoing experiments untouched. No automatic
monitor or additional submission is scheduled.

## Dead games fall to hand-derived programs: H-FAP-PROGRAMS PASSED -- 2026-09-27

The user directed running every open fly-inventory item ("Do em all"). First
result, and the largest score-relevant finding since the six-zeros fix: the
forensics' "short exact program" claim is now MEASURED TRUE on both
template-flavour dead games, with the actual programs recorded.

**ft09, solved through level 2.** The screen is four 3x3 tile grids; each
grid's centre glyph is a miniature of its own grid (glyph colour 2 = tile 9,
glyph 0 = tile 8/the glyph-centre colour; verified exactly on all three
reference grids). The bordered grid's glyph mismatches its own all-9 surround:
it is the goal, and clicking the four tiles its 0-cells prescribe completes
level 1 in FOUR actions (score 0->1). Level 2 states the same rule with two
glyphs and marked colour c; seven more clicks complete it (score 1->2, eleven
actions cumulative). Every 600-action battery row ever run on ft09 scored 0.

**sc25, solved through level 1.** Punch the die's displayed pip pattern into
the 3x3 board (0-cells mark the pips; clicking a 2-cell costs a timer tick, a
0-cell does not), the oversized track marker then shrinks to 2x2, passes the
track notch, and rolling it left (action 3) into the docking box completes
level 1 (~17 actions, score 0->1).

**Engine quirk, measured (sc25 only; absent in ft09):** the first action after
every RESET -- including episode start -- is swallowed completely; identical
frames regardless of which action wakes it. Deployed agents burn one action
per sc25 life and the consequence head records that action as effect-free.

**Blind search does not replace goal reading.** BFS over the offline arcade
(scripts/fap_bfs_probe.py): sc25's directional-only space is 19 states,
exhausted, no win; with 15 salient click targets the space exceeds 5,031
states with no win by the 3,000-node cap. The programs must be DERIVED from
the displayed goal -- the recognize-then-release shape the FAP library plans.

**Scope, per the first principle:** these programs are engineered scaffold,
recorded as such (like taxis). The registered fly seat was RECOGNITION
(H-LC-RECOGNIZER): whether LC/LPLC or lateral-horn population codes identify
a never-seen game's class. Instruments: scripts/fap_program_premise.py
(scripted execution + frame dumps), scripts/fap_bfs_probe.py (program
search); programs recorded in results/diagnostics/fap_programs.json and the
registry entry.

## Tracks 1-4-5 (user-approved order) -- 2026-09-30

- [done] Track 1, H-ONLINE-SEARCH: BAR MET DECISIVELY -- 11 of 25
  games fall to bounded blind search (bar >=5), program lengths 3-15,
  zero errors. Bonus instrument findings: g50t shares sc25's
  post-reset swallow (new); ft09's null under the click cap is a
  candidate-RANKING null (winning clicks at ranks 24-31, cap 12);
  lf52/su15/tn36 collapse under the declared timer mask (manual glance
  owed); seven games exhaust the budget at 6.3k-8.8k states. The
  preregistered consequence is now due: BUILD the online layer and
  gate it through battery + gateway. [up next]
- [done 2026-09-30] H-T4T5-CLASS25-MOTION: REFUTED -- the second
  attributed fly-negative, same decomposition as the MB. Real 0.3875
  held-out (above chance every seed: the validated patch carries real
  direction signal) but uniform-tau matches (0.3917) and the
  degree-preserving rewire exceeds it (0.4306); engineered matcher
  1.0000 ceiling. T4/T5: NOT USEFUL for ARC motion decoding at
  validated fidelity. The definitive answer now has TWO earned
  not-useful verdicts (MB, T4/T5) and one useful component (eye-map).
- [done] Track 4, class 2.5: T4/T5 DS PASSES ITS BAND -- DSI 0.3216,
  T4 tiles four directions, T5 three, on trained flyvis ensemble
  parameters with verified provenance. Attribution, two-sided: trained
  per-pair strengths carry the pass (0.04 -> 0.33); type-mean taus add
  nothing (uniform-tau at trained strengths: 0.3365). T4/T5 is
  VALIDATED and re-enters the pipeline; its requirement-2/3 ARC run is
  owed. Dossier corrections recorded in the registry.
- [done] Track 5, the program write-up, published (private artifact):
  https://claude.ai/artifact/QoUf16jCT2R1offKQLx9Zp -- the four
  requirements, both fidelity classes' pass maps, the MB decomposition,
  the boundary, and the two live levers. To be updated in place when
  tracks 1 and 4 land.
- Context fact recorded: submission 56683298 (thirteen archetypes)
  scored 0.15 -- the third consecutive floor; game-specific grammars
  transfer zero to the hidden set, measured three times.

## PROGRAM: fidelity class 2 -- temporal/spiking dynamics -- opened 2026-09-29

User directive: research and implement the next fidelity class. The class-1
verdict located the wall exactly: no delay lines (kills T4/T5 direction
selectivity), no sparse-coding regime (kills the KC code), no movable bump
(kills the compass). Class 2 supplies precisely the missing physics:
per-type TEMPORAL dynamics on the same anatomy.

**Design (registered before implementation):**
- Engine: leaky-integrate-and-fire on extracted SUBCIRCUITS of the compiled
  graph (optic-lobe patch, MB, CX ring) -- the field's standard practice
  (whole-brain LIF: Shiu et al. 2024 Nature; optic lobe with per-type time
  constants reproducing T4/T5 DS: Lappalainen et al. 2024 Nature; spiking
  EB ring from anatomy: Kakaria & de Bivort 2017). Subcircuits make spiking
  tractable: MB ~2e4 nodes, CX ~1e3, an optic-lobe column patch ~1e4.
- Parameters: per-type membrane/synaptic time constants and thresholds,
  each labelled ESTABLISHED (with source) or ASSUMED (with sweep range).
  Signs stay the measured-NT convention.
- Benchmarks: THE SAME preregistered bands as class 1 (they are the
  published biology; nothing gets re-tuned) -- T4/T5 direction tiling, KC
  sparse fraction 3-15%, EB movable persistent bump -- now swept over the
  assumed-parameter space instead of gain x leak.
- Verdict rule unchanged: a module that passes its benchmark at class 2
  re-enters requirement 2/3 (input gates, ARC native-function tests with
  controls); a module that fails across the assumed-parameter sweep stays
  UNVALIDATABLE with the wall moved one class deeper.

### Statuses
- [done] Research pass (docs/fidelity2/): Shiu 2024 canonical LIF verified
  against paper AND code (v_rest=v_reset=-52mV, v_th=-45mV, tau_m=20ms,
  tau_syn=5ms, delay 1.8ms, refractory 2.2ms, w_syn=0.275mV the only free
  parameter -- to be REFIT on MaleCNS, not copied; zero-baseline silence
  is structural and flagged for the bump/APL); Lappalainen 2024 verified:
  the DS-sufficient model is a GRADED per-type leaky integrator with
  relu-at-synapse, fast/slow type classification anchored to Behnia 2014
  filter peaks, ranked blockers led by CT1-as-point-neuron; Kakaria & de
  Bivort 2017 ring regime (Delta7 inhibition ~75% of excitation is
  load-bearing; the working regime is narrow, calibration of one scalar
  per sign class mandatory) and the Litwin-Kumar 2017 KC threshold
  procedure with the WTA-is-correct-physiology trap documented.
- [done] Engine: subcircuit extraction (signed raw counts, memory-mapped
  scan; ring anatomy verified) + per-type LIF with graded units; 12 tests.
  [CORRECTED 2026-09-30: "ring anatomy verified" overstated. The ring
  test's exact patterns "PEN_a"/"PEN_b" matched ZERO nodes (the MaleCNS
  types are "PEN_a(PEN1)"/"PEN_b(PEN2)"), so the selection the test
  verified was 106 EPG+Delta7+PEG cells with NO PEN population. The
  fc2_eb_ring.py benchmark used corrected wildcard patterns from
  registration (148 neurons), so the class-2 EB verdict below is
  unaffected. Test fixed; see the 2026-09-30 entry.]
- [done] Class-2 benchmark sweeps -- THE SPLIT VERDICT, 2026-09-29:
  * KC SPARSE CODING: PASSED WITH ATTRIBUTION -- the program's first
    dynamical validation. MaleCNS MB subcircuit (627 PN / 4,064 KC / 2
    graded APL / 97 MBON, 770,711 signed-count edges), Litwin-Kumar
    threshold calibration declared on a calibration odor set, SCORED
    HELD-OUT: median active fraction 0.0741 in the [0.03, 0.15] band;
    Lin/APL densification control passes (+0.0098, APL load-bearing
    exactly on the dense stimuli); both trivial alternatives sit at
    1.0000 dense (the class-1 phenotype reproduced and cured by
    threshold + claw coincidence + graded APL); 10/12 configs pass, the
    two failures being the doc's predicted weak-APL corner.
  * T4/T5 DIRECTION SELECTIVITY: FAILED at class-2-frozen -- pooled
    median DSI 0.042 vs the 0.30 band, and the uniform-tau trivial
    alternative MATCHES the heterogeneous model: with frozen
    (untrained) per-pair strengths and resting potentials, per-type
    time constants alone do not produce the correlator on raw MaleCNS
    counts (consistent with flyvis needing TRAINED parameters and with
    Borst 2025). Recorded as a limit of the frozen-parameter recipe;
    the located next lever is the released trained flyvis ensemble
    (class 2.5). One readout-instrument repair fully recorded (DC-
    dominated whole-sweep integral replaced by a crossing-locked
    window BEFORE its numbers were seen; both readouts saved).
  * EB MOVABLE BUMP: FAILED decisively -- 210 configurations (Shiu-
    canonical LIF; per-sign-class scaling incl. the effective-I/E~6.4
    anchor; tonic-drive knob), 155 alive and EVERY one delocalized
    (min circvar 0.853 vs band 0.6), all four seed angles settling at
    ONE fixed point (~192 deg): the class-1 position-independence is
    REPRODUCED at spiking fidelity. The shuffled ring behaves
    comparably. Measured at two fidelity classes: this compiled ring
    holds activity, not position.
- [done] Requirement 2+3 for the MB -- THE PROGRAM'S FINAL VERDICT,
  2026-09-29 (H-MB-CLASS2-ASSOCIATION: refuted). Input gates PASSED
  (PN share of KC drive 62-87% vs the 5% bar). Held-out one-shot
  association: real MB 0.600 (misses the band, p=0.0775);
  degree-preserving rewired 0.800 -- HIGHER than real, so the specific
  wiring adds nothing beyond degree sequences; shuffled-credit 0.400 --
  real beats it (p=0.019), the depression mechanism genuinely carries
  credit; matched one-shot perceptron 0.917 -- dominates. This is the
  project's FIRST true fly-negative: stated with validated code
  underneath, passing gates, and a working mechanism. Stage B gated
  off per the preregistered staging.

### PROGRAM CLOSED -- the definitive per-module answer [done]
USEFUL: the eye's anatomical map, static (measured, replicated,
deployed). NOT USEFUL, now earned rather than assumed: the mushroom
body for one-shot visual association on ARC at class-2 fidelity -- the
one module whose code validated, whose gates passed, and whose real
wiring then measurably failed to beat its degree-preserving null while
an engineered equivalent dominated. UNVALIDATABLE-AT-THIS-FIDELITY:
T4/T5 (wall at frozen per-pair parameters; class-2.5 lever = trained
flyvis ensemble), the CX ring (position-independent at two fidelity
classes, 210-config sweep), LC coding (sign-inverted at class 1,
untested at class 2), LH (substrate gates), efference (no validated
consumer), SEZ/VNC (no native mapping). Every verdict carries its
protocol; every null its mechanism; every wall its located next lever.
- [planned] Class 2.5 for T4/T5 (trained flyvis ensemble parameters);
  ring verdict stands unless a physiological ingredient outside the
  swept space is identified.

## PROGRAM: the fly-module verdict (four requirements) -- opened 2026-09-29

User directive: implement the four requirements for a definitive per-module
answer, keep this section's statuses current, commit periodically. Status
legend: [done] [in progress] [planned] [up next].

**Scope honesty, recorded at registration:** this is the strongest
COMPUTATIONAL version of the program. The transmitter->sign convention
(ACh+, GABA/Glu/His- via GluCl/HisCl) is ESTABLISHED from literature and
already what the compiled graph uses (measured 2026-09-29: consensus_nt
covers 99.9% of nodes; "heuristic" in old labels means this convention,
not guessed signs). What no computational program can supply: wet-lab
physiology beyond published benchmarks. Verdicts will therefore carry one
of three values per module: USEFUL (beat all controls at a validated
operating point), NOT USEFUL (failed controls despite passing validation
and input gates), or UNVALIDATABLE-AT-THIS-FIDELITY (no operating point
passes the module's biological benchmark -- a model-class limit, recorded
as such).

### Requirement 1 -- physiology and validation [in progress]
- [done] Signs from measured NT annotations (pre-existing; provenance now
  recorded precisely).
- [up next] BENCHMARK SUITE: preregistered pass bands from published fly
  results -- T4/T5 direction selectivity (Maisak 2013), EB bump
  persistence + opposite-signed PEN rotation (Seelig 2015, Turner-Evans
  2017), KC sparseness 5-10% with APL (Turner 2008, Lin 2014), PN gain
  normalization (Olsen-Wilson 2010), LC object-position tuning (Wu 2016).
  - [done] VISUAL group (V1 T4/T5 DSI, Maisak 2013; V2 LC
    object-position RSA, Wu 2016): scripts/benchmarks/visual_motion.py,
    bands preregistered and committed (303b035) BEFORE the sweep; full
    21-point grid MEASURED 2026-09-29 (506s total, ~24s/point), results
    in results/benchmarks/visual_motion.json (gitignored). VERDICT: ZERO
    pass points on either benchmark -- on this grid both published
    visual results are UNVALIDATABLE-AT-THIS-FIDELITY.
    - V1 measured: best pooled per-cell median DSI 0.2878 at gain 0.8 /
      leak 0.1 (band >= 0.30; leak 0.1 column ranges 0.175-0.288 and
      falls with gain; leak 0.3/0.6 collapse to 0.004-0.034). The
      structure criterion fails everywhere: subtype-level DSI only
      0.011-0.049, within-subtype preferred-direction consistency
      0.23-0.28 (chance 0.25), and subtypes do not tile directions (at
      the best point T4a/c/d and T5a/c/d all prefer "up"; T4 never
      exceeds 2 distinct directions at any grid point). So the moderate
      per-cell DSIs are idiosyncratic per-cell asymmetries, not
      subtype-organized direction selectivity. This converts the
      header's expected-tier prediction (frozen rate model, no delay
      lines -> no DS) into a measurement. Secondary, for precision:
      T5-only median DSI on the OFF bar reached 0.33 at the best point
      while T4-only was 0.238; the preregistered pooled band misses.
    - V2 measured: Spearman rho NEGATIVE at all 21 points (-0.203 best,
      at gain 0.8 / leak 0.1, to -0.314; band >= +0.50) -- nearby object
      positions give slightly LESS similar LC/LPLC population vectors
      than distant ones, the opposite sign of retinotopic position
      coding. Valid-pair fraction 1.00 everywhere, so the miss is real,
      not degeneracy. Best single-type rho anywhere: LC11 0.243 (gain
      2.5 / leak 0.6); no type reaches 0.5 at any point.
  - [done] MB+AL group (M1 KC sparse coding, Turner 2008 / Honegger
    2011, APL direction Lin 2014; M2 PN sublinear gain, Olsen & Wilson
    2008 / Olsen, Bhandawat & Wilson 2010 -- the program note's
    "Olsen-Wilson 2010, Nature" conflates these two, recorded as such):
    scripts/benchmarks/mb_al.py, bands preregistered and committed
    (ef3ec87) BEFORE the sweep; full 21-point grid MEASURED 2026-09-29
    (1290.7s total, ~60s/point), results in
    results/benchmarks/mb_al.json (gitignored). Populations measured
    before preregistration: 627 PNs (162 glomerular types), 4,064 KCs,
    2 APL, 2,635 ORNs (53 types); ORN->PN 31,640 edges (all +), PN->KC
    22,581, APL->KC 4,633 (all -).
    - M1 measured: ZERO pass points of 21 (band: median KC active
      fraction in [0.03, 0.15], positive lobe, > max(baseline mean +
      2 sigma, 1e-4), 7 seeded odors, amplitude ladder {0.02..0.5}).
      The KC code is BIMODAL everywhere on the grid: for gain <= 2.0
      with a quiet spontaneous baseline the median fraction is
      0.178-1.0 (nearly every reachable KC weakly active); at gain >=
      2.0 with leak >= 0.3 spontaneous activity saturates (baseline
      threshold 0.97-1.00) and the median is exactly 0. Closest
      approaches to the band from either side: 0.0022 (gain 2.5, leak
      0.1, amp 0.02) and 0.178 (gain 2.0, leak 0.1, amp 0.02); the
      silent-to-dense transition skips the sparse regime entirely,
      consistent with the measured anatomy (KC->KC recurrence 85.3% of
      KC input vs 2.4% APL; H-APL section). On this grid KC sparse
      coding is UNVALIDATABLE-AT-THIS-FIDELITY.
    - M1b measured: APL->KC x4 direction is Lin-consistent at 18/21
      points (every point where KCs responded at all; the x4 median
      never exceeded x1 + 0.005 at any evaluable amplitude); best mean
      sparsification 0.132 at gain 2.0 / leak 0.3. 3 points not
      evaluable (x1 medians all < 0.01). Caveat recorded: at gain 2.5
      / leak 0.3 the x4 network's own quieter baseline yields NONZERO
      x4 medians (up to 0.999) where x1 is 0 -- outside the
      preregistered evaluable set, reported, not scored.
    - M2 measured: 21/21 pass (cognate-PN response over 48 PNs of 10
      driven glomeruli, 492 ORNs): at base intensity 0.2 every grid
      point satisfies R(8x)/R(1x) < 4 with detectable rising response;
      best ratio 1.133 at gain 2.5 / leak 0.3; gains >= 1.5 also pass
      at base 0.05. ATTRIBUTION LIMIT, stated plainly: at base 0.01
      the response is near-linear (ratios 7.4-8.3), so the compression
      that passes the band appears where tanh saturation is active; a
      lone tanh unit -- the named trivial alternative -- would also
      pass. This benchmark validates sublinearity as preregistered but
      does NOT establish AL lateral-inhibition normalization; an
      Olsen-2010-style two-odor mixture test (cognate response with vs
      without co-driving other glomeruli) is the discriminating
      follow-up if M2 ever needs to carry weight.
- [up next] OPERATING-POINT SWEEP: gain x leak grid, every benchmark at
  every point; pass regions and their intersection. The CX record
  predicts the intersection may be empty -- that outcome is itself a
  primary result.
- [planned] Per-type parameters where literature provides them; labelled
  assumptions elsewhere.

### Requirement 1 -- RESULT [done 2026-09-29]
The full 21-point gain x leak grid, three groups, bands preregistered and
never adjusted. Pass map: T4/T5 direction selectivity 0/21 (subtypes
never tile directions -- the frozen rate model has no delay lines; the
moderate per-cell DSIs are idiosyncratic wiring asymmetries); LC
object-position code 0/21 with the SIGN INVERTED at every point; KC
sparse coding 0/21 (dense-or-silent bimodal transition skips the sparse
regime entirely; KC->KC recurrence 85.3% of KC input dominates the
model); EB localized persistent bump 0/21 (fixed-point attractor near
222 deg everywhere alive); opposite-signed PEN rotation 7/21 nominal, 4
with a live bump (1.8/0.3, 1.8/0.6, 2.0/0.3, 2.5/0.3); bump survival
under real bio-eye drive 0/21. The two broad passes are generic
dynamics, stated with their attribution limits in the results: APL
inhibition direction 18/21 (Lin-consistent) and PN sublinearity 21/21
(tanh saturation; the named trivial alternative also passes).

### Requirements 2 and 3 -- CLOSED BY THE PREREGISTERED ORDER [done]
The registration fixed the order benchmark -> gate -> test, with
UNVALIDATABLE terminating at step 1. Measured consequence: T4/T5, LC,
the whole MB stack, and LH (whose substrate is the never-validating
PN->KC code) terminate at step 1 at every operating point. CX passes
only the rotation benchmark at 4 points, but its input gate has no
honest ARC mapping (no heading exists) and its bump dies under the
drive a deployed agent actually receives at all 21 points -- closed as
NO-NATIVE-MAPPING. Efference has no validated consumer. SEZ/VNC motor:
NO-NATIVE-MAPPING as preregistered. No requirement-3 ARC re-run is owed
under the preregistered rules: no module reached step 3.

### Verdict [done 2026-09-29]
USEFUL: the eye's anatomical map, used statically (exempt from dynamics
validation; measured load-bearing twice, deployed). NOT USEFUL: NONE --
no prior null may be stated as a fact about the fly, because the model
never passed the fly's own physiology for those modules. UNVALIDATABLE-
AT-THIS-FIDELITY: every dynamical module, now as a measured theorem
about the model class (frozen uniform tanh rate dynamics on the
anatomical graph), located precisely: no delay lines, no sparse-coding
regime, no movable bump, anywhere in the swept operating space. The
next fidelity class (per-type conductance/spiking with temporal
dynamics) is where a per-module fly verdict becomes possible.
Per module at its validated operating point(s): preregistered ARC-mapped
test vs degree-preserving null vs shuffled control vs engineered
equivalent, matched budgets, held-out games. Prior nulls (MB, hash, CX
steering, LC features, T4/T5, efference) must be RE-RUN under validated
regimes to count.

### Requirement 4 -- the module inventory [done]
Measured from the node table (2026-09-29): optic-lobe encoding stack
(lamina/medulla, 89,403 ol_intrinsic + 6,098 ol_sensory), T4/T5 motion
(13,585), LC/LPLC/visual projection (9,201), visual centrifugal (563),
mushroom body (KC/MBON/DAN/APL), lateral horn (~2,028 typed), central
complex (EPG/PEN/Delta7/PEG/FB), antennal lobe (ORN/PN), JO/efference
(672), ascending (1,846), descending readout (1,314), SEZ/motor
(vnc_* and cb_motor -- flagged: may have no honest ARC mapping; if so
the verdict for them is "no native-function mapping", not a null).

### Verdict [planned]
The per-module matrix with tiers, then the definitive answer with its
stated boundary.

## Thirteen-archetype library: battery 28.63 (81x), gateway 28.74 -- 2026-09-29

Integration complete and every gate passed. The 11-agent integration
fan-out delivered all modules at or above their dossier targets with clean
per-archetype negative audits; registration order is measured load-bearing
(specialized before general: glyph_toggle before glyph_miniature 6/6 vs
4/6, pip_door before pip_punch_roll 4 vs 2); 672 tests pass.

**Battery (sg-combo-fap11, 75 rows, matched protocol):** mean 28.6339 vs
2.9358 (two archetypes) vs 0.3519 (champion) -- 81x. Levels 216, breadth
20/25, fap_errors 0, three-seed replication exact, and each converted
game's level count equals its integration agent's executor-verified
target. The 14 non-matching games are byte-identical to the prior arm.

**Gateway (official competition-mode, matched 35-minute window):**
28.742260 -- vs references 0.551859 (the LB-0.15 agent) and 3.044167 (the
submitted two-archetype candidate) on the identical protocol. 73 levels,
20 scoring games, FOUR completed outright at the 100-point cap (tu93 9/9
in 185 actions, ft09 6/6 in 80, ka59 7/7 in 275, sb26 8/8 in 124).

**LB calibration fact:** submission 56650224 (two archetypes) scored
exactly 0.15 -- the abstention floor held perfectly and neither template
grammar matched a hidden game. The thirteen-grammar candidate carries the
same measured floor with eleven times the net. Hidden transfer remains
unknown; the claim boundary is unchanged (engineered scaffold; deployed
fly content = the click head's compiled eye-map). The user authorized this
candidate on 2026-09-29; submitted as 56683298, notebook v12 (record above).

## Completion sweep: ALL ELEVEN dead games decoded; ft09 COMPLETE 6/6 -- 2026-09-28

The five-target completion workflow returned 5/5 with structured reports
(docs/fap_extension_20260928/completion_reports.json; artifacts preserved
beside the first sweep's). Every one execution-verified by the agent in its
own offline runs:

- **ft09: GAME COMPLETE, 6/6 levels, GameState.WIN.** Levels 5-6's missing
  rule: the two-sided glyph rule stands, but the PALETTE comes from the
  top-right indicator pair {e,f} (not the tile census), and a second
  mechanic stacks on top (tile state interacts with click count). The two
  residual unknowns (click-order commutativity, timer-death restore) are
  labelled inferred, non-blocking.
- **sc25: 4/6.** The door rule, measured on levels 3-4: the d-door
  dissolves the instant the colour-6 display pattern is completed on the
  pip board AND the die has line-of-sight to the level's key box. Level 5
  (a stateful multi-key chain, two stacked doors) is mapped but unsolved.
- **bp35: 4/10 verified.** Balloon-corridor climber: lateral moves then
  rise-until-blocked; toggle-open '2' cells, flood surfaces, action 7 =
  undo. Levels 5-10's maps are fully transcribed and mechanics decoded;
  unattempted for timebox only.
- **wa30: 3/9.** Warehouse-ferry on a 16x16 block grid with autonomous
  porter NPCs: bump marks a box, action 5 picks/drops, porters ferry.
  Level 4's sealed-room layout is mapped, unsolved.
- **dc22: 3/6.** Card-climbing puzzle: right-band colour cards teleport
  matching field items between a stack-staircase and a drop point above
  the 2x2 player; level completes stepping onto the carrier. Level 4's
  card vocabulary diverges (phase-flip / slide / transmute), measured but
  unplanned.

Standing total across both sweeps: all 11 never-scoring games are decoded;
four are COMPLETE wins offline (ft09 6/6, tu93 9/9, ka59 7/7, sb26 8/8);
the other seven have 3-7 verified levels each. Integration order (parsers
and planners, never replay scripts): ft09's L5-6 palette rule into the
existing glyph archetype, sc25's door rule into the pip archetype, then
new archetypes by cleanliness -- sb26 flatten builder, tu93 maze BFS, ka59
sokoban planner, re86 parking, su15 merge, ls20 pattern-key, bp35 climber,
dc22 cards, wa30 ferry.

## Extension sweep: six games decoded, three full WINs; recovered from a dead run -- 2026-09-28

The 11-target extension fan-out (9 remaining dead games + the ft09-L5 and
sc25-door boundaries, batches of 3 per the standing parallelism rule) died
mid-run when the previous session ended: the journal shows six completed
agents whose RETURNS were all null. Their WORK survived in /tmp/fap_ext --
per-game NOTES, verified program JSONs, and solver scripts -- and is now
preserved under docs/fap_extension_20260928/ (this is the recovery pattern
the working agreement mandates: read the journal, then salvage artifacts in
the same turn).

**Recovered, all execution-verified by the agents in their own runs:**
- tu93: FULL WIN, 9/9 levels in 187 actions. Lockstep maze: rooms on a
  6px pitch, open doors colour 2, e-tile goal; enemies advance only on the
  avatar's successful moves (blocked moves freeze the world); sentinel /
  patroller / chaser types decoded, timer row 63.
- ka59: FULL WIN, 7/7 levels in 321 actions. Multi-body sokoban-with-
  launchers: click selects an e-ring object, arrows drive it on a 3px
  lattice, contact-push launches; slot geometry IS the goal display.
- sb26: FULL WIN, 8/8 levels in 124 steps. Recursive sequence builder:
  legend = flatten(root box) with cycle-cut references; fill slots so the
  flatten matches, press action 5 to submit.
- re86: 6/8 levels in 335 actions. "Crosshair parking": action 5 cycles the
  active avatar, park each shape so all same-colour dots lie on its
  outline; palette tiles recolour on touch; L6+ adds a deformable squeeze
  object and independently-blocking plus-bars.
- su15: 7/9 levels in 97 actions. Merge-and-deliver: clicking near >=2
  same-stage creatures fuses them up a size ladder; the header shows the
  target shape multiset; action 7 is a full-world UNDO (search-with-
  rollback is legal); refused clicks freeze the world.
- ls20: 5/7 levels in 226 actions. Pattern-key transport: a 5x5 two-tone
  key carries a hidden 3x3 pattern+ink shown in a display box; devices
  transform it (rotator = rot90 CW, shifter = fixed bijection); the goal
  box accepts the key only when pattern AND ink match.

Batch 3 (dc22, bp35, wa30) died mid-investigation (partial probes on disk);
batch 4 (ft09 level 5, sc25 door) never started. A completion sweep for
those five is the next action, feeding the recovered patterns in as
established context. INTEGRATION NOTE, per the first principle and the
hidden-set lesson: the verified programs are seed-specific evidence that
the RULES are right; what enters the library is per-archetype PARSERS and
PLANNERS derived from the rules (maze BFS, sokoban planner, parking
derivation, flatten matcher), never replayed coordinate scripts.

## A/B gate passed; FAP candidate submitted: 56650224 -- 2026-09-28

The bounded candidate-validation session the collaborator review recommended,
run end to end, then the user-authorized submission ("if A/B test passes, go
submit").

**Review response first (commit 8f38c58):** every verifiable claim checked;
real defects fixed -- sg-combo registered (the coherence test genuinely
failed at 490+1), the efference entry now carries its isolation caveat (the
config is surprise+efference; the 19-row single-change pairing vs the killed
registered baseline shows +0.0271, 3/19 rows differing -- no separation
either way), archetype reset hooks clear the pip roll memory on resets and
level advances, a queue-divergence guard drops program steps whenever the
board changes without our action, the pip grammar requires a complete evenly
spaced board and never emits a blind roll, and the wording now states
precisely that H-LC-RECOGNIZER killed only the dead-vs-live role it tested
and that the deployed fly content is the compiled eye-map (static anatomical
metadata), not live neuronal computation. Dataset-version pinning verified:
Kaggle resolves dataset versions at notebook save time, so old submissions
cannot skew; the paired-push rule covers re-saves.

**The A/B, official competition-mode gateway, matched 35-minute windows
ended by SIGINT (the protocol that produced the recorded 0.551859):**
- Arm OFF (combo_light, the exact 0.15 agent's config): 0.551859, 10 levels
  -- replicates the recorded reference EXACTLY.
- Arm ON (combo_light_fap): 3.044167, 16 levels. ft09 47.619/4 levels,
  sc25 16.979/3 levels; the other 23 games' scores identical to four
  decimals; fap_errors 0 everywhere; all 25 games played; the only
  tracebacks are post-SIGINT shutdown races, same as arm OFF.
Preregistered gate: PASSED on all three criteria.

**Submission:** dataset v8 pushed (hosted controller.yaml byte-compared to
configs/combo_light_fap.yaml), notebook v11 pushed, kernel COMPLETE with
FLYGI_PREFLIGHT showing fap_library true / verified true / controller-light,
then `kaggle competitions submit ... -v 11` accepted as submission
**56650224** at 2026-09-28 19:08:50 UTC (PENDING). Claim boundary, stated in
the submission description itself: hidden-set transfer of the two archetype
parsers is unknown; abstention makes the prior submitted behavior (LB 0.15)
the floor. Slots now exhausted for the day.

## FAP seated in the deployed policy; adversarial review; 8.3x pilot -- 2026-09-27

At the user's direction the library was wired into StateGraphPolicy behind a
new default-off knob (controller.fap_library). Seating design: unlike
fly/head/tags/taxis it does not score candidates -- when an archetype matches
it OVERRIDES the ranking with the program's next step, committed through the
same path as a ranked candidate (mode "fap"); when it abstains the turn is
byte-identical to fap=None. Wired identically in the local harness and the
Kaggle adapter; configs/combo_fap.yaml differs from the combo champion in
exactly one line.

**Pilot battery (75 rows, protocol matched to sg-combo exactly), measured:**
mean score 2.9343 vs champion 0.3519 -- 8.3x, the largest local jump in
project history. Levels 45 vs 24, breadth 11 vs 9. ft09 0 -> 47.62 per seed
(3/3 seeds identical, 4 levels each), sc25 0 -> 16.94 per seed (3 levels
each). The other 23 games: EXACTLY zero delta on every row -- system-level
confirmation of abstention byte-identity. Recorded as
sg-combo-fap-pilot; superseded by the post-hardening arm below.

**Adversarial review (39-agent workflow, 3 lenses, 2 refuters per finding)
confirmed real defects, all fixed the same day:**
- CRITICAL hard-ban bypass: the fired path never consulted node.hard_bans and
  measurably re-executed a graph-proven-fatal click for 3 deaths. Now
  refused, counted (fap_banned), and reported to the executor.
- CRITICAL version skew: the config loader rejects unknown controller keys,
  so a controller.yaml carrying fap_library crashes any OLDER embedded flygi
  -- the six-zeros pattern. The packaging script now validates the staged
  controller.yaml against the staged code, and the operational rule (dataset
  version and notebook re-save travel together) is recorded there.
- Executor lifecycle: stale program queues survived forced resets and level
  advances (replaying pre-death coordinates); the revisit guard counted
  abstaining visits and was never cleared, permanently muting a game from
  its 4th life; the swallow retry armed once per game instead of per life; a
  rejected (illegal/banned) proposal desynced the program pointer. Fixed via
  notify_reset/notify_level_advance/reject_last hooks called from the
  policy, and the guard now counts EMISSIONS per frame.
- No exception containment at the seam: an executor bug degraded to random
  play (Kaggle) or a dead row (harness). Now degrades to abstention with a
  fap_errors diagnostic.
- Abstain cost measured 17-65 ms/turn (Python window scan) -- a Kaggle
  wall-clock leak. The lattice scan is vectorized and never-matched games
  back off; measured post-fix cost 0.15-0.19 ms/turn (~300x).
- Deploy visibility: fap_library now appears in FLYGI_PREFLIGHT identity and
  fap_fired/fap_errors in the FLYGI_DIAG line.
491 tests pass (6 new lifecycle/seam tests). Offline solver totals unchanged
after hardening (ft09 4 levels, sc25 3). Known parity gap recorded, not
fixed: the adapter never wires taxis (default-off everywhere, score-inert).

**Hardened battery, measured 2026-09-28 (sg-combo-fap, 75 rows):** mean
score 2.9358 vs champion 0.3519, levels 45 vs 24, breadth 11 vs 9 --
confirming the pilot and a touch above it (sc25 50.94 vs 50.82 total).
fap_errors 0; the hard-ban gate refused 60 proposals across the battery
(the hole the review measured 3 deaths through). Seed replication perfect
(fired turns 590x3 on ft09, 574x3 on sc25); the other 23 games again show
exactly zero delta on every row. Claim boundary: this is a LOCAL number on
the two public template games; hidden-set transfer requires hidden games
sharing these archetypes and is unknown. Next decisions, both the user's:
(a) whether to package sg-combo-fap (on combo or combo_light base) as the
submission candidate -- the mandatory local competition-mode gateway battery
gate applies first; (b) whether to extend the library (ft09 level 5, sc25
level 4, and the other nine dead games' archetypes) before or after that.

## H-EFFERENCE closed by measurement: the preregistered null, confirmed -- 2026-09-27

The registry's last open module ran as a standard battery arm at the user's
direction (sg-bioeye-lc-efference, 75 rows, seeds 0-2, budget 600, contract
PASS). Mean score 0.2409 vs baseline sg-bioeye-lc 0.2504, paired diff -0.0095
with only 21/75 rows differing at all; levels 18 vs 16 (gained lf52, lost
cd82 -- seed churn). Exactly the null the 2026-09-23 registration predicted
by construction (the copy cancels out of the saliency comparison), and with
sg-mbdr-learn already null, every registered use of the efference copy is
now measured. H-EFFERENCE: open -> null. This was the last fly-inventory
item; the full inventory sweep ("do em all") is complete -- see the four
entries below and the registry.

T4/T5's native role closed by reasoning, recorded here rather than run: its
only unclaimed native use, motion-localizing the moving avatar, feeds the
taxis mechanism whose measured bottleneck is arrival semantics, not
segmentation (the engineered shift matcher already recovers 11/14 games'
motions exactly and the taxis arm was null anyway). A run could only improve
a component upstream of a measured-dead endpoint.

## FAP library entries 1-2: ft09 solved through level 2, sc25 level 1 -- 2026-09-27

src/flygi/controller/fap_library.py (engineered scaffold end to end, labelled;
H-LC-RECOGNIZER's refutation closed the fly seat for recognition). Solver-only
offline play (scripts/fap_solver_eval.py): ft09 completes levels 1-2
autonomously -- the glyph parser generalizes across marked colours -- and
sc25 completes levels 1-2 (the roll seeks the detected dock, and the archetype
remembers its last known-good direction for the merge-at-arrival endgame that
level 2 measured). SAME-DAY EXTENSIONS: ft09 level 3's "extra rule" was the
glyph rule's other half -- 2-cells prescribe the OTHER palette colour, not
just 0-cells the marked one -- and the two-sided rule completes ft09 LEVELS
1-4 in 46 solver actions; stall and frame-revisit guards make a stuck solver
abstain instead of burning the timer life (ft09 level 5's measured failure
mode), and with the guards the sc25 stack reaches LEVEL 3. Standing totals:
ft09 4 levels, sc25 3, against an all-time random record of 0 on both.
Boundaries: ft09 level 5 (rule unknown), sc25 level 4+.
ABSTENTION AUDIT across all 25 games at budget 300: zero actions emitted and
zero matches on the other 23 games, no crashes -- seating the library costs
the champion nothing by construction. Random play's all-time record on these
two games is 0 levels; the solver's is 3. Parser rules pinned by
tests/test_fap_library.py (7 tests). NOT yet seated in the deployed policy
and NOT a submission; both are separate decisions.

## H-CX-SCRATCHPAD refuted: the ring holds activity, not position -- 2026-09-27

The last untested use of the compass -- a one-bit context scratchpad -- is
structurally dead at the deployed operating point, and the probe sharpened
what "persistence" meant. Settle map (8 write angles x 2 write styles, 50
darkness steps, gain 2.0): the compiled CX has TWO fixed points, one robust
near 222 degrees (EPG mass ~0.21 -- the band the original persistence
measurement saw) and one vestigial near 90 degrees (mass 4e-4); writes on
half the ring die completely; write scales 3 and 8 are bit-identical (tanh
saturation). The A-vs-B decode explains itself: darkness accuracy is EXACTLY
0.5 because strong-basin writes always read back and opposite writes always
die -- a half-writable bit -- and the visual condition's nominal 0.75-0.85 is
the visual stream reviving dead trials toward the vestigial attractor, not
memory. Recorded on the registry as H-CX-SCRATCHPAD (refuted) plus a
reinterpretation on H-CX-RING-ATTRACTOR: fixed-point attraction, not a ring
continuum; activity endures, position is not stored. The anatomy-specific
real-vs-null separation stands. Instrument: scripts/cx_scratchpad_premise.py
(--settle-map for the structural probe).

## H-LC-RECOGNIZER: killed by its own preregistered condition -- 2026-09-27

Same day, the recognizer seat was premise-killed before any build. Protocol:
40 random-play frames per game x 25 games, stateless gain-2.0 advance, LC
family (4,674 neurons) and lateral horn (2,028) population vectors; real
bio-eye vs the established scrambled-encoder twin; trivial alternative a raw
grid-block histogram. Seen-game identity saturates for EVERY reader (1.0 --
frames are individually distinctive), but the FAP-relevant endpoint,
held-out-GAME dead-vs-live, carries no signal for anyone: nearest-centroid
put all readers at or below chance, and the final preregistered escalation (a
leave-one-game-out linear probe, identical pipeline for all arms) measured
real LC 0.438 / real LH 0.520 vs scrambled 0.510/0.579, raw baseline 0.415,
chance 0.5. The real arms beat neither their controls nor chance;
kill_condition_met true; no further decoder shopping per the escalation's
own registration. A game's CLASS is behavioural, not visual, at frame level.
Consequence: a FAP library's recognition stage would be engineered parsing
and earns the fly nothing; the fly's load-bearing seat remains the
retinotopic click head.

## Reflex sprint: 3.1x faster, byte-identical, same local score -- 2026-09-27

**Measured:** per-action latency 12.9 -> 4.20 ms (profile-driven: grouped
component extraction, vectorized tie-exact pixel selection, pure extraction
cache + trusted construction, bit-packed tag Jaccard). Byte-identity proven
twice by replay hash against a recorded arm trace plus a 120-grid
randomized equivalence test against the reference implementations kept
in-test; 474 tests pass. Gateway battery at the same 35-minute deadline:
0.5519 -- identical to pre-sprint -- with 135,394 actions (was 80,941),
the same ten games, levels, and scores. **Measured conclusion:** on the
public set volume is not the binding constraint; completions happen early
and the fifteen zero games are capability-bound interaction programs. The
sprint's value is deployment-side: a 3.1x cheaper agent under the Kaggle
rerun's 110-parallel-games shared CPU budget, with provably identical
behavior. It costs nothing and hedges slow hardware; it does not raise the
local score. Speed lever: now measured and closed alongside the budget
lever. What remains for score is capability above candidate ordering.

## Best-existing engineering submission — 2026-09-27 15:10 PDT

**Submitted:** Kaggle accepted competition submission **56620463** at
`2026-09-27 22:09:56.043 UTC` (15:09:56 PDT), notebook
`megusalexandrus/flygi-arc-agi-3` **version 10**, output `submission.parquet`.
Independent submission-history query confirms `SubmissionStatus.PENDING`,
with no public score yet. The CLI reports **0 submissions remaining today**;
that message followed acceptance, not rejection. Exactly one submission was
made. Do not repeat it when resuming this log.

Submission description explicitly identifies `combo_light` as an engineering
baseline with neuronal dynamics OFF, source `8021d5c`, construction-crash and
bounded-recording fixes, local public score 0.551859, and unvalidated hidden
performance. A leaderboard result would not establish fly computation.

**Authorization:** after being told there was no candidate meeting the
load-bearing-fly gate, the user explicitly instructed: "Submit whatever is the
best candidate we have." This authorizes one submission of `combo_light` as an
engineering baseline despite that unmet attribution gate. It does not establish
fly computation, change the scientific first principle, or reopen failed
research branches. No new score prediction is made.

**Measured selection:** the locked `combo_light` configuration remains the
highest recorded full local competition-mode engineering result: 0.551859,
10 levels across 25 public games. The neuronal dynamics are disabled. Preserve
the measured legacy coordinate convention; no policy tuning for this upload.

**Measured preflight:** at source `8021d5c`, 21 Kaggle smoke/notebook tests pass.
Local adapter preflight reports verified `controller-light`, retinotopic click
head, deadline 100, `legacy_xy_flat`, `retino_tags`, 166,700 nodes, 24,994,595
edges, K=4, and `neuronal_dynamics_active=false`. Independent package audit
finds no immediate packaging blocker. Known unclosed risks are Swarm
thread-failure visibility, mutable ACTION6 payload isolation, and a long
memory-growth soak; this is not a claim of completing those gates. The previous
official-framework 30-second gateway smoke after the recording fix passed.

**Measured remote state before upload:** Kaggle still reports exactly the six
recorded 0.00 submissions, latest ID 56563583. Dataset
`megusalexandrus/flygi-malecns-runtime` is ready at version 7. Downloaded hosted
config/controller/provenance files match the staged copies byte-for-byte:
controller SHA-256 `a0c595da8c572caca0dc1a3ca99de70f6d32193c41403554b9fd3b6f0770c542`,
config `3d5d17bfcdfeaba40437d899a5ef7149f7ca9aeaef7aca609eb1563fb46a9d38`,
dataset provenance `dbce4fa8c0d2f64fe6bbf357c377271dca6507ed7eeed19c8cbcd07adcd41c00`.
No dataset re-upload was needed. The old dataset provenance's `controller-fly`
label is stale; the actual config and current adapter explicitly say otherwise.

**Notebook upload:** rebuilt current source with
`.venv/bin/python scripts/build_notebook.py`; generated notebook SHA-256
`e7aacbc231f172d84a7bc75f32a0d67b6bf806e156775d7807c687efbb2c01af`.
`kaggle kernels push -p notebooks/` successfully created private CPU,
internet-disabled notebook **version 10**. Its ordinary preflight completed;
downloaded log identity matches every field above. The one-row placeholder
parquet has the expected schema; this ordinary-run file is not a hidden-game
measurement. Log SHA-256
`cdbb53a2431a2a288783f6a9603670b2dcf4c63ca2476309265b955ed8904ba1`;
placeholder SHA-256
`71bfd543030e339d87bd9ff744d466218398a1259650b2c255626d27049c88bb`.
Local read-only evidence is in `/private/tmp/flygi-submit-20260927.PjQ5hp/`;
Kaggle version 10 remains the hosted evidence source if temporary files expire.

**Executed submission command** (credentials supplied privately from the
existing token file, never printed):
`kaggle competitions submit arc-prize-2026-arc-agi-3 -k megusalexandrus/flygi-arc-agi-3 -v 10 -f submission.parquet -m '<engineering-baseline description above>'`.

**Next:** when the user requests status, query submission 56620463's state and
score before drawing any conclusion. No local experiment remains running; no
automatic monitoring or second submission was scheduled. No dataset recreation,
science change, or tuning was needed. Checkpoint this record to the private
remote; retain existing failed-branch stop rules and the default fly-attribution
gate for future work unless the user explicitly changes them again.

## Native visual-MB premise audit — 2026-09-26 13:26 PDT

### Frozen representation gate closed — 2026-09-26 13:50 PDT

**Measured:** H-VISUAL-MEMORY-ENTRY is **refuted under its frozen protocol**.
The exact preregistered command completed in 21.213 seconds at pushed source
`b718f03`, with a clean tracked tree, six sparse-matvec threads, 32 scenes per
condition, 32 updates per scene, the full 166,700-node / 24,994,595-edge graph,
and all 206 annotated KCg-d cells. All input/provenance/reset contracts passed.
Exit code 2 means scientific failure, not a runtime error.

| Representation | Position-transfer accuracy | Frozen requirement |
| --- | ---: | --- |
| Native positive KCg-d state | 0.521875 | >=0.75 and >=both input baselines +0.10 |
| Unchanged sensory drive | 0.550000 | named identity/plumbing comparison |
| Fifteen type-mean drives | 0.497917 | named input-mass/channel comparison |
| Graph-off KC state | 0.500000 | exactly zero state, chance score |

Native position means exceeded chance at 9/16 locations, short of 12. Minimum
positive KC-vector RMS was 2.71927e-6; minimum same-position shape-difference
RMS was 2.21036e-5. Both exceed the declared 1e-7 floor. **Measured:** this is
not a silent-input or numerically sub-floor failure; the fixed readout failed
the specified position-transfer comparisons. It does not establish which
model assumption failed or what a living fly can recognize.

**Decision:** stop this model/interface/readout branch before plasticity. No
gain, timing, cell selector, normalization, stimulus, or threshold rescue; no
anatomy-control expansion or ARC integration. No agent behavior, Kaggle assets,
submission, or leaderboard score changed. The comparison saved us from building
a memory layer on a representation that did not meet its entry requirement.

**Evidence:** ignored immutable result
`results/connectome_agent/visual_memory_entry_v1.json`, SHA-256
`1241b74f3e1df5a8621cf0667d0318c5ae19ba125da226ef3fccf8a9c337ed83`.
The `.json.events.jsonl` sidecar records all 64 scene completions. The artifact
contains exact source/protocol/data hashes, raw KC readouts at steps 4/8/16/32,
all 480 comparison margins per condition, selector IDs, and every gate clause.
Final pre-run focused validation passed 89 tests with Ruff clean. Final
`.venv/bin/pytest -q` passed **473 tests in 26.67 seconds**. Independent
artifact-only recomputation rebuilt the sensory vectors/type means from saved
sparse drives and reproduced every margin, decision, position mean, accuracy,
signal floor, and gate verdict exactly. It also verified all 67 telemetry events,
32 trials per condition, four snapshots per trial, reset flags, shared CSR,
six-thread settings, drive hashes, and pinned provenance. No neural rerun.

**Current stopping point:** evidence verification is complete; no experiment
remains running or queued. No memory or ARC build is justified by this result.
Before another such build, a new independent
visual-model validity protocol must specify the biological response being
reproduced, the literature-constrained input/dynamics, trivial alternatives,
and a finite pass/kill rule. That is a separate model-validation decision, not
permission to tune this failed developmental panel until it passes.

### Probe implementation checkpoint — 2026-09-26 13:46 PDT

Implemented `scripts/probe_visual_memory_entry.py`, an external diagnostic only;
no agent, policy, plasticity, or deployment path changes. The frozen protocol's
SHA-256 is `220591b7b93734e90bdf4fe16123143c54222f4904ac9da21070b5f9827fcf08`
and is enforced before runtime loading. The probe also verifies the four pinned
data assets, exact 206-cell selector, stimulus visibility and uniqueness,
sensory/KC disjointness, reset/chunk identity, graph-off silence, and unchanged
drives. It saves all raw KC responses and 480 ordered comparison margins per
condition; no-overwrite finite JSON and flushed progress events preserve the
audit trail. Six existing sparse-matvec threads retain the reference operation
order rather than substituting a different numerical backend.

Measured pre-outcome validation: the initial focused command
`.venv/bin/pytest -q tests/test_visual_memory_entry.py tests/test_rate_dynamics.py tests/test_dynamics_runtime.py tests/test_spmv.py tests/test_league.py`
passed 82 tests; focused Ruff passed. Synthetic shape codes score 1.0;
constant and location-only codes score .5. These validate the diagnostic, not
the biological hypothesis. The full suite passed 466 tests before five extra
artifact-publication tests were added; the expanded focused suite passed 87.

Independent pre-outcome review found an exact-boundary arithmetic defect:
subtracting rounded accuracies can reject a true .10 advantage. The two margin
gates now compare exact half-credit sums against 48 credits out of 480; this
changes no threshold. Exact-boundary and half-credit-below regressions now pass
(29 probe tests total). The static
178-325 sensory-support golden and graph-off score contract are also enforced.
Six-thread execution is a recorded performance setting, not a scientific gate.
No neural outcome has been inspected.

Independent implementation review is complete. Next: checkpoint/push the exact source, run the single frozen
command from the protocol, record pass/fail, and obey its stop condition. Do not
start a memory implementation merely because the probe executes successfully.

### Execution resumed — 2026-09-26 13:36 PDT

The user authorized proceeding. The next finite deliverable is
H-VISUAL-MEMORY-ENTRY: a 32-scene position-transfer representation gate, fully
specified in `docs/experiments/visual_memory_entry.md` before neural outcomes.
It addresses the reviewed concern that arbitrary direct VP clamps bypass the
upstream visual wiring. Stimuli enter through the existing retinotopic encoder;
all 206 exact KCg-d cells are read after the frozen full-connectome dynamics.

Trivial alternatives are the unchanged sensory drive, fifteen per-type mean
drives, and graph-off. Assumptions A1-A5 freeze the sensory mapping, uniform
rate model/32-step horizon, positive KC interpretation, external diagnostic,
and engineering thresholds. The external nearest-exemplar computation is an
evaluator only and never an agent component. No learning or score claim follows.

Measured static coverage before freeze: `[14,26,38,50]^2` contains two invisible
corners; the central `[20,28,36,44]^2` panel reaches 178-325 sensory neurons for
every rectangle. Input energy varies by position/orientation, so the type-mean
baseline is required. No neural state was advanced during this choice.

Stages: finish compact protocol review -> implement standalone probe and
synthetic comparison tests -> checkpoint/push -> run once -> record verdict.
A failure closes this branch before plasticity. A pass requires a separately
frozen locally matched anatomy test before plasticity, then an end-to-end
cue-value and ARC test. This ordering prevents building a memory system before
checking whether its input supports the intended generalization.

**Pre-outcome review closed:** the method reviewer required an explicit total
of 32 updates, identical positive rectification for both input baselines, defined
zero vectors, and the exact 480-comparison reduction. These are now in the
protocol. RMS floors remain the declared >1e-7 bars. No outcome was used.

**Measured upstream anatomy:** the exact literature-prior MC62 alias is in
`hemibrainType` (248 cells), and PLP251 is in `flywireType` (canonical LoVP97,
two bodies 13707/15915). At raw weight>=5 the existing retinotopic population
has 1,406 edges into MC62; MC62->PLP251 has 75 edges; PLP251->KCg-d has 17.
All are ipsilateral. Only the first block admits substantial within-side
degree-preserving rewiring (99.2% structurally switchable); the downstream
blocks have one target/source per side and no such switches. This is useful
anatomy for a later causal test, not a reason to alter the frozen all-206-KC
representation endpoint after results. The exact LC15/PLP009 mapping from
another connectome does not reproduce here at this threshold.

**Historical process checkpoint (before representation-gate freeze):** no implementation or neural outcome had been run for
the proposed visual-projection-neuron -> visual-KC -> MBON branch. The complete
root WORKLOG and the complete 999-line Experiment 000 specification were read
before planning. `HEAD == origin/main == c008751`; the tracked tree was clean,
with only the unrelated untracked `.fly-or-fake-work/` directory. The next
branch remains design-only until its selectors, biology, controls, independent
unit, metrics, thresholds, and kill rule are frozen outcome-blind.

**Measured selector discrepancy (resolved below):** an independent streaming scan of all
151,856,684 released MaleCNS weight rows does not reproduce the narrative
`1,615 edges / 251 visual VPs / 332 KCs` claim under the most direct exact
interpretation. With presynaptic `superclass == "visual_projection"` and
postsynaptic `type in {"KCg-d", "KCab-p"}`, the pinned files contain **1,435
direct pair edges / 9,736 contacts from 221 VPs into 311 of 335 annotated visual
KCs** at `weight >= 1`; at `weight >= 5`, they contain 595 edges / 8,236
contacts from 82 VPs into 269 KCs. Target annotations are 206 KCg-d and 129
KCab-p. This is a selector-definition discrepancy, not a biological result.

**Measured resolution, static anatomy audit 2026-09-26:** the earlier selector
was every `class == "Kenyon_Cell"` receiving a direct visual-projection edge,
not the exact KCg-d/KCab-p type subset. That raw block has 1,616 pairs from
252 VPs into 332 KCs, totaling 11,094 contacts. The signed runtime removes the
one-contact edge from body 519323 (`aMe8`, unclear consensus transmitter) to
body 105662 (`KCg-d`), yielding exactly 1,615/251/332. These counts are
compatible; their populations and preprocessing differ. "Visual KC" must not
silently mean any weak direct VP recipient: the relational pool includes 12
KCg-m and nine cells of other types as well as 203 KCg-d and 108 KCab-p.

**Measured anatomy constraints from the same read-only audit:** the 332 direct
VP-recipient KCs contact 83 MBON bodies through 4,485 raw pairs / 42,762 contacts.
APL feedback reaches 331/332. The VP sources also have direct shortcuts to MBON,
DAN, and APL, so a whole-network response alone cannot establish mediation by
VP->KC->MBON. Exact-degree source-sign/side and target-type/side strata leave
86.4% of the runtime VP->KC edges structurally switchable; the proposed local
KC->MBON strata leave only 30.5%. The earlier joint-null proposal is therefore
not freeze-ready under the existing 80% switchability requirement. No null
criterion has been relaxed and no neural outcome has been inspected.

**Established and inferred design constraint:**
[Ganguly et al. (2024)](https://www.nature.com/articles/s41467-024-49616-z)
found structured VPN->LVIN connections but individual visual-KC input combinations consistent with biased
random sampling in FlyWire. **Inferred:** arbitrary synthetic VP cues may test
associative mechanics while missing the upstream visual structure whose value
we want to test. Before freeze, specify what visual relationship the stimuli
preserve and which exact anatomical block each null tests. This does not change
the requirement to demonstrate anatomy-dependent benefit before ARC promotion.

**Established versus assumed boundary:** primary literature supports direct
visual input to segregated KCg-d and KCab-p populations and visual associative
memory through shared mushroom-body output/modulatory circuitry. It does not
establish that FlyGI's proposed one-presentation, 32-world delayed-match assay,
rate equation, cue-to-VP clamp, readout scalar, plasticity magnitude, or pass
threshold is physiological. Those remain explicit `MODEL_ASSUMPTION` or
`ENGINEERING_CHOICE` items and must each have a named trivial alternative.

**Literature-audit correction:** reset-separated cue-value recall with only
synaptic weights retained tests associative memory; it does not establish
abstract delayed matching or working memory. The proposed assay name is
one-pairing visual associative recall with delayed two-choice testing. Direct
KCg-d and predominantly indirect KCab-p pathways must be specified separately.
Primary literature also does not license a universal depression-only rule:
[Handler et al. (2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9012144/)
reports timing-dependent depression and potentiation. Exact simulation timing,
learning equation, and magnitude remain declared assumptions.

**Audits received, read-only:** one audit independently reconstructed the exact
MaleCNS local anatomy, including source/target definitions, transmitter/sign,
KC->MBON reach, DAN/APL support, and local-null feasibility. A second audit
checked primary literature for what can legitimately be called established.
Neither audit edited source or ran neural outcomes.

**Earlier next-decision proposal (superseded by the representation gate above):** with the direct-edge count reconciled, choose the
narrowest biologically defensible population rule; then write and red-team the
entire synthetic premise-killer protocol before code. The smallest proposed
falsifier remains a reset-separated, paired visual-cue assay with chance,
no-plasticity, cue/credit-shuffle, and locally degree/sign/weight-matched anatomy
controls. It may earn an end-to-end retinotopic/ARC assay only if the native
circuit beats every frozen control. A contract-valid failure stops the branch;
no post-result selector, threshold, pooling, stimulus-panel, or readout change
is permitted.

## Codex takeover: runtime bounded; score premise reopened — 2026-09-26 11:45 PDT

**Measured:** the six public-leaderboard `0.00` submissions remain construction
failures, not behavioral measurements: the agents took zero actions. The fixed
25-game local competition-mode battery at `bcf18b2` remains a valid measurement
of that engineering candidate only: score `0.551859`, 10 completed levels,
80,941 actions, and no exceptions in 35 minutes. It is not evidence of hidden
transfer and it is not a fly-attributed result.

**Measured audit correction:** `configs/combo_light.yaml` sets
`deploy_fly_tiebreak: false`. Its decisions therefore run through the Python
state-graph controller, Python online click head, and static retinotopy metadata;
the 166,700-neuron recurrent dynamics are not advanced. Replacing the graph by
a degree-preserving null would leave those decisions unchanged. This candidate
is an engineering baseline and fails the repository's load-bearing-fly gate.
Preflight had incorrectly labelled it `controller-fly`; the adapter now reports
`controller-light`, `deploy_fly_tiebreak: false`, and
`neuronal_dynamics_active: false` explicitly.

**Measured deployment blocker and repair:** the 25 files written by the
35-minute gateway battery occupied 2,258,912,722 bytes (`2.104 GiB`), or about
27.9 KB/action. At the same aggregate rate an 8.4-hour rerun projects to about
30.3 GiB of redundant JSONL, while the vendor `Agent` also retained every full
frame in RAM. FlyGI's `is_done` and `choose_action` discard the framework's
history argument; policy memory lives in the per-agent policy. The adapter now
overrides `append_frame` to retain one current frame and suppress local replay
serialization. **ASSUMPTION:** this Markov adapter boundary is valid because no
FlyGI decision reads `self.frames` history; it breaks if future policy code does.

**Measured validation:** `.venv/bin/pytest -q tests/test_kaggle_smoke.py`
passes 18/18 and explicit Ruff checks pass. A fresh official-framework,
competition-mode localhost run on `lp85` reached level 1 on action 16 and score
2.7777777778, exactly matching the prior battery's level-1 milestone. It then
ended on the 30-second wall guard after 1,047 actions, closed the scorecard
cleanly, and left `/private/tmp/flygi_bounded_recordings` at 0 bytes. This
validates the scored milestone and O(1) framework frame history; it does not yet
bound residual growth in `policy.records` or `RetinoTagRegistry._seen`.

**Measured transport repair:** four consecutive empty/malformed gateway replies
now mark the agent transport-dead and return the last valid frame so the next
`is_done()` closes the game, instead of raising inside a Swarm thread. The log
line is valid JSON. **ASSUMPTION:** a last valid frame always exists after agent
construction in the official loop; if construction-time transport can fail
before RESET returns, that separate path must still fail the notebook visibly.

**Measured score-facing defect:** the click head uses `x * 64 + y` to flatten a
candidate even though ARC payloads use `(x=column, y=row)` and grids are indexed
`grid[y, x]`; its tests repeat the same swapped convention. The same row-to-x
convention appears in `retinotopic_saliency.py` and raw-grid slices in
`fly_tiebreak.py`. For `(x=10, y=20)`, the head reads flat index 660 rather than
the row-major 1290. Thus the prior 0.8-cell localization and relevant decoder
nulls tested an internally transposed interface. The `0.551859` baseline also
contains this defect, so it must be preserved as locked control A rather than
silently corrected.

**Measured coordinate gate (completed 2026-09-26 12:14 PDT):**
H-COORDINATE-CONVENTION replayed the exact frozen `sg-combo` traces under both
`legacy_xy_flat` and `arc_row_major`. All 18/18 rows and 10,800 action-step
before/after frame pairs reproduced (21,600 individual hash comparisons); the
comparison contained 9,422 clicks, of which 8,877 changed the frame. Corrected
B lowered mean per-row prequential log loss from 0.144710 to 0.084567. Across
the six nondegenerate rows (3,532 clicks), aggregate average precision rose
from 0.974304 to 0.974420. Those aggregate improvements were concentrated in
`lp85` and `ft09`.

**Measured stop decision:** the preregistered robustness bar failed. Median
paired row log-loss delta was +0.002365 rather than below zero, and only 2/6
game means were non-worse rather than at least 4/6. Per-game corrected-minus-
legacy deltas were `ft09 -0.033901`, `lp85 -0.354565`, `r11l +0.003224`,
`sp80 +0.017843`, `tn36 +0.002089`, and `vc33 +0.004450`. The kill rule therefore
stops this score branch despite the aggregate gain: no behavioral battery, no
corrected `combo_light` candidate, and no post-result amendment of the bar.
The retained convention switch and asymmetric golden tests make both historical
and corrected semantics explicit; they do not promote the Python click head.

**Measured provenance:** local ignored result artifact at closure
`results/connectome_agent/coordinate_convention_replay.json` has SHA-256
`8ce8ca457c1374bf7e9bb539f9365f0885739643a0fbde6d308a25fb7fb94044`.
The artifact records analyzer SHA-256
`9bc9a3bc6e713f15cc3abb9b80dc4388c4c6e4874a16159a86131e59b316d2d2`,
registry-at-run SHA-256
`6e7bcd3965f39459a4cdc452da9d25ae33a592bb1e81209e62f8c9bd8c22f92f`, and
source rows SHA-256
`ae5de86c1f5d8abe8fa19a5e66acad6b87944a1ef6a3ffc2abe88255fa7161ad` and the
locked config has SHA-256
`a0c595da8c572caca0dc1a3ca99de70f6d32193c41403554b9fd3b6f0770c542`.

**Measured analyzer correction before commit:** review found that the first
local artifact pooled 12 single-class rows into aggregate average precision,
contrary to the preregistered exclusion. That result is preserved as
`coordinate_convention_replay.invalid-ap-v1.json` with SHA-256
`04f816f524a5b4020d43df4ee95218e5c54defe114de1d303cc9d2d1adf8f90d` and is
explicitly invalid. The analyzer now groups by row before pooling and has a
degenerate-row regression test. Direct old/new comparison found identical
per-row summaries and all 9,422 example payloads; only AP-related aggregate
fields plus creation time/hash changed. Log loss, all game deltas, and the
failed promotion verdict are identical. A metric-correct intermediate artifact
without analyzer provenance is preserved as
`coordinate_convention_replay.valid-ap-no-analyzer-sha.json` (SHA-256
`403e328844551841f0f482168276ed18b7e95a4b12750c5086c265a1db2fda86`) and is
superseded, not contradictory; the final rerun added analyzer/registry hashes
without changing any metric.

**Measured documentation correction:** source and adapter comments now state
that the static cell-to-column map is anatomy-derived plumbing, not neural
computation. `configs/combo_light.yaml` remains byte-for-byte frozen at the
result hash above, so its two historical “fly-load-bearing” comments are
preserved only as artifact provenance and are superseded by this audit and the
adapter's machine-readable `neuronal_dynamics_active: false` preflight.

**Measured validation:** `.venv/bin/pytest -q` passes 422/422 in 26.73 s;
Ruff check and format pass on every changed Python file; `EXPERIMENTS.yaml`
parses with the coordinate hypothesis `refuted` and the unrelated MB-input-bus
status restored to `open`; `scripts/league.py --hypotheses` renders cleanly and
`LEAGUE.md` is regenerated from the registry. A deliberately broader Ruff run
also surfaced two pre-existing HEAD findings outside this checkpoint
(`SIM108` in `controller/taxis.py`, `RUF059` in `tests/test_taxis.py`); neither
file was changed here and the focused changed-surface checks are green.

**In progress (preregistered and red-teamed 2026-09-26 12:26 PDT; no neural
outcome inspected):** H-RETINO-SURPRISE-RECURRENCE is the separate next
experiment. It is a 32-stimulus synthetic premise killer for the corrected neural
surprise decoder: 32 fixed changed stimuli are each run under real, one
degree-preserving normalized rewire, and recurrent gain zero, yielding 96
changed condition-trials plus three no-change controls. Legacy is only a second
decode of the real traces. The trivial alternatives, stimulus, float32 update,
encoder mapping, state fork, reduction, thresholds, contracts, outcome mapping,
stop rule, artifact provenance, exact command, and expected failure are frozen
in `EXPERIMENTS.yaml` before implementation. It uses no Python controller or
click head.

**Measured preregistration audit:** three independent read-only reviews found
and repaired the protocol before code was written. The original exact golden
at grid row 12/column 49 was impossible because the 64-to-eye affine map
quantizes its marginal axes to row 13/column 50. A later joint-occupancy check
found that 13/50's corresponding (hex1=8,hex2=31) pair is unoccupied. Exhaustive
enumeration found 873 occupied, exactly round-trippable off-diagonal grid pairs;
the final golden is row 20/column 50, which maps to occupied
(hex1=12,hex2=31) with 26 annotated neurons and returns legacy (20,50) versus
corrected (50,20). This correction happened before the probe or any neural
state was run. The loaded null preserves its signed-weight multiset only before
incoming-L1 re-normalization, not in the matrix the probe will run. Its final
weight standard deviation is 0.0199551 versus 0.0145400 in real, although node
degrees, signed counts, and incoming-L1 normalization match. The eight mirrored
fixed centers share h4 baselines and are not independent replicates, so the
invalid sign-test p-value was removed. Seven-of-eight remains only a
preregistered descriptive consistency bar; null seeds are the replication
units for graph-organization claims.

**Measured final contradiction audit before freeze:** the hypothesis is now the
exact conjunction its verdict will test, rather than a broad “better than”
sentence with narrower hidden gates. The protocol freezes
`h <- (1-a)h + a*tanh(g*W*h + u + b)` in float32 with `W[post,pre]`, fixed input
for K=4 synchronous steps, the literal colour-to-type projection, and
recurrence-off using the byte-identical real CSR with gain as its only effective
difference. All three conditions must hash to identical drives. The probe must
check explicit degree/sign/normalization invariants, including 389 zero-input
rows and nonzero-row L1 error <=3e-4; the frozen real/null manifest hashes are
now in the registry. Both FlyTiebreaker saliency construction paths and active
convention reporting are required so a standalone probe cannot pass while
deployment remains transposed.

**Claim boundary fixed before observation:** fly dynamics produce the expected
and actual rate states; Python computes their absolute difference, bin sums,
and argmax. The experiment therefore tests whether real recurrence sharpens an
engineered retinotopic code under this MaleCNS-derived rate model, not whether
the living fly computes prediction error. ARC colours are arbitrarily assigned
to 15 visual cell-type channels, the same 23,720 directly driven neurons are
decoded, and the null does not preserve cell-type/column blocks. The <=4-cell
bar is prior-calibrated, the 20% control margin is assumed, prior-panel overlap
cannot be certified, and this is a developmental retest rather than independent
confirmation. Contract failure is invalid; a contract-valid scientific gate
failure stops the branch; a full pass earns only a separately preregistered
score-adjacent assay.

**Measured preregistration validation at 12:39 PDT:** `EXPERIMENTS.yaml` parses
with the hypothesis open, 9 explicit assumption/limitation entries, and 19
frozen protocol fields; `git diff --check` passes; `tests/test_league.py` passes
4/4; and the regenerated `LEAGUE.md` reflects the narrowed claim. A final
read-only contradiction pass reported the protocol freeze-ready with no
remaining checkpoint blocker. No neural outcome was inspected while selecting
or auditing the protocol.

**Measured pre-implementation correction after that review:** the first test
fixture exposed that checking each decoded axis independently is insufficient;
the joint eye column must also exist. The supposedly exact 13/50 golden had no
mapped neuron in the real retinotopy asset and would have made the probe invalid
by construction. The registry and implementation now require occupied 20/50.
This is a contract correction from static anatomy metadata, not a post-result
threshold or panel change; the 32 scientific stimuli and every outcome gate are
unchanged.

**Measured correction validation at 12:54 PDT:** an independent read-only audit
recomputed the real retinotopy SHA, affine encoder/inverse decoder formulas,
26 unique mapped indices, and all 4,096 grid pairs; it reproduced 873 occupied
exact-roundtrip off-diagonal candidates and reported the corrected golden
freeze-ready. `EXPERIMENTS.yaml` still parses open with 9 assumption/limitation
entries and 19 frozen fields, `git diff --check` passes, and `LEAGUE.md` was
regenerated. No neural state or outcome was inspected.

**Measured implementation checkpoint at 13:14 PDT; still outcome-blind:** the
registered decoder convention is now an exact fail-closed enum. Every historical
config defaults to `legacy_hex1_x`; the single-delta child explicitly selects
`arc_x_hex2`; and both the primary FlyTiebreaker saliency path and the separate
surprise-reclick construction receive the configured convention. The decoder
still computes the same two unnormalized axis-bin sums and the correction only
swaps those arrays byte-for-byte. Module and controller prose now keeps the
claim at its measured tier: fly rate dynamics produce two states, while Python
forms their absolute difference, bin sums, and argmax.

**Measured production round-trip contract:** the actual categorical
`ColumnarColourProjection`, not a duplicate formula alone, maps
`grid[row=20,column=50]` to `(hex1=12,hex2=31)`. Changing only that grid cell
changes exactly encoder histogram key 459. The real asset has 26 neurons at
that occupied column (sorted-index SHA-256
`9197bc795eb62a42e921c3745d63098b92c6d1e82c0fcada0cb7ad240644820c`), exactly
the same set selected by the inverse decoder; legacy returns `(20,50)` and the
corrected convention `(50,20)`. A synthetic swapped-row/column regression fails
this contract. Static enumeration also reconfirmed that all eight frozen panel
centers are occupied and each 5x5 patch reaches 6-12 occupied eye keys. None of
these checks advances a neural state.

**Measured probe implementation:** `scripts/probe_retinotopic_decoder.py`
constructs no policy, controller, click head, action selection, or reclick
path. It runs the exact 32 registered changed stimuli under real, the one frozen
degree-preserving null, and gain-zero on the same live real CSR; legacy is only
a re-decode of the real traces. It asserts the frozen asset/config/null/matrix
contracts, declared and effective float32 gain-only real/off difference,
six-thread execution, identical cross-condition drives, byte-identical h4
forks, exact no-change states, finite positive changed saliency, reduction
order, conjunctive gates, and immutable output refusal. Contract-valid failure
returns 2 under `--require-promotion`; invalid/runtime failure returns 1 with a
parseable diagnostic envelope. Result content remains ignored by Git.

**Measured pre-outcome red team:** two failure-path blockers and one golden
blocker were found and repaired before the frozen command was run. Nonfinite
saliency could have made `allow_nan=False` truncate the invalid artifact;
nonfinite trials now fail before raw arrays are recorded and residual diagnostics
are JSON-sanitized. Real/off compared declared rates but not their effective
float32 values; both representations are now independently load-bearing. The
golden initially exercised only the decoder; it now exercises the production
encoder and proves that its 26-neuron column is the decoder's column. Synthetic
regressions kill all three defects. A final independent contradiction audit then
reported no remaining freeze blocker. The known nonblocking durability limit is
that a hard SIGKILL or power loss after exclusive path reservation but before
final serialization can leave a zero-byte output that must be preserved and
diagnosed rather than silently overwritten.

**Measured validation:** focused config/saliency/FlyTiebreaker/probe tests pass
83/83; the complete suite passes 444/444 in 27.79 seconds; focused Ruff check
and format, Python compilation, YAML parse, and `git diff --check` pass. The
child config SHA-256 is
`cac389dfef042f6f8f26cd0dc17d514a101016ce3373e99ade48ac10866f03a1`; probe
source SHA-256 is
`7014495a3ae043dbe92bba40bf597af72704d701e984a2a291c980aa560012de`; its
synthetic test SHA-256 is
`53548e7802bb7ac8068d0dde0e54ed39656c0e94a9a1c3421afd2e40ab21f7c2`.
The registered result path does not exist. No neural outcome has been run or
inspected. The only allowed next action is to checkpoint and push this clean
implementation, then run the exact frozen command once without tuning.

**Measured frozen result at 13:16 PDT:** the implementation was committed and
pushed first as `7a1b104`, with no tracked dirtiness at run time. The exact
registered command completed in 14.44 seconds and wrote the ignored 594,452-byte
artifact at `results/connectome_agent/retino_surprise_arcxy_probe.json`
(SHA-256
`5de6f8d465b48cace3bd0a360c5adc8c50a2671e670c0d7d838ab271a2f9b58e`).
The artifact is contract-valid: all frozen config, asset, graph, null, matrix,
thread, panel, drive, fork, no-change, finiteness, real/off, and action-path
checks pass; it contains 96 changed condition-trials, 32 legacy re-decodes and
three exact no-change trials. Its Git record shows commit `7a1b104`, branch
`main`, tracked clean, with only the disclosed unrelated untracked
`.fly-or-fake-work/`. EXPERIMENTS-at-run SHA-256 is
`a28daa5ead3f88171f52f960dc2d94dd40f56ba6260196e63c32793f0aabbb27`.

**Measured coordinate result:** the mechanical repair passes completely.
Corrected-real global median error is 1.310660 ARC cells versus 35.009019 under
the legacy transpose; corrected is strictly better at all 8 paired centers and
comfortably passes the <=4-cell absolute gate. This supports only the corrected
axis contract and fixed-panel localization measurement.

**Measured dependency result and preregistered stop:** real recurrence does not
pass the anatomy/control conjunction. The degree-preserving null median is
1.560660, so real/null is 0.839811 rather than <=0.8, and real is strictly
better at only 3/8 centers rather than >=7/8. Recurrence-off median is 2.118034,
so real/off is 0.618810 and passes the global 20% margin, but real again wins
only 3/8 centers. The exact H-RETINO-SURPRISE-RECURRENCE conjunction is therefore
**refuted** on this fixed panel; it is not a claim that living-fly vision lacks
the capability. Per the frozen kill rule, this branch ends here: no threshold
change, alternative pooling, substitute decoder, new panel, ARC replay,
behavior battery, or Kaggle submission. The explicit convention and goldens
stay as correctness repairs.

**Next scientific branch, not yet preregistered:** the native visual-projection-
neuron -> visual-KC -> MBON route remains the smallest genuinely different fly
mechanism with a plausible path to within-game generalization. Before code, its
32-episode one-shot delayed-match 2AFC premise killer must freeze exact MaleCNS
population extraction, sensory placement, state/reset timing, plasticity
equation and site, chance/no-plasticity/cue-shuffled controls, a locally matched
degree/sign/weight-preserving anatomy null, metrics, thresholds, artifact
contract, and kill rule. No ARC integration is earned unless real anatomy beats
every trivial and matched control.

Process audit at 12:02 PDT found and stopped this session's stale
completed-validation gateway on localhost port 8032; a separate pre-existing
gateway on port 8031 belongs to another workflow and remains untouched. No
evaluator or queue waiter is active, and no Kaggle submission is authorized or
queued.

**Scientifically grounded follow-on if the coordinate correction is not enough:**
the strongest genuinely new fly program is the native visual-projection-neuron
→ visual-KC → MBON route. The graph contains 1,615 direct edges from 251 visual
projection neurons into 332 KCs, unlike the prior MB assay's invented global
colour-histogram → olfactory-PN bus. Its cheapest gate is a 32-episode one-shot
2AFC delayed-match probe against chance, no-plasticity, cue-shuffled, and exact
degree/sign/weight-matched local rewires before any ARC integration.

## Parallel Experiment 000 draft checkpoint — 2026-09-23 15:17 PDT

Experiment 000 planning is paused at a clean documentation-only checkpoint on
the isolated branch `codex/experiment-000`. No implementation code was added,
no experiment was launched, and the shared FlyARC checkout was not edited.

The checkpoint adds a detailed mushroom-body associative-learning protocol at
`experiments/000_mb_sanity/SPEC.md`, a scope/resume guide at
`experiments/000_mb_sanity/README.md`, and the experiment's durable record at
`experiments/000_mb_sanity/WORKLOG.md`. The draft now freezes the intended
MaleCNS populations and runtime blocks, trial state machine, paired-world task
battery, conservative exact-degree Curveball null family, primary controls,
statistical reductions, evidence labels, analytic kill tests, and additive
migration boundary. Independent audits covered equations/state transitions,
nulls/statistics, repository migration, biological sources, and internal
contradictions.

This is deliberately marked **PAUSED / DRAFT**, not preregistered or ready to
run. Resume from the experiment worklog's pause checkpoint. Before any code or
data work, close its four remaining specification items: recovery-only
semantics, exact Curveball sweep/telemetry and fresh-replication wording, the
remaining scalar/golden-test ledger, and a final clean contradiction audit.

## Mainline integration checkpoint — 2026-09-23 19:56 PDT

**Measured:** `main` accepted the documentation-only Experiment 000 checkpoint
as merge commit `c9f6323`; the merge adds the three files under
`experiments/000_mb_sanity/` and the 15:17 root-log entry, with no source,
configuration, result, data, or generated-artifact changes.

**Measured:** the previously untracked `CLAUDE_CODE_REFACTOR_HANDOFF.md` is now
being tracked as a historical coordination record, with an explicit notice that
its old queue-launch instructions are closed rather than current. The unrelated
`.fly-or-fake-work/` tree remains untracked and untouched by this integration.

**Measured:** a read-only review of the ARC closure found bounded record repairs
still required before it is canonical: the stopped surprise checkpoint contains
19 rows rather than the reported 18; completion episodes were described as
distinct-game breadth; a null colour-map comparison was overread as equivalence;
the T4/T5 hypothesis status is stale across the registry and league; statistical
resample counts differ; and the validator/source-equivalence language exceeds
the checks recorded by the tooling.

**Inferred:** those closure repairs require a small documentation/registry and
analysis-replay checkpoint, not another full ARC evaluation, assuming the
existing immutable bundles remain unchanged. Claude Code may continue on
ARC-specific surfaces after that repair; it must not move shared modules or edit
Experiment 000 while the additive refactor boundary is being established.

**Measured:** no `evaluate_state_graph` job was active at integration time, but
obsolete watcher shells and orphaned multiprocessing workers from old ARC runs
were still resident. They should be stopped before another queue is armed so an
old condition cannot trigger unexpectedly.

The next Codex action remains the four-item Experiment 000 specification audit
listed above. Physical relocation of FlyARC remains deferred until additive
Experiment 000 namespaces and compatibility goldens exist.

## Everything goes through the fly, or nothing goes at all

This is the project's first principle and it outranks every other consideration
in this repository, including the score.

FlyGI exists to find out what the fly's innate wiring computes for free. A
component that produces a result *without* the connectome carrying it is not a
smaller version of that finding -- it is a different project wearing this one's
name. So:

1. **Every computation the agent depends on must be performed by fly neurons.**
   If a capability can be obtained by writing Python instead, writing the Python
   is a failure, not a shortcut. The controller diffing grids in Python while
   13,585 T4/T5 motion detectors sit unread is the canonical example of the
   mistake.
2. **Encoders, decoders and transformations exist only to make fly modules
   usable.** They are plumbing, and their job is to hand a fly circuit the kind
   of input it evolved to read and to take from it the kind of output it evolved
   to produce. They are not where the intelligence is allowed to live. Any
   parameter in the plumbing that starts doing real work is a bug.
3. **A circuit must be given input it can actually use before any claim is made
   about it.** Measured on 2026-09-23: the mushroom body was taught while
   receiving 0.00% of its input from any driven sensory population, and the
   motion and object detectors were evaluated on spatially scrambled input. Both
   produced nulls. Neither null was about the fly.
4. **When a fly module cannot do the job, say so plainly and stop** -- do not
   quietly substitute an engineered component and keep the name. A recorded
   limit of the connectome is a real result. A scaffold that scores while the
   connectome idles is not.

The test to apply before adding anything: *if the connectome were replaced by a
degree-preserving null tomorrow, would this component still work?* If yes, it is
not part of this project.

## Why FlyGI exists

FlyGI puts the complete MaleCNS v1.0 fruit-fly central-nervous-system graph into
the decision loop of ARC-AGI-3:

```text
ARC frame + action history
        -> sensory interface
        -> 166,700-neuron MaleCNS graph
        -> persistent dynamics / local learning
        -> neural-population readout
        -> legal ARC action
```

**The essence of the project, stated plainly: what computation does the fly's
innate wiring give us for free?** Not a network trained on the fly's shape, not
a network initialized from the connectome and then fitted -- the measured
synaptic graph itself, frozen, with its evolved modules doing whatever they
already do. The mushroom body's 4,064 Kenyon cells and 97 MBONs, the central
complex's ring attractor, the optic lobe's 892 retinotopic columns: these
circuits were shaped over roughly 400 million years for foraging, navigation and
learning in a real world. The question is how much of that transfers, unpaid, to
a benchmark nobody evolved for.

This is why every engineered component in this repository is on probation. A
scaffold that scores well while the connectome sits inert is a negative result
about the fly, however good it looks on a leaderboard. Whatever the agent scores,
the number that matters is the gap between the real graph and a degree-preserving
rewiring of it, because that gap is the only part that anatomy can claim.

The engineering goal is a valid, reproducible leaderboard agent that genuinely
executes the full connectome on every decision. The scientific question is
narrower and more demanding:

> With the interface, dynamics, training budget, parameter count, action budget,
> and seeds held fixed, does evolved MaleCNS wiring make any ARC-relevant
> computation more accessible than a degree-matched rewire, matched artificial
> reservoir, or no-recurrent-graph bypass?

The tracks remain distinct:

- **Track A — Literal Fly:** fixed interface, zero ARC-trained parameters.
- **Track B — Frozen Fly:** frozen graph plus a small trained interface/readout.
- **Track C — Plastic Fly:** constrained local plasticity at a declared
  biological site.

A high score proves only that the whole engineered agent performs well. Credit
goes to the fly only when the real graph beats controller-only, bypass, and
matched graph controls. A zero score does not show that a biological fly lacks
intelligence: a connectome is anatomy, not a complete brain emulation.

## Coordination checkpoint — 2026-09-23 13:21 PDT

Created `CLAUDE_CODE_REFACTOR_HANDOFF.md` at Mustafa's request as the explicit
boundary between the live FlyARC queue and the incoming Experiment 000
mushroom-body refactor. No process, config, source module, result artifact,
commit, or remote was changed as part of this checkpoint.

Measured locally while preparing the handoff: `sg-bioeye-lc-permuted` and
`sg-bioeye-t4t5` were healthy and checkpointed; the two decoder arms had an
armed waiter; no launcher existed for the four registered `sg-mbdr-*` arms.
The operational decision is to finish and close the four already-running/armed
bio-eye/decoder arms, then **not launch the legacy MBdr battery**. Experiment 000
supersedes its PN/DAN selectors, dynamics, plasticity scope, and non-degree-exact
rewire, so deferral is a priority decision rather than a falsification of
H-MB-LEARNING. The handoff records exact config hashes, recovery behavior,
closure checks, ownership, and the staged logical-first refactor plan.

### Handoff adopted — Claude Code, 2026-09-23

The handoff above is adopted as the operating contract for the remainder of the
ARC queue. Confirmed at adoption: all four config SHA-256 values match the
handoff's frozen table; HEAD is the inspected `96353dd`; the decoder waiter is
armed; both active arms were at 68/75 and advancing. Until all four bundles
exist: monitor-only on the read-locked surfaces, no tuning from partials, no
duplicate launches, and the `sg-mbdr-*` battery is not launched -- reversing
this session's earlier plan to queue it, as a priority decision. Closure work
(artifact validation, declared comparisons with the preregistered 19/9/25
endpoints, the smallest endpoint analyzer if still needed, provenance and
source-equivalence audit including the git_dirty=2cf2098 mixed-launch caveat,
closure report, one tested closure commit) begins only after the fourth bundle
lands.

### Incident: repo-wide format touched the foreign workspace — 2026-09-23

A `ruff format .` during closure descended into the untracked
`.fly-or-fake-work/` directory and reformatted 7 Python files there, violating
the do-not-touch instruction. Formatting is semantics-preserving and the two
tracked modifications in that repo's own git predate the incident (ruff does
not format JSON), but its owner should review with their own `git diff`. No
revert was attempted -- most touched files are untracked there, and a revert
could destroy real in-progress work. Recurrence prevented: `.fly-or-fake-work`
is now in ruff's `extend-exclude`, and repo-wide format invocations are
avoided in favour of explicit paths. Disclosed to Mustafa immediately.

### Battery verdict: 0.5519 under real rerun semantics -- 2026-09-26

The full 25-game local gateway battery (competition mode, record=True,
uncapped actions, 35-minute deadline = 1/14th of the real budget):
scorecard 0.5519 -- above the old capped-offline combo (0.3519), above
the official random-sample LB bar (0.18-0.25), with ft09 (a dead-
taxonomy game) completing level 1, ten games scoring, 80,941 actions and
zero thread exceptions. The fixed+uncapped+light candidate is packaged;
kernel verification in flight; submission awaits the user's explicit go
(they killed the auto-submitter). Expected-tier statement with the
project's 0-for-12 base rate on score predictions: with a 2-5x hidden
shrink, the first nonzero leaderboard score is plausible, not promised.

### The six zeros explained: a construction crash invisible to exit codes -- 2026-09-26

The user-directed deep dive (forum mining + harness source + a local
competition-mode gateway) produced the full answer in three layers.

LAYER 1, THE BUG (measured): every Kaggle submission's agents crashed at
CONSTRUCTION. Swarm passes record=True; the base Agent.__init__ calls
start_recording(), which reads agent.name; our name override read
self._mode, set only after super().__init__ returns. AttributeError in
the swarm thread; main.py exits 0; the return-code check passes; the
pre-opened empty scorecard scores 0.00. Six submissions, zero actions
ever played. Every local test had passed record=False -- the single
condition that differed. The fix is two class attributes and a
regression test; the lesson is the new mandatory pre-submission gate:
the local gateway battery (arc_agi competition mode + vendor main.py,
record=True) that found this in two minutes.

LAYER 2, THE BUDGET (measured from forum + harness source): no server
action caps, no rate limits; extra actions can never lower a level's
score; scoring teams run 8h54m-9h11m; the official random sample scores
0.18-0.25 LB. Our 600-action self-cap used <1% of the interaction
budget. Now: MAX_ACTIONS 200k, deadline 8.4h, transport retries,
random-legal fallback on policy errors (the uncapped regime reaches
graph states the cap never saw), light deploy profile (tie seat off --
measured inert four ways). Audit correction on 2026-09-26: the retinotopic
head uses static anatomy metadata but no neuronal or synaptic computation, so
this light profile is not load-bearing-fly under the repository directive.
Replay-by-duplication measured dead at the gateway: duplicates share one
server session.

LAYER 3, THE FIELD (sourced): the public set is officially easier than
the hidden set (~2-5x community shrink); every >10-scoring team is a
Duck-harness LLM-REPL lineage; 0.35 local was never going to display.
With the bug fixed and the budget used, the honest target is beating
the 0.18-0.25 random-sample baseline -- a bar our uncapped lp85 result
(level 1 at 112.89/115, better than human baseline, in the real online
flow) suggests is now reachable.

### Submission 6 armed: the combo candidate, every bar passed -- 2026-09-25

sg-combo (defrag similarity-novelty tags + retinotopic deadline click
head) measured 24 levels / 0.3519 -- the highest arm score recorded,
above both parents -- and produced the FIRST level-2 completion in the
project's ~1,400 rows (vc33 seed 1, advance steps 64 and 596, official
scorecard confirms). BAR A passes both clauses with no override; BAR B
stands on the head's two replicated scrambled-map pairs; BAR C passed on
the packaged agent (both mechanisms verified engaged through the official
framework loop) and again in the kernel log itself (preflight names
click_head retinotopic, deadline 100, state_similarity retino_tags; run
clean). Kernel v8 built against the verified dataset version -- the
stale-dataset race that caught v6 is structurally avoided this time by
waiting on dataset readiness before pushing. Submission fires
automatically when the quota opens (17:00 PDT), per the original
preregistered mechanical rule. Claim discipline: the defrag mechanism is
recorded as ENGINEERING (fly-parity measured); the fly is load-bearing
in the head, where two twin pairs say so.

### Submission 5 scored: 0.00 -- 2026-09-25 ~06:00 UTC

The hidden set returned 0.00, the fifth consecutive zero, including the
champion's own 0.00 (submission 4, local 0.2034). MEASURED lesson, stated
plainly: the entire local score band -- champion 0.20 through click-head
0.31 -- converts to zero on the hidden games. Our local score mass is
three public games (tn36/lp85/r11l) whose level 1 falls to wandering and
whose clicks the head reads well; the hidden set evidently contains no
such freebies, so per-completion efficiency gains multiply zero
completions. The leaderboard pays what BAR A was defending all along:
P(complete anything on an UNSEEN game) -- breadth first, efficiency
second. The user's score-first bet was worth taking and is now priced:
the local-vs-hidden gap, not the local ranking, is the binding problem.
Constructively, this re-points at the fragmentation attack (fly-hash
state keys + MBON novelty): better exploration is the only lever that
plausibly moves P(first level | unseen game).

### SHIPPED: submission 5, the retinotopic click head -- 2026-09-25 04:08 UTC

Submission 56539536, PENDING: the clickhead-deadline candidate (retinotopic
click head in the primary ranking term, deadline 100, fly tie-break intact,
modulators graph). Shipped on the user's explicit Bar A override ("score is
what counts"), with BAR B passed twice (retinotopy load-bearing, 0.306/
0.3058 vs 0.1875 permuted) and BAR C verified two ways: locally through the
official framework loop (80 head updates in 80 actions) and in the kernel
log itself (FLYGI_PREFLIGHT names click_head retinotopic, deadline 100).
The preflight instrumentation earned its keep: kernel v6 was caught running
the PREVIOUS dataset version (click_head none) and was not submitted; v7
verified before the slot was spent. Local reference: 0.3058 vs champion
0.2034. All four prior submissions sit at 0.00 public score, so any
nonzero result is a project first. Pixel-patch arm still running; its
frozen interpretation applies to the claim wording, not to this ship.

### H-MBON-DAN-METAPLASTICITY: the fly's RSI loop, measured link by link -- 2026-09-24 ~21:45 PDT

The RSI deep dive's verdict, converted from prediction to measurement. The
fly's one native second-order learning circuit -- learning changes MBONs,
MBONs feed back onto dopamine neurons, dopamine gates future learning --
exists in our graph (2,589 edges, 338/340 DANs fed), and it turned out to
be already mechanically closed in the shipped machinery: the gate reads
DAN activity from the very network the plastic synapses live in.

The twin-trajectory experiment (learner vs weight-frozen twin on identical
streams; the twin IS the severed-feedback ablation; the first attempt's
read-only crash exposed that a shared bundle would have aliased the weight
arrays and hollowed the comparison -- twins now load independently with a
shares_memory assertion) measured every link: weights move (3.4-61 absolute
change), MBON activity diverges hugely (up to 50%), and then the MBON->DAN
stage crushes it ~250-500x: the gate the learner receives differs from the
never-learned counterfactual by 4e-5 to 2e-3, rising briefly and then
PLATEAUING in every game. Bounded convergence. No compounding. The fly's
recursive loop is real anatomy, working mechanics, and negligible dynamics
-- and it modulates a first-order mechanism already measured three times
at zero score conversion.

### H-CONSEQUENCE-COUPLING day one: the map is load-bearing; the shape is not shippable -- 2026-09-24 17:05 PDT

The full ladder, measured. The headline that HOLDS: the fly's retinotopic
map is load-bearing -- real map completes level 1 at 2.59x human baseline,
the scrambled-map twin at 11.59x, identical machinery otherwise. A 4.5x
efficiency separation attributable to retinotopy itself, the first time in
this project a fly-anatomy component beat its matched control on the
metric the benchmark pays. Score 0.3064, the highest arm mean recorded
(champion 0.2034), concentrated exactly where the offline premise said it
would be (r11l completions at 0.27-0.68x baseline; lp85 1.12-1.94x).

The headline that DOESN'T: both bonus shapes lose breadth (17 levels vs
21; 6-7 games vs 10), so BAR A fails twice and nothing ships -- the slot
is unspent, per the mechanical rule, despite the record score. And my
registered inference about WHY -- suppression starves discovery -- was
refuted by its own calibration arm: boost-only (negative_scale 0) still
loses three of the four games. The redirect toward frame-changers is
itself what starves the broad wander in those games. Chasing "make
something happen" is not the same objective as "find the advance".

Standing: mechanism real, fly-attributed, not yet shippable. Next
registered candidate (not built tonight): a stall-gated head that stays
silent while default exploration is still finding novelty. Base-rate
discipline: this is inference-failure number twelve on score-adjacent
bridges; the measurements, as usual, all held.

### H-JEPA-SPONTANEOUS: closed null, and the control that earned its keep -- 2026-09-24 15:10 PDT

The full preregistered record is in results/jepa/probe_results.json. No
tier passes: at the k=1 change-masked deciding cell the fly's state loses
to the current observation (-0.011 median, p=0.47), loses to the rewired
null (-0.048, p=0.21), and only noise separates it from the no-recurrence
bypass (+0.023, p=0.31). The decisive measurement is the shuffled-time
control: +0.038 -- exactly the real arm's own number -- so what looked like
25/25 games above the copy floor was static within-game structure passing
the change mask, not prediction. Without that preregistered control the
headline would have been wrong in the flattering direction.

Answer to the day's founding question: no -- fly biology does not
spontaneously give N_t JEPA-like predictive structure at this operating
point, on this drive, read linearly. Same-day convergent evidence: the
consequence premise-killer measured the recurrent state at 0.55 AUC on
action-consequence -- below the raw action id -- while the observation
sits at 0.74. The connectome's dynamics blur task information the
observation already carries; the project's live positives remain the
ENCODER side (bio-eye retinotopy), which is exactly where the click head
now places its bet. State caches deleted per the registered disk plan
(regenerable deterministically; 2.8 GiB free).

### H-CONSEQUENCE-COUPLING: the retinotopic click head, built and gated -- 2026-09-24 ~15:30 PDT

The build the premise tests earned. src/flygi/controller/click_head.py: an
online per-game logistic head (401 parameters, zero at start, deterministic
SGD with running class-balance weights -- ft09's measured 5.8% positive
rate drives an unbalanced learner to "always no") that reads the 5x5 patch
at a candidate click through the fly's compiled cell->column map, each
patch cell contributing its retinal column's colour histogram. Its signed
prediction enters the PRIMARY ranking term scaled by the exploration
term's own 1/sqrt(1+evidence) decay: a prior for untried candidates that
measured effects replace. The first divergence gate caught the unscaled
version overriding the controller on 88% of turns -- never the design --
and the evidence scaling brought it to 69%, concentrated on the untried
frontier.

Gates, measured: knob-off replays the champion byte-for-byte (2 games,
replay hashes MATCH at the champion's 600-action budget -- the first gate
attempt failed on a wrong default budget, my command not the code); knob-on
diverges and learns (588 updates in one game). Tests: 7 new, including the
two comparison tests AGENTS.md requires in the same commit -- the head
beats rote coordinate memory by >0.2 AUC at coordinates neither has
clicked, and the permuted-map control destroys the locality signal.

Arms launching (champion recipe + one knob, endpoint levels and per-level
action cost first): sg-clickhead-retinotopic, then controls
retinotopic_permuted / pixel_patch / rote. Load-bearing bar: retinotopic
beats permuted; honesty bar: pixel_patch tells us what a fly-free patch
does. EXPECTED tier reminder: the base rate for score predictions in this
repository is eleven straight nulls.

### H-RECLICK-SEAT: the seat works; the fly's hand is too light -- 2026-09-24 13:25 PDT

Verdict, 75 rows per arm, validation PASS: sg-reclick-fly is outcome-
identical to the champion on all 75 rows -- breadth 10/25 on the same ten
games, 21 levels, 0.2034, delta +0.0000 with a zero-width CI. The
preregistered Branch A bar (breadth > 10/25 AND beats griddiff) fails;
the submission slot stays unspent, per plan.

The control is the informative half. sg-reclick-griddiff diverged from the
champion on 5 rows and HURT: 19 levels, breadth 8/25, 0.1937. So the
attribution question inverted: the reclick seat demonstrably CAN change
outcomes -- the trivial writer broke two levels through it -- while the
fly-surprise writer never moved one decision that mattered. The fly's
deposits (surprise at the clicked coordinate, decayed, mass-capped) were
apparently always below the threshold where the preference reranks a
click that changes anything. Fourth consecutive null on a seat mechanism,
and the sharpest: the lever works, the fly's signal through it is too
faint.

### H-JEPA-SPONTANEOUS: the red-team's blocking find, and the frozen protocol -- 2026-09-24 ~12:15 PDT

The 3-agent design review paid for itself before lunch. Its blocking find:
the equipped null bundle rewired the WRONG parent graph. The bio-eye
gain-2.0 config loads literal-rate-signed-MODULATORS (24,994,595 edges);
the null was a rewire of literal-rate-signed (24,559,055). Any B3 gap would
have confounded anatomy with the 435,540-edge modulator set. A matched null
is rebuilding from the modulators graph; the old null is superseded for
this test. Second trap caught: column_histogram returns the full 1,404-cell
hex lattice but only 892 columns carry neurons -- an unmasked target would
have scored the probes on screen regions the network physically cannot see.

The amended protocol is FROZEN in EXPERIMENTS.yaml
(protocol_frozen_2026_09_24) before any probe ran: change-masked pooled R^2
as primary (ARC streams are persistence-dominated; unmasked R^2 rewards
predicting "nothing changes"), an explicit copy floor B0a, best-of-L delay
baselines, a random-nonlinear-expansion baseline B2' (without which
"beats linear history" cannot support "latent structure"), a history oracle
whose defeat by N_t is registered as a leakage red flag rather than a win,
ESP-derived washout, game-level lambda CV, 5-fold CV by game, Wilcoxon over
25 per-game paired deltas at the k=1 change-masked cell.

Pipeline: capture (25 games x 401 frames, done) -> states (real/bypass
collecting; matched null after rebuild) -> ESP test (running) -> probe
(scripts/jepa_probe.py, machinery validated on a synthetic linear world:
horizon-0 decode 0.999, shuffled-time control collapses to -0.92, copy
floor arithmetic verified).

### H-JEPA-SPONTANEOUS: does the fly's state already do JEPA's job? — 2026-09-24

Mustafa's question, made falsifiable: JEPA trains an encoder so latents carry
predictive structure; the connectome's dynamics might supply it for free --
`advance(N_t, drive)` is already a zero-trained latent predictor (the surprise
decoder, 3.5-cell localization, is its error signal). Registered
H-JEPA-SPONTANEOUS with preregistered claim tiers: N_t's linear-probe
prediction of x_{t+k}'s column representation must beat (B1) the current
observation, (B2) a capacity-matched observation HISTORY, (B3) a
degree-preserving null's state, (B4) a no-recurrence bypass -- weak/medium/
strong tiers respectively; game-disjoint splits; shuffled-time collapse
control. Probes are ridge only: nothing trains in the network, so this asks
whether biology already did the training.

Assets equipped: sklearn added; retinotopy.npz copied into the null bundle
(node ordering preserved across nulls by construction -- verified claim
delegated to the design red-team). A 3-agent design review (methods norms,
adversarial leakage/fairness attack, compute budget) runs before any pipeline
code; its required_changes bind.

Parallel context: the H-RECLICK-SEAT arms occupy 8 threads until ~14:10; the
probe uses the remainder now and the full machine after. The 16:00 submission
fork is unaffected.

### H-MB-LEARNING-DENSE: verdict — null, verified live, slot unspent — 2026-09-24

The arm completed faster than projected (75/75, validation PASS, matched
coverage). Against sg-mbdr-nolearn: **-0.0004, CI [-0.001,+0.000], p=1.000;
breadth 6/25 v 7/25; levels 15 v 16.** The suspicious four-decimal identity
with the sparse arm was checked before recording: the bundle carries
dense_reinforcement=true and only **5/75 replay hashes** match the sparse arm
-- dense dopamine changed play on 70/75 games, and the outcomes converged to
the same clears regardless. A genuine null, not a dead switch.

Ship gate: failed at condition 1 (no separation). **The slot is not spent
tonight**, exactly as the preregistered expected outcome said. Controls stay
gated -- there is no effect to falsify.

Standing conclusion, inferred tier: three learning nulls of increasing
strength (invalid signal -> fair sparse -> dense balanced action-dependent)
now bracket the mechanism. The learning WORKS -- weights move, behaviour
changes -- and the tie-break seat does not convert changed behaviour into
changed outcomes. The bottleneck has moved from signal to SEAT. Tomorrow's
candidates by elimination: hidden-failure forensics (the workflow's own
'missing' list, item 1), and the unanswered structural question of a larger
safe seat for the fly -- noting honestly that a larger seat was never safely
tested, only noise-in-the-same-seat (which hurt).

### H-MB-LEARNING-DENSE: today's candidate, measured into existence — 2026-09-24

A 12-agent workflow (ground -> 4 proposal lenses -> adversarial kill panel ->
synthesis) produced one survivor: **dense opponent dopamine**. The fair null's
proven-dead entry is scoped to its 31:1, ~8-events-per-episode signal; this
changes exactly that variable. Canonical-novel-and-changed destinations send a
small reward to PAM, NOOPs a small punishment to PPL1, familiar EFFECTs stay
silent; etas sized from measured medians (513 novel / 14 NOOP per row) with a
2-terminal-equivalent budget and hard per-side caps.

Measured before implementation: dense outcomes are action-dependent (novelty
p<0.05 on 70/75 rows sha-based, 64/75 change-gated; null 3.8) -- the signal can
carry credit. Supporting regularity from the evidence-mining lens: **29/38
level-clearing clicks re-click a coordinate that previously changed
something** (clicks advance at 1.79x the per-use rate of other actions) --
precisely the scene-x-action pattern this signal lets the mushroom body learn
within a game. Kill panel: survives all five refutation criteria.

Implemented config-gated (`dense_reinforcement`, default false; 4 new tests;
395 pass). `sg-mbdr-learn-dense` preregistered (breadth primary vs 7/25;
LEDGER-WIN bar CI>0; SLOT-RELEVANCE bar >10/25; controls gated) and running.
Honest expectation, recorded: the slot is NOT spent tonight unless every
ship-gate condition holds, including a mechanism-level account of the
10/25-to-0 hidden conversion.

**Backup branch, measured and parked:** the candidate-admission caps
(policy.py `_candidate_metadata`) were accused of index-order truncation.
Measured on 3 click-heavy no-progress games, 400 click turns: the tier cap
never binds (0%), the component cap binds on 18% of turns, median
present==offered (62==62). Real but marginal; parked with its numbers, behind
dense and hidden-forensics.

### H-MB-LEARNING: the fair test, and a fair null — 2026-09-24

The revived battery ran clean (validation PASS, 75/75 both arms). Learning
against its matched baseline: **-0.0004, CI [-0.001, +0.000], p=1.000** --
levels 15 v 16, breadth 6/25 v 7/25. Null, with nothing left to blame: sensory
content, biological sparsity, rectified credit, and action identity were all
verified present before launch. Real weight moved at the real site and the
controller's behaviour did not change. Per the preregistered gate the
falsification controls stay unlaunched. Secondary observation: the mbdr
circuit package itself costs local breadth against plain g2-nolearn (7/25 vs
10/25).

What remains honest for Experiment 002's score mandate after this: the
depression-only rule under a 31:1 punishment-dominated signal is now fairly
excluded on this scaffold. Generalization-changing candidates left standing:
Experiment 000's mechanism (different dynamics, task, and nulls -- its gates
remain open), or acceptance that 002's contribution is the audited T4/T5
finding, the methodology, and a complete honest negative. Slots stay unspent
until a local ledger win exists.

### Submission 4 resolved: the first informative 0.00 — 2026-09-24

`56511405`: COMPLETE, 0.00, under the fail-loud notebook. Because every
infrastructure failure now raises to Error status, COMPLETE is a measurement:
the gateway was reached, main.py ran to exit 0, the fail-closed preflight
passed (no fallback), the agent played the hidden games, and it cleared zero
levels. Branch (c) is proven. Three prior ambiguous 0.00s are retroactively
explained as most plausibly the same result.

**What this establishes (measured):** the local-to-hidden generalization gap is
total for this agent class. 10/25 breadth on public games converts to 0 on
hidden ones. Novelty-driven state-graph exploration with fly tie-breaks does
not transfer to unseen games, in any of the four configurations tried.

**Consequence, committed to in advance:** no more submissions of this class.
Configuration five would buy a fifth copy of a proven result. The next slot is
spent only on a mechanism that changes GENERALIZATION -- realistically,
within-game learning (H-MB-LEARNING, still open; the mbdr battery remains
revivable under Experiment 002, and Experiment 000's validated mechanism
supersedes it when its gates close). Until such a mechanism exists and beats
the local ledger, the slots stay unspent.

The ARC arm's standing results are unchanged: the T4/T5 HELPS, the mechanism
findings, and a now-complete diagnosis chain from ambiguous zeros to a proven
one.

### Experiment 002 reopened: P1 diagnosis + P3 verdict + submission 4 — 2026-09-23 night

**P1 (rerun-log diagnosis), closed.** Via Chrome: all three submissions read
Succeeded (rules out crash and hard timeout); the hidden rerun's logs are not
participant-visible anywhere. Scaffold audit found the real defect: the rerun
cell's bare `!` shell lines swallow exit codes, so a dead gateway or crashed
main.py still yields Succeeded -- three submissions could not distinguish
played-and-scored-zero from never-played. Fixed: subprocess with check=True
everywhere, FLYGI_RERUN_SUMMARY, and a raise on nonzero main.py. From
submission 4 onward the status channel is authoritative.

**P3 (breadth stack), did not ship.** Breadth 8/25 against the preregistered
>10/25 bar; 22 levels exactly tying bioeye-t4t5 alone; stacking did not
compose. The preregistration held: no ship.

**Submission 4** therefore carries the breadth champion instead: the
g2-nolearn config (10/25 games, 21 levels; gain-2.0 modulators graph,
controller + fly tie-break, never previously submitted) inside the hardened
diagnostic notebook. Decision value regardless of score: Error status now
means infrastructure, Succeeded means the agent truly played the hidden set.

### ARC queue closed — 2026-09-23 evening

All four bio-eye/decoder arms are resolved: permuted (null, as preregistered),
bioeye-t4t5 (**the league's first HELPS**, +0.0717 CI [+0.005,+0.156] p=0.070,
22 v 13 levels, survived the hash-grade source audit), retdec (HURTS on score
at every preregistered endpoint while completing +5 levels everywhere — the
breadth/depth trade at its sharpest), surprise (killed 19/75, priority).
Submission 3 scored 0.00, consistent with both priors. MBdr deferred, not
falsified. Full detail, provenance, audit, and deviations:
`docs/arc_agi/ARC_CLOSURE_2026-09-23.md`. Registry, league, and this log agree.
Next step: hand the closure SHA to Codex; the Experiment 000 refactor starts
from it.

### Submission 3 assembled and shipped — 2026-09-23 14:0x PDT

On Mustafa's explicit instruction ("whatever improvements we have planned and
that we think will help that are crucial -- like efference copy -- make those
and submit all of those to kaggle asap"), which by the handoff's own authority
clause overrides its no-submit-during-closure provision. Deviation recorded
here; the running decoder arms are untouched (their code was imported at
launch).

**Shipped stack** (`configs/kaggle_bioeye_t4t5_efference.yaml`), tiers stated:
retinotopic-colour encoder + T4/T5 readout (measured HELPS, borderline, audit
pending), retinotopic-surprise coordinates (measured 3.5-cell localization;
behavioural arm still running), Johnston's-organ efference copy at 0.05
(measured separation/cancellation; behaviourally untested by design).
**Excluded**: MB learning -- 31:1 punishment-dominated teaching signal, unknown
sign, unevaluated; a deliberate omission, not an oversight.

**Verified before shipping**: packaging now carries `retinotopy.npz` (it did
not before -- the encoder would have failed closed on Kaggle); staged config and
controller byte-identical to intent; the exact config played locally (tn36
level completed at 80 actions); server file list confirmed all 8 files with the
modulators graph at 93,348,402 bytes; the SERVED config downloaded back and
hash-matched (`edb956eb...`), per the submission-2 precedent. Instrumentation:
`FLYGI_AGENT=` identity line per game, `FLYGI_DIAG=` every 100 turns
(decisive rate, states, outcomes), `FLYGI_ERROR=` with turn and game on any
exception before fail-closed propagation.

Dataset version pushed; kernel version 4 pushed. Submission to the competition
follows kernel completion.

## Current snapshot — 2026-09-22

- Private repository: <https://github.com/msafdari/FlyGI>.
- Branch: `main`, tracking `origin/main`.
- 325 tests pass; Ruff clean for FlyGI-owned files.
- Both official submissions scored **0.00**. No submission remains today.
- The Phase 1 state/effect controller and the Phase 5 fly tiebreaker are
  committed (`8ad3863`). 325 tests pass; Ruff clean across `src/` and the
  evaluator.
- A parallel session works in the same tree. Stage files by name; `git add -A`
  here would sweep in half-finished work.
- No raw connectome, compiled arrays, ARC game packages, result traces, model
  checkpoints, credentials, virtual environments, or generated notebooks belong
  in normal Git history.

### Experiments closed on this date

| Experiment | Outcome | Score change |
| --- | --- | --- |
| Budget 80 → 600 → 1600 | Saturated at 600 | none beyond 600 |
| Plasticity, real vs rewired mushroom body | Falsification inconclusive | none |
| Track B trained head | Uses the connectome; **zero held-out generalization** | none held out |
| Phase 0 retinotopic encoder | **Worse on every axis** | 0.190476 → 0.003156 |

Four experiments, zero score improvements. The single actionable defect found is
the coordinate head, which explores 3.29x less than random clicking in the six
games where clicking is the only legal action.

### The coordinate-head defect, diagnosed

**Temperature is not the problem.** Six click-only games, three seeds, 600
actions:

| Condition | Mean score | Mean unique observations |
| --- | ---: | ---: |
| Coordinate temperature 0.2 (submitted) | 0.000000 | 71.7 |
| Coordinate temperature 1.0 | 0.000000 | 67.0 |
| Coordinate temperature 4.0 | 0.000000 | 67.0 |
| **Random clicking** | **0.009425** | **235.6** |

1.0 and 4.0 produced **identical** results, which is the clue. At a near-uniform
temperature of 4.0 the agent still touches only 1-2% of the grid:

| Game | Unique coordinates used | Share of 4,096 cells |
| --- | ---: | ---: |
| `r11l` | 96 | 2.3% |
| `s5i5` | 52 | 1.3% |
| `tn36` | 63 | 1.5% |
| `vc33` | 52 | 1.3% |
| `lp85` | 1,434 | 35.0% |

**The cause is the branch order, not the distribution.** The head selects by:

```
if explore_unchanged_click: seeded uniform
elif centroid is not None:  novelty_centroid   <- deterministic
else:                       factorized_sample  <- the only temperature-controlled path
```

When a click *does* change the frame, `centroid` is not None, so the agent
deterministically clicks the centroid of the changed cells and the
temperature-controlled sample is never reached. That collapses it onto a handful
of self-reinforcing locations in exactly the games that respond to clicking.

`lp85` is the proof: it has a 2.5% effect rate, so clicks almost never change
anything, the unchanged-click branch fires instead, and coverage jumps to 35%.
**The heuristic explores widely precisely when the game ignores it, and collapses
precisely when the game responds.**

`decoder.coordinate_fallback: factorized` now disables the centroid branch. A
test of it is running over the same six games and seeds. This is a defect fix
with a measured mechanism behind it, not a tuning pass.

## Immutable data and runtime identity

MaleCNS source release: `male-cns:v1.0`.

| Runtime property | Signed deployed graph |
| --- | ---: |
| Retained neurons | 166,700 |
| Directed nonzero edges | 24,559,055 |
| Descending-neuron readout population | 1,314 |
| Graph SHA-256 | `45e332d90ea4e881ece5d4d72216955bd53eec922aa60955a69db510272eff61` |
| Node metadata SHA-256 | `2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c` |
| Groups SHA-256 | `09736379ce989268080f57b64f357e800cf446972007c1af2287a86b9985a89d` |

The unsigned graph contains 25,582,837 edges. The heuristic-signed build zeros
1,023,782 outgoing edges from modulatory or unknown-transmitter neurons. A
separate modulator-preserving runtime contains 24,994,595 edges for the Track C
learning experiment.

Detailed source hashes, acquisition provenance, preprocessing choices, and
runtime records live in `data/manifests/` and the tracked result manifests.

## What is implemented

### Core and deployment

- Strict Python 3.12 config, provenance, graph-build, validation, and CLI paths.
- Full sparse MaleCNS compilation without a dense adjacency matrix.
- Persistent float32 leaky-tanh dynamics on CPU/SciPy CSR.
- Fixed sparse frame encoder, adaptive DN standardizer, legal-action sampler,
  coordinate head, per-environment state, and loop-escape memory.
- Strict-offline public-game evaluator with immutable traces, deterministic
  replay, action/coordinate validation, timing, hashes, and resumable rows.
- Offline Kaggle Dataset/notebook packaging, graph preflight, fail-closed
  competition behavior, 600-action deployment ceiling, and seven-hour guard.

### Controls and analysis

- Three exact directed degree-preserving rewires.
- Interface-matched no-recurrent-graph bypass.
- Matched random reservoir and an edge-of-chaos positive control.
- Paired analysis clustered on games, trace-diversity audit, game-clustered
  bootstrap, within-pair permutation, and correct right-censoring.
- Retrospective recovery of the actual action index of every level completion.

### Learning experiments

- Track B: a fixed 48-dimensional compression plus an eight-action linear head,
  520 trainable parameters total, integrated before legal masking and sampling.
- Resumable CEM trainer with dense exploration objective, sparse level bonus,
  worker-local graph reuse, and mandatory descending-trace ablation.
- Track C: local dopamine-gated KC->MBON depression with bounded normalized
  updates, writable weights but immutable topology, a modulator-preserving
  runtime, and a degree-preserving mushroom-body partner rewire.

### Track B: the head uses the connectome, and generalizes nothing

CEM trained the 520-parameter action head on eight public games, stopped early
at generation 25 of 60: the objective peaked at **320.25 at generation 16**,
nothing after improved, and sigma sat at its 0.075 floor from generation 8. The
remaining 35 generations would have re-sampled a converged distribution.

All 25 public games, seed 0, 600 actions, split by whether the game was in the
eight-game training set:

| Condition | All 25 | Training (8) | **Held out (17)** |
| --- | ---: | ---: | ---: |
| Untrained (the submitted policy) | 0.190476 | 0.595238 | **0.000000** |
| **Trained head** | **0.283458** | **0.885805** | **0.000000** |
| Trained head, descending trace zeroed | 0.000000 | 0.000000 | 0.000000 |
| Random legal, 600 actions, seeds 0-2 | 0.097568 | — | — |

**Two findings, pulling opposite ways.**

*The head genuinely uses the connectome.* Zeroing the descending trace before
the head sees it drops the score from 0.283458 to **exactly 0.000000**, and mean
unique observations from 263.4 to 169.5. The head did not learn to route around
the graph; without the graph it does nothing. That is the cleanest
connectome-dependence result the project has produced.

*It generalizes nothing.* Every point of its advantage is on games it trained
on: 0.885805 there against the untrained 0.595238. On the seventeen held-out
games it scores **0.000000**, exactly like the untrained policy. The two games
it solved, `ar25` and `sp80`, are both in the training set.

This predicts the hidden-set outcome directly: a trained head would also score
0.00, because the hidden set is held out by construction. **Track B is not a
submission candidate**, and training harder would only deepen the in-sample fit.

### 3. The coordinate head is worse than random clicking

A diagnostic over the 20 games no condition has ever solved found that the
obvious explanation is wrong. **Effect rate is not the problem.** Actions change
the frame at a similar rate whether or not a game is ever solved:

| Group | Fly effect rate | Random effect rate |
| --- | ---: | ---: |
| Solved (5 games) | 84.7% | 91.2% |
| **Never solved (20 games)** | **76.3%** | **81.1%** |

The agent is not stuck. Its actions do things. It simply gets nowhere, which
rules out exploration volume as the core failure and points at what it does with
the effects it causes.

**Six games expose `ACTION6` as their only legal action**, so coordinates are
the *only* thing that can differ between conditions there. Isolating them:

| Game | Fly unique observations | Random unique observations | Ratio |
| --- | ---: | ---: | ---: |
| `ft09` | 130 | 81 | 0.63x |
| `lp85` | 15 | 14 | 0.91x |
| `r11l` | 121 | 576 | **4.76x** |
| `s5i5` | 51 | 276 | **5.42x** |
| `tn36` | 62 | 339 | **5.47x** |
| `vc33` | 51 | 126 | 2.48x |
| **mean** | **72** | **236** | **3.29x** |

With the identical single action available, **uniform random clicking explores
3.29 times more than the coordinate head**, and random solved `r11l` while the
fly never has. The novelty-centroid and untried-grid logic is not merely
unhelpful in these games; it is actively worse than clicking at random, and it
accounts for roughly 63% of all clicks the agent makes.

`lp85` is separately pathological: a 2.5% effect rate and 15 unique observations
for the fly, 2.2% and 14 for random. Almost nothing either agent clicks changes
the frame at all, so that game needs targeted rather than broader clicking.

A coordinate-temperature test is running over those six games at three seeds:
the frozen 0.2 against 1.0 and 4.0. This is a component that is demonstrably
worse than chance at its one job, so raising its temperature is a defect fix
rather than a tuning pass -- though it is still public-set development and is
recorded as such.

### 4. A retinotopic interface made things worse, not better

Phase 0 existed to test the standing excuse that the connectome has never had a
fair interface. All 25 public games, seed 0, 600 actions, identical to the
submitted configuration except the encoder.

| Measurement | Sparse projection (submitted) | **Retinotopic** |
| --- | ---: | ---: |
| Mean score | **0.190476** | **0.003156** |
| Games with a level | 1 (`cd82`) | 1 (`sp80`) |
| Mean unique observations | 280.3 | 238.0 |
| Mean action entropy (bits) | 1.703 | 1.398 |

Preserving retinotopy made the agent **worse on every axis measured**: sixty
times lower score, less exploration, less varied behaviour. Both conditions
completed one level, but the retinotopic one's was worth 0.0789 against the
sparse condition's 4.76.

**The most likely cause is a trade I did not notice making.** The sparse encoder
feeds a 16-channel one-hot of the frame, so colour identity is preserved
exactly. The retinotopic encoder collapses those 16 categorical colours onto a
scalar luminance ramp before injecting them, because a column has to receive a
number. ARC is a game about categorical colour, and two unrelated colours with
adjacent indices become nearly identical under that mapping.

So Phase 0 bought spatial structure and paid for it in colour structure, and the
exchange was bad. That is a specific, testable explanation rather than a
mystery, and per the standing rule it will be *tested cheaply before* any
colour-preserving encoder is built.

**This also weakens the project's standing excuse.** "The connectome has never
had a fair interface" has been the explanation for every null result so far. One
dimension of fairness has now been restored, and performance fell. That is
evidence, not proof -- the colour trade confounds it -- but it is the first
direct test of the excuse, and the excuse did not survive it cleanly.

### 5. Disabling the novelty centroid: the first real improvement

**The defect.** The coordinate head selects by branch order:

```
if explore_unchanged_click: seeded uniform
elif centroid is not None:  novelty_centroid   <- deterministic
else:                       factorized_sample  <- the only temperature-controlled path
```

When a click changes the frame, `centroid` is not None and the agent
deterministically clicks the centroid of the changed cells, never reaching the
sampler. Temperature is therefore irrelevant: 1.0 and 4.0 produced **identical**
results. `lp85` proves the mechanism -- its 2.5% effect rate means clicks rarely
change anything, the unchanged-click branch fires instead, and coverage jumps to
35% of the grid. The heuristic explores widely precisely when the game ignores
it and collapses precisely when the game responds.

**Six click-only games, three seeds, 600 actions:**

| Condition | Mean score | Unique obs | Levels | Games solved |
| --- | ---: | ---: | ---: | --- |
| Centroid ON, T=0.2 (submitted) | 0.000000 | 71.7 | 0 | none |
| Centroid ON, T=4.0 | 0.000000 | 67.0 | 0 | none |
| **Centroid OFF** | **0.010120** | **247.4** | **3** | `r11l`, `vc33` |
| Random clicking | 0.009425 | 235.6 | 3 | `r11l` |

Coordinate coverage recovered roughly fourteen-fold: `r11l` 96 to 1,383, `s5i5`
52 to 1,352, `tn36` 63 to 1,391, `vc33` 52 to 1,367 distinct cells of 4,096.

**All 25 games, seed 0, 600 actions:**

| Condition | Mean | Click-only (6) | Other (19) | Unique obs | Games solved |
| --- | ---: | ---: | ---: | ---: | --- |
| Submitted | 0.190476 | 0.000000 | 0.250627 | 280.3 | `cd82` |
| **Centroid OFF** | **0.195388** | **0.020466** | 0.250627 | **322.6** | `cd82`, `r11l` |

**Strictly dominant: 1 game better, 0 worse, 24 unchanged.** The nineteen games
where clicking is not the only action are **identical to six decimal places**, so
the change does no harm where it does not apply, and all of the gain is where
the defect was.

**Status: adopted as the default, not a submission on its own.** The overall
margin is +2.6%, far short of the 2x bar for spending a daily slot, and both
prior submissions scored 0.00 on games this class of fix does not reach. It
should be carried into whatever the Phase 1 controller produces rather than
spent alone.

**What it cost.** The defect shipped in both competition submissions. It had six
passing tests, none comparing it against clicking at random. It is the exact
failure the standing rule in `AGENTS.md` was written for, found four days late.

### 6. The Phase 1 state-graph controller: 3.5x the games reached

All 25 games, **three seeds**, 600 actions, same strict-offline harness, action
ceiling, legality and replay contracts as every other condition.

| Condition | Rows | Mean score | Levels | **Games with progress** | Games solved |
| --- | ---: | ---: | ---: | ---: | --- |
| Random legal | 75 | 0.097568 | 6 | 2 / 25 (8%) | `r11l`, `sp80` |
| Centroid-OFF connectome | 25 | 0.195388 | 2 | 2 / 25 (8%) | `cd82`, `r11l` |
| **State-graph controller** | 75 | 0.194691 | **20** | **7 / 25 (28%)** | `ar25`, `g50t`, `lp85`, `m0r0`, `r11l`, `tn36`, `vc33` |

**Mean score is a tie. Breadth is not.** The controller completes **20 levels
against the connectome's 2**, and reaches progress in **3.5x as many games**. Its
promotion gate passed: mean above the 0.097568 random baseline, with seven
progress games against a required minimum of three.

Per-game means, and note the consistency across seeds:

| Game | Mean | Seeds |
| --- | ---: | --- |
| `tn36` | 2.304995 | 1.978 / 2.533 / 2.404 |
| `lp85` | 1.693618 | 2.224 / 2.478 / 0.379 |
| `r11l` | 0.626983 | 1.190 / 0.662 / 0.028 |
| `g50t` | 0.169976 | 0.094 / 0.082 / 0.334 |

**Five of these games had never been completed by anything in this project**:
`ar25`, `g50t`, `lp85`, `m0r0`, `tn36`. `lp85` is the one with a 2.5% effect
rate, where nothing either agent clicked used to change the frame. `tn36`'s mean
of 2.30 is the highest per-game score recorded here.

The mean parity is a scoring artifact rather than equivalence: the connectome's
0.195 comes almost entirely from `cd82`, a single game whose first level happens
to be worth 4.76, while the controller earns its number across seven games. On a
hidden set, breadth of progress is the property that transfers; a single lucky
game is not.

**The tension this creates.** The controller uses **no connectome at all**. Its
own evaluator states that no connectome assets or game identities are available
to it. Submitting it would put the best score on the board under a project named
for a fly brain that had nothing to do with it. That is the Path A / Path B fork
recorded earlier, now with numbers attached, and it is the user's decision rather
than a technical one.

### Phase 0 — retinotopic optic-lobe encoder

`encoder.kind: retinotopic` injects the 64x64 grid into the fly's own columnar
lattice, replacing the random projection that destroys spatial structure.

Where it injects was decided by measurement, not by the plan. Photoreceptors
(`ol_sensory`) carry **no** column assignment -- 0 of 6,098 -- so they cannot be
targeted retinotopically at all. The coordinates live on **23,720
`ol_intrinsic`** lamina and medulla interneurons (L1, L2, L3, L5, Mi1, Mi4, Mi9,
T1, C2, C3) spanning hex1 1..36 and hex2 1..39 over **892 occupied columns**.

`scripts/build_retinotopy.py` compiles that map into a hashed asset beside the
graph (`retinotopy.npz`, SHA-256 `ebc2b699e541330097a257003c2346f367d4beda1f04e88b2aaa1e1542db1a8d`)
so a deployed bundle needs no annotation table.

Verified on the real graph: 15,582 neurons driven, and a 6x6 corner edit changes
only **43** of them. Under the random projection any local edit perturbs the
whole sensory population; here it stays local, which is the property the optic
lobe exists to exploit.

Channel assignment (ON: L1/Mi1/Mi4/Tm3, OFF: L2/L3/Tm1/Tm2/Tm4/Tm9, change:
T1/C2/C3/L5/Mi9) and the mapping of 16 categorical ARC colours to a scalar
luminance are **declared heuristics, not physiological claims**, and live in
config so they can be ablated. The bypass is refused a retinotopic projection,
because its projection must address the readout population.

## Decisive results

### 1. The graph is structurally non-random

At the deployed `K=4`, `leak=0.3`, `gain=0.9` operating point:

| Measurement | Real signed graph | Three exact degree nulls |
| --- | ---: | ---: |
| Spectral radius | **0.8289** | 0.2360 / 0.2348 / 0.2219 |
| Hops for visual input to reach every DN | 3 | 2 / 2 / 2 |
| DN participation ratio | 5.39 | 18.54 / 14.33 / 16.00 |

The 3.59x spectral-radius separation survives exact in- and out-degree
preservation. This is the strongest reproducible connectome result. It has not
yet produced an ARC outcome advantage.

### 2. The literal interface is the main failure

The original encoder random-projects ARC features into 6,098 visual sensory
neurons. The decoder partitions 1,314 DNs into ARC action blocks by sorted body
ID. Those mappings preserve neither retinotopy nor motor semantics. The graph
causally changes actions, but an interface-matched bypass matched its ARC score.

Gate 2, 25 games x five seeds x 80 actions:

| Condition | Mean score | Levels | Games with a level |
| --- | ---: | ---: | --- |
| Real signed MaleCNS | 0.190476 | 5 duplicate-seed rows | `sp80` |
| No-graph bypass | 0.190476 | 5 duplicate-seed rows | `r11l` |
| Degree-preserving null | 0.000000 | 0 | none |
| Random legal | 0.050626 | 2 | `sp80` |

The graph policies were deterministic, so five identical seeds were not five
replicates. Effective n was 25 games.

### 3. Exploration, not raw entropy, was deficient

At 500 actions x 25 games x three seeds:

| Condition | Mean score | Levels | Unique observations |
| --- | ---: | ---: | ---: |
| Real signed | 0.064751 | 2 | 15,996 |
| Degree null | 0.007872 | 3 | 16,262 |
| Bypass | 0.000754 | 1 | 16,339 |
| Random legal | **0.097568** | **6** | **25,140** |

Formal paired analysis found no condition distinguishable on ARC outcome.
Recovered completion times also retracted an earlier apparent fly-efficiency
claim: completer-only means were 143 actions for the fly and 144 for random,
while random completed three times as often.

### 4. Loop escape helps, but budget alone saturates quickly

- 600 actions, seed 0, loop escape off: score 0.000000.
- 600 actions, seed 0, loop escape on: score 0.190476, `cd82` level 1.
- 500 actions x three seeds, loop escape on: mean 0.126984, two levels
  (`cd82` seed 0 and `sp80` seed 1). This beat the old real mean but failed the
  preregistered requirement of more than two levels.
- 1,600 actions, seed 0: mean **0.191289**, first levels in `cd82`, `sk48`, and
  `sp80`. The last two required 1,033 and 825 actions and contributed only
  0.009686 and 0.010641 game score. They raised the mean by just 0.000813 over
  600 actions while multiplying worst-case work by 2.67.

Thus a larger budget finds more states, but breadth-only exploration cannot
approach a score of 10 efficiently.

### 5. Plasticity changes exploration, not outcome

At 600 actions over 25 games, seed 0:

| Condition | Mean score | Levels | Mean unique observations |
| --- | ---: | ---: | ---: |
| Frozen modulator runtime | 0.001418 | 1 | 256.96 |
| Real plastic mushroom body | 0.005337 | 1 | **270.96** |
| Rewired plastic mushroom body | 0.000892 | 1 | 261.80 |

Real plastic minus frozen unique observations was +14.0 with a bootstrap
interval excluding zero. The required direct comparison, real plastic minus
rewired plastic, was +9.16 with 95% interval `[-1.24, +21.72]`, p=0.1539.
Plasticity unlocked no level. The result is interesting but inconclusive and is
not a connectome-advantage claim.

### 7. Phase 5 — the fly returned to the decision loop (in progress)

The Phase 1 state-graph controller reached 7 of 25 games with progress against
the connectome policy's 2, which raised the objection that makes or breaks this
project: the fly had stopped doing anything. Phase 5 puts it back, at exactly
one place.

The controller ranks candidates by

```text
(retry_prefix, attempts, -(priority + exploration), TIEBREAK, bytes)
```

`TIEBREAK` was `_tie_digest`, a deterministic hash: reproducible, carrying no
information. `src/flygi/controller/fly_tiebreak.py` puts the connectome there and
nowhere else, so it cannot override legality, a known death state, a verified
plan, or a learned effect estimate. It speaks only where the controller is
genuinely indifferent. That placement is also what makes the experiment clean:
real graph, degree-preserving rewiring, and hash differ in one thing only.

Measured before the full run, per the `AGENTS.md` rule:

| Check | Trivial alternative | Result |
| --- | --- | --- |
| Does the fly discriminate? | a constant | 6/6 distinct action preferences after warmup; click scores span 1.8-4.5 |
| Does it change decisions? | the hash | diverges at step 1; 63% of 200 steps differ |
| Does it stay in its slot? | unconfined | action totals byte-identical with and without |

Turn 0 is exactly zero for every candidate, because the adaptive standardizer's
EMA mean equals its first sample. `preference()` returns 0.0 there, so an
unobserved turn degrades to the controller's own ordering rather than to noise.

Cost: the connectome advance is ~0.148 s/action, roughly 16x the controller
alone. Caching the per-turn decode was necessary first -- the trace changes once
per observation, but one turn ranks hundreds of candidate clicks, and
recomputing the readout reduction for each cost ~10x on click-heavy games
(ar25: ~15 min -> 98.8 s per 600-action row). Verified bit-identical by replay
hash before adoption.

The three-way ablation is running against the matched baseline below. Nulls
already exist at
`data/processed/male-cns-v1.0/literal-rate-signed/nulls/degree_preserving/seed-20260921`
and load as a tiebreaker (166,700 nodes / 24,559,055 edges, identical to real).

| Condition (3 seeds x 25 games x 600 actions) | Mean score | Levels | Games w/ progress |
| --- | ---: | ---: | ---: |
| Controller alone | 0.194691 | 20 | 7/25 |
| Controller + real fly | 0.216301 | **20** | 10/25 |
| Controller + grid-hash (state-dependent, no anatomy) | 0.179650 | 9 | 3/25 |

**Result: the fly does not beat the controller.** Level count is *exactly*
tied, 20 against 20. Score is `+0.021610`, 95% CI `[-0.166096, +0.186871]`,
`p=0.8350`. Row-level: 15 better, 10 worse, 50 tied. The connectome is
mechanically load-bearing -- decisive on 25-37% of turns -- and that influence
does not convert into levels.

What the fly does do is **trade depth for breadth**. It reaches a first level in
four games the controller never cracked (cd82, lf52, s5i5, sp80) and loses one
it had (ar25), for 10 games with progress against 7. With five discordant games
split 4-1 that is not significant either. Both conditions still complete twenty
levels in total; the fly spreads them differently.

**Against the anatomy-free control the fly does separate.** Real minus
grid-hash: levels `+0.146667`, 95% CI `[+0.013333, +0.293333]` (excludes zero),
`p=0.0822`; score `+0.036651`, `p=0.5028`. Injecting a *random* state-dependent
tiebreaker into the same seam costs the controller more than half its levels
(20 -> 9) and most of its coverage (7 -> 3 games), while injecting the
connectome costs it nothing. So the fly's signal is structured rather than
noise-like. Suggestive, not significant at 0.05, and confounded by scale: the
grid hash draws uniformly on [0,1) while the readout is smooth and standardized.
Do not report this as the connectome beating a matched control.

**Discipline note.** At 41 of 75 rows this comparison read `+10.6%` on score and
`+3` on levels, and was reported as partial. Seeds 1 and 2 erased it entirely.
The 41-row snapshot was seed-0-heavy, and seed 0 is where the fly's wins
concentrate. Partial matrices from a seed-ordered run are not small versions of
the result; they are a biased sample of it. Wait for the full matrix.

**Submission gate: not cleared.** The user's condition is that the fly be
load-bearing *and* the agent beat both 0.00 submissions. The fly is load-bearing
in the mechanical sense and produces no demonstrable improvement, so this agent
is not a submission candidate. The budget arm below is the live route to an
actual gain.

**How often is the fly actually decisive?** `fly_decisive_rate` in
`policy_diagnostics` counts turns where removing the connectome would have
chosen a different candidate: 24.7% on ar25, 28.5-37.2% on ls20. It is neither
inert nor saturated -- on roughly three turns in four the controller's own
learning already picks a unique winner and the fly is silent, which is the
guardrail working.

**The action budget is NOT binding. This inference was wrong and is retracted.**
All 125 rows at 600 actions ended `budget_exhausted` with zero wins, completions
landed as late as action 599, and exploration had not plateaued -- 72.9-74.6 new
observations in the last 100 actions against 91.5-91.7 in the first. That looked
like a binding budget and it was recorded as the cheapest score gain available.

The 1800-action arm settles it: **tripling the budget bought exactly nothing.**
21 matched seed-0 rows, all running the full 1800 actions, all
`budget_exhausted`: 7 levels at 600 and 7 levels at 1800, mean score identical
to six decimal places, and **zero level completions after action 600**. The
agent is still finding 62.3 novel observations per 100 actions at action 1800.

The lesson is that **novel-state discovery is not progress**. The agent wanders
into genuinely new states indefinitely and converts none of them into level
completions. Continued exploration was read as evidence of unfinished business;
it is evidence of an agent that cannot tell which states matter. The bottleneck
is credit assignment, not action count. `MAX_ACTIONS` stays at 600 -- raising it
costs wall-clock on Kaggle and buys nothing.

**Submission gate: not cleared.** The user's condition is that the fly be
load-bearing *and* the agent beat both 0.00 submissions. The fly is load-bearing
in the mechanical sense and produces no demonstrable improvement, so this agent
is not a submission candidate. The budget arm below is the live route to an
actual gain.

**How often is the fly actually decisive?** `fly_decisive_rate` in
`policy_diagnostics` counts turns where removing the connectome would have
chosen a different candidate: 24.7% on ar25, 28.5-37.2% on ls20. It is neither
inert nor saturated -- on roughly three turns in four the controller's own
learning already picks a unique winner and the fly is silent, which is the
guardrail working.

**The action budget is binding, and this is the cheapest score gain available.**
All 125 completed rows across both conditions ended by `budget_exhausted`; not
one ended in a win. Level completions run as late as action 514 (controller) and
599 (fly) -- the literal last action of the budget. Exploration has not
plateaued: rows still find 72.9 (controller) and 74.6 (fly) new observations in
their last 100 actions against 91.5/91.7 in their first 100, an 80-81%
retention, with only 3 of 75 rows finding 5 or fewer. A 1800-action arm is
running to measure the gain. Kaggle allows nine hours; at 0.148 s/action the fly
costs 266 s/game at 1800 actions, so the budget is not the constraint there.

Baseline games with progress: ar25, g50t, lp85, m0r0, r11l, tn36, vc33. The
75-row controller-only matrix is in
`results/connectome_agent/sg-full.rows.jsonl`; its final JSON write was lost
when the process exited, but every row is on disk.

**Reading the result in advance, so it cannot be read motivatedly later.** Real
above null is the first evidence in this project that anatomy buys ARC-relevant
computation. Real equal to null means the fly is acting as a seeded hash and the
honest report is that the scaffold scores, not the fly. Real below null is a
real finding too, and gets recorded.

### 8. The operating point is dead, and that outranks the mushroom body

Research before building, per the user's instruction. Three independent sources
converge on how connectome-based MB learning is actually done, and two of their
documented failure modes are ones this repository can be checked for in minutes.

**Established practice for KC->MBON learning:**

- Plasticity is **depression only**, never potentiation. Dopamine coincident
  with KC activity depresses the KC->MBON synapse (LTD). Published
  implementations use learning rate ~0.06 with a **weight floor** (~0.25 of
  baseline) so synapses cannot be driven to zero, plus slow recovery toward
  baseline as a forgetting term.
- Credit assignment uses an **eligibility trace**, decaying ~0.55 per step so
  roughly six steps stay eligible. Reward arrives after the action; without a
  trace there is nothing to assign credit to.
- Valence is anatomical: **PAM** neurons carry reward, **PPL1** punishment, and
  they innervate distinct MBON compartments. Punishment depresses the channel
  taken; reward depresses the channels not taken.
- KC->DAN synapses stay **fixed**; only KC->MBON is plastic.
- The code must be **sparse**, a few percent of KCs per stimulus, maintained by
  APL feedback inhibition.

**The two failure modes worth checking first, both documented:**

1. *Saturation.* If every KC fires every step the eligibility trace is a
   constant and the rule degenerates to a per-compartment scalar. One project
   traced this to KC->KC recurrence being 56% of KC input against 9.3% from APL,
   pushing loop gain above unity. **Ours is worse: KC->KC is 85.3% of KC input
   (642,932 edges) against 2.4% from APL.**
2. *No reach.* A published MB-lesion control found that cutting MB output left
   behaviour unchanged -- the MB never reached the readout, so no plasticity
   could have mattered.

**What the checks found here is a third thing, and it is worse.**

`modulator_treatment: zero` in the deployed config deletes the entire
dopaminergic pathway: **0 DAN->KC and 0 DAN->MBON edges**. There is no teaching
signal to gate anything. The `-modulators` build (`modulator_treatment:
positive`) restores 129,099 DAN->KC and 3,159 DAN->MBON edges and is the graph
any learning work must use.

But the blocking problem is the operating point. At the deployed `gain=0.9`:

| Group | mean abs activity | vs sensory drive |
| --- | ---: | ---: |
| `ol_sensory` (drive) | 2.295e-01 | 1x |
| `ol_intrinsic` (1 hop) | 2.332e-03 | 100x weaker |
| **descending neurons (the readout)** | **2.611e-06** | **87,906x weaker** |
| KC / MBON / DAN | 1.6-3.4e-06 | comparable to DN |

Float32 epsilon is 1.19e-7, so the readout carries roughly one significant digit
above quantization. **The whole post-sensory network is silent, not just the
mushroom body.** Incoming-L1 normalization makes rows sum to one, and with
signed weights a row of mixed signs averages to near zero, so amplitude is lost
at ~100x per hop rather than the ~0.9x the gain suggests.

This retroactively explains a great deal: why the connectome policy never beat
an interface-matched bypass, why the trained head generalized nothing, and why
the fly ties the controller while still beating a random tiebreaker -- its
readout is structured, but at an amplitude barely above the numerical floor.

**A gain sweep finds a narrow biological window.** KC active fraction against
recurrent gain, ten turns, biological target 0.05-0.11:

| gain | mean abs DN | KC frac >0.1 | mean KC |
| ---: | ---: | ---: | ---: |
| 0.9 (deployed) | 2.6e-06 | 0.000 | 0.0000 |
| 2.4 | 5.9e-05 | 0.000 | 0.0119 |
| **2.6** | 9.5e-05 | **0.031** | 0.0327 |
| **2.8** | 1.6e-04 | **0.188** | 0.0774 |
| 3.0 | 2.7e-04 | 0.800 | 0.1813 |
| 3.4 | 1.2e-03 | 0.991 | 0.6381 |
| 4.0+ | -- | 1.000 | ~0.97 (latched) |

Between silence and latching there is roughly `gain in [2.6, 2.9]`. There the
KC code is biologically sparse and DN amplitude sits ~40-100x above the current
value and ~1000x above float32 epsilon.

**A sharp prediction falls out of this.** At `gain~2.7` the real graph
(spectral radius 0.8289) sits at effective radius ~2.2 and comes alive, while a
degree-preserving null (radius ~0.23) sits at ~0.63 and stays silent. The 3.59x
structural separation, which has never produced a behavioural difference, would
for the first time be placed at an operating point where it *should* produce
one. That is preregistered here before the run.

**Execution directive for this plan (set by the user, 2026-09-23).**

Follow all five steps to completion before running the test and validation
batteries. Do **not** abort the implementation partway because an intermediate
check looks unfavourable, and do not revert work already built in this plan.
Measure twice, cut once: the measuring has been done -- operating point, KC
sparsity, DAN edge counts and the gain window are all recorded above -- so the
remaining work is the cut.

This deliberately suspends the `AGENTS.md` habit of killing a build at the first
bad intermediate signal, and it is not a licence to skip validation. Validation
happens at the end, in full, and its results are reported whatever they say. The
rule being replaced was aimed at *speculative* builds; this build's premises
were checked first, which is precisely why it earns a straight run. If a step
turns out to be impossible rather than merely discouraging, record it, finish
every other step, and report what was left out.

**Ordered plan.**

1. Re-tune the operating point on the `-modulators` graph: pick the gain where
   KC sparsity lands in 0.05-0.11, and confirm DN amplitude clears the float32
   floor by a wide margin. Nothing else can be trusted until this is done.
2. Run the MB reach test at that operating point: zero every MBON outgoing edge
   and check whether the action sequence changes at all. If it does not, MB
   plasticity cannot affect behaviour and the plan stops here.
3. Re-measure the existing three arms at the new operating point. Changing gain
   invalidates every score in this worklog; those scores are of a dead network,
   so this is a cost worth paying, but it must be paid explicitly and not
   quietly.
4. Only then implement KC->MBON depression: depression-only, floor at 0.25 of
   baseline, learning rate ~0.06, eligibility trace decaying ~0.55 per turn,
   PAM-gated on level advance and PPL1-gated on death, with the controller
   supplying the reinforcement signal the connectome has never had.
5. Control it with the rewired mushroom body already implemented in
   `rewire_mushroom_body`, and with reinforcement shuffled in time.

### 9. Validation battery for the mushroom-body build

Implementation complete and committed before any of this ran, per the user's
execution directive. Results recorded as measured.

**1. MB reach test -- PASSES, decisively.** Zeroing every outgoing MBON edge
changes the descending-neuron readout by **22.286% of its own magnitude** and
touches **92.2% of readout entries** (20 turns, `results/mb_reach_gain2.7.json`).
The published failure mode -- an MB that never reaches the readout, where a
lesion changes nothing and no plasticity could matter -- is absent here.
KC->MBON plasticity can affect actions. The per-turn effect decays across the
episode (0.316 at turn 1 to 0.151 at turn 20), which is worth watching but does
not threaten the result.

**2. Operating point -- the dead-network defect is fixed; sparsity is a declared
compromise.** The first gain sweep used uncorrelated random frames and picked
2.7. That was wrong. Real ARC frames are highly correlated -- a persistent grid
with small edits -- and correlated drive sustains the Kenyon-cell population far
more effectively. Re-swept with correlated input:

| gain | KC active frac (mean / max) | mean abs DN | x float32 eps |
| ---: | ---: | ---: | ---: |
| 0.9 (deployed) | 0.000 / 0.000 | 2.61e-06 | **22** |
| 1.5 | 0.000 / 0.000 | 1.09e-05 | 92 |
| 1.8 | 0.002 / 0.037 | 5.47e-05 | 460 |
| **2.0 (adopted)** | **0.123 / 0.555** | **5.95e-04** | **4998** |
| 2.2 | 0.265 / 1.000 | 1.36e-03 | 11448 |
| 2.7 | 0.496 / 1.000 | 8.96e-03 | 75292 |

Adopted 2.0. The readout now sits ~5000x above float32 epsilon against the
deployed 22x, which is the defect that matters most. Mean KC activity of 0.123
is **above** the biological 0.05-0.11 band and the population still latches on
individual turns (max 0.555), so the eligibility trace is not as sharp as the
literature's. Measured spread is 2.09, well clear of the degenerate zero, so the
trace still carries structure.

There is **no gain that delivers both** biological sparsity and a readout clear
of the numerical floor. The anatomy says why: KC->KC is 85.3% of Kenyon-cell
input against 2.4% from APL, which makes the transition from silent to latched
abrupt. The principled fix is to strengthen APL feedback rather than scale the
global gain -- a separate change with its own controls, not folded in here.

**3-4. Waking the network did not help, and neither did learning.** 3 seeds x 25
games x 600 actions, matched rows, clustered on games.

| Condition | Mean score | Levels/row | Levels | vs controller (score) |
| --- | ---: | ---: | ---: | --- |
| Controller alone | 0.194691 | 0.2667 | 20 | reference |
| Fly at gain 2.0, frozen | 0.203443 | 0.2800 | 21 | `+0.008752`, p=0.8625 |
| Fly at gain 2.0, **learning** | 0.203451 | 0.2400 | **18** | `+0.008760`, p=0.8675 |

Learning against no-learning is the comparison that matters and it is flat:
score identical to five decimal places, and the learning arm completes *fewer*
levels (18 against 21). Nothing here is significant; every confidence interval
spans zero comfortably.

**The learning rule is not inert.** Instrumented over three games: 29
`reinforce()` calls moving a total absolute weight change of 95.21. It fires, it
moves real weight at the right site, and it changes behaviour -- the learning and
frozen arms are not bit-identical. It simply does not help.

**The teaching signal is pathologically imbalanced, and this is the finding
worth keeping.** In that instrumented sample: **2 rewards against 27
punishments**. Across all 75 rows: 18 level advances against 569 game-over
frames, a ratio of about 31 to 1. Mushroom-body plasticity is depression-only,
so an agent that is punished thirty times for every reward spends nearly all of
its learning depressing PPL1-gated compartments. The PAM reward channel -- 316
of the 340 dopaminergic neurons -- fires almost never. The circuit is being
taught almost exclusively what not to do, by an agent that dies constantly and
succeeds rarely, and depression-only plasticity has no mechanism to recover from
that except slow decay toward baseline.

That is a property of the *task signal*, not of the fly. ARC-AGI-3 gives an
agent this bad no usable reward statistics, and no associative learning rule can
extract a curriculum from 2 positive examples.

**5. Falsification controls running** (`--fly-rewire-mb`, `--fly-shuffle-credit`).
With a null main effect they cannot explain anything away, but they are run
because the plan preregistered them and because a control that *did* show a
difference would indicate something wrong with the harness.

**Standing conclusion after this battery.** Three separate interventions --
tiebreaking, operating point, associative learning -- have each been implemented
correctly, verified to fire, and produced no score gain. The bottleneck is not
any of them. What remains untried is the fly's perceptual machinery: 13,585
T4/T5 motion detectors at 54.5x the readout's activity and 4,257 LC object
detectors at 16.1x, all firing on every frame, all upstream of the 1,314
descending neurons this agent actually reads. See section 10.


**The controller-only reference survives the operating-point change.** It never
touches the connectome, so gain does not affect it: 0.194691, 20 levels, 7/25
games stands as the comparison point. Every *connectome* score recorded before
this section was measured at gain 0.9 and describes a dead network, including
the degree-preserving null arm that completed during this build. Those are
retained as a record of the dead regime and are not comparable to what follows.

### 10. Reading the fly's perception instead of its motor output

Every intervention so far changed what the agent does with the signal. This one
changes which signal is read. Measured at gain 2.0 on the `-modulators` graph,
mean absolute activity relative to the descending neurons this project has
always decoded, with each population's response to a changed scene:

| Circuit | Neurons | Types | Activity vs DN | Change response |
| --- | ---: | ---: | ---: | ---: |
| T4/T5 motion detectors | 13,585 | 10 | **54.5x** | 4.0% |
| LC lobula columnar | 4,257 | **50** | **16.1x** | 4.4% |
| LPLC looming | 417 | 4 | 11.0x | 4.9% |
| ER ring neurons | 282 | 26 | 8.5x | 4.5% |
| **DN (deployed readout)** | 1,314 | -- | **1.0x** | 8.9% |
| EPG/PEN/PEG compass | 110 | 5 | 0.5x | 14.4% |
| PFL steering | 50 | 3 | 0.1x | 23.7% |

In absolute discriminative signal -- activity times change response -- T4/T5
carry roughly 25x what the descending neurons do. The project has been driving
photoreceptors, passing the signal through 13,585 motion detectors and 4,257
object detectors, and then reading the motor-output layer at the far end, which
is close to the faintest thing in the chain.

`population_indices` in `flygi.arc.factory` makes this a configuration change
rather than a recompilation: a readout group compiled into `groups.npz` is used
as-is, and one declared only under `groups:` is resolved against
`node_metadata.npz` by exact or prefix match. Adding a readout no longer costs a
24.5M-edge rebuild.

Three arms, each identical to `configs/literal_rate_mb_learning.yaml` apart from
the decoded population, learning off so the readout is isolated, matched against
`sg-g2-nolearn` (0.203443, 21 levels):

| Config | Readout | Size | Action spread (standardized) |
| --- | --- | ---: | --- |
| `literal_rate_lc_readout` | LC object detectors | 4,257 | 0.214-0.511 |
| `literal_rate_t4t5_readout` | T4/T5 motion | 13,585 | 0.124-0.303 |
| `literal_rate_central_complex` | EPG/PEN/PEG/ER/FC/PFL | 719 | 0.773-1.978 |

**Limitation recorded before the runs.** The central-complex arm reads a circuit
that is not receiving the input it evolved to integrate. A ring attractor
integrates *angular velocity*: the fly updates its compass from its own turning.
An ARC agent does not turn, does not move, and has no heading. A null result
there is therefore weak evidence about the circuit rather than strong evidence
against it. Driving it properly means synthesizing a heading from something in
the ARC frame, which is engineering rather than anatomy and needs its own
justification.

### 11. We have not been using the circuits properly. Three of three.

Prompted by the user asking whether the components are connected and calibrated
as they should be. They are not, and this revises the "stop adding fly
components" recommendation made just before it. The null results so far are not
evidence that these circuits cannot help; they are evidence that each was given
input it cannot use.

**1. The mushroom body is wired to a sense we never drive.** Input composition
of the 4,064 Kenyon cells, by total absolute incoming weight:

| Source | Share of KC input |
| --- | ---: |
| Other Kenyon cells (KCg-m, KCab-s/m/c, KCa'b'-*) | ~85% |
| APL | 2.0% |
| PAM dopaminergic | ~7% |
| `cb_sensory` (the olfactory pathway) | **0.00%** |
| `ol_sensory` (what we drive) | **0.00%** |

In *Drosophila* the mushroom body is primarily an olfactory structure: Kenyon
cells are driven by uniglomerular projection neurons from the antennal lobe.
Those neurons live in `cb_sensory`, 4,868 of them, and the encoder drives
`ol_sensory` -- photoreceptors -- exclusively. So the learning experiment in
section 9 taught a circuit that receives essentially none of this agent's
sensory input, and is otherwise dominated by its own recurrence. The rule fired
and moved weight on activity that was mostly indirect leakage. That is why it
did nothing, and it says nothing about mushroom-body learning.

**2. T4/T5 and LC are correctly wired but fed spatially scrambled input.** Their
anatomy checks out -- photoreceptors to `ol_intrinsic` lamina/medulla (97.4% of
T4/T5 input) to T4/T5 to LC (62.0% `ol_intrinsic`, 26.2% `visual_projection`).
The defect is upstream. `build_sensory_projection` assigns each photoreceptor 64
**uniformly random** features:

```python
columns = generator.integers(0, FEATURE_DIMENSION, size=(rows, per_row))
```

Neighbouring photoreceptors therefore see uncorrelated parts of the screen. T4
and T5 compute direction-selective motion by comparing *adjacent* columns with a
delay; LC neurons integrate over retinotopic neighbourhoods. Both are pure
spatial computations, and retinotopy is destroyed before the graph sees
anything. The three perception arms now running are motion and object detectors
fed a spatial scramble.

**3. The two encoders are each broken, in complementary ways.**

| Encoder | Retinotopy | Colour |
| --- | --- | --- |
| `sparse_projection` (deployed) | **destroyed** (random) | preserved (16-way one-hot) |
| `retinotopic` | preserved (columnar lattice) | **destroyed** (`grid / 15.0` scalar) |

This is the real explanation for the retinotopic encoder's 0.190476 -> 0.003156
collapse, which was previously guessed at. ARC colours are **categorical**:
colour 3 is not between 2 and 4. Mapping sixteen categories onto a scalar
luminance ramp discards the distinction the benchmark is built from. So one
encoder gives the fly colour without space, the other space without colour, and
the fly's visual system needs both.

**Consequence.** No experiment run so far has given the fly's visual hierarchy an
input it could use, and no experiment has given the mushroom body any sensory
input at all. The sequence of nulls is consistent with that and does not yet
license a conclusion about the fly.

**Next, and it is upstream of everything else:** a retinotopic encoder that
preserves colour identity. The fly's medulla carries roughly 60 cell types per
column, each encoding different visual features, so distributing ARC's sixteen
categorical colours across distinct medulla types within each column is
anatomically defensible rather than invented. The currently running arms become
the matched scrambled-retinotopy control for it rather than wasted work.

### 18. Three proposed improvements, two killed by measurement in ten minutes

Asked what else would make a positive difference. Applying the claim-tier rule
before building anything:

1. **More seeds per arm -- rejected, measured.** Variance decomposition of the
   paired differences (bio-eye vs control): between-game variance 0.080,
   within-game 0.068. At 3 seeds the game term contributes ~78% of the cluster
   variance, so doubling seeds narrows CIs by ~6% for 2x compute. The games
   are the noise, not the seeds. (The probe script's own printed inference
   said otherwise; its threshold compared between to within instead of
   between to within/n_seeds -- the claim-tier rule catching a bad bridge in
   the same hour it was written.)

2. **Saliency-guided candidate injection -- demoted, measured.** On 323
   click-tie turns across three click-dominant games, the controller's
   candidate menu already lies within 3 cells of the fly's saliency argmax on
   76% of turns (median 2.0 cells; 5% beyond 8). The menu is not the
   bottleneck. Parked with its measurement; worth revisiting only if the
   decoder arms show an effect that the 5% tail could be capping.

3. **Treatment-matched endpoints -- adopted, free.** Measured on
   sg-g2-nolearn: 6 of 25 games never click, so every click-decoder effect is
   structurally diluted ~24% on the full-set mean, and game heterogeneity is
   the dominant noise term (see 1). The decoder arms now carry PREREGISTERED
   endpoints, declared before either arm has run a row: primary = the 19
   click games, secondary = the 9 click-dominant games, with the full 25-game
   comparison always reported alongside. Registered in EXPERIMENTS.yaml; this
   is a design decision made blind, not a post-hoc subgroup.

### 17. The efference copy: the connectome learns what it just did

Prompted by asking whether any non-visual sense exists for ARC. Two do, and one
was mis-wired: reinforcement already reaches dopamine correctly, but the
agent's knowledge of its own action -- proprioception -- was spliced into the
VISUAL feature vector under the old encoder and lost entirely under the
bio-eye one.

**Precision, before anyone else has to burst this balloon.** Only the
*connectome* was action-blind; the controller always knew its actions, and the
fly speaks only at ties. And the old scrambled arms were *near*-blind rather
than blind: the 16 action features were sampled into roughly 90 of 390,272
projection connections -- present as noise. The section-16-adjacent claim
"every bio-eye arm was action-blind" is correct only with "connectome" in
front of it.

**Built and measured.** `encoder.efference_copy: antennal_mechanosensory`
delivers the previous action to Johnston's organ, the fly's own mechanosensory
entry (672 neurons, 34 types, sorted round-robin over the 8 action slots --
convention, declared). The chosen action rides from the controller into
`fly.observe(previous_action_id=...)`, and the forward model's reference
carries the same copy.

| property | measured |
| --- | --- |
| KC action separation (scale 0.05) | **144.7%** -- the learning site knows the action |
| LC (visual readout) perturbation | 0.2% |
| surprise on action-only turns | **exactly 0.000** at every scale (the copy cancels) |
| localization through the real path | 3.4 cells (surprise alone: 3.5) |

**Honest expectation, preregistered.** `sg-bioeye-lc-efference` should be
near-null on score BY CONSTRUCTION: the copy cancels out of the saliency map
and barely moves the readout. Its load-bearing use is `sg-mbdr-learn` -- the
mushroom body could not previously know which action preceded a reward, so
depression-only learning could form context->valence associations but never
context->action ones. The mbdr config now carries the copy at the calibrated
scale. A null on the bio-eye arm does not falsify H-EFFERENCE; a null on the
mbdr retest would.

### 16. The decoder was the scrambled half all along -- measured, then fixed

Prompted by asking what perception work is *demonstrably* wrong after the
bio-eye null. Reference practice (flyvis, Lappalainen et al., Nature 2024)
decodes the optic lobe as instantaneous per-column, per-cell-type activity.
Ours decodes click coordinates from **body-id-ordered blocks** of the readout
-- spatially meaningless, the exact mirror of the input scramble fixed in
section 12.

**The measurement that proves it** (16 trials, structured scenes, one 6x6
change at a known place, bio-eye encoder):

| method | median localization error |
| --- | ---: |
| hex-map readback of the state change (joint) | **0.8 cells** |
| prediction-error readback (joint) | **0.8 cells** |
| the deployed coordinate head | 23.5 cells |
| chance | 37.2 cells |

The fly's optic-lobe state knows WHERE to sub-cell precision; the deployed
decoder reads that same brain at chance. Side-finding: T4/T5 carry no hex
assignments in MaleCNS, so the spatial substrate is the 15 mapped
lamina/medulla types.

**Implemented**: `decoder.coordinate_source` --

- `retinotopic_state`: click x/y scores from per-column |state change| mapped
  back through the inverse of the encoder's affine assignment;
- `retinotopic_surprise`: the reference is the frozen connectome advanced on
  the previous frame -- the network free-running as its own one-step forward
  model. Predictive coding in spirit, JEPA-adjacent in shape, and zero trained
  parameters because the predictor IS the graph. Cost: one extra advance per
  turn.

**The wired-path measurement, and the day's most interesting number.** Through
the real `preference()` path (separable x+y marginals over candidate clicks):
state_change degrades to **12.1 cells**; surprise holds at **3.5**. Mechanism:
the free-run reference contains the network's own settling transients, so they
cancel, leaving only input-caused deviation -- the forward model explains away
self-generated dynamics. The prediction is not decoration; it is what makes
the marginal readback usable.

**Claim boundary, stated before the arms run.** All of this is localization,
measured; none of it is score. H-RETINO-DECODER is open, `sg-bioeye-lc-retdec`
and `sg-bioeye-lc-surprise` are registered against `sg-bioeye-lc`, and three
straight full-matrix nulls counsel exactly zero confidence beyond the
measurements themselves.

### 15. The bio-eye result: null, and the third partial-lead collapse

`sg-bioeye-lc` against its matched scrambled control `sg-lc`, 75 rows each,
identical readout, identical everything except the encoder:

| | score | levels | delta |
| --- | ---: | ---: | --- |
| scrambled projection (`sg-lc`) | 0.241245 | 16 | reference |
| retinotopic categorical colour (`sg-bioeye-lc`) | 0.250396 | **16** | `+0.009151`, CI `[-0.125, +0.172]`, p=0.817 |

Levels exactly tied. H-RETINOTOPY-COLOUR is **null** on the LC readout: giving
the visual hierarchy input it can use -- adjacency preserved, colours
categorical, motion visible to T4/T5 at 3.4x -- changed nothing the score can
see. The T4/T5 bio-eye arm is still running and gets its own verdict.

**The partial-lead collapse, third occurrence.** At 59 rows the matched delta
had drifted to +0.072 with a 14-12 level lead; the final 16 rows erased it
completely. Same shape as the tiebreak arm (+10.6% at 41 rows, gone at 75) and
consistent across this project: seed-ordered partials drift positive in the
middle rows and regress by the end. The league's no-verdict-on-partials rule
has now paid for itself three times. The currently running arms show partial
deltas of +0.12 (permuted) and +0.07 (bio-eye t4t5); given the pattern, the
expectation is regression, and no excitement is licensed before row 75.

Both scrambled-readout arms also completed and received verdicts:
`sg-lc` +0.0378 (p=0.526) and `sg-t4t5` -0.0280 (p=0.557) against
`sg-g2-nolearn` -- H-PERCEPTION-READOUT closes as null on complete pairs.

### 14. The mushroom body done right: built, calibrated, awaiting its turn

Built now, to run after the bio-eye battery settles, per the plan. Everything
below is construction and calibration; no behavioural claim is made until the
`sg-mbdr-*` arms run.

**The input bus (H-MB-INPUT-BUS).** `encoder.mb_input_bus: colour_histogram`
drives the 627 uniglomerular projection neurons -- measured direct: 22,581
synapses reaching 3,811/4,064 Kenyon cells at ONE hop, 7.23% of KC input weight,
which corrects section 11's "two hops" framing -- with the screen's global
colour histogram as an odour-mixture analogue. Glomerular types are assigned to
colours by sorted order, round-robin: convention, not biology, and the
permutation-control pattern applies here too if the bus ever shows an effect.
Live probe: PN activity 2.5e-05 -> 2.3e-01; KC patterns separate colour-9 from
colour-3 screens by 23-78%; reinforcement moves |dW|=3.6. The composite
projection refuses any overlap with the visual encoder, so nothing can be
double-driven silently.

**APL sparsification (H-APL) -- supported, with a mechanism finding worth more
than the knob.** Scaling the 4,633 APL->KC inhibitory synapses is exact to the
digit and touches nothing else. But in a signed tanh network, inhibition CANNOT
sparsify absolute activity: it drives cells negative, and |-0.4| counts as
active. Measured: APL x4-x25 made |abs| sparsity worse (0.123 -> 0.177,
latching 0.95). On the positive lobe -- firing, the only biological reading --
APL behaves exactly as Lin et al. 2014 predicts: x2 0.098, x4 0.078 (in the
0.05-0.11 band), plateauing at x10-25 because negative feedback self-limits.

**Corollary fix: rectified eligibility.** The plasticity trace previously used
|abs| Kenyon activity, which counted an APL-inhibited cell as MORE eligible the
harder it was suppressed -- backwards from the biology it models. Eligibility
now reads the positive lobe only (`eligibility_rectified`, default true,
declared with the measurement that exposed it; `false` restores |abs| for
comparison).

**Calibration, not assumption.** `mb_input_scale` swept against the KC firing
band: every naive scale (1.0 down to 0.02) saturates the KC pool through its
85% recurrence; 0.003 at APL x4 lands at 0.091, in band, DN live at 1.5e-04.
The sparse-and-loud-but-starved regime (APL x10-25, tiny scale, separation up
to 227% but DN dimming toward 5e-05) was measured and deliberately not chosen.

**Registered ahead of running:** `sg-mbdr-nolearn` (circuit changes alone, vs
`sg-g2-nolearn`), `sg-mbdr-learn` (the fair retest of H-MB-LEARNING, vs
`sg-mbdr-nolearn`), and both falsification controls, gated on the main arm
separating from its baseline. The league lists them as `missing` until they
run.

### 13. The bio-eye battery: main arm, its falsification control, and T4/T5

Three arms complete the encoder experiment. All assemble and discriminate,
verified before launch, all on the threaded matvec (4 threads, bit-identical).

| Arm | Config | What it isolates |
| --- | --- | --- |
| `sg-bioeye-lc` (running) | `literal_rate_bioeye_lc` | encoder vs the scrambled `sg-lc` control: does retinotopic categorical colour matter at all |
| `sg-bioeye-lc-permuted` (queued) | `literal_rate_bioeye_lc_permuted` | assumption A: does it matter *which* medulla type carries which colour |
| `sg-bioeye-t4t5` (queued) | `literal_rate_bioeye_t4t5` | the highest-signal readout (13,585 T4/T5, ~25x DN discriminative signal) with usable input; `sg-t4t5` becomes its matched scrambled control |

**The permutation control, measured before use.** `colour_permutation_seed:
20260923` reassigns 14 of 16 colours to different cell types; the 0/15
collision pair still shares a channel, so the collision structure is matched.
Deterministic across builds. An identity permutation is refused at construction
-- a control that changes nothing must fail loudly, not run quietly.

**Known imperfection of the control, declared rather than discovered later:**
cell types differ in neurons per column, so reassigning colours shifts total
injected drive by ~4% (1531.5 vs 1593.2 on a random frame) and nonzero support
by ~3.7%. Matched in information and structure, not exactly in input energy.
The adaptive per-neuron standardizer removes global scale downstream, but a
small score difference between the declared rule and the permutation should be
checked against drive totals before being read as mapping semantics.

**How to read the three results together, written before any of them exist:**

- bio-eye > scrambled, permuted = bio-eye: retinotopic categorical input helps;
  the specific colour-to-type assignment is harmless convention, as assumed.
- bio-eye > scrambled, permuted < bio-eye: the assignment itself carries weight
  it has no biological right to carry; report as an interface artifact, not as
  fly computation.
- bio-eye = scrambled: the encoder fix, the best-motivated change in the
  project, did not matter either -- and the perception readouts join the list of
  correctly-implemented components that produced nothing.

### 12. Plan: give the fly's eye a real image (measured before designing)

The first principle above says every computation must be carried by fly neurons.
Section 11 established that no experiment has yet given a fly circuit input it
could use. This is the fix, and per the user's instruction the assumptions were
measured **before** the design rather than after.

#### What was measured, including two assumptions that failed

| # | Assumption | Measured | Verdict |
| --- | --- | --- | --- |
| A1 | The optic lobe can be addressed retinotopically | 23,720 `ol_intrinsic` neurons, 892 columns on a 36x39 lattice; `ol_sensory` photoreceptors carry **no** column assignment, 0 of 6,098 | holds -- inject at lamina/medulla, not photoreceptors |
| A2 | A column has enough distinct cell types to carry 16 colours | **15** types, not 16: C2, C3, L1, L2, L3, L5, Mi1, Mi4, Mi9, T1, Tm1, Tm2, Tm20, Tm4, Tm9. 814 of 892 columns (91.3%) carry all 15 | **FAILED as stated** -- one collision is unavoidable |
| A3 | ARC colour 0 is background, so 15 types suffice for colours 1-15 | Over 1,200 real frames across 4 games: colour 0 is **2.72%**, not background. Colour 9 dominates at 36.89%, then 12 at 17.18%, 4 at 15.37%, 5 at 13.03% | **FAILED** -- there is no free colour to drop |
| A4 | The mushroom body's real input pathway could be driven | `cb_sensory` reaches **4,025 of 4,064** Kenyon cells in **2 hops**, inside the K=4 budget | holds, with a caveat below |

A2 and A3 would each have forced a revert within two commits. They are recorded
here because the design below is shaped by their failure, not by their success.

#### The design

**Injection site.** The 892 occupied columns, at the lamina and medulla
interneurons, because photoreceptors carry no coordinates. The ARC 64x64 grid
maps onto the hex lattice by the fixed affine assignment already compiled by
`scripts/build_retinotopy.py`.

**Colour.** Colour `c` drives medulla type index `c mod 15`. Fifteen channels,
sixteen colours, so colours 0 and 15 share a channel. The rule is fixed and
game-independent **on purpose**: choosing the collision from the measured
frequencies above would tune the encoder to four games and is exactly the kind
of engineering this project must not put in the plumbing. The collision is
declared, not hidden, and 78 columns (8.7%) carrying fewer than 15 types lose
their highest channels.

This is the fix for the previous retinotopic encoder's 0.190476 -> 0.003156
collapse. That encoder preserved space and destroyed colour, mapping sixteen
categories onto a scalar luminance ramp `grid / 15.0`. ARC colours are
categorical: colour 3 is not between 2 and 4.

**Change detection is removed, deliberately.** The previous encoder spent T1, C2
and C3 on an explicit changed-cell channel. Those channels are returned to
colour, and **T4/T5 compute motion themselves** from the frame-to-frame sequence,
which is what 13,585 direction-selective neurons are for and what the first
principle demands. Network state already persists across actions, so the
temporal structure the computation needs is present.

**Non-visual features.** The legal-action mask and previous-action one-hot are
not visual quantities and have no retinotopic home. They keep the existing sparse
projection into a disjoint sensory subset, declared as plumbing.

#### The mushroom body, and an honest caveat

A4 holds structurally, but driving `cb_sensory` means piping ARC data into the
fly's **olfactory** input. ARC has no odours, so this is not a more faithful use
of the organ than the current one -- it is a different arbitrary mapping. The
defensible framing, and the only one to be used: the mushroom body is an
associative memory whose input bus is the projection-neuron pathway, and that bus
is what gets driven. It is not being treated as an olfactory organ. This is a
**separate change from the encoder** and must not be bundled with it, or the two
confound.

#### Order of work

1. Compile `retinotopy.npz` into the `-modulators` bundle, which does not have it.
2. Implement the colour-preserving retinotopic encoder.
3. Verify before running anything: neighbouring ARC cells drive neighbouring
   columns; distinct colours drive distinct types; T4/T5 respond to a moving
   stimulus more than to a static one.
4. Run it against the scrambled-retinotopy arms already in flight, which become
   its matched control.
5. Only afterwards, and separately, consider the mushroom-body input bus.

## Execution telemetry

Every runnable component is instrumented. Result bundles already recorded
*provenance* -- which graph, which config, which game, hashed. What nothing
recorded was *execution*: what a run did, in what order, how long each stage
took, what it decided and why, and how it ended. That lived in ad-hoc `print`
calls whose format differed per script, so reconstructing a run meant reading
the source that produced it.

`src/flygi/telemetry.py` is the single place that changes. One JSON object per
line in `results/telemetry/<run_id>.jsonl`, append-only, so a killed run still
leaves everything up to the moment it died -- which is when telemetry matters
most. The console keeps its existing prose: machines read the file, people read
the terminal, neither is degraded for the other.

**Coverage: 22 of 22 scripts plus the `flygi` CLI.** Each gets `run.start`,
`run.end` and a recorded cause when it does not finish, from one line at its
`__main__`.

The five questions a reader or tool can answer without the source:

| Question | Answered by |
| --- | --- |
| what | `event` (dotted, hierarchical) plus `data` |
| when | `ts` wall clock, `elapsed_s` monotonic, `seq` for ordering within a timestamp |
| where | `run.start`: git commit and dirty flag, host, platform, Python and package versions, pid, argv, cwd, plus the resolved path and SHA-256 of every config read |
| how | `phase.begin`/`phase.end` with per-phase duration and outcome |
| why | every decision, warning and failure carries `reason` |

Read them with `scripts/inspect_telemetry.py`: recent runs, one run in full,
filtered by component or event name, `--failures` for bad endings, `--json` for
another tool to consume.

**Three defects the tests and first runs caught, all fixed:**

- `json.dumps(default=str)` invokes `__repr__` on the payload, which is
  arbitrary code and can raise anything. The guard caught only `TypeError` and
  `ValueError`, so an awkward object could have killed a six-hour evaluation.
  Now deliberately broad, degrading the event to a warning.
- `argparse --help` exits via `SystemExit(0)`, which was recorded as **failed**.
  Every help invocation would have poisoned the failure list until real failures
  stopped standing out. Clean exits are now `ok`; nonzero is `failed` with the
  code.
- A coverage audit reported the CLI as instrumented. It was a false positive:
  `cli.py` owns an unrelated function also called `entrypoint`. The CLI was
  genuinely uninstrumented and now is, via an aliased import.

Secrets are never captured: environment recording is an explicit allowlist, and
a test asserts a token in the environment does not reach the log.

## Interruption and recovery

Every evaluation checkpoints each completed row to `<condition>.rows.jsonl`
immediately, rows are independent and deterministic given (seed, game) -- the
tiebreaker and its standardizer are reset per game -- so an interrupted run
loses at most the row in flight, and `--resume` continues exactly. Laptop sleep
is not an interruption at all: macOS suspends the processes and they continue
on wake.

The gap was recovery after a real death (reboot, battery, kill): nothing
auto-restarts and the launch commands lived in nobody's head reliably.
`scripts/resume_runs.py` closes it using what telemetry already records --
every run's full argv at `run.start`. It lists each condition that has a
checkpoint but no final bundle and no clean `run.end`, prints the exact command
to continue it, skips anything currently running (checked against the process
table), and relaunches only with `--exec`. After any reboot:

    uv run python scripts/resume_runs.py --exec

## Execution speed

The agent is one sparse matvec in a loop, and SciPy's `csr_matvec` is a
single-threaded C kernel that Apple's Accelerate does not touch. Measured on the
deployed graph (166,700 nodes, 24,994,595 edges, float32) on an Apple M4: 54.0
ms per matvec at 3.7 GB/s, against roughly 120 GB/s of machine bandwidth. The
operation is bandwidth-bound and was using about 3% of the machine.

| Implementation | ms | GB/s | Speedup | Bit-identical |
| --- | ---: | ---: | ---: | --- |
| SciPy CSR, single thread | 54.0 | 3.7 | 1.00x | reference |
| Numba `njit(parallel=True)` | 18.7 | 10.7 | 2.88x | **no**, 1.19e-07 |
| **SciPy + threaded row split** | **14.4** | **13.9** | **3.76x** | **yes** |

End to end on a real 120-action game: 24.2 s at one thread, 10.5 s at four
(2.31x), 10.2 s at six -- with **identical replay hashes at every thread count**,
so no baseline in this worklog needs re-measuring. The end-to-end figure is
below the matvec figure because encoding, decoding and the environment step are
serial.

**Why row splitting is exact.** Each output element is one row's dot product,
computed by SciPy's own kernel in SciPy's own order. Float32 addition is not
associative, so order is everything. Splitting *within* a row -- a GPU segmented
reduction, or Numba's restructured reduction -- is not exact, which is why Numba
was measured, found slower *and* inexact, and removed again rather than adopted.

**The dangerous defect found on the way, and the reason to have written the
test.** `csr_matrix((data, indices, indptr), copy=False)` **copies anyway**:
measured, the block does not share memory with the parent even when every dtype
already matches. That would double the 200 MB matrix and, far worse, silently
sever in-place plasticity -- the mushroom body writes weights through the parent
matrix, and a copied block would never see them, so section 9's learning would
have appeared to run while changing nothing. Blocks are now built as empty
shells with their arrays assigned afterwards, and `SpmvPlan.rebuild` raises if
they ever stop sharing memory rather than degrading quietly.

Defaults and gotchas are in `docs/performance.md`; the numbered pitfalls are in
the `src/flygi/dynamics/spmv.py` docstring. Short version: default 4 threads,
`FLYGI_SPMV_THREADS=6` for a machine to yourself, `=1` to reproduce a
pre-optimisation measurement, and keep `arms x threads <= 10`.

## The experiment league

`EXPERIMENTS.yaml` at the repository root is the central claim-tracker: every
condition ever run, the baseline it is fairly compared against, the operating
regime it belongs to, and the hypothesis its result moves. `scripts/league.py`
joins it with the immutable bundles, the live checkpoints and the telemetry to
render the leaderboard -- the registry owns the *why*, the artifacts own every
number, so the table cannot drift from reality. `LEAGUE.md` is the generated
snapshot; edit the registry, never the snapshot.

Guardrails, each one a mistake this project actually made:

- **No verdict from a partial.** A 41-row seed-ordered partial once showed
  +10.6% that the full matrix erased. Partials get a delta labelled `partial`
  and an explicit "biased sample, no verdict" warning.
- **No cross-regime comparison.** gain0.9 numbers are measurements of a
  numerically dead network; the league refuses to compare them against live
  ones (controller-only excepted, since it uses no connectome).
- **Unregistered bundles are surfaced loudly.** All 20 historical Track A/B
  bundles are now registered, so the full ablation record -- 35 experiments, 10
  hypotheses, 3 regimes -- is in one queryable place.

The hypothesis register in `EXPERIMENTS.yaml` supersedes the prose assumptions
table below as the tracked state; the prose stays as narrative.

## Assumptions register

Every mapping from an ARC quantity onto a fly quantity is an invention until
shown otherwise. This is the list, kept current, so no reader has to guess which
results rest on a choice rather than a fact. Each is labelled in the source with
`ASSUMPTION` or `HYPOTHESIS` at the line that encodes it.

| # | Assumption | Where | Status | If wrong |
| --- | --- | --- | --- | --- |
| A | Colour `c` drives medulla type index `c % 15` | `encoding/retinotopic.py` | **assumed, biologically unmotivated** | Results hold as "retinotopic categorical input helps", not as "the fly's visual feature channels help" |
| B | Channel order is the sorted type name | `encoding/retinotopic.py` | assumed, arbitrary | Nothing, if A's permutation control is null |
| C | Drive magnitude is fractional colour occupancy of a column | `encoding/retinotopic.py` | assumed | Weakly constrained; ~3.4 ARC cells per column |
| D | All drive is positive; ON/OFF opponency dropped | `encoding/retinotopic.py` | assumed | The lamina's opponency is unexercised by this input |
| E | T4/T5 can compute motion from the frame sequence | `encoding/retinotopic.py` | **hypothesis, partially verified** | See below |
| F | Dopamine's sign in ordinary propagation is positive | `configs/*_modulators.yaml` | declared approximation | Modulator contribution to rate is mis-signed; plasticity uses activity and real anatomy, not this sign |
| G | The mushroom body may be driven through its olfactory input bus | WORKLOG section 12 | **assumed, not yet built** | ARC has no odours; this is a different arbitrary mapping, not a more faithful one |
| H | `gain=2.0` is the right operating point | `configs/literal_rate_mb_learning.yaml` | measured compromise | KC sparsity sits at 0.123 against a biological 0.05-0.11; declared, not hidden |

**On A, the largest one.** Medulla and lamina types are not colour bins. L1 and
L2 head the ON and OFF luminance pathways; Mi and Tm types carry sustained and
transient features. None of them encodes "ARC colour 7". The mapping exists
because the grid has sixteen categories and a column has fifteen addressable
types, and something had to be chosen. **The control that tests it** is a
permuted colour-to-type assignment: if a permutation scores the same, the
specific mapping carries nothing and only the categorical-plus-retinotopic
structure matters. That control must run before any claim that the fly's visual
*types* are doing work.

**On E, including a wrong measurement.** The first check compared population-mean
T4/T5 activity for a moving versus a static bar and found a ratio of 1.001,
which reads as failure. That metric was wrong: direction-selective cells encode
motion in *which* cells fire, not how many. Measured at the pattern level, the
frame-to-frame change in T4/T5 activity is **3.41x** larger for a moving bar,
2.53x for LC, with the conditions separated by ~10% of activity. Motion is
visible. What is **not** established is that it is visible as *direction-
selective* motion: a frozen rate model has none of the explicit delay lines that
make T4/T5 direction-tuned in the animal, so this may be undifferentiated change
sensitivity wearing a motion detector's name.

## Official submissions

| Ref | Configuration | Status | Public score |
| --- | --- | --- | ---: |
| `56444435` | signed graph, 80 actions, seeded literal policy | complete | **0.00** |
| `56459984` | signed graph, 600 actions, mild loop escape | complete | **0.00** |

The version-3 notebook preflighted the exact 166,700-node / 24,559,055-edge
runtime, `K=4`, loop escape 0.25/0.50, zero trainable parameters, and the three
expected array hashes. No fallback policy was used. The published dataset's
`config.yaml` was downloaded back and hashed before submitting
(`63b50521c324ecd1c2d39e1498dd8113b9d6838731ea7f31b3fb8a94317e5c7c`,
byte-identical to the intended config); the preflight verifies the three array
hashes but **not** the config, so serving the previous version would otherwise
have silently submitted the 0.000000 condition.

Both submissions establish the same thing: **configuration tuning does not move
the hidden-set score.** Budget is saturated (1600 actions bought nothing over
600 locally; 600 bought nothing over 80 on the hidden set), and the held-out
split above shows why -- every local gain so far lives on specific known games.

## Why a living connectome can score 0.00

This is not paradoxical. Natural selection shaped fly nervous systems over
millions of years for embodied survival, not symbolic program induction. More
importantly, FlyGI currently supplies only a wiring diagram and substitutes or
omits much of what makes that wiring compute:

1. **The retina is scrambled.** A random projection destroys eye columns,
   color channels, optic flow, and spatial neighborhood.
2. **The motor semantics are scrambled.** Body-ID DN blocks have no principled
   relationship to ARC arrows, click, interact, or undo.
3. **Physiology is flattened.** Every neuron receives the same leaky-tanh rule,
   leak, gain, and time scale. Real cell types, receptors, spikes, adaptation,
   delays, and oscillations are absent.
4. **Embodiment is missing.** The fly's loops expect proprioception, efference
   copy, self-motion, and muscles. ARC supplies none of those unless engineered.
5. **Learning was initially amputated.** The deployed signed runtime zeroed all
   modulatory output, deleting 129,132 DAN->KC and 3,195 DAN->MBON edges.
6. **The task is alien.** ARC-AGI-3 needs goal inference, compositional rule
   learning, counterfactual prediction, and planning. A fly has useful
   perception, memory, valuation, and control circuits, not a ready-made ARC
   executive.

The fair conclusion is not “166,700 neurons are useless.” It is “our current
interface and dynamics fail to express the functions that those circuits evolved
to perform.”

## Goal: a credible route to score 10.0

### What 10.0 means

The live Kaggle leaderboard read on 2026-09-22 had a leader at 18.81 and seven
teams at or above 10.0. A score of 10 is therefore a top-eight-class system, not
a parameter-tuning milestone.

Breadth alone cannot get there. In a six-level game, level 1 is capped at
`100 / (1+2+3+4+5+6) = 4.76`. Even reaching only level 1 in every such game
would average 4.76. Score 10 requires efficient multi-level depth across many
unseen games. The missing capabilities are action-effect learning, goal
inference, executable world models, planning, and cross-level transfer.

### Target architecture

```text
frame/history
   -> stable UI-masked object scene + learned visual features
   -> candidate actions / component-grounded clicks
   -> online action-effect and uncertainty model
   -> state-transition graph + executable rule hypotheses
   -> information-gain probe OR shortest verified plan
   -> legal action

parallel FlyGI branch
   -> retinotopic optic-lobe drive
   -> motion / salience / CX context / MB novelty / DN prior
   -> guarded residual features and tie-breaks inside the controller
```

The outer controller supplies functions the connectome does not automatically
provide: object tracking, controllability, goal hypotheses, search, and plan
verification. The fly supplies structured perception, memory, novelty/value,
and action priors. Hard legality, death bans, and verified replay paths remain
controller-owned.

### Phase 0 — finish the current head experiment

**Build:** allow the active 60-generation CEM run to finish; validate its
artifact, deterministic loading, trace ablation, and held-out-game result.

**Promotion gate:** the trained head must beat the frozen loop-escape policy on
held-out games, retain a material objective gap when compared with trace
ablation, and pass a parameter-matched bypass run. Otherwise keep it as a named
negative result and do not spend a submission.

**Purpose:** close the experiment already consuming compute. This head alone is
not expected to reach 10.

### Phase 1 — competent generic exploration kernel

Implement or adapt a permissively licensed state-graph controller with:

- frozen HUD/UI masking and stable state hashes;
- 4-connected component click candidates on actual foreground pixels;
- action/click effect statistics and calibrated novelty;
- hard bans for known terminal/dead actions;
- BFS return to the nearest reachable frontier;
- exact replay paths and cross-level retention of mechanics.

Start with controller-only. Then let graph logits break equal controller
priorities and rank valid component clicks; never let the graph resurrect an
illegal, failed, or fatal action.

**Gate:** 25 public games x three diverse seeds x 500 actions; zero protocol
violations; progress in at least three distinct games; controller-only must beat
the 0.097568 random benchmark. The hybrid must retain at least 95% of controller
score. A fly claim additionally requires hybrid > controller-only and bypass.

**Expected effort:** 3-5 focused engineering days. **Score target, not forecast:**
0.3-1.0 hidden.

### Phase 2 — replay-pretrained affordance and value model

Acquire the official 342 human replays for all 25 public games and combine them
with counterexamples generated by our local random/graph runs. Split by whole
game, never by transition, so validation measures cross-game transfer.

Train one small offline model with four heads:

1. probability each legal action or component click changes the state;
2. object-level next-state delta and avatar displacement;
3. click-affordance heatmap;
4. novelty/progress value used to rank frontiers.

Use augmentation that preserves mechanics: translation, palette permutation,
component permutation, UI-strip perturbation, and trajectory truncation. Do not
feed game IDs or source code. Initialize online learning from this prior, then
update from each new environment's actual transitions.

**Gate:** leave-five-games-out cross-validation; effect calibration and
next-object-delta accuracy must beat frequency/identity baselines; the complete
controller must improve score and level depth on every held-out fold, not only
memorized training games.

**Expected effort:** 1-2 weeks. **Score target:** 1-3.

### Phase 3 — online executable world model and planning

Represent frames as tracked objects and learn a small library of composable
transition primitives: translate, rotate, recolor, toggle, select, carry,
collide, spawn/delete, counter/cycle, and conditional interaction. Maintain
multiple rule hypotheses rather than committing after one example.

At each frontier:

- choose the cheapest action that maximally separates competing hypotheses;
- verify every predicted transition against reality;
- turn mismatches into counterexamples immediately;
- plan with BFS/A*/beam search only through transitions whose predictions are
  calibrated; stop a plan at the first mismatch and repair the model.

When a level completes, back-label its shortest successful path, train the value
head, infer which object relation constituted progress, and transfer both the
mechanics and goal schema to later levels.

**Gate:** on held-out games, at least 65% exact prediction for never-taken legal
actions on visited states; probes below 20% of executed actions; multi-level
progress in at least five distinct public games; every planned action carries a
prediction that is checked afterward.

**Expected effort:** 2-4 weeks. **Score target:** 3-6.

### Phase 4 — depth, skill transfer, and compute allocation

- Store successful plans as abstract object-relation skills, not pixel scripts.
- Retrieve by scene/mechanic similarity and adapt using the learned world model.
- Route click-only, movement, orchestration, and mixed games to specialized
  candidate generators while sharing one transition/value model.
- Run a small ensemble of rule hypotheses and learned dynamics; allocate actions
  and wall time by uncertainty and observed progress.
- Use later levels' higher score weight deliberately: once mechanics are known,
  minimize redundant probing and prioritize efficient plan execution.
- Keep a seven-hour global guard and benchmark CPU/GPU parity before submission.

**Gate:** leave-game-out evaluation must show broad multi-level depth rather
than one-game spikes; no game-specific identifiers or source-derived rules; at
least two independent seeds with verified trace diversity; staged Kaggle
preflight must reproduce local model hashes.

**Expected effort:** 3-6 additional weeks. **Score target:** 6-10+.

### Phase 5 — make the fly contribution biologically meaningful

This proceeds beside Phases 2-4 but never blocks the competent controller:

1. map 64x64 ARC space to the 36x39 optic-lobe hex layout;
2. send luminance/change to R1-R6-like channels and fixed color-opponent codes
   to R7/R8-like channels;
3. expose named T4/T5 motion, LC/LPLC salience, central-complex context,
   KC/MBON novelty/value, and DN/VNC action-prior summaries;
4. route previous action and observed consequence through ascending/efference
   channels instead of the eye;
5. learn only small, parameter-matched pooling/residual heads first; add local
   KC->MBON plasticity only after generic delayed-cue and novelty probes pass.

Required comparisons are controller-only, controller + real graph, identical
bypass, degree-preserving null, shuffled retinotopy, and named-module lesions.
The real graph earns credit only by beating them on the same candidate set,
training budget, and seeds.

## Submission gate (set by the user, 2026-09-23)

Nothing is submitted unless **both** hold:

1. **The fly is load-bearing.** The agent must use the connectome in a way that
   changes its decisions. The Phase 1 state-graph controller alone is not a
   submission candidate however well it scores locally -- a scaffold that scores
   with the connectome inert is a negative result about the fly wearing a
   leaderboard entry as a disguise.
2. **It beats both existing submissions.** `56444435` and `56459984` each scored
   0.00, so the bar is a nonzero leaderboard score.

Condition 1 is not satisfied merely by the fly being present in the process. It
requires a control arm showing the connectome contributes beyond what any
state-dependent tiebreaker would: see the `grid_hash` arm (no anatomy, varies
with the observation) and the degree-preserving null arm. If the real fly ties
the grid hash, the fly is decoration and the honest report is that the
controller scores.

Slots reset 00:00 UTC, one per day.

## Promotion and submission discipline

- One frozen intervention, one exact local gate; no edit/revert tuning loops.
- A daily submission must test a material capability change, not a larger
  action budget or cosmetic variation.
- Public-game development is allowed but always labelled; game-held-out results
  choose architectures, while Kaggle hidden score chooses submissions.
- Keep controller performance and fly attribution separate. We may submit a
  high-scoring hybrid before full controls, but we do not claim that the fly
  caused its score until the controls support that statement.
- Checkpoint source, WORKLOG, model/data provenance, validation, and next work
  before each push. Never commit generated traces or large assets.

## Ordered next actions

1. **Completed and stopped:** the Python click-head coordinate switch, asymmetric
   golden, and exact replay are recorded under H-COORDINATE-CONVENTION. The
   aggregate primary moved, but the robustness gate failed; do not launch its
   behavioral A/B or tune this branch further.
2. **Completed and stopped:** H-RETINO-SURPRISE-RECURRENCE is contract-valid;
   the coordinate repair passed, but the exact real-vs-controls conjunction
   failed. Keep the convention/goldens, but do not tune or run ARC behavior in
   this branch.
3. **Completed and stopped:** H-VISUAL-MEMORY-ENTRY failed its preregistered
   representation gate: native 0.521875 versus sensory 0.55, type-mean 0.497917,
   graph-off 0.5. Do not build the proposed visual-MB memory/plasticity branch,
   tune this panel, or promote it to ARC. Before any replacement, freeze an
   independent biological visual-model validity test; a new design is required,
   not another setting of this failed experiment. No such next run is queued.
4. Defer remaining notebook/deployment gates until a genuinely load-bearing
   neural candidate earns deployment. The pending gates are decision-critical
   asset hashes, process-visible Swarm failures, mutable ACTION6 payload
   isolation, and a short multi-game RSS soak.
5. Do not submit `combo_light` as FlyGI. Require controller-only / real graph /
   degree-preserving-null evidence before a FlyGI submission or attribution
   claim.

## Durable limitations and claim boundary

- Heuristic transmitter signs and uniform rate dynamics are not biological
  physiology.
- The public 25 games are development data; the Kaggle public leaderboard uses
  55 unseen games and the final private leaderboard another 55.
- Existing result distributions are extremely sparse and game-clustered.
- The current best local scores come from first-level completions and do not
  predict a hidden score reliably.
- Structural non-randomness is established; behavioral advantage is not.
- Score 10 is a credible engineering objective because current teams exceed it,
  but it requires a new world-model-and-planning system. It is not a credible
  outcome of more loop-escape tuning, a larger budget, or the 520-parameter head
  alone.
