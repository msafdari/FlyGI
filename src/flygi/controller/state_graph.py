"""Generic state-transition memory for controller-only ARC exploration.

The classes in this module deliberately know nothing about individual games,
connectome state, or environment source code.  They store only observations and
actions supplied by a policy.  Exact state transitions remain separate from the
cross-level effect model: the former supports verified replay within one level,
while the latter carries generic action-effect evidence across levels of the
same game.
"""

from __future__ import annotations

import hashlib
import math
from collections import Counter, deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from functools import total_ordering
from types import MappingProxyType

ARC_ACTION_MIN = 1
ARC_ACTION_MAX = 7
CLICK_ACTION_ID = 6
GRID_SIZE = 64
ARC_COLOR_MIN = 0
ARC_COLOR_MAX = 15
DEFAULT_STATE_DIGEST_BYTES = 16


class StateGraphError(ValueError):
    """Base class for invalid state-graph operations."""


class StateCollisionError(StateGraphError):
    """Raised when one compact state key is presented with different bytes."""


def _canonical_bytes(value: bytes | bytearray | memoryview, name: str) -> bytes:
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError(f"{name} must be bytes-like")
    normalized = bytes(value)
    if not normalized:
        raise ValueError(f"{name} must not be empty")
    return normalized


def _boolean(value: bool, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a boolean")
    return value


@total_ordering
@dataclass(frozen=True, slots=True)
class ActionCandidate:
    """One executable non-reset ARC action.

    ``RESET`` is intentionally not representable.  It is legal only when the
    protocol reports ``NOT_PLAYED`` or ``GAME_OVER`` and must therefore remain a
    forced policy action, never a graph exploration candidate.

    The three-byte representation is stable: ``action_id`` followed by ``x+1``
    and ``y+1``.  Zero denotes an absent coordinate.
    """

    action_id: int
    x: int | None = None
    y: int | None = None

    def __post_init__(self) -> None:
        if isinstance(self.action_id, bool) or not isinstance(self.action_id, int):
            raise TypeError("action_id must be an integer")
        if not ARC_ACTION_MIN <= self.action_id <= ARC_ACTION_MAX:
            raise ValueError(
                f"action_id must lie in [{ARC_ACTION_MIN}, {ARC_ACTION_MAX}]; "
                "RESET is protocol-forced and is not a candidate"
            )

        if self.action_id == CLICK_ACTION_ID:
            if self.x is None or self.y is None:
                raise ValueError("ACTION6 candidates require both x and y coordinates")
            for name, coordinate in (("x", self.x), ("y", self.y)):
                if isinstance(coordinate, bool) or not isinstance(coordinate, int):
                    raise TypeError(f"{name} must be an integer")
                if not 0 <= coordinate < GRID_SIZE:
                    raise ValueError(f"{name} must lie in [0, {GRID_SIZE - 1}]")
        elif self.x is not None or self.y is not None:
            raise ValueError("only ACTION6 candidates may carry click coordinates")

    @property
    def is_click(self) -> bool:
        return self.action_id == CLICK_ACTION_ID

    @property
    def sort_key(self) -> tuple[int, int, int]:
        """Return the total ordering used by graph traversal and tie-breaking."""

        return (
            self.action_id,
            -1 if self.x is None else self.x,
            -1 if self.y is None else self.y,
        )

    @property
    def payload(self) -> dict[str, int]:
        """Return the action-data payload expected by the ARC adapter."""

        if not self.is_click:
            return {}
        assert self.x is not None and self.y is not None
        return {"x": self.x, "y": self.y}

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ActionCandidate):
            return NotImplemented
        return self.sort_key < other.sort_key

    def to_bytes(self) -> bytes:
        """Serialize to a compact, deterministic three-byte key."""

        x_code = 0 if self.x is None else self.x + 1
        y_code = 0 if self.y is None else self.y + 1
        return bytes((self.action_id, x_code, y_code))

    @classmethod
    def from_bytes(cls, payload: bytes | bytearray | memoryview) -> ActionCandidate:
        """Decode and validate :meth:`to_bytes` output."""

        if not isinstance(payload, (bytes, bytearray, memoryview)):
            raise TypeError("candidate payload must be bytes-like")
        encoded = bytes(payload)
        if len(encoded) != 3:
            raise ValueError("candidate payload must contain exactly three bytes")
        action_id, x_code, y_code = encoded
        x = None if x_code == 0 else x_code - 1
        y = None if y_code == 0 else y_code - 1
        try:
            candidate = cls(action_id=action_id, x=x, y=y)
        except (TypeError, ValueError) as exc:
            raise ValueError("candidate payload is not canonical") from exc
        if candidate.to_bytes() != encoded:
            raise ValueError("candidate payload is not canonical")
        return candidate


