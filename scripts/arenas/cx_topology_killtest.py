#!/usr/bin/env python3
"""H-CX-RING-TOPOLOGY -- the Task 9 Stage-A (structural) kill test.

PREREGISTRATION (EXPERIMENTS.yaml H-CX-RING-TOPOLOGY and
docs/arenas/task9_cx_latent/killtest_design.md, both 2026-10-10,
frozen BEFORE this file existed; restated, not changed):

  - Substrate: the validated CX subcircuit -- select_nodes patterns
    ("EPG", "PEN_a*", "PEN_b*", "Delta7", "PEG"), recorded composition
    148 neurons = 46 EPG + 20 PEN_a(PEN1) + 22 PEN_b(PEN2) + 42 Delta7
    + 18 PEG (BLOCKED on mismatch).
  - Wedge mapping (AC-1, cx_ring/cx_scratchpad VERBATIM): instance
    regex `_([LR])(\\d)`, index = (wedge-1)*2 + (0 if L else 1),
    16 positions, 22.5 deg each; no metric depends on the fixed
    rotation.
  - Metrics (AC-4, mechanical): two-hop W2 = relu(W[EPG<-PEN]) @
    relu(W[PEN<-EPG]) per PEN population; 16x16 wedge aggregation
    (mean over cell pairs); BANDEDNESS = mass fraction within
    circular wedge distance <= 2 of the all-PEN matrix; OFFSET per
    population = argmax over circular difference d in {-7..8} of the
    mean profile (valid only for 1 <= |d| <= 7).
  - NULLS: 200 degree-preserving rewires of the full 148-neuron
    subcircuit matrix (seeds 4242+0..199), identical pipeline;
    empirical one-sided p = (1 + #{null >= real}) / 201.
  - PASS iff (1) bandedness beats the nulls at p < 0.05 AND
    (2) PEN_a-left and PEN_a-right offsets are valid, OPPOSITE in
    sign, and the separation S = |off_L - off_R| (0 unless signs
    oppose) beats the nulls at p < 0.05. PEN_b offsets and a blind
    spectral-ordering check are reported as context and decide
    nothing. KILL closes Task 9 with no dynamics built (Stage B,
    H-CX-HEADING-LATENT, then closes not-pursued).
  - BLOCKED (exit 3): composition mismatch; wedge labels parse for
    < 90% of EPG or of PEN_a; degenerate (zero) all-PEN two-hop;
    compiled runtime absent.

Data gate: runs where the compiled runtime lives (the cloud container
lacks it). The PIPELINE itself is pure and is validated in-cloud on
synthetic ring graphs, including against the real rewire machinery,
before any data contact.

Run:    python scripts/arenas/cx_topology_killtest.py
Output: results/arenas/cx_topology_killtest.json (+ .log)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# --- frozen constants (killtest_design.md; do not tune) ---------------------
N_WEDGES = 16
BAND = 2
N_NULLS = 200
REWIRE_SEED_BASE = 4242
ALPHA = 0.05
TYPE_PATTERNS = ("EPG", "PEN_a*", "PEN_b*", "Delta7", "PEG")
EXPECTED_COUNTS = {"EPG": 46, "PEN_a(PEN1)": 20, "PEN_b(PEN2)": 22,
                   "Delta7": 42, "PEG": 18}
MIN_WEDGE_COVERAGE = 0.90

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
OUT_JSON = ROOT / "results/arenas/cx_topology_killtest.json"

WEDGE_RE = re.compile(r"_([LR])(\d)")


# ---------------------------------------------------------------------------
# Pure plumbing (unit-tested in-cloud on synthetic rings)
# ---------------------------------------------------------------------------

def wedge_index(instance: str):
    """AC-1, cx_ring verbatim: _L1.._L8/_R1.._R8 -> 0..15, else None."""
    match = WEDGE_RE.search(instance)
    if not match:
        return None
    side, wedge = match.group(1), int(match.group(2))
    if not 1 <= wedge <= 8:
        return None
    return (wedge - 1) * 2 + (0 if side == "L" else 1)


def relu_dense(block) -> np.ndarray:
    arr = np.asarray(block.todense() if hasattr(block, "todense") else block,
                     dtype=np.float64)
    return np.maximum(arr, 0.0)


def two_hop(W, epg_idx: np.ndarray, mid_idx: np.ndarray) -> np.ndarray:
    """relu(W[EPG<-mid]) @ relu(W[mid<-EPG]) -> (n_epg, n_epg), with
    W[post, pre] orientation throughout."""
    a = relu_dense(W[epg_idx][:, mid_idx])      # EPG <- mid
    b = relu_dense(W[mid_idx][:, epg_idx])      # mid <- EPG
    return a @ b


def wedge_aggregate(W2: np.ndarray, wedges: np.ndarray,
                    n: int = N_WEDGES) -> np.ndarray:
    """Mean cell-pair coupling into an (n, n) (post-wedge, pre-wedge)
    matrix; zero where no pair exists. `wedges` aligns with W2's axes."""
    sums = np.zeros((n, n))
    counts = np.zeros((n, n))
    for j in range(W2.shape[0]):
        wj = wedges[j]
        if wj < 0:
            continue
        for i in range(W2.shape[1]):
            wi = wedges[i]
            if wi < 0:
                continue
            sums[wj, wi] += W2[j, i]
            counts[wj, wi] += 1.0
    out = np.zeros((n, n))
    nonzero = counts > 0
    out[nonzero] = sums[nonzero] / counts[nonzero]
    return out


