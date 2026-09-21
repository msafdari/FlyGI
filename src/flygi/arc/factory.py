"""Assemble a closed-loop connectome policy from a config and a runtime bundle.

The same factory builds the real condition and every null condition. Only
``runtime_dir`` changes between them: the encoder seed, projection, sensory
population, readout population, decoder, dynamics parameters, internal steps and
state policy are taken from one config and are therefore identical by
construction. That is the specification's fairness constraint made mechanical
rather than aspirational.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from flygi.config import FlyGIConfig
from flygi.decoding.coordinate_head import CoordinateHead
from flygi.decoding.dn_trace import AdaptiveStandardizer, DescendingTrace
from flygi.decoding.literal import LiteralActionMap
from flygi.dynamics.rate import RateParameters, ScipyRateNetwork
from flygi.dynamics.runtime import RuntimeConnectome, load_runtime_connectome
from flygi.encoding.sparse_projection import (
    ProjectionOptions,
    SensoryProjection,
    build_sensory_projection,
)
from flygi.seed import derive_seed

from .policy import ConnectomePolicy, PolicyError, StatePolicy
from .protocol import ActionFactory


class RuntimeAssemblyError(RuntimeError):
    """Raised when a runtime bundle cannot satisfy the declared interface."""


def sensory_indices_for_superclass(runtime_dir: str | Path, superclass: str) -> NDArray[np.int64]:
    """Resolve a node-metadata superclass to sorted dense runtime indices."""

    path = Path(runtime_dir) / "node_metadata.npz"
    with np.load(path, allow_pickle=False) as archive:
        if "superclass" not in archive:
            raise RuntimeAssemblyError(f"{path} has no 'superclass' column")
        labels = archive["superclass"]
    selected = np.flatnonzero(labels == superclass).astype(np.int64)
    if selected.size == 0:
        available = sorted({str(value) for value in np.unique(labels)})
        raise RuntimeAssemblyError(
            f"sensory superclass {superclass!r} matched no nodes; available: {available}"
        )
    return selected


@dataclass(frozen=True)
class AssembledPolicy:
    """A ready policy together with everything needed to describe the run."""

    policy: ConnectomePolicy
    bundle: RuntimeConnectome
    projection: SensoryProjection
    sensory_indices: NDArray[np.int64]
    readout_indices: NDArray[np.int64]

    def describe(self) -> dict[str, Any]:
        record = dict(self.policy.describe())
        record["graph"] = {
            "nodes": self.bundle.node_count,
            "edges": self.bundle.edge_count,
            "release": self.bundle.manifest.get("release"),
            "verified_output_hashes": dict(self.bundle.verified_hashes),
            "preprocessing": dict(self.bundle.manifest.get("preprocessing", {})),
        }
        record["populations"] = {
            "sensory_size": int(self.sensory_indices.size),
            "readout_size": int(self.readout_indices.size),
        }
        return record


def build_connectome_policy(
    config: FlyGIConfig,
    actions: ActionFactory,
    *,
    runtime_dir: str | Path | None = None,
    bundle: RuntimeConnectome | None = None,
    projection: SensoryProjection | None = None,
    ablate_graph: bool = False,
    internal_steps: int | None = None,
) -> AssembledPolicy:
    """Build one closed-loop policy. Pass ``bundle`` to reuse a loaded graph."""

    if config.encoder.kind != "sparse_projection":
        raise RuntimeAssemblyError(
            f"encoder kind {config.encoder.kind!r} is declared but not implemented"
        )
    readout_group = config.decoder.readout
    directory = Path(runtime_dir) if runtime_dir is not None else Path(config.graph.output_dir)
    loaded = bundle or load_runtime_connectome(directory, required_groups=(readout_group,))

    readout_indices = np.asarray(loaded.groups[readout_group], dtype=np.int64)
    sensory = sensory_indices_for_superclass(directory, config.encoder.sensory_superclass)

    if projection is None:
        projection = build_sensory_projection(
            sensory,
            loaded.node_count,
            seed=derive_seed(config.seed, "encoder"),
            options=ProjectionOptions(
                connections_per_neuron=config.encoder.connections_per_neuron,
                input_scale=config.encoder.input_scale,
            ),
        )
    elif not np.array_equal(projection.sensory_indices, sensory):
        raise RuntimeAssemblyError(
            "a reused projection must target the same sensory population; "
            "the interface must not vary across graph conditions"
        )

    network = ScipyRateNetwork(
        loaded.matrix,
        RateParameters(
            internal_steps=(
                config.dynamics.internal_steps if internal_steps is None else internal_steps
            ),
            leak=config.dynamics.leak,
            recurrent_gain=config.dynamics.recurrent_gain,
            bias=config.dynamics.bias,
        ),
        copy_connectivity=False,
    )
    readout = DescendingTrace(readout_indices, loaded.node_count)
    try:
        policy = ConnectomePolicy(
            actions,
            network=network,
            projection=projection,
            readout=readout,
            action_map=LiteralActionMap(readout.size, action_slots=config.decoder.action_slots),
            coordinate_head=CoordinateHead(readout.size),
            standardizer=(
                AdaptiveStandardizer(
                    readout.size,
                    adaptation_rate=config.decoder.adaptation_rate,
                    clip=config.decoder.clip,
                )
                if config.decoder.readout_normalization == "adaptive"
                else None
            ),
            internal_steps=network.parameters.internal_steps,
            state_policy=StatePolicy(
                reset_on_new_environment=config.state.reset_on_new_environment,
                preserve_across_levels=config.state.preserve_across_levels,
                preserve_across_actions=config.state.preserve_across_actions,
                preserve_after_game_over_reset=config.state.preserve_after_game_over_reset,
            ),
            ablate_graph=ablate_graph,
        )
    except PolicyError as exc:
        raise RuntimeAssemblyError(str(exc)) from exc

    return AssembledPolicy(
        policy=policy,
        bundle=loaded,
        projection=projection,
        sensory_indices=sensory,
        readout_indices=readout_indices,
    )
