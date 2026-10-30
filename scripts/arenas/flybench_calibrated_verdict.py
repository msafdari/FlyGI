#!/usr/bin/env python3
"""H-FLYGI-FLYBENCH-CALIBRATED -- the frozen verdict, computed mechanically.

Registered 2026-10-02 (docs/arenas/task3_flybench/calibrated_design.md,
EXPERIMENTS.yaml), BEFORE the calibrated adapter existed. This script takes
the two result JSONs and applies the frozen rule; it decides nothing itself.

CHECK SPLIT (frozen wording made mechanical): an ACTIVATION check requires
a measurement to EXCEED a threshold (result-JSON `op` is ">" or ">=") and
is not a ratio; ratio checks (description contains " / ") and
below-threshold checks are SUPPRESSION. The classified lists are printed
so the sets are auditable.

FROZEN BARS (all three must hold; constants verbatim from the registry):
  1. mean graded over SHARED activation checks: calibrated >= uniform + 0.02
  2. overall graded (calibrated) >= 0.701
  3. specificity vs rewired (calibrated) >= +0.252
BLOCKED (not a verdict). The two registered conditions, frozen: near-zero
tau/type coverage, or the KC sparseness band unreachable (both read from
the calibration sidecars). A third condition -- an empty shared activation
set -- is NOT in the registration: it is an instrument-level guard added
at build time, because bar 1 is a mean over the shared activation set and
is undefined on an empty set.

Usage:
  python scripts/arenas/flybench_calibrated_verdict.py \
      results/arenas/malecns_flygi.json results/arenas/malecns_calibrated.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BAR_ACTIVATION_DELTA = 0.02
BAR_OVERALL_GRADED = 0.701
BAR_SPECIFICITY = 0.252
CAL_CACHE_DIR = Path.home() / ".cache" / "flygi-flybench-calibration"


def is_activation(check: dict) -> bool:
    op = str(check.get("op", ""))
    ratio = " / " in str(check.get("description", ""))
    return op in (">", ">=") and not ratio


def check_table(report: dict) -> dict[tuple[str, str], dict]:
    # Key by the check's identity, NOT its full description: flybench appends
    # a volatile "  [N/3 seeds, sd S]" annotation that changes whenever the
    # measured values change, so keying on the full string silently drops
    # every check the manipulation moved (caught 2026-10-03: 66 of 149 checks
    # "shared" on the first calibrated run). Same convention as flybench's
    # own diff command.
    out = {}
    for task in report.get("tasks", []):
        for check in task.get("checks", []):
            ident = str(check.get("description", "")).split("  [")[0]
            out[(task.get("task", "?"), ident)] = check
    return out


def split_scores(uniform: dict, calibrated: dict):
    """Shared checks, classified; returns (activation_rows, suppression_rows)
    as lists of (key, graded_uniform, graded_calibrated)."""
    tu, tc = check_table(uniform), check_table(calibrated)
    act, sup = [], []
    for key in sorted(set(tu) & set(tc)):
        row = (key, float(tu[key].get("graded", 0.0)),
               float(tc[key].get("graded", 0.0)))
        (act if is_activation(tu[key]) else sup).append(row)
    return act, sup


def blocked_reasons(calibrated: dict) -> list[str]:
    n = int(calibrated.get("n_neurons") or 0)
    reasons = []
    for sidecar in sorted(CAL_CACHE_DIR.glob("*.json")):
        try:
            s = json.loads(sidecar.read_text())
        except Exception:
            continue
        if n and int(s.get("n_neurons") or 0) != n:
            continue   # a sidecar from a different connectome (e.g. the toy)
        if s.get("blocked") or s.get("blocked_sparseness"):
            reasons.append(f"{sidecar.name}: KC sparseness band unreachable "
                           f"(achieved {s.get('achieved')})")
        if s.get("tau_rows_matched", 1) == 0 and s.get("kc_count", 1) == 0:
            reasons.append(f"{sidecar.name}: zero type coverage")
    return reasons


def verdict(uniform: dict, calibrated: dict) -> dict:
    act, sup = split_scores(uniform, calibrated)
    reasons = blocked_reasons(calibrated)
    # Instrument-level guard, not in the registration: bar 1 is a mean
    # over the shared activation set, hence undefined on an empty set.
    if not act:
        reasons.append("shared activation-check set is empty")
    mean = lambda rows, i: (sum(r[i] for r in rows) / len(rows)) if rows else float("nan")  # noqa: E731
    act_uni, act_cal = mean(act, 1), mean(act, 2)
    sup_uni, sup_cal = mean(sup, 1), mean(sup, 2)
    overall = float(calibrated.get("graded") or 0.0)
    spec = calibrated.get("specificity")
    spec = float(spec) if spec is not None else float("nan")
    bars = {
        "activation_improves": (act_cal - act_uni) >= BAR_ACTIVATION_DELTA if act else False,
        "overall_holds": overall >= BAR_OVERALL_GRADED,
        "specificity_holds": spec >= BAR_SPECIFICITY,
    }
    state = ("BLOCKED" if reasons
             else "PASS" if all(bars.values()) else "KILL")
    return {
        "n_shared_checks": len(act) + len(sup),
        "n_activation": len(act), "n_suppression": len(sup),
        "activation_mean": {"uniform": act_uni, "calibrated": act_cal,
                            "delta": act_cal - act_uni if act else float("nan")},
        "suppression_mean": {"uniform": sup_uni, "calibrated": sup_cal},
        "overall_graded_calibrated": overall,
        "specificity_calibrated": spec,
        "bars": bars, "blocked_reasons": reasons, "verdict": state,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("uniform", type=Path,
                        help="the Shiu-uniform row (the trivial alternative)")
    parser.add_argument("calibrated", type=Path)
    parser.add_argument("--list-checks", action="store_true",
                        help="print the classified check lists (audit)")
    args = parser.parse_args()
    uniform = json.loads(args.uniform.read_text())
    calibrated = json.loads(args.calibrated.read_text())
    act, sup = split_scores(uniform, calibrated)
    if args.list_checks:
        for name, rows in (("ACTIVATION", act), ("SUPPRESSION", sup)):
            print(f"-- {name} ({len(rows)}):")
            for (task, desc), gu, gc in rows:
                print(f"   {task:>28} | {gu:.3f} -> {gc:.3f} | {desc[:70]}")
    out = verdict(uniform, calibrated)
    print(json.dumps(out, indent=2))
    print(f"VERDICT: {out['verdict']}")
    return 0 if out["verdict"] == "PASS" else (3 if out["verdict"] == "BLOCKED" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
