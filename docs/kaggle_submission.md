# Kaggle submission workflow

This document describes the deployment contract. It is not evidence that this
checkout has produced or submitted `submission.parquet`.

## Milestone 0

First validate the official ARC-AGI-3-compatible random agent and local plumbing:

```bash
make verify-local
python scripts/smoke_test.py
```

Where the starter workflow is available, its intended progression is:

```text
edit agent -> play locally -> verify locally -> build notebook -> submit
```

Inspect the generated artifact rather than treating a successful process exit
as proof of a valid competition submission. Competition rules, package images,
actions, and deadlines can change; recheck the official ARC Prize documentation
and Kaggle competition immediately before packaging.

## FlyGI adapter contract

The competition adapter owns the framework-specific `MyAgent` class. In
Milestone 0 it delegates deterministic random-legal action selection to the core
package. The eventual FlyGI adapter will load the packaged graph and config once,
then delegate frame encoding, sparse propagation, readout, legal-action masking,
and coordinate generation. Core `flygi` modules do not import Kaggle-specific
code.

## Offline package requirements

The evaluation notebook runs without internet. A later full-agent package must
therefore include the compiled graph, group indices and compact metadata,
configuration, complete manifests and hashes, optional trained readout weights,
and any dependency wheels unavailable in the image.

It must not include or download the 1.1 GB source Feather table at evaluation
time, call neuPrint, or rebuild the graph in the notebook. Assets are loaded
once, not per action. Missing files or hash mismatches must fail clearly before
gameplay.

The expected eventual adapter exposes:

```python
class MyAgent(Agent):
    def is_done(self, frames, latest_frame) -> bool: ...
    def choose_action(self, frames, latest_frame) -> GameAction: ...
```

Milestones 0-1 validate only the random-agent path and connectome ingestion.
Packaging the complete FlyGI policy, control graphs, and trained heads is later
work.
