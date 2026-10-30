# Task 5 (Brain-Score) — due diligence delta, 2026-10-04

What has changed since the 2026-09-30 survey ranked this arena fifth,
what was re-verified today, and what the kill test must decide before
any BrainModel wrapper or submission plumbing exists. Status: the
survey's premise re-verified; kill test NOT yet registered — the
registration follows the user's go, per the program pattern.

## What the survey said (2026-09-30)

"Brain-Score (standing, open submission). Oddball, cheapest of all:
score the compiled fly visual system as a primate ventral-stream
model. Whatever the number, no connectome model is on the board.
Static images suit the eye map + early filters."

## Re-verified today (SOURCED 2026-10-04, this cloud session)

- **Submission still open and automated.** Models go in as a zip via
  the brain-score.org website (Jenkins converts it to a PR) or as a
  GitHub PR directly; passing PRs auto-merge and scoring runs on
  their OpenMind cluster (brain-score readthedocs, submission page,
  via web search — the readthedocs host itself is egress-blocked
  from this container).
- **Package alive.** brainscore-vision 2.3.22 on PyPI, released
  2026-06-09; requires Python >=3.11; 29 runtime deps including
  torch>=2.6, torchvision>=0.21, opencv, psycopg2-binary (measured:
  `curl pypi.org/pypi/brainscore-vision/json`).
- **Local scoring on public benchmarks exists.** A limited public
  pool (e.g. MajajHong2015public.IT-pls) is scorable locally without
  submitting; models implement the BrainModel interface
  (start_task / look_at) only for the full submission, not for a
  local public-pool score.
- **Container reachability (measured):** brain-score.org HTTP 000,
  brain-score.readthedocs.io egress-blocked, github.com/brain-score
  403 via proxy (unattached repo), pypi.org 200. Benchmark stimulus
  and neural data are therefore presumed local-side acquisition, like
  DSEC and DVS Gesture (untested which host serves them — likely S3).

## Moved priors since the survey

1. **Base rate is now 0 for 14** (survey said 0 for 12). H-FLYGI-
   FLYBENCH-CALIBRATED and H-T4T5-DVS-GESTURE both refuted since.
2. **Rewire-over-real is now 4 consecutive on T4/T5** (ARC motion,
   DSEC real + uniform-tau context, DVS Gesture). Every dynamics-
   bearing fly circuit we have scored against its degree-preserving
   rewire on an external task has lost to it.
3. **The one surviving fly-positive is static anatomy, not
   dynamics.** The eye map's measured ARC win (2.59x vs scrambled
   11.59x action cost, 4.5x separation) was the compiled column
   assignment deployed as metadata — no live neurons. The survey
   line "static images suit the eye map + early filters" quietly
   bundles a circuit that won as anatomy with dynamics ("early
   filters") of the family that keeps losing. The kill test must
   split that bundle.
4. **Composing-stages warning stands** (FlyBench's flyvis->LIF
   hand-off failure; our own Task-3 calibrated arm).

What has NOT moved: lamina/medulla early filters (the ol_intrinsic
population, 23,720 neurons over 892 columns) have never themselves
been tested against their own rewire. T4/T5's four losses are a prior
about a sibling circuit, not a measurement of this one. That is the
open question, and it is exactly the shape of question this program
exists to answer either way.

## The cross-phylum mapping is the biggest declared assumption yet

Brain-Score regresses model features onto PRIMATE ventral-stream
recordings (e.g. IT). Any entry asserts, implicitly, that fly early
vision produces features useful for predicting primate neural
responses to static natural images. Two new assumption rows are
registered today (AB-4, AB-5; AB-1..AB-3 are the survey's):

- **Image -> ommatidia drive.** A static image must be presented to a
  luminance-change-native frontend. Options (sustained luminance
  drive; onset flash + settle, as fc2 does) are ASSUMED choices; the
  kill test fixes ONE and declares it, no sweep.
- **Fly features -> primate predictivity.** Pure invention until
  measured. The survey's own hedge ("whatever the number") is the
  honest frame: the contribution is the first connectome row on the
  board, at whatever score, with its controls.

## Trivial alternatives (named before anything is built)

1. **Raw-pixel features** through the identical readout/regression —
   Brain-Score's own baseline family; costs nothing.
2. **The patch's degree-preserving rewire**, same plumbing, per seed —
   the control that has won four straight against T4/T5.

## Kill-test sketch (to freeze in killtest_design.md on go)

Score lamina/medulla early-filter population features on ONE public
benchmark (candidate: MajajHong2015public.IT-pls, their metric code
run verbatim, locally) against both trivial alternatives, BEFORE any
BrainModel wrapper, website account, or submission plumbing exists.
PASS iff real wiring beats BOTH raw pixels and its own rewire on the
same split. KILL closes the arena with no submission built (a
sub-pixel or sub-rewire score is a recordable connectome limit, not
an entry). BLOCKED if the public benchmark data cannot be acquired
locally or the package cannot run on the user's machine.

Execution split, per the established pattern: cloud registers and
builds what is buildable without data; the scoring run is local
(package install on the user's machine is the user's own call; the
AF-6 in-container authorization covered flybench only and is NOT
assumed to extend to brainscore-vision).

## Decision needed from the user

- **Go / no-go on Task 5** as sketched (registration would be written
  and frozen first, as always), versus
- an explicit go on the still-gated Task 4 Keyword-FSCIL/MB limb, or
- a re-rank of the remaining arenas given the fourth consecutive
  rewire-over-real result.
