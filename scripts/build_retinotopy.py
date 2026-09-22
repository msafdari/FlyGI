#!/usr/bin/env python3
"""Compile the optic-lobe retinotopic map into a runtime bundle.

The current encoder projects the ARC grid into sensory neurons through a random
sparse matrix, which destroys retinotopy: two neighbouring cells land on
unrelated neurons. The fly's visual system is built around spatial structure, so
that projection removes the one property the optic lobe exists to exploit.

Measured in MaleCNS v1.0: photoreceptors (`ol_sensory`) carry **no** column
assignment at all -- 0 of 6,098 -- so they cannot be targeted retinotopically.
The columnar coordinates live on 23,720 `ol_intrinsic` neurons spanning
``assignedOlHex1`` 1..36 and ``assignedOlHex2`` 1..39 across 892 occupied
columns, with types L1, L2, L5, Mi1, Tm1, T1 and similar. Those are the lamina
and medulla interneurons that actually carry the visual signal, and they are
where a retinotopic injection has to go.

The output is a small hashed asset beside the graph, so the deployed bundle
carries it without needing the 14 MB annotation table.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

HEX1 = "assignedOlHex1"
HEX2 = "assignedOlHex2"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/literal_rate_signed.yaml")
    parser.add_argument("--annotations", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    import pandas as pd

    from flygi.config import load_config
    from flygi.connectome.build import load_runtime_graph
    from flygi.connectome.manifest import sha256_file

    config = load_config(args.config)
    runtime_dir = Path(config.graph.output_dir)
    annotations_path = args.annotations or Path(config.data.annotations_path)
    output = runtime_dir / "retinotopy.npz"
    if output.exists() and not args.force:
        raise SystemExit(f"{output} already exists; pass --force to rebuild")

    _, node_index = load_runtime_graph(runtime_dir / "graph.npz")
    body_ids = np.asarray(node_index.body_ids)

    frame = pd.read_feather(annotations_path, columns=["bodyId", "superclass", "type", HEX1, HEX2])
    frame = frame.dropna(subset=[HEX1, HEX2])
    if frame.empty:
        raise SystemExit(f"no hex coordinates found in {annotations_path}")

    ids = frame["bodyId"].to_numpy().astype(np.uint64)
    position = np.searchsorted(body_ids, ids)
    position = np.clip(position, 0, len(body_ids) - 1)
    retained = body_ids[position] == ids
    if not retained.any():
        raise SystemExit("no hex-annotated neuron survives the runtime node filter")

    frame = frame.loc[retained]
    indices = position[retained].astype(np.int32)
    hex1 = frame[HEX1].to_numpy().astype(np.int16)
    hex2 = frame[HEX2].to_numpy().astype(np.int16)
    types = frame["type"].fillna("").to_numpy().astype("<U32")
    superclass = frame["superclass"].fillna("").to_numpy().astype("<U21")

    order = np.argsort(indices, kind="stable")
    arrays = {
        "format_version": np.asarray([1], dtype=np.int16),
        "node_indices": indices[order],
        "hex1": hex1[order],
        "hex2": hex2[order],
        "type": types[order],
        "superclass": superclass[order],
    }
    # np.savez_compressed appends .npz when the name lacks it, so the partial
    # path has to already end in .npz for the atomic replace to find it.
    temporary = output.with_name(output.name + ".partial.npz")
    np.savez_compressed(temporary, **arrays)
    temporary.replace(output)

    columns = len({(int(a), int(b)) for a, b in zip(arrays["hex1"], arrays["hex2"], strict=True)})
    report = {
        "output": str(output),
        "bytes": output.stat().st_size,
        "sha256": sha256_file(output),
        "neurons": len(arrays["node_indices"]),
        "occupied_columns": columns,
        "hex1_range": [int(arrays["hex1"].min()), int(arrays["hex1"].max())],
        "hex2_range": [int(arrays["hex2"].min()), int(arrays["hex2"].max())],
        "superclasses": sorted({str(s) for s in arrays["superclass"]}),
        "top_types": sorted({str(t) for t in arrays["type"]})[:10],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
