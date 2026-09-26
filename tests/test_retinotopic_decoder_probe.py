"""Contract tests for the preregistered retinotopic recurrence probe.

These tests use synthetic summaries only.  They must never run the registered
MaleCNS neural outcomes before the implementation checkpoint is frozen.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from flygi.config import load_config
from flygi.encoding.retinotopic import ColumnarColourProjection

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/probe_retinotopic_decoder.py"
SPEC = importlib.util.spec_from_file_location("_flygi_test_retinotopic_probe", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _condition(
    errors: dict[tuple[int, int], float], *, legacy_offset: float | None = None
) -> dict[str, Any]:
    trials: list[dict[str, Any]] = []
    for center in MODULE.CENTERS:
        for from_colour, to_colour in MODULE.TRANSITIONS:
            trial: dict[str, Any] = {
                "center_xy": list(center),
                "from_colour": from_colour,
                "to_colour": to_colour,
                "error_cells": errors[center],
            }
            if legacy_offset is not None:
                trial["legacy_redecode"] = {
                    "error_cells": errors[center] + legacy_offset,
                }
            trials.append(trial)
    return {"changed_trials": trials}


def test_argmax_ties_choose_the_lowest_index() -> None:
    x = np.zeros(64, dtype=np.float32)
    y = np.zeros(64, dtype=np.float32)
    x[[7, 11]] = 3.0
    y[[4, 19]] = 2.0

    assert MODULE._predict(x, y) == (7, 4)


def test_registered_patch_uses_arc_y_rows_x_columns_and_exactly_25_cells() -> None:
    grid = MODULE._grid(1, center=(12, 32), to_colour=7)
    changed = np.argwhere(grid != 1)

    assert changed.shape == (25, 2)
    assert set(map(tuple, changed)) == {(y, x) for y in range(30, 35) for x in range(10, 15)}
    assert np.all(grid[30:35, 10:15] == 7)


def test_encoder_column_contract_passes_correct_orientation_and_rejects_swap() -> None:
    types = [f"T{index}" for index in range(8)]
    node_indices: list[int] = []
    hex1: list[int] = []
    hex2: list[int] = []
    type_names: list[str] = []
    for first in range(8):
        for second in range(10):
            for type_name in types:
                node_indices.append(len(node_indices))
                hex1.append(first)
                hex2.append(second)
                type_names.append(type_name)
    columns = {
        "node_indices": np.asarray(node_indices, dtype=np.int64),
        "hex1": np.asarray(hex1, dtype=np.int64),
        "hex2": np.asarray(hex2, dtype=np.int64),
        "type": np.asarray(type_names),
    }
    projection = ColumnarColourProjection(columns, len(node_indices))

    correct = MODULE._encoder_column_contract(
        projection,
        columns,
        grid_row=20,
        grid_column=50,
        expected_hex1=2,
        expected_hex2=7,
        expected_neurons=8,
    )
    swapped = MODULE._encoder_column_contract(
        projection,
        columns,
        grid_row=50,
        grid_column=20,
        expected_hex1=2,
        expected_hex2=7,
        expected_neurons=8,
    )

    assert correct["passed"] is True
    assert correct["mapped_hex1"] == 2
    assert correct["mapped_hex2"] == 7
    assert correct["changed_histogram_column_keys"] == [27]
    assert swapped["passed"] is False
    assert swapped["checks"]["grid_row_maps_to_hex1"] is False
    assert swapped["checks"]["grid_column_maps_to_hex2"] is False
    assert swapped["checks"]["changed_histogram_column_is_expected"] is False


def test_scientific_gate_counts_seven_of_eight_as_descriptive_bar() -> None:
    real_errors = {center: 1.0 for center in MODULE.CENTERS}
    null_errors = {center: 2.0 for center in MODULE.CENTERS}
    off_errors = {center: 2.0 for center in MODULE.CENTERS}
    null_errors[MODULE.CENTERS[-1]] = 1.0
    off_errors[MODULE.CENTERS[-1]] = 1.0
    conditions = {
        "corrected_real": _condition(real_errors, legacy_offset=1.0),
        "corrected_null": _condition(null_errors),
        "corrected_recurrence_off": _condition(off_errors),
    }

    passed = MODULE._scientific_summary(conditions)

    assert passed["strict_win_counts"]["corrected_null"] == 7
    assert passed["strict_win_counts"]["corrected_recurrence_off"] == 7
    assert passed["promotion_passed"] is True

    null_errors[MODULE.CENTERS[-2]] = 1.0
    failed = MODULE._scientific_summary(
        {
            **conditions,
            "corrected_null": _condition(null_errors),
        }
    )
    assert failed["strict_win_counts"]["corrected_null"] == 6
    assert failed["single_null_dependency_gate_passed"] is False
    assert failed["promotion_passed"] is False

    # Eight strict wins do not rescue a missed 20% global effect-size gate:
    # every conjunct remains load-bearing and ties never count as wins.
    shallow_control = {center: 1.1 for center in MODULE.CENTERS}
    ratio_failed = MODULE._scientific_summary(
        {
            **conditions,
            "corrected_null": _condition(shallow_control),
        }
    )
    assert ratio_failed["strict_win_counts"]["corrected_null"] == 8
    assert ratio_failed["checks"]["corrected_real_median_le_80pct_null"] is False
    assert ratio_failed["promotion_passed"] is False


def test_recurrence_off_contract_requires_same_real_csr_and_gain_only() -> None:
    real = {
        "graph_sha256": MODULE.EXPECTED_HASHES["real"]["graph.npz"],
        "connectivity_object_id": 100,
        "connectivity_data_object_id": 200,
        "copy_connectivity": False,
        "parameters": {
            "internal_steps": 4,
            "leak": 0.3,
            "recurrent_gain": 2.0,
            "bias": 0.0,
        },
        "effective_parameters": {
            "internal_steps": 4,
            "leak": float(np.float32(0.3)),
            "recurrent_gain": float(np.float32(2.0)),
            "bias": float(np.float32(0.0)),
        },
    }
    off = {
        **real,
        "parameters": {**real["parameters"], "recurrent_gain": 0.0},
        "effective_parameters": {
            **real["effective_parameters"],
            "recurrent_gain": float(np.float32(0.0)),
        },
    }
    conditions = {
        "corrected_real": {"network_contract": real},
        "corrected_recurrence_off": {"network_contract": off},
    }

    assert all(MODULE._real_off_contract(conditions).values())

    copied = {**off, "connectivity_object_id": 101}
    failed = MODULE._real_off_contract(
        {
            **conditions,
            "corrected_recurrence_off": {"network_contract": copied},
        }
    )
    assert failed["same_live_csr_object"] is False

    extra_delta = {
        **off,
        "parameters": {**off["parameters"], "leak": 0.2},
    }
    failed = MODULE._real_off_contract(
        {
            **conditions,
            "corrected_recurrence_off": {"network_contract": extra_delta},
        }
    )
    assert failed["gain_is_only_parameter_difference"] is False

    hidden_effective_delta = {
        **off,
        "effective_parameters": {
            **off["effective_parameters"],
            "leak": float(np.float32(0.2)),
        },
    }
    failed = MODULE._real_off_contract(
        {
            **conditions,
            "corrected_recurrence_off": {"network_contract": hidden_effective_delta},
        }
    )
    assert failed["gain_is_only_declared_parameter_difference"] is True
    assert failed["gain_is_only_effective_parameter_difference"] is False
    assert failed["gain_is_only_parameter_difference"] is False


def test_rate_parameter_record_distinguishes_declared_and_effective_float32() -> None:
    parameters = MODULE.RateParameters(
        internal_steps=4,
        leak=0.3,
        recurrent_gain=2.0,
        bias=0.0,
    )

    record = MODULE._rate_parameter_record(parameters)

    assert record["declared"]["leak"] == 0.3
    assert record["effective_float32"]["leak"] == float(np.float32(0.3))
    assert record["effective_float32"]["recurrent_gain"] == 2.0


def test_exact_six_thread_command_contract_fails_before_config_or_graph_load(
    tmp_path: Path, monkeypatch: Any
) -> None:
    monkeypatch.delenv("FLYGI_SPMV_THREADS", raising=False)

    def forbidden(_path: Path) -> Any:
        raise AssertionError("config load must not happen after thread-contract failure")

    monkeypatch.setattr(MODULE, "_config_contract", forbidden)
    args = argparse.Namespace(
        config=tmp_path / "config.yaml",
        real_runtime=tmp_path / "real",
        null_runtime=tmp_path / "null",
    )

    with pytest.raises(MODULE.ContractViolation) as raised:
        MODULE._execute_probe(args)

    assert "FLYGI_SPMV_THREADS=6" in str(raised.value)
    assert raised.value.observations["action_paths_constructed"] is False
    assert raised.value.observations["real_rate_parameters"]["effective_float32"]["leak"] == float(
        np.float32(0.3)
    )


def test_reduction_is_median_of_four_then_median_of_eight() -> None:
    trials = []
    expected_center_medians: dict[tuple[int, int], float] = {}
    for index, center in enumerate(MODULE.CENTERS):
        values = [float(index), float(index + 2), float(index + 4), float(index + 100)]
        expected_center_medians[center] = float(index + 3)
        for (from_colour, to_colour), value in zip(MODULE.TRANSITIONS, values, strict=True):
            trials.append(
                {
                    "center_xy": list(center),
                    "from_colour": from_colour,
                    "to_colour": to_colour,
                    "error_cells": value,
                }
            )

    reduced = MODULE._condition_center_errors({"changed_trials": trials})

    assert reduced == expected_center_medians
    assert float(np.median(list(reduced.values()))) == 6.5


def test_child_config_parsed_semantic_delta_is_exactly_registered() -> None:
    parent = load_config(ROOT / "configs/literal_rate_bioeye_lc_surprise.yaml")
    child = load_config(ROOT / "configs/literal_rate_bioeye_lc_surprise_arcxy.yaml")

    assert MODULE._leaf_differences(asdict(parent), asdict(child)) == [
        "decoder.retinotopic_coordinate_convention",
        "future.experiment.name",
    ]


def test_invalid_contract_writes_envelope_and_returns_one(tmp_path: Path, monkeypatch: Any) -> None:
    output = tmp_path / "invalid.json"

    def fail(_args: Any) -> dict[str, Any]:
        raise MODULE.ContractViolation(
            "synthetic contract failure",
            observations={"config_contract": {"child_sha256": "observed"}},
        )

    monkeypatch.setattr(MODULE, "_execute_probe", fail)
    status = MODULE.main(
        [
            "--config",
            str(tmp_path / "not-loaded.yaml"),
            "--real-runtime",
            str(tmp_path / "not-loaded-real"),
            "--null-runtime",
            str(tmp_path / "not-loaded-null"),
            "--output",
            str(output),
            "--require-promotion",
        ]
    )

    artifact = json.loads(output.read_text(encoding="utf-8"))
    assert status == 1
    assert artifact["status"] == "invalid"
    assert artifact["contract_valid"] is False
    assert artifact["scientific_verdict"] is None
    assert artifact["error"]["type"] == "ContractViolation"
    assert "synthetic contract failure" in artifact["error"]["message"]
    assert artifact["invalid_contract_observations"]["config_contract"] == {
        "child_sha256": "observed"
    }
    assert artifact["provenance"]["probe_sha256"]
    assert artifact["provenance"]["experiments_sha256"]


def test_nonfinite_invalid_observations_are_sanitized_to_valid_json(
    tmp_path: Path, monkeypatch: Any
) -> None:
    output = tmp_path / "nonfinite-invalid.json"

    def fail(_args: Any) -> dict[str, Any]:
        raise MODULE.ContractViolation(
            "synthetic nonfinite failure",
            observations={
                "diagnostic": {
                    "nan": float("nan"),
                    "positive": np.float32(np.inf),
                    "negative": -float("inf"),
                }
            },
        )

    monkeypatch.setattr(MODULE, "_execute_probe", fail)
    status = MODULE.main(
        [
            "--config",
            "unused",
            "--real-runtime",
            "unused",
            "--null-runtime",
            "unused",
            "--output",
            str(output),
        ]
    )

    artifact = json.loads(output.read_text(encoding="utf-8"))
    diagnostic = artifact["invalid_contract_observations"]["diagnostic"]
    assert status == 1
    assert diagnostic == {
        "nan": "nonfinite:nan",
        "positive": "nonfinite:+inf",
        "negative": "nonfinite:-inf",
    }


def test_unexpected_runtime_error_still_writes_valid_invalid_envelope(
    tmp_path: Path, monkeypatch: Any
) -> None:
    output = tmp_path / "unexpected-runtime.json"

    def crash(_args: Any, _observations: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("synthetic unexpected crash")

    monkeypatch.setattr(MODULE, "_execute_probe_inner", crash)
    status = MODULE.main(
        [
            "--config",
            "unused",
            "--real-runtime",
            "unused",
            "--null-runtime",
            "unused",
            "--output",
            str(output),
        ]
    )

    artifact = json.loads(output.read_text(encoding="utf-8"))
    assert status == 1
    assert artifact["status"] == "invalid"
    assert artifact["error"]["type"] == "ContractViolation"
    assert artifact["invalid_contract_observations"]["unexpected_runtime_error"] == {
        "type": "RuntimeError",
        "message": "synthetic unexpected crash",
    }


def test_require_promotion_returns_two_for_contract_valid_scientific_failure(
    tmp_path: Path, monkeypatch: Any
) -> None:
    output = tmp_path / "scientific-fail.json"
    monkeypatch.setattr(
        MODULE,
        "_execute_probe",
        lambda _args: {
            "status": "complete",
            "contract_valid": True,
            "scientific_verdict": "fail",
        },
    )

    status = MODULE.main(
        [
            "--config",
            "unused",
            "--real-runtime",
            "unused",
            "--null-runtime",
            "unused",
            "--output",
            str(output),
            "--require-promotion",
        ]
    )

    artifact = json.loads(output.read_text(encoding="utf-8"))
    assert status == 2
    assert artifact["status"] == "complete"
    assert artifact["contract_valid"] is True
    assert artifact["scientific_verdict"] == "fail"


def test_existing_output_is_refused_before_any_probe_load(tmp_path: Path, monkeypatch: Any) -> None:
    output = tmp_path / "existing.json"
    original = b"do not overwrite\n"
    output.write_bytes(original)
    called = False

    def forbidden(_args: Any) -> dict[str, Any]:
        nonlocal called
        called = True
        raise AssertionError("probe must not be entered")

    monkeypatch.setattr(MODULE, "_execute_probe", forbidden)
    status = MODULE.main(
        [
            "--config",
            "unused",
            "--real-runtime",
            "unused",
            "--null-runtime",
            "unused",
            "--output",
            str(output),
        ]
    )

    assert status == 1
    assert called is False
    assert output.read_bytes() == original
