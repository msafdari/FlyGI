"""Extract the six recorded clicks for publicity, without choosing new actions.

Run from the repo: .venv/bin/python docs/social/instagram_20261104/reel/replay.py
Raw frames and PNGs go to ignored results/social/instagram_20261104/reel/.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "results/social/instagram_20261104/reel"
SOURCE = ROOT / "results/connectome_agent/sg-clickhead-retinotopic.rows.jsonl.gz"
EXPECTED_SOURCE_SHA256 = "e1e652d6f167f6460e889cbcf2455f1246043c16ef9b6a48d13effeae4ed0238"
OUTPUT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(OUTPUT / "mpl-cache"))
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
from PIL import Image
from arc_agi.rendering import COLOR_MAP, frame_to_rgb_array
from flygi.encoding.features import latest_grid


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    assert digest(SOURCE) == EXPECTED_SOURCE_SHA256, "archive changed"
    spec = importlib.util.spec_from_file_location("_reel_replay", ROOT / "scripts/replay_click_coordinate_ab.py")
    assert spec and spec.loader
    helpers = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helpers
    spec.loader.exec_module(helpers)
    baseline = helpers._load_baseline_module()
    runtime = baseline.load_arc_runtime()
    with gzip.open(SOURCE, "rt") as handle:
        row = next(r for r in map(json.loads, handle) if r["game_id"] == "r11l-495a7899" and r["seed"] == 1)
    frozen = baseline.discover_games(runtime, ROOT / "environment_files", ["r11l"])[0]
    arcade = baseline._new_offline_arcade(runtime, ROOT / "environment_files")
    baseline._seed_process_for_environment(row["environment_seed"])
    env = arcade.make(frozen.game_id, seed=row["environment_seed"], save_recording=False, include_frame_data=False)
    frame = env.observation_space
    assert frame is not None
    manifest = {
        "schema": "flygi.reel-replay.v1",
        "source_archive": str(SOURCE.relative_to(ROOT)),
        "source_archive_sha256": EXPECTED_SOURCE_SHA256,
        "game_manifest": frozen.manifest(),
        "policy_seed_label": 1,
        "environment_seed": row["environment_seed"],
        "coordinate_semantics": "Executed payload x is screen column, y is screen row, zero-based. Do not transpose because the historical predictor had a legacy internal coordinate convention.",
        "frame_semantics": "All native response frames are preserved in their returned order; endpoints are the last grid. Action-six endpoint shows level two, not the solved previous board. Display timing is editorial, not a wall-clock benchmark.",
        "palette_source": "arc_agi.rendering.COLOR_MAP",
        "palette_rgba": COLOR_MAP,
        "runtime_versions": {name: importlib.metadata.version(name) for name in ("arc-agi", "arcengine")},
        "game_credit": "ARC Prize Foundation, R11L, MIT License, copyright 2026.",
        "snapshots": [],
        "actions": [],
    }
    raw = []

    def capture(response, completed: int) -> None:
        grids = [np.asarray(grid) for grid in response.frame]
        assert grids and all(grid.shape == (64, 64) for grid in grids)
        assert np.array_equal(grids[-1], latest_grid(response))
        paths = []
        for index, grid in enumerate(grids):
            filename = f"action-{completed:02d}-frame-{index:03d}.png"
            Image.fromarray(frame_to_rgb_array(completed, grid, scale=1)).save(OUTPUT / filename)
            paths.append(filename)
        endpoint = OUTPUT / f"endpoint-{completed:02d}.png"
        endpoint.write_bytes((OUTPUT / paths[-1]).read_bytes())
        manifest["snapshots"].append({
            "actions_completed": completed,
            "levels_completed": int(response.levels_completed),
            "observation_sha256": baseline._frame_fingerprint(response),
            "native_frame_count": len(grids),
            "native_frames": paths,
            "endpoint": endpoint.name,
            "endpoint_sha256": digest(endpoint),
        })
        raw.append({"actions_completed": completed, "grids": [grid.tolist() for grid in grids]})

    capture(frame, 0)
    # ASSUMPTION: the cached game and stored seed reproduce the archived run.
    # All twelve before/after response hashes must match before provenance is saved.
    for count, entry in enumerate(row["trace"][:6], start=1):
        before = baseline._frame_fingerprint(frame)
        assert before == entry["observation_before_sha256"], (count, "before")
        payload = dict(entry.get("payload") or {})
        response = env.step(helpers._make_action(runtime, entry["action_id"]), data=payload)
        after = baseline._frame_fingerprint(response)
        assert after == entry["observation_after_sha256"], (count, "after")
        assert int(response.levels_completed) == entry["levels_completed_after"]
        manifest["actions"].append({
            "number": count, "action_id": entry["action_id"], "payload": payload,
            "before_sha256": before, "after_sha256": after,
            "levels_completed_before": int(frame.levels_completed),
            "levels_completed_after": int(response.levels_completed),
        })
        capture(response, count)
        frame = response
    assert len(manifest["actions"]) == 6
    assert manifest["snapshots"][0]["levels_completed"] == 0 and frame.levels_completed == 1
    (OUTPUT / "raw_frames.json").write_text(json.dumps(raw, separators=(",", ":")) + "\n")
    text = json.dumps(manifest, indent=2) + "\n"
    (OUTPUT / "manifest.json").write_text(text)
    Path(__file__).with_name("replay_provenance.json").write_text(text)
    print("Verified all 12 before/after hashes; six recorded actions; first level cleared.")
    print("Native frame counts:", [s["native_frame_count"] for s in manifest["snapshots"]])
    print("Output:", OUTPUT)


if __name__ == "__main__":
    main()
