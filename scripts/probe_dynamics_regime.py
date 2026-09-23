#!/usr/bin/env python3
"""Measure the dynamical regime of a compiled FlyGI runtime.

This is a diagnostic probe, not an acceptance gate. It answers four questions
that determine whether a closed-loop agent built on a given runtime and
operating point can carry frame information to its readout at all:

1. What is the spectral radius of the normalized matrix, and the leading
   eigenvalue of the update linearized about ``h = 0``?
2. How many directed hops separate the declared sensory population from the
   declared readout population, and how many internal steps does injected drive
   actually need before readout activity becomes nonzero?
3. How fast do two distinct drive histories converge once drive is removed,
   measured in external actions rather than internal steps?
4. How separable and how high-dimensional is the readout code across distinct
   inputs?

The probe reports numbers; it does not pass or fail. ``--weak-null-seed``
additionally repeats every measurement on a within-row presynaptic shuffle.
That shuffle preserves each postsynaptic node's in-degree and its exact weight
multiset but does **not** preserve out-degree, so it is strictly weaker than the
preregistered directed degree-preserving null and must never be reported as one.
"""

from __future__ import annotations

import argparse
import json
import platform
import resource
import subprocess
import sys
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

from flygi.config import FlyGIConfig, load_config
from flygi.connectome.normalize import estimate_spectral_radius
from flygi.dynamics import (
    RateParameters,
    RuntimeConnectome,
    ScipyRateNetwork,
    load_runtime_connectome,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/literal_rate.yaml"
DEFAULT_RESULTS_DIR = ROOT / "results/diagnostics"
WEAK_NULL_KIND = "within_row_presynaptic_shuffle"
WEAK_NULL_PRESERVES = ("postsynaptic in-degree", "per-row weight multiset")
WEAK_NULL_DESTROYS = ("presynaptic out-degree", "all higher-order topology")


def _peak_rss_bytes() -> int:
    """Return process peak RSS in bytes on macOS and Linux."""

    raw = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return raw if sys.platform == "darwin" else raw * 1024


def _git_revision() -> dict[str, Any]:
    def run(*args: str) -> str | None:
        try:
            return subprocess.check_output(
                ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    status = run("status", "--porcelain")
    return {
        "commit": run("rev-parse", "HEAD"),
        "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
        "clean": None if status is None else status == "",
    }


def _cosine(left: NDArray[np.floating], right: NDArray[np.floating]) -> float | None:
    left_norm = float(np.linalg.norm(left))
    right_norm = float(np.linalg.norm(right))
    if left_norm == 0.0 or right_norm == 0.0:
        return None
    return float(np.dot(left, right) / (left_norm * right_norm))


def _superclass_indices(runtime_dir: Path, superclass: str) -> NDArray[np.int64]:
    """Resolve a node-metadata superclass label to dense runtime indices."""

    metadata_path = runtime_dir / "node_metadata.npz"
    with np.load(metadata_path, allow_pickle=False) as handle:
        if "superclass" not in handle:
            raise SystemExit(f"{metadata_path} has no 'superclass' column")
        labels = handle["superclass"]
    selected = np.flatnonzero(labels == superclass).astype(np.int64)
    if selected.size == 0:
        available = sorted({str(value) for value in np.unique(labels)})
        raise SystemExit(
            f"superclass {superclass!r} matched no nodes; available labels: {available}"
        )
    return selected


def _forward_hops(
    matrix: sparse.csr_matrix,
    sources: NDArray[np.int64],
    targets: NDArray[np.int64],
    *,
    max_hops: int,
) -> dict[str, Any]:
    """BFS along directed edges from ``sources``, counting reached ``targets``.

    The stored convention is ``W[post, pre]``, so the transpose's row ``pre``
    enumerates that neuron's postsynaptic partners.
    """

    forward = matrix.T.tocsr()
    forward.sort_indices()
    node_count = matrix.shape[0]
    reached = np.zeros(node_count, dtype=bool)
    reached[sources] = True
    is_target = np.zeros(node_count, dtype=bool)
    is_target[targets] = True

    frontier = sources
    hops: list[dict[str, int]] = []
    for hop in range(1, max_hops + 1):
        candidates = np.unique(forward[frontier].indices)
        candidates = candidates[~reached[candidates]]
        if candidates.size == 0:
            break
        reached[candidates] = True
        frontier = candidates.astype(np.int64, copy=False)
        hops.append(
            {
                "hop": hop,
                "newly_reached": int(candidates.size),
                "total_reached": int(reached.sum()),
                "targets_reached": int((reached & is_target).sum()),
            }
        )
        if int((reached & is_target).sum()) == int(is_target.sum()):
            break

    reached_all = next(
        (record["hop"] for record in hops if record["targets_reached"] == int(is_target.sum())),
        None,
    )
    first_reached = next((record["hop"] for record in hops if record["targets_reached"] > 0), None)
    return {
        "hops": hops,
        "first_target_hop": first_reached,
        "all_targets_hop": reached_all,
        "targets_total": int(is_target.sum()),
        "nodes_unreached": int(node_count - reached.sum()),
    }


def _drive(
    node_count: int, indices: NDArray[np.int64], pattern: NDArray[np.float32]
) -> NDArray[np.float32]:
    vector = np.zeros(node_count, dtype=np.float32)
    vector[indices] = pattern
    return vector


def _arrival_by_internal_step(
    network: ScipyRateNetwork,
    sensory: NDArray[np.int64],
    readout: NDArray[np.int64],
    *,
    steps: int,
) -> list[dict[str, Any]]:
    """Track when constant unit sensory drive first moves the readout."""

    node_count = network.node_count
    drive = _drive(node_count, sensory, np.ones(len(sensory), dtype=np.float32))
    state = np.zeros(node_count, dtype=np.float32)
    records: list[dict[str, Any]] = []
    for step in range(1, steps + 1):
        state = network.advance(state, drive, internal_steps=1)
        values = np.abs(state[readout])
        records.append(
            {
                "internal_step": step,
                "state_mean_abs": float(np.abs(state).mean()),
                "readout_mean_abs": float(values.mean()),
                "readout_max_abs": float(values.max()),
                "readout_nonzero": int(np.count_nonzero(values > 0.0)),
            }
        )
    return records


def _memory_decay(
    network: ScipyRateNetwork,
    sensory: NDArray[np.int64],
    readout: NDArray[np.int64],
    patterns: tuple[NDArray[np.float32], NDArray[np.float32]],
    *,
    internal_steps: int,
    drive_actions: int,
    silent_actions: int,
) -> dict[str, Any]:
    """Drive two distinct histories, then measure convergence after offset."""

    node_count = network.node_count
    left = np.zeros(node_count, dtype=np.float32)
    right = np.zeros(node_count, dtype=np.float32)
    left_drive = _drive(node_count, sensory, patterns[0])
    right_drive = _drive(node_count, sensory, patterns[1])
    for _ in range(drive_actions):
        left = network.advance(left, left_drive, internal_steps=internal_steps)
        right = network.advance(right, right_drive, internal_steps=internal_steps)

    driven_readout_cosine = _cosine(left[readout], right[readout])
    baseline = float(np.linalg.norm(left - right))
    if baseline == 0.0:
        raise SystemExit("distinct drives produced identical states; probe cannot proceed")

    trace: list[dict[str, Any]] = []
    half_life: int | None = None
    for action in range(1, silent_actions + 1):
        left = network.advance(left, None, internal_steps=internal_steps)
        right = network.advance(right, None, internal_steps=internal_steps)
        remaining = float(np.linalg.norm(left - right) / baseline)
        if half_life is None and remaining < 0.5:
            half_life = action
        trace.append(
            {
                "silent_action": action,
                "state_difference_fraction": remaining,
                "readout_cosine": _cosine(left[readout], right[readout]),
            }
        )
    return {
        "driven_readout_cosine": driven_readout_cosine,
        "half_life_actions": half_life,
        "trace": trace,
    }


def _readout_code(
    network: ScipyRateNetwork,
    sensory: NDArray[np.int64],
    readout: NDArray[np.int64],
    *,
    internal_steps: int,
    settle_actions: int,
    inputs: int,
    generator: np.random.Generator,
    amplitude: float,
) -> dict[str, Any]:
    """Characterize the readout code produced by many distinct inputs."""

    node_count = network.node_count
    responses = np.empty((inputs, len(readout)), dtype=np.float32)
    for row in range(inputs):
        pattern = (generator.standard_normal(len(sensory)) * amplitude).astype(np.float32)
        drive = _drive(node_count, sensory, pattern)
        state = np.zeros(node_count, dtype=np.float32)
        for _ in range(settle_actions):
            state = network.advance(state, drive, internal_steps=internal_steps)
        responses[row] = state[readout]

    centered = responses - responses.mean(axis=0, keepdims=True)
    singular = np.linalg.svd(centered.astype(np.float64), compute_uv=False)
    energy = singular**2
    total = float(energy.sum())
    if total == 0.0:
        raise SystemExit("readout responses were identically zero; probe cannot proceed")
    explained = energy / total
    participation = float(explained.sum() ** 2 / float((explained**2).sum()))

    pairs = [
        _cosine(responses[i], responses[j]) for i in range(inputs) for j in range(i + 1, inputs)
    ]
    finite_pairs = [value for value in pairs if value is not None]
    return {
        "inputs": inputs,
        "participation_ratio": participation,
        "max_possible_components": int(min(responses.shape)),
        "top1_variance_fraction": float(explained[0]),
        "top5_variance_fraction": float(explained[:5].sum()),
        "top20_variance_fraction": float(explained[:20].sum()),
        "mean_pairwise_cosine": float(np.mean(finite_pairs)) if finite_pairs else None,
        "readout_mean_abs": float(np.abs(responses).mean()),
    }


def _weak_null(matrix: sparse.csr_matrix, seed: int) -> sparse.csr_matrix:
    """Shuffle presynaptic partners within each postsynaptic row.

    Preserves in-degree and the per-row weight multiset exactly. Destroys
    out-degree and every higher-order structure. Strictly weaker than the
    preregistered directed degree-preserving null.
    """

    generator = np.random.default_rng(seed)
    node_count = matrix.shape[0]
    indptr = np.asarray(matrix.indptr)
    indices = np.asarray(matrix.indices).copy()
    for row in range(node_count):
        start = int(indptr[row])
        stop = int(indptr[row + 1])
        if stop > start:
            indices[start:stop] = generator.choice(node_count, size=stop - start, replace=False)
    shuffled = sparse.csr_matrix(
        (np.asarray(matrix.data).copy(), indices, indptr.copy()), shape=matrix.shape
    )
    shuffled.sort_indices()
    shuffled.sum_duplicates()
    shuffled.eliminate_zeros()
    return shuffled


def _leak(config: FlyGIConfig, args: argparse.Namespace) -> float:
    return float(config.dynamics.leak if args.leak is None else args.leak)


def _gain(config: FlyGIConfig, args: argparse.Namespace) -> float:
    return float(
        config.dynamics.recurrent_gain if args.recurrent_gain is None else args.recurrent_gain
    )


def _network(
    matrix: sparse.csr_matrix, config: FlyGIConfig, args: argparse.Namespace
) -> ScipyRateNetwork:
    parameters = RateParameters(
        internal_steps=args.internal_steps,
        leak=_leak(config, args),
        recurrent_gain=_gain(config, args),
        bias=config.dynamics.bias,
    )
    return ScipyRateNetwork(matrix, parameters, copy_connectivity=False)


def _measure_condition(
    matrix: sparse.csr_matrix,
    config: FlyGIConfig,
    sensory: NDArray[np.int64],
    readout: NDArray[np.int64],
    args: argparse.Namespace,
    *,
    include_reachability: bool,
) -> dict[str, Any]:
    started = time.perf_counter()
    network = _network(matrix, config, args)
    spectral = estimate_spectral_radius(matrix, max_iterations=args.power_iterations)
    leak = _leak(config, args)
    gain = _gain(config, args)

    generator = np.random.default_rng(args.seed)
    left = (generator.standard_normal(len(sensory)) * args.amplitude).astype(np.float32)
    right = (generator.standard_normal(len(sensory)) * args.amplitude).astype(np.float32)

    record: dict[str, Any] = {
        "edges": int(matrix.nnz),
        "negative_weight_fraction": float(np.mean(np.asarray(matrix.data) < 0.0)),
        "spectral_radius": float(spectral),
        "linearized_leading_eigenvalue": (1.0 - leak) + leak * gain * float(spectral),
        "rows_without_incoming_weight": int(np.count_nonzero(np.diff(matrix.indptr) == 0)),
        "arrival_by_internal_step": _arrival_by_internal_step(
            network, sensory, readout, steps=args.arrival_steps
        ),
        "memory_decay": _memory_decay(
            network,
            sensory,
            readout,
            (left, right),
            internal_steps=args.internal_steps,
            drive_actions=args.drive_actions,
            silent_actions=args.silent_actions,
        ),
        "readout_code": _readout_code(
            network,
            sensory,
            readout,
            internal_steps=args.internal_steps,
            settle_actions=args.settle_actions,
            inputs=args.code_inputs,
            generator=np.random.default_rng(args.seed + 1),
            amplitude=args.amplitude,
        ),
    }
    if include_reachability:
        record["reachability"] = _forward_hops(matrix, sensory, readout, max_hops=args.max_hops)
    record["seconds"] = time.perf_counter() - started
    return record


def _write_json_exclusive(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(payload)


def _default_output() -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    return DEFAULT_RESULTS_DIR / f"{timestamp}-regime.json"


def _summarize(result: dict[str, Any]) -> str:
    lines: list[str] = []
    for name, record in result["conditions"].items():
        decay = record["memory_decay"]
        tail = decay["trace"][-1]
        arrival = next(
            (
                item["internal_step"]
                for item in record["arrival_by_internal_step"]
                if item["readout_nonzero"] > 0
            ),
            None,
        )
        dense = next(
            (
                item["internal_step"]
                for item in record["arrival_by_internal_step"]
                if item["readout_nonzero"] >= 0.99 * result["populations"]["readout_size"]
            ),
            None,
        )
        lines.append(
            f"  {name:<28s} edges={record['edges']:>10,d} rho={record['spectral_radius']:.4f} "
            f"first/dense readout step={arrival}/{dense} "
            f"half-life={decay['half_life_actions']} actions "
            f"remaining@{tail['silent_action']}={tail['state_difference_fraction']:.5f} "
            f"PR={record['readout_code']['participation_ratio']:.2f}"
        )
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=None,
        help="compiled runtime to probe; defaults to the config's graph.output_dir",
    )
    parser.add_argument(
        "--sensory-superclass",
        default="ol_sensory",
        help="node-metadata superclass used as the injection population",
    )
    parser.add_argument(
        "--readout-group",
        default="descending_neurons",
        help="compiled group used as the readout population",
    )
    parser.add_argument("--internal-steps", type=int, default=None, help="defaults to the config K")
    parser.add_argument("--leak", type=float, default=None, help="defaults to the config leak")
    parser.add_argument(
        "--recurrent-gain", type=float, default=None, help="defaults to the config gain"
    )
    parser.add_argument("--arrival-steps", type=int, default=16)
    parser.add_argument("--max-hops", type=int, default=8)
    parser.add_argument("--drive-actions", type=int, default=8)
    parser.add_argument("--silent-actions", type=int, default=12)
    parser.add_argument("--settle-actions", type=int, default=6)
    parser.add_argument("--code-inputs", type=int, default=32)
    parser.add_argument("--amplitude", type=float, default=0.5)
    parser.add_argument("--power-iterations", type=int, default=300)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--weak-null-seed",
        type=int,
        default=None,
        help="also measure a within-row presynaptic shuffle; NOT the preregistered null",
    )
    parser.add_argument("--output", type=Path, default=None)
    return parser


def _validate_args(args: argparse.Namespace) -> None:
    positive = {
        "arrival_steps": args.arrival_steps,
        "max_hops": args.max_hops,
        "drive_actions": args.drive_actions,
        "silent_actions": args.silent_actions,
        "settle_actions": args.settle_actions,
        "power_iterations": args.power_iterations,
    }
    for name, value in positive.items():
        if value <= 0:
            raise SystemExit(f"--{name.replace('_', '-')} must be positive")
    if args.code_inputs < 2:
        raise SystemExit("--code-inputs must be at least 2")
    if args.amplitude <= 0:
        raise SystemExit("--amplitude must be positive")
    if args.internal_steps is not None and args.internal_steps <= 0:
        raise SystemExit("--internal-steps must be positive")
    if args.leak is not None and not 0.0 < args.leak <= 1.0:
        raise SystemExit("--leak must lie in (0, 1]")
    if args.recurrent_gain is not None and args.recurrent_gain < 0.0:
        raise SystemExit("--recurrent-gain must be non-negative")


def run_probe(args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    config = load_config(args.config)
    if args.internal_steps is None:
        args.internal_steps = int(config.dynamics.internal_steps)

    runtime_dir = (
        Path(args.runtime_dir).resolve()
        if args.runtime_dir is not None
        else (ROOT / config.graph.output_dir).resolve()
    )
    load_started = time.perf_counter()
    bundle: RuntimeConnectome = load_runtime_connectome(
        runtime_dir, required_groups=(args.readout_group,)
    )
    load_seconds = time.perf_counter() - load_started

    readout = np.asarray(bundle.groups[args.readout_group], dtype=np.int64)
    sensory = _superclass_indices(runtime_dir, args.sensory_superclass)

    result: dict[str, Any] = {
        "kind": "flygi-dynamics-regime-probe",
        "schema_version": 1,
        "is_acceptance_gate": False,
        "started_utc": datetime.now(UTC).isoformat(),
        "config_path": str(
            args.config.relative_to(ROOT) if args.config.is_relative_to(ROOT) else args.config
        ),
        "runtime_dir": str(runtime_dir.relative_to(ROOT)),
        "runtime_release": bundle.manifest.get("release"),
        "runtime_preprocessing": dict(bundle.manifest.get("preprocessing", {})),
        "verified_output_hashes": dict(bundle.verified_hashes),
        "load_seconds": load_seconds,
        "operating_point": {
            "internal_steps": int(args.internal_steps),
            "leak": _leak(config, args),
            "recurrent_gain": _gain(config, args),
            "bias": float(config.dynamics.bias),
            "activation": config.dynamics.activation,
        },
        "populations": {
            "sensory_superclass": args.sensory_superclass,
            "sensory_size": int(sensory.size),
            "readout_group": args.readout_group,
            "readout_size": int(readout.size),
            "node_count": int(bundle.node_count),
        },
        "probe_arguments": {
            key: (str(value) if isinstance(value, Path) else value)
            for key, value in sorted(vars(args).items())
        },
        "provenance": {
            "git": _git_revision(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": sparse.__dict__.get("__version__") or __import__("scipy").__version__,
            "platform": platform.platform(),
            "machine": platform.machine() or None,
        },
        "conditions": {},
    }

    result["conditions"]["real"] = _measure_condition(
        bundle.matrix, config, sensory, readout, args, include_reachability=True
    )

    if args.weak_null_seed is not None:
        null_matrix = _weak_null(bundle.matrix, args.weak_null_seed)
        record = _measure_condition(
            null_matrix, config, sensory, readout, args, include_reachability=True
        )
        record["null"] = {
            "kind": WEAK_NULL_KIND,
            "seed": int(args.weak_null_seed),
            "preserves": list(WEAK_NULL_PRESERVES),
            "destroys": list(WEAK_NULL_DESTROYS),
            "is_preregistered_degree_preserving_null": False,
        }
        result["conditions"]["weak_null"] = record

    result["peak_rss_bytes"] = _peak_rss_bytes()
    result["finished_utc"] = datetime.now(UTC).isoformat()
    output = args.output or _default_output()
    return result, output


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    _validate_args(args)
    result, output = run_probe(args)
    _write_json_exclusive(output, result)
    print(f"dynamics-regime probe written to {output}")
    print(
        f"runtime={result['runtime_dir']} K={result['operating_point']['internal_steps']} "
        f"leak={result['operating_point']['leak']} gain={result['operating_point']['recurrent_gain']}"
    )
    print(
        f"sensory={result['populations']['sensory_superclass']}"
        f"({result['populations']['sensory_size']}) -> "
        f"readout={result['populations']['readout_group']}"
        f"({result['populations']['readout_size']})"
    )
    reach = result["conditions"]["real"].get("reachability", {})
    print(
        f"anatomical hops to first/all readout targets: "
        f"{reach.get('first_target_hop')}/{reach.get('all_targets_hop')}"
    )
    print(_summarize(result))
    if "weak_null" in result["conditions"]:
        print(
            "NOTE: weak_null preserves in-degree and row weights only. It is NOT the "
            "preregistered directed degree-preserving null."
        )
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("probe_dynamics_regime", main))
