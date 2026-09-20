# Data provenance

## Canonical sources

FlyGI targets `male-cns:v1.0`, released 2026-06-08. The corresponding Cell
paper was published 2026-09-03. The canonical project pages are:

- [project](https://male-cns.janelia.org/)
- [downloads and API examples](https://male-cns.janelia.org/download/)
- [release notes](https://male-cns.janelia.org/release/)
- [paper DOI](https://doi.org/10.1016/j.cell.2026.08.015)

The three source URLs used by Milestone 1 are declared in the YAML configs. See
[`data/README.md`](../data/README.md) for attribution and the CC BY 4.0 notice.

## Fail-closed ingestion

Source schemas are external facts, not assumptions. The ingestion code must
inspect actual Arrow schemas, validate required semantic fields, and stop with
a useful error if a column is absent, ambiguous, or incompatible. It must not
guess a replacement column. Body IDs must round-trip exactly as 64-bit values.

The checked-in MaleCNS v1.0 configs explicitly retain rows whose `superclass`
is non-null/non-empty and define the descending readout group with the observed
value `superclass: descending_neuron`. These names and values were checked
against the official v1.0 annotation table on 2026-09-19. They remain model
configuration, not universal aliases: an upstream schema or label change must
fail validation. The builder measures and records resulting counts on every
real build instead of treating a literature or community count as acceptance
data.

The graph convention is:

```text
W[post_index, pre_index] = influence from presynaptic neuron to postsynaptic neuron
activity_next = W @ activity
```

A three-node `A -> B -> C` fixture must validate this orientation. Production
construction uses sparse COO/CSR arrays and must never allocate a dense
connectome-sized adjacency matrix.

## Derived assets

A runtime graph contains CSR-like `indptr`, `indices`, and `weights` arrays;
`uint64` node IDs; the reverse body-index mapping; compact metadata; declared
group indices; and a machine-readable manifest. Edge transforms and
normalization are configuration inputs, not undocumented cleanup.

Self-edge handling, missing annotations, disconnected nodes, unknown
transmitters, and modulators must be counted and reported. Heuristic transmitter
signs are a model choice, not a measured postsynaptic effect.

## Manifest completeness

The required manifest fields are listed in
[`data/manifests/README.md`](../data/manifests/README.md). A manifest is complete
only when its source and output hashes and measured statistics come from a real
build. A template, approximate literature value, cloud object identifier, or
null field must never be represented as an observed SHA-256 or graph count.

## Milestone 0-1 status boundary

The repository provides the ingestion contract, configuration, sparse build
path, and fixture-level validation. It does not check a generated full-data
manifest into Git and therefore does not claim that the large source files have
been downloaded or that any commonly quoted node/edge totals were reproduced
on this checkout.
