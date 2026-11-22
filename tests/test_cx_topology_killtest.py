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

# The map every fixture and pipeline call below names explicitly (the
# instruments accept no silent default; see the amendment of 2026-11-21).
MAP = cx.DEFAULT_RING_MAP


def test_wedge_index_registered_map_is_the_frozen_expression():
    # AC-1 as frozen 2026-10-10 (INVALIDATED 2026-11-21; kept so the
    # registered run reproduces): L_k beside R_k.
    reg = "registered"
    assert cx.wedge_index("EPG_L1", reg) == 0
    assert cx.wedge_index("EPG_R1", reg) == 1
    assert cx.wedge_index("EPG_L8", reg) == 14
    assert cx.wedge_index("EPG_R8", reg) == 15
    assert cx.wedge_index("PEN_a(PEN1)_L4_x", reg) == 6
    assert cx.wedge_index("no label here", reg) is None
    assert cx.wedge_index("EPG_L9", reg) is None     # out of 1..8


def test_wedge_index_amended_map_is_the_default():
    # AC-1 as amended 2026-11-21: right half unchanged, left reflected;
    # ring order L1 R1 L8 R2 L7 R3 L6 R4 L5 R5 L4 R6 L3 R7 L2 R8.
    assert cx.DEFAULT_RING_MAP == "amended"      # the command-line default
    order = ["L1", "R1", "L8", "R2", "L7", "R3", "L6", "R4",
             "L5", "R5", "L4", "R6", "L3", "R7", "L2", "R8"]
    for index, label in enumerate(order):
        assert cx.wedge_index(f"EPG(PB08)_{label}", "amended") == index
    for k in range(1, 9):                       # right half as registered
        assert (cx.wedge_index(f"EPG_R{k}", "amended")
                == cx.wedge_index(f"EPG_R{k}", "registered"))
    assert cx.wedge_index("no label here", "amended") is None
    assert cx.wedge_index("EPG_L9", "amended") is None   # range check unchanged
    with pytest.raises(ValueError):
        cx.wedge_index("EPG_L1", "some other map")


def test_the_map_is_a_required_argument_at_every_level():
    """No silent default: a call that forgets the map must raise, so a
    --ring-map registered run can never quietly use the amended map (or
    the reverse). The only default is the command-line flag."""
    with pytest.raises(TypeError):
        cx.wedge_index("EPG_L1")
    W, types, instances = _ring()
    with pytest.raises(TypeError):
        cx.run_pipeline(W, types, instances, 2, lambda m: None)
    with pytest.raises(TypeError):                # keyword-only
        cx.run_pipeline(W, types, instances, 2, lambda m: None, None,
                        "amended")


def _ring(n_per_wedge=3, pen_per_side=1, offset_l=1, offset_r=-1,
          noise=0.0, seed=0, ring_map=None):
    """Synthetic compass: EPG tiled over 16 wedges; PEN_a L/R shifted
    by the given offsets; PEN_b mirrored; Delta7 global inhibition.
    Returns (csr W[post,pre], types, instances). EPG labels are written
    with the INVERSE of the named ring map (default: the instrument's
    default), so the fixture follows the parser. That makes this gate
    blind to which map is right -- the 2026-11-21 finding -- and is why
    test_registered_map_misreads_an_anatomically_labelled_ring exists."""
    from flygi.compass_map import ring_label
    ring_map = ring_map or MAP
    rng = np.random.default_rng(seed)
    types, instances = [], []
    epg, pen = [], {"PEN_a_L": [], "PEN_a_R": [], "PEN_b_L": [], "PEN_b_R": []}
    wedge_name = lambda w: "_%s%d" % ring_label(w, ring_map)
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
    wedges = np.array([cx.wedge_index(s, MAP) for s in instances[epg_idx]])
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


