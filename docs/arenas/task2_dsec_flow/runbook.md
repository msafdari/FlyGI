# Task 2 (DSEC-Flow) — kill-test runbook (user-executed)

The kill test cannot run in the cloud container: dsec.ifi.uzh.ch,
download.ifi.uzh.ch and drive.google.com all returned HTTP 000 (measured
2026-10-01), and the container has no compiled MaleCNS runtime and no
fc25 results file. Everything below runs on the local machine, where all
three live. The design and the pass/kill rule are frozen in
`killtest_design.md`; nothing in this runbook is a knob.

## 0. Preconditions (one-time check)

On the local machine, from the repo root on branch
`claude/admiring-goldberg-wtqkbg`:

```bash
python scripts/arenas/dsec_killtest.py          # no --data-root yet
```

It must report BLOCKED with exactly ONE missing line — the `--data-root`
one. If it lists anything else (runtime, annotations, fc25 results,
h5py/hdf5plugin/pyarrow/scipy), fix that first; `pip install h5py
hdf5plugin` are the only dependencies the earlier benchmarks did not
already need. hdf5plugin is REQUIRED, not optional: DSEC compresses
event arrays with Blosc (HDF5 filter 32001), which plain h5py cannot
decompress (measured 2026-10-02 on the first local run). The metrics
module is self-contained (numpy + stdlib):

```bash
python scripts/arenas/dsec_metrics.py --selftest    # expect 6/6
python -m pytest tests/test_dsec_metrics.py tests/test_dsec_killtest.py -q
```

## 1. Download ONE training sequence (~4 GB total)

From the DSEC download page (https://dsec.ifi.uzh.ch -> Datasets ->
Download; the cloud container could not reach it, so exact file names
are unverified from here — SOURCED, not measured):

1. The optical-flow ground truth for one TRAIN sequence with forward
   flow — primary choice `thun_00_a` (any train sequence with forward
   GT works; the harness logs which it used).
2. That same sequence's LEFT event camera data (`events_left`),
   including the rectify map.

Arrange (or symlink) into the layout the harness expects:

```
<DSEC_ROOT>/thun_00_a/flow/forward/*.png          # 16-bit GT flow PNGs
<DSEC_ROOT>/thun_00_a/flow/forward_timestamps.txt # from_us, to_us rows
<DSEC_ROOT>/thun_00_a/events/left/events.h5
<DSEC_ROOT>/thun_00_a/events/left/rectify_map.h5  # optional but wanted
```

Keep the data OUTSIDE the repo tree (AGENTS.md: no large artifacts in
Git; `results/*` is already gitignored).

MVSEC fallback (only if DSEC is unreachable everywhere): download
indoor_flying1 and convert it into the same layout (events to an
`events/{x,y,p,t}` HDF5, GT flow to KITTI-encoded PNGs via
`dsec_metrics.write_flow_png`, a two-column microsecond timestamps
file). Say so and the conversion script becomes a Claude-side task;
don't hand-roll it silently.

## 2. Run the kill test (the one command)

```bash
python scripts/arenas/dsec_killtest.py --data-root <DSEC_ROOT>
```

Single process (the standing resource rule). Expected cost: five
simulated arms x (4 calibration dts x ~50 windows + ~200 eval windows)
of a ~2.5k-node sparse model — minutes to low tens of minutes on the
machine that ran fc25, not hours. Output:

- `results/arenas/dsec_killtest.json` — the verdict and every number.
- `results/arenas/dsec_killtest.log` — the console mirror.

## 3. Read the verdict (no interpretation needed — it is frozen)

`verdict` in the JSON is one of:

- **PASS** — real beat BOTH the event-centroid comparator and the
  degree-preserving rewire (p < 0.05 paired sign tests, lower medians).
  Next steps (each still gated, nothing automatic): AD-4 dense-decoder
  registration, then the benchmark-account decisions (AD-1
  institutional email, AD-2 six-month report rule) — yours.
- **KILL** — a bar failed. The task is COMPLETE with a recorded
  class-2.5 limit; no dense pipeline, no benchmark entry. This is the
  base-rate outcome (0 for 12) and the ARC precedent's direction.
- **BLOCKED** — fewer than 30 usable evaluation windows; an
  instrument/data problem, not a verdict. Report it back as such.

## 4. Report back

Paste or commit-say the JSON (it is small; `results/` stays
gitignored — do not force-add it). The Claude-side closeout then
updates EXPERIMENTS.yaml (H-T4T5-DSEC-DIRECTION open -> supported /
refuted), ASSUMPTIONS.md AD-3..AD-8, and WORKLOG.md from those numbers,
and Task 2 closes per the program's operating rule 3 (a failed kill
test is a completed task, not an abandoned one).
