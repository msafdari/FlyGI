"""Tests for scripts/arenas/cx_topology_killtest.py
(H-CX-RING-TOPOLOGY, Task 9 Stage A). The real measurement is
data-gated and local; the PIPELINE is pure, so what is testable
in-cloud is nearly everything: the AC-1 wedge parser, the two-hop /
aggregation / bandedness / offset / separation mechanics, the
empirical p, the verdict bars, and -- the load-bearing one -- the full
pipeline end-to-end on a synthetic ring compass, driven through the
REAL degree-preserving-rewire machinery, asserting PASS on the ring
and the nulls scoring below it, plus KILL when the ring is destroyed."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

_spec = importlib.util.spec_from_file_location(
    "cx_topology_killtest", ROOT / "scripts/arenas/cx_topology_killtest.py")
cx = importlib.util.module_from_spec(_spec)
sys.modules["cx_topology_killtest"] = cx
_spec.loader.exec_module(cx)


def test_wedge_index_verbatim_mapping():
    assert cx.wedge_index("EPG_L1") == 0
    assert cx.wedge_index("EPG_R1") == 1
    assert cx.wedge_index("EPG_L8") == 14
    assert cx.wedge_index("EPG_R8") == 15
    assert cx.wedge_index("PEN_a(PEN1)_L4_x") == 6
    assert cx.wedge_index("no label here") is None
    assert cx.wedge_index("EPG_L9") is None     # out of 1..8


def _ring(n_per_wedge=3, pen_per_side=1, offset_l=1, offset_r=-1,
          noise=0.0, seed=0):
    """Synthetic compass: EPG tiled over 16 wedges; PEN_a L/R shifted
    by the given offsets; PEN_b mirrored; Delta7 global inhibition.
    Returns (csr W[post,pre], types, instances)."""
    rng = np.random.default_rng(seed)
    types, instances = [], []
    epg, pen = [], {"PEN_a_L": [], "PEN_a_R": [], "PEN_b_L": [], "PEN_b_R": []}
    wedge_name = lambda w: f"_{'L' if w % 2 == 0 else 'R'}{w // 2 + 1}"
    for w in range(16):
        for k in range(n_per_wedge):
            epg.append((len(types), w))
            types.append("EPG")
            instances.append(f"EPG{wedge_name(w)}.{k}")
    for label, tname, off in (("PEN_a_L", "PEN_a(PEN1)", offset_l),
                              ("PEN_a_R", "PEN_a(PEN1)", offset_r),
                              ("PEN_b_L", "PEN_b(PEN2)", offset_l),
                              ("PEN_b_R", "PEN_b(PEN2)", offset_r)):
        side = label[-1]
        for w in range(16):
            for _ in range(pen_per_side):
                pen[label].append((len(types), w, off))
                types.append(tname)
                instances.append(f"{tname}_{side}{w // 2 + 1}")
    d7 = []
    for k in range(8):
        d7.append(len(types))
        types.append("Delta7")
        instances.append(f"Delta7.{k}")
    n = len(types)
    W = np.zeros((n, n))
    for label, cells in pen.items():
        for (p_i, p_w, off) in cells:
            for (e_i, e_w) in epg:
                if e_w == p_w:
                    W[p_i, e_i] = 2.0          # PEN <- same-wedge EPG
                if e_w == (p_w + off) % 16:
                    W[e_i, p_i] = 2.0          # EPG(+off) <- PEN
    for (e_i, _) in epg:
        for d in d7:
            W[e_i, d] = -1.0                   # global inhibition
            W[d, e_i] = 0.5
    if noise:
        # jitter EXISTING edges only: dense noise would make the graph
        # complete and leave the degree-preserving rewire zero legal swaps
        mask = W != 0
        W[mask] *= 1.0 + noise * rng.standard_normal(int(mask.sum()))
    return sparse.csr_matrix(W), np.array(types), np.array(instances)


def test_metrics_on_synthetic_ring():
    W, types, instances = _ring()
    epg_idx = np.flatnonzero(types == "EPG")
    wedges = np.array([cx.wedge_index(s) for s in instances[epg_idx]])
    pen_a = np.flatnonzero(types == "PEN_a(PEN1)")
    pen_l = np.array([i for i in pen_a if "_L" in instances[i]])
    pen_r = np.array([i for i in pen_a if "_R" in instances[i]])
    M_l = cx.wedge_aggregate(cx.two_hop(W, epg_idx, pen_l), wedges)
    M_r = cx.wedge_aggregate(cx.two_hop(W, epg_idx, pen_r), wedges)
    assert cx.offset(M_l) == (1, True)
    assert cx.offset(M_r) == (-1, True)
    both = np.concatenate([pen_l, pen_r])
    M = cx.wedge_aggregate(cx.two_hop(W, epg_idx, both), wedges)
    assert cx.bandedness(M) == 1.0             # all mass within +/-1
    assert cx.spectral_context(M)["residual_deg"] < 15.0


def _shift_matrix(d):
    M = np.zeros((16, 16))
    for i in range(16):
        M[(i + d) % 16, i] = 1.0
    return M


def test_mirror_peak_and_context_stats():
    # adopted statistic: perfect mirror (+1 vs -1) -> 1.0, either chirality
    assert cx.mirror_peak(_shift_matrix(1), _shift_matrix(-1)) == 1.0
    assert cx.mirror_peak(_shift_matrix(-1), _shift_matrix(1)) == 1.0
    # same-side peaks are NOT a shifter -> 0
    assert cx.mirror_peak(_shift_matrix(1), _shift_matrix(1)) == 0.0
    # zero-offset concentration is not a shifter -> 0
    assert cx.mirror_peak(_shift_matrix(0), _shift_matrix(0)) == 0.0
    # empty side -> 0
    assert cx.mirror_peak(np.zeros((16, 16)), _shift_matrix(-1)) == 0.0
    # context stats keep their semantics
    assert abs(cx.mean_offset(_shift_matrix(1)) - 1.0) < 1e-12
    assert np.isnan(cx.mean_offset(_shift_matrix(8)))   # antipode-only
    assert cx.offset(_shift_matrix(8)) == (8, False)
    assert cx.offset(np.eye(16)) == (0, False)
    assert cx.offset(np.zeros((16, 16))) == (0, False)


def test_bandedness_and_empirical_p():
    M = np.zeros((16, 16))
    for i in range(16):
        M[i, i] = 1.0
        M[(i + 5) % 16, i] = 1.0
    assert abs(cx.bandedness(M) - 0.5) < 1e-12
    assert np.isnan(cx.bandedness(np.zeros((16, 16))))
    assert cx.empirical_p(0.9, [0.1] * 199) == 1.0 / 200.0
    assert cx.empirical_p(0.1, [0.1] * 199) == 1.0


def test_full_pipeline_pass_on_ring_and_kill_on_destroyed():
    W, types, instances = _ring(noise=0.01)
    logs = []
    record = cx.run_pipeline(W, types, instances, 60, logs.append)
    assert "blocked" not in record, record
    assert record["bars"] == {"banded": True, "shifter": True}
    assert record["verdict"] == "PASS"
    assert record["p_banded"] < 0.05 and record["p_mirror_peak"] < 0.05
    # destroyed ring: a single rewire of the synthetic compass should
    # kill at least one bar through the same frozen pipeline
    from flygi.connectome.nulls import degree_preserving_rewire
    broken, _ = degree_preserving_rewire(W, seed=7)
    record2 = cx.run_pipeline(broken, types, instances, 60, logs.append)
    assert "blocked" not in record2
    assert record2["verdict"] == "KILL"


def test_pipeline_blocked_paths():
    W, types, instances = _ring()
    # strip wedge labels from most EPGs -> coverage BLOCKED
    stripped = instances.copy()
    epg_pos = np.flatnonzero(types == "EPG")
    for i in epg_pos[: int(0.5 * epg_pos.size)]:
        stripped[i] = "EPG unlabelled"
    record = cx.run_pipeline(W, types, stripped, 5, lambda m: None)
    assert "blocked" in record and "coverage" in record["blocked"]
    # zero out the excitatory loops -> degenerate two-hop BLOCKED
    Wz = sparse.csr_matrix(np.minimum(W.todense(), 0.0))
    record2 = cx.run_pipeline(Wz, types, instances, 5, lambda m: None)
    assert "blocked" in record2 and "degenerate" in record2["blocked"]


def test_frozen_constants_match_registration():
    assert cx.N_WEDGES == 16 and cx.BAND == 2
    assert cx.N_NULLS == 200 and cx.REWIRE_SEED_BASE == 4242
    assert cx.ALPHA == 0.05
    assert cx.EXPECTED_COUNTS == {"EPG": 46, "PEN_a(PEN1)": 20,
                                  "PEN_b(PEN2)": 22, "Delta7": 42, "PEG": 18}
    assert cx.MIN_WEDGE_COVERAGE == 0.90
    assert cx.TYPE_PATTERNS == ("EPG", "PEN_a*", "PEN_b*", "Delta7", "PEG")


def test_check_prerequisites_reports_cloud_blockers():
    missing = cx.check_prerequisites()
    assert any("runtime" in m for m in missing) or missing == []
