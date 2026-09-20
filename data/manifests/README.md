# Provenance manifests

This directory is reserved for small, reviewable provenance records. Generated
graph assets belong under ignored `data/processed/` paths; a copy of a completed
manifest may be promoted here only after its hashes and measured values have
been independently reviewed.

A completed manifest must include:

- source URLs, MaleCNS release, UTC download timestamp, and SHA-256 for every
  source file;
- every input dataframe's column names and dtypes;
- counts of annotated and retained neurons, aggregated directed edges,
  self-edges, disconnected nodes, unknown transmitters, and missing annotations;
- the measured sum of synaptic-contact weights;
- exact preprocessing, signing, self-edge, transform, and normalization options;
- Python, FlyGI, and dependency versions; and
- hashes of every generated runtime asset.

There is deliberately no example JSON containing invented digests or counts.
The graph builder is responsible for writing the machine-readable record from
observations made during a real build.
