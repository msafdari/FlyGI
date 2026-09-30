#!/usr/bin/env python3
"""FIDELITY CLASS 2.5 -- BENCHMARK V1 RERUN: T4/T5 DS with TRAINED flyvis
parameters on the SAME MaleCNS patch protocol as fc2_visual_ds.

Class-2 result this extends (results/benchmarks/fc2_visual_ds.json,
2026-09-29): frozen-parameter flyvis-form dynamics FAILED the band at all
8 heterogeneous-tau configs (best pooled median DSI 0.042 under the
corrected v2 crossing-window readout, vs the 0.30 band) AND the
uniform-tau trivial control matched it (0.045) -- temporal heterogeneity
contributed nothing under FROZEN per-pair strengths and resting
potentials. The located blocker (fc2 header, doc R3/R4): frozen alpha
and V_rest. The dossier's I5/R3 rows name the lever: the RELEASED
TRAINED ENSEMBLE (Lappalainen et al. 2024, 50 task-trained models).
Class 2.5 changes PARAMETERS ONLY: trained per-type tau, trained
per-type V_rest, trained per-TYPE-PAIR unitary strengths (alpha), all
read from the released checkpoints. Dynamics, patch, stimulus, readout,
calibration procedure and band are fc2's, imported from fc2_visual_ds
(single source of truth; asserted at run time). THE BAND DOES NOT CHANGE.

===========================================================================
PREREGISTERED PASS BAND -- verbatim from class-1 scripts/benchmarks/
visual_motion.py (BENCHMARK V1), fixed before any class-2 dynamics ran,
and identical (asserted) to fc2_visual_ds.BAND_TEXT:

  "PASS iff pooled per-cell median DSI >= 0.3 (T4 on ON bar, T5 on OFF
  bar) AND T4a-d distinct preferred directions >= 3 AND T5a-d distinct
  >= 3 AND defined-DSI fraction >= 0.5; preregistered before the sweep"

  CITATION: Maisak et al. 2013, Nature 500:212-216.
===========================================================================

TRAINED PARAMETERS (extracted by `--extract`, saved with provenance to
docs/fidelity2/flyvis_trained_params.json, read back by the run):

  - Source: flyvis 1.2.0 (pip), released pretrained ensemble
    "flow/0000" (50 task-trained models), downloaded with the package's
    own `flyvis download-pretrained` (SHA256-checksummed zips), plus
    the released precomputed UMAP+GMM clustering.
  - Task-optimal subset: cluster 0 of Ensemble.cluster_indices("T4c")
    on the RELEASED clustering. flyvis relabels clusters by ascending
    task error (verified: get_cluster_to_indices ->
    task_error_sort_labels in flyvis/analysis/clustering.py), so
    cluster 0 is the paper's task-optimal T4c-tuning cluster
    (Lappalainen 2024 Fig. 4). MEASURED at extraction: n=31 models,
    mean min-validation loss 5.2974 vs 5.3158 / 5.3572 for clusters
    1 / 2. Aggregation rule: arithmetic mean over subset models of raw
    checkpoint values (alpha clamped >= 0 per model first, as flyvis
    clamps at use; negatives counted and recorded). All-50 mean is
    extracted alongside and run as a secondary config.
  - ALPHA UNIT MAPPING (declared): in flyvis the edge weight is
        weight_ij = sign_pair * syn_count_ij * syn_strength_pair
    (VERIFIED in flyvis/network/dynamics.py,
    PPNeuronIGRSynapses.write_derived_params). syn_strength (alpha) is
    a per-(source_type,target_type) UNITARY strength multiplying the
    synapse count; it does NOT absorb counts. Therefore here:
        W_ij = curated_sign(pre) * alpha_trained(pre->post) * N_ij
    with N_ij the raw MaleCNS synapse count of the fc2 patch.
    ASSUMPTION (labeled): MaleCNS per-pair counts stand in for
    flyvis's FIB25-derived filter counts on a comparable per-pair
    scale. The GLOBAL scale mismatch is absorbed by the declared gain
    calibration; RELATIVE per-pair scale differences between the two
    connectomes are uncorrected and would misweight arms.
  - MISSING-PAIR FALLBACK (declared): MaleCNS patch pairs absent from
    flyvis's 604 trained pairs get flyvis's own INIT rule
    alpha = 0.01 / mean_nonzero_patch_count(pair) (VERIFIED at
    flyvis/network/initialization.py:501, SynapseCountScaling:
    alpha = rho/<N>, rho=0.01). Coverage (edges and synapse mass under
    trained alphas) is measured and recorded. NOTE, recorded
    correction: the dossier (optic_lobe_temporal.md section 1) states
    alpha init "0.01 * <N_titj>"; the flyvis source says 0.01 / <N>.
    fc2 implemented 0.01*<N> as its own declared frozen-init choice;
    fc25 follows the flyvis source formula for untrained pairs.
  - V_rest: trained per-type bias (subset mean). Replaces fc2's
    uniform 0.5.
  - tau: trained per-type time constants, seconds -> ms (subset mean);
    engine clamps tau >= dt at use exactly as fc2/flyvis do.

GAIN CALIBRATION (same declared procedure as fc2: one global scalar g
per configuration, chosen on the held-out +45deg-diagonal edge at
5 col/s in both polarities, log-grid argmin |log(median peak evoked
over T4-on-ON u T5-on-OFF / 0.5)| subject to stability; scoring never
feeds back into g). ONE DECLARED CHANGE, made before any fc25 run:
the log grid is EXTENDED upward, continuing fc2's exact {1,3}x10^k
pattern from 3e-1 through 3e3. Reason (unit analysis, not tuning):
trained alpha sits near flyvis's init scale rho/<N> while fc2's frozen
alpha was 0.01*<N>; the weights therefore shrink by a factor ~<N>^2
(10^2..10^5 over patch pairs) and fc2's grid top of 0.3 would pin every
configuration to the grid edge. The identical extended grid applies to
every configuration INCLUDING the trivial control; whether any chosen
gain still sits at a grid edge is recorded.

CONFIGURATIONS (all on the identical fc2 patch, stimulus, dt, settle,
readouts):
  1. trained_subset  -- tau, V_rest, alpha = task-optimal-cluster means
                        (PRIMARY).
  2. trained_all50   -- same, means over all 50 models (secondary).
  3. TRIVIAL ALTERNATIVE (mandatory, named in advance): uniform tau
     50 ms (flyvis init) for every type, WITH the trained subset alphas
     and trained V_rest -- so the comparison isolates TEMPORAL
     HETEROGENEITY under trained strengths. Attribution rule,
     operationalized IN ADVANCE exactly as fc2: best trained pooled
     median DSI >= 2x the uniform-tau value AND absolute margin
     >= 0.10, on the v2 (crossing-window) readout.

READOUT: fc2's v2 crossing-locked window is the corrected instrument
and the primary; v1 whole-sweep is scored and retained as the recorded
artifact. Both come from the same simulations (fc2.score_config).

TIER DISCIPLINE: every number printed or saved is Measured under this
protocol. The only Expected claim, with its base rate: this repo's
expected-to-help changes are 0 for 11 (now 0 for 12 counting fc2's
heterogeneous-tau arm); whether trained parameters rescue DS on
MaleCNS counts is open until this runs.

Run:  python scripts/benchmarks/fc25_visual_ds.py --extract   (needs
      FLYVIS_ROOT_DIR pointing at the downloaded ensemble; writes
      docs/fidelity2/flyvis_trained_params.json)
      python scripts/benchmarks/fc25_visual_ds.py             (the
      benchmark; reads that JSON)
Output: results/benchmarks/fc25_visual_ds.json (saved after every
        config) and results/benchmarks/fc25_visual_ds.log
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PARAMS_JSON = ROOT / "docs/fidelity2/flyvis_trained_params.json"

# The preregistered band, restated verbatim (asserted == fc2.BAND_TEXT).
BAND_TEXT = (
    "PASS iff pooled per-cell median DSI >= 0.3 (T4 on ON bar, T5 on OFF "
    "bar) AND T4a-d distinct preferred directions >= 3 AND T5a-d distinct "
    ">= 3 AND defined-DSI fraction >= 0.5; preregistered before the sweep"
)

MOTION_TYPES = (
    "L1", "L2", "L3", "L4", "L5", "Mi1", "Mi4", "Mi9",
    "Tm1", "Tm2", "Tm3", "Tm4", "Tm9", "CT1(M10)", "CT1(Lo1)",
    "T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d",
)

# fc2 grid continued with the same {1,3}x10^k pattern (declared, header).
EXTENDED_GAIN_GRID = (
    1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1,
    1e0, 3e0, 1e1, 3e1, 1e2, 3e2, 1e3, 3e3,
)

UNIFORM_TAU = 50.0          # trivial alternative: flyvis init, as fc2
FALLBACK_RHO = 0.01         # flyvis SynapseCountScaling rho (verified)


def load_fc2():
    spec = importlib.util.spec_from_file_location(
        "fc2_visual_ds", HERE / "fc2_visual_ds.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["fc2_visual_ds"] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# --extract: pull trained parameters from the released ensemble
# --------------------------------------------------------------------------

def extract(flyvis_root: str) -> int:
    os.environ["FLYVIS_ROOT_DIR"] = flyvis_root
    import torch  # noqa: PLC0415
    import flyvis  # noqa: PLC0415
    from flyvis import EnsembleView, NetworkView  # noqa: PLC0415

    kw = {"validation_subdir": "validation", "loss_file_name": "loss"}
    ens = EnsembleView("flow/0000", best_checkpoint_fn_kwargs=kw)
    names = [n.split("/")[-1] for n in ens.names]
    losses = np.asarray(ens.min_validation_losses())
    clusters = {
        int(k): sorted(int(i) for i in v)
        for k, v in ens.cluster_indices("T4c").items()
    }
    subset = clusters[0]

    # Index -> name maps from one instantiated network (verified: raw
    # checkpoint vectors match Parameter.raw_values elementwise).
    nv = NetworkView("flow/0000/000", best_checkpoint_fn_kwargs=kw)
    net = nv.init_network()
    node_keys = list(net.node_params.time_const.keys)
    assert node_keys == list(net.node_params.bias.keys)
    edge_keys = [tuple(k) for k in net.edge_params.syn_strength.keys]

    tau = np.zeros((len(names), len(node_keys)))
    bias = np.zeros((len(names), len(node_keys)))
    alpha = np.zeros((len(names), len(edge_keys)))
    negatives = 0
    for i, name in enumerate(names):
        ck = torch.load(
            Path(flyvis_root) / "results/flow/0000" / name
            / "chkpts/chkpt_00000",
            map_location="cpu", weights_only=False,
        )["network"]
        assert ck["nodes_time_const"].shape[0] == len(node_keys)
        assert ck["edges_syn_strength"].shape[0] == len(edge_keys)
        tau[i] = ck["nodes_time_const"].numpy()
        bias[i] = ck["nodes_bias"].numpy()
        a = ck["edges_syn_strength"].numpy()
        negatives += int((a < 0).sum())
        alpha[i] = np.maximum(a, 0.0)   # flyvis clamps non-negative at use

    sub = np.asarray(subset)

    def agg(arr_2d, idx):
        col = arr_2d[:, idx]
        return {
            "subset_mean": float(col[sub].mean()),
            "subset_std": float(col[sub].std()),
            "all50_mean": float(col.mean()),
            "all50_std": float(col.std()),
        }

    types_table = {}
    for t in MOTION_TYPES:
        i = node_keys.index(t)
        types_table[t] = {
            "tau_ms": {k: v * 1000.0 for k, v in agg(tau, i).items()},
            "v_rest": agg(bias, i),
            "per_model_tau_ms": [round(v * 1000.0, 4) for v in tau[:, i]],
            "per_model_v_rest": [round(float(v), 4) for v in bias[:, i]],
        }

    pairs_table = {}
    motion = set(MOTION_TYPES)
    for j, (src, dst) in enumerate(edge_keys):
        if src in motion and dst in motion:
            pairs_table[f"{src}->{dst}"] = agg(alpha, j)

    out = {
        "provenance": {
            "source": "flyvis {} (pip), released pretrained ensemble "
                      "flow/0000, Lappalainen et al. 2024 Nature 634:1132"
                      .format(flyvis.__version__),
            "download": "flyvis download-pretrained (package's public "
                        "Google Drive distribution; SHA256 checksums "
                        "verified by the downloader: "
                        "results_pretrained_models.zip 71c78d40..., "
                        "results_umap_and_clustering.zip 6300ec1e...)",
            "checkpoint": "chkpts/chkpt_00000 per model (sole released "
                          "checkpoint; verified identical to what "
                          "NetworkView.init_network() recovers)",
            "ensemble_ids": names,
            "min_validation_losses": [round(float(x), 4) for x in losses],
            "task_optimal_subset": {
                "definition": "cluster 0 of Ensemble.cluster_indices('T4c') "
                              "on the RELEASED precomputed UMAP+GMM "
                              "clustering; flyvis relabels clusters by "
                              "ascending task error, so cluster 0 is the "
                              "paper's task-optimal T4c-tuning cluster "
                              "(Lappalainen 2024 Fig. 4)",
                "clusters": clusters,
                "cluster_mean_task_error": {
                    str(k): round(float(losses[np.asarray(v)].mean()), 4)
                    for k, v in clusters.items()
                },
                "subset_model_ids": [names[i] for i in subset],
                "n": len(subset),
                "caveat": "sklearn emitted InconsistentVersionWarning "
                          "unpickling the stored clustering (built with "
                          "1.1.1, read with the installed version); labels "
                          "and mask are stored values, not refit, and the "
                          "ensemble-consistency check in cluster_indices "
                          "passed",
            },
            "aggregation": "arithmetic mean (and std) over models of raw "
                           "checkpoint values; alpha clamped >=0 per model "
                           "before averaging (flyvis clamps at use); "
                           "negative raw alphas encountered: {}"
                           .format(negatives),
            "alpha_semantics": "weight_ij = sign_pair * syn_count_ij * "
                               "alpha_pair (VERIFIED, flyvis/network/"
                               "dynamics.py PPNeuronIGRSynapses."
                               "write_derived_params); alpha is the "
                               "per-type-pair unitary strength multiplying "
                               "the synapse count, units a.u. per synapse; "
                               "flyvis init was rho/<N>_pair, rho=0.01 "
                               "(VERIFIED, flyvis/network/"
                               "initialization.py SynapseCountScaling)",
            "units": "tau in ms (checkpoint stores seconds); v_rest and "
                     "alpha in flyvis a.u.",
            "tau_raw_range_ms": [round(float(tau.min() * 1000), 2),
                                 round(float(tau.max() * 1000), 2)],
            "extracted_by": "scripts/benchmarks/fc25_visual_ds.py "
                            "--extract, 2026-09-29",
        },
        "types": types_table,
        "pairs": pairs_table,
    }
    PARAMS_JSON.write_text(json.dumps(out, indent=1))
    print(f"wrote {PARAMS_JSON}: {len(types_table)} types, "
          f"{len(pairs_table)} trained pairs among motion types, "
          f"subset n={len(subset)}, negative alphas clamped: {negatives}")
    return 0


# --------------------------------------------------------------------------
# benchmark run: fc2 protocol with trained parameters
# --------------------------------------------------------------------------

def trained_weight_matrix(fc2, patch, alpha_of_pair: dict[str, float]):
    """W_ij = curated_sign(pre) * alpha(pre->post) * N_ij (header mapping).

    Pairs without a trained alpha get flyvis's init rule rho/<N>_patch_pair
    (declared fallback). Returns (csr matrix, coverage record).
    """
    from scipy import sparse  # noqa: PLC0415

    coo = patch["raw_counts"].tocoo()
    types = patch["types"]
    pre_types = types[coo.col]
    post_types = types[coo.row]
    counts = np.abs(coo.data)
    measured_sign = np.sign(coo.data)
    curated = np.array([fc2.CURATED_SIGNS.get(t, 0) for t in pre_types])
    signs = np.where(curated != 0, curated, measured_sign)

    pair_names = np.array([f"{a}->{b}" for a, b in zip(pre_types, post_types)])
    unique_pairs, inverse = np.unique(pair_names, return_inverse=True)
    # patch mean nonzero count per pair, for the fallback rho/<N>
    pair_sum = np.zeros(unique_pairs.size)
    pair_n = np.zeros(unique_pairs.size)
    np.add.at(pair_sum, inverse, counts)
    np.add.at(pair_n, inverse, 1.0)
    mean_count = pair_sum / np.maximum(pair_n, 1.0)

    alpha_per_pair = np.empty(unique_pairs.size)
    trained_mask = np.zeros(unique_pairs.size, dtype=bool)
    for k, p in enumerate(unique_pairs):
        got = alpha_of_pair.get(p)
        if got is not None:
            alpha_per_pair[k] = got
            trained_mask[k] = True
        else:
            alpha_per_pair[k] = FALLBACK_RHO / max(mean_count[k], 1e-12)

    alpha_edges = alpha_per_pair[inverse]
    trained_edges = trained_mask[inverse]
    weight = signs * alpha_edges * counts
    matrix = sparse.csr_matrix(
        (weight, (coo.row, coo.col)), shape=patch["raw_counts"].shape
    )
    coverage = {
        "pairs_total": int(unique_pairs.size),
        "pairs_trained": int(trained_mask.sum()),
        "pairs_fallback": sorted(
            unique_pairs[~trained_mask].tolist()
        ),
        "edges_trained_fraction": float(trained_edges.mean()),
        "synapse_mass_trained_fraction": float(
            counts[trained_edges].sum() / counts.sum()
        ),
        "fallback_rule": "alpha = 0.01 / mean_nonzero_patch_count(pair) "
                         "(flyvis init formula; declared, header)",
    }
    return matrix, coverage


def trained_table(fc2, params: dict, which: str, uniform_tau: float | None):
    """ParameterTable: trained per-type tau + V_rest (aggregate `which`),
    or uniform tau with trained V_rest for the trivial control."""
    from flygi.dynamics.spiking import ParameterTable, TypeParams  # noqa: PLC0415

    def graded(tau_ms: float, v_rest: float, provenance: str) -> TypeParams:
        return TypeParams(
            tau_m_ms=tau_ms, v_thresh=1e9, provenance=provenance,
            v_rest=v_rest, graded=True, graded_gain=1.0,
        )

    rules = []
    for t, row in params["types"].items():
        v_rest = row["v_rest"][f"{which}_mean"]
        if uniform_tau is not None:
            rules.append((t, graded(
                uniform_tau, v_rest,
                f"{t}: TRIVIAL CONTROL uniform tau {uniform_tau:.0f} ms "
                f"(flyvis init); V_rest {v_rest:.4f} TRAINED "
                f"({which} mean) -- heterogeneity ablated, strengths kept")))
        else:
            tau_ms = row["tau_ms"][f"{which}_mean"]
            rules.append((t, graded(
                tau_ms, v_rest,
                f"{t}: tau {tau_ms:.2f} ms, V_rest {v_rest:.4f} -- "
                f"MEASURED(model-derived): flyvis flow/0000 {which} mean")))
    return ParameterTable(
        default=graded(
            UNIFORM_TAU, 0.5,
            "unmatched type: flyvis init 50 ms / 0.5 (should never fire; "
            "all patch types carry trained rules)"),
        rules=rules,
    )


def run_benchmark() -> int:
    fc2 = load_fc2()
    assert fc2.BAND_TEXT == BAND_TEXT, "band drifted from fc2 -- refuse to run"
    params = json.loads(PARAMS_JSON.read_text())

    # Declared calibration-grid extension (header). Same procedure, same
    # held-out stimulus, same target; applies to every config equally.
    fc2.GAIN_GRID = EXTENDED_GAIN_GRID

    out_path = ROOT / "results/benchmarks/fc25_visual_ds.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(out_path.with_suffix(".log"), "w")
    log = lambda m: fc2.log_print(handle, m)  # noqa: E731

    try:
        import psutil  # noqa: PLC0415
        free_gb = psutil.virtual_memory().available / 2**30
    except Exception:
        free_gb = float("nan")
    log(f"free RAM at start: {free_gb:.2f} GiB (resource rule: single "
        f"process, class-2 run was ~3 min; this adds ~1 config-worth)")

    started = time.time()
    patch = fc2.build_patch()
    types = patch["types"]
    patch["driven_mask"] = np.isin(types, fc2.DRIVEN_TYPES)
    score_mask = np.isin(types, fc2.T4_SUBTYPES + fc2.T5_SUBTYPES)
    score_idx = np.flatnonzero(score_mask)
    score_types = types[score_idx]
    log(f"patch: {patch['node_count']} cells, raw edges "
        f"{patch['raw_counts'].nnz}, {score_idx.size} scored T4/T5 cells, "
        f"built in {time.time() - started:.1f}s")
    log(f"sign audit: {patch['sign_audit']}")

    report: dict[str, Any] = {
        "benchmark": "FC2.5 V1 rerun -- T4/T5 direction selectivity: fc2 "
                     "patch/protocol with TRAINED flyvis ensemble "
                     "parameters (per-type tau, per-type V_rest, per-pair "
                     "alpha)",
        "band": fc2.BAND_TEXT,
        "citation": fc2.CITATION,
        "fc2_result": "all 8 frozen-parameter configs failed (best v2 "
                      "median DSI 0.042; uniform-tau control 0.045 -- "
                      "matched); results/benchmarks/fc2_visual_ds.json",
        "trained_params": str(PARAMS_JSON.relative_to(ROOT)),
        "params_provenance": params["provenance"],
        "alpha_mapping": "W_ij = curated_sign(pre) * alpha_trained(pair) * "
                         "N_ij(MaleCNS); flyvis alpha multiplies counts "
                         "(does NOT absorb them; verified in dynamics.py). "
                         "ASSUMPTION: MaleCNS counts comparable per-pair "
                         "to flyvis's FIB25-derived counts; global scale "
                         "absorbed by gain calibration, relative per-pair "
                         "scale uncorrected (header)",
        "calibration_declared": (
            "fc2 procedure unchanged (held-out +45deg diagonal, 5 col/s, "
            "both polarities, argmin |log(median peak evoked/0.5)|, "
            "stability-gated); grid EXTENDED before any run by continuing "
            "the {1,3}x10^k pattern to 3e3 (unit analysis, header); "
            "identical grid for every config including the control"
        ),
        "gain_grid": list(EXTENDED_GAIN_GRID),
        "expected_tier_note": "repo base rate for expected-to-help changes "
                              "is 0/12; pass/fail open until run",
        "configs": [],
        "trivial_alternative": None,
    }

    def save() -> None:
        out_path.write_text(json.dumps(report, indent=2))

    save()

    def one_config(label: str, which: str, uniform_tau: float | None):
        t0 = time.time()
        log(f"[config {label}]")
        matrix, coverage = trained_weight_matrix(
            fc2, patch, {p: v[f"{which}_mean"]
                         for p, v in params["pairs"].items()}
        )
        patch["matrix"] = matrix
        if uniform_tau is None:
            log(f"  alpha coverage: {coverage['pairs_trained']}/"
                f"{coverage['pairs_total']} pairs trained, synapse mass "
                f"{coverage['synapse_mass_trained_fraction']:.4f}")
        table = trained_table(fc2, params, which, uniform_tau)
        cal = fc2.calibrate(patch, table, score_idx, score_types, handle)
        row: dict[str, Any] = {
            "label": label,
            "aggregate": which,
            "uniform_tau_ms": uniform_tau,
            "alpha_coverage": coverage,
            "parameter_provenance": table.provenance_report(),
            "calibration": cal,
        }
        if cal["chosen_gain"] is None:
            row["result"] = None
            row["blocker"] = "no stable nonzero gain on calibration grid"
        else:
            grid = EXTENDED_GAIN_GRID
            row["gain_at_grid_edge"] = cal["chosen_gain"] in (grid[0], grid[-1])
            row["result"] = fc2.score_config(
                patch, table, cal["chosen_gain"], score_idx, score_types,
                handle,
            )
            if row["result"] is None:
                row["blocker"] = ("settle diverged at the calibrated gain "
                                  "during scoring")
        row["elapsed_s"] = round(time.time() - t0, 1)
        return row

    for label, which in (("trained_subset", "subset"),
                         ("trained_all50", "all50")):
        report["configs"].append(one_config(label, which, None))
        save()

    control = one_config(
        "uniform_tau_50ms_trained_alpha_vrest", "subset", UNIFORM_TAU
    )
    report["trivial_alternative"] = control
    save()

    scored = [c for c in report["configs"] if c.get("result")]
    report["summary"] = {"total_elapsed_s": round(time.time() - started, 1)}
    for key in ("readout_v2_crossing_window", "readout_v1_wholesweep"):
        best = max(
            scored, key=lambda c: c["result"][key]["median_dsi_pooled"],
            default=None,
        )
        control_dsi = (
            control["result"][key]["median_dsi_pooled"]
            if control.get("result") else float("nan")
        )
        best_dsi = best["result"][key]["median_dsi_pooled"] if best else None
        report["summary"][key] = {
            "pass_configs": [c["label"] for c in scored
                             if c["result"][key]["pass"]],
            "best_config": best["label"] if best else None,
            "best_gain": best["calibration"]["chosen_gain"] if best else None,
            "best_median_dsi": best_dsi,
            "trivial_uniform_tau_median_dsi": control_dsi,
            "attribution_holds": bool(
                best is not None
                and np.isfinite(control_dsi)
                and best_dsi > 2.0 * abs(control_dsi)
                and best_dsi - abs(control_dsi) > 0.10
            ) if best else False,
        }
    save()
    log(json.dumps(report["summary"], indent=2))
    handle.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="FC2.5 trained-parameter "
                                                 "T4/T5 DS benchmark")
    parser.add_argument("--extract", action="store_true",
                        help="extract trained params from the downloaded "
                             "flyvis ensemble into docs/fidelity2/")
    parser.add_argument("--flyvis-root",
                        default=os.environ.get("FLYVIS_ROOT_DIR"),
                        help="FLYVIS_ROOT_DIR containing results/flow/0000")
    args = parser.parse_args()
    if args.extract:
        if not args.flyvis_root:
            print("--extract needs --flyvis-root or FLYVIS_ROOT_DIR")
            return 2
        return extract(args.flyvis_root)
    return run_benchmark()


if __name__ == "__main__":
    raise SystemExit(main())
