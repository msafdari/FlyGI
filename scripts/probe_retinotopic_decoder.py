#!/usr/bin/env python3
"""Frozen premise killer for H-RETINO-SURPRISE-RECURRENCE.

This is a contract-first synthetic assay, not an ARC agent.  Fly rate dynamics
produce the expected and changed states; Python is limited to the registered
absolute-difference, retinotopic bin sums, coordinate argmax, and reductions.
The protocol, thresholds, and stop rule are frozen in ``EXPERIMENTS.yaml``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import traceback
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
import scipy
from numpy.typing import NDArray

from flygi.config import FlyGIConfig, load_config
from flygi.connectome.manifest import sha256_file
from flygi.decoding.retinotopic_saliency import RetinotopicSaliency
from flygi.dynamics import RateParameters, ScipyRateNetwork, load_runtime_connectome
from flygi.dynamics.runtime import RuntimeConnectome
from flygi.encoding.features import FEATURE_DIMENSION, ObservationFeatures
from flygi.encoding.retinotopic import RetinotopicOptions, build_columnar_colour_projection

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "flygi.retino-surprise-recurrence-probe.v1"
HYPOTHESIS = "H-RETINO-SURPRISE-RECURRENCE"
PARENT_CONFIG = ROOT / "configs/literal_rate_bioeye_lc_surprise.yaml"
EXPERIMENTS = ROOT / "EXPERIMENTS.yaml"

CENTERS: tuple[tuple[int, int], ...] = (
    (12, 32),
    (32, 12),
    (22, 44),
    (44, 22),
    (20, 49),
    (49, 20),
    (13, 42),
    (42, 13),
)
TRANSITIONS: tuple[tuple[int, int], ...] = ((1, 7), (7, 1), (3, 12), (12, 3))
CONDITIONS = ("corrected_real", "corrected_null", "corrected_recurrence_off")

EXPECTED_HASHES: Mapping[str, Mapping[str, str]] = {
    "real": {
        "manifest.json": "0286615f7cac594afea986742ed0113112e2d7322c853d4352e26eb8c16671e1",
        "graph.npz": "f5553b59d4efaab36600cee5c319d524e3023b27906642720c634f3a000babb9",
        "retinotopy.npz": "ebc2b699e541330097a257003c2346f367d4beda1f04e88b2aaa1e1542db1a8d",
        "node_metadata.npz": "2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c",
        "groups.npz": "09736379ce989268080f57b64f357e800cf446972007c1af2287a86b9985a89d",
    },
    "null": {
        "manifest.json": "5ac5e0dd233fa828260842fffa8e27286493fde0bff399b20e0d039c4355e082",
        "graph.npz": "b832cbbcc31d55b5d91ed14f6c32713d1fd69ae8b7c47a053af79fd28850a39b",
        "retinotopy.npz": "ebc2b699e541330097a257003c2346f367d4beda1f04e88b2aaa1e1542db1a8d",
        "node_metadata.npz": "2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c",
        "groups.npz": "09736379ce989268080f57b64f357e800cf446972007c1af2287a86b9985a89d",
    },
}
EXPECTED_PARENT_CONFIG_SHA256 = "99417e77f0528540be64b2d86dc64d6713805f83f231313fb0f7fe7190c16833"
EXPECTED_NODE_COUNT = 166_700
EXPECTED_EDGE_COUNT = 24_994_595
EXPECTED_POSITIVE = 15_180_624
EXPECTED_NEGATIVE = 9_813_971
EXPECTED_ZERO_INCOMING = 389
MAX_L1_ERROR = 3e-4


class ContractViolation(RuntimeError):
    """A preregistered contract failed, so no scientific verdict is valid."""

    def __init__(
        self,
        message: str,
        *,
        observations: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.observations = dict(observations or {})


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _sha256_array(array: NDArray[Any]) -> str:
    values = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(values.dtype.str.encode("ascii"))
    digest.update(str(values.shape).encode("ascii"))
    digest.update(values.tobytes())
    return digest.hexdigest()


def _byte_identical(left: NDArray[Any], right: NDArray[Any]) -> bool:
    return (
        left.dtype == right.dtype
        and left.shape == right.shape
        and np.ascontiguousarray(left).tobytes() == np.ascontiguousarray(right).tobytes()
    )


def _relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def _git_state() -> dict[str, Any]:
    def run(*arguments: str) -> str | None:
        try:
            return subprocess.check_output(
                ["git", *arguments], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    status = run("status", "--porcelain")
    tracked_status = run("status", "--porcelain", "--untracked-files=no")
    untracked = run("ls-files", "--others", "--exclude-standard")
    return {
        "commit": run("rev-parse", "HEAD"),
        "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": None if status is None else bool(status),
        "status": [] if not status else status.splitlines(),
        "tracked_dirty": None if tracked_status is None else bool(tracked_status),
        "tracked_status": [] if not tracked_status else tracked_status.splitlines(),
        "untracked_paths": [] if not untracked else untracked.splitlines(),
    }


def _leaf_differences(left: Any, right: Any, prefix: str = "") -> list[str]:
    """Return exact leaf paths whose parsed values differ."""

    if isinstance(left, Mapping) and isinstance(right, Mapping):
        paths: list[str] = []
        for key in sorted(set(left) | set(right), key=str):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in left or key not in right:
                paths.append(path)
            else:
                paths.extend(_leaf_differences(left[key], right[key], path))
        return paths
    if left != right:
        return [prefix]
    return []


def _observed_file(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {"path": _relative(path), "exists": path.is_file()}
    if record["exists"]:
        try:
            record["sha256"] = sha256_file(path)
        except OSError as exc:
            record["hash_error"] = f"{type(exc).__name__}: {exc}"
    return record


def _rate_parameter_record(parameters: RateParameters) -> dict[str, Any]:
    return {
        "declared": asdict(parameters),
        "effective_float32": {
            "internal_steps": int(parameters.internal_steps),
            "leak": float(np.float32(parameters.leak)),
            "recurrent_gain": float(np.float32(parameters.recurrent_gain)),
            "bias": float(np.float32(parameters.bias)),
        },
    }


def _config_contract(config_path: Path) -> tuple[FlyGIConfig, dict[str, Any]]:
    record: dict[str, Any] = {
        "parent": _observed_file(PARENT_CONFIG),
        "child": _observed_file(config_path),
        "expected_parent_sha256": EXPECTED_PARENT_CONFIG_SHA256,
    }
    parent_hash = record["parent"].get("sha256")
    if parent_hash != EXPECTED_PARENT_CONFIG_SHA256:
        raise ContractViolation(
            f"parent config hash changed: {parent_hash} != {EXPECTED_PARENT_CONFIG_SHA256}",
            observations={"config_contract": record},
        )
    try:
        parent = load_config(PARENT_CONFIG)
        child = load_config(config_path)
    except Exception as exc:
        record["load_error"] = f"{type(exc).__name__}: {exc}"
        raise ContractViolation(
            "parent or child config could not be loaded",
            observations={"config_contract": record},
        ) from exc
    differences = _leaf_differences(asdict(parent), asdict(child))
    expected = [
        "decoder.retinotopic_coordinate_convention",
        "future.experiment.name",
    ]
    if differences != expected:
        record["parsed_leaf_differences"] = differences
        raise ContractViolation(
            f"child config parsed differences are {differences}, expected {expected}",
            observations={"config_contract": record},
        )

    checks = {
        "encoder_kind": child.encoder.kind == "retinotopic_colour",
        "encoder_input_scale": child.encoder.input_scale == 1.0,
        "encoder_unpermuted": child.encoder.colour_permutation_seed is None,
        "dynamics_backend": child.dynamics.backend == "rate",
        "execution_backend": child.dynamics.execution_backend == "scipy-csr-cpu",
        "activation": child.dynamics.activation == "tanh",
        "internal_steps": child.dynamics.internal_steps == 4,
        "leak": child.dynamics.leak == 0.3,
        "recurrent_gain": child.dynamics.recurrent_gain == 2.0,
        "bias": child.dynamics.bias == 0.0,
        "frozen_graph": child.dynamics.frozen_graph is True,
        "initial_state": child.dynamics.initial_state == "zeros",
        "state_dtype": child.dynamics.state_dtype == "float32",
        "coordinate_source": child.decoder.coordinate_source == "retinotopic_surprise",
        "coordinate_convention": (child.decoder.retinotopic_coordinate_convention == "arc_x_hex2"),
        "reclick_memory": child.decoder.reclick_memory == "none",
        "encoder_untrained": not child.encoder.trainable and not child.encoder.per_game_rules,
        "decoder_untrained": not child.decoder.trainable,
        "plasticity_disabled": not child.plasticity.enabled,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    record.update(
        {
            "checks": checks,
            "parsed_leaf_differences": differences,
        }
    )
    if failed:
        raise ContractViolation(
            f"config contract checks failed: {failed}",
            observations={"config_contract": record},
        )
    return child, record


def _asset_hashes(runtime: Path, condition: str) -> dict[str, str]:
    observed: dict[str, str] = {}
    records: dict[str, Any] = {}
    failures: list[str] = []
    for name, expected in EXPECTED_HASHES[condition].items():
        path = runtime / name
        record = _observed_file(path)
        record["expected_sha256"] = expected
        records[name] = record
        if not path.is_file():
            failures.append(f"missing {name}")
            continue
        digest = record.get("sha256")
        if isinstance(digest, str):
            observed[name] = digest
        if digest != expected:
            failures.append(f"{name} hash {digest} != {expected}")
    if failures:
        raise ContractViolation(
            f"{condition} asset contract failed: {failures}",
            observations={f"{condition}_asset_hashes": records},
        )
    return observed


def _matrix_contract(
    real: RuntimeConnectome,
    null: RuntimeConnectome,
) -> dict[str, Any]:
    real_matrix = real.matrix
    null_matrix = null.matrix
    checks: dict[str, bool] = {
        "real_node_count": real.node_count == EXPECTED_NODE_COUNT,
        "null_node_count": null.node_count == EXPECTED_NODE_COUNT,
        "real_edge_count": real.edge_count == EXPECTED_EDGE_COUNT,
        "null_edge_count": null.edge_count == EXPECTED_EDGE_COUNT,
        "identical_node_ids": np.array_equal(real.node_index.body_ids, null.node_index.body_ids),
        # CSR canonical format is SciPy's explicit duplicate-free guarantee.
        "real_zero_duplicate_edges": bool(real_matrix.has_canonical_format),
        "null_zero_duplicate_edges": bool(null_matrix.has_canonical_format),
        "real_no_self_edges": int(np.count_nonzero(real_matrix.diagonal())) == 0,
        "null_no_self_edges": int(np.count_nonzero(null_matrix.diagonal())) == 0,
        "in_degrees_equal": np.array_equal(
            np.diff(real_matrix.indptr), np.diff(null_matrix.indptr)
        ),
        "out_degrees_equal": np.array_equal(
            np.bincount(real_matrix.indices, minlength=EXPECTED_NODE_COUNT),
            np.bincount(null_matrix.indices, minlength=EXPECTED_NODE_COUNT),
        ),
    }

    matrix_stats: dict[str, dict[str, Any]] = {}
    for name, matrix in (("real", real_matrix), ("null", null_matrix)):
        row_l1 = np.asarray(abs(matrix).sum(axis=1)).ravel()
        nonzero = row_l1 > 0.0
        stats = {
            "positive_weights": int(np.count_nonzero(matrix.data > 0.0)),
            "negative_weights": int(np.count_nonzero(matrix.data < 0.0)),
            "zero_incoming_rows": int(np.count_nonzero(~nonzero)),
            "max_nonzero_row_l1_error": float(np.max(np.abs(row_l1[nonzero] - 1.0))),
        }
        matrix_stats[name] = stats
        checks[f"{name}_positive_count"] = stats["positive_weights"] == EXPECTED_POSITIVE
        checks[f"{name}_negative_count"] = stats["negative_weights"] == EXPECTED_NEGATIVE
        checks[f"{name}_zero_incoming"] = stats["zero_incoming_rows"] == EXPECTED_ZERO_INCOMING
        checks[f"{name}_incoming_l1"] = stats["max_nonzero_row_l1_error"] <= MAX_L1_ERROR

    null_record = null.manifest.get("preprocessing", {}).get("null", {})
    null_invariants = null_record.get("invariants", {})
    checks.update(
        {
            "null_manifest_kind": null_record.get("kind") == "degree_preserving",
            "null_manifest_seed": null_record.get("seed") == 20260921,
            "null_manifest_valid": null_invariants.get("valid") is True,
            "null_manifest_reached_target": null_record.get("reached_target") is True,
            "null_manifest_zero_duplicates": null_invariants.get("duplicate_edges") == 0,
            "null_manifest_zero_self_edges": null_invariants.get("self_edges") == 0,
            "null_manifest_source_graph": (
                null_record.get("source_graph_sha256") == EXPECTED_HASHES["real"]["graph.npz"]
            ),
        }
    )
    failed = sorted(name for name, passed in checks.items() if not passed)
    record = {
        "checks": checks,
        "matrix_statistics": matrix_stats,
        "null_manifest": null_record,
    }
    if failed:
        raise ContractViolation(
            f"graph/null contract checks failed: {failed}",
            observations={"graph_contract": record},
        )
    return record


def _features(grid: NDArray[np.int8]) -> ObservationFeatures:
    return ObservationFeatures(
        vector=np.zeros(FEATURE_DIMENSION, dtype=np.float32),
        grid=np.asarray(grid, dtype=np.int8),
        changed_cells=0,
    )


def _grid(
    from_colour: int, center: tuple[int, int] | None = None, to_colour: int | None = None
) -> NDArray[np.int8]:
    grid = np.full((64, 64), from_colour, dtype=np.int8)
    if center is not None:
        x, y = center
        if to_colour is None:
            raise ValueError("changed grid requires to_colour")
        grid[y - 2 : y + 3, x - 2 : x + 3] = np.int8(to_colour)
    return grid


def _predict(
    x_scores: NDArray[np.floating],
    y_scores: NDArray[np.floating],
) -> tuple[int, int]:
    """NumPy argmax implements the frozen lowest-index tie rule."""

    return int(np.argmax(x_scores)), int(np.argmax(y_scores))


def _error(prediction: tuple[int, int], center: tuple[int, int]) -> float:
    return float(np.hypot(prediction[0] - center[0], prediction[1] - center[1]))


def _encoder_column_contract(
    projection: Any,
    columns: Mapping[str, NDArray[Any]],
    *,
    grid_row: int,
    grid_column: int,
    expected_hex1: int,
    expected_hex2: int,
    expected_neurons: int,
) -> dict[str, Any]:
    """Exercise the production encoder's row/column orientation at one cell."""

    background = np.full((64, 64), 1, dtype=np.int8)
    changed = background.copy()
    changed[grid_row, grid_column] = np.int8(7)
    background_histogram = projection.column_histogram(background)
    changed_histogram = projection.column_histogram(changed)
    histogram_delta = changed_histogram - background_histogram
    changed_column_keys = np.flatnonzero(np.any(histogram_delta != 0.0, axis=1)).astype(np.int64)

    hex1 = np.asarray(columns["hex1"], dtype=np.int64)
    hex2 = np.asarray(columns["hex2"], dtype=np.int64)
    indices = np.asarray(columns["node_indices"], dtype=np.int64)
    min_hex1, min_hex2 = int(hex1.min()), int(hex2.min())
    span1 = max(int(hex1.max()) - min_hex1, 1)
    span2 = max(int(hex2.max()) - min_hex2, 1)
    mapped_hex1 = int(np.rint(grid_row / 63 * span1)) + min_hex1
    mapped_hex2 = int(np.rint(grid_column / 63 * span2)) + min_hex2
    expected_column_key = (expected_hex1 - min_hex1) * (span2 + 1) + (expected_hex2 - min_hex2)
    column_mask = (hex1 == expected_hex1) & (hex2 == expected_hex2)
    column_indices = indices[column_mask]
    checks = {
        "grid_row_maps_to_hex1": mapped_hex1 == expected_hex1,
        "grid_column_maps_to_hex2": mapped_hex2 == expected_hex2,
        "exactly_one_histogram_column_changed": changed_column_keys.size == 1,
        "changed_histogram_column_is_expected": (
            changed_column_keys.tolist() == [expected_column_key]
        ),
        "expected_column_is_occupied": column_indices.size > 0,
        "expected_column_neuron_count": column_indices.size == expected_neurons,
    }
    return {
        "grid_row": grid_row,
        "grid_column": grid_column,
        "background_colour": 1,
        "changed_colour": 7,
        "mapped_hex1": mapped_hex1,
        "mapped_hex2": mapped_hex2,
        "expected_hex1": expected_hex1,
        "expected_hex2": expected_hex2,
        "expected_column_key": int(expected_column_key),
        "changed_histogram_column_keys": changed_column_keys.tolist(),
        "column_neurons": int(column_indices.size),
        "column_node_indices_sha256": _sha256_array(column_indices),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _golden_contract(runtime: Path, node_count: int) -> dict[str, Any]:
    projection = build_columnar_colour_projection(
        runtime,
        node_count,
        options=RetinotopicOptions(input_scale=1.0, colour_permutation_seed=None),
    )
    legacy = RetinotopicSaliency(runtime, mode="surprise", coordinate_convention="legacy_hex1_x")
    corrected = RetinotopicSaliency(runtime, mode="surprise", coordinate_convention="arc_x_hex2")
    with np.load(runtime / "retinotopy.npz", allow_pickle=False) as archive:
        columns = {name: np.asarray(archive[name]) for name in archive.files}
    indices = np.asarray(columns["node_indices"], dtype=np.int64)
    hex1 = np.asarray(columns["hex1"], dtype=np.float64)
    hex2 = np.asarray(columns["hex2"], dtype=np.float64)
    encoder_contract = _encoder_column_contract(
        projection,
        columns,
        grid_row=20,
        grid_column=50,
        expected_hex1=12,
        expected_hex2=31,
        expected_neurons=26,
    )
    if not encoder_contract["passed"]:
        raise ContractViolation(
            "production encoder failed the row=20,column=50 mapping contract",
            observations={"coordinate_golden": {"encoder_contract": encoder_contract}},
        )
    row = np.rint((hex1 - hex1.min()) / max(hex1.max() - hex1.min(), 1.0) * 63).astype(np.int64)
    column = np.rint((hex2 - hex2.min()) / max(hex2.max() - hex2.min(), 1.0) * 63).astype(np.int64)
    selected = indices[(row == 20) & (column == 50)]
    if selected.size == 0:
        raise ContractViolation(
            "registered golden row=20,column=50 has no mapped neuron",
            observations={
                "coordinate_golden": {
                    "grid_row": 20,
                    "grid_column": 50,
                    "selected_neurons": 0,
                }
            },
        )
    reference = np.zeros(node_count, dtype=np.float32)
    actual = reference.copy()
    actual[selected] = 1.0
    legacy_axes = legacy.axis_scores(actual, reference)
    corrected_axes = corrected.axis_scores(actual, reference)
    legacy_prediction = _predict(*legacy_axes)
    corrected_prediction = _predict(*corrected_axes)
    selected_sha256 = _sha256_array(selected)
    checks = {
        "production_encoder_round_trip": encoder_contract["passed"],
        "selected_neuron_count": selected.size == 26,
        "encoder_decoder_same_neurons": (
            selected_sha256 == encoder_contract["column_node_indices_sha256"]
        ),
        "legacy_prediction": legacy_prediction == (20, 50),
        "corrected_prediction": corrected_prediction == (50, 20),
        "corrected_x_is_legacy_y": _byte_identical(corrected_axes[0], legacy_axes[1]),
        "corrected_y_is_legacy_x": _byte_identical(corrected_axes[1], legacy_axes[0]),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    record = {
        "grid_row": 20,
        "grid_column": 50,
        "selected_neurons": int(selected.size),
        "selected_node_indices_sha256": selected_sha256,
        "legacy_prediction_xy": list(legacy_prediction),
        "corrected_prediction_xy": list(corrected_prediction),
        "encoder_contract": encoder_contract,
        "checks": checks,
    }
    if failed:
        raise ContractViolation(
            f"coordinate golden failed: {failed}",
            observations={"coordinate_golden": record},
        )
    return record


def _condition_trials(
    *,
    name: str,
    runtime: Path,
    bundle: RuntimeConnectome,
    parameters: RateParameters,
    include_legacy: bool,
    graph_sha256: str,
) -> dict[str, Any]:
    options = RetinotopicOptions(input_scale=1.0, colour_permutation_seed=None)
    projection = build_columnar_colour_projection(runtime, bundle.node_count, options=options)
    corrected = RetinotopicSaliency(runtime, mode="surprise", coordinate_convention="arc_x_hex2")
    legacy = (
        RetinotopicSaliency(runtime, mode="surprise", coordinate_convention="legacy_hex1_x")
        if include_legacy
        else None
    )
    network = ScipyRateNetwork(bundle.matrix, parameters, copy_connectivity=False)
    projection_description = projection.describe()
    colour_map = projection_description["colour_channel_map"]
    network_contract = {
        "copy_connectivity": False,
        "connectivity_object_is_bundle_matrix": network.connectivity is bundle.matrix,
        "connectivity_data_shared": np.shares_memory(network.connectivity.data, bundle.matrix.data),
        "connectivity_object_id": id(bundle.matrix),
        "connectivity_data_object_id": id(bundle.matrix.data),
        "graph_sha256": graph_sha256,
        "spmv": network.spmv.describe(),
        "parameters": asdict(parameters),
        "effective_parameters": _rate_parameter_record(parameters)["effective_float32"],
        "projection_neurons": projection_description["neurons"] == 23_720,
        "projection_occupied_columns": projection_description["occupied_columns"] == 892,
        "projection_channels": projection_description["channels"] == 15,
        "registered_colours_use_distinct_channels": (
            len({colour_map[str(colour)] for colour in (1, 7, 3, 12)}) == 4
        ),
        "effective_spmv_threads_is_six": network.spmv.describe()["threads"] == 6,
    }
    if not all(
        network_contract[key]
        for key in (
            "connectivity_object_is_bundle_matrix",
            "connectivity_data_shared",
            "projection_neurons",
            "projection_occupied_columns",
            "projection_channels",
            "registered_colours_use_distinct_channels",
            "effective_spmv_threads_is_six",
        )
    ):
        network.spmv.close()
        failed = sorted(
            key
            for key, value in network_contract.items()
            if key
            in {
                "connectivity_object_is_bundle_matrix",
                "connectivity_data_shared",
                "projection_neurons",
                "projection_occupied_columns",
                "projection_channels",
                "registered_colours_use_distinct_channels",
                "effective_spmv_threads_is_six",
            }
            and not value
        )
        raise ContractViolation(
            f"{name} network/projection contract failed: {failed}",
            observations={f"{name}_network_contract": network_contract},
        )

    background_drives: dict[int, NDArray[np.float32]] = {}
    h4_by_colour: dict[int, NDArray[np.float32]] = {}
    try:
        for from_colour in sorted({item[0] for item in TRANSITIONS}):
            background = _grid(from_colour)
            drive = projection.drive_features(_features(background))
            background_drives[from_colour] = drive
            state = network.initial_state()
            for _ in range(4):
                state = network.advance(state, drive)
            h4_by_colour[from_colour] = state

        trials: list[dict[str, Any]] = []
        all_forks_identical = True
        all_changed_finite_positive = True
        for center in CENTERS:
            for from_colour, to_colour in TRANSITIONS:
                background_drive = background_drives[from_colour]
                changed_drive = projection.drive_features(
                    _features(_grid(from_colour, center, to_colour))
                )
                expected_start = h4_by_colour[from_colour].copy()
                actual_start = h4_by_colour[from_colour].copy()
                fork_identical = _byte_identical(expected_start, actual_start)
                all_forks_identical &= fork_identical
                expected = network.advance(expected_start, background_drive)
                actual = network.advance(actual_start, changed_drive)
                x_scores, y_scores = corrected.axis_scores(actual, expected)
                axes_finite = bool(np.isfinite(x_scores).all() and np.isfinite(y_scores).all())
                if not axes_finite:
                    raise ContractViolation(
                        f"{name} produced non-finite changed-trial saliency",
                        observations={
                            f"{name}_nonfinite_trial": {
                                "center_xy": list(center),
                                "from_colour": from_colour,
                                "to_colour": to_colour,
                                "x_nonfinite_count": int(np.count_nonzero(~np.isfinite(x_scores))),
                                "y_nonfinite_count": int(np.count_nonzero(~np.isfinite(y_scores))),
                                "raw_scores_stored": False,
                            }
                        },
                    )
                finite_positive = bool(float(x_scores.sum() + y_scores.sum()) > 0.0)
                all_changed_finite_positive &= finite_positive
                prediction = _predict(x_scores, y_scores)
                record: dict[str, Any] = {
                    "condition": name,
                    "center_xy": list(center),
                    "from_colour": from_colour,
                    "to_colour": to_colour,
                    "h4_sha256": _sha256_array(h4_by_colour[from_colour]),
                    "forks_byte_identical": fork_identical,
                    "background_drive_sha256": _sha256_array(background_drive),
                    "changed_drive_sha256": _sha256_array(changed_drive),
                    "expected_state_sha256": _sha256_array(expected),
                    "actual_state_sha256": _sha256_array(actual),
                    "predicted_xy": list(prediction),
                    "error_cells": _error(prediction, center),
                    "x_scores": x_scores.tolist(),
                    "y_scores": y_scores.tolist(),
                    "x_sum": float(x_scores.sum()),
                    "y_sum": float(y_scores.sum()),
                    "finite_positive_saliency": finite_positive,
                }
                if legacy is not None:
                    legacy_x, legacy_y = legacy.axis_scores(actual, expected)
                    legacy_prediction = _predict(legacy_x, legacy_y)
                    record["legacy_redecode"] = {
                        "predicted_xy": list(legacy_prediction),
                        "error_cells": _error(legacy_prediction, center),
                        "x_scores": legacy_x.tolist(),
                        "y_scores": legacy_y.tolist(),
                        "arrays_swap_byte_exact": bool(
                            _byte_identical(x_scores, legacy_y)
                            and _byte_identical(y_scores, legacy_x)
                        ),
                    }
                trials.append(record)

        background_drive = background_drives[1]
        expected_start = h4_by_colour[1].copy()
        actual_start = h4_by_colour[1].copy()
        no_change_fork = _byte_identical(expected_start, actual_start)
        expected = network.advance(expected_start, background_drive)
        actual = network.advance(actual_start, background_drive)
        x_scores, y_scores = corrected.axis_scores(actual, expected)
        if not np.isfinite(x_scores).all() or not np.isfinite(y_scores).all():
            raise ContractViolation(
                f"{name} produced non-finite no-change saliency",
                observations={
                    f"{name}_nonfinite_no_change": {
                        "colour": 1,
                        "x_nonfinite_count": int(np.count_nonzero(~np.isfinite(x_scores))),
                        "y_nonfinite_count": int(np.count_nonzero(~np.isfinite(y_scores))),
                        "raw_scores_stored": False,
                    }
                },
            )
        no_change = {
            "condition": name,
            "colour": 1,
            "h4_sha256": _sha256_array(h4_by_colour[1]),
            "drive_sha256": _sha256_array(background_drive),
            "forks_byte_identical": bool(no_change_fork),
            "states_byte_identical": _byte_identical(expected, actual),
            "expected_state_sha256": _sha256_array(expected),
            "actual_state_sha256": _sha256_array(actual),
            "state_difference_nonzero": int(np.count_nonzero(actual - expected)),
            "max_abs_state_difference": float(np.max(np.abs(actual - expected))),
            "x_scores": x_scores.tolist(),
            "y_scores": y_scores.tolist(),
            "x_sum": float(x_scores.sum()),
            "y_sum": float(y_scores.sum()),
            "axis_sums_exactly_zero": bool(
                float(x_scores.sum()) == 0.0 and float(y_scores.sum()) == 0.0
            ),
        }
    finally:
        network.spmv.close()
        network_contract["spmv_closed"] = True

    return {
        "network_contract": network_contract,
        "projection": projection_description,
        "decoder": corrected.describe(),
        "changed_trials": trials,
        "no_change_trial": no_change,
        "contract_summary": {
            "changed_trial_count": len(trials),
            "legacy_redecode_count": sum("legacy_redecode" in item for item in trials),
            "all_h4_forks_byte_identical": bool(all_forks_identical),
            "all_changed_finite_positive": bool(all_changed_finite_positive),
            "no_change_exact": bool(
                no_change_fork
                and no_change["states_byte_identical"]
                and no_change["state_difference_nonzero"] == 0
                and no_change["max_abs_state_difference"] == 0.0
                and no_change["axis_sums_exactly_zero"]
            ),
        },
    }


def _drive_contract(conditions: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    reference = conditions["corrected_real"]["changed_trials"]
    checks: list[dict[str, Any]] = []
    for index, real_trial in enumerate(reference):
        identity = (
            tuple(real_trial["center_xy"]),
            int(real_trial["from_colour"]),
            int(real_trial["to_colour"]),
        )
        digests = {
            name: (
                condition["changed_trials"][index]["background_drive_sha256"],
                condition["changed_trials"][index]["changed_drive_sha256"],
            )
            for name, condition in conditions.items()
        }
        identities = {
            name: (
                tuple(condition["changed_trials"][index]["center_xy"]),
                int(condition["changed_trials"][index]["from_colour"]),
                int(condition["changed_trials"][index]["to_colour"]),
            )
            for name, condition in conditions.items()
        }
        identical = len(set(digests.values())) == 1 and all(
            candidate == identity for candidate in identities.values()
        )
        checks.append(
            {
                "center_xy": real_trial["center_xy"],
                "from_colour": real_trial["from_colour"],
                "to_colour": real_trial["to_colour"],
                "digests": {name: list(value) for name, value in digests.items()},
                "stimulus_identities": {
                    name: [list(value[0]), value[1], value[2]] for name, value in identities.items()
                },
                "identical": identical,
            }
        )
    no_change_digests = {
        name: condition["no_change_trial"]["drive_sha256"] for name, condition in conditions.items()
    }
    passed = all(item["identical"] for item in checks) and len(set(no_change_digests.values())) == 1
    return {
        "passed": passed,
        "changed_trials": checks,
        "no_change_digests": no_change_digests,
    }


def _condition_center_errors(
    condition: Mapping[str, Any], *, legacy: bool = False
) -> dict[tuple[int, int], float]:
    grouped: dict[tuple[int, int], list[float]] = {center: [] for center in CENTERS}
    for trial in condition["changed_trials"]:
        center = tuple(trial["center_xy"])
        value = trial["legacy_redecode"]["error_cells"] if legacy else trial["error_cells"]
        grouped[center].append(float(value))
    result: dict[tuple[int, int], float] = {}
    for center, values in grouped.items():
        if len(values) != 4:
            raise ContractViolation(f"center {center} has {len(values)} trials, expected four")
        result[center] = float(median(values))
    return result


def _transition_summaries(
    condition: Mapping[str, Any], *, legacy: bool = False
) -> dict[str, dict[str, Any]]:
    grouped: dict[tuple[int, int], list[float]] = {transition: [] for transition in TRANSITIONS}
    for trial in condition["changed_trials"]:
        transition = (int(trial["from_colour"]), int(trial["to_colour"]))
        value = trial["legacy_redecode"]["error_cells"] if legacy else trial["error_cells"]
        grouped[transition].append(float(value))
    summaries: dict[str, dict[str, Any]] = {}
    for transition, values in grouped.items():
        if len(values) != len(CENTERS):
            raise ContractViolation(
                f"transition {transition} has {len(values)} trials, expected {len(CENTERS)}"
            )
        summaries[f"{transition[0]}->{transition[1]}"] = {
            "errors_by_registered_center_order": values,
            "median_error_cells": float(median(values)),
        }
    return summaries


def _scientific_summary(conditions: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    center_errors = {
        "corrected_real": _condition_center_errors(conditions["corrected_real"]),
        "legacy_real": _condition_center_errors(conditions["corrected_real"], legacy=True),
        "corrected_null": _condition_center_errors(conditions["corrected_null"]),
        "corrected_recurrence_off": _condition_center_errors(
            conditions["corrected_recurrence_off"]
        ),
    }
    global_medians = {
        name: float(median(list(errors.values()))) for name, errors in center_errors.items()
    }
    transition_summaries = {
        "corrected_real": _transition_summaries(conditions["corrected_real"]),
        "legacy_real": _transition_summaries(conditions["corrected_real"], legacy=True),
        "corrected_null": _transition_summaries(conditions["corrected_null"]),
        "corrected_recurrence_off": _transition_summaries(conditions["corrected_recurrence_off"]),
    }
    real = center_errors["corrected_real"]
    legacy_wins = sum(real[center] < center_errors["legacy_real"][center] for center in CENTERS)
    null_wins = sum(real[center] < center_errors["corrected_null"][center] for center in CENTERS)
    off_wins = sum(
        real[center] < center_errors["corrected_recurrence_off"][center] for center in CENTERS
    )
    checks = {
        "corrected_real_global_median_le_4": global_medians["corrected_real"] <= 4.0,
        "corrected_real_beats_legacy_all_8": legacy_wins == 8,
        "corrected_real_median_le_80pct_null": (
            global_medians["corrected_real"] <= 0.8 * global_medians["corrected_null"]
        ),
        "corrected_real_beats_null_at_least_7_of_8": null_wins >= 7,
        "corrected_real_median_le_80pct_recurrence_off": (
            global_medians["corrected_real"] <= 0.8 * global_medians["corrected_recurrence_off"]
        ),
        "corrected_real_beats_recurrence_off_at_least_7_of_8": off_wins >= 7,
    }
    coordinate_checks = {
        key: checks[key]
        for key in (
            "corrected_real_global_median_le_4",
            "corrected_real_beats_legacy_all_8",
        )
    }
    dependency_checks = {
        key: value for key, value in checks.items() if key not in coordinate_checks
    }
    return {
        "center_errors": {
            name: {f"{x},{y}": value for (x, y), value in errors.items()}
            for name, errors in center_errors.items()
        },
        "global_medians": global_medians,
        "per_transition_diagnostics": transition_summaries,
        "strict_win_counts": {
            "legacy_real": legacy_wins,
            "corrected_null": null_wins,
            "corrected_recurrence_off": off_wins,
        },
        "checks": checks,
        "coordinate_repair_gate_passed": all(coordinate_checks.values()),
        "single_null_dependency_gate_passed": all(dependency_checks.values()),
        "promotion_passed": all(checks.values()),
    }


def _validate_trial_contracts(conditions: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    real = conditions["corrected_real"]
    expected_panel = [
        (center, from_colour, to_colour)
        for center in CENTERS
        for from_colour, to_colour in TRANSITIONS
    ]

    def panel(condition: Mapping[str, Any]) -> list[tuple[tuple[int, int], int, int]]:
        return [
            (
                tuple(trial["center_xy"]),
                int(trial["from_colour"]),
                int(trial["to_colour"]),
            )
            for trial in condition["changed_trials"]
        ]

    checks = {
        "three_conditions": tuple(conditions) == CONDITIONS,
        "96_changed_condition_trials": (
            sum(len(value["changed_trials"]) for value in conditions.values()) == 96
        ),
        "32_legacy_real_redecodes": (real["contract_summary"]["legacy_redecode_count"] == 32),
        "three_no_change_trials": len(conditions) == 3,
        "exact_registered_panel_in_every_condition": all(
            panel(value) == expected_panel for value in conditions.values()
        ),
        "no_change_colour_is_one": all(
            value["no_change_trial"]["colour"] == 1 for value in conditions.values()
        ),
        "legacy_decode_only_on_real": all(
            "legacy_redecode" not in trial
            for name, value in conditions.items()
            if name != "corrected_real"
            for trial in value["changed_trials"]
        ),
        "every_spmv_plan_closed": all(
            value["network_contract"].get("spmv_closed") is True for value in conditions.values()
        ),
        "all_h4_forks_byte_identical": all(
            value["contract_summary"]["all_h4_forks_byte_identical"]
            for value in conditions.values()
        ),
        "all_changed_finite_positive": all(
            value["contract_summary"]["all_changed_finite_positive"]
            for value in conditions.values()
        ),
        "all_no_change_exact": all(
            value["contract_summary"]["no_change_exact"] for value in conditions.values()
        ),
        "all_legacy_arrays_swap_byte_exact": all(
            trial["legacy_redecode"]["arrays_swap_byte_exact"] for trial in real["changed_trials"]
        ),
    }
    return checks


def _real_off_contract(conditions: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    real = conditions["corrected_real"]["network_contract"]
    off = conditions["corrected_recurrence_off"]["network_contract"]
    declared_differences = _leaf_differences(real["parameters"], off["parameters"])
    effective_differences = _leaf_differences(
        real["effective_parameters"], off["effective_parameters"]
    )
    declared_gain_only = declared_differences == ["recurrent_gain"]
    effective_gain_only = effective_differences == ["recurrent_gain"]
    return {
        "same_registered_real_graph_hash": (
            real["graph_sha256"] == off["graph_sha256"] == EXPECTED_HASHES["real"]["graph.npz"]
        ),
        "same_live_csr_object": real["connectivity_object_id"] == off["connectivity_object_id"],
        "same_live_csr_data_object": (
            real["connectivity_data_object_id"] == off["connectivity_data_object_id"]
        ),
        "both_disable_connectivity_copy": (
            real["copy_connectivity"] is False and off["copy_connectivity"] is False
        ),
        "gain_is_only_declared_parameter_difference": declared_gain_only,
        "gain_is_only_effective_parameter_difference": effective_gain_only,
        "gain_is_only_parameter_difference": declared_gain_only and effective_gain_only,
        "registered_gains": (
            real["parameters"]["recurrent_gain"] == 2.0
            and off["parameters"]["recurrent_gain"] == 0.0
        ),
        "registered_effective_gains": (
            real["effective_parameters"]["recurrent_gain"] == float(np.float32(2.0))
            and off["effective_parameters"]["recurrent_gain"] == float(np.float32(0.0))
        ),
    }


def _execute_probe_inner(
    args: argparse.Namespace,
    observations: dict[str, Any],
) -> dict[str, Any]:
    config_path = args.config.resolve()
    real_runtime = args.real_runtime.resolve()
    null_runtime = args.null_runtime.resolve()
    real_parameters = RateParameters(
        internal_steps=4,
        leak=0.3,
        recurrent_gain=2.0,
        bias=0.0,
    )
    off_parameters = RateParameters(
        internal_steps=4,
        leak=0.3,
        recurrent_gain=0.0,
        bias=0.0,
    )
    observations.update(
        {
            "action_paths_constructed": False,
            "rate_equation": "h <- (1-a)h + a*tanh(g*W*h + u + b); W[post,pre]",
            "real_rate_parameters": _rate_parameter_record(real_parameters),
            "recurrence_off_rate_parameters": _rate_parameter_record(off_parameters),
            "spmv_threads_environment": os.environ.get("FLYGI_SPMV_THREADS"),
        }
    )
    if os.environ.get("FLYGI_SPMV_THREADS") != "6":
        raise ContractViolation(
            "the frozen command requires FLYGI_SPMV_THREADS=6 before any graph load"
        )
    config, config_record = _config_contract(config_path)
    observations["config_contract"] = config_record
    observations["active_decoder_convention"] = config.decoder.retinotopic_coordinate_convention
    observations["inert_action_configuration"] = {
        "controller_enabled": config.controller.enabled,
        "deploy_fly_tiebreak": config.controller.deploy_fly_tiebreak,
        "loop_escape_enabled": config.decoder.loop_escape_enabled,
        "loop_escape_exploration_bonus": config.decoder.loop_escape_exploration_bonus,
        "loop_escape_unchanged_failure_penalty": (
            config.decoder.loop_escape_unchanged_failure_penalty
        ),
        "coordinate_fallback": config.decoder.coordinate_fallback,
        "unchanged_click_exploration": config.decoder.unchanged_click_exploration,
    }
    asset_hashes: dict[str, dict[str, str]] = {}
    asset_failures: list[str] = []
    for name, runtime in (("real", real_runtime), ("null", null_runtime)):
        try:
            asset_hashes[name] = _asset_hashes(runtime, name)
        except ContractViolation as exc:
            observations.update(exc.observations)
            asset_failures.append(str(exc))
    observations["asset_hashes"] = asset_hashes
    if asset_failures:
        raise ContractViolation(
            f"asset preflight failed: {asset_failures}", observations=observations
        )
    real = load_runtime_connectome(real_runtime, required_groups=())
    null = load_runtime_connectome(null_runtime, required_groups=())
    graph_contract = _matrix_contract(real, null)
    observations["graph_contract"] = graph_contract
    golden = _golden_contract(real_runtime, real.node_count)
    observations["coordinate_golden"] = golden

    parameter_differences = _leaf_differences(asdict(real_parameters), asdict(off_parameters))
    observations["real_off_parameter_differences"] = parameter_differences
    if parameter_differences != ["recurrent_gain"]:
        raise ContractViolation(
            f"real/off parameter differences are {parameter_differences}, expected recurrent_gain"
        )

    # Networks are intentionally constructed and closed one at a time.  The
    # gain-zero arm reuses the exact real CSR object with copy_connectivity=False.
    conditions: dict[str, Any] = {}
    conditions["corrected_real"] = _condition_trials(
        name="corrected_real",
        runtime=real_runtime,
        bundle=real,
        parameters=real_parameters,
        include_legacy=True,
        graph_sha256=asset_hashes["real"]["graph.npz"],
    )
    observations["completed_conditions"] = conditions
    conditions["corrected_null"] = _condition_trials(
        name="corrected_null",
        runtime=null_runtime,
        bundle=null,
        parameters=real_parameters,
        include_legacy=False,
        graph_sha256=asset_hashes["null"]["graph.npz"],
    )
    observations["completed_conditions"] = conditions
    conditions["corrected_recurrence_off"] = _condition_trials(
        name="corrected_recurrence_off",
        runtime=real_runtime,
        bundle=real,
        parameters=off_parameters,
        include_legacy=False,
        graph_sha256=asset_hashes["real"]["graph.npz"],
    )
    observations["completed_conditions"] = conditions

    trial_checks = _validate_trial_contracts(conditions)
    real_off_contract = _real_off_contract(conditions)
    drive_contract = _drive_contract(conditions)
    science = _scientific_summary(conditions)
    contract_failures = sorted(name for name, passed in trial_checks.items() if not passed)
    contract_failures.extend(
        f"real_off:{name}" for name, passed in real_off_contract.items() if not passed
    )
    if not drive_contract["passed"]:
        contract_failures.append("identical_drives_across_conditions")
    contract_valid = not contract_failures
    result = {
        "status": "complete" if contract_valid else "invalid",
        "scientific_verdict": (
            ("pass" if science["promotion_passed"] else "fail") if contract_valid else None
        ),
        "contract_valid": contract_valid,
        "contract_failures": contract_failures,
        "hypothesis": HYPOTHESIS,
        "claim_boundary": (
            "Fixed-panel, single-null test of whether recurrence sharpens an engineered "
            "retinotopic code in this MaleCNS-derived rate model; not living-fly vision."
        ),
        "action_paths_constructed": False,
        "inert_action_fields_changed": False,
        "inert_action_configuration": {
            "controller_enabled": config.controller.enabled,
            "deploy_fly_tiebreak": config.controller.deploy_fly_tiebreak,
            "loop_escape_enabled": config.decoder.loop_escape_enabled,
            "loop_escape_exploration_bonus": config.decoder.loop_escape_exploration_bonus,
            "loop_escape_unchanged_failure_penalty": (
                config.decoder.loop_escape_unchanged_failure_penalty
            ),
            "coordinate_fallback": config.decoder.coordinate_fallback,
            "unchanged_click_exploration": config.decoder.unchanged_click_exploration,
            "why_inert": (
                "standalone probe constructs no policy, controller, FlyTiebreaker, "
                "click head, action selection, or reclick-memory path"
            ),
        },
        "config_contract": config_record,
        "asset_hashes": asset_hashes,
        "graph_contract": graph_contract,
        "coordinate_golden": golden,
        "rate_equation": "h <- (1-a)h + a*tanh(g*W*h + u + b); W[post,pre]",
        "real_rate_parameters": _rate_parameter_record(real_parameters),
        "recurrence_off_rate_parameters": _rate_parameter_record(off_parameters),
        "real_off_parameter_differences": parameter_differences,
        "trial_contract_checks": trial_checks,
        "real_off_contract": real_off_contract,
        "drive_contract": drive_contract,
        "conditions": conditions,
        "scientific_summary": science,
        "active_decoder_convention": config.decoder.retinotopic_coordinate_convention,
    }
    if not contract_valid:
        result["scientific_summary_interpretation"] = (
            "diagnostic reductions only; the failed contract forbids a scientific verdict"
        )
    return result


def _execute_probe(args: argparse.Namespace) -> dict[str, Any]:
    observations: dict[str, Any] = {}
    try:
        return _execute_probe_inner(args, observations)
    except ContractViolation as exc:
        observations.update(exc.observations)
        raise ContractViolation(str(exc), observations=observations) from exc
    except Exception as exc:
        observations["unexpected_runtime_error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
        raise ContractViolation(
            f"unexpected runtime failure: {type(exc).__name__}: {exc}",
            observations=observations,
        ) from exc


def _base_envelope(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "kind": "retino-surprise-recurrence-premise-killer",
        "hypothesis": HYPOTHESIS,
        "started_utc": _utc_now(),
        "status": "reserved",
        "contract_valid": False,
        "scientific_verdict": None,
        "arguments": {
            key: _relative(value) if isinstance(value, Path) else value
            for key, value in sorted(vars(args).items())
        },
        "provenance": {
            "probe_path": _relative(Path(__file__)),
            "probe_sha256": sha256_file(Path(__file__)),
            "experiments_path": _relative(EXPERIMENTS),
            "experiments_sha256": sha256_file(EXPERIMENTS),
            "git": _git_state(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "spmv_threads_environment": os.environ.get("FLYGI_SPMV_THREADS"),
        },
    }


def _json_safe(value: Any) -> Any:
    """Return a JSON-native tree, preserving non-finite diagnostics as labels."""

    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            return "nonfinite:nan"
        return "nonfinite:+inf" if value > 0.0 else "nonfinite:-inf"
    return value


def _write_reserved(stream: Any, envelope: Mapping[str, Any]) -> None:
    json.dump(_json_safe(envelope), stream, indent=2, sort_keys=True, allow_nan=False)
    stream.write("\n")
    stream.flush()
    os.fsync(stream.fileno())


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--real-runtime", type=Path, required=True)
    parser.add_argument("--null-runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-promotion", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        stream = output.open("x", encoding="utf-8")
    except FileExistsError:
        print(f"refusing to overwrite existing output: {output}", file=sys.stderr)
        return 1

    envelope: dict[str, Any] = {
        "schema": SCHEMA,
        "schema_version": 1,
        "kind": "retino-surprise-recurrence-premise-killer",
        "hypothesis": HYPOTHESIS,
        "started_utc": _utc_now(),
        "status": "reserved",
        "contract_valid": False,
        "scientific_verdict": None,
    }
    exit_status = 1
    try:
        envelope.update(_base_envelope(args))
        result = _execute_probe(args)
        envelope.update(result)
        envelope["finished_utc"] = _utc_now()
        if not result["contract_valid"]:
            exit_status = 1
        elif result["scientific_verdict"] == "pass":
            exit_status = 0
        else:
            exit_status = 2 if args.require_promotion else 0
    except Exception as exc:  # Invalid outcomes must still leave a durable envelope.
        invalid_observations = exc.observations if isinstance(exc, ContractViolation) else {}
        envelope.update(
            {
                "status": "invalid",
                "contract_valid": False,
                "scientific_verdict": None,
                "finished_utc": _utc_now(),
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                },
                "invalid_contract_observations": invalid_observations,
            }
        )
        exit_status = 1
    finally:
        try:
            _write_reserved(stream, envelope)
        finally:
            stream.close()

    print(
        f"{HYPOTHESIS}: status={envelope['status']} "
        f"verdict={envelope['scientific_verdict']} output={output}"
    )
    return exit_status


if __name__ == "__main__":
    raise SystemExit(main())
