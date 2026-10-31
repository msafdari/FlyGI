#!/usr/bin/env python3
"""H-CX-BISWAS-FITTED -- the Biswas-recipe-fitted EPG-Delta7 ring
attractor on our compiled MaleCNS counts (Task 10, item 3).

PREREGISTRATION (EXPERIMENTS.yaml H-CX-BISWAS-FITTED; partial freeze
2026-10-23 + the dated NUMERIC COMPLETION 2026-10-31 in
docs/arenas/task10_menu/killtest_design.md section 3, committed
BEFORE this file existed; restated, not changed):

  - PREMISE: given their published derivation recipe applied ONCE to
    our counts (Biswas et al., bioRxiv 10.1101/2024.11.01.621596v2),
    the derived EPG-Delta7 realization sustains a position-faithful
    heading bump that its degree-preserving rewires do not. Their
    realization is EPG+Delta7 ONLY -- PEN/PEG have no role in it and
    stay unused (the AC-8 composition check still runs). A PASS is
    never reported unfitted: "given fitted per-type physiology" rides
    every close sentence.
  - RECIPE (ESTABLISHED, their Methods): EPG -> 8 wedges (AC-B1
    label convention); Delta7 -> 8 units by maximal cumulative output
    to EPG wedges (AC-B5 tie rule); unit counts = sum over pre,
    average over post; distance averaging (A_Delta=8) or mirror
    averaging (A_Delta=6,4); gammas fitted by their own procedures
    (r_a scan / 100^3 grid + Levenberg-Marquardt); validity = their
    Table 1 + Table 2 conditions.
  - G1 bars verbatim from H-CX-CLASS3-COMPASS, mapped to the 8-unit
    rate vector: 8 seeds 45 deg apart (the mu=0 rotations), per-seed
    retention >= 0.05 AND circvar <= 0.6 AND PVA error <= 45 deg;
    G1 passes iff >= 6 of 8. The simulation never masks units.
  - G2 NON-DECISIONAL: their model has no rotation input.
  - NULL BAR: 3 degree-preserving rewires (seeds 4242+0..2) of the
    neuron-level EPG+Delta7 subcircuit; the FULL recipe re-runs per
    rewire; no valid fit at a configuration counts as failing G1
    there; a null-error is BLOCKED, never a verdict.
  - CONFIGURATIONS: their three declared A_Delta realizations
    {8, 6, 4}, nothing else.
  - CROSS-CHECK (reading, never a verdict-changer): fitted r_a vs
    their published MaleCNS values 0.548 / 0.437 / 0.391, band 0.1.
  - IN-CLOUD GATE (amended; the reproduce-theirs gate is
    unexecutable, absence finding recorded): synthetic recovery to
    1e-6 + 8/8 G1 on the synthetic + a can-fail uniform-counts
    control + the analytic identities, all before MaleCNS contact.
  - BLOCKED floors: runtime absent; AC-8 composition mismatch; empty
    EPG wedge; real-graph assignment degeneracy (tie_fraction >
    0.25); gate fail; null-error; no valid fit at ANY configuration
    on the REAL graph (closed as a measured recipe-transfer limit,
    never a fly statement).

BUILD-TIME OPERATIONALIZATIONS (dated 2026-10-31, pre-data-contact;
also recorded in killtest_design.md's build-time notes): exactness
floors FIT_RTOL_SYM 1e-6 (their intersections are exact by
construction; this tolerates float accumulation) and FIT_ATOL_MIRROR
1e-8; drive-check tolerance TOL_DRIVE 1e-9 (their A.31 first
inequality is IDENTICALLY zero on the branch, so strict signs would
fail exact arithmetic); the mirror fit runs at one canonical
placement (active EPG units {2,3,4,5} 0-based, axis between 3 and 4;
the recipe statistics are rotation-invariant); a zero-output Delta7
counts as a tie; seed amplitude sigma=1 (the attractor family is
scale-invariant); multiple valid symmetric candidates are all
reported and the smallest-residual one is used, flagged.

Exit codes: 0 = PASS, 1 = KILL, 3 = BLOCKED.

Run:    python scripts/arenas/cx_biswas_killtest.py
Output: results/arenas/cx_biswas_killtest.json (+ .log)
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

# --- frozen constants (registration + G1 bars verbatim) ----------------------
N_UNITS = 8
ACTIVE_SIZE = 4
A_DELTA_CONFIGS = (8, 6, 4)
# AC-B4: inactive Delta7 units sit AT the bump, mirror-symmetric about
# the canonical active-EPG axis (active EPG = {2,3,4,5} 0-based).
Z_INACTIVE = {8: (), 6: (3, 4), 4: (2, 3, 4, 5)}
CANONICAL_ACTIVE = (2, 3, 4, 5)

# Published MaleCNS r_a values (their p8). CROSS-CHECK ONLY -- these
# numbers enter nothing but the consistency reading (frozen).
PUBLISHED_RA = {8: 0.548, 6: 0.437, 4: 0.391}
RA_CONSISTENCY_BAND = 0.1

GAMMA_II_DEFAULT = 0.0            # their A_Delta=8 default
# their published residual-grid ranges (seed search, not validity)
GRID_GAMMA_EE = (0.0, 0.05, 100)
GRID_GAMMA_EIE = (-0.001, 0.0, 100)
GRID_GAMMA_II = (-0.05, 0.0, 100)

# G1 bars, verbatim from H-CX-CLASS3-COMPASS
RETENTION_MIN = 0.05
CIRCVAR_MAX = 0.6
ERR_MAX_DEG = 45.0
G1_MIN_PASS = 6
SIGMA_SEED = 1.0
T_DARK = 100.0                    # tau units; tau = 1
ODE_RTOL, ODE_ATOL = 1e-8, 1e-10
RUNAWAY_MAX = 1e6
Z_FP_ITERS = 100

# build-time floors (dated notes)
FIT_RTOL_SYM = 1e-6
FIT_ATOL_MIRROR = 1e-8
TOL_DRIVE = 1e-9
RA_SCAN_XATOL = 1e-10
RA_SCAN_POINTS = 2001

# AC-B5 tie rule
TIE_MARGIN = 0.98
TIE_BLOCK_FRACTION = 0.25

REWIRE_SEED_BASE = 4242
REWIRE_SEEDS = (0, 1, 2)

EXPECTED_COUNTS = {"EPG": 46, "PEN_a(PEN1)": 20, "PEN_b(PEN2)": 22,
                   "Delta7": 42, "PEG": 18}
RECIPE_TYPES = ("EPG", "Delta7")
RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
OUT_JSON = ROOT / "results/arenas/cx_biswas_killtest.json"
WEDGE_RE = re.compile(r"_([LR])(\d)")

UNIT_ANGLES_DEG = np.arange(N_UNITS) * 45.0
UNIT_ANGLES_RAD = np.deg2rad(UNIT_ANGLES_DEG)


# ---------------------------------------------------------------------------
# Their analytic branch (Appendix A; exact formulas, no choices)
# ---------------------------------------------------------------------------

def w_profile(r_a: float) -> np.ndarray:
    """(w1, w2, w3) on their viable branch: A.23, A.17, A.18."""
    w1 = (1.0 + r_a) / 2.0
    return np.array([w1, 1.0 - 2.0 * w1 ** 2, w1 * (4.0 * w1 ** 2 - 3.0)])


def bump_profile(mu: float, r_a: float) -> np.ndarray:
    """A.22 active-set profile (1-mu, r_s-mu r_a, r_s+mu r_a, 1+mu),
    r_s = r_a + 2 (A.24)."""
    r_s = r_a + 2.0
    return np.array([1.0 - mu, r_s - mu * r_a, r_s + mu * r_a, 1.0 + mu])


def mean_angle_a6(profile: np.ndarray) -> float:
    """Their A.6 linear average over the active set at encoded angles
    {-3pi/8, -pi/8, pi/8, 3pi/8} -- used only by the identity gate."""
    theta = np.array([-3, -1, 1, 3]) * np.pi / 8.0
    return float((theta * profile).sum() / profile.sum())


# ---------------------------------------------------------------------------
# Coarse-graining (their Methods, replicated verbatim)
# ---------------------------------------------------------------------------

def epg_unit_from_instance(name: str) -> int | None:
    """AC-B1: unit = (PB glomerulus digit - 1) mod 8, L/R merged.
    A global rotation of unit labels changes nothing downstream (the
    recipe statistics are rotation-invariant; G1 seeds all rotations)."""
    match = WEDGE_RE.search(name)
    if not match:
        return None
    return (int(match.group(2)) - 1) % N_UNITS


def assign_delta7_units(matrix_abs, epg_idx: np.ndarray,
                        epg_units: np.ndarray,
                        d7_idx: np.ndarray) -> dict[str, Any]:
    """Their recipe: each Delta7 goes to the unit of MAXIMAL CUMULATIVE
    OUTPUT of synapse counts to EPG grouped by wedge. AC-B5 tie rule:
    lowest index wins; top-two within 2% (ratio >= TIE_MARGIN) or an
    all-zero output row counts as a tie; tie_fraction is reported."""
    dense = np.asarray(matrix_abs[np.ix_(epg_idx, d7_idx)].todense()) \
        if hasattr(matrix_abs, "todense") else \
        np.asarray(matrix_abs)[np.ix_(epg_idx, d7_idx)]
    out_to_wedge = np.zeros((d7_idx.size, N_UNITS))
    for k in range(N_UNITS):
        rows = epg_units == k
        out_to_wedge[:, k] = dense[rows, :].sum(axis=0)
    units = out_to_wedge.argmax(axis=1)
    ties = 0
    for row, unit in zip(out_to_wedge, units):
        top = row[unit]
        if top <= 0:
            ties += 1
            continue
        rest = np.delete(row, unit)
        if rest.size and rest.max() >= TIE_MARGIN * top:
            ties += 1
    return {"units": units,
            "tie_fraction": float(ties / max(1, d7_idx.size)),
            "outputs": out_to_wedge}


def unit_count_matrix(matrix_abs, pre_idx: np.ndarray,
                      pre_units: np.ndarray, post_idx: np.ndarray,
                      post_units: np.ndarray) -> np.ndarray:
    """C_ij = mean over POSTSYNAPTIC neurons of unit i of the SUMMED
    counts from presynaptic neurons of unit j (their 'connections to
    every neuron summed per presynaptic wedge ... postsynaptic
    connectivity averaged per wedge'). W is [post, pre]."""
    dense = np.asarray(matrix_abs[np.ix_(post_idx, pre_idx)].todense()) \
        if hasattr(matrix_abs, "todense") else \
        np.asarray(matrix_abs)[np.ix_(post_idx, pre_idx)]
    summed = np.zeros((post_idx.size, N_UNITS))
    for j in range(N_UNITS):
        summed[:, j] = dense[:, pre_units == j].sum(axis=1)
    out = np.zeros((N_UNITS, N_UNITS))
    for i in range(N_UNITS):
        rows = post_units == i
        if not rows.any():
            raise ValueError(f"empty postsynaptic unit {i}")
        out[i] = summed[rows].mean(axis=0)
    return out


def circular_distance_matrix() -> np.ndarray:
    idx = np.arange(N_UNITS)
    d = np.abs(idx[:, None] - idx[None, :])
    return np.minimum(d, N_UNITS - d)


def distance_average(C: np.ndarray) -> np.ndarray:
    """5-vector c_d, d = 0 (self) .. 4 (opposite)."""
    D = circular_distance_matrix()
    return np.array([C[D == d].mean() for d in range(5)])


def circulant_from_profile(c: np.ndarray) -> np.ndarray:
    D = circular_distance_matrix()
    return c[D]


def mirror_permutation() -> np.ndarray:
    """Mirror about the canonical axis (between units 3 and 4):
    i* = 7 - i (their i + i* = N + 1, 1-based)."""
    return (N_UNITS - 1) - np.arange(N_UNITS)


def mirror_average(C: np.ndarray) -> np.ndarray:
    p = mirror_permutation()
    return 0.5 * (C + C[np.ix_(p, p)])


# ---------------------------------------------------------------------------
# Gamma fits (their procedures)
# ---------------------------------------------------------------------------

def effective_feedback(C_EI: np.ndarray, C_II: np.ndarray,
                       C_IE: np.ndarray, gamma_ii: float,
                       active_z: np.ndarray) -> np.ndarray:
    """C^EIE = C^EI (I - gamma^II C^II)^-1 C^IE on the ACTIVE z set
    (their C.65-C.67)."""
    az = np.asarray(active_z)
    core = np.linalg.inv(np.eye(az.size)
                         - gamma_ii * C_II[np.ix_(az, az)])
    return C_EI[:, az] @ core @ C_IE[az, :]


def fit_symmetric(c_EE: np.ndarray, c_EIE: np.ndarray) -> dict[str, Any]:
    """Their fully-symmetric procedure: scan r_a in [0,1] minimizing
    ||(Chat Chat^+ - I) w(r_a)||, Chat the 3x2 of (c^EE_d, c^EIE_d)
    d=1..3; normalize gammahat for the self-loop (C.76/C.85 algebra);
    gamma^EI = -gamma^IE = -sqrt(|gamma^EIE|)."""
    from scipy.optimize import minimize_scalar

    Chat = np.column_stack([c_EE[1:4], c_EIE[1:4]])

    def residual(ra: float) -> tuple[float, np.ndarray]:
        w = w_profile(ra)
        sol, *_ = np.linalg.lstsq(Chat, w, rcond=None)
        return float(np.linalg.norm(Chat @ sol - w)), sol

    # coarse scan, then refine every local minimum (their S3 shows
    # several intersections; only valid ones survive the inequalities)
    grid = np.linspace(0.0, 1.0, RA_SCAN_POINTS)
    vals = np.array([residual(ra)[0] for ra in grid])
    candidates = []
    for i in range(len(grid)):
        lo = max(0, i - 1)
        hi = min(len(grid) - 1, i + 1)
        if vals[i] <= vals[lo] and vals[i] <= vals[hi]:
            res = minimize_scalar(
                lambda ra: residual(ra)[0], method="bounded",
                bounds=(grid[lo], grid[hi]),
                options={"xatol": RA_SCAN_XATOL})
            candidates.append((float(res.x), float(res.fun)))
    records = []
    for ra, fun in sorted(candidates, key=lambda t: t[1]):
        w = w_profile(ra)
        rel = fun / np.linalg.norm(w)
        _, gammahat = residual(ra)
        record = evaluate_symmetric_candidate(ra, rel, gammahat,
                                              c_EE, c_EIE)
        records.append(record)
    valid = [r for r in records if r["valid"]]
    chosen = valid[0] if valid else (records[0] if records else None)
    return {"kind": "symmetric", "candidates": records,
            "n_valid": len(valid),
            "multiple_valid": len(valid) > 1,
            "chosen": chosen, "valid": bool(valid)}


def evaluate_symmetric_candidate(ra: float, rel_residual: float,
                                 gammahat: np.ndarray, c_EE: np.ndarray,
                                 c_EIE: np.ndarray) -> dict[str, Any]:
    """Their Table 1 + Table 2 conditions on one candidate."""
    checks: dict[str, bool] = {}
    checks["exact_intersection"] = bool(rel_residual <= FIT_RTOL_SYM)
    c0 = np.array([c_EE[0], c_EIE[0]])
    denom = 1.0 + float(c0 @ gammahat)
    checks["normalization_denominator_positive"] = denom > 0
    gamma = gammahat / denom if denom > 0 else np.full(2, np.nan)
    checks["gamma_ee_positive"] = bool(gamma[0] > 0)
    checks["gamma_eie_negative"] = bool(gamma[1] < 0)
    w1 = (1.0 + ra) / 2.0
    checks["w1_in_profile_range"] = bool(0.5 <= w1 < 1.0)  # A.26/A.27
    wbar4 = float(gammahat @ np.array([c_EE[4], c_EIE[4]]))
    checks["w4_bound_a32"] = bool(
        wbar4 <= -(8 * w1 ** 4 - 8 * w1 ** 2 + 1) + TOL_DRIVE)
    checks["w4_bound_a36"] = bool(wbar4 <= -(4 * w1 ** 2 - 3) + TOL_DRIVE)
    # z-state check (C.82, all 8 z active for A_Delta=8): with
    # gamma^II = 0 the effective feedforward is gamma^IE C^IE, all
    # counts nonnegative and gamma^IE > 0, so active-z drives are
    # nonnegative whenever each z unit receives ANY input from the
    # active EPGs; checked numerically by the caller on the full
    # blocks (needs C^IE, not just profiles) -- recorded there.
    return {"r_a": ra, "rel_residual": rel_residual,
            "gammahat": gammahat.tolist(),
            "gamma_ee": float(gamma[0]), "gamma_eie": float(gamma[1]),
            "gamma_ii": GAMMA_II_DEFAULT,
            "wbar4": wbar4, "checks": checks,
            "valid": all(checks.values())}


def mirror_params(Wb: np.ndarray) -> np.ndarray:
    """Read the six B.39 parameters (w1', w2', w3, w1'', w1, w2'')
    from the barred matrix at the canonical placement; mirror pairs
    averaged defensively."""
    a1, a2, a3, a4 = CANONICAL_ACTIVE
    w1p = 0.5 * (Wb[a1, a2] + Wb[a4, a3])
    w2p = 0.5 * (Wb[a1, a3] + Wb[a4, a2])
    w3 = 0.5 * (Wb[a1, a4] + Wb[a4, a1])
    w1pp = 0.5 * (Wb[a2, a1] + Wb[a3, a4])
    w1 = 0.5 * (Wb[a2, a3] + Wb[a3, a2])
    w2pp = 0.5 * (Wb[a2, a4] + Wb[a3, a1])
    return np.array([w1p, w2p, w3, w1pp, w1, w2pp])


def mirror_equations(params: np.ndarray) -> np.ndarray:
    """Residuals of their three equalities B.44, B.48, B.54."""
    w1p, w2p, w3, w1pp, w1, w2pp = params
    f1 = (1 - w3) * (1 - w1) - (w1p + w2p) * (w1pp + w2pp)
    f2 = (1 + w3) * (1 + w1) - (w1p - w2p) * (w1pp - w2pp)
    f3 = w2p ** 2 - w1p ** 2 - w2p - w3 * w1p
    return np.array([f1, f2, f3])


def mirror_barred(C_EE: np.ndarray, C_EIE: np.ndarray, g_ee: float,
                  g_eie: float) -> np.ndarray | None:
    """Their Eq (1)/C.85: Wbar_ij = Wtilde_ij / (1 - Wtilde_ii),
    diagonal zeroed; None where a denominator is nonpositive."""
    Wt = g_ee * C_EE + g_eie * C_EIE
    denom = 1.0 - np.diag(Wt)
    if (denom <= 0).any():
        return None
    Wb = Wt / denom[:, None]
    np.fill_diagonal(Wb, 0.0)
    return Wb


def fit_mirror(C_EE: np.ndarray, C_EI: np.ndarray, C_IE: np.ndarray,
               C_II: np.ndarray, a_delta: int) -> dict[str, Any]:
    """Their mirror-symmetric procedure: 100^3 residual grid over the
    published gamma ranges, then Levenberg-Marquardt on B.44/B.48/B.54."""
    from scipy.optimize import least_squares

    active_z = np.array([u for u in range(N_UNITS)
                         if u not in Z_INACTIVE[a_delta]])

    def equations(x: np.ndarray) -> np.ndarray:
        g_ee, g_eie, g_ii = x
        try:
            C_EIE = effective_feedback(C_EI, C_II, C_IE, g_ii, active_z)
        except np.linalg.LinAlgError:
            return np.full(3, 1e6)
        Wb = mirror_barred(C_EE, C_EIE, g_ee, g_eie)
        if Wb is None:
            return np.full(3, 1e6)
        return mirror_equations(mirror_params(Wb))

    # grid seed: only 6 off-diagonal + 2 diagonal entries matter
    a1, a2, a3, a4 = CANONICAL_ACTIVE
    pos = [(a1, a2), (a1, a3), (a1, a4), (a2, a1), (a2, a3), (a2, a4)]
    ee = np.linspace(*GRID_GAMMA_EE[:2], GRID_GAMMA_EE[2])[:, None]
    eie = np.linspace(*GRID_GAMMA_EIE[:2], GRID_GAMMA_EIE[2])[None, :]
    best = (np.inf, None)
    for g_ii in np.linspace(*GRID_GAMMA_II[:2], GRID_GAMMA_II[2]):
        try:
            C_EIE = effective_feedback(C_EI, C_II, C_IE, g_ii, active_z)
        except np.linalg.LinAlgError:
            continue
        d_ee = np.diag(C_EE)[[a1, a2]]
        d_eie = np.diag(C_EIE)[[a1, a2]]
        den1 = 1.0 - ee * d_ee[0] - eie * d_eie[0]
        den2 = 1.0 - ee * d_ee[1] - eie * d_eie[1]
        bad = (den1 <= 0) | (den2 <= 0)
        with np.errstate(divide="ignore", invalid="ignore"):
            entries = []
            for (i, j), den in zip(pos, [den1] * 3 + [den2] * 3):
                entries.append((ee * C_EE[i, j] + eie * C_EIE[i, j])
                               / den)
            w1p, w2p, w3, w1pp, w1, w2pp = entries
            f1 = (1 - w3) * (1 - w1) - (w1p + w2p) * (w1pp + w2pp)
            f2 = (1 + w3) * (1 + w1) - (w1p - w2p) * (w1pp - w2pp)
            f3 = w2p ** 2 - w1p ** 2 - w2p - w3 * w1p
            total = f1 ** 2 + f2 ** 2 + f3 ** 2
        total[bad | ~np.isfinite(total)] = np.inf
        k = int(np.argmin(total))
        value = float(total.flat[k])
        if value < best[0]:
            i, j = np.unravel_index(k, total.shape)
            best = (value, np.array([float(ee[i, 0]),
                                     float(eie[0, j]), float(g_ii)]))
    if best[1] is None:
        return {"kind": "mirror", "a_delta": a_delta, "valid": False,
                "blocked": "no feasible grid point (denominators)"}
    sol = least_squares(equations, best[1], method="lm",
                        xtol=1e-15, ftol=1e-15, gtol=1e-15)
    g_ee, g_eie, g_ii = (float(v) for v in sol.x)
    f = equations(sol.x)
    checks: dict[str, bool] = {
        "equations_solved": bool(np.abs(f).max() <= FIT_ATOL_MIRROR),
        "gamma_ee_positive": g_ee > 0,
        "gamma_eie_negative": g_eie < 0,
        "gamma_ii_nonpositive": g_ii <= 0,
    }
    record: dict[str, Any] = {"kind": "mirror", "a_delta": a_delta,
                              "gamma_ee": g_ee, "gamma_eie": g_eie,
                              "gamma_ii": g_ii,
                              "max_abs_residual": float(np.abs(f).max()),
                              "grid_seed": best[1].tolist(),
                              "checks": checks}
    C_EIE = effective_feedback(C_EI, C_II, C_IE, g_ii, active_z)
    Wb = mirror_barred(C_EE, C_EIE, g_ee, g_eie)
    if Wb is None:
        checks["barred_denominators_positive"] = False
        record["valid"] = False
        return record
    checks["barred_denominators_positive"] = True
    w1p, w2p, w3, w1pp, w1, w2pp = mirror_params(Wb)
    checks["stability_b50"] = bool(abs(w1 + w3) < 2)        # B.50
    r_s = (1 - w3) / (w1p + w2p) if (w1p + w2p) != 0 else np.nan
    r_a = (1 + w3) / (w1p - w2p) if (w1p - w2p) != 0 else np.nan
    checks["r_a_positive_b55"] = bool(np.isfinite(r_a) and r_a > 0)
    checks["r_s_positive_b53"] = bool(np.isfinite(r_s) and r_s > 0)
    record.update({"r_a": float(r_a), "r_s": float(r_s),
                   "six_params": [float(v) for v in
                                  (w1p, w2p, w3, w1pp, w1, w2pp)]})
    if all(checks.values()):
        drives = drive_checks(Wb, feedforward_z(C_IE, C_II, g_eie, g_ii,
                                                active_z),
                              r_a, Z_INACTIVE[a_delta])
        checks.update(drives)
    record["checks"] = checks
    record["valid"] = all(checks.values())
    return record


def feedforward_z(C_IE: np.ndarray, C_II: np.ndarray, g_eie: float,
                  g_ii: float, active_z: np.ndarray) -> np.ndarray:
    """Effective feedforward from active EPG units to every z unit
    (their C.86 restricted construction); rows = z units, cols = the
    four canonical active EPG units. gamma^IE = sqrt(|gamma^EIE|)."""
    g_ie = float(np.sqrt(abs(g_eie)))
    az = np.asarray(active_z)
    core = np.linalg.inv(np.eye(az.size) - g_ii * C_II[np.ix_(az, az)])
    act = list(CANONICAL_ACTIVE)
    direct = g_ie * C_IE[:, act]
    indirect = g_ii * g_ie * (C_II[:, az] @ core @ C_IE[np.ix_(az, act)])
    return direct + indirect


def drive_checks(Wb: np.ndarray, u_z: np.ndarray, r_a: float,
                 z_inactive: tuple[int, ...]) -> dict[str, bool]:
    """Numeric sign checks at the extreme profiles mu = +/-1 (their
    stated shortcut for A.28-A.36 / B.60-B.63 / C.81-C.82). Their
    A.31 first inequality is IDENTICALLY zero on the branch, hence
    the tolerance."""
    act = list(CANONICAL_ACTIVE)
    inactive_epg = [u for u in range(N_UNITS) if u not in act]
    ok_epg, ok_z_active, ok_z_inactive = True, True, True
    for mu in (-1.0, 1.0):
        y = bump_profile(mu, r_a)
        for o in inactive_epg:
            if float(Wb[o, act] @ y) > TOL_DRIVE:
                ok_epg = False
        for k in range(N_UNITS):
            drive = float(u_z[k] @ y)
            if k in z_inactive:
                if drive > TOL_DRIVE:
                    ok_z_inactive = False
            elif drive < -TOL_DRIVE:
                ok_z_active = False
    return {"inactive_epg_drives_nonpositive": ok_epg,
            "active_z_drives_nonnegative": ok_z_active,
            "inactive_z_drives_nonpositive": ok_z_inactive}


# ---------------------------------------------------------------------------
# G1 simulation (the frozen bars mapped to the 8-unit rate vector)
# ---------------------------------------------------------------------------

def pva_deg(y: np.ndarray) -> tuple[float, float]:
    """(PVA angle deg, circular variance) of a nonnegative profile."""
    total = float(y.sum())
    if total <= 0:
        return float("nan"), 1.0
    vec = complex((y * np.cos(UNIT_ANGLES_RAD)).sum(),
                  (y * np.sin(UNIT_ANGLES_RAD)).sum())
    return float(np.degrees(np.angle(vec)) % 360.0), \
        float(1.0 - abs(vec) / total)


def circ_err_deg(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def simulate_g1(W_EE: np.ndarray, W_EI: np.ndarray, W_IE: np.ndarray,
                W_II: np.ndarray, r_a: float) -> dict[str, Any]:
    """8 seeds = the mu=0 rotations of the active-4 set, 45 deg apart
    (A.25); dark integration to T_DARK; bars verbatim. The simulation
    never masks units."""
    from scipy.integrate import solve_ivp

    r_s = r_a + 2.0

    def rhs(_t, s):
        y, z = s[:N_UNITS], s[N_UNITS:]
        dy = -y + np.maximum(0.0, W_EE @ y + W_EI @ z)
        dz = -z + np.maximum(0.0, W_IE @ y + W_II @ z)
        return np.concatenate([dy, dz])

    rows = []
    for k in range(N_UNITS):
        active = [(k + m) % N_UNITS for m in range(ACTIVE_SIZE)]
        y0 = np.zeros(N_UNITS)
        y0[active] = SIGMA_SEED * np.array([1.0, r_s, r_s, 1.0])
        z0 = np.zeros(N_UNITS)
        for _ in range(Z_FP_ITERS):
            z0 = np.maximum(0.0, W_IE @ y0 + W_II @ z0)
        seed_pva, _ = pva_deg(y0)
        row: dict[str, Any] = {"seed_pva_deg": seed_pva}
        try:
            sol = solve_ivp(rhs, (0.0, T_DARK),
                            np.concatenate([y0, z0]), method="RK45",
                            rtol=ODE_RTOL, atol=ODE_ATOL,
                            t_eval=[T_DARK])
            y_final = sol.y[:N_UNITS, -1]
        except Exception as exc:                    # solver blow-up
            row.update({"error": repr(exc), "pass": False})
            rows.append(row)
            continue
        finite = bool(np.isfinite(y_final).all()
                      and np.abs(y_final).max() <= RUNAWAY_MAX)
        retention = float(y_final.sum() / y0.sum()) if finite else 0.0
        final_pva, circvar = pva_deg(np.maximum(y_final, 0.0)) \
            if finite else (float("nan"), 1.0)
        err = circ_err_deg(final_pva, seed_pva) \
            if np.isfinite(final_pva) else float("nan")
        row.update({
            "finite": finite, "retention": retention,
            "circvar": circvar, "final_pva_deg": final_pva,
            "err_deg": err,
            "pass": bool(finite and retention >= RETENTION_MIN
                         and circvar <= CIRCVAR_MAX
                         and np.isfinite(err) and err <= ERR_MAX_DEG)})
        rows.append(row)
    n_pass = sum(1 for r in rows if r["pass"])
    return {"rows": rows, "n_pass": n_pass,
            "pass": n_pass >= G1_MIN_PASS}


# ---------------------------------------------------------------------------
# Per-graph recipe (real and rewired alike -- the full pipeline)
# ---------------------------------------------------------------------------

def run_configuration(blocks: dict[str, np.ndarray],
                      a_delta: int) -> dict[str, Any]:
    """Fit + G1 for one declared A_Delta realization, given the raw
    8x8 unit-count blocks (C_EE, C_EI, C_IE, C_II; W is [post, pre],
    so C_EI = Delta7 -> EPG counts)."""
    C_EE, C_EI = blocks["C_EE"], blocks["C_EI"]
    C_IE, C_II = blocks["C_IE"], blocks["C_II"]
    if a_delta == 8:
        C_EIE = effective_feedback(C_EI, C_II, C_IE, GAMMA_II_DEFAULT,
                                   np.arange(N_UNITS))
        fit = fit_symmetric(distance_average(C_EE),
                            distance_average(C_EIE))
        sim_EE = circulant_from_profile(distance_average(C_EE))
        sim_EI = circulant_from_profile(distance_average(C_EI))
        sim_IE = circulant_from_profile(distance_average(C_IE))
        sim_II = circulant_from_profile(distance_average(C_II))
        chosen = fit["chosen"]
        if not fit["valid"] or chosen is None:
            return {"a_delta": a_delta, "fit": fit, "valid_fit": False,
                    "g1": None, "pass": False}
        g_ee, g_eie = chosen["gamma_ee"], chosen["gamma_eie"]
        g_ii, r_a = GAMMA_II_DEFAULT, chosen["r_a"]
        # the symmetric z-state check (C.82), numeric on the full blocks
        u_z = feedforward_z(sim_IE, sim_II, g_eie, g_ii,
                            np.arange(N_UNITS))
        zcheck = drive_checks(np.zeros((N_UNITS, N_UNITS)), u_z, r_a,
                              Z_INACTIVE[8])
        chosen["checks"]["active_z_drives_nonnegative"] = \
            zcheck["active_z_drives_nonnegative"]
        if not zcheck["active_z_drives_nonnegative"]:
            chosen["valid"] = False
            fit["valid"] = False
            return {"a_delta": a_delta, "fit": fit, "valid_fit": False,
                    "g1": None, "pass": False}
    else:
        sym = {k: mirror_average(v) for k, v in blocks.items()}
        fit = fit_mirror(sym["C_EE"], sym["C_EI"], sym["C_IE"],
                         sym["C_II"], a_delta)
        if not fit.get("valid"):
            return {"a_delta": a_delta, "fit": fit, "valid_fit": False,
                    "g1": None, "pass": False}
        sim_EE, sim_EI = sym["C_EE"], sym["C_EI"]
        sim_IE, sim_II = sym["C_IE"], sym["C_II"]
        g_ee, g_eie = fit["gamma_ee"], fit["gamma_eie"]
        g_ii, r_a = fit["gamma_ii"], fit["r_a"]
    g_ie = float(np.sqrt(abs(g_eie)))
    g_ei = -g_ie
    g1 = simulate_g1(g_ee * sim_EE, g_ei * sim_EI, g_ie * sim_IE,
                     g_ii * sim_II, r_a)
    record = {"a_delta": a_delta, "fit": fit, "valid_fit": True,
              "r_a": float(r_a), "g1": g1,
              "pass": bool(g1["pass"])}
    return record


def unit_blocks(matrix_abs, epg_idx: np.ndarray, epg_units: np.ndarray,
                d7_idx: np.ndarray, d7_units: np.ndarray) \
        -> dict[str, np.ndarray]:
    return {
        "C_EE": unit_count_matrix(matrix_abs, epg_idx, epg_units,
                                  epg_idx, epg_units),
        "C_EI": unit_count_matrix(matrix_abs, d7_idx, d7_units,
                                  epg_idx, epg_units),
        "C_IE": unit_count_matrix(matrix_abs, epg_idx, epg_units,
                                  d7_idx, d7_units),
        "C_II": unit_count_matrix(matrix_abs, d7_idx, d7_units,
                                  d7_idx, d7_units),
    }


def run_graph(matrix_abs, epg_idx: np.ndarray, epg_units: np.ndarray,
              d7_idx: np.ndarray) -> dict[str, Any]:
    """The FULL recipe on one graph: Delta7 assignment re-derived from
    the graph (the registration's per-rewire rule), blocks, three
    configurations."""
    assignment = assign_delta7_units(matrix_abs, epg_idx, epg_units,
                                     d7_idx)
    empty = [k for k in range(N_UNITS)
             if not (assignment["units"] == k).any()]
    if empty:
        # the coarse-graining is undefined: on a REWIRE this counts as
        # no-valid-fit everywhere (their inequalities define existence;
        # destroyed assignment structure is the null doing its job);
        # the REAL graph hits a BLOCKED floor in main() instead.
        configs = {a: {"a_delta": a, "valid_fit": False, "pass": False,
                       "g1": None,
                       "fit": {"blocked":
                               f"empty Delta7 unit(s) {empty}"}}
                   for a in A_DELTA_CONFIGS}
        return {"tie_fraction": assignment["tie_fraction"],
                "empty_z_units": empty, "configs": configs}
    blocks = unit_blocks(matrix_abs, epg_idx, epg_units, d7_idx,
                         assignment["units"])
    configs = {}
    for a_delta in A_DELTA_CONFIGS:
        configs[a_delta] = run_configuration(blocks, a_delta)
    return {"tie_fraction": assignment["tie_fraction"],
            "configs": configs}


def assemble_verdict(real: dict[str, Any],
                     nulls: list[dict[str, Any]]) -> str:
    """Frozen: PASS iff real passes >= 1 configuration and all 3
    rewires fail at every real-passing configuration (no valid fit =
    fail); KILL iff real fails G1 at every valid-fit configuration or
    a rewire passes where real passes; BLOCKED iff a null errored, a
    null is missing, or real has no valid fit anywhere (the measured
    recipe-transfer limit)."""
    if real.get("error"):
        return "BLOCKED"
    configs = real["configs"]
    real_passing = [a for a, c in configs.items() if c["pass"]]
    any_valid = any(c["valid_fit"] for c in configs.values())
    if any(n.get("error") for n in nulls):
        return "BLOCKED"
    if not real_passing:
        return "KILL" if any_valid else "BLOCKED"
    if len(nulls) != len(REWIRE_SEEDS):
        return "BLOCKED"
    for a in real_passing:
        for null in nulls:
            entry = null["configs"].get(a)
            if entry is None:
                return "BLOCKED"
            if entry["pass"]:
                return "KILL"
    return "PASS"


# ---------------------------------------------------------------------------
# The amended in-cloud validation gate (synthetic; runs before data)
# ---------------------------------------------------------------------------

SYNTH_RA = 0.5
SYNTH_GAMMA_EE = 0.01
SYNTH_GAMMA_EIE = -2.0e-4
SYNTH_W4 = -0.2
SYNTH_EI_SCALE = 50.0


def synthetic_blocks() -> dict[str, Any]:
    """Counts constructed from the known ground truth (SYNTH_*):
    diagonal C^EI so C^EIE = s C^IE factors exactly; nonzero unit
    self-loops exercise the C.76/C.85 normalization."""
    w = np.append(w_profile(SYNTH_RA), SYNTH_W4)       # d = 1..4
    c_ee = np.array([20.0, 70.0, 30.0, 10.0, 5.0])      # d = 0..4
    c_eie0 = 500.0
    denom = 1.0 - SYNTH_GAMMA_EE * c_ee[0] - SYNTH_GAMMA_EIE * c_eie0
    gammahat = np.array([SYNTH_GAMMA_EE, SYNTH_GAMMA_EIE]) / denom
    c_eie = np.empty(5)
    c_eie[0] = c_eie0
    for d in range(1, 5):
        c_eie[d] = (gammahat[0] * c_ee[d] - w[d - 1]) / (-gammahat[1])
    if (c_eie < 0).any():
        raise AssertionError("synthetic construction must be a count")
    C_EE = circulant_from_profile(c_ee)
    C_IE = circulant_from_profile(c_eie / SYNTH_EI_SCALE)
    C_EI = SYNTH_EI_SCALE * np.eye(N_UNITS)
    C_II = np.full((N_UNITS, N_UNITS), 10.0)
    return {"C_EE": C_EE, "C_EI": C_EI, "C_IE": C_IE, "C_II": C_II,
            "r_a": SYNTH_RA, "gamma_ee": SYNTH_GAMMA_EE,
            "gamma_eie": SYNTH_GAMMA_EIE}


def validate_gate() -> dict[str, Any]:
    """(i) synthetic recovery to 1e-6; (ii) 8/8 G1 on the synthetic;
    (iii) uniform counts yield no valid fit; (iv) analytic identities."""
    record: dict[str, Any] = {}
    synth = synthetic_blocks()
    result = run_configuration(synth, 8)
    chosen = result["fit"]["chosen"] if result["fit"]["valid"] else None
    record["recovery"] = {
        "valid_fit": result["valid_fit"],
        "r_a": None if chosen is None else chosen["r_a"],
        "gamma_ee": None if chosen is None else chosen["gamma_ee"],
        "gamma_eie": None if chosen is None else chosen["gamma_eie"],
    }
    ok_recovery = (
        result["valid_fit"] and chosen is not None
        and abs(chosen["r_a"] - synth["r_a"]) <= 1e-6
        and abs(chosen["gamma_ee"] - synth["gamma_ee"])
        <= 1e-6 * abs(synth["gamma_ee"])
        and abs(chosen["gamma_eie"] - synth["gamma_eie"])
        <= 1e-6 * abs(synth["gamma_eie"]))
    record["recovery"]["pass"] = bool(ok_recovery)
    record["g1_synthetic"] = {
        "n_pass": 0 if result["g1"] is None else result["g1"]["n_pass"]}
    ok_g1 = result["g1"] is not None and result["g1"]["n_pass"] == 8
    record["g1_synthetic"]["pass"] = bool(ok_g1)
    uniform = {"C_EE": np.full((8, 8), 10.0),
               "C_EI": np.full((8, 8), 10.0),
               "C_IE": np.full((8, 8), 10.0),
               "C_II": np.full((8, 8), 10.0)}
    flat = run_configuration(uniform, 8)
    record["can_fail"] = {"uniform_valid_fit": flat["valid_fit"],
                          "pass": not flat["valid_fit"]}
    ids = []
    for ra in (0.1, 0.5, 0.548, 0.9):
        w1, w2, w3 = w_profile(ra)
        ids.append(abs(w2 - (1 - 2 * w1 ** 2)) < 1e-12)
        ids.append(abs(w3 - w1 * (4 * w1 ** 2 - 3)) < 1e-12)
        ids.append(abs((2 * w1 + 1) - (2 * w1 - 1) - 2.0) < 1e-12)
        for mu in (-1.0, -0.3, 0.0, 0.7, 1.0):
            ids.append(abs(mean_angle_a6(bump_profile(mu, ra))
                           - mu * np.pi / 8) < 1e-12)
    # mirror equalities reduce to the symmetric ones when primes equal
    # (their B.49 remark): on the exact branch the residuals vanish
    for ra in (0.3, 0.5):
        w1, w2, w3 = w_profile(ra)
        params = np.array([w1, w2, w3, w1, w1, w2])
        ids.append(bool(np.abs(mirror_equations(params)[:2]).max()
                        < 1e-12))
    record["identities"] = {"pass": bool(all(ids)), "n": len(ids)}
    record["pass"] = bool(ok_recovery and ok_g1
                          and record["can_fail"]["pass"]
                          and record["identities"]["pass"])
    return record


# ---------------------------------------------------------------------------
# Data-gated assembly (local host only)
# ---------------------------------------------------------------------------

def check_prerequisites() -> list[str]:
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    for mod in ("scipy",):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-CX-BISWAS-FITTED kill test (data-gated)")
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites()
    if missing:
        print("BLOCKED -- the kill test cannot run here. Missing:")
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
    gate = validate_gate()
    log(f"in-cloud gate: pass={gate['pass']} "
        f"(recovery {gate['recovery']['pass']}, synthetic G1 "
        f"{gate['g1_synthetic']['n_pass']}/8, can-fail "
        f"{gate['can_fail']['pass']}, identities "
        f"{gate['identities']['pass']})")
    if not gate["pass"]:
        log("BLOCKED: the gate fails -- invalid instrument, nothing "
            "claimed")
        return 3

    from flygi.connectome.nulls import degree_preserving_rewire
    from flygi.connectome.subcircuit import extract_subcircuit, select_nodes

    indices = select_nodes(RUNTIME_DIR,
                           type_patterns=("EPG", "PEN_a*", "PEN_b*",
                                          "Delta7", "PEG"))
    sub = extract_subcircuit(RUNTIME_DIR, indices)
    counts = {t: int((sub.types == t).sum()) for t in EXPECTED_COUNTS}
    log(f"subcircuit: {sub.node_count} nodes, composition {counts}")
    if counts != EXPECTED_COUNTS:
        log(f"BLOCKED: composition deviates from {EXPECTED_COUNTS}")
        return 3

    types = sub.types.astype("U")
    keep = np.flatnonzero((types == "EPG") | (types == "Delta7"))
    matrix = sub.matrix[np.ix_(keep, keep)].tocsr()
    types = types[keep]
    instances = sub.instances[keep].astype("U")
    epg_idx = np.flatnonzero(types == "EPG")
    d7_idx = np.flatnonzero(types == "Delta7")

    units, labelled = [], []
    for i in epg_idx:
        unit = epg_unit_from_instance(instances[i])
        if unit is not None:
            units.append(unit)
            labelled.append(i)
    epg_idx = np.asarray(labelled)
    epg_units = np.asarray(units)
    log(f"EPG labelled {epg_idx.size}/{(types == 'EPG').sum()}, "
        f"Delta7 {d7_idx.size}")
    wedge_sizes = [int((epg_units == k).sum()) for k in range(N_UNITS)]
    log(f"EPG wedge sizes: {wedge_sizes}")
    if min(wedge_sizes) == 0:
        log("BLOCKED: an EPG wedge is empty -- coarse-graining "
            "undefined")
        return 3

    abs_real = abs(matrix)
    real: dict[str, Any] = {}
    try:
        real = run_graph(abs_real, epg_idx, epg_units, d7_idx)
    except Exception as exc:
        real = {"error": repr(exc)}
        log(f"BLOCKED: real-graph recipe raised {exc!r}")
    if not real.get("error") and real.get("empty_z_units"):
        log(f"BLOCKED: empty Delta7 unit(s) {real['empty_z_units']} "
            "on the real graph -- coarse-graining undefined")
        real["error"] = "empty Delta7 unit(s) on the real graph"
    if not real.get("error") and real["tie_fraction"] > TIE_BLOCK_FRACTION:
        log(f"BLOCKED: Delta7 assignment degenerate on the real graph "
            f"(tie_fraction {real['tie_fraction']:.3f} > "
            f"{TIE_BLOCK_FRACTION})")
        real["error"] = "assignment degeneracy floor"
    cross = {}
    if not real.get("error"):
        for a_delta, entry in real["configs"].items():
            line = (f"real A_Delta={a_delta}: valid_fit="
                    f"{entry['valid_fit']}")
            if entry["valid_fit"]:
                delta = entry["r_a"] - PUBLISHED_RA[a_delta]
                cross[a_delta] = {
                    "fitted_ra": entry["r_a"],
                    "published_ra": PUBLISHED_RA[a_delta],
                    "delta": delta,
                    "consistent": bool(abs(delta)
                                       <= RA_CONSISTENCY_BAND)}
                line += (f" r_a={entry['r_a']:.4f} (published "
                         f"{PUBLISHED_RA[a_delta]}, delta "
                         f"{delta:+.4f}) G1 {entry['g1']['n_pass']}/8")
            log(line)

    nulls = []
    for k in REWIRE_SEEDS:
        seed = REWIRE_SEED_BASE + k
        try:
            rewired, _stats = degree_preserving_rewire(matrix, seed=seed)
            record = run_graph(abs(rewired), epg_idx, epg_units, d7_idx)
            record["seed"] = seed
        except Exception as exc:
            record = {"seed": seed, "error": repr(exc)}
            log(f"null seed {seed}: ERROR {exc!r}")
        if not record.get("error"):
            summary = {a: (c["valid_fit"], c["pass"])
                       for a, c in record["configs"].items()}
            log(f"null seed {seed}: tie_fraction "
                f"{record['tie_fraction']:.3f} configs {summary}")
        nulls.append(record)

    verdict = assemble_verdict(real, nulls)
    record = {"hypothesis": "H-CX-BISWAS-FITTED",
              "gate": gate, "real": real, "nulls": nulls,
              "ra_cross_check": cross,
              "g2": {"decisional": False,
                     "reason": "their model has no rotation input "
                               "(frozen non-decisional)"},
              "verdict": verdict,
              "elapsed_s": round(time.time() - started, 1)}
    args.output.write_text(json.dumps(record, indent=2, default=float))
    log(json.dumps({k: record[k] for k in
                    ("ra_cross_check", "verdict", "elapsed_s")},
                   indent=2, default=float))
    log(f"VERDICT: {verdict}")
    handle.close()
    return {"PASS": 0, "KILL": 1, "BLOCKED": 3}[verdict]


if __name__ == "__main__":
    sys.exit(main())
