"""Generic online state-graph policy for ARC-AGI-3.

The policy intentionally consumes only the public observation contract: the
terminal rendered frame, game state, completed-level count, and legal-action
mask.  It contains no game identifiers, fixed palette meanings, or
source-derived rules.

Learning is one turn late.  Selecting an action creates a pending transition;
the next observation reconciles that transition exactly once, even when the
adapter calls :meth:`is_done` and :meth:`choose_action` on the same frame.
"""

from __future__ import annotations

import hashlib
import math
from collections import Counter
from contextlib import suppress
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from flygi.arc.protocol import ActionFactory, ActionLike, FrameLike
from flygi.arc.state import ArcTurnState, action_id
from flygi.config import ControllerConfig

from .scene import (
    ClickCandidate,
    SceneConfig,
    SceneObservation,
    SceneTracker,
    VolatileMaskConfig,
)
from .state_graph import ActionCandidate, EffectModel, ReplayStep, StateGraph

_STATE_PREFIX = b"flygi.controller.state.v1\x00"

# ASSUMPTION (measured priors, 2026-09-24, sg-mbdr-learn rows): per-row medians
# of dense events, used only to size per-event eta. The per-side caps bound any
# deviation from these priors; it cannot compound.
_DENSE_PRIOR_NOVEL = 513.0
_DENSE_PRIOR_NOOP = 14.0
_TIE_PREFIX = b"flygi.controller.tie.v1\x00"
_UINT64_MAX = (1 << 64) - 1
_RESET_ACTION_ID = 0
_CLICK_ACTION_ID = 6


class StateGraphPolicyError(RuntimeError):
    """Raised when the controller cannot produce a protocol-valid decision."""


@dataclass(slots=True)
class ControllerTurnRecord:
    """Mutable audit record, completed when the following frame arrives."""

    step: int
    action_id: int
    source_state: str
    source_key: str | None
    mode: str
    forced_reset: bool
    coordinate_x: int | None = None
    coordinate_y: int | None = None
    clicked_color: int | None = None
    click_tier: int | None = None
    expected_destination: str | None = None
    outcome: str | None = None
    destination_key: str | None = None
    changed_cells: int | None = None
    changed: bool | None = None
    novel: bool | None = None
    fatal: bool | None = None
    advanced: bool | None = None
    reconciled: bool = False


@dataclass(slots=True)
class _PendingDecision:
    candidate: ActionCandidate
    source_key: bytes
    source_grid: NDArray[np.int8]
    source_state: str
    source_levels: int
    source_legal_ids: tuple[int, ...]
    clicked_color: int | None
    expected_destination: bytes | None
    record: ControllerTurnRecord


@dataclass(slots=True)
class _PendingReset:
    record: ControllerTurnRecord


@dataclass(slots=True)
class _ObservedFrame:
    turn: ArcTurnState
    levels_completed: int
    scene: SceneObservation | None
    state_key: bytes | None
    candidate_metadata: dict[ActionCandidate, ClickCandidate | None]


