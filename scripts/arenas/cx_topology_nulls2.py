#!/usr/bin/env python3
"""H-STAGEA-NULL-DECOMPOSITION -- the second null family applied to
Stage A (Task 10, item 7).

PREREGISTRATION (EXPERIMENTS.yaml H-STAGEA-NULL-DECOMPOSITION and
docs/arenas/task10_menu/killtest_design.md section 7, frozen 2026-10-23
BEFORE this file existed, jointly with the other Task-10 items;
restated, not changed):

  - REFINEMENT, NEVER A REOPENING: the degree-preserving rewire
    destroys edge placement and magnitude assignment simultaneously.
    This instrument re-runs the Stage-A statistics (bandedness,
    PEN_a mirror-peak) on the SAME 148-neuron CX subcircuit under two
    further null families that hold topology fixed:
      weight family -- |w| permuted over existing edges
        (within-presynaptic-column PRIMARY, AC-N1; global variant
        also reported), per-edge signs fixed;
      sign family -- per-presynaptic-neuron sign assignment permuted,
        Dale-consistent (AC-N2), per-edge |w| fixed.
    No closed verdict changes at any outcome; the outputs are
    DECOMPOSITION READINGS ("separates at p < 0.05" or not, per
    statistic x family). AC-N4, bridge stated: "p >= 0.05 under the
    weight family => the property is topology-carried" is an inference
    whose bridge is the invariant set.
  - 200 nulls per family, seeds 4242+0..199, one-sided empirical
    p = (1+k)/201, SAME seeds as Stage A for comparability (AC-N3).
  - DEGENERACY FLOORS: < 0.5 of edges changing |w| under the weight
    family = BLOCKED-degenerate; constant sign multiset = NA reported,
    never a p; any shuffle_invariants failure = BLOCKED.
  - Machinery: cx_topology_killtest.py's run_pipeline VERBATIM with
    the null generator injected (its rewire_fn seam); the Stage-A
    'verdict' key is discarded and replaced by reading labels.

Exit codes (section-7 override of the shared convention, stated in
the registration): 0 = readings completed, 3 = BLOCKED. There is no
KILL exit -- a refinement has readings, not verdicts.

Run:    python scripts/arenas/cx_topology_nulls2.py
Output: results/arenas/cx_topology_nulls2.json (+ .log)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# --- Stage-A machinery, imported VERBATIM (the registration's clause) --------
_CX_PATH = ROOT / "scripts/arenas/cx_topology_killtest.py"
_spec = importlib.util.spec_from_file_location("cx_topology_killtest",
                                               _CX_PATH)
cx = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("cx_topology_killtest", cx)
_spec.loader.exec_module(cx)

N_NULLS = cx.N_NULLS                      # 200
SEED_BASE = cx.REWIRE_SEED_BASE           # 4242 (AC-N3: same seeds)
ALPHA = cx.ALPHA                          # 0.05
EXPECTED_COUNTS = cx.EXPECTED_COUNTS
RUNTIME_DIR = cx.RUNTIME_DIR
TYPE_PATTERNS = cx.TYPE_PATTERNS

# frozen degeneracy floor (killtest_design.md section 7)
MIN_FRACTION_CHANGED = 0.5
OUT_JSON = ROOT / "results/arenas/cx_topology_nulls2.json"

# The three declared families, in reporting order. AC-N1: within-pre
# is PRIMARY for the decomposition sentence.
FAMILIES = ("weight_within_pre", "weight_global", "sign")


def family_fn(family: str):
    """Return a (matrix, seed) -> matrix null generator for run_pipeline's
    rewire_fn seam, plus a stats probe used by the degeneracy floors."""
    from flygi.connectome import nulls

    if family == "weight_within_pre":
        def fn(matrix, seed):
            shuffled, _ = nulls.weight_shuffle(matrix, seed=seed,
                                               within_presynaptic=True)
            return shuffled
    elif family == "weight_global":
        def fn(matrix, seed):
            shuffled, _ = nulls.weight_shuffle(matrix, seed=seed,
                                               within_presynaptic=False)
            return shuffled
    elif family == "sign":
        def fn(matrix, seed):
            shuffled, _ = nulls.sign_shuffle(matrix, seed=seed)
            return shuffled
    else:
        raise ValueError(f"unknown family {family!r}")
    return fn


def degeneracy_check(matrix, family: str) -> dict[str, Any]:
    """The frozen floors, probed on the first seed BEFORE the 200-null
    loop: near-identity weight permutations and constant sign multisets
    yield BLOCKED/NA, never a p."""
    from flygi.connectome import nulls

    if family.startswith("weight"):
        shuffled, stats = nulls.weight_shuffle(
            matrix, seed=SEED_BASE,
            within_presynaptic=(family == "weight_within_pre"))
        invariants = nulls.shuffle_invariants(
            matrix, shuffled, family="weight",
            within_presynaptic=(family == "weight_within_pre"))
        return {"stats": stats, "invariants": invariants,
                "blocked": (None if stats["fraction_magnitudes_changed"]
                            >= MIN_FRACTION_CHANGED else
                            f"degenerate weight shuffle: fraction changed "
                            f"{stats['fraction_magnitudes_changed']:.3f} < "
                            f"{MIN_FRACTION_CHANGED}"),
                "na": None}
    shuffled, stats = nulls.sign_shuffle(matrix, seed=SEED_BASE)
    invariants = nulls.shuffle_invariants(matrix, shuffled, family="sign")
    return {"stats": stats, "invariants": invariants, "blocked": None,
            "na": ("constant sign multiset -- shuffle is the identity"
                   if stats["constant_sign_multiset"] else None)}


def reading(p: float) -> str:
    return "separates" if p < ALPHA else "does not separate"


def run_decomposition(matrix, types, instances, n_nulls: int, log,
                      families=FAMILIES) -> dict[str, Any]:
    """Pure given its inputs: per family, degeneracy floors then the
    Stage-A pipeline with the family's generator injected. Readings
    only; the Stage-A 'verdict' key is discarded by design."""
    record: dict[str, Any] = {"hypothesis": "H-STAGEA-NULL-DECOMPOSITION",
                              "n_nulls": n_nulls, "families": {}}
    for family in families:
        log(f"--- family {family} ---")
        probe = degeneracy_check(matrix, family)
        entry: dict[str, Any] = {
            "generator_stats": probe["stats"],
            "invariants": probe["invariants"],
        }
        if not probe["invariants"]["valid"]:
            entry["blocked"] = ("invariant violation: "
                                + "; ".join(probe["invariants"]["failures"]))
            record["families"][family] = entry
            continue
        if probe["blocked"]:
            entry["blocked"] = probe["blocked"]
            record["families"][family] = entry
            continue
        if probe["na"]:
            entry["na"] = probe["na"]
            record["families"][family] = entry
            continue
        result = cx.run_pipeline(matrix, types, instances, n_nulls, log,
                                 rewire_fn=family_fn(family))
        if "blocked" in result:
            entry["blocked"] = result["blocked"]
            record["families"][family] = entry
            continue
        # readings, never verdicts (the registration's refinement rule)
        entry.update({
            "real_bandedness": result["real"]["bandedness"],
            "real_mirror_peak_pen_a": result["real"]["mirror_peak_pen_a"],
            "null_bandedness_max": result["null_bandedness_max"],
            "null_mirror_peak_max": result["null_mirror_peak_max"],
            "p_banded": result["p_banded"],
            "p_mirror_peak": result["p_mirror_peak"],
            "reading_banded": reading(result["p_banded"]),
            "reading_mirror_peak": reading(result["p_mirror_peak"]),
        })
        record["families"][family] = entry
        log(f"[{family}] bandedness: {entry['reading_banded']} "
            f"(p {entry['p_banded']:.5f}); mirror-peak: "
            f"{entry['reading_mirror_peak']} (p {entry['p_mirror_peak']:.5f})")
    return record


def check_prerequisites() -> list[str]:
    return cx.check_prerequisites()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-STAGEA-NULL-DECOMPOSITION readings (data-gated)")
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites()
    if missing:
        print("BLOCKED -- the decomposition cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        print("Run where the compiled runtime lives "
              "(docs/arenas/task10_menu/runbook.md).")
        return 3

    args.output.parent.mkdir(parents=True, exist_ok=True)
    handle = open(args.output.with_suffix(".log"), "w")

    def log(message: str) -> None:
        print(message, flush=True)
        handle.write(message + "\n")
        handle.flush()

    started = time.time()
    from flygi.connectome.subcircuit import extract_subcircuit, select_nodes
    indices = select_nodes(RUNTIME_DIR, type_patterns=TYPE_PATTERNS)
    sub = extract_subcircuit(RUNTIME_DIR, indices)
    counts = {t: int((sub.types == t).sum()) for t in EXPECTED_COUNTS}
    log(f"subcircuit: {sub.node_count} nodes, composition {counts}")
    if counts != EXPECTED_COUNTS:
        log(f"BLOCKED: composition deviates from {EXPECTED_COUNTS}")
        return 3

    record = run_decomposition(sub.matrix, sub.types, sub.instances,
                               N_NULLS, log)
    record["elapsed_s"] = round(time.time() - started, 1)
    args.output.write_text(json.dumps(record, indent=2, default=float))
    log(json.dumps(record, indent=2, default=float))
    blocked = [f for f, e in record["families"].items() if "blocked" in e]
    if blocked and len(blocked) == len(record["families"]):
        log(f"BLOCKED: every family blocked ({blocked})")
        return 3
    log("READINGS COMPLETE (refinement; no verdict changes)")
    handle.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
