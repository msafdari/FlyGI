# Modeling assumptions

MaleCNS supplies anatomy: neuron identities, annotations, predicted
transmitters, and aggregate directed contact counts. FlyGI must supply dynamics,
input injection, state initialization, normalization, transmitter-sign rules,
motor readout, and any learning rule. Those additions are hypotheses, not facts
contained in the connectome.

## Milestone 1 assumptions

- A source row describes influence from a presynaptic body to a postsynaptic
  body; the stored matrix uses `W[post, pre]` so propagation is `W @ activity`.
- MaleCNS body IDs are preserved as `uint64` and separately mapped to dense
  zero-based runtime indices.
- Aggregate synaptic-contact counts are edge weights before a declared
  transform. Duplicate neuron pairs, if present in source input, are aggregated
  deterministically.
- Self-edge policy is explicit. The initial configs reject/drop self-edges and
  require the manifest to record what was observed and retained.
- The full graph is sparse. A dense `N x N` representation is prohibited.
- Missing or changed source columns cause a reported schema error rather than a
  guessed mapping.
- The primary configs declare a non-empty `superclass` retention filter and the
  exact v1.0 `descending_neuron` group label. Both choices appear in the output
  manifest; the code does not silently apply them to other releases.

## Milestone 2 dynamics assumptions

The implemented SciPy/CPU reference backend uses the explicit float32 update

```text
h_next = (1 - leak) * h + leak * tanh(gain * (W @ h) + drive + bias)
```

where `drive` is already projected into graph space. It is held fixed for the
configured number of internal steps. The literal baseline declares `K=4`,
`leak=0.3`, `gain=0.9`, scalar `bias=0`, zero initialization, and a frozen
graph. `K=4` was selected after the full-graph diagnostic found that all 1,314
descending neurons first receive sensory influence at four internal steps.
Leak and gain were assumed, not searched, when this literal baseline was
declared. Gain was later swept: the first sweep ran on unrepresentative input
(uncorrelated random frames) and picked 2.7, recorded as a reversal; the
re-sweep on correlated frames adopted 2.0, and the later league regime is
`gain2.0-modulators` (see `LEAGUE.md` and
`docs/arenas/task1_arc_paper/factsheet.md`). State transitions return a new vector and never mutate the caller's
state, input, or graph. A deterministic nonzero initialization exists only as
an explicit seeded diagnostic; it is not the literal-agent initialization.

The `tanh` and convex leak keep a state initialized in `[-1, 1]` bounded absent
non-finite arithmetic, but the repository still executes and records an actual
10,000-step full-graph stability gate. SciPy CPU repeatability is tested
bit-for-bit on the same backend. No GPU backend is currently claimed.

The heuristic signed graph mode treats transmitter identity as an approximation
to connection sign; receptor and cell context can reverse or modulate effects.
Uncertain modulators remain configurable and are not silently relabeled
excitatory. Both `graph.modulator_treatment` and
`graph.unknown_transmitter_treatment` are declared explicitly in every checked-in
config rather than defaulted, because they change which edges exist.

A treatment of `zero` assigns sign 0 to the affected presynaptic neurons, which
deletes **all** of their outgoing edges. `configs/literal_rate_signed.yaml`
therefore compiles a graph with fewer edges than
`configs/literal_rate.yaml`, and the two are not edge-count-matched. Each signed
condition requires null graphs generated from the signed graph itself. The
manifest records the transmitter counts, both treatments, and
`edges_zeroed_by_sign_or_normalization` so the difference is measured rather
than assumed.

## Implemented interface choices

The neutral encoder uses a fixed seeded sparse projection shared across the real
graph and its controls. It maps the declared ARC feature vector into the chosen
sensory population; this is an experimental interface, not a unique biological
interpretation.

Descending-neuron readout is the primary interpretable condition. Whole-state
readout is an access-rich ablation and must be reported separately. Legal-action
masking is part of the ARC interface, not evidence of graph intelligence.

The literal decoder has no trainable parameters. It z-scores legal action
logits before categorical sampling and uses the same policy-owned, recorded
NumPy RNG for actions and factorized `ACTION6` coordinates. A score-blind
three-point calibration froze action temperature 0.15 and coordinate
temperature 0.20. Changed cells supply a novelty-centroid click; after an
unchanged click, the policy samples a not-yet-clicked grid cell. MEASURED
defect: the deterministic novelty-centroid branch explores 3.29x less than
uniform random clicking in the six click-only games (72 vs 236 mean unique
observations); switching the centroid off recovered coverage roughly
fourteen-fold (r11l 96 -> 1,383 cells), and later arms ran without it (the
`nocentroid` rows in `LEAGUE.md`; "COORDINATE-HEAD defect" in
`docs/arenas/task1_arc_paper/factsheet.md`). These rules are
fixed across the real graph, nulls, and the matched bypass.

Persistent recurrent state is preserved across ordinary actions, levels, and a
protocol-required game-over reset, with reset on a new environment. Alternative
reset schedules remain ablations.

## Explicit nonclaims

FlyGI is not a biophysical brain simulation. It omits morphology, compartmental
electrophysiology, neuromodulatory state, receptor distributions, development,
the body, and the natural sensory environment. Its results concern the chosen
graph, interface, and dynamics only.
