"""The closed-loop connectome policy.

One ARC turn runs the declared causal path exactly once:

``frame -> features -> sensory drive -> graph state -> descending trace ->
action logits -> legal mask -> action``

The graph is not decoration. Every active, non-reset decision advances the
persistent 166,700-neuron state and reads descending activity out of it, and a
test asserts that ablating the graph's contribution changes the action
sequence.
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from flygi.decoding.coordinate_head import CoordinateHead
from flygi.decoding.dn_trace import AdaptiveStandardizer, DescendingTrace
from flygi.decoding.literal import LiteralActionMap
from flygi.dynamics.rate import ScipyRateNetwork
from flygi.encoding.features import encode_observation
from flygi.encoding.sparse_projection import SensoryProjection

from .protocol import ActionFactory, ActionLike, FrameLike
from .state import ArcTurnState, action_id

ACTION6 = 6


class PolicyError(RuntimeError):
    """Raised when the closed loop cannot produce a legal action."""


@dataclass(frozen=True)
class StatePolicy:
    """Declared lifetime of the persistent neural state.

    The defaults implement the specification's recommendation: state survives
    ordinary actions, level transitions, and the reset that follows a game
    over, and is cleared only when a new environment begins. A recurrent
    connectome can only matter if its state outlives a single decision.
    """

    reset_on_new_environment: bool = True
    preserve_across_levels: bool = True
    preserve_across_actions: bool = True
    preserve_after_game_over_reset: bool = True


@dataclass
class TurnRecord:
    """Per-turn diagnostics, recorded for zero-score behavioral analysis."""

    step: int
    action_id: int
    changed_cells: int
    readout_mean_abs: float
    readout_std: float
    readout_silent: bool
    state_mean_abs: float
    argmax_unique: bool
    forced_reset: bool
    graph_advanced: bool
    logits: list[float] = field(default_factory=list)


class ConnectomePolicy:
    """Drive ARC actions from persistent MaleCNS dynamics."""

    def __init__(
        self,
        actions: ActionFactory,
        *,
        network: ScipyRateNetwork,
        projection: SensoryProjection,
        readout: DescendingTrace,
        action_map: LiteralActionMap,
        coordinate_head: CoordinateHead,
        internal_steps: int,
        standardizer: AdaptiveStandardizer | None = None,
        state_policy: StatePolicy | None = None,
        ablate_graph: bool = False,
    ) -> None:
        if bool(ablate_graph) and float(network.parameters.recurrent_gain) != 0.0:
            raise PolicyError(
                "an ablated policy must have zero recurrent gain; otherwise the "
                "graph is still contributing"
            )
        if projection.sensory_indices.max() >= network.node_count:
            raise PolicyError("sensory population does not fit the graph")
        if readout.size != action_map.readout_size:
            raise PolicyError("readout population and action map disagree in size")
        if readout.size != coordinate_head.readout_size:
            raise PolicyError("readout population and coordinate head disagree in size")
        if internal_steps <= 0:
            raise PolicyError("internal_steps must be positive")

        self._actions = actions
        self._network = network
        self._projection = projection
        self._readout = readout
        self._action_map = action_map
        self._coordinates = coordinate_head
        self._internal_steps = int(internal_steps)
        self._state_policy = state_policy or StatePolicy()
        self._ablate_graph = bool(ablate_graph)
        self._standardizer = standardizer
        if standardizer is not None and standardizer.size != readout.size:
            raise PolicyError("standardizer and readout population disagree in size")

        self._state = network.initial_state()
        self._previous_grid: NDArray[np.int8] | None = None
        self._previous_action_id: int | None = None
        self._step = 0
        self.records: list[TurnRecord] = []

    @property
    def state(self) -> NDArray[np.float32]:
        """A read-only view of the persistent neural state."""

        view = self._state.view()
        view.flags.writeable = False
        return view

    @property
    def internal_steps(self) -> int:
        return self._internal_steps

    def describe(self) -> dict[str, Any]:
        """Full interface provenance, written into every result bundle."""

        return {
            "policy": "connectome-literal",
            "graph_ablated": self._ablate_graph,
            "internal_steps": self._internal_steps,
            "node_count": self._network.node_count,
            "backend": self._network.backend_name,
            "dynamics": {
                "leak": float(self._network.parameters.leak),
                "recurrent_gain": float(self._network.parameters.recurrent_gain),
                "bias": float(self._network.parameters.bias),
            },
            "encoder": self._projection.describe(),
            "readout": {
                "kind": "descending_neurons",
                "size": self._readout.size,
                "normalization": (
                    {"kind": "population_zscore", "trainable": False}
                    if self._standardizer is None
                    else self._standardizer.describe()
                ),
            },
            "action_map": self._action_map.describe(),
            "coordinate_head": self._coordinates.describe(),
            "state_policy": {
                "reset_on_new_environment": self._state_policy.reset_on_new_environment,
                "preserve_across_levels": self._state_policy.preserve_across_levels,
                "preserve_across_actions": self._state_policy.preserve_across_actions,
                "preserve_after_game_over_reset": (
                    self._state_policy.preserve_after_game_over_reset
                ),
            },
            "trainable_parameters": 0,
        }

    def reset_state(self) -> None:
        """Clear the persistent state, as at the start of a new environment."""

        self._state = self._network.initial_state()
        self._previous_grid = None
        self._previous_action_id = None
        if self._standardizer is not None:
            self._standardizer.reset()

    def is_done(self, latest_frame: FrameLike) -> bool:
        """Stop after a win; a game-over frame is reset and retried."""

        return ArcTurnState.from_frame(latest_frame).is_win

    def _advance(self, frame: FrameLike, turn: ArcTurnState) -> tuple[NDArray[np.float32], int]:
        """Encode the frame, advance the graph, and return the readout trace."""

        features = encode_observation(
            frame,
            previous_grid=self._previous_grid,
            previous_action_id=self._previous_action_id,
            available_action_ids=turn.available_action_ids,
        )
        drive = self._projection.drive(features.vector)
        # The ablation is a property of the network and the projection, not a
        # branch here: a bypass condition runs the identical update with zero
        # recurrent gain and a readout-targeted projection of matched budget.
        self._state = self._network.advance(self._state, drive, internal_steps=self._internal_steps)
        self._previous_grid = features.grid
        return self._state, features.changed_cells

    def choose_action(self, latest_frame: FrameLike) -> ActionLike:
        """Run one full closed-loop decision."""

        turn = ArcTurnState.from_frame(latest_frame)
        state, changed_cells = self._advance(latest_frame, turn)
        population, diagnostics = self._readout.standardized(state)
        trace = (
            population
            if self._standardizer is None
            else self._standardizer.transform(self._readout.raw(state))
        )

        reset = self._actions.RESET
        reset_id = action_id(reset)
        if turn.needs_reset:
            # The protocol forces RESET here. The graph still saw the frame, so
            # the failed attempt leaves a trace in the persistent state.
            chosen_id = reset_id
            action = reset
            unique = True
            logits: list[float] = []
        else:
            if not turn.available_action_ids:
                raise PolicyError(
                    f"active ARC frame in state {turn.game_state!r} declares no legal actions"
                )
            decision = self._action_map.decide(trace, turn.available_action_ids)
            chosen_id = decision.action_id
            unique = decision.argmax_was_unique
            logits = [float(value) for value in decision.logits]
            action = self._resolve_action(chosen_id)
            if chosen_id == ACTION6:
                self._attach_coordinates(action, trace)

        self._annotate(action, chosen_id, turn)
        self.records.append(
            TurnRecord(
                step=self._step,
                action_id=chosen_id,
                changed_cells=changed_cells,
                readout_mean_abs=diagnostics.mean_abs,
                readout_std=diagnostics.standard_deviation,
                readout_silent=diagnostics.silent,
                state_mean_abs=float(np.abs(state).mean()),
                argmax_unique=unique,
                forced_reset=turn.needs_reset,
                graph_advanced=not self._ablate_graph,
                logits=logits,
            )
        )
        self._previous_action_id = chosen_id
        self._step += 1
        return action

    def _resolve_action(self, identifier: int) -> ActionLike:
        resolver = getattr(self._actions, "from_id", None)
        if callable(resolver):
            try:
                return resolver(identifier)
            except ValueError as exc:
                raise PolicyError(f"unknown ARC action id {identifier}") from exc
        for candidate in self._actions:  # type: ignore[union-attr]
            if action_id(candidate) == identifier:
                return candidate
        raise PolicyError(f"unknown ARC action id {identifier}")

    def _attach_coordinates(self, action: ActionLike, trace: NDArray[np.float32]) -> None:
        x, y = self._coordinates.coordinates(trace)
        setter = getattr(action, "set_data", None)
        if not callable(setter):
            raise PolicyError("complex ARC actions must implement set_data(data)")
        setter({"x": x, "y": y})

    def _annotate(self, action: ActionLike, chosen_id: int, turn: ArcTurnState) -> None:
        reasoning: Any = {
            "policy": "flygi-connectome-literal",
            "action_id": chosen_id,
            "legal_action_ids": list(turn.available_action_ids),
            "internal_steps": self._internal_steps,
        }
        with suppress(AttributeError, TypeError):
            action.reasoning = reasoning
