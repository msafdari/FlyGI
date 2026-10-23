"""Tests for scripts/arenas/fb_topology_killtest.py
(H-FB-COLUMNAR-TOPOLOGY, Task 10 item 4). The real measurement is
data-gated and local; the PIPELINE is pure, so what is testable
in-cloud is nearly everything: the AC-FB1..4 parsers and frames, the
two-hop / aggregation / antipodal-mass / offset-histogram mechanics,
the VERBATIM Stage-A mirror_peak reuse (asserted by identity, never
re-implemented), the frozen constants, the BLOCKED floors, and -- the
load-bearing one -- the registered synthetic gate: the idealized
Hulse-motif FB circuit must PASS both bars at the empirical floor
through the REAL degree-preserving-rewire machinery, and its own
rewire must KILL both bars."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

_spec = importlib.util.spec_from_file_location(
    "fb_topology_killtest", ROOT / "scripts/arenas/fb_topology_killtest.py")
fb = importlib.util.module_from_spec(_spec)
sys.modules["fb_topology_killtest"] = fb
_spec.loader.exec_module(fb)

cx = sys.modules["cx_topology_killtest"]  # loaded by fb itself


def test_mirror_peak_is_stage_a_verbatim():
    # The registration forbids re-implementation: the Bar 2 statistic is
    # the very same function object the Stage-A instrument validated.
    assert fb.mirror_peak is cx.mirror_peak
    assert fb.empirical_p is cx.empirical_p
    assert fb.relu_dense is cx.relu_dense
    assert fb.N_OFFSET_BINS == cx.N_WEDGES == 16


def test_fb_column_parser():
    assert fb.fb_column("FC1A_C5.2") == 5
    assert fb.fb_column("vDeltaB_C0") == 0
    # AC-FB3: a/b sub-column suffixes collapse to the numeric column
    assert fb.fb_column("hDeltaA_C12a.1") == 12
    assert fb.fb_column("hDeltaC_C3b") == 3
    assert fb.fb_column("PFNd_L4_C7") == 7
    assert fb.fb_column("no label here") is None
    assert fb.fb_column("hDeltaK_irreg") is None  # kept + flagged, unlabelled


def test_pb_glomerulus_parser():
    assert fb.pb_glomerulus("PFNd_L4_C7.0") == ("L", 4)
    assert fb.pb_glomerulus("PFNa_R9") == ("R", 9)
    assert fb.pb_glomerulus("PFNv_L2_x") == ("L", 2)
    assert fb.pb_glomerulus("PFNd_C7") is None       # no side marker
    assert fb.pb_glomerulus("PFNd_L1") is None       # digit outside 2..9
    assert fb.pb_glomerulus("PFNd_R0") is None


def test_angle_frames():
    # AC-FB1: angle = 360*(c-0.5)/N on the type row's own column count
    assert fb.column_angle_deg(1, 9) == pytest.approx(20.0)
    assert fb.column_angle_deg(9, 9) == pytest.approx(340.0)
    assert fb.column_angle_deg(5, 9) == pytest.approx(180.0)
    # vDelta's C0 (N = 10 incl. C0) wraps instead of going negative
    assert fb.column_angle_deg(0, 10) == pytest.approx(342.0)
    # AC-FB2: 45-deg spacing, sides mirrored, anchored at glomerulus 2
    assert fb.glom_angle_deg("R", 2) == pytest.approx(0.0)
    assert fb.glom_angle_deg("R", 3) == pytest.approx(45.0)
    assert fb.glom_angle_deg("R", 9) == pytest.approx(315.0)
    assert fb.glom_angle_deg("L", 2) == pytest.approx(0.0)
    assert fb.glom_angle_deg("L", 3) == pytest.approx(315.0)
    for g in range(2, 10):
        assert fb.glom_angle_deg("L", g) == pytest.approx(
            (360.0 - fb.glom_angle_deg("R", g)) % 360.0)
    # wrap / circular distance mechanics
    assert fb.wrap_deg(190.0) == pytest.approx(-170.0)
    assert fb.wrap_deg(180.0) == pytest.approx(180.0)
    assert float(fb.circ_dist_deg(350.0, 10.0)) == pytest.approx(20.0)


def test_aggregate_mean_is_cell_pair_mean():
    values = np.array([[2.0, 4.0], [6.0, 8.0]])
    mean, out_u, in_u = fb.aggregate_mean(values, np.array([10.0, 10.0]),
                                          np.array([50.0, 50.0]))
    assert mean.shape == (1, 1) and mean[0, 0] == pytest.approx(5.0)
    mean2, out_u2, _ = fb.aggregate_mean(values, np.array([10.0, 170.0]),
                                         np.array([50.0, 50.0]))
    assert list(out_u2) == [10.0, 170.0]
    assert mean2[:, 0] == pytest.approx([3.0, 7.0])


def test_antipodal_mass_sector():
    nine = np.array([fb.column_angle_deg(c, 9) for c in range(1, 10)])
    # mass only on the diagonal (distance 0) -> A = 0
    assert fb.antipodal_mass(np.eye(9), nine, nine) == 0.0
    # mass only at the 160-deg straddle of the antipode -> A = 1 (the
    # sector is distance within [160, 180], boundary inclusive)
    M = np.zeros((9, 9))
    for i in range(9):
        M[(i + 4) % 9, i] = 1.0
        M[(i + 5) % 9, i] = 1.0
    assert fb.antipodal_mass(M, nine, nine) == pytest.approx(1.0)
    # distance 120 (3 columns away) is outside the sector
    M3 = np.zeros((9, 9))
    for i in range(9):
        M3[(i + 3) % 9, i] = 1.0
    assert fb.antipodal_mass(M3, nine, nine) == 0.0
    # degenerate zero mass -> NaN (BLOCKED upstream)
    assert np.isnan(fb.antipodal_mass(np.zeros((9, 9)), nine, nine))


def test_offset_histogram_and_circulant_roundtrip():
    # one pair at +40 deg -> 40/22.5 rounds to bin 2; one at -40 -> bin -2
    h = fb.offset_histogram(np.array([[3.0]]), np.array([40.0]),
                            np.array([0.0]))
    assert h[2] == pytest.approx(3.0) and h.sum() == pytest.approx(3.0)
    h2 = fb.offset_histogram(np.array([[5.0]]), np.array([0.0]),
                             np.array([40.0]))
    assert h2[-2 % 16] == pytest.approx(5.0)
    # circulant embedding reproduces the histogram through the Stage-A
    # offset_profile VERBATIM, so mirror_peak sees exactly q_L, q_R
    rng = np.random.default_rng(0)
    h3 = rng.random(16)
    profile = cx.offset_profile(fb.circulant(h3))
    for d, value in profile.items():
        assert value == pytest.approx(h3[d % 16])


def test_mirror_peak_on_embedded_profiles():
    def one_hot(k):
        h = np.zeros(16)
        h[k % 16] = 1.0
        return fb.circulant(h)

    # opposite-signed concentration -> 1.0, either chirality
    assert fb.mirror_peak(one_hot(2), one_hot(-2)) == 1.0
    assert fb.mirror_peak(one_hot(-2), one_hot(2)) == 1.0
    # same-signed concentration is NOT a mirror -> 0
    assert fb.mirror_peak(one_hot(2), one_hot(2)) == 0.0
    # zero-offset concentration is not a mirror -> 0
    assert fb.mirror_peak(one_hot(0), one_hot(0)) == 0.0
    # empty side -> 0
    assert fb.mirror_peak(fb.circulant(np.zeros(16)), one_hot(-2)) == 0.0


def test_ideal_circuit_metrics():
    W, types, instances = fb.build_ideal_circuit()
    g = fb.parse_groups(np.asarray(types), np.asarray(instances))
    assert g["fc_coverage"] == 1.0 and g["hdelta_coverage"] == 1.0
    assert g["pfn_col_coverage"] == 1.0 and g["pfn_glom_coverage"] == 1.0
    assert g["fc_n_columns"] == 9           # the registered FC frame
    assert g["pfn_n_columns"]["PFNd"] == 9  # ideal occupies all columns
    real = fb.analyze(W, g, with_context=True)
    # hDelta half-width connectivity puts ALL two-hop mass in the sector
    assert real["bar1_antipodal"] == pytest.approx(1.0)
    # opposite-signed one-sector offsets give a strong mirror peak
    assert real["bar2_mirror"] > 0.25
    assert min(real["bar2_onehop_mass"].values()) > 0
    assert real["context"]["non_decisional"] is True


def test_synthetic_gate_passes_both_directions():
    # THE registered in-cloud gate (BLOCKED floor 5), run through the
    # REAL degree_preserving_rewire machinery at a reduced null count.
    logs = []
    gate = fb.synthetic_gate(60, logs.append)
    assert gate["ideal_passes_at_floor"], gate["ideal"]
    assert gate["ideal"]["verdict"] == "PASS"
    assert gate["ideal"]["p_antipodal"] == pytest.approx(gate["empirical_floor"])
    assert gate["ideal"]["p_mirror"] == pytest.approx(gate["empirical_floor"])
    assert gate["rewire_kills_both"], gate["rewired_ideal"]
    assert gate["rewired_ideal"]["bars"] == {"antipode": False,
                                             "mirror": False}
    assert gate["passed"]


def test_pipeline_blocked_paths():
    W, types, instances = fb.build_ideal_circuit()
    types = np.asarray(types)
    instances = np.asarray(instances)
    # strip column labels from most FCs -> coverage BLOCKED (AC-FB6)
    stripped = instances.copy()
    fc_pos = np.flatnonzero(np.char.startswith(types, "FC"))
    for i in fc_pos[: int(0.5 * fc_pos.size)]:
        stripped[i] = "FC1A unlabelled"
    record = fb.run_pipeline(W, types, stripped, 5, lambda m: None)
    assert "blocked" in record and "fc_column" in record["blocked"]
    # strip glomerulus markers from most PFNs -> glomerulus coverage BLOCKED
    noglom = instances.copy()
    pfn_pos = np.flatnonzero(np.char.startswith(types, "PFN"))
    for i in pfn_pos[: int(0.5 * pfn_pos.size)]:
        noglom[i] = str(instances[i]).replace("_L", "_x").replace("_R", "_x")
    record2 = fb.run_pipeline(W, types, noglom, 5, lambda m: None)
    assert "blocked" in record2
    assert "labelled_pfn_glomerulus" in record2["blocked"]
    # zero out the excitatory edges -> degenerate two-hop BLOCKED
    Wz = sparse.csr_matrix(np.minimum(W.todense(), 0.0))
    record3 = fb.run_pipeline(Wz, types, instances, 5, lambda m: None)
    assert "blocked" in record3 and "degenerate" in record3["blocked"]
    # remove only the one-hop FC<-PFN edges -> Bar 2 degenerate BLOCKED
    Wd = np.asarray(W.todense())
    fc_mask = np.char.startswith(types, "FC")
    pfn_mask = np.char.startswith(types, "PFN")
    Wd[np.ix_(fc_mask, pfn_mask)] = 0.0
    record4 = fb.run_pipeline(sparse.csr_matrix(Wd), types, instances, 5,
                              lambda m: None)
    assert "blocked" in record4 and "one-hop" in record4["blocked"]


def test_composition_check():
    representative = {"hDelta": "hDeltaA", "vDelta": "vDeltaM", "FC": "FC2B"}
    types = []
    for row, count in fb.COMPOSITION.items():
        types.extend([representative.get(row, row)] * count)
    assert fb.composition_check(np.asarray(types)) == []
    assert len(types) == 1399  # the frozen table's total
    mismatches = fb.composition_check(np.asarray(types[:-1]))
    assert mismatches and any("PFL3" in m for m in mismatches)


def test_frozen_constants_match_registration():
    assert fb.N_NULLS == 200 and fb.REWIRE_SEED_BASE == 4242
    assert fb.ALPHA == 0.05 and fb.MIN_COVERAGE == 0.90
    assert fb.SECTOR_DEG == 40.0 and fb.ANTIPODE_DEG == 180.0
    assert (fb.GLOM_MIN, fb.GLOM_MAX, fb.N_GLOMS) == (2, 9, 8)
    assert fb.COMPOSITION == {
        "PFNa": 58, "PFNd": 40, "PFNm_a": 21, "PFNm_b": 26,
        "PFNp_a": 64, "PFNp_b": 136, "PFNp_c": 40, "PFNp_d": 28,
        "PFNp_e": 23, "PFNv": 20,
        "hDelta": 189, "vDelta": 430, "FC": 274,
        "PFL1": 14, "PFL2": 12, "PFL3": 24,
    }
    assert fb.LABELLED_PFN_ROWS == ("PFNa", "PFNd", "PFNm_a", "PFNm_b",
                                    "PFNv")
    assert sum(fb.COMPOSITION[row] for row in fb.LABELLED_PFN_ROWS) == 165
    assert fb.TYPE_PATTERNS == tuple(fb.ROW_PATTERNS.values())
    assert set(fb.ROW_PATTERNS) == set(fb.COMPOSITION)


def test_check_prerequisites_reports_cloud_blockers():
    missing = fb.check_prerequisites()
    assert any("runtime" in m for m in missing) or missing == []