@dataclass(slots=True)
class TransitionOutcomeStats:
    """Observed outcomes for one exact ``(state, candidate)`` pair."""

    attempts: int = 0
    changed_count: int = 0
    novel_count: int = 0
    fatal_count: int = 0
    advanced_count: int = 0
    destinations: Counter[bytes] = field(default_factory=Counter)

    def record(
        self,
        *,
        destination: bytes | None,
        changed: bool,
        novel: bool,
        fatal: bool,
        advanced: bool,
    ) -> None:
        """Add one fully observed transition outcome."""

        changed = _boolean(changed, "changed")
        novel = _boolean(novel, "novel")
        fatal = _boolean(fatal, "fatal")
        advanced = _boolean(advanced, "advanced")
        if destination is None and not fatal:
            raise StateGraphError("a non-fatal transition must identify its destination")
        normalized_destination = (
            None if destination is None else _canonical_bytes(destination, "destination")
        )

        self.attempts += 1
        self.changed_count += int(changed)
        self.novel_count += int(novel)
        self.fatal_count += int(fatal)
        self.advanced_count += int(advanced)
        if normalized_destination is not None:
            self.destinations[normalized_destination] += 1

    @property
    def no_op_count(self) -> int:
        return self.attempts - self.changed_count

    @property
    def deterministic_destination(self) -> bytes | None:
        """Return the only replay-safe destination, if one exists.

        A single observed target is not sufficient when some attempts were
        fatal or had no target.  Every recorded attempt must have reached the
        same non-fatal state.
        """

        if self.attempts == 0 or self.fatal_count or len(self.destinations) != 1:
            return None
        destination, count = next(iter(self.destinations.items()))
        return destination if count == self.attempts else None

    @property
    def destination_counts(self) -> tuple[tuple[bytes, int], ...]:
        """Return destination counts in portable deterministic order."""

        return tuple(sorted(self.destinations.items()))


@dataclass(slots=True)
class StateNode:
    """Exact state memory and its local candidate bookkeeping."""

    key: bytes
    canonical_bytes: bytes
    candidates: set[ActionCandidate] = field(default_factory=set)
    tested: set[ActionCandidate] = field(default_factory=set)
    hard_bans: set[ActionCandidate] = field(default_factory=set)
    visits: int = 0

    def __post_init__(self) -> None:
        self.key = _canonical_bytes(self.key, "state key")
        self.canonical_bytes = _canonical_bytes(self.canonical_bytes, "canonical state")
        self.candidates = set(self.candidates)
        self.tested = set(self.tested)
        self.hard_bans = set(self.hard_bans)
        if isinstance(self.visits, bool) or not isinstance(self.visits, int):
            raise TypeError("visits must be an integer")
        if self.visits < 0:
            raise ValueError("visits must be non-negative")
        self.candidates.update(self.tested)
        self.candidates.update(self.hard_bans)
        self.tested.update(self.hard_bans)

    def merge_candidates(self, candidates: Iterable[ActionCandidate]) -> None:
        for candidate in candidates:
            if not isinstance(candidate, ActionCandidate):
                raise TypeError("state candidates must be ActionCandidate instances")
            self.candidates.add(candidate)

    def mark_tested(self, candidate: ActionCandidate) -> None:
        self.merge_candidates((candidate,))
        self.tested.add(candidate)

    def ban(self, candidate: ActionCandidate) -> None:
        self.mark_tested(candidate)
        self.hard_bans.add(candidate)

    @property
    def ordered_candidates(self) -> tuple[ActionCandidate, ...]:
        return tuple(sorted(self.candidates))

    @property
    def frontier_candidates(self) -> tuple[ActionCandidate, ...]:
        return tuple(sorted(self.candidates - self.tested - self.hard_bans))

    @property
    def has_frontier(self) -> bool:
        return bool(self.frontier_candidates)


@dataclass(frozen=True, slots=True)
class ReplayStep:
    """One verified edge in a replay-to-frontier plan."""

    expected_source: bytes
    candidate: ActionCandidate
    expected_destination: bytes

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "expected_source",
            _canonical_bytes(self.expected_source, "expected source"),
        )
        object.__setattr__(
            self,
            "expected_destination",
            _canonical_bytes(self.expected_destination, "expected destination"),
        )
        if not isinstance(self.candidate, ActionCandidate):
            raise TypeError("replay candidate must be an ActionCandidate")


