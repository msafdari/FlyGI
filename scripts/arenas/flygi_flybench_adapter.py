"""FlyGI -> flybench simulator adapter (Task 3 kill test).

PREREGISTRATION: docs/arenas/task3_flybench/killtest_design.md +
EXPERIMENTS.yaml H-FLYGI-FLYBENCH-ADAPTER (2026-10-01, frozen before
this file existed). This module is PLUMBING ONLY, and everything it
does is declared there:

  - flygi.dynamics.spiking.SpikingNetwork runs UNMODIFIED; this file
    may not alter the engine's dynamics in any way.
  - Weight bridge: flybench's connectome.W is CSR rows=pre, signed
    synapse counts; our engine wants W[post, pre] -> transpose. Unit
    bridge DERIVED (unit analysis, not tuning):
        w_scale = w_syn_mv * gain / tau_m_ms
    because their per-spike kick w = w_syn*gain*count enters the
    membrane as integral(g/tau_m)dt = w*tau_syn/tau_m, while ours
    D = w_scale*count enters as integral(i)dt = D*tau_syn.
  - Constants: the Shiu 2024 set carried by their LIFParams, mapped
    onto our TypeParams default (shared published anchor, not a fit).
    dt = 0.5 ms (our engine default; theirs 0.1 -- declared
    difference). No axonal delay line in our engine (theirs 1.8 ms);
    effective one-step delay, declared difference.
  - Stimulus bridge: their stimuli are Poisson FORCED spikes; the
    adapter samples the same events (np RNG from params.seed, fresh
    per run -> determinism) and injects a one-step current pulse
    (v_th - v_rest)/dt + 1.0 so the spike happens through the engine's
    own threshold (refractory honoured as their forced path honours
    it). DECLARED LIMIT, stated in the registration: a driven neuron
    held far below rest by inhibition may not cross; their forced path
    would fire it regardless.
  - capabilities = {"can_silence"}: silencing arrives as zeroed
    outgoing rows in the handed connectome; we read W from it, so it
    holds structurally.

Run (from the FlyGI repo root, flybench installed):
    PYTHONPATH=src:scripts/arenas flybench verify-adapter \
        flygi_flybench_adapter:FlyGIAdapter -c toy
    PYTHONPATH=src:scripts/arenas flybench run -c toy \
        --simulator flygi_flybench_adapter:FlyGIAdapter
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# flybench's CLI imports this module bare; make flygi importable too.
_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from flybench.sim import LIFParams, SimResult  # noqa: E402
from flygi.dynamics.spiking import (  # noqa: E402
    ParameterTable,
    SpikingNetwork,
    TypeParams,
)

DT_MS = 0.5   # our engine default; declared in the registration


class FlyGIAdapter:
    """flybench Simulator contract over the unmodified class-2 engine."""

    capabilities: frozenset = frozenset({"can_silence"})

    def __init__(self, connectome, params: LIFParams | None = None):
        self.c = connectome
        self.p = params or LIFParams()
        p = self.p
        # Declared unit bridge (registration): w_scale = w_syn*gain/tau_m.
        w_scale = p.w_syn_mv * p.gain / p.tau_m_ms
        table = ParameterTable(
            default=TypeParams(
                tau_m_ms=p.tau_m_ms,
                v_thresh=p.v_th_mv,
                provenance=(
                    "Shiu 2024 constants via flybench LIFParams "
                    "(shared published anchor; killtest_design.md)"
                ),
                tau_syn_ms=p.tau_syn_ms,
                v_rest=p.v_rest_mv,
                v_reset=p.v_reset_mv,
                refractory_ms=p.t_ref_ms,
                graded=False,
            ),
        )
        # The toy carries no APL/CT1-class labels, so the graded mask is
        # empty here by construction (declared); a uniform type vector
        # resolves everything to the default row.
        types = np.full(connectome.n, "neuron", dtype="U16")
        self.net = SpikingNetwork(
            connectome.W.T.tocsr(),
            types,
            table,
            dt_ms=DT_MS,
            w_scale=w_scale,
            seed=p.seed,
        )
        self._spiking = ~self.net.params["graded"]
        # One-step suprathreshold pulse (frozen formula, registration).
        self._pulse = (p.v_th_mv - p.v_rest_mv) / DT_MS + 1.0

    def run(self, duration_ms: float, stimuli=None) -> SimResult:
        net = self.net
        net.reset()
        rng = np.random.default_rng(self.p.seed)
        stimuli = stimuli or []
        n = self.c.n
        n_steps = int(round(duration_ms / DT_MS))
        per_ms = DT_MS / 1000.0
        stim = [
            (np.asarray(s.neurons, dtype=np.int32), s.rate_hz * per_ms,
             s.t_start_ms, s.t_end_ms, s)
            for s in stimuli
            if len(s.neurons)
        ]
        times: list[np.ndarray] = []
        ids: list[np.ndarray] = []
        external = np.zeros(n, dtype=np.float64)
        for k in range(n_steps):
            t_now = k * DT_MS          # window test at step start (as theirs)
            external[:] = 0.0
            any_event = False
            for neurons, prob, t0, t1, s in stim:
                if not (t0 <= t_now < t1):
                    continue
                if s.rate_series_hz is not None:
                    events = neurons[
                        rng.random(neurons.size) < s.rates_at(t_now) * per_ms
                    ]
                elif s.rate_end_hz is not None:
                    events = neurons[
                        rng.random(neurons.size) < s.rate_at(t_now) * per_ms
                    ]
                else:
                    events = neurons[rng.random(neurons.size) < prob]
                if events.size:
                    external[events] += self._pulse
                    any_event = True
            output = net.step(external if any_event else None)
            fired = np.flatnonzero((output > 0) & self._spiking)
            if fired.size:
                # spike timestamp = end of the step, as the reference stamps
                times.append(np.full(fired.size, (k + 1) * DT_MS,
                                     dtype=np.float32))
                ids.append(fired.astype(np.int32))
        return SimResult(
            spike_times_ms=(np.concatenate(times) if times
                            else np.empty(0, dtype=np.float32)),
            spike_neurons=(np.concatenate(ids) if ids
                           else np.empty(0, dtype=np.int32)),
            duration_ms=float(n_steps * DT_MS),
            n=n,
        )


# ===========================================================================
# CALIBRATED ADAPTER -- H-FLYGI-FLYBENCH-CALIBRATED
# (docs/arenas/task3_flybench/calibrated_design.md, registered 2026-10-02
# BEFORE this code existed; the engine below stays UNMODIFIED -- everything
# here is composition: parameter tables, index-level post-resolution, and a
# calibration that edits the engine's declared parameter arrays.)
# ===========================================================================

import hashlib
import json as _json
import os as _os
import tempfile as _tempfile
from pathlib import Path as _Path

# --- per-type membrane taus (design ingredient 1) ---------------------------
# Fast/slow CLASS assignments ESTABLISHED (Arenz 2017; Behnia 2014; Borst
# 2025); the milliseconds are the fc2 table VERBATIM (fc2_visual_ds.py
# FAST_TAUS). ASSUMPTION: tau_slow = 150 ms for L3/Mi4/Mi9 and Tm9 = 200 ms
# (the dossier's 200:150 anchor) -- fc2 swept 100-300; a single value had to
# be chosen and 150 is the doc's anchor, not a new fit.
CALIBRATED_TAUS_MS = {
    "L1": 15.0, "L2": 15.0, "L4": 20.0, "L5": 25.0, "Mi1": 20.0,
    "Tm3": 12.0, "Tm1": 20.0, "Tm2": 12.0, "Tm4": 20.0,
    "T4a": 20.0, "T4b": 20.0, "T4c": 20.0, "T4d": 20.0,
    "T5a": 20.0, "T5b": 20.0, "T5c": 20.0, "T5d": 20.0,
    "L3": 150.0, "Mi4": 150.0, "Mi9": 150.0, "Tm9": 200.0,
}

# --- graded units (design ingredient 2) -------------------------------------
# APL and CT1: ESTABLISHED non-spiking interneurons. Selectors copied from
# the benchmark's OWN task files (26_mb_sparseness_apl.yaml for APL), so
# population identity is dataset-proof. ASSUMPTION (rate-equivalence
# bridge): a graded unit's per-step output must live in the same currency
# as spikes (1.0 on spike steps). We map depolarization to an equivalent
# rate via G_RATE_HZ_PER_MV, so output/step = G * (v - v_rest) * dt_s.
# G = 5 Hz/mV ASSUMED (10 mV depolarization ~ 50 Hz, a plausible graded
# interneuron transfer); it is a bridge constant, not a fit on any task.
APL_SELECT = {"any": [{"cell_type": "APL"}, {"hemibrain_type": "APL"}]}
CT1_SELECT = {"any": [{"cell_type": "CT1"}, {"hemibrain_type": "CT1"},
                      {"cell_type_regex": "^CT1\\("}]}
KC_SELECT = {"cell_type_regex": "^KC"}   # verbatim from task 26's readout
G_RATE_HZ_PER_MV = 5.0

# --- KC threshold calibration (design ingredient 3) -------------------------
# Litwin-Kumar-style: threshold_i = mu_i + alpha * sigma_i over a NON-TASK
# calibration set (seeded random subsets of the KCs' own presynaptic
# partners -- never a benchmark stimulus), alpha bisected so the mean
# active fraction hits the literature band midpoint. All instrument
# constants fixed here, before any MaleCNS run of this class.
CAL_N_STIMULI = 8
CAL_DURATION_MS = 300.0
CAL_SETTLE_MS = 100.0
CAL_RATE_HZ = 100.0
CAL_SUBSET_FRAC = 0.10
CAL_TARGET_SPARSENESS = 0.075       # Turner 2008 / Honegger 2011 band midpoint
CAL_SEED = 20261003
CAL_ALPHA_RANGE = (0.0, 8.0)
CAL_CACHE_DIR = _Path.home() / ".cache" / "flygi-flybench-calibration"


def lk_alpha_search(v_max, mu, sigma, target, alpha_range=CAL_ALPHA_RANGE,
                    iters=40):
    """Bisect alpha so mean_{stim,cell} [v_max > mu + alpha*sigma] ~ target.
    v_max: (n_stim, n_cell); mu/sigma per cell. Returns (alpha, achieved).
    Active fraction decreases monotonically in alpha."""
    lo, hi = alpha_range

    def frac(alpha):
        thr = mu + alpha * sigma
        return float((v_max > thr[None, :]).mean())

    if frac(lo) < target:            # even the laxest threshold is too sparse
        return lo, frac(lo)
    if frac(hi) > target:            # even the strictest is too dense
        return hi, frac(hi)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if frac(mid) > target:
            lo = mid
        else:
            hi = mid
    alpha = 0.5 * (lo + hi)
    return alpha, frac(alpha)


def _wiring_key(W) -> str:
    h = hashlib.blake2b(digest_size=16)
    h.update(np.int64(W.shape[0]).tobytes())
    h.update(W.indptr.tobytes())
    h.update(W.indices.tobytes())
    h.update(np.ascontiguousarray(W.data).tobytes())
    return h.hexdigest()


def _same_indices(W, base) -> bool:
    return (W.shape == base.shape
            and W.indptr.shape == base.indptr.shape
            and np.array_equal(W.indptr, base.indptr)
            and np.array_equal(W.indices, base.indices))


def _silenced_subset(W, base) -> bool:
    """True iff W equals base except some neurons' OUTGOING synapses are
    removed. flybench's silence_neurons zeroes rows of its (pre, post)
    matrix; the engine holds the TRANSPOSE (post, pre), so silencing
    appears as zeroed COLUMNS here -- compare in CSC space, where columns
    are contiguous. (The first version of this predicate checked rows of
    the transposed matrix -- i.e. incoming synapses -- and was caught by
    its unit test: silencing the toy APL matched 0 rows.)"""
    if W.shape != base.shape or W.nnz >= base.nnz:
        return False
    Wc, Bc = W.tocsc(), base.tocsc()
    nz_w = np.diff(Wc.indptr)
    nz_b = np.diff(Bc.indptr)
    zeroed = (nz_w == 0) & (nz_b > 0)
    same = nz_w == nz_b
    if not np.all(zeroed | same) or not np.any(zeroed):
        return False
    keep = np.repeat(same, nz_b)
    return (np.array_equal(Wc.indices, Bc.indices[keep])
            and np.allclose(Wc.data, Bc.data[keep]))


class FlyGICalibratedAdapter:
    """flybench Simulator contract over the UNMODIFIED class-2 engine, with
    the registered calibrated parameter set layered on as composition.

    Calibration reuse policy (declared; each branch labelled):
      - identical wiring        -> cached thresholds (same brain).
      - same sparsity pattern   -> reuse (their weight-jitter 'second
        individual': the task measures PARAMETER robustness, matching how
        the reference model is treated -- no homeostatic refit).
      - row-zeroed subset       -> reuse (their `silence:` conditions are
        ACUTE shibire-style blocks; thresholds must NOT re-tune, or the
        calibration would partially cancel the manipulation under test).
      - anything else           -> calibrate fresh (a genuinely different
        wiring -- above all the degree-preserving rewired CONTROL, which
        must receive the same procedure on ITS OWN wiring, or specificity
        would be inflated by a threshold mismatch artifact).
    The file cache makes this cheap across worker processes and runs.
    """

    capabilities: frozenset = frozenset({"can_silence"})
    _bases: list = []        # [(key, W)] seen base wirings, process-level

    def __init__(self, connectome, params: LIFParams | None = None):
        self.c = connectome
        self.p = params or LIFParams()
        p = self.p
        w_scale = p.w_syn_mv * p.gain / p.tau_m_ms   # derived bridge (uniform class)
        ann = connectome.annotations
        types = ann["cell_type"].fillna("").astype(str).to_numpy(dtype="U64")

        def spiking_params(tau_ms, provenance):
            return TypeParams(
                tau_m_ms=tau_ms, v_thresh=p.v_th_mv, provenance=provenance,
                tau_syn_ms=p.tau_syn_ms, v_rest=p.v_rest_mv,
                v_reset=p.v_reset_mv, refractory_ms=p.t_ref_ms, graded=False,
            )

        rules = [
            (name, spiking_params(
                tau, f"{name}: fast/slow class ESTABLISHED; {tau:.0f} ms "
                     f"from the fc2 table (calibrated_design.md ingredient 1)"))
            for name, tau in CALIBRATED_TAUS_MS.items()
        ]
        table = ParameterTable(
            default=spiking_params(
                p.tau_m_ms, "Shiu 2024 constants via flybench LIFParams"),
            rules=rules,
        )
        self.net = SpikingNetwork(
            connectome.W.T.tocsr(), types, table,
            dt_ms=DT_MS, w_scale=w_scale, seed=p.seed,
        )
        # graded_gain carries dt_s: output/step = G * (v - v_rest) * dt_s.
        dt_s = DT_MS / 1000.0

        # --- graded APL/CT1 by index (their own selectors; AF-4: internal,
        # no spikes emitted; if a task ever declares one as a READOUT it is
        # the recorded exception in the design doc) ------------------------
        graded_idx = np.unique(np.concatenate([
            connectome.select(APL_SELECT), connectome.select(CT1_SELECT)
        ]).astype(np.int64)) if connectome.n else np.empty(0, np.int64)
        pr = self.net.params
        if graded_idx.size:
            pr["graded"][graded_idx] = True
            pr["graded_gain"][graded_idx] = G_RATE_HZ_PER_MV * dt_s
            pr["v_thresh"][graded_idx] = 1e9

        self._spiking = ~pr["graded"]
        self._pulse = (p.v_th_mv - p.v_rest_mv) / DT_MS + 1.0

        # --- KC threshold calibration (cached per base wiring) -------------
        kc_idx = connectome.select(KC_SELECT).astype(np.int64)
        self.calibration = {
            "tau_rows_matched": int(np.isin(types, list(CALIBRATED_TAUS_MS)).sum()),
            "graded_units": int(graded_idx.size),
            "kc_count": int(kc_idx.size),
            "applied": False, "reused": None, "blocked_sparseness": False,
        }
        if kc_idx.size:
            self._calibrate_kcs(connectome, kc_idx, graded_idx)

    # -- calibration machinery ---------------------------------------------
    def _calibrate_kcs(self, c, kc_idx, graded_idx):
        W = self.net.matrix   # post, pre (transposed)
        for key, base in self._bases:
            if _same_indices(W, base) and _wiring_key(W) == key:
                thr = self._load_cache(key)
                if thr is not None:
                    self._apply(kc_idx, thr, reused="identical")
                    return
        for key, base in self._bases:
            if _same_indices(W, base):
                thr = self._load_cache(key)
                if thr is not None:
                    self._apply(kc_idx, thr, reused="jitter-same-pattern")
                    return
            if _silenced_subset(W, base):
                thr = self._load_cache(key)
                if thr is not None:
                    self._apply(kc_idx, thr, reused="silenced-subset")
                    return
        key = _wiring_key(W)
        thr = self._load_cache(key)
        if thr is None:
            thr = self._run_calibration(kc_idx, graded_idx, key)
            self._save_cache(key, thr)
        type(self)._bases.append((key, W))
        self._apply(kc_idx, thr, reused=None)

    def _apply(self, kc_idx, thr, reused):
        # floor: a threshold at/below rest would make a KC fire tonically.
        floored = np.maximum(thr["thresholds"], self.p.v_rest_mv + 0.1)
        self.net.params["v_thresh"][kc_idx[:floored.size]] = floored.astype(np.float32)
        self.calibration.update(
            applied=True, reused=reused, alpha=thr["alpha"],
            achieved_sparseness=thr["achieved"],
            blocked_sparseness=bool(thr["blocked"]),
        )
        self.net.reset()

    def _run_calibration(self, kc_idx, graded_idx, key):
        net, p = self.net, self.p
        n = net.node_count
        # the KCs' own presynaptic partners (nonzero columns of the KC rows
        # in the post,pre matrix), minus graded units and the KCs themselves
        pre = np.unique(net.matrix[kc_idx, :].tocoo().col)
        pre = pre[~np.isin(pre, np.concatenate([kc_idx, graded_idx]))]
        rng = np.random.default_rng(CAL_SEED)
        saved = net.params["v_thresh"][kc_idx].copy()
        net.params["v_thresh"][kc_idx] = 1e9        # subthreshold collection
        settle_steps = int(round(CAL_SETTLE_MS / DT_MS))
        drive_steps = int(round(CAL_DURATION_MS / DT_MS))
        prob = CAL_RATE_HZ * DT_MS / 1000.0
        v_max = np.full((CAL_N_STIMULI, kc_idx.size), -np.inf, np.float64)
        external = np.zeros(n)
        for s in range(CAL_N_STIMULI):
            net.reset()
            subset = rng.choice(pre, size=max(int(round(CAL_SUBSET_FRAC * pre.size)), 1),
                                replace=False) if pre.size else np.empty(0, np.int64)
            for _ in range(settle_steps):
                net.step(None)
            for _ in range(drive_steps):
                external[:] = 0.0
                if subset.size:
                    events = subset[rng.random(subset.size) < prob]
                    external[events] = self._pulse
                net.step(external)
                np.maximum(v_max[s], net.v[kc_idx], out=v_max[s])
        net.params["v_thresh"][kc_idx] = saved
        mu = v_max.mean(axis=0)
        sigma = np.maximum(v_max.std(axis=0), 1e-6)
        alpha, achieved = lk_alpha_search(v_max, mu, sigma, CAL_TARGET_SPARSENESS)
        blocked = abs(achieved - CAL_TARGET_SPARSENESS) > 0.05
        net.reset()
        return {"thresholds": mu + alpha * sigma, "alpha": float(alpha),
                "achieved": float(achieved), "blocked": blocked, "key": key}

    def _cache_path(self, key):
        return CAL_CACHE_DIR / f"{key}.npz"

    def _load_cache(self, key):
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            with np.load(path) as z:
                return {"thresholds": z["thresholds"], "alpha": float(z["alpha"]),
                        "achieved": float(z["achieved"]),
                        "blocked": bool(z["blocked"]), "key": key}
        except Exception:
            return None

    def _save_cache(self, key, thr):
        CAL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        fd, tmp = _tempfile.mkstemp(dir=str(CAL_CACHE_DIR), suffix=".npz")
        _os.close(fd)
        np.savez(tmp, thresholds=thr["thresholds"], alpha=thr["alpha"],
                 achieved=thr["achieved"], blocked=thr["blocked"])
        _os.replace(tmp, self._cache_path(key))
        sidecar = {k: v for k, v in thr.items() if k != "thresholds"}
        sidecar.update(self.calibration)
        sidecar["n_neurons"] = int(self.net.node_count)
        (CAL_CACHE_DIR / f"{key}.json").write_text(_json.dumps(sidecar, indent=1))

    # -- contract ------------------------------------------------------------
    def run(self, duration_ms: float, stimuli=None) -> SimResult:
        return FlyGIAdapter.run(self, duration_ms, stimuli)
