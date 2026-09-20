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

## Declared later-model choices

The checked-in rate configs declare a leaky tanh network, but full-graph
dynamics are Milestone 2 work. The heuristic signed mode treats transmitter
identity as an approximation to connection sign; receptor and cell context can
reverse or modulate effects. Uncertain modulators remain configurable and are
not silently relabeled excitatory.

The neutral encoder will use a fixed seeded sparse projection shared across the
real graph and all nulls. The bio-oriented encoder necessarily imposes a mapping
from a rectangular 16-value ARC grid to fly visual populations. Neither is a
unique biological interpretation.

Descending-neuron readout is the primary interpretable condition. Whole-state
readout is an access-rich ablation and must be reported separately. Legal-action
masking is part of the ARC interface, not evidence of graph intelligence.

Persistent recurrent state is planned across ordinary actions and levels, with
reset on a new environment. The alternative reset schedules are ablations.

## Explicit nonclaims

FlyGI is not a biophysical brain simulation. It omits morphology, compartmental
electrophysiology, neuromodulatory state, receptor distributions, development,
the body, and the natural sensory environment. Its results concern the chosen
graph, interface, and dynamics only.