class StateGraph:
    """Directed exact-state graph with conservative replay semantics."""

    def __init__(self, *, digest_size: int = DEFAULT_STATE_DIGEST_BYTES) -> None:
        if isinstance(digest_size, bool) or not isinstance(digest_size, int):
            raise TypeError("digest_size must be an integer")
        if not 1 <= digest_size <= 64:
            raise ValueError("digest_size must lie in [1, 64]")
        self._digest_size = digest_size
        self._nodes: dict[bytes, StateNode] = {}
        self._transitions: dict[tuple[bytes, ActionCandidate], TransitionOutcomeStats] = {}

    @property
    def nodes(self) -> Mapping[bytes, StateNode]:
        return MappingProxyType(self._nodes)

    @property
    def transitions(
        self,
    ) -> Mapping[tuple[bytes, ActionCandidate], TransitionOutcomeStats]:
        return MappingProxyType(self._transitions)

    def state_key(self, canonical_state: bytes | bytearray | memoryview) -> bytes:
        """Hash canonical state bytes using the graph's declared key size."""

        canonical = _canonical_bytes(canonical_state, "canonical state")
        return hashlib.blake2b(canonical, digest_size=self._digest_size).digest()

    def upsert_state(
        self,
        key: bytes | bytearray | memoryview,
        canonical_state: bytes | bytearray | memoryview,
        candidates: Iterable[ActionCandidate] = (),
    ) -> StateNode:
        """Visit a state, verifying its compact key and merging candidates."""

        normalized_key = _canonical_bytes(key, "state key")
        canonical = _canonical_bytes(canonical_state, "canonical state")
        node = self._nodes.get(normalized_key)
        if node is None:
            node = StateNode(key=normalized_key, canonical_bytes=canonical)
            self._nodes[normalized_key] = node
        elif node.canonical_bytes != canonical:
            raise StateCollisionError(
                "state-key collision: one key was presented with different canonical bytes"
            )
        node.merge_candidates(candidates)
        node.visits += 1
        return node

    def node(self, key: bytes | bytearray | memoryview) -> StateNode:
        normalized_key = _canonical_bytes(key, "state key")
        try:
            return self._nodes[normalized_key]
        except KeyError as exc:
            raise StateGraphError("unknown state key") from exc

    def merge_candidates(
        self,
        key: bytes | bytearray | memoryview,
        candidates: Iterable[ActionCandidate],
    ) -> StateNode:
        node = self.node(key)
        node.merge_candidates(candidates)
        return node

    def ban_candidate(
        self,
        key: bytes | bytearray | memoryview,
        candidate: ActionCandidate,
    ) -> None:
        """Hard-ban a candidate only at this exact state."""

        self.node(key).ban(candidate)

    def transition_stats(
        self,
        source: bytes | bytearray | memoryview,
        candidate: ActionCandidate,
    ) -> TransitionOutcomeStats | None:
        source_key = _canonical_bytes(source, "source state")
        return self._transitions.get((source_key, candidate))

    def record_transition(
        self,
        source: bytes | bytearray | memoryview,
        candidate: ActionCandidate,
        destination: bytes | bytearray | memoryview | None,
        *,
        changed: bool,
        novel: bool,
        fatal: bool,
        advanced: bool,
    ) -> TransitionOutcomeStats:
        """Record one directed observation without overwriting earlier outcomes."""

        if not isinstance(candidate, ActionCandidate):
            raise TypeError("candidate must be an ActionCandidate")
        source_node = self.node(source)
        destination_key = (
            None if destination is None else _canonical_bytes(destination, "destination state")
        )
        if destination_key is not None and destination_key not in self._nodes:
            raise StateGraphError("destination state must be registered before its transition")
        if destination_key is None and not fatal:
            raise StateGraphError("a non-fatal transition must identify its destination")

        source_node.mark_tested(candidate)
        stats = self._transitions.setdefault((source_node.key, candidate), TransitionOutcomeStats())
        stats.record(
            destination=destination_key,
            changed=changed,
            novel=novel,
            fatal=fatal,
            advanced=advanced,
        )
        if fatal:
            source_node.ban(candidate)
        return stats

    def safe_replay_edges(self, source: bytes | bytearray | memoryview) -> tuple[ReplayStep, ...]:
        """Return only observed, non-fatal, single-destination outgoing edges."""

        source_node = self.node(source)
        steps: list[ReplayStep] = []
        for candidate in source_node.ordered_candidates:
            if candidate in source_node.hard_bans:
                continue
            stats = self._transitions.get((source_node.key, candidate))
            if stats is None:
                continue
            destination = stats.deterministic_destination
            if destination is None or destination not in self._nodes:
                continue
            steps.append(
                ReplayStep(
                    expected_source=source_node.key,
                    candidate=candidate,
                    expected_destination=destination,
                )
            )
        return tuple(steps)

    def nearest_reachable_frontier(
        self, start: bytes | bytearray | memoryview
    ) -> tuple[ReplayStep, ...] | None:
        """BFS to the nearest state with an untested, non-banned candidate.

        Traversal uses directed replay-safe edges only.  The returned steps carry
        both expected endpoints so a policy can verify every response and abort
        immediately on a mismatch.  An empty tuple means the start is already a
        frontier; ``None`` means no frontier is safely reachable.
        """

        start_node = self.node(start)
        if start_node.has_frontier:
            return ()

        queue: deque[bytes] = deque((start_node.key,))
        visited = {start_node.key}
        parent: dict[bytes, ReplayStep] = {}

        while queue:
            source = queue.popleft()
            for step in self.safe_replay_edges(source):
                destination = step.expected_destination
                if destination in visited:
                    continue
                visited.add(destination)
                parent[destination] = step
                if self._nodes[destination].has_frontier:
                    return self._reconstruct_path(start_node.key, destination, parent)
                queue.append(destination)
        return None

    @staticmethod
    def _reconstruct_path(
        start: bytes,
        destination: bytes,
        parent: Mapping[bytes, ReplayStep],
    ) -> tuple[ReplayStep, ...]:
        reversed_steps: list[ReplayStep] = []
        cursor = destination
        while cursor != start:
            step = parent[cursor]
            reversed_steps.append(step)
            cursor = step.expected_source
        reversed_steps.reverse()
        return tuple(reversed_steps)


