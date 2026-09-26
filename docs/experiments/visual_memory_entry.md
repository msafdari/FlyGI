# Visual memory entry gate

Protocol `visual-memory-entry-v1`, 2026-09-26. Status: frozen after pre-outcome
review. Hypothesis `H-VISUAL-MEMORY-ENTRY`. No neural response has been inspected.

## Question and decision

Can the fixed MaleCNS rate model express horizontal-versus-vertical identity
across a change of position in its anatomically annotated visual KC population,
beyond information already available in its sensory interface?

This is a cheap necessary-condition test for the proposed position-tolerant
visual associative-memory branch. It is not an ARC score, a test of learning,
abstract matching, a living fly, or exact-topology superiority. A failure stops
this model/interface branch before plasticity is built. A pass earns only an
anatomy-specific control experiment, which must pass before memory or ARC work.
The older olfactory Experiment 000 draft remains separate.

## Scientific basis and assumptions

Established: visual input reaches KCg-d directly and via local visual
interneurons. Upstream VPN->LVIN connections are structured, whereas individual
KC input combinations are consistent with biased random sampling in FlyWire.
Position tolerance is a proposed consequence of the upstream convergence,
not an established property of this simulator.
[Ganguly et al. 2024](https://www.nature.com/articles/s41467-024-49616-z).

Measured in the pinned MaleCNS annotations: exact `class == "Kenyon_Cell"`
and `type == "KCg-d"` selects 206 neurons, 99 L and 107 R. All 206 are read,
including cells without a direct visual input. The larger direct-VP-recipient
pool mixes KC types and is not the primary population.

Assumptions (also required beside implementation):

- A1: the existing affine 64x64-to-eye mapping and declared ON/OFF assignments
  deliver a useful monochrome signal. ARC colors are not treated as luminance:
  this synthetic assay explicitly defines 0=dark and 15=bright. These stimuli
  say nothing about categorical ARC colors.
- A2: uniform float32 leaky-tanh dynamics at gain 2, leak .3 and 32 steps expose
  useful visual activity. These are fixed model parameters, not physiology;
  the assay does not claim convergence or assign seconds to steps.
- A3: the positive part of KC state is the candidate firing representation.
  Negative state remains reported as a model diagnostic, not eligible activity.
- A4: normalized Euclidean nearest-exemplar scoring is an external diagnostic
  of accessible information. It is not a fly computation or deployable decoder.
- A5: the numerical floor and promotion bars below are engineering choices.
  A failure is scoped to this panel, interface, readout and operating point.

Expected: no ARC gain is forecast; the recorded score-prediction base rate is
at least twelve failed bridges. No post-result tuning is authorized.

## Frozen inputs and runtime

Runtime: `data/processed/male-cns-v1.0/literal-rate-signed-modulators`.
Require the normal loader's manifest verification and these SHA-256 values:

| File | SHA-256 |
| --- | --- |
| graph.npz | f5553b59d4efaab36600cee5c319d524e3023b27906642720c634f3a000babb9 |
| node_metadata.npz | 2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c |
| retinotopy.npz | ebc2b699e541330097a257003c2346f367d4beda1f04e88b2aaa1e1542db1a8d |
| raw annotations | 2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2 |

Require 166,700 nodes, 24,994,595 edges, `W[post,pre]`, and exact agreement
between raw annotations and runtime body ordering for the KC selector.

Panel: centers `(row,column)` in lexicographic Cartesian product
`[20,28,36,44] x [20,28,36,44]`. At each center present two separate images:
horizontal rectangle `grid[row-1:row+2, col-4:col+5] = 15`; vertical rectangle
`grid[row-4:row+5, col-1:col+2] = 15`. Other cells are zero. Exactly 27 bright
pixels, 32 unique images, one shape pair, 16 locations.

Use existing `RetinotopicProjection`, default ON/OFF/change type sets,
`input_scale=1`, `change_gain=0`. The feature vector is zero: no Python temporal
difference, action, or legal mask is supplied. Verify every drive is finite,
nonzero, unique, and zero outside the 23,720 annotated sensory indices. Sensory
and KC sets must be disjoint. Record signed drive sums/L1 norms and type means.

Pre-outcome static audit: the wider proposed panel `[14,26,38,50]^2` contained
two invisible positions. It was replaced before protocol freeze or any neural
run by the central panel above. All central drives reach 178-325 neurons.
Orientation-dependent input mass remains and motivates the type-mean control.

Native condition: for each scene start all 166,700 states at exact zero; apply
the same drive for 32 synchronous updates using the existing `ScipyRateNetwork`:
`h <- .7*h + .3*tanh(2*W*h + u)` in its established float32 operation order.
Exactly 32 individual updates are performed, not 32 configured multi-step calls.
Bias is zero. Record readouts and full-state diagnostic summaries at steps
4, 8, 16, 32; only step 32 determines the gate. No plasticity or activity carries
between scenes. Repeat the first scene from zero at the end as a reset golden.

Graph-off condition: same live real matrix, drive, steps, and parameters except
gain=0. Its KC state must be exactly zero and score exactly .5. It is a
disconnection check, not an interface-matched anatomy-null competitor.

## Trivial alternatives and evaluation

Compute the identical diagnostic for:

1. Native positive KC state at step 32.
2. Positive encoded drive restricted to sensory indices (identity/plumbing floor).
3. Fifteen per-type mean signed sensory drives, sorted by type name (a
   geometry-free input-mass/channel baseline).
4. Graph-off KC state (constant/chance .5).

Apply `max(vector,0)` to every representation including both input baselines;
keep the unrectified vectors as diagnostics only. Convert each vector to float64,
divide by its L2 norm when nonzero, otherwise
retain zero. For all 16 target positions `j`, all 15 different exemplar positions
`i`, and each target shape `s`, compare squared Euclidean distance from
`representation[j,s]` to `representation[i,s]` and `representation[i,1-s]`.
If wrong-distance minus correct-distance is >1e-12 score 1, <-1e-12 score 0,
otherwise .5. Average the 30 decisions within target position, then the 16
position means. Retain all 480 margins/decisions in the artifact. No classifier,
fit, training set selection, or reward enters the neural runs.

Conjunctive descriptive gate:

- native accuracy >= .75;
- native accuracy >= each of the two plumbing baselines + .10;
- at least 12/16 native target-position means strictly > .5;
- every native positive KC vector has RMS > 1e-7, and every same-position
  horizontal/vertical pair has RMS difference > 1e-7 before normalization.

The numerical-floor clauses are scientific/model failures, not invalid runs.
Equal means, hemispheres, 480 decisions, and repeated execution do not increase
the number of independent shape pairs or biological specimens. Report no
p-value or population-generalization confidence interval for this developmental
panel. No claims about arbitrary shape recognition are permitted.

## Validation, evidence, and stopping

Before outcomes, test: exact stimulus bounds/area/order; synthetic perfect
shape code=1; constant and location-only codes=.5; graph/input disjointness;
reset identity; score invariance to positive per-vector scaling; invalid
dimensions/nonfinite rejection; each gate independently fails when violated.
Independent review must verify that the protocol and implementation agree.

One command, after checkpointing source and protocol:

```bash
FLYGI_SPMV_THREADS=6 .venv/bin/python scripts/probe_visual_memory_entry.py \
  --output results/connectome_agent/visual_memory_entry_v1.json
```

The result refuses overwrite and records source/protocol/registry/data hashes,
Git status, software versions, timing, selector IDs, stimulus/drive hashes,
raw readouts, diagnostic traces, complete scores, checks, and verdict. Invalid
contracts yield `invalid` with no scientific verdict; a complete comparison
yields `pass` or `fail`. Serialize finite JSON atomically; append progress
telemetry so interruption is diagnosable. Generated data stays ignored.

On failure stop this branch without changing gains, timing, readout, panel,
normalization, or threshold. On pass, freeze a local anatomy-control experiment
from structural evidence before running it: representation success alone cannot
justify plasticity or ARC integration. Its design must control shortcuts around
KCs and preserve the specific pathway under test. Do not substitute the known
weak global null or the 30.5%-switchable local MBON null for this requirement.
