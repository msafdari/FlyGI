#!/usr/bin/env python3
"""Frozen visual-memory entry falsifier; no policy, plasticity, or ARC actions.

Neural representations are computed only by the pinned MaleCNS rate model.
Nearest-exemplar scoring is an external diagnostic, never an agent component.
See docs/experiments/visual_memory_entry.md for assumptions and the kill rule.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import subprocess
import tempfile
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from flygi.connectome.manifest import sha256_file, software_versions
from flygi.dynamics import RateParameters, ScipyRateNetwork, load_runtime_connectome
from flygi.encoding.features import FEATURE_DIMENSION, ObservationFeatures
from flygi.encoding.retinotopic import RetinotopicOptions, build_retinotopic_projection

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
ANNOTATIONS = ROOT / "data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather"
PROTOCOL = ROOT / "docs/experiments/visual_memory_entry.md"
EXPECTED = {
    PROTOCOL: "220591b7b93734e90bdf4fe16123143c54222f4904ac9da21070b5f9827fcf08",
    RUNTIME / "graph.npz": "f5553b59d4efaab36600cee5c319d524e3023b27906642720c634f3a000babb9",
    RUNTIME
    / "node_metadata.npz": "2a84309be4f1ea860032476390de1ffa3b8ce635710898a13466a29e4d00eb0c",
    RUNTIME / "retinotopy.npz": "ebc2b699e541330097a257003c2346f367d4beda1f04e88b2aaa1e1542db1a8d",
    ANNOTATIONS: "2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2",
}
CENTERS = tuple(itertools.product((20, 28, 36, 44), repeat=2))


def require(passed: bool, message: str) -> None:
    if not passed:
        raise ValueError(message)


def array_hash(values: np.ndarray) -> str:
    values = np.ascontiguousarray(values)
    return hashlib.sha256(
        f"{values.dtype.str}|{values.shape}|".encode() + values.tobytes()
    ).hexdigest()


def make_panel() -> np.ndarray:
    # ASSUMPTION A1: synthetic luminance rectangles test this one visual relation.
    # The central panel was selected for sensory coverage before neural outcomes.
    panel = np.zeros((16, 2, 64, 64), dtype=np.int8)
    for p, (row, col) in enumerate(CENTERS):
        panel[p, 0, row - 1 : row + 2, col - 4 : col + 5] = 15
        panel[p, 1, row - 4 : row + 5, col - 1 : col + 2] = 15
    return panel


def transfer_scores(values: np.ndarray) -> dict:
    values = np.asarray(values, dtype=np.float64)
    require(
        values.ndim == 3 and values.shape[:2] == (16, 2) and values.shape[2] > 0,
        "representations must have shape (16,2,nonzero_dimension)",
    )
    require(bool(np.isfinite(values).all()), "nonfinite representation")
    # ASSUMPTIONS A3/A4: positive rates and a scale-invariant external diagnostic.
    # Apply the same transform to both interface baselines; zero codes tie.
    positive = np.maximum(values, 0.0)
    norms = np.linalg.norm(positive, axis=2, keepdims=True)
    normalized = np.divide(positive, norms, out=np.zeros_like(positive), where=norms > 0)
    decisions, margins, per_position = [], [], []
    for target in range(16):
        local = []
        for exemplar in range(16):
            if target == exemplar:
                continue
            for shape in range(2):
                distance = ((normalized[exemplar] - normalized[target, shape]) ** 2).sum(axis=1)
                margin = float(distance[1 - shape] - distance[shape])
                decision = 1.0 if margin > 1e-12 else 0.0 if margin < -1e-12 else 0.5
                margins.append(margin)
                decisions.append(decision)
                local.append(decision)
        per_position.append(float(np.mean(local)))
    return {
        "accuracy": float(np.mean(per_position)),
        "per_position": per_position,
        "decisions": decisions,
        "margins": margins,
    }


def scientific_gate(native_values: np.ndarray, scores: dict) -> dict:
    positive = np.maximum(np.asarray(native_values, dtype=np.float64), 0.0)
    rms = np.sqrt(np.mean(positive**2, axis=2))
    differences = np.sqrt(np.mean((positive[:, 0] - positive[:, 1]) ** 2, axis=1))
    native = scores["native"]
    # HYPOTHESIS/A5: all bars are descriptive engineering choices, frozen before
    # outcomes. A small/silent signal fails science; it is not a broken contract.
    checks = {
        "absolute_accuracy": native["accuracy"] >= 0.75,
        # All 480 scores are exact half-credits. A 0.10 advantage is exactly
        # 48 credits; subtracting rounded accuracies can reject this boundary.
        "sensory_margin": sum(native["decisions"]) - sum(scores["sensory"]["decisions"]) >= 48,
        "type_mean_margin": sum(native["decisions"]) - sum(scores["type_mean"]["decisions"]) >= 48,
        "position_count": sum(s > 0.5 for s in native["per_position"]) >= 12,
        "native_signal_floor": bool(np.all(rms > 1e-7)),
        "paired_shape_floor": bool(np.all(differences > 1e-7)),
        "graph_off_chance": scores["graph_off"]["accuracy"] == 0.5,
    }
    return {"passed": all(checks.values()), "checks": checks}


def git_state() -> dict:
    def git(*args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

    return {
        "commit": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "tracked_changes": git("status", "--porcelain", "--untracked-files=no"),
        "untracked": git("ls-files", "--others", "--exclude-standard").splitlines(),
    }


def execute(result: dict, emit) -> None:
    result["git"] = git_state()
    require(not result["git"]["tracked_changes"], "checkpoint tracked source before outcomes")
    result["hashes"] = {}
    for path, expected in EXPECTED.items():
        digest = sha256_file(path)
        result["hashes"][str(path.relative_to(ROOT))] = digest
        require(digest == expected, f"asset hash mismatch: {path.name}")
    for path in (Path(__file__), PROTOCOL, ROOT / "EXPERIMENTS.yaml", RUNTIME / "manifest.json"):
        result["hashes"][str(path.relative_to(ROOT))] = sha256_file(path)
    bundle = load_runtime_connectome(RUNTIME)
    require((bundle.node_count, bundle.edge_count) == (166700, 24994595), "graph counts")
    ann = pd.read_feather(ANNOTATIONS).set_index("bodyId")
    ids = bundle.node_index.body_ids
    ordered = ann.loc[ids]
    kc = np.flatnonzero((ordered["class"] == "Kenyon_Cell") & (ordered["type"] == "KCg-d"))
    body_hash = hashlib.sha256("".join(f"{int(i)}\n" for i in ids[kc]).encode()).hexdigest()
    require(
        body_hash == "5de316386283b16376b1c23025b63f89e600ca452d6025907e4bf10b0dd6144e",
        "exact KCg-d body list",
    )
    require(
        len(kc) == 206
        and ordered.iloc[kc].somaSide.value_counts().to_dict() == {"R": 107, "L": 99},
        "KC count/laterality",
    )
    with np.load(RUNTIME / "node_metadata.npz", allow_pickle=False) as meta:
        require(np.array_equal(meta["body_ids"], ids), "metadata ordering")
        require(
            np.array_equal(
                np.flatnonzero((meta["class"] == "Kenyon_Cell") & (meta["type"] == "KCg-d")), kc
            ),
            "raw/runtime selector",
        )
    # ASSUMPTION A1: existing declared ON/OFF plumbing, no temporal-change channel.
    projection = build_retinotopic_projection(
        RUNTIME, bundle.node_count, options=RetinotopicOptions(input_scale=1, change_gain=0)
    )
    sensory = projection.sensory_indices
    require(len(sensory) == 23720 and len(np.unique(sensory)) == 23720, "sensory population")
    require(not np.intersect1d(kc, sensory).size, "KC directly driven")
    types = ordered.iloc[sensory].type.to_numpy()
    names = sorted(set(types))
    require(len(names) == 15, "sensory type count")
    panel = make_panel()
    require(np.all(np.count_nonzero(panel, axis=(2, 3)) == 27), "panel ink")
    drives = np.stack(
        [
            projection.drive_features(
                ObservationFeatures(np.zeros(FEATURE_DIMENSION, dtype=np.float32), grid, 0)
            )
            for grid in panel.reshape(32, 64, 64)
        ]
    )
    allowed = np.zeros(bundle.node_count, dtype=bool)
    allowed[sensory] = True
    require(bool(np.isfinite(drives).all() and np.all(drives[:, ~allowed] == 0)), "drive scope")
    support = np.count_nonzero(drives, axis=1)
    require((int(support.min()), int(support.max())) == (178, 325), "static support golden")
    drive_hashes = [array_hash(v) for v in drives]
    require(len(set(drive_hashes)) == 32, "aliased scenes")
    drives.flags.writeable = False
    sense = drives[:, sensory].reshape(16, 2, -1)
    means = np.stack(
        [sense[..., types == name].mean(axis=2, dtype=np.float64) for name in names], axis=2
    )
    result.update(
        {
            "software": software_versions(),
            "encoder": projection.describe(),
            "kc_ids": ids[kc].tolist(),
            "kc_ids_sha256": body_hash,
            "sensory_ids_sha256": array_hash(ids[sensory]),
            "type_names": names,
            "centers": CENTERS,
            "panel_sha256": array_hash(panel),
            "grids": panel.tolist(),
            "type_means": means.tolist(),
            "stimuli": [],
            "conditions": {},
        }
    )
    for grid, drive, digest in zip(panel.reshape(32, 64, 64), drives, drive_hashes, strict=True):
        nz = np.flatnonzero(drive)
        result["stimuli"].append(
            {
                "grid_sha256": array_hash(grid),
                "drive_sha256": digest,
                "indices": nz.tolist(),
                "values": drive[nz].tolist(),
                "drive_l1": float(np.abs(drive).sum()),
                "drive_signed_sum": float(drive.sum(dtype=np.float64)),
                "support": len(nz),
            }
        )
    emit("contracts_passed", scenes=32, kc_count=len(kc))
    for name, gain in (("native", 2.0), ("graph_off", 0.0)):
        # ASSUMPTION A2: fixed horizon/operating point, not a converged or physical clock.
        network = ScipyRateNetwork(
            bundle.matrix,
            RateParameters(internal_steps=32, leak=0.3, recurrent_gain=gain, bias=0),
            copy_connectivity=False,
        )
        condition = {
            "parameters": asdict(network.parameters),
            "spmv": network.spmv.describe(),
            "trials": [],
            "same_live_csr": network.connectivity is bundle.matrix,
        }
        result["conditions"][name] = condition
        outputs = []
        try:
            for scene, drive in enumerate(drives):
                state = network.initial_state()
                snapshots = []
                for steps, total in ((4, 4), (4, 8), (8, 16), (16, 32)):
                    state = network.advance(state, drive, internal_steps=steps)
                    readout = state[kc]
                    snapshots.append(
                        {
                            "step": total,
                            "kc_signed": readout.tolist(),
                            "state_max_abs": float(np.max(np.abs(state))),
                            "kc_positive_fraction": float(np.mean(readout > 0)),
                            "kc_positive_rms": float(
                                np.sqrt(np.mean(np.maximum(readout.astype(np.float64), 0) ** 2))
                            ),
                        }
                    )
                outputs.append(state[kc].copy())
                condition["trials"].append({"scene": scene, "snapshots": snapshots})
                emit("scene_complete", condition=name, scene=scene)
            # Repeat from zero with one 32-step call: validates reset and chunk timing.
            repeated = network.advance(network.initial_state(), drives[0], internal_steps=32)[kc]
            require(np.array_equal(repeated, outputs[0]), f"{name} reset/chunk mismatch")
            condition["reset_exact"] = True
        finally:
            network.spmv.close()
            condition["spmv_closed"] = True
        values = np.asarray(outputs).reshape(16, 2, len(kc))
        require(bool(np.isfinite(values).all()), "nonfinite neural output")
        if name == "graph_off":
            require(bool(np.all(values == 0)), "graph-off KC nonzero")
        condition["raw_readout"] = values.tolist()
        condition["score"] = transfer_scores(values)
        if name == "graph_off":
            require(condition["score"]["accuracy"] == 0.5, "graph-off scorer contract")
    require([array_hash(v) for v in drives] == drive_hashes, "mutated drives")
    require(all(c["same_live_csr"] for c in result["conditions"].values()), "real/off CSR identity")
    scores = {name: c["score"] for name, c in result["conditions"].items()}
    scores.update(sensory=transfer_scores(sense), type_mean=transfer_scores(means))
    gate = scientific_gate(np.asarray(result["conditions"]["native"]["raw_readout"]), scores)
    result.update(
        status="complete",
        contract_valid=True,
        scores=scores,
        gate=gate,
        scientific_verdict="pass" if gate["passed"] else "fail",
    )


def atomic_json(path: Path, result: dict) -> None:
    """Publish complete finite JSON atomically without overwriting any result."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=path.parent, suffix=".pending", delete=False
        ) as out:
            temporary = Path(out.name)
            json.dump(result, out, allow_nan=False, separators=(",", ":"))
            out.flush()
            os.fsync(out.fileno())
        os.link(temporary, path)  # Atomic no-overwrite publication on this filesystem.
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        parser.error(f"refusing overwrite: {output}")
    events_path = output.with_suffix(output.suffix + ".events.jsonl")
    try:
        events = events_path.open("x")
    except FileExistsError:
        parser.error(f"existing run reservation: {events_path}; preserve and diagnose it")
    start = time.monotonic()
    result = {
        "schema": "flygi.visual-memory-entry.v1",
        "hypothesis": "H-VISUAL-MEMORY-ENTRY",
        "status": "invalid",
        "contract_valid": False,
        "scientific_verdict": None,
        "created_utc": datetime.now(UTC).isoformat(),
    }
    with events:

        def emit(event, **data):
            record = {"event": event, "elapsed_s": time.monotonic() - start, **data}
            events.write(json.dumps(record, allow_nan=False) + "\n")
            events.flush()
            if event != "scene_complete" or data["scene"] % 8 == 7:
                print(json.dumps(record), flush=True)

        emit("run_start")
        try:
            execute(result, emit)
        except (Exception, KeyboardInterrupt) as exc:
            result.update(
                status="invalid",
                contract_valid=False,
                scientific_verdict=None,
                error=f"{type(exc).__name__}: {exc}",
            )
        result["elapsed_s"] = time.monotonic() - start
        atomic_json(output, result)
        emit("run_end", status=result["status"], verdict=result["scientific_verdict"])
    return 1 if not result["contract_valid"] else 0 if result["scientific_verdict"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
