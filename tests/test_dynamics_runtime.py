"""Verified runtime-bundle loading for full-graph dynamics."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from flygi.connectome.build import BuildOptions, build_connectome
from flygi.connectome.manifest import HashMismatchError
from flygi.dynamics.runtime import load_runtime_connectome


def _build_runtime(
    destination: Path,
    annotations: pd.DataFrame,
    neurotransmitters: pd.DataFrame,
    *,
    groups: dict[str, dict[str, object]],
) -> Path:
    body_ids = [int(value) for value in annotations["bodyId"]]
    weights = pd.DataFrame(
        {
            "body_pre": pd.Series(body_ids[:2], dtype="int64"),
            "body_post": pd.Series(body_ids[1:], dtype="int64"),
            "weight": pd.Series([2, 3], dtype="int64"),
        }
    )
    build_connectome(
        weights,
        annotations,
        neurotransmitters,
        destination,
        options=BuildOptions(
            weight_transform="raw",
            sign_mode="unsigned",
            normalization="none",
            allow_self_edges=False,
            node_filter_column=None,
        ),
        group_definitions=groups,
    )
    return destination


def test_load_runtime_connectome_verifies_cross_checks_and_freezes(
    tmp_path: Path,
    tiny_annotations: pd.DataFrame,
    tiny_neurotransmitters: pd.DataFrame,
) -> None:
    runtime = _build_runtime(
        tmp_path / "runtime",
        tiny_annotations,
        tiny_neurotransmitters,
        groups={"descending_neurons": {"superclass": "descending"}},
    )

    bundle = load_runtime_connectome(runtime)

    assert bundle.node_count == 3
    assert bundle.edge_count == 2
    assert bundle.matrix.shape == (3, 3)
    assert bundle.matrix.dtype == np.float32
    assert bundle.matrix.has_canonical_format
    assert len(bundle.verified_hashes) == 3
    np.testing.assert_array_equal(bundle.groups["descending_neurons"], [2])
    assert not bundle.matrix.data.flags.writeable
    assert not bundle.matrix.indices.flags.writeable
    assert not bundle.matrix.indptr.flags.writeable
    assert not bundle.groups["descending_neurons"].flags.writeable

    with pytest.raises(ValueError, match="read-only"):
        bundle.matrix.data[0] = np.float32(9.0)
    with pytest.raises(TypeError):
        bundle.groups["other"] = np.asarray([0], dtype=np.int32)  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        bundle.matrix = bundle.matrix  # type: ignore[misc]


def test_load_runtime_connectome_detects_output_tampering(
    tmp_path: Path,
    tiny_annotations: pd.DataFrame,
    tiny_neurotransmitters: pd.DataFrame,
) -> None:
    runtime = _build_runtime(
        tmp_path / "runtime",
        tiny_annotations,
        tiny_neurotransmitters,
        groups={"descending_neurons": {"superclass": "descending"}},
    )
    with (runtime / "graph.npz").open("ab") as stream:
        stream.write(b"tampered")

    with pytest.raises(HashMismatchError, match="SHA-256 mismatch"):
        load_runtime_connectome(runtime)


def test_load_runtime_connectome_rejects_manifest_count_mismatch(
    tmp_path: Path,
    tiny_annotations: pd.DataFrame,
    tiny_neurotransmitters: pd.DataFrame,
) -> None:
    runtime = _build_runtime(
        tmp_path / "runtime",
        tiny_annotations,
        tiny_neurotransmitters,
        groups={"descending_neurons": {"superclass": "descending"}},
    )
    manifest_path = runtime / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["counts"]["runtime_nonzero_edges"] += 1
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="edge count disagrees"):
        load_runtime_connectome(runtime)


def test_load_runtime_connectome_requires_declared_nonempty_group(
    tmp_path: Path,
    tiny_annotations: pd.DataFrame,
    tiny_neurotransmitters: pd.DataFrame,
) -> None:
    runtime = _build_runtime(
        tmp_path / "runtime",
        tiny_annotations,
        tiny_neurotransmitters,
        groups={},
    )

    with pytest.raises(ValueError, match=r"required connectome group.*missing"):
        load_runtime_connectome(runtime)
    bundle = load_runtime_connectome(runtime, required_groups=())
    assert bundle.groups == {}


@pytest.mark.parametrize(
    "indices",
    [
        np.asarray([2, 1], dtype=np.int32),
        np.asarray([1, 1], dtype=np.int32),
        np.asarray([-1], dtype=np.int32),
        np.asarray([3], dtype=np.int32),
    ],
)
def test_load_runtime_connectome_rejects_invalid_group_indices(
    tmp_path: Path,
    tiny_annotations: pd.DataFrame,
    tiny_neurotransmitters: pd.DataFrame,
    indices: np.ndarray,
) -> None:
    runtime = _build_runtime(
        tmp_path / "runtime",
        tiny_annotations,
        tiny_neurotransmitters,
        groups={"descending_neurons": {"superclass": "descending"}},
    )
    with (runtime / "groups.npz").open("wb") as stream:
        np.savez_compressed(
            stream,
            format_version=np.asarray([1], dtype=np.int16),
            names=np.asarray(["descending_neurons"]),
            offsets=np.asarray([0, len(indices)], dtype=np.int64),
            indices=indices,
        )

    with pytest.raises(ValueError, match=r"sorted and unique|outside"):
        load_runtime_connectome(runtime, verify_hashes=False)


@pytest.mark.parametrize(
    ("names", "message"),
    [
        (["", "other"], "non-empty"),
        (["duplicate", "duplicate"], "unique"),
    ],
)
def test_load_runtime_connectome_rejects_invalid_group_names(
    tmp_path: Path,
    tiny_annotations: pd.DataFrame,
    tiny_neurotransmitters: pd.DataFrame,
    names: list[str],
    message: str,
) -> None:
    runtime = _build_runtime(
        tmp_path / "runtime",
        tiny_annotations,
        tiny_neurotransmitters,
        groups={"descending_neurons": {"superclass": "descending"}},
    )
    with (runtime / "groups.npz").open("wb") as stream:
        np.savez_compressed(
            stream,
            format_version=np.asarray([1], dtype=np.int16),
            names=np.asarray(names),
            offsets=np.asarray([0, 1, 2], dtype=np.int64),
            indices=np.asarray([1, 2], dtype=np.int32),
        )

    with pytest.raises(ValueError, match=message):
        load_runtime_connectome(runtime, verify_hashes=False, required_groups=())


def test_load_runtime_connectome_rejects_serialized_dtype_changes(
    tmp_path: Path,
    tiny_annotations: pd.DataFrame,
    tiny_neurotransmitters: pd.DataFrame,
) -> None:
    runtime = _build_runtime(
        tmp_path / "runtime",
        tiny_annotations,
        tiny_neurotransmitters,
        groups={"descending_neurons": {"superclass": "descending"}},
    )
    graph_path = runtime / "graph.npz"
    with np.load(graph_path, allow_pickle=False) as archive:
        arrays = {name: np.asarray(archive[name]) for name in archive.files}
    arrays["weights"] = arrays["weights"].astype(np.float64)
    with graph_path.open("wb") as stream:
        np.savez_compressed(stream, **arrays)

    with pytest.raises(ValueError, match="weights dtype must be float32"):
        load_runtime_connectome(runtime, verify_hashes=False)

    arrays["weights"] = arrays["weights"].astype(np.float32)
    with graph_path.open("wb") as stream:
        np.savez_compressed(stream, **arrays)
    groups_path = runtime / "groups.npz"
    with np.load(groups_path, allow_pickle=False) as archive:
        group_arrays = {name: np.asarray(archive[name]) for name in archive.files}
    group_arrays["indices"] = group_arrays["indices"].astype(np.int64)
    with groups_path.open("wb") as stream:
        np.savez_compressed(stream, **group_arrays)

    with pytest.raises(ValueError, match="group indices dtype must be int32"):
        load_runtime_connectome(runtime, verify_hashes=False)
