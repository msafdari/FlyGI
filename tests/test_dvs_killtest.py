"""Tests for the PURE plumbing of scripts/arenas/dvs_killtest.py
(H-T4T5-DVS-GESTURE). The measurement is data-gated and local; what is
testable here: the AEDAT 3.1 polarity reader on synthetic packed bytes,
window placement, the event-count comparator features, the exact
binomial, and the frozen three-bar verdict assembly."""

import importlib.util
import math
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "dvs_killtest", ROOT / "scripts/arenas/dvs_killtest.py")
dv = importlib.util.module_from_spec(_spec)
sys.modules["dvs_killtest"] = dv
_spec.loader.exec_module(dv)

_spec2 = importlib.util.spec_from_file_location(
    "dsec_killtest", ROOT / "scripts/arenas/dsec_killtest.py")
dk = importlib.util.module_from_spec(_spec2)
sys.modules["dsec_killtest"] = dk
_spec2.loader.exec_module(dk)


def _polarity_word(x, y, p, valid=1):
    return (x << 17) | (y << 2) | (p << 1) | valid


def _packet(events, tsovf=0, etype=1, esize=8):
    """Pack an AEDAT 3.1 packet from (x, y, p, t_us, valid) tuples."""
    header = struct.pack("<HHIIIIII", etype, 0, esize, 0, tsovf,
                         len(events), len(events), len(events))
    body = b"".join(
        struct.pack("<II", _polarity_word(x, y, p, v), t)
        for x, y, p, t, v in events)
    return header + body


def test_aedat_parser_synthetic_round_trip():
    events = [(5, 7, 1, 1000, 1), (120, 3, 0, 2000, 1), (64, 64, 1, 3000, 1)]
    buf = b"#!AER-DAT3.1\r\n#comment line\r\n" + _packet(events)
    x, y, p, t = dv.read_aedat31_polarity(buf)
    assert x.tolist() == [5, 120, 64]
    assert y.tolist() == [7, 3, 64]
    assert p.tolist() == [1, 0, 1]
    assert t.tolist() == [1000.0, 2000.0, 3000.0]


def test_aedat_parser_validity_overflow_and_foreign_packets():
    # one invalid event is dropped; a non-polarity packet is skipped;
    # the timestamp-overflow word shifts by 31 bits
    ev = [(1, 2, 1, 500, 1), (3, 4, 0, 600, 0)]
    special = struct.pack("<HHIIIIII", 0, 0, 4, 0, 0, 2, 2, 2) + b"\x00" * 8
    buf = b"#hdr\n" + special + _packet(ev, tsovf=1)
    x, y, p, t = dv.read_aedat31_polarity(buf)
    assert x.tolist() == [1] and p.tolist() == [1]
    assert t[0] == 500.0 + float(1 << 31)


def test_aedat_parser_truncated_tail_is_safe():
    buf = b"#h\n" + _packet([(1, 1, 1, 10, 1)]) + b"\x01\x02\x03"
    x, _, _, _ = dv.read_aedat31_polarity(buf)
    assert x.size == 1


def test_expand_subwindow_drive_matches_dense_layout():
    # Regression for the 2026-10-03 memory fix: the per-trial dense
    # (k, n_sub, n_nodes) drive tensors (measured ~21 GB held state over
    # the real dataset, pre-fix) are replaced by (m, n_sub, n_cols) grids
    # expanded one sub-window at a time. The expansion must reproduce the
    # old layout bit for bit.
    rng = np.random.default_rng(7)
    m, n_sub, n_cols, n_nodes = 3, 2, 5, 7
    driven_idx = np.array([1, 4, 2])
    driven_cols = np.array([0, 3, 2])
    input_drive = 7.5
    cum = rng.normal(size=(m, n_sub, n_cols))
    dense = np.zeros((m, n_sub, n_nodes))
    dense[:, :, driven_idx] = input_drive * cum[:, :, driven_cols]
    out = np.zeros((n_nodes, m))
    for k in range(n_sub):
        got = dv.expand_subwindow_drive(cum, k, driven_idx, driven_cols,
                                        input_drive, out)
        assert np.array_equal(got, dense[:, k, :].T)


