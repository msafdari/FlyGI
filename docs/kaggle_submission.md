# Kaggle submission workflow

This document describes the deployment contract. It is not evidence that this
checkout has produced or submitted `submission.parquet`.

## Local preparation

First validate the official ARC-AGI-3-compatible random agent and local plumbing:

```bash
make verify-local
python scripts/smoke_test.py
```

The complete current progression is:

```text
verify evaluator -> calibrate without score -> run frozen full gate ->
stage dataset -> run private notebook -> submit one notebook version
```

Inspect the generated artifact rather than treating a successful process exit
as proof of a valid competition submission. Competition rules, package images,
actions, and deadlines can change; recheck the official ARC Prize documentation
and Kaggle competition immediately before packaging.

## FlyGI adapter contract

The competition adapter owns the framework-specific `MyAgent` class. In
the current implementation it loads and hash-verifies the packaged graph and
config once per process, then delegates frame encoding, sparse propagation,
readout, legal-action masking, seeded action sampling, and coordinate generation
to the core package. Core `flygi` modules do not import Kaggle-specific code.

Missing or invalid connectome assets fail closed. The random-legal fallback is
available only through an explicit local smoke-test opt-in, and competition
reruns ignore that opt-in. An ordinary private notebook run performs a no-game
preflight and prints a machine-readable `FLYGI_PREFLIGHT=` JSON line containing
the verified runtime identity.

## Offline package requirements

The evaluation notebook runs without internet. The staged private dataset
therefore includes the compiled graph, group indices, compact node metadata,
configuration, and complete manifest hashes. Repository-owned Python is embedded
in the generated notebook as a deterministic source zip; dependency wheels come
from the competition input.

It must not include or download the 1.1 GB source Feather table at evaluation
time, call neuPrint, or rebuild the graph in the notebook. Assets are loaded
once, not per action. Missing files or hash mismatches must fail clearly before
gameplay.

The adapter exposes:

```python
class MyAgent(Agent):
    def is_done(self, frames, latest_frame) -> bool: ...
    def choose_action(self, frames, latest_frame) -> GameAction: ...
```

Build the offline artifacts with:

```bash
uv run python scripts/package_kaggle_dataset.py
make notebook
```

The staged dataset and generated notebook are ignored by Git. Publishing the
private dataset, pushing the private notebook, and spending a competition
submission are separate outward-facing actions. The ordinary notebook log must
show the signed 166,700-node, 24,559,055-edge, `K=4` runtime before the selected
notebook version is submitted.
