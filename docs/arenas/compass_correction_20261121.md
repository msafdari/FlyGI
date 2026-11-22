# Correction to the compass results (2026-11-21)

This corrects the compass results in the locked paper
([doi:10.34740/kaggle/w/116268](https://doi.org/10.34740/kaggle/w/116268)).
The ARC results do not change: the leaderboard agents did not use the
compass. It is a draft kept in the repository; where it is posted is the
author's decision.

## What was wrong

Every compass instrument placed each EPG neuron on the ellipsoid-body ring
from its protocerebral-bridge label, and the rule it used put left
glomerulus k beside right glomerulus k. In the fly the two bridge halves
run round the ring in opposite directions, so left k lies between right
9 minus k and right 10 minus k (ESTABLISHED: Hulse et al. 2021; Wolff,
Iyer and Rubin 2015). The rule reflected the left half of the ring. The
eight-unit version used by the fitted compass, which pooled left k with
right k, was wrong for the same reason. MEASURED: 18.7% of the direct
EPG-to-EPG synapse count between different ring positions joins ring
neighbours under the old rule, close to random labelings (mean 13.3%),
against 81.7% under the corrected one.

The corrected eight-unit grouping pools left k with right 9 minus k. It
was found on 2026-11-21, while fact-checking a draft email to the authors
of the fitted-compass recipe, through its agreement with their published
values. It was adopted on a different piece of evidence that uses no
fitted value: a cell-by-cell match of our counts to the EPG block of their
Fig. 1g, which only this grouping reproduces among 960 candidate orderings.
How it was found is disclosed in full in
[the amendment](compass_map_amendment_20261121.md), section 9.

## What was done

The correction was written as a dated amendment, reviewed in seven rounds
by subagents of the session that wrote it (no one outside that session has
reviewed it), and frozen in git (tag `compass-map-freeze-20261121`) before
any compass instrument was run under it. Every bar, threshold, null, seed
and protocol stayed as registered; only the label-to-ring map changed,
apart from one status rule for the one-bit scratchpad test (not decisive
here) and a rule narrowing statements to what their bars measure. The ten
registered compass runs were then made once each, in the registered order,
through a wrapper that refused any change to the frozen files, and one new
non-decisional reading was added. The reading of every possible outcome
had been written down before the runs. Each run's record is hashed in the
[worklog](../../WORKLOG.md) and copied to
`results/manifests/compass_amended_20261121/`.

## What changed and what did not (MEASURED unless marked, 2026-11-21)

No status word changed.

- **Ring structure.** Still passes, by a wider margin (p at the 1/201
  floor both times). Ring bandedness is 0.8505 against a maximum of 0.3342
  over 200 degree-preserving rewires (the paper reported 0.5881 against
  0.3376 on the reflected ring). The second structural bar also passes (0
  of 200 rewires at or above the real value). The left and right PEN_a
  halves now lean in opposite directions, but the corrected geometry alone
  could produce that (inferred, from the map's tile geometry), so the
  registry no longer describes it as a shifter. The bandedness bar had been
  seen before the freeze; the second bar had not.
- **The three earlier model classes.** All three fail again. Class 1: no
  grid point holds a localized bump in darkness. Class 2: no calibration
  pass in 210 configurations; 157 were active and none was localized (the
  paper's circuit figure says "All 155 active class-2 configurations
  spread out", from the original run). Class 3, at spiking fidelity (the
  standalone 148-neuron circuit under the declared count mapping and
  grid): at best 5 of 8 writes ended within the registered 45 degrees of
  their starting heading (the bar is 6; the original run reached 2 of 8),
  none of them kept its own position, and steering was never
  opposite-signed. The circuit figure's class-3 sentence ("the peak
  survived but drifted toward one region") described the original run and
  is withdrawn: at the grid point with the most passes, the bumps settled
  at several points (about 104, 152, 180, 185 and 262 degrees). The
  separate heading-latent test is again blocked at its persistence
  precheck.
- **The fitted compass.** Passes again: two of three configurations hold
  an initialized heading at all eight rotations, and the three registered
  degree-preserving rewires admit no valid fit. **One sentence of the
  paper's text is withdrawn, and the two statements in its circuit figure
  above are replaced.** The sentence said the fitted shape parameters
  differed from the authors' values (the paper's run gave 0.4221 and
  0.2132). Under the corrected grouping, at the two configurations with a
  valid fit, they agree to print precision (0.5480 and 0.4373 against the
  published 0.548 and 0.437); the third published value (0.391, at
  A_Delta 4) still has no valid fit under the registered validity
  condition. The earlier difference came from this project's grouping.
  The agreement is not independent evidence, because the grouping was
  first noticed through it, and the model is not a reproduction of the
  authors' numeric realization.
- **A new limit on the fitted compass.** A non-decisional reading run with
  the correction fitted the same recipe to 200 further rewires: 25
  admitted a valid fit and 2 also held the heading at all eight rotations,
  both at A_Delta 6, a configuration at which the real counts also pass.
  "No valid fit on the rewires" holds for the three registered rewires,
  not for rewires in general.
- **The one-bit scratchpad test.** Its status was already refuted, by a
  structural rule; its own registered kill condition now fires too (visual
  readback at chance, 0.5; it was 0.85).

The project's record of score predictions is unchanged, at 0 for 16.

## Where to check

- The amendment, with every pre-stated reading:
  [docs/arenas/compass_map_amendment_20261121.md](compass_map_amendment_20261121.md)
- The registry entries, each with a dated bullet: [EXPERIMENTS.yaml](../../EXPERIMENTS.yaml)
  (H-CX-RING-TOPOLOGY, H-CX-BISWAS-FITTED, H-CX-CLASS3-COMPASS,
  H-MODULE-VERDICT and others)
- The run records and their hashes: [WORKLOG.md](../../WORKLOG.md), entry
  "Compass amended runs, one at a time against the freeze"