def _ring_stats(parse_map, label_map):
    W, types, instances = _ring(ring_map=label_map)
    epg_idx = np.flatnonzero(types == "EPG")
    wedges = np.array([cx.wedge_index(s, parse_map)
                       for s in instances[epg_idx]])
    pen_a = np.flatnonzero(types == "PEN_a(PEN1)")
    pen_l = np.array([i for i in pen_a if "_L" in instances[i]])
    pen_r = np.array([i for i in pen_a if "_R" in instances[i]])
    M = cx.wedge_aggregate(
        cx.two_hop(W, epg_idx, np.concatenate([pen_l, pen_r])), wedges)
    M_l = cx.wedge_aggregate(cx.two_hop(W, epg_idx, pen_l), wedges)
    M_r = cx.wedge_aggregate(cx.two_hop(W, epg_idx, pen_r), wedges)
    return (cx.bandedness(M), cx.mirror_peak(M_l, M_r),
            cx.spectral_context(M)["residual_deg"])


def test_registered_map_misreads_an_anatomically_labelled_ring():
    """THE REGRESSION TEST for the 2026-11-21 instrument-bug finding.

    A perfect ring whose cells carry anatomical labels (the amended
    order) is read correctly by the amended map and misread by the
    registered one: the registered map reflects the left half-ring, so
    most neighbour coupling lands outside the +/-2 band, the opposite
    left/right PEN offsets blur, and the blind ordering check sits
    45 to 51 deg off -- the 2026-10-10 run recorded 46.6 deg and it
    was read as inconclusive. Fails on the pre-amendment code, where
    only the registered map existed.

    The two spectral bounds are the ATTAINABLE ranges, not one build's
    value: on a perfect ring the two Laplacian eigenvalues the check
    uses are exactly equal, so the eigensolver may return any basis of
    that plane, and the check tries rotations in 22.5 deg steps. A
    correctly read ring therefore lands anywhere in 0..11.25 deg and
    the misread one anywhere in 45.0..50.6 deg (49.2 with numpy on
    Apple Accelerate). Bandedness and the mirror-peak are exact."""
    banded, mirror, resid = _ring_stats("amended", "amended")
    assert banded == 1.0 and mirror == pytest.approx(1.0)
    assert resid < 11.3
    banded_reg, mirror_reg, resid_reg = _ring_stats("registered", "amended")
    assert banded_reg == pytest.approx(0.25)    # 8 of 32 neighbour pairs
    assert mirror_reg == pytest.approx(0.0625)
    assert 44.0 < resid_reg < 51.0              # a reflected half-ring
    # and the converse: the fault is symmetric in which map is "true",
    # which is why a self-labelled fixture could never have caught it
    assert _ring_stats("registered", "registered")[0] == 1.0
    assert _ring_stats("amended", "registered")[0] == pytest.approx(0.25)


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
    record = cx.run_pipeline(W, types, instances, 60, logs.append,
                             ring_map=MAP)
    assert "blocked" not in record, record
    assert record["bars"] == {"banded": True, "shifter": True}
    assert record["verdict"] == "PASS"
    assert record["p_banded"] < 0.05 and record["p_mirror_peak"] < 0.05
    # destroyed ring: a single rewire of the synthetic compass should
    # kill at least one bar through the same frozen pipeline
    from flygi.connectome.nulls import degree_preserving_rewire
    broken, _ = degree_preserving_rewire(W, seed=7)
    record2 = cx.run_pipeline(broken, types, instances, 60, logs.append,
                              ring_map=MAP)
    assert "blocked" not in record2
    assert record2["verdict"] == "KILL"


def test_pipeline_blocked_paths():
    W, types, instances = _ring()
    # strip wedge labels from most EPGs -> coverage BLOCKED
    stripped = instances.copy()
    epg_pos = np.flatnonzero(types == "EPG")
    for i in epg_pos[: int(0.5 * epg_pos.size)]:
        stripped[i] = "EPG unlabelled"
    record = cx.run_pipeline(W, types, stripped, 5, lambda m: None,
                             ring_map=MAP)
    assert "blocked" in record and "coverage" in record["blocked"]
    # zero out the excitatory loops -> degenerate two-hop BLOCKED
    Wz = sparse.csr_matrix(np.minimum(W.todense(), 0.0))
    record2 = cx.run_pipeline(Wz, types, instances, 5, lambda m: None,
                              ring_map=MAP)
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