class StateGraphPolicy:
    """Explore observable ARC states, learn effects, and replay safe paths."""

    def __init__(
        self,
        actions: ActionFactory,
        controller_config: ControllerConfig,
        decision_seed: int,
        fly: object | None = None,
        click_head: object | None = None,
    ) -> None:
        if not controller_config.enabled:
            raise StateGraphPolicyError("state-graph policy requires controller.enabled=true")
        if controller_config.kind != "state_graph":
            raise StateGraphPolicyError(f"unsupported controller kind: {controller_config.kind!r}")
        if isinstance(decision_seed, bool) or not isinstance(decision_seed, int):
            raise TypeError("decision_seed must be an integer")
        if not 0 <= decision_seed <= _UINT64_MAX:
            raise ValueError("decision_seed must lie in the unsigned 64-bit range")

        self._actions = actions
        self._config = controller_config
        self._decision_seed = decision_seed
        # The connectome occupies the tie position only. Everything ranked
        # before it -- retries, attempt counts, learned effect estimates --
        # still decides first, so the fly can never override what the
        # controller has actually learned.
        self._fly = fly
        # H-CONSEQUENCE-COUPLING: unlike the fly tiebreaker, the click head
        # sits INSIDE the primary ranking term, so it can reorder candidates
        # the controller does not consider tied. Injected prebuilt, like fly.
        self._click_head = click_head
        self._head_ranked = 0
        self._head_decisive = 0
        self._last_action_id: int | None = None
        self._dense_spent_reward = 0.0
        self._dense_spent_punish = 0.0
        self._pending_click_xy: tuple[int, int] | None = None
        self._fly_ranked = 0
        self._fly_decisive = 0
        self._scene_tracker = SceneTracker(
            SceneConfig(
                volatile_mask=VolatileMaskConfig(
                    border_width=controller_config.ui_border_width,
                    comparisons_to_freeze=controller_config.mask_freeze_after,
                    minimum_changes=controller_config.volatile_min_changes,
                    minimum_change_rate=controller_config.volatile_threshold,
                ),
                minimum_component_area=controller_config.component_min_area,
                max_click_tier=controller_config.max_candidate_tier,
            )
        )
        self._graph = StateGraph()
        self._effects = EffectModel(
            advancement_bonus=controller_config.advancement_bonus,
            death_penalty=controller_config.death_penalty,
        )
        self._effects.start_level()

        self.records: list[ControllerTurnRecord] = []
        self._pending: _PendingDecision | None = None
        self._pending_reset: _PendingReset | None = None
        self._replay_queue: list[ReplayStep] = []
        self._replay_cooldown = 0
        self._level_epoch = 0
        self._last_levels: int | None = None
        self._decision_index = 0
        self._outcomes: Counter[str] = Counter()
        self._replay_drifts = 0
        self._local_resets = 0

        # The official harness calls is_done(frame), then choose_action(frame).
        # Object-identity caching makes that pair one observation while still
        # allowing a new, visually identical response to resolve a no-op.
        self._cached_frame: object | None = None
        self._cached_observation: _ObservedFrame | None = None
        self._choice_frame: object | None = None
        self._choice_action: ActionLike | None = None

    @property
    def decision_seed(self) -> int:
        return self._decision_seed

    def is_done(self, latest_frame: FrameLike) -> bool:
        """Reconcile the latest response before reporting terminal success."""

        observed = self._consume_frame(latest_frame)
        return observed.turn.is_win

    def choose_action(self, latest_frame: FrameLike) -> ActionLike:
        """Return a forced reset or one legal graph-controller candidate."""

        if self._choice_frame is latest_frame and self._choice_action is not None:
            return self._choice_action

        observed = self._consume_frame(latest_frame)
        turn = observed.turn
        if self._fly is not None and observed.scene is not None:
            # Advance the connectome on this frame before ranking, so its
            # preference reflects what the agent is currently looking at. The
            # last executed action rides along as the efference copy; a fly
            # without that sense ignores the extra argument.
            self._fly.observe(
                observed.scene.grid,
                turn.available_action_ids,
                previous_action_id=self._last_action_id,
                previous_click=self._pending_click_xy,
            )
        if turn.is_win:
            raise StateGraphPolicyError("cannot choose an action after WIN")
        if turn.needs_reset:
            action = self._forced_reset(observed)
        else:
            if observed.scene is None or observed.state_key is None:
                raise StateGraphPolicyError("an active ARC frame must contain a terminal grid")
            action = self._choose_active(observed)

        self._choice_frame = latest_frame
        self._choice_action = action
        self._last_action_id = getattr(action, "value", None)
        return action

    def describe(self) -> dict[str, object]:
        """Return the static, serializable controller contract."""

        return {
            "enabled": True,
            "kind": "state_graph",
            "state_hash": self._config.state_hash,
            "decision_seed": self._decision_seed,
            "trainable": False,
            "trainable_parameters": 0,
            "observation": "last_action_complete_subframe",
            "reset_policy": "forced_only_for_not_played_or_game_over",
            "mask_freeze_after": self._config.mask_freeze_after,
            "ui_border_width": self._config.ui_border_width,
            "component_min_area": self._config.component_min_area,
            "component_limit": self._config.component_limit,
            "max_candidate_tier": self._config.max_candidate_tier,
            "max_clicks_per_tier": self._config.max_clicks_per_tier,
        }

    def diagnostics(self) -> dict[str, object]:
        """Return current online-learning and replay diagnostics."""

        last_scene = None if self._cached_observation is None else self._cached_observation.scene
        return {
            "turns": len(self.records),
            "reconciled_turns": sum(record.reconciled for record in self.records),
            "pending_transition": self._pending is not None,
            "pending_reset": self._pending_reset is not None,
            "outcomes": dict(sorted(self._outcomes.items())),
            "level_epoch": self._level_epoch,
            "fly_present": self._fly is not None,
            "fly_ranked_turns": self._fly_ranked,
            "fly_decisive_turns": self._fly_decisive,
            "head_ranked_turns": self._head_ranked,
            "head_decisive_turns": self._head_decisive,
            "head": (None if self._click_head is None else self._click_head.describe()),
            "fly_decisive_rate": (
                0.0 if self._fly_ranked == 0 else self._fly_decisive / self._fly_ranked
            ),
            "effect_observations": self._effects.observation_count,
            "effect_levels_started": self._effects.levels_started,
            "graph_nodes": len(self._graph.nodes),
            "graph_edges": len(self._graph.transitions),
            "graph_transition_observations": sum(
                stats.attempts for stats in self._graph.transitions.values()
            ),
            "replay_queue": len(self._replay_queue),
            "replay_drifts": self._replay_drifts,
            "replay_cooldown": self._replay_cooldown,
            "local_graph_resets": self._local_resets,
            "mask_frozen": None if last_scene is None else last_scene.mask_frozen,
            "mask_comparisons": None if last_scene is None else last_scene.mask_comparisons,
        }

    def _consume_frame(self, frame: FrameLike) -> _ObservedFrame:
        if self._cached_frame is frame and self._cached_observation is not None:
            return self._cached_observation

        # A new response invalidates the decision cache, even when it is
        # visually identical to the previous response.
        self._choice_frame = None
        self._choice_action = None
        turn = ArcTurnState.from_frame(frame)

        if not self._has_grid(frame):
            if self._pending is not None or self._pending_reset is not None or self.records:
                raise StateGraphPolicyError(
                    "only the initial pre-action dummy frame may omit its terminal grid"
                )
            observed = _ObservedFrame(
                turn=turn,
                levels_completed=self._levels_completed(frame),
                scene=None,
                state_key=None,
                candidate_metadata={},
            )
            self._cache(frame, observed)
            return observed

        scene = self._scene_tracker.observe(frame, turn.available_action_ids)
        levels = self._levels_completed(frame)
        if self._last_levels is None:
            self._last_levels = levels
            self._level_epoch = levels

        candidate_metadata = self._candidate_metadata(scene, turn.available_action_ids)
        canonical = self._canonical_state(scene, turn.game_state, self._level_epoch)
        destination_key = self._graph.state_key(canonical)
        novel = destination_key not in self._graph.nodes
        self._graph.upsert_state(destination_key, canonical, candidate_metadata)

        advanced_by = 0
        if self._pending is not None:
            advanced_by = self._reconcile_pending(
                destination_key=destination_key,
                destination_scene=scene,
                destination_turn=turn,
                destination_levels=levels,
                novel=novel,
            )
        if self._pending_reset is not None:
            self._reconcile_reset(destination_key, scene)

        graph_reset = scene.mask_just_frozen
        if advanced_by > 0:
            self._level_epoch += advanced_by
            for _ in range(advanced_by):
                self._effects.start_level()
            graph_reset = True
        elif self._last_levels is not None and levels < self._last_levels:
            # This should not occur because the policy never voluntarily
            # resets. If an external full reset happens, its pixels and bans
            # cannot safely share a graph epoch; transferable effects remain.
            self._level_epoch += 1
            graph_reset = True

        if graph_reset:
            self._reset_local_graph()
            canonical = self._canonical_state(scene, turn.game_state, self._level_epoch)
            destination_key = self._graph.state_key(canonical)
            self._graph.upsert_state(destination_key, canonical, candidate_metadata)

        self._last_levels = levels
        observed = _ObservedFrame(
            turn=turn,
            levels_completed=levels,
            scene=scene,
            state_key=destination_key,
            candidate_metadata=candidate_metadata,
        )
        self._cache(frame, observed)
        return observed

    def _reconcile_pending(
        self,
        *,
        destination_key: bytes,
        destination_scene: SceneObservation,
        destination_turn: ArcTurnState,
        destination_levels: int,
        novel: bool,
    ) -> int:
        pending = self._pending
        if pending is None:
            return 0
        self._pending = None

        changed_cells = int(np.count_nonzero(pending.source_grid != destination_scene.grid))
        if self._click_head is not None and pending.candidate.is_click:
            self._click_head.update(
                pending.source_grid,
                pending.candidate.x,
                pending.candidate.y,
                bool(changed_cells),
            )
        advanced_by = max(0, destination_levels - pending.source_levels)
        fatal = destination_turn.game_state == "GAME_OVER"
        won = destination_turn.game_state == "WIN"
        changed = bool(
            changed_cells
            or destination_turn.game_state != pending.source_state
            or destination_turn.available_action_ids != pending.source_legal_ids
            or advanced_by
        )
        advanced = advanced_by > 0

        if fatal:
            outcome = "DEATH"
        elif won:
            outcome = "WIN"
        elif advanced:
            outcome = "LEVEL_ADVANCE"
        elif changed:
            outcome = "EFFECT"
        else:
            outcome = "NOOP"

        # The reinforcement the connectome has never had. The controller knows
        # what the fly cannot work out for itself -- that a level was cleared or
        # that a move was fatal -- and the mushroom body is the anatomy evolved
        # to consume exactly that signal. Sent through getattr so a tiebreaker
        # without a learning site is unaffected.
        if self._fly is not None:
            reinforce = getattr(self._fly, "reinforce", None)
            if callable(reinforce):
                if outcome in ("WIN", "LEVEL_ADVANCE"):
                    reinforce(1.0)
                elif outcome == "DEATH":
                    reinforce(-1.0)
                elif self._config.dense_reinforcement:
                    # H-MB-LEARNING-DENSE: per-turn outcomes as dopamine. Etas
                    # are sized from MEASURED per-row medians (~513 novel, ~14
                    # NOOP) so each valence expects dense_budget/2 of drive per
                    # game, and hard per-side caps turn that balance into a
                    # worst-case guarantee. Familiar EFFECTs stay silent:
                    # re-treading known ground is neither reward nor pain.
                    half = self._config.dense_budget / 2.0
                    if novel and changed and self._dense_spent_reward < half:
                        eta = half / _DENSE_PRIOR_NOVEL
                        self._dense_spent_reward += eta
                        reinforce(eta)
                    elif not changed and self._dense_spent_punish < half:
                        eta = half / _DENSE_PRIOR_NOOP
                        self._dense_spent_punish += eta
                        reinforce(-eta)

        self._graph.record_transition(
            pending.source_key,
            pending.candidate,
            None if fatal else destination_key,
            changed=changed,
            novel=bool(novel and not fatal),
            fatal=fatal,
            advanced=advanced,
        )
        self._effects.observe(
            pending.candidate,
            effect=changed,
            novel=bool(novel and not fatal),
            fatal=fatal,
            advanced=advanced,
            clicked_color=pending.clicked_color,
        )

        record = pending.record
        record.outcome = outcome
        record.destination_key = destination_key.hex()
        record.changed_cells = changed_cells
        record.changed = changed
        record.novel = bool(novel and not fatal)
        record.fatal = fatal
        record.advanced = advanced
        record.reconciled = True
        self._outcomes[outcome] += 1

        expected = pending.expected_destination
        if expected is not None and expected != destination_key:
            self._abort_replay()
        return advanced_by

    def _reconcile_reset(self, destination_key: bytes, destination_scene: SceneObservation) -> None:
        pending = self._pending_reset
        if pending is None:
            return
        self._pending_reset = None
        record = pending.record
        record.outcome = "RESET"
        record.destination_key = destination_key.hex()
        record.changed_cells = None
        record.changed = True
        record.novel = destination_key not in self._graph.nodes
        record.fatal = False
        record.advanced = False
        record.reconciled = True
        self._outcomes["RESET"] += 1
        del destination_scene

    def _choose_active(self, observed: _ObservedFrame) -> ActionLike:
        assert observed.scene is not None and observed.state_key is not None
        state_key = observed.state_key
        node = self._graph.node(state_key)

        if self._replay_cooldown > 0:
            self._replay_cooldown -= 1

        candidate: ActionCandidate | None = None
        mode = "frontier"
        expected_destination: bytes | None = None

        if self._replay_queue and self._replay_cooldown == 0:
            step = self._replay_queue[0]
            if (
                step.expected_source == state_key
                and step.candidate in node.candidates
                and step.candidate not in node.hard_bans
            ):
                self._replay_queue.pop(0)
                candidate = step.candidate
                expected_destination = step.expected_destination
                mode = "replay"
            else:
                self._abort_replay()

        if candidate is None and node.frontier_candidates:
            candidate = self._rank_candidates(state_key, node.frontier_candidates, observed)[0]
            mode = "frontier"

        if candidate is None and self._replay_cooldown == 0:
            path = self._graph.nearest_reachable_frontier(state_key)
            if path:
                self._replay_queue = list(path)
                step = self._replay_queue.pop(0)
                candidate = step.candidate
                expected_destination = step.expected_destination
                mode = "replay"

        if candidate is None:
            safe = tuple(sorted(node.candidates - node.hard_bans))
            if not safe:
                raise StateGraphPolicyError(
                    "active state has no legal nonfatal candidate; RESET remains forbidden"
                )
            candidate = self._rank_candidates(state_key, safe, observed, retries=True)[0]
            mode = "retry"

        metadata = observed.candidate_metadata.get(candidate)
        clicked_color = self._clicked_color(candidate, metadata, observed.scene)
        estimate = self._effects.estimate(candidate, clicked_color=clicked_color)
        action = self._resolve_action(candidate.action_id)
        self._pending_click_xy = (
            (int(candidate.x), int(candidate.y)) if candidate.is_click else None
        )
        if candidate.is_click:
            setter = getattr(action, "set_data", None)
            if not callable(setter):
                raise StateGraphPolicyError("ACTION6 must implement set_data(data)")
            setter(candidate.payload)

        reasoning = {
            "policy": "state-graph-controller",
            "step": self._decision_index,
            "mode": mode,
            "state_key": state_key.hex(),
            "level_epoch": self._level_epoch,
            "action_id": candidate.action_id,
            "effect_priority": estimate.priority,
            "effect_evidence": estimate.evidence,
            "expected_destination": (
                None if expected_destination is None else expected_destination.hex()
            ),
        }
        if candidate.is_click:
            reasoning["coordinate"] = candidate.payload
            reasoning["clicked_color"] = clicked_color
            reasoning["click_tier"] = None if metadata is None else metadata.tier
        self._annotate(action, reasoning)

        record = ControllerTurnRecord(
            step=self._decision_index,
            action_id=candidate.action_id,
            source_state=observed.turn.game_state,
            source_key=state_key.hex(),
            mode=mode,
            forced_reset=False,
            coordinate_x=candidate.x,
            coordinate_y=candidate.y,
            clicked_color=clicked_color,
            click_tier=None if metadata is None else metadata.tier,
            expected_destination=(
                None if expected_destination is None else expected_destination.hex()
            ),
        )
        self.records.append(record)
        source_grid = np.asarray(observed.scene.grid, dtype=np.int8).copy()
        source_grid.setflags(write=False)
        self._pending = _PendingDecision(
            candidate=candidate,
            source_key=state_key,
            source_grid=source_grid,
            source_state=observed.turn.game_state,
            source_levels=observed.levels_completed,
            source_legal_ids=observed.turn.available_action_ids,
            clicked_color=clicked_color,
            expected_destination=expected_destination,
            record=record,
        )
        self._decision_index += 1
        return action

    def _forced_reset(self, observed: _ObservedFrame) -> ActionLike:
        action = self._resolve_action(_RESET_ACTION_ID)
        reasoning = {
            "policy": "state-graph-controller",
            "step": self._decision_index,
            "mode": "forced-reset",
            "state": observed.turn.game_state,
        }
        self._annotate(action, reasoning)
        record = ControllerTurnRecord(
            step=self._decision_index,
            action_id=_RESET_ACTION_ID,
            source_state=observed.turn.game_state,
            source_key=None if observed.state_key is None else observed.state_key.hex(),
            mode="forced-reset",
            forced_reset=True,
        )
        self.records.append(record)
        self._pending_reset = _PendingReset(record=record)
        self._replay_queue.clear()
        self._decision_index += 1
        return action

    def _candidate_metadata(
        self, scene: SceneObservation, legal_ids: tuple[int, ...]
    ) -> dict[ActionCandidate, ClickCandidate | None]:
        candidates: dict[ActionCandidate, ClickCandidate | None] = {}
        legal = tuple(dict.fromkeys(int(identifier) for identifier in legal_ids))
        for identifier in legal:
            if identifier in (_RESET_ACTION_ID, _CLICK_ACTION_ID):
                continue
            candidates[ActionCandidate(identifier)] = None

        if _CLICK_ACTION_ID in legal:
            per_tier: Counter[int] = Counter()
            for click in scene.click_candidates:
                if click.component_index >= self._config.component_limit:
                    continue
                if per_tier[click.tier] >= self._config.max_clicks_per_tier:
                    continue
                candidate = ActionCandidate(_CLICK_ACTION_ID, x=click.x, y=click.y)
                candidates.setdefault(candidate, click)
                per_tier[click.tier] += 1

            # A completely uniform click-only scene still needs a legal
            # protocol action. This fallback is deliberately last-resort and
            # does not masquerade as a component-grounded click.
            if not any(candidate.is_click for candidate in candidates):
                coordinate = self._fallback_coordinate(scene)
                candidate = ActionCandidate(_CLICK_ACTION_ID, x=coordinate[0], y=coordinate[1])
                candidates[candidate] = None
        return candidates

    def _rank_candidates(
        self,
        state_key: bytes,
        candidates: tuple[ActionCandidate, ...],
        observed: _ObservedFrame,
        *,
        retries: bool = False,
    ) -> tuple[ActionCandidate, ...]:
        assert observed.scene is not None
        node = self._graph.node(state_key)
        family_attempts: Counter[int] = Counter()
        for known in node.candidates:
            stats = self._graph.transition_stats(state_key, known)
            if stats is not None:
                family_attempts[known.action_id] += stats.attempts

        def rank(
            candidate: ActionCandidate, *, use_fly: bool = True, use_head: bool = True
        ) -> tuple[float | int | bytes, ...]:
            metadata = observed.candidate_metadata.get(candidate)
            color = self._clicked_color(candidate, metadata, observed.scene)
            estimate = self._effects.estimate(candidate, clicked_color=color)
            exploration = self._config.effect_exploration_bonus / math.sqrt(1.0 + estimate.evidence)
            consequence = 0.0
            if (
                use_head
                and self._click_head is not None
                and candidate.is_click
                and observed.scene is not None
            ):
                # H-CONSEQUENCE-COUPLING: predicted click consequence enters
                # the PRIMARY term, so a click the head has learned is a
                # no-op sorts behind actions the controller would otherwise
                # rank equal or better. Scaled by the same 1/sqrt(1+evidence)
                # decay as the exploration bonus: the prediction is a PRIOR
                # for untried candidates, and measured effects replace it as
                # evidence arrives -- the first divergence gate measured an
                # unscaled head overriding the controller on 88% of turns,
                # which was never the registered mechanism.
                consequence = float(
                    self._click_head.bonus(observed.scene.grid, candidate.x, candidate.y)
                ) / math.sqrt(1.0 + estimate.evidence)
            stats = self._graph.transition_stats(state_key, candidate)
            attempts = 0 if stats is None else stats.attempts
            retry_prefix = attempts if retries else family_attempts[candidate.action_id]
            fly_rank = 0.0
            if use_fly and self._fly is not None:
                # Negated: higher connectome preference sorts earlier.
                fly_rank = -float(
                    self._fly.preference(candidate.action_id, candidate.x, candidate.y)
                )
            return (
                retry_prefix,
                attempts,
                -(estimate.priority + exploration + consequence),
                fly_rank,
                self._tie_digest(state_key, candidate),
                candidate.to_bytes(),
            )

        ordered = tuple(sorted(candidates, key=rank))
        if self._fly is not None and ordered:
            # How often does the connectome actually decide? Everything ranked
            # before it can leave no tie at all, in which case the fly is present
            # but inert. Counting the turns where removing it would have chosen
            # differently is the only honest measure of its influence, and it is
            # what tells us whether the tie position has headroom left.
            self._fly_ranked += 1
            without = min(candidates, key=lambda c: rank(c, use_fly=False))
            if without != ordered[0]:
                self._fly_decisive += 1
        if self._click_head is not None and ordered:
            self._head_ranked += 1
            without_head = min(candidates, key=lambda c: rank(c, use_head=False))
            if without_head != ordered[0]:
                self._head_decisive += 1
        return ordered

    def _tie_digest(self, state_key: bytes, candidate: ActionCandidate) -> bytes:
        digest = hashlib.blake2b(digest_size=16)
        digest.update(_TIE_PREFIX)
        digest.update(self._decision_seed.to_bytes(8, "little", signed=False))
        digest.update(self._level_epoch.to_bytes(8, "little", signed=False))
        digest.update(len(state_key).to_bytes(2, "little", signed=False))
        digest.update(state_key)
        digest.update(candidate.to_bytes())
        digest.update(self._decision_index.to_bytes(8, "little", signed=False))
        return digest.digest()

    def _clicked_color(
        self,
        candidate: ActionCandidate,
        metadata: ClickCandidate | None,
        scene: SceneObservation,
    ) -> int | None:
        if not candidate.is_click:
            return None
        if metadata is not None:
            return metadata.color
        assert candidate.x is not None and candidate.y is not None
        return int(scene.grid[candidate.y, candidate.x])

    def _canonical_state(self, scene: SceneObservation, game_state: str, epoch: int) -> bytes:
        state = game_state.encode("ascii", errors="strict")
        return (
            _STATE_PREFIX
            + epoch.to_bytes(8, "little", signed=False)
            + len(state).to_bytes(1, "little", signed=False)
            + state
            + scene.state_key.canonical
        )

    def _reset_local_graph(self) -> None:
        self._graph = StateGraph()
        self._replay_queue.clear()
        self._replay_cooldown = 0
        self._local_resets += 1

    def _abort_replay(self) -> None:
        self._replay_queue.clear()
        self._replay_drifts += 1
        self._replay_cooldown = self._config.replan_cooldown

    def _fallback_coordinate(self, scene: SceneObservation) -> tuple[int, int]:
        size = self._config.coarse_cell_size
        for y in range(size // 2, 64, size):
            for x in range(size // 2, 64, size):
                if not bool(scene.volatile_mask[y, x]):
                    return x, y
        return 32, 32

    def _resolve_action(self, identifier: int) -> ActionLike:
        resolver = getattr(self._actions, "from_id", None)
        if callable(resolver):
            try:
                return resolver(identifier)
            except ValueError as exc:
                raise StateGraphPolicyError(f"unknown ARC action id {identifier}") from exc
        for action in self._actions:  # type: ignore[union-attr]
            if action_id(action) == identifier:
                return action
        raise StateGraphPolicyError(f"unknown ARC action id {identifier}")

    @staticmethod
    def _annotate(action: ActionLike, reasoning: dict[str, object]) -> None:
        with suppress(AttributeError, TypeError):
            action.reasoning = reasoning

    @staticmethod
    def _levels_completed(frame: FrameLike) -> int:
        raw = getattr(frame, "levels_completed", 0)
        if isinstance(raw, bool) or not isinstance(raw, (int, np.integer)):
            raise StateGraphPolicyError("levels_completed must be an integer")
        levels = int(raw)
        if levels < 0:
            raise StateGraphPolicyError("levels_completed cannot be negative")
        return levels

    @staticmethod
    def _has_grid(frame: FrameLike) -> bool:
        raw = getattr(frame, "frame", None)
        if raw is None:
            return False
        try:
            return len(raw) > 0  # type: ignore[arg-type]
        except TypeError:
            return bool(np.asarray(raw).size)

    def _cache(self, frame: FrameLike, observed: _ObservedFrame) -> None:
        self._cached_frame = frame
        self._cached_observation = observed


__all__ = [
    "ControllerTurnRecord",
    "StateGraphPolicy",
    "StateGraphPolicyError",
]
