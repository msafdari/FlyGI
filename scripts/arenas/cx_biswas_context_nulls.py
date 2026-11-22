#!/usr/bin/env python3
"""H-CX-BISWAS-FITTED -- a NON-DECISIONAL context reading: the fitted
compass recipe on many more degree-preserving rewires.

REGISTERED 2026-11-21, in the compass map amendment
(docs/arenas/compass_map_amendment_20261121.md), BEFORE this script
ran on any rewire it reports.

WHY. The registered null bar of H-CX-BISWAS-FITTED is three rewires
(seeds 4242, 4243, 4244). It stays the bar: the verdict is the
instrument's, scripts/arenas/cx_biswas_killtest.py, and nothing here
can change it. Three is thin for the sentence "its degree-preserving
rewires do not", so this script reads the same recipe on N more.

WHAT IT DOES. For each seed it draws one degree-preserving rewire of
the neuron-level 88-node EPG + Delta7 matrix and runs the instrument's
own run_graph on it (Delta7 units re-derived per rewire, the three
declared A_Delta realizations, the same validity conditions, cluster
cap and G1 test). EPG unit labels are anatomical and stay fixed, as
the registration says. No constant is changed and none is defined
here: everything is imported from the instrument.

SEEDS (declared): 4265 .. 4464, 200 rewires. These are UNSEEN. Seeds
4242-4244 are the registered bar. Seeds 4245-4264 were looked at in
the unregistered check of 2026-11-21 (0 of 20 with a valid fit under
the amended grouping; under the registered grouping one of them, 4257,
had a valid A_Delta=8 fit that failed G1 0 of 8), so they are left out
of this reading and stay reported as unregistered.

READING, pre-stated: reported as "k of n rewires admit a valid fit
at some configuration" and "m of n pass G1 at some configuration",
with the seeds listed, where n is the number of rewires on which the
recipe ran to completion. A rewire on which the recipe RAISES is
listed by seed and left out of n (it is not counted as "no valid
fit"). m > 0 is reported as a stated limit on the
wiring-specificity sentence; it does not change the registered
verdict. k > 0 with m = 0 is reported as is: a fit that does not hold
a bump is a fit that fails the same G1 the real graph must pass.

The seeds are constants of this file, not flags: there is one
declared window and no way to read another into the same output.

Exit codes: 0 = reading complete, 3 = BLOCKED (runtime absent,
composition mismatch, or the instrument's gate failing).

Run:    python scripts/arenas/cx_biswas_context_nulls.py
Output: results/arenas/cx_biswas_context_nulls.amended_map.json (+ .log)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# --- the instrument, imported (nothing below redefines any of it) ------------
_BK_PATH = ROOT / "scripts/arenas/cx_biswas_killtest.py"
_spec = importlib.util.spec_from_file_location("cx_biswas_killtest", _BK_PATH)
bk = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("cx_biswas_killtest", bk)
_spec.loader.exec_module(bk)

CONTEXT_SEED_FIRST = 4265          # declared in the amendment
CONTEXT_SEED_COUNT = 200           # declared in the amendment
OUT_JSON = ROOT / "results/arenas/cx_biswas_context_nulls.json"


def summarize(records: list[dict]) -> dict:
    """Counts over rewire records (pure; unit-tested)."""
    valid_any, pass_any, errors = [], [], []
    per_config = {str(a): {"valid_fit": 0, "pass": 0}
                  for a in bk.A_DELTA_CONFIGS}
    for record in records:
        if record.get("error"):
            errors.append(record["seed"])
            continue
        configs = record["configs"]
        if any(c["valid_fit"] for c in configs.values()):
            valid_any.append(record["seed"])
        if any(c["pass"] for c in configs.values()):
            pass_any.append(record["seed"])
        for a, c in configs.items():
            per_config[str(a)]["valid_fit"] += int(bool(c["valid_fit"]))
            per_config[str(a)]["pass"] += int(bool(c["pass"]))
    return {"n_rewires": len(records), "n_errors": len(errors),
            "n_evaluated": len(records) - len(errors),
            "error_seeds": errors,
            "n_valid_fit_any_config": len(valid_any),
            "valid_fit_seeds": valid_any,
            "n_pass_g1_any_config": len(pass_any),
            "pass_g1_seeds": pass_any,
            "per_config": per_config}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--ring-map", choices=bk.RING_MAPS,
                        default=bk.DEFAULT_RING_MAP)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.output is None:
        args.output = bk.default_output(OUT_JSON, args.ring_map)
    seed_first, count = CONTEXT_SEED_FIRST, CONTEXT_SEED_COUNT

    missing = bk.check_prerequisites()
    if missing:
        print("BLOCKED -- cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        return 3

    args.output.parent.mkdir(parents=True, exist_ok=True)
    handle = open(args.output.with_suffix(".log"), "w")

    def log(message: str) -> None:
        print(message, flush=True)
        handle.write(message + "\n")
        handle.flush()

    started = time.time()
    log(f"ring map: {args.ring_map} -- "
        f"{bk.RING_MAP_DESCRIPTION[args.ring_map]}")
    log(f"NON-DECISIONAL context reading: seeds {seed_first}.."
        f"{seed_first + count - 1} ({count} rewires)")
    gate = bk.validate_gate()
    if not gate["pass"]:
        log("BLOCKED: the instrument's gate fails -- nothing reported")
        return 3

    from flygi.connectome.nulls import degree_preserving_rewire
    from flygi.connectome.subcircuit import extract_subcircuit, select_nodes

    indices = select_nodes(bk.RUNTIME_DIR,
                           type_patterns=("EPG", "PEN_a*", "PEN_b*",
                                          "Delta7", "PEG"))
    sub = extract_subcircuit(bk.RUNTIME_DIR, indices)
    counts = {t: int((sub.types == t).sum()) for t in bk.EXPECTED_COUNTS}
    if counts != bk.EXPECTED_COUNTS:
        log(f"BLOCKED: composition deviates from {bk.EXPECTED_COUNTS}")
        return 3
    types = sub.types.astype("U")
    keep = np.flatnonzero((types == "EPG") | (types == "Delta7"))
    matrix = sub.matrix[np.ix_(keep, keep)].tocsr()
    types = types[keep]
    instances = sub.instances[keep].astype("U")
    epg_all = np.flatnonzero(types == "EPG")
    d7_idx = np.flatnonzero(types == "Delta7")
    units, labelled = [], []
    for i in epg_all:
        unit = bk.epg_unit_from_instance(instances[i], args.ring_map)
        if unit is not None:
            units.append(unit)
            labelled.append(i)
    epg_idx, epg_units = np.asarray(labelled), np.asarray(units)
    sizes = [int((epg_units == k).sum()) for k in range(bk.N_UNITS)]
    log(f"EPG labelled {epg_idx.size}/{epg_all.size}, unit sizes {sizes}")
    if min(sizes) == 0:
        log("BLOCKED: an EPG unit is empty")
        return 3

    records = []
    for k in range(count):
        seed = seed_first + k
        try:
            rewired, _stats = degree_preserving_rewire(matrix, seed=seed)
            full = bk.run_graph(abs(rewired), epg_idx, epg_units, d7_idx)
            record = {"seed": seed, "tie_fraction": full["tie_fraction"],
                      "configs": {
                          str(a): {"valid_fit": bool(c["valid_fit"]),
                                   "pass": bool(c["pass"]),
                                   "r_a": c.get("r_a"),
                                   "g1_n_pass": (c["g1"]["n_pass"]
                                                 if c.get("g1") else None)}
                          for a, c in full["configs"].items()}}
        except Exception as exc:               # reported, never hidden
            record = {"seed": seed, "error": repr(exc)}
            log(f"seed {seed}: ERROR {exc!r}")
        records.append(record)
        if not record.get("error") and any(
                c["valid_fit"] for c in record["configs"].values()):
            log(f"seed {seed}: VALID FIT {record['configs']}")
        if (k + 1) % 25 == 0:
            log(f"  {k + 1}/{count} rewires "
                f"({time.time() - started:.0f}s)")

    summary = summarize(records)
    out = {"hypothesis": "H-CX-BISWAS-FITTED",
           "reading": "NON-DECISIONAL context (amendment 2026-11-21); "
                      "the verdict is the instrument's",
           "ring_map": args.ring_map,
           "epg_unit_sizes": sizes,
           "seed_first": seed_first, "count": count,
           "summary": summary, "rewires": records,
           "elapsed_s": round(time.time() - started, 1)}
    args.output.write_text(json.dumps(out, indent=2, default=float))
    log(json.dumps({"summary": summary, "elapsed_s": out["elapsed_s"]},
                   indent=2))
    log("CONTEXT READING COMPLETE (non-decisional)")
    handle.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
