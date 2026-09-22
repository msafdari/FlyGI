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
from flygi.decoding.dn_trace import AdaptiveStandardizer, DescendingTrace, ReadoutError
from flygi.decoding.literal import LiteralActionMap
from flygi.decoding.loop_escape import (
    LoopEscapeError,
    LoopEscapeParameters,
)
from flygi.decoding.trained_head import TrainedActionHead, TrainedHeadSpec
from flygi.dynamics.rate import RateParameters, ScipyRateNetwork
from flygi.dynamics.runtime import RuntimeConnectome, load_runtime_connectome
from flygi.encoding.sparse_projection import (
    ProjectionOptions,
    SensoryProjection,
    build_sensory_projection,
)
from flygi.plasticity import (
    MushroomBody,
    MushroomBodyParameters,
    resolve_mushroom_body,
    rewire_mushroom_body,
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


MUSHROOM_BODY_KENYON_CLASS = "Kenyon_Cell"
MUSHROOM_BODY_MBON_CLASS = "MBON"
DOPAMINERGIC_TYPE_PREFIXES = ("PAM", "PPL", "PPM")


def mushroom_body_populations(
    runtime_dir: str | Path,
) -> tuple[NDArray[np.int64], NDArray[np.int64], NDArray[np.int64]]:
    """Resolve Kenyon cells, MBONs and dopaminergic neurons from annotations.

    Populations come from the dataset's own ``class`` and ``type`` labels, not
    from a hand-listed body-ID set, so the circuit is whatever MaleCNS says it
    is.
    """

    path = Path(runtime_dir) / "node_metadata.npz"
    with np.load(path, allow_pickle=False) as archive:
        for column in ("class", "type"):
            if column not in archive:
                raise RuntimeAssemblyError(f"{path} has no {column!r} column")
        classes = archive["class"]
        types = archive["type"]

    kenyon = np.flatnonzero(classes == MUSHROOM_BODY_KENYON_CLASS).astype(np.int64)
    mbons = np.flatnonzero(classes == MUSHROOM_BODY_MBON_CLASS).astype(np.int64)
    dopaminergic = np.flatnonzero(
        np.array(
            [str(value).startswith(DOPAMINERGIC_TYPE_PREFIXES) for value in types],
            dtype=bool,
        )
    ).astype(np.int64)

    for name, found in (
        ("Kenyon cells", kenyon),
        ("MBONs", mbons),
        ("dopaminergic neurons", dopaminergic),
    ):
        if found.size == 0:
            raise RuntimeAssemblyError(
                f"no {name} found in {path}; this runtime cannot support mushroom-body plasticity"
            )
    return kenyon, mbons, dopaminergic


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
    trained_head_parameters: NDArray[np.floating] | None = None,
    trained_head_feature_dim: int = 48,
    ablate_trace: bool = False,
    decision_seed: int | None = None,
    action_temperature: float | None = None,
    coordinate_temperature: float | None = None,
    loop_escape_enabled: bool | None = None,
    loop_escape_exploration_bonus: float | None = None,
    loop_escape_unchanged_failure_penalty: float | None = None,
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

    # The preregistered no-recurrent-graph control keeps the interface budget
    # and removes only the graph. Its projection targets the readout population
    # directly, with connections_per_neuron rescaled so the total number of
    # interface nonzeros matches the real condition's, and the recurrent gain
    # is zero. Without the retargeting the readout would never be driven at all
    # and the control would measure nothing.
    target = readout_indices if ablate_graph else sensory
    if ablate_graph:
        matched_total = int(sensory.size) * int(config.encoder.connections_per_neuron)
        per_neuron = max(1, round(matched_total / int(readout_indices.size)))
    else:
        per_neuron = int(config.encoder.connections_per_neuron)

    if projection is None:
        projection = build_sensory_projection(
            target,
            loaded.node_count,
            seed=derive_seed(config.seed, "encoder"),
            options=ProjectionOptions(
                connections_per_neuron=per_neuron,
                input_scale=config.encoder.input_scale,
            ),
        )
    elif not np.array_equal(projection.sensory_indices, target):
        raise RuntimeAssemblyError(
            "a reused projection must target the same population; "
            "the interface must not vary across graph conditions"
        )

    plastic = config.plasticity.enabled
    kenyon = mbons = dopaminergic = None
    if plastic:
        # Plasticity mutates weights, so this policy gets a private writable
        # copy. The shared loaded bundle stays frozen and hash-verified.
        connectivity = loaded.matrix.copy()
        connectivity.data = np.array(connectivity.data, dtype=np.float32, copy=True)
        connectivity.indices = np.array(connectivity.indices, copy=True)
        connectivity.indptr = np.array(connectivity.indptr, copy=True)
        kenyon, mbons, dopaminergic = mushroom_body_populations(directory)
        if config.plasticity.rewire_mushroom_body_seed is not None:
            # The falsification control. This is a topology edit, so it must
            # happen here, before the network freezes `indices` for the run.
            # Same degrees, same per-MBON weight multiset, different partners,
            # nothing else in the graph touched.
            try:
                rewire_mushroom_body(
                    connectivity,
                    resolve_mushroom_body(
                        connectivity,
                        kenyon_cells=kenyon,
                        mbons=mbons,
                        dopaminergic=dopaminergic,
                    ),
                    seed=config.plasticity.rewire_mushroom_body_seed,
                )
            except Exception as exc:
                raise RuntimeAssemblyError(
                    f"mushroom-body rewire could not be applied: {exc}"
                ) from exc
    else:
        connectivity = loaded.matrix
    network = ScipyRateNetwork(
        connectivity,
        RateParameters(
            internal_steps=(
                config.dynamics.internal_steps if internal_steps is None else internal_steps
            ),
            leak=config.dynamics.leak,
            recurrent_gain=0.0 if ablate_graph else config.dynamics.recurrent_gain,
            bias=config.dynamics.bias,
        ),
        copy_connectivity=False,
        allow_plasticity=plastic,
    )

    mushroom_body = None
    if plastic:
        try:
            anatomy = resolve_mushroom_body(
                network.connectivity,
                kenyon_cells=kenyon,
                mbons=mbons,
                dopaminergic=dopaminergic,
            )
            mushroom_body = MushroomBody(
                network.connectivity,
                anatomy,
                MushroomBodyParameters(
                    learning_rate=config.plasticity.learning_rate,
                    decay=config.plasticity.decay,
                    weight_ceiling_scale=config.plasticity.weight_ceiling_scale,
                    reward_scale=config.plasticity.reward_scale,
                ),
            )
        except Exception as exc:
            raise RuntimeAssemblyError(
                f"mushroom-body plasticity could not be assembled: {exc}"
            ) from exc
    readout = DescendingTrace(readout_indices, loaded.node_count)
    resolved_decision_seed = (
        derive_seed(config.seed, "decision") if decision_seed is None else decision_seed
    )
    try:
        policy = ConnectomePolicy(
            actions,
            network=network,
            projection=projection,
            readout=readout,
            action_map=LiteralActionMap(
                readout.size,
                action_slots=config.decoder.action_slots,
                temperature=(
                    config.decoder.action_temperature
                    if action_temperature is None
                    else action_temperature
                ),
            ),
            coordinate_head=CoordinateHead(
                readout.size,
                temperature=(
                    config.decoder.coordinate_temperature
                    if coordinate_temperature is None
                    else coordinate_temperature
                ),
            ),
            ablate_trace=ablate_trace,
            mushroom_body=mushroom_body,
            reward_source=config.plasticity.reward_source,
            level_reward=config.plasticity.level_reward,
            trained_head=(
                None
                if trained_head_parameters is None
                else TrainedActionHead(
                    TrainedHeadSpec(
                        readout_size=readout.size,
                        feature_dim=trained_head_feature_dim,
                    ),
                    trained_head_parameters,
                )
            ),
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
            decision_seed=resolved_decision_seed,
            loop_escape=LoopEscapeParameters(
                enabled=(
                    config.decoder.loop_escape_enabled
                    if loop_escape_enabled is None
                    else loop_escape_enabled
                ),
                exploration_bonus=(
                    config.decoder.loop_escape_exploration_bonus
                    if loop_escape_exploration_bonus is None
                    else loop_escape_exploration_bonus
                ),
                unchanged_failure_penalty=(
                    config.decoder.loop_escape_unchanged_failure_penalty
                    if loop_escape_unchanged_failure_penalty is None
                    else loop_escape_unchanged_failure_penalty
                ),
                state_hash=config.decoder.loop_escape_state_hash,
                coordinate_memory=config.decoder.loop_escape_coordinate_memory,
            ),
            state_policy=StatePolicy(
                reset_on_new_environment=config.state.reset_on_new_environment,
                preserve_across_levels=config.state.preserve_across_levels,
                preserve_across_actions=config.state.preserve_across_actions,
                preserve_after_game_over_reset=config.state.preserve_after_game_over_reset,
            ),
            ablate_graph=ablate_graph,
        )
    except (LoopEscapeError, PolicyError, ReadoutError) as exc:
        raise RuntimeAssemblyError(str(exc)) from exc

    return AssembledPolicy(
        policy=policy,
        bundle=loaded,
        projection=projection,
        sensory_indices=sensory,
        readout_indices=readout_indices,
    )
