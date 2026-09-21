"""Compile MaleCNS source tables into a sparse, offline runtime asset."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd
from scipy import sparse

from .download import OFFICIAL_BASE_URL, OFFICIAL_FILENAMES
from .groups import GroupDefinition, resolve_groups, save_groups
from .manifest import (
    create_connectome_manifest,
    file_record,
    sha256_file,
    write_manifest,
)
from .normalize import (
    Normalization,
    UnknownTreatment,
    WeightTransform,
    apply_presynaptic_signs,
    normalize_matrix,
    transform_weights,
    transmitter_signs,
)
from .schema import (
    WEIGHTS_COLUMNS,
    WEIGHTS_CONTRACT,
    SchemaMismatchError,
    coerce_body_ids,
    dataframe_schema,
    inspect_table_schema,
    read_table,
    validate_annotations_table,
    validate_neurotransmitters_table,
    validate_observed_schema,
    validate_weights_table,
)

TableInput = str | Path | pd.DataFrame


@dataclass(frozen=True)
class BuildOptions:
    """All choices that can change the compiled runtime graph."""

    weight_transform: WeightTransform = "log1p"
    sign_mode: Literal["unsigned", "heuristic"] = "unsigned"
    normalization: Normalization = "incoming_l1"
    epsilon: float = 1e-8
    spectral_radius: float = 0.9
    allow_self_edges: bool = True
    strict_source_schema: bool = True
    # The full annotated population is retained by default. Any anatomical
    # subset must be an explicit, recorded experimental choice.
    node_filter_column: str | None = None
    node_filter_values: tuple[object, ...] | None = None
    modulator_treatment: UnknownTreatment = "zero"
    unknown_transmitter_treatment: UnknownTreatment = "zero"
    compress_output: bool = True
    overwrite: bool = False

    def __post_init__(self) -> None:
        if self.sign_mode not in {"unsigned", "heuristic"}:
            raise ValueError(f"Unknown sign mode: {self.sign_mode!r}")
        if self.epsilon <= 0 or not np.isfinite(self.epsilon):
            raise ValueError("epsilon must be finite and strictly positive")
        if self.spectral_radius < 0 or not np.isfinite(self.spectral_radius):
            raise ValueError("spectral_radius must be finite and non-negative")


@dataclass(frozen=True)
class NodeIndex:
    """A lossless mapping between uint64 body IDs and dense zero-based indices."""

    body_ids: np.ndarray

    def __post_init__(self) -> None:
        values = np.asarray(self.body_ids)
        if values.dtype != np.uint64 or values.ndim != 1:
            raise TypeError("NodeIndex.body_ids must be a 1-D uint64 array")
        if len(values) and np.any(values[1:] <= values[:-1]):
            raise ValueError("NodeIndex.body_ids must be sorted and unique")
        immutable = values.copy()
        immutable.flags.writeable = False
        object.__setattr__(self, "body_ids", immutable)

    @classmethod
    def from_body_ids(cls, body_ids: Iterable[int] | pd.Series | np.ndarray) -> NodeIndex:
        values = coerce_body_ids(body_ids, column="bodyId")
        return cls(np.unique(values))

    def __len__(self) -> int:
        return len(self.body_ids)

    def indices_for(
        self,
        body_ids: Iterable[int] | pd.Series | np.ndarray,
        *,
        missing: Literal["error", "negative_one"] = "error",
    ) -> np.ndarray:
        query = coerce_body_ids(body_ids, column="bodyId")
        positions = np.searchsorted(self.body_ids, query)
        valid = positions < len(self.body_ids)
        if valid.any():
            valid_indices = np.flatnonzero(valid)
            valid[valid_indices] = self.body_ids[positions[valid_indices]] == query[valid_indices]
        if not valid.all() and missing == "error":
            examples = [int(value) for value in query[~valid][:5]]
            raise KeyError(f"body IDs are absent from the node index: {examples}")
        if missing == "negative_one":
            result = np.full(len(query), -1, dtype=np.int64)
            result[valid] = positions[valid].astype(np.int64, copy=False)
            return result
        if missing != "error":
            raise ValueError(f"Unknown missing-ID policy: {missing!r}")
        return positions.astype(np.int64, copy=False)

    def body_ids_for(self, indices: Iterable[int] | np.ndarray) -> np.ndarray:
        dense = np.asarray(list(indices) if not isinstance(indices, np.ndarray) else indices)
        if dense.ndim != 1 or not np.issubdtype(dense.dtype, np.integer):
            raise TypeError("dense indices must be a one-dimensional integer array")
        if len(dense) and ((dense < 0).any() or (dense >= len(self)).any()):
            raise IndexError("dense node index out of range")
        return self.body_ids[dense.astype(np.int64, copy=False)].copy()


def build_sparse_counts(
    edges: pd.DataFrame,
    node_index: NodeIndex,
    *,
    allow_self_edges: bool = True,
    drop_unknown_nodes: bool = True,
) -> sparse.csr_matrix:
    """Aggregate edges into CSR with the convention ``W[post, pre]``."""

    validate_weights_table(edges, strict=False)
    pre_ids = coerce_body_ids(edges["body_pre"], column="body_pre")
    post_ids = coerce_body_ids(edges["body_post"], column="body_post")
    pre = node_index.indices_for(pre_ids, missing="negative_one")
    post = node_index.indices_for(post_ids, missing="negative_one")
    retained = (pre >= 0) & (post >= 0)
    if not retained.all() and not drop_unknown_nodes:
        examples = [
            (int(source), int(target))
            for source, target in zip(pre_ids[~retained][:5], post_ids[~retained][:5], strict=True)
        ]
        raise KeyError(f"edge endpoints are absent from the node index: {examples}")
    if not allow_self_edges:
        retained &= pre_ids != post_ids

    data = edges["weight"].to_numpy(dtype=np.int64, copy=True)[retained]
    rows = post[retained].astype(np.int32, copy=False)
    columns = pre[retained].astype(np.int32, copy=False)
    matrix = sparse.coo_matrix(
        (data, (rows, columns)),
        shape=(len(node_index), len(node_index)),
        dtype=np.int64,
    ).tocsr()
    matrix.sum_duplicates()
    matrix.eliminate_zeros()
    matrix.sort_indices()
    return matrix


def _filter_annotation_nodes(annotations: pd.DataFrame, options: BuildOptions) -> pd.DataFrame:
    if options.node_filter_column is None:
        retained = annotations.copy()
    else:
        column = options.node_filter_column
        if column not in annotations:
            raise SchemaMismatchError(f"node filter requires missing annotation column {column!r}")
        if options.node_filter_values is None:
            mask = annotations[column].notna()
            if (
                pd.api.types.is_string_dtype(annotations[column].dtype)
                or annotations[column].dtype == object
            ):
                mask &= annotations[column].astype("string").str.strip().ne("").fillna(False)
        else:
            mask = annotations[column].isin(options.node_filter_values)
        retained = annotations.loc[mask].copy()
    if retained.empty:
        raise ValueError("node filtering retained no neurons")
    return retained


def _labels_for_nodes(neurotransmitters: pd.DataFrame, node_index: NodeIndex) -> np.ndarray:
    transmitter_ids = coerce_body_ids(neurotransmitters["body"], column="body")
    order = np.argsort(transmitter_ids, kind="stable")
    sorted_ids = transmitter_ids[order]
    if len(sorted_ids) and np.any(sorted_ids[1:] == sorted_ids[:-1]):
        duplicate = int(sorted_ids[np.flatnonzero(sorted_ids[1:] == sorted_ids[:-1])[0]])
        raise SchemaMismatchError(f"neurotransmitter table contains duplicate body ID {duplicate}")
    sorted_labels = neurotransmitters["consensus_nt"].to_numpy(copy=False)[order]
    positions = np.searchsorted(sorted_ids, node_index.body_ids)
    present = positions < len(sorted_ids)
    if present.any():
        present_indices = np.flatnonzero(present)
        present[present_indices] = (
            sorted_ids[positions[present_indices]] == node_index.body_ids[present_indices]
        )
    labels = np.empty(len(node_index), dtype=object)
    labels[:] = None
    labels[present] = sorted_labels[positions[present]]
    return labels


def _iter_weight_batches(table: TableInput) -> Iterable[pd.DataFrame]:
    if isinstance(table, pd.DataFrame):
        yield table.loc[:, WEIGHTS_COLUMNS].copy()
        return
    path = Path(table)
    if path.suffix.lower() in {".feather", ".arrow", ".ipc"}:
        try:
            import pyarrow as pa
            import pyarrow.ipc as ipc
        except ImportError as exc:  # pragma: no cover - dependency error path
            raise RuntimeError("pyarrow is required to build from Feather files") from exc
        with pa.memory_map(str(path), "r") as memory:
            reader = ipc.open_file(memory)
            for batch_number in range(reader.num_record_batches):
                batch = reader.get_batch(batch_number).select(list(WEIGHTS_COLUMNS))
                yield batch.to_pandas()
        return
    yield read_table(path, columns=WEIGHTS_COLUMNS)


def _build_streaming_counts(
    weights: TableInput,
    node_index: NodeIndex,
    *,
    allow_self_edges: bool,
    annotation_index: NodeIndex | None = None,
) -> tuple[sparse.csr_matrix, dict[str, Any]]:
    rows: list[np.ndarray] = []
    columns: list[np.ndarray] = []
    values: list[np.ndarray] = []
    source_rows = 0
    source_contact_total = 0
    source_self_edges = 0
    dropped_missing_annotation_edges = 0
    dropped_node_filter_edges = 0
    dropped_self_edges = 0
    missing_annotation_ids: set[int] = set()
    for batch in _iter_weight_batches(weights):
        validate_weights_table(batch, strict=False)
        source_rows += len(batch)
        pre_ids = coerce_body_ids(batch["body_pre"], column="body_pre")
        post_ids = coerce_body_ids(batch["body_post"], column="body_post")
        batch_weights = batch["weight"].to_numpy(dtype=np.int64, copy=True)
        source_contact_total += int(batch_weights.sum(dtype=np.int64))
        self_mask = pre_ids == post_ids
        source_self_edges += int(np.count_nonzero(self_mask))

        if annotation_index is not None:
            annotated_pre = annotation_index.indices_for(pre_ids, missing="negative_one") >= 0
            annotated_post = annotation_index.indices_for(post_ids, missing="negative_one") >= 0
            has_missing_annotation = ~(annotated_pre & annotated_post)
            dropped_missing_annotation_edges += int(np.count_nonzero(has_missing_annotation))
            if has_missing_annotation.any():
                missing_annotation_ids.update(int(value) for value in pre_ids[~annotated_pre])
                missing_annotation_ids.update(int(value) for value in post_ids[~annotated_post])
        else:
            has_missing_annotation = np.zeros(len(batch), dtype=bool)

        pre = node_index.indices_for(pre_ids, missing="negative_one")
        post = node_index.indices_for(post_ids, missing="negative_one")
        retained = (pre >= 0) & (post >= 0)
        dropped_node_filter_edges += int(np.count_nonzero(~retained & ~has_missing_annotation))
        if not allow_self_edges:
            dropped_self_edges += int(np.count_nonzero(retained & self_mask))
            retained &= ~self_mask
        if retained.any():
            columns.append(pre[retained].astype(np.int32, copy=False))
            rows.append(post[retained].astype(np.int32, copy=False))
            values.append(batch_weights[retained])

    if not values:
        matrix = sparse.csr_matrix((len(node_index), len(node_index)), dtype=np.int64)
    else:
        matrix = sparse.coo_matrix(
            (
                np.concatenate(values),
                (np.concatenate(rows), np.concatenate(columns)),
            ),
            shape=(len(node_index), len(node_index)),
            dtype=np.int64,
        ).tocsr()
        matrix.sum_duplicates()
        matrix.eliminate_zeros()
        matrix.sort_indices()
    return matrix, {
        "source_directed_edge_rows": int(source_rows),
        "source_synaptic_contact_weight_sum": int(source_contact_total),
        "source_self_edges": int(source_self_edges),
        "edges_dropped_missing_annotations": int(dropped_missing_annotation_edges),
        "edges_dropped_node_filter": int(dropped_node_filter_edges),
        "edges_dropped_self": int(dropped_self_edges),
        "missing_annotation_ids": missing_annotation_ids,
    }


def _atomic_npz(destination: Path, arrays: Mapping[str, np.ndarray], *, compressed: bool) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            writer = np.savez_compressed if compressed else np.savez
            writer(stream, **arrays)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, destination)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def _unicode_array(values: pd.Series | np.ndarray) -> np.ndarray:
    series = values if isinstance(values, pd.Series) else pd.Series(values)
    strings = series.astype("string").fillna("").to_numpy(dtype=str)
    width = max((len(value) for value in strings), default=1)
    return np.asarray(strings, dtype=f"<U{max(1, width)}")


def _save_metadata(
    destination: Path,
    annotations: pd.DataFrame,
    node_index: NodeIndex,
    transmitter_labels: np.ndarray,
    *,
    compressed: bool,
) -> None:
    annotation_ids = coerce_body_ids(annotations["bodyId"], column="bodyId")
    order = np.argsort(annotation_ids, kind="stable")
    sorted_ids = annotation_ids[order]
    if not np.array_equal(sorted_ids, node_index.body_ids):
        raise ValueError("retained annotations do not exactly match the node index")
    sorted_annotations = annotations.iloc[order]
    arrays: dict[str, np.ndarray] = {
        "format_version": np.asarray([1], dtype=np.int16),
        "body_ids": node_index.body_ids,
        "dense_indices": np.arange(len(node_index), dtype=np.int32),
        "consensus_nt": _unicode_array(transmitter_labels),
    }
    for column in (
        "type",
        "instance",
        "superclass",
        "class",
        "subclass",
        "somaSide",
        "rootSide",
    ):
        if column in sorted_annotations:
            arrays[column] = _unicode_array(sorted_annotations[column])
    _atomic_npz(destination, arrays, compressed=compressed)


def _source_record(
    logical_name: str,
    source: TableInput,
    source_urls: Mapping[str, str] | None,
    source_download_timestamps: Mapping[str, str] | None,
    source_expected_hashes: Mapping[str, str | None] | None,
) -> dict[str, object]:
    if isinstance(source, pd.DataFrame):
        return {
            "name": logical_name,
            "path": None,
            "url": None if source_urls is None else source_urls.get(logical_name),
            "bytes": None,
            "sha256": None,
            "expected_sha256": None,
            "hash_verified": False,
            "downloaded_at": None,
            "source_kind": "in_memory_fixture",
        }
    path = Path(source).resolve()
    url = source_urls.get(logical_name) if source_urls is not None else None
    if url is None and path.name in OFFICIAL_FILENAMES.values():
        url = f"{OFFICIAL_BASE_URL}/{path.name}"
    expected_sha256 = (
        source_expected_hashes.get(logical_name) if source_expected_hashes is not None else None
    )
    downloaded_at = (
        source_download_timestamps.get(logical_name)
        if source_download_timestamps is not None
        else None
    )
    timestamp_source = "download_manifest"
    if downloaded_at is None:
        from datetime import UTC, datetime

        downloaded_at = (
            datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat().replace("+00:00", "Z")
        )
        timestamp_source = "file_mtime"
    record = file_record(
        path,
        name=logical_name,
        url=url,
        expected_sha256=expected_sha256,
        downloaded_at=downloaded_at,
    )
    record["source_kind"] = "file"
    record["timestamp_source"] = timestamp_source
    return record


def _output_record(path: Path) -> dict[str, object]:
    return {
        "name": path.name,
        "path": path.name,
        "bytes": int(path.stat().st_size),
        "sha256": sha256_file(path),
    }


def build_connectome(
    weights: TableInput,
    annotations: TableInput,
    neurotransmitters: TableInput,
    output_dir: str | Path,
    *,
    release: str = "male-cns:v1.0",
    options: BuildOptions | None = None,
    source_urls: Mapping[str, str] | None = None,
    group_definitions: (
        Iterable[GroupDefinition] | Mapping[str, Mapping[str, object]] | None
    ) = None,
    source_download_timestamps: Mapping[str, str] | None = None,
    source_expected_hashes: Mapping[str, str | None] | None = None,
) -> dict[str, object]:
    """Build sparse runtime assets and return the written provenance manifest."""

    settings = options or BuildOptions()
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    graph_path = destination / "graph.npz"
    metadata_path = destination / "node_metadata.npz"
    groups_path = destination / "groups.npz"
    manifest_path = destination / "manifest.json"
    targets = (graph_path, metadata_path, groups_path, manifest_path)
    existing = [path for path in targets if path.exists()]
    if existing and not settings.overwrite:
        raise FileExistsError(
            "refusing to overwrite existing connectome assets: "
            + ", ".join(str(path) for path in existing)
        )

    # Hash and (when configured) verify every source before performing the
    # expensive build or writing any runtime asset.
    source_records = [
        _source_record(
            "weights",
            weights,
            source_urls,
            source_download_timestamps,
            source_expected_hashes,
        ),
        _source_record(
            "annotations",
            annotations,
            source_urls,
            source_download_timestamps,
            source_expected_hashes,
        ),
        _source_record(
            "neurotransmitters",
            neurotransmitters,
            source_urls,
            source_download_timestamps,
            source_expected_hashes,
        ),
    ]

    annotations_frame = read_table(annotations)
    neurotransmitters_frame = read_table(neurotransmitters)
    validate_annotations_table(annotations_frame, strict=settings.strict_source_schema)
    validate_neurotransmitters_table(neurotransmitters_frame, strict=settings.strict_source_schema)

    annotations_ids = coerce_body_ids(annotations_frame["bodyId"], column="bodyId")
    if len(np.unique(annotations_ids)) != len(annotations_ids):
        raise SchemaMismatchError("annotations contain duplicate bodyId values")
    retained_annotations = _filter_annotation_nodes(annotations_frame, settings)
    node_index = NodeIndex.from_body_ids(retained_annotations["bodyId"])
    annotation_index = NodeIndex.from_body_ids(annotations_ids)

    weight_schema = (
        dataframe_schema(weights)
        if isinstance(weights, pd.DataFrame)
        else inspect_table_schema(weights)
    )
    validate_observed_schema(
        weight_schema["columns"],
        weight_schema["dtypes"],
        WEIGHTS_CONTRACT,
        strict=settings.strict_source_schema,
    )
    raw_matrix, source_stats = _build_streaming_counts(
        weights,
        node_index,
        allow_self_edges=settings.allow_self_edges,
        annotation_index=annotation_index,
    )
    weight_schema["rows"] = int(source_stats["source_directed_edge_rows"])

    contact_total = int(raw_matrix.data.sum(dtype=np.int64))
    aggregated_edges = int(raw_matrix.nnz)
    self_edges = int(np.count_nonzero(raw_matrix.diagonal()))
    incoming = np.diff(raw_matrix.indptr) != 0
    outgoing = np.bincount(raw_matrix.indices, minlength=len(node_index)) != 0
    disconnected = int(np.count_nonzero(~incoming & ~outgoing))

    transmitter_labels = _labels_for_nodes(neurotransmitters_frame, node_index)
    signs, transmitter_stats = transmitter_signs(
        transmitter_labels,
        modulator_treatment=settings.modulator_treatment,
        unknown_treatment=settings.unknown_transmitter_treatment,
    )
    weighted = raw_matrix.copy()
    weighted.data = transform_weights(weighted.data, settings.weight_transform)
    if settings.sign_mode == "heuristic":
        weighted = apply_presynaptic_signs(weighted, signs)
    else:
        weighted = weighted.astype(np.float32, copy=False)
    normalized = normalize_matrix(
        weighted,
        settings.normalization,
        epsilon=settings.epsilon,
        spectral_radius=settings.spectral_radius,
    )
    normalized.sort_indices()

    graph_arrays = {
        "format_version": np.asarray([1], dtype=np.int16),
        "indptr": normalized.indptr.astype(np.int64, copy=False),
        "indices": normalized.indices.astype(np.int32, copy=False),
        "weights": normalized.data.astype(np.float32, copy=False),
        "node_ids": node_index.body_ids,
        # Both directions are serialized explicitly.  The first array is sorted,
        # so callers can also use binary search without loading a Python dict.
        "body_to_index_ids": node_index.body_ids,
        "body_to_index_values": np.arange(len(node_index), dtype=np.int32),
    }
    _atomic_npz(graph_path, graph_arrays, compressed=settings.compress_output)
    _save_metadata(
        metadata_path,
        retained_annotations,
        node_index,
        transmitter_labels,
        compressed=settings.compress_output,
    )
    groups = resolve_groups(retained_annotations, node_index.body_ids, group_definitions)
    temporary_groups = groups_path.with_name(f".{groups_path.name}.partial")
    save_groups(temporary_groups, groups)
    os.replace(temporary_groups, groups_path)

    schemas = {
        "weights": weight_schema,
        "annotations": dataframe_schema(annotations_frame),
        "neurotransmitters": dataframe_schema(neurotransmitters_frame),
    }
    counts = {
        "annotated_neurons": len(annotations_frame),
        "retained_neurons": len(node_index),
        "aggregated_directed_edges": aggregated_edges,
        "runtime_nonzero_edges": int(normalized.nnz),
        "edges_zeroed_by_sign_or_normalization": aggregated_edges - int(normalized.nnz),
        "synaptic_contact_weight_sum": int(contact_total),
        "self_edges": self_edges,
        "disconnected_nodes": disconnected,
        "unknown_transmitters": int(transmitter_stats["unknown"]),
        "missing_annotations": len(source_stats["missing_annotation_ids"]),
        "modulatory_transmitters": int(transmitter_stats["modulatory"]),
        "source_directed_edge_rows": int(source_stats["source_directed_edge_rows"]),
        "source_synaptic_contact_weight_sum": int(
            source_stats["source_synaptic_contact_weight_sum"]
        ),
        "source_self_edges": int(source_stats["source_self_edges"]),
        "edges_dropped_missing_annotations": int(source_stats["edges_dropped_missing_annotations"]),
        "edges_dropped_node_filter": int(source_stats["edges_dropped_node_filter"]),
        "edges_dropped_self": int(source_stats["edges_dropped_self"]),
    }
    preprocessing = asdict(settings)
    preprocessing.update(
        {
            "matrix_convention": "W[post_index, pre_index]",
            "node_order": "ascending uint64 bodyId",
            "node_filter_semantics": (
                "all annotated neurons"
                if settings.node_filter_column is None
                else (
                    "non-null/non-empty"
                    if settings.node_filter_values is None
                    else "explicit allowed values"
                )
            ),
            "transmitter_counts": transmitter_stats,
            "group_definitions": {name: len(indices) for name, indices in groups.items()},
        }
    )
    output_records = [
        _output_record(graph_path),
        _output_record(metadata_path),
        _output_record(groups_path),
    ]
    manifest = create_connectome_manifest(
        release=release,
        sources=source_records,
        dataframe_schemas=schemas,
        counts=counts,
        preprocessing=preprocessing,
        outputs=output_records,
    )
    write_manifest(manifest_path, manifest)
    return manifest


def load_runtime_graph(
    path: str | Path,
) -> tuple[sparse.csr_matrix, NodeIndex]:
    """Load a compiled graph without enabling numpy object deserialization."""

    with np.load(Path(path), allow_pickle=False) as archive:
        version = np.asarray(archive["format_version"])
        raw_indptr = np.asarray(archive["indptr"])
        indices = np.asarray(archive["indices"])
        weights = np.asarray(archive["weights"])
        node_ids = np.asarray(archive["node_ids"])
        inverse_ids = np.asarray(archive["body_to_index_ids"])
        inverse_values = np.asarray(archive["body_to_index_values"])
    if version.dtype != np.int16:
        raise ValueError("graph format_version dtype must be int16")
    if version.tolist() != [1]:
        raise ValueError(f"Unsupported graph format version: {version.tolist()}")
    if raw_indptr.dtype not in (np.dtype(np.int32), np.dtype(np.int64)):
        raise ValueError("graph indptr dtype must be int32 or int64")
    if indices.dtype != np.int32:
        raise ValueError("graph indices dtype must be int32")
    if weights.dtype != np.float32:
        raise ValueError("graph weights dtype must be float32")
    if node_ids.dtype != np.uint64 or inverse_ids.dtype != np.uint64:
        raise ValueError("graph node ID arrays must have uint64 dtype")
    if inverse_values.dtype != np.int32:
        raise ValueError("graph body-to-index values must have int32 dtype")
    indptr = raw_indptr.astype(np.int64, copy=False)
    node_index = NodeIndex(node_ids)
    if not np.array_equal(inverse_ids, node_ids) or not np.array_equal(
        inverse_values, np.arange(len(node_ids), dtype=np.int32)
    ):
        raise ValueError("serialized body-to-index mapping is inconsistent")
    if indptr.shape != (len(node_ids) + 1,) or indptr[0] != 0:
        raise ValueError("invalid CSR indptr")
    if indptr[-1] != len(indices) or len(indices) != len(weights):
        raise ValueError("inconsistent CSR array lengths")
    if np.any(indptr[1:] < indptr[:-1]):
        raise ValueError("CSR indptr must be non-decreasing")
    if len(indices) and ((indices < 0).any() or (indices >= len(node_ids)).any()):
        raise ValueError("CSR column index out of range")
    matrix = sparse.csr_matrix((weights, indices, indptr), shape=(len(node_ids), len(node_ids)))
    return matrix, node_index