@dataclass(slots=True)
class _EffectCounts:
    attempts: int = 0
    effect_count: int = 0
    novel_count: int = 0
    fatal_count: int = 0
    advanced_count: int = 0

    def record(self, *, effect: bool, novel: bool, fatal: bool, advanced: bool) -> None:
        self.attempts += 1
        self.effect_count += int(effect)
        self.novel_count += int(novel)
        self.fatal_count += int(fatal)
        self.advanced_count += int(advanced)


@dataclass(frozen=True, slots=True)
class EffectEstimate:
    """Posterior effect probabilities and their deterministic priority."""

    effect_probability: float
    novelty_probability: float
    fatal_probability: float
    advancement_probability: float
    evidence: float
    exploration_bonus: float
    priority: float


type EffectKey = tuple[str, int] | tuple[str, int, int]


class EffectModel:
    """Cross-level, within-game action-effect evidence.

    Simple actions learn one action-ID posterior.  Clicks combine two generic
    posteriors: the observed color under the click and its coarse spatial region.
    Every Bernoulli outcome uses the same Beta prior (Laplace smoothing by
    default).  Exact fatal bans remain the responsibility of :class:`StateGraph`;
    death evidence here is deliberately only a soft penalty.
    """

    def __init__(
        self,
        *,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0,
        effect_weight: float = 1.0,
        novelty_weight: float = 1.0,
        advancement_bonus: float = 2.0,
        death_penalty: float = 2.0,
        exploration_bonus: float = 0.5,
        coarse_region_bins: int = 4,
    ) -> None:
        for name, value in (
            ("prior_alpha", prior_alpha),
            ("prior_beta", prior_beta),
        ):
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
        for name, value in (
            ("effect_weight", effect_weight),
            ("novelty_weight", novelty_weight),
            ("advancement_bonus", advancement_bonus),
            ("death_penalty", death_penalty),
            ("exploration_bonus", exploration_bonus),
        ):
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")
        if isinstance(coarse_region_bins, bool) or not isinstance(coarse_region_bins, int):
            raise TypeError("coarse_region_bins must be an integer")
        if not 1 <= coarse_region_bins <= GRID_SIZE:
            raise ValueError(f"coarse_region_bins must lie in [1, {GRID_SIZE}]")

        self._prior_alpha = float(prior_alpha)
        self._prior_beta = float(prior_beta)
        self._effect_weight = float(effect_weight)
        self._novelty_weight = float(novelty_weight)
        self._advancement_bonus = float(advancement_bonus)
        self._death_penalty = float(death_penalty)
        self._exploration_bonus = float(exploration_bonus)
        self._coarse_region_bins = coarse_region_bins
        self._counts: dict[EffectKey, _EffectCounts] = {}
        self._levels_started = 0

    @property
    def levels_started(self) -> int:
        return self._levels_started

    @property
    def observation_count(self) -> int:
        """Return action observations, without double-counting click features."""

        simple = sum(counts.attempts for key, counts in self._counts.items() if key[0] == "simple")
        click_colors = sum(
            counts.attempts for key, counts in self._counts.items() if key[0] == "click-color"
        )
        return simple + click_colors

    def start_level(self) -> None:
        """Mark a level boundary without forgetting cross-level evidence."""

        self._levels_started += 1

    def reset_game(self) -> None:
        """Clear learned effects only when a new game/environment begins."""

        self._counts.clear()
        self._levels_started = 0

    def observe(
        self,
        candidate: ActionCandidate,
        *,
        effect: bool,
        novel: bool,
        fatal: bool,
        advanced: bool,
        clicked_color: int | None = None,
    ) -> None:
        """Update every generic feature attached to an executed candidate."""

        effect = _boolean(effect, "effect")
        novel = _boolean(novel, "novel")
        fatal = _boolean(fatal, "fatal")
        advanced = _boolean(advanced, "advanced")
        for key in self._feature_keys(candidate, clicked_color):
            self._counts.setdefault(key, _EffectCounts()).record(
                effect=effect,
                novel=novel,
                fatal=fatal,
                advanced=advanced,
            )

    def estimate(
        self,
        candidate: ActionCandidate,
        *,
        clicked_color: int | None = None,
    ) -> EffectEstimate:
        """Return the smoothed estimate used to rank this candidate."""

        keys = self._feature_keys(candidate, clicked_color)
        counts = [self._counts.get(key, _EffectCounts()) for key in keys]
        effect_probability = self._mean_posterior(counts, "effect_count")
        novelty_probability = self._mean_posterior(counts, "novel_count")
        fatal_probability = self._mean_posterior(counts, "fatal_count")
        advancement_probability = self._mean_posterior(counts, "advanced_count")
        evidence = sum(item.attempts for item in counts) / len(counts)
        exploration_bonus = self._exploration_bonus / math.sqrt(1.0 + evidence)
        priority = (
            self._effect_weight * effect_probability
            + self._novelty_weight * novelty_probability
            + self._advancement_bonus * advancement_probability
            - self._death_penalty * fatal_probability
            + exploration_bonus
        )
        return EffectEstimate(
            effect_probability=effect_probability,
            novelty_probability=novelty_probability,
            fatal_probability=fatal_probability,
            advancement_probability=advancement_probability,
            evidence=evidence,
            exploration_bonus=exploration_bonus,
            priority=float(priority),
        )

    def priority(
        self,
        candidate: ActionCandidate,
        *,
        clicked_color: int | None = None,
    ) -> float:
        return self.estimate(candidate, clicked_color=clicked_color).priority

    def _feature_keys(
        self,
        candidate: ActionCandidate,
        clicked_color: int | None,
    ) -> tuple[EffectKey, ...]:
        if not isinstance(candidate, ActionCandidate):
            raise TypeError("candidate must be an ActionCandidate")
        if not candidate.is_click:
            return (("simple", candidate.action_id),)

        if isinstance(clicked_color, bool) or not isinstance(clicked_color, int):
            raise TypeError("click candidates require an integer clicked_color")
        if not ARC_COLOR_MIN <= clicked_color <= ARC_COLOR_MAX:
            raise ValueError(f"clicked_color must lie in [{ARC_COLOR_MIN}, {ARC_COLOR_MAX}]")
        assert candidate.x is not None and candidate.y is not None
        region_x = min(
            self._coarse_region_bins - 1,
            candidate.x * self._coarse_region_bins // GRID_SIZE,
        )
        region_y = min(
            self._coarse_region_bins - 1,
            candidate.y * self._coarse_region_bins // GRID_SIZE,
        )
        return (
            ("click-color", clicked_color),
            ("click-region", region_x, region_y),
        )

    def _mean_posterior(self, counts: list[_EffectCounts], field_name: str) -> float:
        probabilities = []
        for item in counts:
            successes = int(getattr(item, field_name))
            probabilities.append(
                (successes + self._prior_alpha)
                / (item.attempts + self._prior_alpha + self._prior_beta)
            )
        return float(sum(probabilities) / len(probabilities))