def test_load_split_binner_bins_filtered_events_and_drops_them(tmp_path):
    # The binner must receive the same in-frame-filtered events the eager
    # layout stored, with the label row's own t0/t1 -- and the raw arrays
    # must not be kept on the trial.
    events = [(5, 7, 1, 1000, 1), (200, 3, 0, 1500, 1),  # x=200: out of frame
              (64, 64, 1, 2000, 1)]
    (tmp_path / "a.aedat").write_bytes(b"#hdr\n" + _packet(events))
    (tmp_path / "a_labels.csv").write_text(
        "class,startTime_usec,endTime_usec\n2,900,1600\n5,1900,2100\n")
    (tmp_path / "split.txt").write_text("a.aedat\n")
    logs = []
    plain = dv.load_split(tmp_path, "split.txt", logs.append)
    calls = []

    def binner(evts, t0, t1):
        calls.append((evts, t0, t1))
        return ("binned", t0, t1)

    binned = dv.load_split(tmp_path, "split.txt", logs.append, binner=binner)
    assert len(plain) == len(binned) == len(calls) == 2
    for trial_plain, trial_binned, (evts, t0, t1) in zip(plain, binned, calls):
        assert "events" not in trial_binned
        assert trial_binned["windows"] == ("binned", t0, t1)
        assert (t0, t1) == (trial_plain["t0"], trial_plain["t1"])
        for got, want in zip(evts, trial_plain["events"]):
            assert np.array_equal(got, want)
    assert calls[0][0][0].tolist() == [5, 64]  # out-of-frame event filtered


def test_window_starts_spacing_and_short_trials():
    s = dv.window_starts(0.0, 6_000_000.0)          # 6 s trial
    assert s.size == dv.WINDOWS_PER_TRIAL
    assert s[0] == 0.0 and s[-1] == 6_000_000.0 - 250_000.0
    assert np.all(np.diff(s) > 0)
    short = dv.window_starts(0.0, 600_000.0)        # 0.6 s -> 2 windows fit
    assert short.size == 2
    assert dv.window_starts(0.0, 100_000.0).size == 0   # nothing fits


def test_event_count_features_shape_and_values():
    signed = np.array([[[1.0, -2.0], [0.0, 3.0]]])[0]   # (n_sub=2, n_cols=2)
    counts = np.abs(signed)
    f = dv.event_count_features(signed, counts)
    assert f.shape == (4,)
    assert f.tolist() == [1.0, 5.0, 1.0, 1.0]


def test_exact_binomial():
    # chance: 1/11; 288 trials at exactly chance should NOT be significant
    assert dv.exact_binomial_above_chance(26, 288) > 0.4
    # clearly above chance is
    assert dv.exact_binomial_above_chance(60, 288) < 1e-6
    assert math.isnan(dv.exact_binomial_above_chance(0, 0))


def _seed_rows(real, null, ec, chance_p=1e-9):
    return [{"seed": s, "real_acc": real[s], "null_acc": null[s],
             "event_count_acc": ec[s], "twin_acc": 0.0,
             "real_chance_p": chance_p} for s in range(3)]


def test_verdict_pass_and_kill_paths():
    n_cells = 18    # 6 subjects x 3 seeds
    good = np.full(n_cells, 0.6)
    weak = np.full(n_cells, 0.4)
    cells = {"real": good, "null": weak, "event_count": weak, "twin": weak}
    rows = _seed_rows([0.6] * 3, [0.4] * 3, [0.4] * 3)
    out = dv.assemble_verdict(rows, cells, dk.paired_sign_test_less)
    assert out["verdict"] == "PASS", out
    # kill: chance bar fails in one seed
    rows_bad = _seed_rows([0.6] * 3, [0.4] * 3, [0.4] * 3)
    rows_bad[1]["real_chance_p"] = 0.5
    out2 = dv.assemble_verdict(rows_bad, cells, dk.paired_sign_test_less)
    assert out2["verdict"] == "KILL"
    # kill: real loses to the event-count comparator
    cells3 = dict(cells, event_count=np.full(n_cells, 0.7))
    rows3 = _seed_rows([0.6] * 3, [0.4] * 3, [0.7] * 3)
    out3 = dv.assemble_verdict(rows3, cells3, dk.paired_sign_test_less)
    assert out3["verdict"] == "KILL"
    assert not out3["bars"]["real_beats_event_count"]
    # kill: sign test significant but pooled majority missing
    rows4 = _seed_rows([0.6, 0.39, 0.39], [0.4, 0.40, 0.40], [0.4] * 3)
    out4 = dv.assemble_verdict(rows4, cells, dk.paired_sign_test_less)
    assert not out4["bars"]["real_beats_null"]


def test_frozen_constants_match_registration():
    assert dv.WINDOWS_PER_TRIAL == 6
    assert dv.WINDOW_MS == 250.0 and dv.TAIL_MS == 250.0
    assert dv.DT_SUB_MS == 10.0
    assert dv.TRAIN_PER_CLASS == 40
    assert dv.SEEDS == (0, 1, 2) and dv.REWIRE_SEED_BASE == 4242
    assert dv.N_CLASSES == 11
    assert dv.MIN_TRAIN_TRIALS == 600 and dv.MIN_TEST_TRIALS == 150
    assert dv.MAX_UNSTABLE_FRACTION == 0.20


def test_check_prerequisites_reports_cloud_blockers():
    missing = dv.check_prerequisites(None)
    assert any("--data-root" in m for m in missing)
