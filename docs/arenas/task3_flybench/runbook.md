# Task 3 (FlyBench) — MaleCNS runbook (user-executed)

The adapter kill test PASSED in-cloud on the toy (2026-10-01,
H-FLYGI-FLYBENCH-ADAPTER: supported — verify-adapter clean, five core
reflexes at the derived unit bridge, 5/5 across 3 seeds). What the
cloud cannot do is fetch MaleCNS: neuprint.janelia.org is HTTP 000
from the container (AF-2). This runbook is the local half: fetch,
build, and the first characterization rows. Commands were verified
against flybench v0.2.1 (commit 3052ce5) in-container; only the fetch
step itself is untested from here.

SCOPE, stated before any run: these are CHARACTERIZATION rows — our
MODEL FORM (current-based LIF, no delay line, dt 0.5 ms) at the shared
Shiu constants behind their contract. The current adapter does NOT yet
carry our calibrated parameters (per-type taus, graded APL/CT1,
Litwin-Kumar KC thresholds); that is the next registered design (AF-4
included) and the scientific heart of Task 3. No claim and no
submission comes out of this runbook — measured rows only.

## 0. One-time setup (local machine)

```bash
git clone https://github.com/brandoncho369/flybench ~/flybench
cd ~/flybench && pip install -e .
```

Sanity, reproducing the cloud result (from the FlyGI repo root,
branch `claude/admiring-goldberg-wtqkbg`):

```bash
cd <FlyGI repo root>
PYTHONPATH=src:scripts/arenas flybench verify-adapter \
    flygi_flybench_adapter:FlyGIAdapter -c toy        # expect: no defects
PYTHONPATH=src:scripts/arenas flybench run -c toy \
    --simulator flygi_flybench_adapter:FlyGIAdapter --tier core --seeds 3
# expect: 5/5 tasks, graded ~0.99
```

## 1. Fetch + build MaleCNS (~10–20 min, resumable, anonymous)

```bash
flybench fetch-neuprint data-malecns      # male-cns:v1.0, >=5 synapses
flybench build data-malecns --name malecns
flybench fingerprint -c malecns           # record the printed hash
```

Keep `data-malecns/` outside the FlyGI repo tree (no large artifacts
in Git). Note for the record: their build is 176,422 neurons / 6.29 M
edges at >=5 synapses — a DIFFERENT compilation of the same source as
our 166,700 / 24.99 M (AF-1); never compare across them silently.

## 2. The characterization rows (both at their Minecraft-demo config)

Reference first (their own baseline, reproduces their recorded row),
then our adapter, same config, three seeds, rewired control:

```bash
cd <FlyGI repo root>
flybench run -c malecns --config ~/flybench/configs/malecns_minecraft.yaml \
    --seeds 3 --controls rewired \
    --label "reference LIF, gain 0.65" -o results/arenas/malecns_reference.json

PYTHONPATH=src:scripts/arenas flybench run -c malecns \
    --config ~/flybench/configs/malecns_minecraft.yaml \
    --simulator flygi_flybench_adapter:FlyGIAdapter \
    --seeds 3 --controls rewired \
    --label "FlyGI class-2 engine, Shiu constants" \
    -o results/arenas/malecns_flygi.json

flybench diff results/arenas/malecns_reference.json \
    results/arenas/malecns_flygi.json
```

Their README's cost note: a full 31-task run with 3 seeds and the
rewired control is ~18 min on a laptop with `--jobs 6`; the MaleCNS
graph is 45x the toy, so budget accordingly (both runs are resumable
re-runs if interrupted; `--jobs` parallelizes).

Watch for: MaleCNS type names differ from FlyWire's, so some task
selectors match 0 neurons and those tasks SKIP (their design: skipped,
not failed). The skip list in the output is itself data — record it.

## 3. Report back

The two JSONs + the diff output + the fingerprint hash. Claude-side
then: records the rows in the registry (measured tier, scope words
"model form at Shiu constants"), checks our adapter's specificity
against the rewired control (a pass the shuffled brain also makes is
non-diagnostic — their flag, our discipline too), and registers the
calibrated-parameters design (per-type tables + graded units through
AF-4) before any of it is built. Any PR / submission / verified-badge
step is yours and comes only after that design's own kill test.
