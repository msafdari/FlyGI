# Task 3 — calibrated-parameters design (the scientific heart)

Registered 2026-10-02, BEFORE any build, from the first measured MaleCNS
rows (WORKLOG same date). Per the program rules: trivial alternative
named, bars frozen, a failed kill test is a recorded verdict.

## What the first rows established (measured, the baseline)

On the unpinned MaleCNS build (AF-7), malecns_minecraft config, 3 seeds,
rewired control:

| arm | core | hard | graded | specificity vs rewired |
|---|---|---|---|---|
| reference LIF g0.65 | 0.5667 | 0.5366 | 0.639 | +0.184 |
| FlyGI class-2 engine, Shiu constants | 1.000 | 0.6044 | 0.711 | +0.282 |

And the decomposition that matters (AF-8, the user's analysis): our net
win is built on SUPPRESSION checks a globally quieter engine wins
cheaply (reference saturates 292 Hz -> 0), while our one big loss is an
ACTIVATION check (water response 95.8 -> 0 Hz). So the uniform-constants
engine's headline number flatters it. The discriminating question is
whether BIOLOGICAL calibration — the ingredients our class-2 program
validated on our own substrate — buys back activation without
surrendering suppression or specificity.

## Premise under test

Layering our class-2 calibration ingredients onto the adapter as
declared per-type parameter tables improves the ACTIVATION-check subset
over the measured Shiu-uniform baseline, while keeping the overall
graded score and the wiring-specificity edge. The ingredients, each at
its tier:

1. **Per-type membrane time constants** — fast/slow CLASS assignments
   ESTABLISHED (Arenz 2017; Behnia 2014; Borst 2025; the fc2 table);
   specific millisecond values ASSUMED, taken verbatim from
   scripts/benchmarks/fc2_visual_ds.py's table (no new sweeping).
   Resolution is by MaleCNS type name via the engine's ParameterTable
   patterns; their build uses the same male-cns:v1.0 annotations, so
   names should match — coverage (fraction of neurons resolved to a
   non-default row) is MEASURED and reported, and a near-zero coverage
   is a BLOCKED outcome, not a verdict.
2. **Graded (non-spiking) units** — APL and CT1, ESTABLISHED
   non-spiking interneurons; graded in our engine. AF-4's structural
   resolution applies: graded units are internal (no spikes emitted);
   if any task's READOUT resolves to a graded population, that task is
   recorded and the unit reverts to spiking for that run (contract over
   physiology, declared).
3. **KC thresholds, Litwin-Kumar-style calibration** — the one FITTED
   piece. Calibrated at adapter construction on a DECLARED NON-TASK
   protocol: seeded random PN-subset drives (fixed count and seed,
   never a benchmark stimulus), per-KC thresholds set to a
   literature-pinned sparseness target (0.05-0.10 band midpoint). This
   respects their no-fitting-on-tasks rule (AF-3) by construction.

Draft open-division declaration (finalized at submission time, if any):
`n_free_parameters: 2` (global gain, inherited from the baseline row;
KC sparseness target, literature-pinned); `fit_data`: "KC thresholds
calibrated to a published sparseness band on seeded random PN drives;
per-type time constants are literature class assignments; nothing
fitted on any benchmark task."

## Trivial alternative (named)

The measured Shiu-uniform row above — OUR OWN baseline, not the
reference. If biological calibration cannot beat uniform constants on
the set where uniform constants measurably underperform, the honest
statement is that flybench's tasks (like ARC before them) do not need
what the calibration adds, and the row stands as uniform.

## Frozen bars (evaluated on the same unpinned build, same config,
3 seeds, rewired control; activation/suppression split defined
MECHANICALLY from the task YAML before any calibrated run: an
activation check requires a rate/count/spikes-per-neuron measurement to
EXCEED a threshold; ratio and below-threshold checks are suppression)

PASS iff ALL THREE:

1. Mean graded score over SHARED activation checks: calibrated >=
   uniform + 0.02 (declared minimum effect).
2. Overall graded: calibrated >= 0.701 (uniform 0.711 minus a 0.01
   noise allowance — the suppression wins must not be given back).
3. Specificity vs rewired: calibrated >= +0.252 (uniform +0.282 minus
   0.03).

KILL if any bar fails: recorded verdict that uniform constants are not
improved by this calibration set on these tasks, the uniform row stands
as Task 3's measured contribution, and any submission/PR decision (the
user's) proceeds from that row. BLOCKED (not a verdict) if type-name
coverage is near zero (ingredient 1) or the KC calibration cannot reach
the sparseness band on the non-task protocol.

Secondary endpoints, reported not scored: the water-response check
specifically; the suppression subset; per-task deltas; spike-count
economy (their cost column). Expected tier, base rate stated: 0 for 12
on expected-to-help; the nearest precedents split (temporal
heterogeneity added nothing on ARC motion; the LK calibration DID carry
the class-2 MB sparseness pass on our substrate).

## Execution split

Cloud-side: implement the calibrated table + calibration hook in
scripts/arenas/flygi_flybench_adapter.py (engine stays UNMODIFIED; the
adapter composes it), toy regression, unit tests for the
split-derivation and calibration plumbing. Local (user): the one
measurement command, mirroring the characterization runs.

AMENDED 2026-10-03, at build time and before any MaleCNS run of this
class: the registration assumed the toy would resolve no fly types, so
byte-identity was named as the toy regression bar. MEASURED at build:
the toy DOES carry KC (400), APL (2) and even fc2 tau-table type names
(192 cells) by construction — task 26 runs on the toy. The toy bar is
therefore amended to a CALIBRATION-EXERCISE check: verify-adapter clean
on the calibrated class; the full toy suite completes with calibration,
graded units and the silenced-reuse path engaged; the achieved
calibration sparseness hits the target. Byte-identity remains the bar
for the UNIFORM class only. The three frozen MaleCNS bars are untouched
by this amendment. (Toy exercise result, context only: score 0.91 /
graded 0.93 / 22 of 30 vs the uniform class's 0.90 / 0.92 / 21.)

Registration: EXPERIMENTS.yaml `H-FLYGI-FLYBENCH-CALIBRATED` (same
commit). The flagged bootstrap-CI transcription oddity from the first
rows (point estimate outside the reported interval) must be re-checked
before any of these numbers appear in outward text. (RESOLVED 2026-10-03,
re-checked: the point estimate is real; the CI covers a different
estimator — a flybench diff-tool inconsistency, not a transcription error
and not a problem with these rows. See the WORKLOG 2026-10-03 entry.)
