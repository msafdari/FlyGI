#!/usr/bin/env python3
"""Run the manual Milestone 2 full-connectome dynamics acceptance gate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

from flygi.config import FlyGIConfig, load_config
from flygi.connectome.manifest import sha256_file
from flygi.dynamics import (
    RateParameters,
    RuntimeConnectome,
    ScipyRateNetwork,
    load_runtime_connectome,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/literal_rate.yaml"
DEFAULT_RESULTS_DIR = ROOT / "results/dynamics"
REQUIRED_INTERNAL_STEPS = (1, 2, 4, 8)
MINIMUM_WARMUP_ACTIONS = 3
MINIMUM_MEASURED_ACTIONS = 25
MINIMUM_STABILITY_STEPS = 10_000
PROBE_AMPLITUDE = np.float32(0.25)
INITIAL_DIAGNOSTIC_SCALE = 0.01
EXPECTED_RELEASE = "male-cns:v1.0"
EXPECTED_LITERAL_NODES = 166_700
EXPECTED_LITERAL_EDGES = 25_582_837
EXPECTED_LITERAL_OUTPUT_HASHES = {
    "graph.npz": "99c9441be6e6ac89eb20c3c17162308240f2e4326003d97a4e5034e998be8acc",
    "node_metadata.npz": "2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c",
    "groups.npz": "09736379ce989268080f57b64f357e800cf446972007c1af2287a86b9985a89d",
}


def _peak_rss_bytes() -> int:
    """Return process peak RSS in bytes on macOS and Linux."""

    raw = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return raw if sys.platform == "darwin" else raw * 1024


def _array_sha256(array: NDArray[np.generic]) -> str:
    """Hash an array together with its shape and dtype contract."""

    contiguous = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(str(contiguous.dtype).encode("ascii"))
    digest.update(json.dumps(list(contiguous.shape), separators=(",", ":")).encode("ascii"))
    digest.update(memoryview(contiguous).cast("B"))
    return digest.hexdigest()


def _timing_summary(samples_ns: Sequence[int]) -> dict[str, float | int | None]:
    """Summarize measured action times without imposing a machine threshold."""

    if not samples_ns:
        return {
            "count": 0,
            "total_ns": 0,
            "mean_ns": None,
            "median_ns": None,
            "p95_ns": None,
            "min_ns": None,
            "max_ns": None,
        }
    values = np.asarray(samples_ns, dtype=np.int64)
    return {
        "count": len(values),
        "total_ns": int(values.sum(dtype=np.int64)),
        "mean_ns": float(np.mean(values)),
        "median_ns": float(np.median(values)),
        "p95_ns": float(np.percentile(values, 95)),
        "min_ns": int(np.min(values)),
        "max_ns": int(np.max(values)),
    }


def _state_diagnostics(state: NDArray[np.float32]) -> dict[str, float | int | str]:
    absolute = np.abs(state)
    return {
        "sha256": _array_sha256(state),
        "minimum": float(np.min(state)),
        "maximum": float(np.max(state)),
        "maximum_absolute": float(np.max(absolute)),
        "mean": float(np.mean(state, dtype=np.float64)),
        "l2_norm": float(np.linalg.norm(state)),
        "nonzero": int(np.count_nonzero(state)),
        "saturation_fraction_abs_ge_0_99": float(np.mean(absolute >= 0.99)),
    }


def _select_pre_dn_probe(
    matrix: sparse.csr_matrix,
    descending_indices: NDArray[np.int32],
) -> dict[str, int | float]:
    """Choose the strongest deterministic non-DN input edge to a DN row."""

    best: tuple[float, int, int, float] | None = None
    descending_set = {int(index) for index in descending_indices}
    for post_raw in descending_indices:
        post = int(post_raw)
        start = int(matrix.indptr[post])
        stop = int(matrix.indptr[post + 1])
        if start == stop:
            continue
        for offset in range(start, stop):
            pre = int(matrix.indices[offset])
            if pre in descending_set:
                continue
            weight = float(matrix.data[offset])
            candidate = (-abs(weight), post, pre, weight)
            if best is None or candidate < best:
                best = candidate
    if best is None:
        raise ValueError("descending-neuron group has no incoming non-DN graph edge")
    _, post, pre, weight = best
    return {
        "presynaptic_index": pre,
        "descending_index": post,
        "weight": weight,
    }


def _git_provenance() -> dict[str, Any]:
    def run(*arguments: str) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    try:
        commit = run("rev-parse", "HEAD")
        status = run("status", "--porcelain=v1", "--untracked-files=all").splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        return {"commit": None, "dirty": None, "status": [], "error": str(exc)}
    return {"commit": commit, "dirty": bool(status), "status": status}


def _dependency_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for distribution in ("flygi", "numpy", "scipy", "PyYAML"):
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            versions[distribution] = None
    return versions


def _cpu_identity() -> dict[str, str | None]:
    brand: str | None = None
    model: str | None = None
    cores: str | None = None
    memory: str | None = None
    if sys.platform == "darwin":
        try:
            completed = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                check=True,
                capture_output=True,
                text=True,
            )
            brand = completed.stdout.strip() or None
        except (OSError, subprocess.CalledProcessError):
            pass
        if brand is None:
            try:
                completed = subprocess.run(
                    ["system_profiler", "SPHardwareDataType"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                whitelisted: dict[str, str] = {}
                for line in completed.stdout.splitlines():
                    key, separator, value = line.strip().partition(":")
                    if separator and key in {
                        "Model Name",
                        "Chip",
                        "Total Number of Cores",
                        "Memory",
                    }:
                        whitelisted[key] = value.strip()
                brand = whitelisted.get("Chip")
                model = whitelisted.get("Model Name")
                cores = whitelisted.get("Total Number of Cores")
                memory = whitelisted.get("Memory")
            except (OSError, subprocess.CalledProcessError):
                pass
    elif sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
                if line.lower().startswith("model name"):
                    brand = line.partition(":")[2].strip() or None
                    break
        except OSError:
            pass
    return {
        "brand": brand,
        "model": model,
        "cores": cores,
        "memory": memory,
        "machine": platform.machine() or None,
        "processor": platform.processor() or None,
    }


def _manifest_output_hashes(manifest: Mapping[str, Any]) -> dict[str, str]:
    records = manifest.get("outputs")
    if not isinstance(records, list):
        return {}
    return {
        str(record["path"]): str(record["sha256"]).lower()
        for record in records
        if isinstance(record, Mapping) and "path" in record and "sha256" in record
    }


def _runtime_identity_issues(
    config: FlyGIConfig,
    bundle: RuntimeConnectome,
) -> list[str]:
    """Pin Gate 1 to the declared full literal MaleCNS runtime."""

    issues: list[str] = []
    manifest = bundle.manifest
    if config.data.release != EXPECTED_RELEASE or manifest.get("release") != EXPECTED_RELEASE:
        issues.append(f"runtime release must be exactly {EXPECTED_RELEASE}")
    if config.data.output_dir != config.graph.output_dir:
        issues.append("data.output_dir and graph.output_dir must identify the same runtime")
    if bundle.node_count != EXPECTED_LITERAL_NODES:
        issues.append(
            f"literal runtime must have {EXPECTED_LITERAL_NODES} nodes, observed {bundle.node_count}"
        )
    if bundle.edge_count != EXPECTED_LITERAL_EDGES:
        issues.append(
            f"literal runtime must have {EXPECTED_LITERAL_EDGES} edges, observed {bundle.edge_count}"
        )

    observed_hashes = _manifest_output_hashes(manifest)
    for name, expected in EXPECTED_LITERAL_OUTPUT_HASHES.items():
        if observed_hashes.get(name) != expected:
            issues.append(f"literal runtime {name} SHA-256 does not match the pinned identity")

    preprocessing = manifest.get("preprocessing")
    if not isinstance(preprocessing, Mapping):
        issues.append("runtime manifest preprocessing must be a mapping")
        return issues
    expected_preprocessing = {
        "matrix_convention": config.graph.matrix_convention,
        "weight_transform": config.graph.weight_transform,
        "sign_mode": config.graph.sign_mode,
        "modulator_treatment": config.graph.modulator_treatment,
        "normalization": config.graph.normalization,
        "epsilon": config.graph.epsilon,
        "allow_self_edges": config.graph.allow_self_edges,
        "node_filter_column": config.graph.node_filter_column,
        "node_filter_values": config.graph.node_filter_values,
    }
    for key, expected in expected_preprocessing.items():
        observed = preprocessing.get(key)
        if isinstance(expected, tuple):
            observed = tuple(observed) if isinstance(observed, list) else observed
        if observed != expected:
            issues.append(
                f"manifest preprocessing {key} disagrees with config: "
                f"expected {expected!r}, observed {observed!r}"
            )
    if config.graph.normalization == "spectral_radius" and (
        preprocessing.get("spectral_radius") != config.graph.spectral_radius
    ):
        issues.append("manifest spectral_radius disagrees with config")
    if config.groups.get("descending_neurons") != {"superclass": "descending_neuron"}:
        issues.append("literal config must declare the exact descending-neuron group filter")
    if len(bundle.groups["descending_neurons"]) != 1_314:
        issues.append("literal runtime must contain exactly 1,314 descending neurons")
    return issues


def _write_json_exclusive(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(payload)


def _default_output() -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    return DEFAULT_RESULTS_DIR / f"{timestamp}-gate1.json"


def _network(config: FlyGIConfig, matrix: sparse.csr_matrix) -> ScipyRateNetwork:
    parameters = RateParameters(
        internal_steps=config.dynamics.internal_steps,
        leak=config.dynamics.leak,
        recurrent_gain=config.dynamics.recurrent_gain,
        bias=config.dynamics.bias,
    )
    return ScipyRateNetwork(matrix, parameters, copy_connectivity=False)


def _stability_check(
    network: ScipyRateNetwork,
    initial: NDArray[np.float32],
    drive: NDArray[np.float32],
    *,
    steps: int,
    chunk: int,
) -> dict[str, Any]:
    state = initial.copy()
    completed = 0
    maximum_absolute_observed = float(np.max(np.abs(state)))
    report_every = max(chunk, steps // 10)
    next_report = min(steps, report_every)
    started = time.perf_counter_ns()
    while completed < steps:
        count = min(chunk, steps - completed)
        state = network.advance(state, drive, internal_steps=count)
        completed += count
        maximum_absolute_observed = max(
            maximum_absolute_observed,
            float(np.max(np.abs(state))),
        )
        if completed >= next_report or completed == steps:
            print(
                f"[stability] {completed}/{steps} internal steps; "
                f"max_abs={maximum_absolute_observed:.7f}",
                flush=True,
            )
            next_report = min(steps, next_report + report_every)
    elapsed = time.perf_counter_ns() - started
    finite = bool(np.isfinite(state).all())
    bound = float(1.0 + 8 * np.finfo(np.float32).eps)
    return {
        "steps_requested": steps,
        "steps_completed": completed,
        "chunk_size": chunk,
        "wall_ns": elapsed,
        "finite": finite,
        "declared_bound": bound,
        "maximum_absolute_observed": maximum_absolute_observed,
        "within_declared_bound": finite and maximum_absolute_observed <= bound,
        "final_state": _state_diagnostics(state),
    }


def _benchmark_internal_steps(
    network: ScipyRateNetwork,
    initial: NDArray[np.float32],
    drive: NDArray[np.float32],
    *,
    internal_steps: Sequence[int],
    warmup_actions: int,
    measured_actions: int,
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for steps in internal_steps:
        print(
            f"[timing] K={steps}: {warmup_actions} warmup + {measured_actions} measured actions",
            flush=True,
        )
        state = initial.copy()
        for _ in range(warmup_actions):
            state = network.advance(state, drive, internal_steps=steps)

        samples: list[int] = []
        for _ in range(measured_actions):
            started = time.perf_counter_ns()
            state = network.advance(state, drive, internal_steps=steps)
            samples.append(time.perf_counter_ns() - started)
        summary = _timing_summary(samples)
        median_ns = float(summary["median_ns"])
        p95_ns = float(summary["p95_ns"])
        results[str(steps)] = {
            "internal_steps": steps,
            "warmup_actions": warmup_actions,
            "measured_actions": measured_actions,
            "samples_ns": samples,
            "summary": summary,
            "derived": {
                "actions_per_second_from_median": 1e9 / median_ns,
                "seconds_per_80_action_game_from_median": median_ns * 80 / 1e9,
                "seconds_per_25_game_seed_from_median": median_ns * 25 * 80 / 1e9,
                "seconds_per_125_row_gate_from_median": median_ns * 125 * 80 / 1e9,
                "seconds_per_125_row_gate_from_p95": p95_ns * 125 * 80 / 1e9,
            },
            "final_state_sha256": _array_sha256(state),
            "peak_rss_bytes_after": _peak_rss_bytes(),
        }
    return results


def _protocol_issues(
    args: argparse.Namespace,
    *,
    configured_internal_steps: int,
) -> list[str]:
    issues: list[str] = []
    if tuple(args.internal_steps) != REQUIRED_INTERNAL_STEPS:
        issues.append(f"timing sweep must be exactly {list(REQUIRED_INTERNAL_STEPS)}")
    if configured_internal_steps not in args.internal_steps:
        issues.append("configured internal_steps must be included in the timing sweep")
    if configured_internal_steps not in REQUIRED_INTERNAL_STEPS:
        issues.append(f"configured internal_steps must be one of {list(REQUIRED_INTERNAL_STEPS)}")
    if args.warmup_actions < MINIMUM_WARMUP_ACTIONS:
        issues.append(
            f"timing gate requires at least {MINIMUM_WARMUP_ACTIONS} warmup actions per K"
        )
    if args.measured_actions < MINIMUM_MEASURED_ACTIONS:
        issues.append(
            f"timing gate requires at least {MINIMUM_MEASURED_ACTIONS} measured actions per K"
        )
    if args.stability_steps < MINIMUM_STABILITY_STEPS:
        issues.append(
            f"stability gate requires at least {MINIMUM_STABILITY_STEPS:,} "
            "full-graph internal steps"
        )
    return issues


def run_gate(args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    output = args.output.resolve() if args.output is not None else _default_output()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing result: {output}")

    config_path = args.config.resolve()
    config = load_config(config_path)
    git = _git_provenance()

    print(f"[load] verifying and loading {config.graph.output_dir}", flush=True)
    load_started = time.perf_counter_ns()
    bundle = load_runtime_connectome(config.graph.output_dir)
    load_wall_ns = time.perf_counter_ns() - load_started
    rss_after_load = _peak_rss_bytes()
    print(
        f"[load] N={bundle.node_count:,} E={bundle.edge_count:,} "
        f"wall={load_wall_ns / 1e9:.3f}s RSS={rss_after_load / (1024**2):.1f} MiB",
        flush=True,
    )

    network = _network(config, bundle.matrix)
    descending = bundle.groups["descending_neurons"]
    descending_set = {int(index) for index in descending}
    identity_issues = _runtime_identity_issues(config, bundle)
    probe = _select_pre_dn_probe(bundle.matrix, descending)
    positive_drive = np.zeros(bundle.node_count, dtype=np.float32)
    positive_drive[int(probe["presynaptic_index"])] = PROBE_AMPLITUDE
    negative_drive = -positive_drive
    zero_state = network.initial_state()
    seeded_state = network.initial_state(seed=config.seed, scale=INITIAL_DIAGNOSTIC_SCALE)

    print("[correctness] one full update and exact-repeat check", flush=True)
    one_step = network.step(seeded_state, positive_drive)
    deterministic_first = network.advance(seeded_state, positive_drive)
    deterministic_second = network.advance(seeded_state, positive_drive)
    exact_repeat = bool(np.array_equal(deterministic_first, deterministic_second))

    sensitivity_steps = max(2, config.dynamics.internal_steps)
    positive_state = network.advance(
        zero_state,
        positive_drive,
        internal_steps=sensitivity_steps,
    )
    negative_state = network.advance(
        zero_state,
        negative_drive,
        internal_steps=sensitivity_steps,
    )
    positive_dn = network.readout(positive_state, descending)
    negative_dn = network.readout(negative_state, descending)
    target = int(probe["descending_index"])
    presynaptic = int(probe["presynaptic_index"])
    target_positive_activity = float(positive_state[target])
    target_negative_activity = float(negative_state[target])
    sensitivity = {
        "internal_steps": sensitivity_steps,
        "probe": {
            **probe,
            "amplitude": float(PROBE_AMPLITUDE),
            "presynaptic_body_id": int(bundle.node_index.body_ids[presynaptic]),
            "descending_body_id": int(bundle.node_index.body_ids[target]),
            "presynaptic_is_descending": presynaptic in descending_set,
        },
        "full_states_differ": not np.array_equal(positive_state, negative_state),
        "descending_traces_differ": not np.array_equal(positive_dn, negative_dn),
        "descending_nonzero": bool(np.any(positive_dn != 0.0)),
        "target_positive_activity": target_positive_activity,
        "target_negative_activity": target_negative_activity,
        "target_response_nonzero": (
            target_positive_activity != 0.0 or target_negative_activity != 0.0
        ),
        "target_responses_differ": target_positive_activity != target_negative_activity,
        "positive_state_sha256": _array_sha256(positive_state),
        "negative_state_sha256": _array_sha256(negative_state),
        "positive_dn_sha256": _array_sha256(positive_dn),
        "negative_dn_sha256": _array_sha256(negative_dn),
        "maximum_absolute_dn_difference": float(np.max(np.abs(positive_dn - negative_dn))),
    }

    print(
        f"[stability] running {args.stability_steps:,} full-graph internal steps",
        flush=True,
    )
    stability = _stability_check(
        network,
        seeded_state,
        positive_drive,
        steps=args.stability_steps,
        chunk=args.stability_chunk,
    )
    timing = _benchmark_internal_steps(
        network,
        seeded_state,
        positive_drive,
        internal_steps=args.internal_steps,
        warmup_actions=args.warmup_actions,
        measured_actions=args.measured_actions,
    )

    issues: list[str] = list(identity_issues)
    if git.get("dirty") is not False:
        issues.append("Git worktree was not clean at benchmark start")
    issues.extend(
        _protocol_issues(
            args,
            configured_internal_steps=config.dynamics.internal_steps,
        )
    )
    if one_step.shape != (bundle.node_count,) or one_step.dtype != np.float32:
        issues.append("one full rate step returned the wrong shape or dtype")
    if not np.isfinite(one_step).all():
        issues.append("one full rate step produced non-finite activity")
    if not exact_repeat:
        issues.append("same-backend repeated dynamics were not bitwise identical")
    if not sensitivity["full_states_differ"]:
        issues.append("opposite nonzero inputs produced identical full states")
    if not sensitivity["descending_traces_differ"] or not sensitivity["descending_nonzero"]:
        issues.append("graph-mediated probe did not change descending-neuron activity")
    if sensitivity["probe"]["presynaptic_is_descending"]:
        issues.append("graph-mediated probe input node must not be a descending neuron")
    if not sensitivity["target_response_nonzero"] or not sensitivity["target_responses_differ"]:
        issues.append("selected descending target did not respond differently through its edge")
    if not stability["finite"] or not stability["within_declared_bound"]:
        issues.append("full-graph stability contract failed")

    manifest_path = config.graph.output_dir / "manifest.json"
    result = {
        "schema": "flygi.dynamics-gate",
        "schema_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "status": "passed" if not issues else "failed",
        "parameters": {
            "config": str(config_path),
            "seed": config.seed,
            "model": config.dynamics.backend,
            "execution_backend": network.backend_name,
            "activation": config.dynamics.activation,
            "configured_internal_steps": config.dynamics.internal_steps,
            "leak": config.dynamics.leak,
            "recurrent_gain": config.dynamics.recurrent_gain,
            "bias": config.dynamics.bias,
            "initial_state": config.dynamics.initial_state,
            "state_dtype": config.dynamics.state_dtype,
            "graph_frozen": config.dynamics.frozen_graph,
            "diagnostic_initial_state": {
                "kind": "seeded_uniform",
                "scale": INITIAL_DIAGNOSTIC_SCALE,
                "sha256": _array_sha256(seeded_state),
            },
            "timing_internal_steps": list(args.internal_steps),
            "warmup_actions": args.warmup_actions,
            "measured_actions": args.measured_actions,
            "stability_steps": args.stability_steps,
            "stability_chunk": args.stability_chunk,
        },
        "provenance": {
            "git": git,
            "python": sys.version,
            "platform": platform.platform(),
            "cpu": _cpu_identity(),
            "dependencies": _dependency_versions(),
            "thread_environment": {
                name: os.environ.get(name)
                for name in (
                    "OMP_NUM_THREADS",
                    "OPENBLAS_NUM_THREADS",
                    "MKL_NUM_THREADS",
                    "VECLIB_MAXIMUM_THREADS",
                )
            },
            "config_sha256": sha256_file(config_path),
            "uv_lock_sha256": sha256_file(ROOT / "uv.lock"),
            "benchmark_script_sha256": sha256_file(Path(__file__).resolve()),
            "connectome_manifest_sha256": sha256_file(manifest_path),
            "verified_output_hashes": dict(bundle.verified_hashes),
        },
        "graph": {
            "directory": str(config.graph.output_dir),
            "matrix_convention": bundle.manifest["matrix_convention"],
            "propagation": bundle.manifest["propagation"],
            "nodes": bundle.node_count,
            "edges": bundle.edge_count,
            "matrix_dtype": str(bundle.matrix.dtype),
            "indptr_dtype": str(bundle.matrix.indptr.dtype),
            "indices_dtype": str(bundle.matrix.indices.dtype),
            "csr_bytes": int(
                bundle.matrix.data.nbytes
                + bundle.matrix.indices.nbytes
                + bundle.matrix.indptr.nbytes
            ),
            "descending_neurons": len(descending),
            "expected_identity": {
                "release": EXPECTED_RELEASE,
                "nodes": EXPECTED_LITERAL_NODES,
                "edges": EXPECTED_LITERAL_EDGES,
                "output_sha256": EXPECTED_LITERAL_OUTPUT_HASHES,
            },
        },
        "load": {
            "scope": "process-cold verified asset load; OS disk cache state uncontrolled",
            "wall_ns": load_wall_ns,
            "peak_rss_bytes_after_load": rss_after_load,
        },
        "checks": {
            "one_full_step": {
                "shape": list(one_step.shape),
                "dtype": str(one_step.dtype),
                "finite": bool(np.isfinite(one_step).all()),
                "state": _state_diagnostics(one_step),
            },
            "same_backend_determinism": {
                "exact_match": exact_repeat,
                "first_sha256": _array_sha256(deterministic_first),
                "second_sha256": _array_sha256(deterministic_second),
            },
            "input_and_descending_sensitivity": sensitivity,
            "runtime_identity": {
                "issues": identity_issues,
                "passed": not identity_issues,
            },
            "stability": stability,
        },
        "timing": timing,
        "resources": {
            "peak_rss_bytes": _peak_rss_bytes(),
        },
        "gate": {
            "required_internal_steps": list(REQUIRED_INTERNAL_STEPS),
            "minimum_warmup_actions": MINIMUM_WARMUP_ACTIONS,
            "minimum_measured_actions": MINIMUM_MEASURED_ACTIONS,
            "minimum_stability_steps": MINIMUM_STABILITY_STEPS,
            "issues": issues,
            "passed": not issues,
        },
    }
    _write_json_exclusive(output, result)
    return result, output


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--internal-steps",
        type=int,
        nargs="+",
        default=list(REQUIRED_INTERNAL_STEPS),
    )
    parser.add_argument("--warmup-actions", type=int, default=MINIMUM_WARMUP_ACTIONS)
    parser.add_argument("--measured-actions", type=int, default=MINIMUM_MEASURED_ACTIONS)
    parser.add_argument("--stability-steps", type=int, default=MINIMUM_STABILITY_STEPS)
    parser.add_argument("--stability-chunk", type=int, default=100)
    parser.add_argument("--output", type=Path, default=None)
    return parser


def _validate_args(args: argparse.Namespace) -> None:
    if not args.internal_steps or any(value <= 0 for value in args.internal_steps):
        raise ValueError("--internal-steps values must be positive")
    if len(set(args.internal_steps)) != len(args.internal_steps):
        raise ValueError("--internal-steps values must be unique")
    if args.internal_steps != sorted(args.internal_steps):
        raise ValueError("--internal-steps values must be ascending")
    if args.warmup_actions < 0:
        raise ValueError("--warmup-actions must be non-negative")
    if args.measured_actions <= 0:
        raise ValueError("--measured-actions must be positive")
    if args.stability_steps <= 0:
        raise ValueError("--stability-steps must be positive")
    if args.stability_chunk <= 0:
        raise ValueError("--stability-chunk must be positive")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        _validate_args(args)
        result, output = run_gate(args)
    except (FileNotFoundError, FileExistsError, TypeError, ValueError) as exc:
        raise SystemExit(f"dynamics gate: {exc}") from exc
    print(
        f"Wrote {output} (gate={result['status']}, "
        f"peak_RSS={result['resources']['peak_rss_bytes'] / (1024**2):.1f} MiB)",
        flush=True,
    )
    return 0 if result["gate"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
