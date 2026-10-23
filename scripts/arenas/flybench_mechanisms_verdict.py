#!/usr/bin/env python3
"""H-FLYGI-FLYBENCH-SFA / H-FLYGI-FLYBENCH-TERMINAL -- the frozen verdict.

Registered 2026-10-23 (docs/arenas/task10_menu/killtest_design.md section 6,
frozen BEFORE this script or either mechanism adapter existed). This script
takes the stored uniform-baseline result JSON and one mechanism's result
JSON, applies the frozen bars and floors mechanically, and decides nothing
itself. Precedent: scripts/arenas/flybench_calibrated_verdict.py; the check
split, the check-identity keying and the exit codes are carried verbatim.

FROZEN BARS (constants verbatim from the registration; PASS iff ALL hold):

  SFA       1. hard-tier graded: mechanism >= uniform hard_graded + 0.02
            2. overall graded >= 0.701            (= uniform 0.7113 - 0.01)
            3. specificity vs rewired >= +0.252   (= +0.282 - 0.03)
            4. activation-subset mean graded >= uniform - 0.01
               (SFA is suppressive; it must not buy the hard tier by
               selling activation -- AF-8's failure axis)

  TERMINAL  1. hard-tier graded: mechanism >= uniform hard_graded + 0.02
            2. core_score stays 1.000             (regression guard)
            3. overall graded >= 0.701
            4. specificity vs rewired >= +0.252   (rewired control runs
               terminal=None per FlyBench's own convention -- declared)

BLOCKED (exit 3; an instrument statement, never a verdict). Registered
floors mechanically checkable here: (iii) uniform baseline JSON absent/
unreadable, or build composition != the baseline's recorded 176,422
neurons; (iv) terminal only: body-ID coverage < 0.95 or synapse survival
< 0.90 on a base arm; (v) non-finite membrane recorded in any arm. Floors
(i) off-switch bit-identity and (ii) the in-cloud gates are asserted by
tests/test_flybench_mechanisms.py, which must pass before any run of this
script means anything. INSTRUMENT-LEVEL GUARDS added at build time, NOT in
the registration (each one makes an otherwise-undefined or silently-fake
bar impossible, the calibrated-verdict precedent): an empty shared
activation set (SFA bar 4 is a mean over it); hard_graded or specificity
missing from a report (bars 1/3 undefined); no mechanism sidecar for this
build, a sidecar recording sfa_b == 0 (mechanism never on), or no base
sidecar with the shipped table attached (terminal silently ran as the
uniform engine).

Usage:
  python scripts/arenas/flybench_mechanisms_verdict.py --mechanism sfa \
      results/arenas/malecns_flygi.json results/arenas/malecns_sfa.json
  python scripts/arenas/flybench_mechanisms_verdict.py --mechanism terminal \
      results/arenas/malecns_flygi.json results/arenas/malecns_terminal.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MECHANISMS = ("sfa", "terminal")

# frozen bars (killtest_design.md section 6, verbatim)
BAR_HARD_DELTA = 0.02
BAR_OVERALL_GRADED = 0.701
BAR_SPECIFICITY = 0.252
BAR_ACTIVATION_GUARD = 0.01      # SFA bar 4
BAR_CORE = 1.0                   # terminal bar 2

# frozen floors / registered baseline facts
UNIFORM_BASELINE_N_NEURONS = 176_422
TERMINAL_TABLE_SUM = 3_782_429
TERMINAL_COVERAGE_FLOOR = 0.95
TERMINAL_SURVIVAL_FLOOR = 0.90

MECH_SIDECAR_DIR = Path.home() / ".cache" / "flygi-flybench-mechanisms"


# --- check split, VERBATIM from flybench_calibrated_verdict.py (the
# registered precedent; copied rather than imported so this script stays a
# single frozen file) ---------------------------------------------------------

def is_activation(check: dict) -> bool:
    op = str(check.get("op", ""))
    ratio = " / " in str(check.get("description", ""))
    return op in (">", ">=") and not ratio


def check_table(report: dict) -> dict[tuple[str, str], dict]:
    # Key by the check's identity, NOT its full description: flybench appends
    # a volatile "  [N/3 seeds, sd S]" annotation (the 2026-10-03 lesson).
    out = {}
    for task in report.get("tasks", []):
        for check in task.get("checks", []):
            ident = str(check.get("description", "")).split("  [")[0]
            out[(task.get("task", "?"), ident)] = check
    return out


def split_scores(uniform: dict, mechanism: dict):
    """Shared checks, classified; (activation_rows, suppression_rows) as
    lists of (key, graded_uniform, graded_mechanism)."""
    tu, tm = check_table(uniform), check_table(mechanism)
    act, sup = [], []
    for key in sorted(set(tu) & set(tm)):
        row = (key, float(tu[key].get("graded", 0.0)),
               float(tm[key].get("graded", 0.0)))
        (act if is_activation(tu[key]) else sup).append(row)
    return act, sup


# --- floors ------------------------------------------------------------------

def sidecar_rows(mechanism: str, n_neurons: int,
                 sidecar_dir: Path) -> list[tuple[str, dict]]:
    rows = []
    for f in sorted(Path(sidecar_dir).glob(f"{mechanism}-*.json")):
        try:
            s = json.loads(f.read_text())
        except Exception:
            continue
        if int(s.get("n_neurons") or 0) != n_neurons:
            continue   # a sidecar from a different wiring (e.g. the toy)
        rows.append((f.name, s))
    return rows


def blocked_reasons(mechanism: str, uniform: dict, mech: dict,
                    sidecar_dir: Path = MECH_SIDECAR_DIR) -> list[str]:
    reasons: list[str] = []
    n_uni = int(uniform.get("n_neurons") or 0)
    n_mech = int(mech.get("n_neurons") or 0)
    # floor (iii): the stored baseline must be the registered build
    if n_uni != UNIFORM_BASELINE_N_NEURONS:
        reasons.append(
            f"uniform baseline has {n_uni} neurons, the registered baseline "
            f"recorded {UNIFORM_BASELINE_N_NEURONS} (floor iii)")
    if n_mech != n_uni:
        reasons.append(
            f"mechanism run has {n_mech} neurons vs the baseline's {n_uni} "
            f"-- build composition changed (floor iii)")
    # instrument guards: bars undefined without these report fields
    if uniform.get("hard_graded") is None or mech.get("hard_graded") is None:
        reasons.append("hard_graded missing from a report (instrument guard:"
                       " bar 1 is undefined without the hard tier)")
    if mech.get("specificity") is None:
        reasons.append("specificity missing from the mechanism report -- no "
                       "control ran (instrument guard: bar undefined)")
    # floor (v) + mechanism-specific guards, via the adapter sidecars
    rows = sidecar_rows(mechanism, n_mech, sidecar_dir)
    if not rows:
        reasons.append(
            f"no {mechanism} sidecar for the {n_mech}-neuron build under "
            f"{sidecar_dir} (instrument guard: the run did not go through "
            f"the registered adapter)")
    for name, s in rows:
        if s.get("nonfinite_v"):
            reasons.append(f"{name}: non-finite membrane recorded (floor v)")
    if mechanism == "sfa":
        for name, s in rows:
            if float(s.get("sfa_b") or 0.0) == 0.0:
                reasons.append(f"{name}: sfa_b == 0 -- the mechanism was "
                               f"never on (instrument guard)")
    if mechanism == "terminal":
        # floor (iv), evaluated on BASE arms only (non-control, unjittered,
        # unsilenced), so a weight-jitter task condition cannot spuriously
        # block the run (declared in resolve_terminal's docstring).
        base = [(n, s) for n, s in rows
                if not s.get("control")
                and not float(s.get("weight_jitter") or 0.0)
                and not int(s.get("silenced") or 0)]
        attached = [(n, s) for n, s in base if s.get("attached")]
        if rows and not attached:
            reasons.append(
                "terminal never attached on a base (non-control) arm -- the "
                "mechanism run was the uniform engine (instrument guard; set "
                "FLYGI_TERMINAL_TABLE)")
        for name, s in attached:
            if s.get("source") != "table":
                reasons.append(
                    f"{name}: terminal attached from {s.get('source')!r}, "
                    f"not the registered shipped table (instrument guard)")
                continue
            if float(s.get("table_sum") or 0) != TERMINAL_TABLE_SUM:
                reasons.append(
                    f"{name}: table sum {s.get('table_sum')} != "
                    f"{TERMINAL_TABLE_SUM} (loader gate)")
            if float(s.get("coverage") or 0.0) < TERMINAL_COVERAGE_FLOOR:
                reasons.append(
                    f"{name}: body-ID coverage {s.get('coverage')} < "
                    f"{TERMINAL_COVERAGE_FLOOR} (floor iv)")
            if float(s.get("survival") or 0.0) < TERMINAL_SURVIVAL_FLOOR:
                reasons.append(
                    f"{name}: synapse survival {s.get('survival')} < "
                    f"{TERMINAL_SURVIVAL_FLOOR} (floor iv)")
    return reasons


# --- the frozen rule ----------------------------------------------------------

def verdict(mechanism: str, uniform: dict, mech: dict,
            sidecar_dir: Path = MECH_SIDECAR_DIR) -> dict:
    if mechanism not in MECHANISMS:
        raise ValueError(f"mechanism must be one of {MECHANISMS}")
    act, sup = split_scores(uniform, mech)
    reasons = blocked_reasons(mechanism, uniform, mech, sidecar_dir)
    if mechanism == "sfa" and not act:
        # the calibrated-verdict precedent's instrument guard: bar 4 is a
        # mean over the shared activation set, undefined on an empty set
        reasons.append("shared activation-check set is empty")
    mean = lambda rows, i: (sum(r[i] for r in rows) / len(rows)) if rows else float("nan")  # noqa: E731
    act_uni, act_mech = mean(act, 1), mean(act, 2)
    sup_uni, sup_mech = mean(sup, 1), mean(sup, 2)
    hard_uni = uniform.get("hard_graded")
    hard_mech = mech.get("hard_graded")
    hard_uni = float(hard_uni) if hard_uni is not None else float("nan")
    hard_mech = float(hard_mech) if hard_mech is not None else float("nan")
    overall = float(mech.get("graded") or 0.0)
    spec = mech.get("specificity")
    spec = float(spec) if spec is not None else float("nan")
    bars = {
        "hard_improves": hard_mech >= hard_uni + BAR_HARD_DELTA,
        "overall_holds": overall >= BAR_OVERALL_GRADED,
        "specificity_holds": spec >= BAR_SPECIFICITY,
    }
    if mechanism == "sfa":
        bars["activation_holds"] = (
            (act_mech >= act_uni - BAR_ACTIVATION_GUARD) if act else False)
    else:
        bars["core_holds"] = float(mech.get("core_score") or 0.0) >= BAR_CORE
    state = ("BLOCKED" if reasons
             else "PASS" if all(bars.values()) else "KILL")
    return {
        "mechanism": mechanism,
        "n_shared_checks": len(act) + len(sup),
        "n_activation": len(act), "n_suppression": len(sup),
        "hard_graded": {"uniform": hard_uni, "mechanism": hard_mech,
                        "delta": hard_mech - hard_uni},
        "activation_mean": {"uniform": act_uni, "mechanism": act_mech,
                            "delta": act_mech - act_uni if act else float("nan")},
        "suppression_mean": {"uniform": sup_uni, "mechanism": sup_mech},
        "overall_graded_mechanism": overall,
        "specificity_mechanism": spec,
        "core_score_mechanism": mech.get("core_score"),
        "bars": bars, "blocked_reasons": reasons, "verdict": state,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mechanism", required=True, choices=MECHANISMS)
    parser.add_argument("uniform", type=Path,
                        help="the stored uniform-baseline row "
                             "(the trivial alternative)")
    parser.add_argument("mechanism_json", type=Path,
                        help="the mechanism run to judge")
    parser.add_argument("--sidecar-dir", type=Path, default=MECH_SIDECAR_DIR,
                        help="adapter sidecar directory (audit/testing)")
    parser.add_argument("--list-checks", action="store_true",
                        help="print the classified check lists (audit)")
    args = parser.parse_args()
    reports = []
    for path in (args.uniform, args.mechanism_json):
        try:
            reports.append(json.loads(path.read_text()))
        except Exception as exc:   # floor (iii): absent/unreadable -> BLOCKED
            print(json.dumps({
                "mechanism": args.mechanism,
                "blocked_reasons": [f"{path}: absent or unreadable "
                                    f"({type(exc).__name__}: {exc}) -- floor iii"],
                "verdict": "BLOCKED"}, indent=2))
            print("VERDICT: BLOCKED")
            return 3
    uniform, mech = reports
    if args.list_checks:
        act, sup = split_scores(uniform, mech)
        for name, rows in (("ACTIVATION", act), ("SUPPRESSION", sup)):
            print(f"-- {name} ({len(rows)}):")
            for (task, desc), gu, gm in rows:
                print(f"   {task:>28} | {gu:.3f} -> {gm:.3f} | {desc[:70]}")
    out = verdict(args.mechanism, uniform, mech, args.sidecar_dir)
    print(json.dumps(out, indent=2))
    print(f"VERDICT: {out['verdict']}")
    return 0 if out["verdict"] == "PASS" else (3 if out["verdict"] == "BLOCKED" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
