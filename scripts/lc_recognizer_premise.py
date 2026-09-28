#!/usr/bin/env python3
"""H-LC-RECOGNIZER / H-LH-RECOGNIZER premise-killer.

HYPOTHESIS (registered 2026-09-27, before any build): the fly's visual
projection neurons -- the LC/LPLC object-class detectors that in the animal
RELEASE stereotyped behavioural programs (LC16 backing-up, LPLC2 escape) --
and the lateral horn, the innate stimulus->valence mapper, carry enough
game-identity information from single frames to serve as the RECOGNIZER of
a fixed-action-pattern library (recognize the archetype, release the
program). The load-bearing fly claim is the EYE MAP: LC dendrites integrate
over retinotopic neighbourhoods, so their recognition signal should depend
on retinotopy being real.

PREREGISTERED DESIGN, before running:
  * Frames: K random-legal-play frames per public game, captured offline,
    one shared capture file for every arm.
  * Per arm, per frame, STATELESS drive: state = advance(initial_state,
    encoder(frame), internal_steps from the config); read the raw activation
    of (a) LC-family nodes (type prefix LC/LPLC, 4,674) and (b) lateral horn
    nodes (type prefix LH, 2,028).
  * Task: 25-way game identification, nearest class centroid, split-half
    (centroids from the first half of each game's frames, accuracy on the
    second half). No training, no learned parameters.
  * Arms: REAL = configs/literal_rate_bioeye_lc.yaml (bio-eye retinotopic
    encoder). CONTROL = configs/literal_rate_lc_readout.yaml (the
    established scrambled sparse-projection encoder, identical readout,
    identical graph) -- the fly-attribution twin that destroys retinotopy
    and keeps everything else.
  * TRIVIAL ALTERNATIVE (named per the operating directive): nearest
    centroid on the raw 64x64 grid one-hot colour histogram per 8x8 block
    (1,024 dims, no fly). If the real arm cannot beat the scrambled
    control, the eye map contributes nothing to recognition and the
    LC-recognizer premise is DEAD regardless of absolute accuracy. The raw
    baseline states how much signal a trivial reader already gets.

KILL CONDITION, stated before the run: real_accuracy <= control_accuracy
on both LC and LH readouts.

AMENDED 2026-09-27 BEFORE ANY VERDICT (first probe run saturated): 25-way
game ID is at ceiling for every arm INCLUDING the trivial baseline (1.0
everywhere) -- no headroom, so it discriminates nothing. The preregistered
primary endpoint becomes HELD-OUT-GAME dead-vs-live recognition, the actual
fixed-action-pattern question (an unseen game's CLASS, not a seen game's
identity): leave one game out, class centroids from the remaining 24 games
(mean of per-game centroids, so game count does not weight the class),
classify every frame of the held-out game. Dead list measured from the
union of every battery rows file (11 games: bp35 dc22 ft09 ka59 ls20 re86
sb26 sc25 su15 tu93 wa30). Same kill condition, on this endpoint; the
saturated game-ID number is reported alongside.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

DEAD_GAMES = {
    "bp35", "dc22", "ft09", "ka59", "ls20", "re86",
    "sb26", "sc25", "su15", "tu93", "wa30",
}


def _load_baseline() -> Any:
    path = ROOT / "scripts" / "evaluate_random_baseline.py"
    spec = importlib.util.spec_from_file_location("_flygi_lc_recognizer_base", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def capture(args: argparse.Namespace) -> None:
    """Play random-legal actions offline and save frames for every game."""

    import numpy as np

    base = _load_baseline()
    runtime = base.load_arc_runtime()
    games = base.discover_games(runtime, args.environments_dir.resolve(), ["all"])
    from flygi.encoding.features import latest_grid

    arcade = base._new_offline_arcade(runtime, args.environments_dir.resolve())
    scorecard_id = arcade.open_scorecard(
        tags=["diagnostic", "lc-recognizer-capture"], opaque={}
    )
    grids: dict[str, list[Any]] = {}
    for game in games:
        environment_seed, policy_seed = base.derived_run_seeds(args.seed, game.game_id)
        base._seed_process_for_environment(environment_seed)
        environment = arcade.make(
            game.game_id,
            seed=environment_seed,
            scorecard_id=scorecard_id,
            save_recording=False,
            include_frame_data=False,
        )
        policy = base.RandomLegalPolicy(runtime.GameAction, seed=policy_seed)
        frame = environment.observation_space
        collected = [np.asarray(latest_grid(frame), dtype=np.int8).copy()]
        while len(collected) < args.frames_per_game:
            action = policy.choose_action(frame)
            payload = base._action_payload(action)
            response = environment.step(action, data=payload, reasoning=None)
            if response is None:
                break
            frame = response
            collected.append(np.asarray(latest_grid(frame), dtype=np.int8).copy())
        grids[game.game_id.split("-")[0]] = collected
        print(f"{game.game_id}: {len(collected)} frames", flush=True)
    arrays = {gid: np.stack(frames) for gid, frames in grids.items()}
    np.savez_compressed(args.capture_file, **arrays)
    print(f"wrote {args.capture_file}")


def _grid_baseline_features(grids: Any) -> Any:
    """Trivial alternative: per-8x8-block colour histogram, 1,024 dims."""

    import numpy as np

    n = grids.shape[0]
    blocks = grids.reshape(n, 8, 8, 8, 8).swapaxes(2, 3).reshape(n, 64, 64)
    out = np.zeros((n, 64, 16), dtype=np.float32)
    for b in range(64):
        for c in range(16):
            out[:, b, c] = (blocks[:, b, :] == c).mean(axis=1)
    return out.reshape(n, -1)


def _split_half_accuracy(features: Any, labels: Any) -> float:
    """Centroids from each game's first half of frames; score the second."""

    import numpy as np

    train_mask = np.zeros(len(labels), dtype=bool)
    for label in np.unique(labels):
        idx = np.flatnonzero(labels == label)
        train_mask[idx[: len(idx) // 2]] = True
    classes = np.unique(labels)
    centroids = np.stack(
        [features[train_mask & (labels == c)].mean(axis=0) for c in classes]
    )
    test = features[~train_mask]
    truth = labels[~train_mask]
    # Cosine distance: activation scale differs across encoders by design.
    def normalize(m: Any) -> Any:
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        return m / np.maximum(norms, 1e-12)

    scores = normalize(test) @ normalize(centroids).T
    predicted = classes[np.argmax(scores, axis=1)]
    return float((predicted == truth).mean())


def _normalize(matrix: Any) -> Any:
    import numpy as np

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.maximum(norms, 1e-12)


def _holdout_dead_vs_live(features: Any, game_names: list[str], labels: Any) -> dict[str, Any]:
    """Leave one game out; classify its frames dead-vs-live by class centroid.

    Class centroids are means of per-game centroids so 11-vs-14 game counts
    do not weight the classes.
    """

    import numpy as np

    normalized = _normalize(features)
    game_centroids = {
        name: normalized[labels == i].mean(axis=0)
        for i, name in enumerate(game_names)
    }
    per_game: dict[str, float] = {}
    for i, held_out in enumerate(game_names):
        dead = [v for n, v in game_centroids.items() if n != held_out and n in DEAD_GAMES]
        live = [v for n, v in game_centroids.items() if n != held_out and n not in DEAD_GAMES]
        centroids = _normalize(np.stack([np.mean(dead, axis=0), np.mean(live, axis=0)]))
        scores = normalized[labels == i] @ centroids.T
        predicted_dead = scores[:, 0] > scores[:, 1]
        truth = held_out in DEAD_GAMES
        per_game[held_out] = float((predicted_dead == truth).mean())
    return {
        "mean_accuracy": float(np.mean(list(per_game.values()))),
        "per_game": per_game,
    }


def probe(args: argparse.Namespace) -> None:
    import numpy as np

    from flygi.arc.factory import build_connectome_policy
    from flygi.config import load_config
    from flygi.encoding.features import encode_observation

    with np.load(args.capture_file) as archive:
        grids = {k: archive[k] for k in archive.files}
    game_names = list(grids.keys())
    labels = np.concatenate(
        [np.full(len(v), i) for i, v in enumerate(grids.values())]
    )
    stacked = np.concatenate(list(grids.values()), axis=0)
    print(f"{len(grids)} games, {len(stacked)} frames", flush=True)

    baseline_features = _grid_baseline_features(stacked)
    report: dict[str, Any] = {
        "frames_per_game": int(stacked.shape[0] / len(grids)),
        "arms": {},
        "baseline_grid_histogram": _split_half_accuracy(baseline_features, labels),
        "baseline_holdout_dead_vs_live": _holdout_dead_vs_live(
            baseline_features, game_names, labels
        )["mean_accuracy"],
        "chance": 1.0 / len(grids),
        "holdout_chance": 0.5,
    }
    print(
        f"raw-grid baseline: game-id {report['baseline_grid_histogram']:.4f}, "
        f"holdout dead/live {report['baseline_holdout_dead_vs_live']:.4f}",
        flush=True,
    )

    class _NullActions:
        RESET = 0

        @staticmethod
        def from_id(identifier: int) -> int:
            return identifier

    class _Frame:
        def __init__(self, g: Any) -> None:
            self.frame = [g]

    for arm_name, config_path in (
        ("real_bioeye", "configs/literal_rate_bioeye_lc.yaml"),
        ("control_scrambled", "configs/literal_rate_lc_readout.yaml"),
    ):
        config = load_config(ROOT / config_path)
        assembled = build_connectome_policy(config, _NullActions)
        network = assembled.policy._network
        internal_steps = assembled.policy.internal_steps
        projection = assembled.projection
        with np.load(
            Path(config.graph.output_dir) / "node_metadata.npz", allow_pickle=False
        ) as archive:
            types = archive["type"].astype("U")
        groups = {
            "lc_family": np.flatnonzero(
                np.char.startswith(types, "LC") | np.char.startswith(types, "LPLC")
            ),
            "lateral_horn": np.flatnonzero(np.char.startswith(types, "LH")),
        }
        cache = ROOT / "results" / "diagnostics" / f"recognizer_features_{arm_name}.npz"
        if cache.exists():
            with np.load(cache) as archive:
                collected = {name: archive[name] for name in groups}
            print(f"  {arm_name}: loaded cached features", flush=True)
        else:
            collected = {
                name: np.zeros((len(stacked), len(idx)), dtype=np.float32)
                for name, idx in groups.items()
            }
            initial = network.initial_state()
            for row, grid in enumerate(stacked):
                features = encode_observation(
                    _Frame(grid),
                    previous_grid=None,
                    previous_action_id=None,
                    available_action_ids=(6,),
                )
                drive = projection.drive_features(features)
                state = network.advance(initial, drive, internal_steps=internal_steps)
                for name, idx in groups.items():
                    collected[name][row] = state[idx]
                if row % 200 == 0:
                    print(f"  {arm_name}: {row}/{len(stacked)}", flush=True)
            np.savez_compressed(cache, **collected)
        report["arms"][arm_name] = {
            name: {
                "game_id_split_half": _split_half_accuracy(vectors, labels),
                "holdout_dead_vs_live": _holdout_dead_vs_live(
                    vectors, game_names, labels
                ),
            }
            for name, vectors in collected.items()
        }
        print(f"{arm_name}: {json.dumps(report['arms'][arm_name])}", flush=True)
        del assembled, network, projection, collected

    real = report["arms"]["real_bioeye"]
    control = report["arms"]["control_scrambled"]
    report["kill_condition_met"] = bool(
        real["lc_family"]["holdout_dead_vs_live"]["mean_accuracy"]
        <= control["lc_family"]["holdout_dead_vs_live"]["mean_accuracy"]
        and real["lateral_horn"]["holdout_dead_vs_live"]["mean_accuracy"]
        <= control["lateral_horn"]["holdout_dead_vs_live"]["mean_accuracy"]
    )
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["capture", "probe"])
    parser.add_argument("--frames-per-game", type=int, default=40)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--environments-dir", type=Path, default=ROOT / "environment_files"
    )
    parser.add_argument(
        "--capture-file",
        type=Path,
        default=ROOT / "results" / "diagnostics" / "recognizer_frames.npz",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "recognizer_premise.json",
    )
    args = parser.parse_args()
    if args.mode == "capture":
        capture(args)
    else:
        probe(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