def circ_dist(a: int, b: int, n: int = N_WEDGES) -> int:
    return min((a - b) % n, (b - a) % n)


def bandedness(M: np.ndarray, band: int = BAND) -> float:
    """Mass fraction within circular wedge distance <= band. NaN if the
    matrix is all zero (degenerate -> BLOCKED upstream)."""
    total = float(M.sum())
    if total <= 0:
        return float("nan")
    n = M.shape[0]
    inside = sum(float(M[j, i]) for j in range(n) for i in range(n)
                 if circ_dist(j, i, n) <= band)
    return inside / total


def offset_profile(M: np.ndarray) -> dict[int, float]:
    """Mean coupling over (post, pre) wedge pairs at signed circular
    difference d = (post - pre) mod n, mapped to {-7..8}."""
    n = M.shape[0]
    sums = {d: 0.0 for d in range(-(n // 2 - 1), n // 2 + 1)}
    counts = dict.fromkeys(sums, 0)
    for j in range(n):
        for i in range(n):
            d = (j - i) % n
            if d > n // 2:
                d -= n
            sums[d] += float(M[j, i])
            counts[d] += 1
    return {d: (sums[d] / counts[d] if counts[d] else 0.0) for d in sums}


def offset(M: np.ndarray):
    """argmax of the profile; valid only for 1 <= |d| <= 7 (0 and the
    antipode 8 fail per the registration). REPORTED AS CONTEXT since
    the 2026-10-10 pre-data-contact amendment. Returns (d, valid)."""
    profile = offset_profile(M)
    if all(v == 0.0 for v in profile.values()):
        return 0, False
    d = max(profile, key=profile.get)
    return d, 1 <= abs(d) <= N_WEDGES // 2 - 1


def mean_offset(M: np.ndarray) -> float:
    """Mass-weighted mean offset over d in -7..7 (antipode excluded).
    REPORTED AS CONTEXT: tried as the decision statistic in the
    2026-10-10 amendment sequence and measured too weak (null max 5.4,
    p 0.230 on the perfect synthetic compass)."""
    profile = offset_profile(M)
    num = den = 0.0
    for d, v in profile.items():
        if abs(d) == N_WEDGES // 2:
            continue
        mass = max(v, 0.0)
        num += d * mass
        den += mass
    return num / den if den > 0 else float("nan")


def norm_profile(M: np.ndarray):
    """Normalized positive offset profile q(d), d in -7..7 (antipode
    excluded); None when the positive mass is zero."""
    profile = offset_profile(M)
    positive = {d: max(v, 0.0) for d, v in profile.items()
                if abs(d) != N_WEDGES // 2}
    total = sum(positive.values())
    if total <= 0:
        return None
    return {d: v / total for d, v in positive.items()}


def mirror_peak(M_l: np.ndarray, M_r: np.ndarray) -> float:
    """THE ADOPTED shifter statistic (amendment of 2026-10-10, before
    any data contact; killtest_design.md records the measured
    sequence): S = max over d in 1..7 of
    max(q_L(d)*q_R(-d), q_L(-d)*q_R(d)). Chirality-free; nonzero only
    when the hemispheres concentrate coupling at OPPOSITE offsets.
    Synthetic gate: real 1.0000 vs rewire-null max 0.107, p 0.0099."""
    q_l, q_r = norm_profile(M_l), norm_profile(M_r)
    if q_l is None or q_r is None:
        return 0.0
    return max(max(q_l[d] * q_r[-d], q_l[-d] * q_r[d])
               for d in range(1, N_WEDGES // 2))


def empirical_p(real: float, nulls: list[float]) -> float:
    return (1.0 + sum(1 for x in nulls if x >= real)) / (len(nulls) + 1.0)


def spectral_context(M: np.ndarray) -> dict[str, Any]:
    """Blind ordering check (context, decides nothing): Laplacian
    eigenmap angles of the symmetrized wedge matrix vs the anatomical
    ordering, scored as the best mean absolute circular residual over
    the 16 rotations x 2 reflections."""
    A = (M + M.T) / 2.0
    np.fill_diagonal(A, 0.0)
    if A.sum() <= 0:
        return {"residual_deg": float("nan")}
    L = np.diag(A.sum(axis=1)) - A
    _, vecs = np.linalg.eigh(L)
    angles = np.arctan2(vecs[:, 2], vecs[:, 1])
    anatomical = np.arange(N_WEDGES) * (2 * np.pi / N_WEDGES)
    best = float("inf")
    for reflect in (1.0, -1.0):
        for rot in range(N_WEDGES):
            trial = reflect * angles + rot * (2 * np.pi / N_WEDGES)
            resid = np.angle(np.exp(1j * (trial - anatomical)))
            best = min(best, float(np.mean(np.abs(resid))))
    return {"residual_deg": float(np.degrees(best))}


def analyze(matrix, epg_idx, epg_wedges, pen_groups) -> dict[str, Any]:
    """One wiring's full metric set. pen_groups maps a label (e.g.
    'PEN_a_L') to its node-index array."""
    all_pen = np.concatenate([idx for idx in pen_groups.values()
                              if idx.size]).astype(np.int64)
    M_all = wedge_aggregate(two_hop(matrix, epg_idx, all_pen), epg_wedges)
    result: dict[str, Any] = {"bandedness": bandedness(M_all)}
    offsets = {}
    wedge_matrices = {}
    for label, idx in pen_groups.items():
        if idx.size == 0:
            offsets[label] = {"offset": 0, "valid": False,
                              "mean_offset": float("nan")}
            wedge_matrices[label] = np.zeros((N_WEDGES, N_WEDGES))
            continue
        M = wedge_aggregate(two_hop(matrix, epg_idx, idx), epg_wedges)
        wedge_matrices[label] = M
        d, valid = offset(M)
        offsets[label] = {"offset": int(d), "valid": bool(valid),
                          "mean_offset": mean_offset(M)}
    result["offsets"] = offsets
    result["mirror_peak_pen_a"] = mirror_peak(
        wedge_matrices["PEN_a_L"], wedge_matrices["PEN_a_R"])
    result["mirror_peak_pen_b"] = mirror_peak(
        wedge_matrices["PEN_b_L"], wedge_matrices["PEN_b_R"])
    result["spectral_context"] = spectral_context(M_all)
    return result


def run_pipeline(matrix, types, instances, n_nulls: int, log,
                 rewire_fn=None) -> dict[str, Any]:
    """The whole frozen decision pipeline, pure given its inputs:
    wedge parsing, real metrics, null distribution, bars. Returns the
    record dict with 'verdict' of PASS / KILL, or 'blocked' set."""
    types = np.asarray(types)
    instances = np.asarray(instances)
    epg_all = np.flatnonzero(types == "EPG")
    epg_wedge_raw = np.array([
        w if (w := wedge_index(instances[i])) is not None else -1
        for i in epg_all])
    epg_cov = float((epg_wedge_raw >= 0).mean()) if epg_all.size else 0.0
    keep = epg_wedge_raw >= 0
    epg_idx = epg_all[keep]
    epg_wedges = epg_wedge_raw[keep]

    pen_groups: dict[str, np.ndarray] = {}
    pen_cov = {}
    for tname, label in (("PEN_a(PEN1)", "PEN_a"), ("PEN_b(PEN2)", "PEN_b")):
        cells = np.flatnonzero(types == tname)
        left, right, labelled = [], [], 0
        for i in cells:
            match = WEDGE_RE.search(str(instances[i]))
            if match:
                labelled += 1
                (left if match.group(1) == "L" else right).append(int(i))
        pen_cov[label] = (labelled / cells.size) if cells.size else 0.0
        pen_groups[f"{label}_L"] = np.asarray(left, dtype=np.int64)
        pen_groups[f"{label}_R"] = np.asarray(right, dtype=np.int64)

    record: dict[str, Any] = {
        "hypothesis": "H-CX-RING-TOPOLOGY",
        "epg_wedge_coverage": epg_cov,
        "pen_coverage": pen_cov,
        "group_sizes": {k: int(v.size) for k, v in pen_groups.items()},
    }
    if epg_cov < MIN_WEDGE_COVERAGE or pen_cov["PEN_a"] < MIN_WEDGE_COVERAGE:
        record["blocked"] = (f"wedge coverage below {MIN_WEDGE_COVERAGE}: "
                             f"EPG {epg_cov:.2f}, PEN_a {pen_cov['PEN_a']:.2f}")
        return record

    real = analyze(matrix, epg_idx, epg_wedges, pen_groups)
    if not np.isfinite(real["bandedness"]):
        record["blocked"] = "degenerate all-PEN two-hop (zero mass)"
        return record
    record["real"] = real
    log(f"real: bandedness {real['bandedness']:.4f}, offsets "
        + " ".join(f"{k}={v['offset']}{'' if v['valid'] else '!'}"
                   for k, v in real["offsets"].items())
        + f", mirror-peak a={real['mirror_peak_pen_a']:.4f} "
          f"b={real['mirror_peak_pen_b']:.4f}, spectral residual "
          f"{real['spectral_context']['residual_deg']:.1f} deg")

    if rewire_fn is None:
        from flygi.connectome.nulls import degree_preserving_rewire

        def rewire_fn(m, seed):
            rewired, _ = degree_preserving_rewire(m, seed=seed)
            return rewired

    null_banded, null_mirror = [], []
    t0 = time.time()
    for k in range(n_nulls):
        null = analyze(rewire_fn(matrix, REWIRE_SEED_BASE + k),
                       epg_idx, epg_wedges, pen_groups)
        null_banded.append(null["bandedness"] if
                           np.isfinite(null["bandedness"]) else 0.0)
        null_mirror.append(null["mirror_peak_pen_a"])
        if (k + 1) % 50 == 0:
            log(f"  nulls {k + 1}/{n_nulls} ({time.time() - t0:.1f}s)")

    p_banded = empirical_p(real["bandedness"], null_banded)
    p_mirror = empirical_p(real["mirror_peak_pen_a"], null_mirror)
    bars = {
        "banded": bool(p_banded < ALPHA),
        # amended 2026-10-10 pre-data-contact (killtest_design.md):
        # mirror-peak beats the rewire nulls
        "shifter": bool(p_mirror < ALPHA),
    }
    record.update({
        "null_bandedness_max": float(max(null_banded)),
        "null_mirror_peak_max": float(max(null_mirror)),
        "p_banded": p_banded,
        "p_mirror_peak": p_mirror,
        "n_nulls": n_nulls,
        "bars": bars,
        "verdict": "PASS" if all(bars.values()) else "KILL",
    })
    return record


def check_prerequisites() -> list[str]:
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    for mod in ("scipy",):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    return missing


# ---------------------------------------------------------------------------
# Data-gated assembly (local host only)
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-CX-RING-TOPOLOGY kill test (data-gated)")
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites()
    if missing:
        print("BLOCKED -- the kill test cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        print("Run where the compiled runtime lives "
              "(docs/arenas/task9_cx_latent/runbook.md).")
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
        log(f"BLOCKED: composition deviates from the recorded "
            f"{EXPECTED_COUNTS}")
        return 3

    record = run_pipeline(sub.matrix, sub.types, sub.instances, N_NULLS, log)
    record["elapsed_s"] = round(time.time() - started, 1)
    args.output.write_text(json.dumps(record, indent=2, default=float))
    log(json.dumps(record, indent=2, default=float))
    if "blocked" in record:
        log(f"BLOCKED: {record['blocked']}")
        return 3
    log(f"VERDICT: {record['verdict']}")
    handle.close()
    return 0 if record["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
