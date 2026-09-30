"""Online search layer: budgeted incremental BFS through the live game.

REGISTERED under H-ONLINE-SEARCH (supported 2026-09-30): eleven of 25 public
games fall to bounded blind program search (programs of length 3-15), measured
by the offline instrument scripts/online_search_premise.py. This module is the
preregistered consequence: the same mechanism seated ONLINE, consulted by the
policy exactly like the FAP executor -- abstaining by default, overriding only
while ENGAGED. It is ENGINEERED SCAFFOLD end to end, recorded as such per the
first principle: no fly neuron computes anything here.

PREREGISTERED NUMBERS (EXPERIMENTS.yaml H-ONLINE-SEARCH build ship bars,
immutable): engagement after a 75-turn stuck signal, an exploration budget of
at most 1,500 emitted actions per level (RESET replays included) followed by
permanent abstention for that level, and the instrument's click-candidate cap
of 12. The timer-line rule, wake handling, scene-derived click branching and
frame+legal-mask state identity are ports of the measured offline instrument.

Mechanism when engaged: maintain a search tree whose nodes are masked-frame
fingerprints; emit ONE step per ``propose`` -- a RESET, the next replay step of
the frontier node's prefix, or the frontier expansion action -- and consume
``observe`` to record the resulting state. A step whose result fingerprint
equals the next target's is never replayed to (states equal under the search's
own identity are the same state), which is how the online layer fits the
1,500-action budget that the offline instrument's replay-per-branch discipline
would exceed.

ASSUMPTIONS, labelled where encoded and summarized here:
  * observe() calls approximate reconciled turns for the stuck signal; the
    counter restarts on notify_level_advance ONLY -- a forced reset is not a
    level advance, and the sp80 measurement (a death every ~31 champion
    turns) showed a counter that restarted on forced resets would never
    reach the preregistered 75.
  * The timer-line rule samples the champion's own pre-engagement transitions
    in place of the instrument's 24-step seeded random walk (same border-line
    rule and thresholds); the mask freezes at first engagement and is reused
    across levels.
  * RESET is emitted without a legal-mask check: MEASURED 2026-09-30 (offline
    arcade probe, cd82) that active frames accept action 0 while never listing
    it in available_actions; the premise instrument's thousands of replays
    relied on exactly that.
  * The post-reset swallow (measured on sc25/g50t) is handled by re-emitting
    the first post-reset step once when its result left the masked state
    unchanged -- the instrument's probe-once wake, expressed under the
    search's own state identity.
  * DECLARED LIMITATION (ported): replay assumes RESET restores the level's
    initial frame exactly; drift counters record violations instead of
    recovering from them.
"""

from __future__ import annotations

import hashlib
from collections import deque
from dataclasses import dataclass, field
from math import ceil
from typing import Any

import numpy as np
from numpy.typing import NDArray

from flygi.controller.fap_library import Step
from flygi.controller.scene import (
    component_click_candidates,
    components_for_coverage,
    extract_components,
    infer_background,
)

# --- Preregistered numbers (EXPERIMENTS.yaml H-ONLINE-SEARCH; immutable) ----
STUCK_OBSERVE_TURNS = 75
LEVEL_ACTION_BUDGET = 1500
# GATE-(a) AMENDMENT, registered 2026-09-30 before any re-run: engagement
# additionally requires the remaining host action budget (when known) to
# cover the full immutable search plus margin. At 600-action battery rows
# the layer therefore never engages (measured: engaging there burned the
# row on unfinishable searches and erased wandering progress); the gateway
# and the uncapped rerun are where it works.
ENGAGEMENT_MIN_REMAINING_BUDGET = 1600
CLICK_CAP = 12

# --- Instrument constants (ported from scripts/online_search_premise.py) ----
DEPTH_LIMIT = 16
TIMER_BORDER_WIDTH = 4
TIMER_CHANGE_FRACTION = 0.60
TIMER_MIN_CHANGES = 4
_COMPONENT_LIMIT = 64  # champion ControllerConfig.component_limit
_MAX_TIER = 2  # champion ControllerConfig.max_candidate_tier
_MAX_CLICKS_PER_TIER = 64  # champion ControllerConfig.max_clicks_per_tier
_FALLBACK_CLICK = (32, 32)
_GRID_SIZE = 64

_SIMPLE_ACTIONS = (1, 2, 3, 4, 5)
_CLICK_ACTION = 6
_RESET_ACTION = 0
_RESET_STEP = Step(action=_RESET_ACTION)

# Safety valves (stall/loop guards; not part of the preregistered budget).
_MAX_CONSECUTIVE_RESET_REJECTS = 3
_MAX_TARGET_DRIFTS = 3
_EMISSION_SCAN_LIMIT = 256


@dataclass
class _Node:
    """One reachable masked state: how to get there and what to try from it."""

    prefix: tuple[Step, ...]
    branches: tuple[Step, ...]
    next_branch: int = 0


@dataclass
class OnlineSearchLayer:
    """Budgeted online BFS with the FAP executor's seating protocol.

    IDLE by default: ``propose`` returns None and the host turn is
    byte-identical to a policy built without the layer. ENGAGED after the
    preregistered stuck signal: ``propose`` emits one search step per turn
    until the level falls, the state space is exhausted, or the 1,500-action
    budget is spent (permanent abstention for that level). A found program is
    banked keyed by its level-start fingerprint and re-executed directly if
    the game ever returns to a banked root.
    """

    # -- idle / engagement bookkeeping --------------------------------------
    _remaining_budget: int | None = None
    _observes_since_boundary: int = 0
    _engaged: bool = False
    _level_abstain: bool = False
    _abstain_reason: str | None = None
    _level_index: int = 0

    # -- passive timer-line learning (pre-engagement) -----------------------
    _timer_prev: NDArray[np.int16] | None = None
    _timer_row_changes: dict[int, int] = field(default_factory=dict)
    _timer_col_changes: dict[int, int] = field(default_factory=dict)
    _timer_effective: int = 0
    _mask_rows: tuple[int, ...] = ()
    _mask_cols: tuple[int, ...] = ()
    _mask_frozen: bool = False

    # -- last observation cache (observe precedes propose on each frame) ----
    _last_grid16: NDArray[np.int16] | None = None
    _last_legal: tuple[int, ...] = ()
    _last_fp: bytes | None = None

    # -- emission / swallow state -------------------------------------------
    _awaiting: Step | None = None
    _awaiting_kind: str | None = None
    _pre_emit_fp: bytes | None = None
    _retry_step: tuple[Step, str] | None = None
    _swallow_armed: bool = False
    _retried_swallow: bool = False
    _forced_reset_pending: bool = False
    _consecutive_reset_rejects: int = 0

    # -- the search tree -----------------------------------------------------
    _nodes: dict[bytes, _Node] = field(default_factory=dict)
    _queue: deque[bytes] = field(default_factory=deque)
    _root_fp: bytes | None = None
    _phase: str = "reset"
    _target_fp: bytes | None = None
    _replay_pos: int = 0
    _target_drifts: int = 0

    # -- banking / execution -------------------------------------------------
    _banked: dict[bytes, tuple[Step, ...]] = field(default_factory=dict)
    _exec_program: tuple[Step, ...] | None = None
    _exec_pos: int = 0
    _programs_found: int = 0
    _programs_executed: int = 0

    # -- budget and diagnostics ----------------------------------------------
    _actions_emitted: int = 0
    _replay_drifts: int = 0
    _root_mismatches: int = 0

    # ------------------------------------------------------------------ API

    @property
    def engaged(self) -> bool:
        return self._engaged

    @property
    def programs_found(self) -> int:
        return self._programs_found

    def observe(
        self, grid: NDArray[np.integer], legal_ids: Any = None
    ) -> None:
        """Record one active frame (and, while engaged, our step's result).

        The host passes the frame's legal-action ids alongside the grid; they
        are part of the preregistered state identity (frame + legal-mask
        hashing) and the source of branch legality.
        """

        grid16 = np.asarray(grid, dtype=np.int16).copy()
        if legal_ids is not None:
            self._last_legal = tuple(sorted({int(i) for i in legal_ids}))
        self._observes_since_boundary += 1
        if not self._mask_frozen:
            self._timer_learn(grid16)
        fp = self._fingerprint(grid16) if self._engaged else None
        if self._engaged:
            self._consume_engaged(fp, grid16)
        self._last_grid16 = grid16
        self._last_fp = fp

    def set_remaining_budget(self, remaining: int | None) -> None:
        """Host-supplied remaining action budget; None means uncapped."""

        self._remaining_budget = None if remaining is None else int(remaining)

    def propose(self, grid: NDArray[np.integer]) -> Step | None:
        """Return the next search step, or None to leave the champion alone.

        ASSUMPTION (labelled): the host calls observe() before propose() on
        the same frame, as the FAP seating already guarantees; the layer acts
        on what observe() recorded.
        """

        del grid
        if self._level_abstain:
            return None
        if not self._engaged:
            # PREREGISTERED stuck signal: 75 turns without a level advance.
            # observe() calls approximate reconciled turns (the layer cannot
            # see reconciliation); the counter restarts on level advances
            # only, because a forced reset is not an advance.
            if self._observes_since_boundary < STUCK_OBSERVE_TURNS:
                return None
            if (
                self._remaining_budget is not None
                and self._remaining_budget < ENGAGEMENT_MIN_REMAINING_BUDGET
            ):
                # Registered amendment: never start a search the host budget
                # cannot finish. Unknown budget (deployment) means uncapped.
                return None
            self._engage()
        if self._actions_emitted >= LEVEL_ACTION_BUDGET:
            # PREREGISTERED budget: permanent abstention for this level.
            self._exhaust_level("action-budget-exhausted")
            return None
        emission = self._next_emission()
        if emission is None:
            return None
        step, kind = emission
        self._awaiting = step
        self._awaiting_kind = kind
        self._pre_emit_fp = self._last_fp
        self._actions_emitted += 1
        return step

    def reject_last(self) -> None:
        """The host refused the last proposed step; it never executed."""

        step = self._awaiting
        kind = self._awaiting_kind
        self._awaiting = None
        self._awaiting_kind = None
        if step is None:
            return
        self._actions_emitted = max(0, self._actions_emitted - 1)
        if not self._engaged:
            return
        self._retry_step = None
        if kind == "reset":
            self._consecutive_reset_rejects += 1
            if self._consecutive_reset_rejects >= _MAX_CONSECUTIVE_RESET_REJECTS:
                # Without RESET the layer cannot replay at all: fail safe.
                self._exhaust_level("reset-rejected")
            return
        if kind == "expand":
            # Most likely hard-banned (graph-proven fatal): consume the
            # branch -- the game has not moved, so the next branch can go out
            # directly on the following turn.
            node = self._nodes.get(self._target_fp or b"")
            if node is not None:
                node.next_branch += 1
            return
        if kind == "replay":
            # The path to the target is refused on the live board: skip it.
            self._skip_target()
            self._phase = "reset"
            return
        if kind == "execute":
            if self._root_fp is not None:
                self._banked.pop(self._root_fp, None)
            self._exec_program = None
            self._phase = "reset"

    def notify_reset(self) -> None:
        """A FORCED reset ran (the layer's own resets do not arrive here).

        It does NOT restart the stuck counter: the preregistered signal is
        "no level advance for 75 reconciled turns", and a forced reset is not
        an advance. MEASURED 2026-09-30 (sp80, scratch policy loop): the
        champion dies every ~31 turns there, so a counter that restarted on
        forced resets would never engage at all.
        """

        self._timer_prev = None
        if not self._engaged:
            return
        step = self._awaiting
        kind = self._awaiting_kind
        self._awaiting = None
        self._awaiting_kind = None
        self._retry_step = None
        if step is not None and kind == "expand":
            # Our expansion killed the game: the branch is consumed and its
            # terminal child is not enqueued (mirrors the offline BFS, where
            # a GAME_OVER frame offers no further branches).
            node = self._nodes.get(self._target_fp or b"")
            if node is not None:
                node.next_branch += 1
        elif step is not None and kind in ("replay", "execute"):
            self._replay_drifts += 1
            if kind == "execute" and self._root_fp is not None:
                self._banked.pop(self._root_fp, None)
                self._exec_program = None
        # The forced RESET does the job our own RESET emission would have
        # done: the next observed frame is the level-start board.
        self._forced_reset_pending = True
        self._phase = "reset"

    def notify_level_advance(self) -> None:
        """The level fell: bank the program if our own step completed it."""

        step = self._awaiting
        kind = self._awaiting_kind
        if self._engaged and step is not None:
            if kind == "execute":
                self._programs_executed += 1
            else:
                program = self._program_from_awaiting(step, kind)
                if program is not None:
                    if self._root_fp is not None:
                        self._banked[self._root_fp] = program
                    self._programs_found += 1
        self._timer_prev = None
        self._observes_since_boundary = 0
        self._level_index += 1
        self._engaged = False
        self._level_abstain = False
        self._abstain_reason = None
        self._actions_emitted = 0
        self._awaiting = None
        self._awaiting_kind = None
        self._clear_tree()

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "online_search",
            "engaged": self._engaged,
            "phase": self._phase if self._engaged else None,
            "level_index": self._level_index,
            "actions_emitted": self._actions_emitted,
            "budget": LEVEL_ACTION_BUDGET,
            "level_abstain": self._level_abstain,
            "abstain_reason": self._abstain_reason,
            "nodes": len(self._nodes),
            "frontier": len(self._queue),
            "programs_found": self._programs_found,
            "programs_executed": self._programs_executed,
            "banked_programs": len(self._banked),
            "timer_mask_rows": list(self._mask_rows),
            "timer_mask_cols": list(self._mask_cols),
            "timer_effective_transitions": self._timer_effective,
            "replay_drifts": self._replay_drifts,
            "root_mismatches": self._root_mismatches,
            "fly_content": "none; engineered scaffold (H-ONLINE-SEARCH)",
        }

    # ------------------------------------------------------- engagement

    def _engage(self) -> None:
        self._engaged = True
        self._freeze_timer_mask()
        self._phase = "reset"
        self._awaiting = None
        self._awaiting_kind = None
        self._retry_step = None
        self._consecutive_reset_rejects = 0
        self._forced_reset_pending = False

    def _exhaust_level(self, reason: str) -> None:
        self._engaged = False
        self._level_abstain = True
        self._abstain_reason = reason
        self._awaiting = None
        self._awaiting_kind = None
        self._clear_tree()

    def _clear_tree(self) -> None:
        self._nodes = {}
        self._queue = deque()
        self._root_fp = None
        self._target_fp = None
        self._replay_pos = 0
        self._target_drifts = 0
        self._exec_program = None
        self._exec_pos = 0
        self._phase = "reset"
        self._retry_step = None
        self._swallow_armed = False
        self._retried_swallow = False
        self._forced_reset_pending = False

    # ------------------------------------------------- state identity

    def _fingerprint(self, grid16: NDArray[np.int16]) -> bytes:
        """BLAKE2b-128 over the timer-masked grid plus the legal-action mask,
        exactly as the offline instrument hashes states."""

        masked = grid16
        if self._mask_rows or self._mask_cols:
            masked = grid16.copy()
            if self._mask_rows:
                masked[list(self._mask_rows), :] = -1
            if self._mask_cols:
                masked[:, list(self._mask_cols)] = -1
        legal = bytes(1 if i in self._last_legal else 0 for i in range(7))
        return hashlib.blake2b(masked.tobytes() + legal, digest_size=16).digest()

    def _ignored_mask(self) -> NDArray[np.bool_] | None:
        if not self._mask_rows and not self._mask_cols:
            return None
        mask = np.zeros((_GRID_SIZE, _GRID_SIZE), dtype=np.bool_)
        if self._mask_rows:
            mask[list(self._mask_rows), :] = True
        if self._mask_cols:
            mask[:, list(self._mask_cols)] = True
        return mask

    # ------------------------------------------------- timer-line learning

    def _timer_learn(self, grid16: NDArray[np.int16]) -> None:
        """Port of the instrument's border-line rule, fed passively.

        ASSUMPTION (labelled): the champion's own pre-engagement transitions
        stand in for the instrument's 24-step seeded random walk. The rule is
        unchanged -- border lines (outer 4) changing in >= 60% of effective
        transitions, minimum 4 -- computed over every transition seen before
        the first engagement rather than exactly 24 sampled steps. Checked by
        comparing the frozen mask against the instrument's per-game masks;
        breaks state dedup (more states, slower search) if wrong, never
        correctness.
        """

        previous = self._timer_prev
        self._timer_prev = grid16
        if previous is None:
            return
        diff = previous != grid16
        if not diff.any():
            return
        self._timer_effective += 1
        for index in range(_GRID_SIZE):
            if index >= TIMER_BORDER_WIDTH and index < _GRID_SIZE - TIMER_BORDER_WIDTH:
                continue
            if diff[index, :].any():
                self._timer_row_changes[index] = self._timer_row_changes.get(index, 0) + 1
            if diff[:, index].any():
                self._timer_col_changes[index] = self._timer_col_changes.get(index, 0) + 1

    def _freeze_timer_mask(self) -> None:
        if self._mask_frozen:
            return
        self._mask_frozen = True
        effective = self._timer_effective
        if effective < TIMER_MIN_CHANGES:
            return
        threshold = max(TIMER_MIN_CHANGES, ceil(TIMER_CHANGE_FRACTION * effective))
        self._mask_rows = tuple(
            index
            for index in sorted(self._timer_row_changes)
            if self._timer_row_changes[index] >= threshold
        )
        self._mask_cols = tuple(
            index
            for index in sorted(self._timer_col_changes)
            if self._timer_col_changes[index] >= threshold
        )

    # ------------------------------------------------- click branching

    def _branches(self, grid16: NDArray[np.int16]) -> tuple[Step, ...]:
        legal = self._last_legal
        out = [Step(action=i) for i in _SIMPLE_ACTIONS if i in legal]
        if _CLICK_ACTION in legal:
            out.extend(self._derive_clicks(grid16))
        return tuple(out)

    def _derive_clicks(self, grid16: NDArray[np.int16]) -> list[Step]:
        """Scene-component click candidates, exactly as the instrument: the
        champion's own scene machinery, ranked (tier asc, area desc, emission
        order), capped at the preregistered 12."""

        ignored = self._ignored_mask()
        background = infer_background(grid16, ignored_mask=ignored)
        components = components_for_coverage(
            extract_components(
                grid16,
                background_color=background,
                ignored_mask=ignored,
                minimum_area=1,
            ),
            limit=_COMPONENT_LIMIT,
        )
        candidates = component_click_candidates(
            components,
            max_tier=_MAX_TIER,
            max_clicks_per_tier=_MAX_CLICKS_PER_TIER,
        )
        if not candidates:
            # Last-resort centre click on a uniform scene, as the policy does.
            return [Step(action=_CLICK_ACTION, x=_FALLBACK_CLICK[0], y=_FALLBACK_CLICK[1])]
        area = {component.index: component.area for component in components}
        ranked = sorted(candidates, key=lambda c: (c.tier, -area[c.component_index]))
        return [
            Step(action=_CLICK_ACTION, x=candidate.x, y=candidate.y)
            for candidate in ranked[:CLICK_CAP]
        ]

    # ------------------------------------------------- engaged bookkeeping

    def _consume_engaged(self, fp: bytes, grid16: NDArray[np.int16]) -> None:
        if self._forced_reset_pending:
            self._forced_reset_pending = False
            self._arrive_at_root(fp, grid16)
            return
        step = self._awaiting
        kind = self._awaiting_kind
        if step is None:
            # A frame the layer did not cause (the FAP or the champion acted
            # after a rejection): any traversal in progress was built on a
            # board that has now moved. Restart from a fresh RESET.
            self._phase = "reset"
            self._retry_step = None
            return
        self._awaiting = None
        self._awaiting_kind = None
        self._consecutive_reset_rejects = 0
        if kind == "reset":
            self._arrive_at_root(fp, grid16)
            return
        changed = fp != self._pre_emit_fp
        if not changed and self._swallow_armed and not self._retried_swallow:
            # Measured engine quirk (sc25 2026-09-27; g50t 2026-09-30): the
            # first action after a RESET can be swallowed completely. Probe
            # once, as the offline instrument does: re-emit the same step.
            self._retried_swallow = True
            self._retry_step = (step, kind)
            return
        self._swallow_armed = False
        if kind == "replay":
            node = self._nodes.get(self._target_fp or b"")
            self._replay_pos += 1
            if node is not None and self._replay_pos >= len(node.prefix):
                if fp == self._target_fp:
                    self._phase = "expand"
                    self._target_drifts = 0
                else:
                    # DECLARED LIMITATION (ported): replay assumes RESET
                    # restores the initial frame exactly; count the drift
                    # and retry, dropping the node after repeated failures.
                    self._replay_drifts += 1
                    self._target_drifts += 1
                    if self._target_drifts >= _MAX_TARGET_DRIFTS:
                        self._skip_target()
                    self._phase = "reset"
            return
        if kind == "expand":
            parent = self._nodes.get(self._target_fp or b"")
            if parent is not None:
                parent.next_branch += 1
                if fp not in self._nodes:
                    prefix = (*parent.prefix, step)
                    branches: tuple[Step, ...] = ()
                    if len(prefix) < DEPTH_LIMIT:
                        branches = self._branches(grid16)
                    self._nodes[fp] = _Node(prefix=prefix, branches=branches)
                    if branches:
                        self._queue.append(fp)
            self._next_traversal(fp)
            return
        if kind == "execute":
            self._exec_pos += 1
            if self._exec_program is not None and self._exec_pos >= len(self._exec_program):
                # The banked program ran to its end without the level falling
                # (notify_level_advance would have disengaged us): the bank
                # is stale for this board. Drop it and explore instead.
                if self._root_fp is not None:
                    self._banked.pop(self._root_fp, None)
                self._exec_program = None
                self._phase = "reset"

    def _arrive_at_root(self, fp: bytes, grid16: NDArray[np.int16]) -> None:
        self._swallow_armed = True
        self._retried_swallow = False
        self._retry_step = None
        if self._root_fp is None:
            self._root_fp = fp
        elif fp != self._root_fp:
            # DECLARED LIMITATION (ported): reset fidelity is assumed, as the
            # forensics measured; a mismatch is counted, not recovered from.
            self._root_mismatches += 1
        if fp not in self._nodes:
            node = _Node(prefix=(), branches=self._branches(grid16))
            self._nodes[fp] = node
            if node.branches:
                self._queue.append(fp)
        banked = self._banked.get(fp)
        if banked and self._exec_program is None:
            # EXECUTION mode: the level starting here has a banked program.
            self._exec_program = banked
            self._exec_pos = 0
            self._phase = "execute"
            return
        self._next_traversal(fp)

    def _next_traversal(self, current_fp: bytes | None) -> None:
        while self._queue:
            head = self._queue[0]
            node = self._nodes[head]
            if node.next_branch < len(node.branches):
                if head != self._target_fp:
                    self._target_drifts = 0
                self._target_fp = head
                self._replay_pos = 0
                if current_fp == head:
                    # Already at the frontier node under the search's own
                    # state identity: no replay is needed. This continuation
                    # is what keeps no-op-heavy boards inside the budget.
                    self._phase = "expand"
                elif current_fp is not None and current_fp == self._root_fp:
                    self._phase = "replay"
                else:
                    self._phase = "reset"
                return
            self._queue.popleft()
        # Every reachable masked state within the depth limit is expanded:
        # the offline instrument's "state-space-exhausted" outcome.
        self._exhaust_level("state-space-exhausted")

    def _skip_target(self) -> None:
        node = self._nodes.get(self._target_fp or b"")
        if node is not None:
            node.next_branch = len(node.branches)
        self._target_drifts = 0

    def _program_from_awaiting(self, step: Step, kind: str | None) -> tuple[Step, ...] | None:
        node = self._nodes.get(self._target_fp or b"")
        if kind == "expand" and node is not None:
            return (*node.prefix, step)
        if kind == "replay" and node is not None:
            return node.prefix[: self._replay_pos + 1]
        return None

    # ------------------------------------------------- emission selection

    def _is_legal(self, step: Step) -> bool:
        if step.action == _RESET_ACTION:
            # MEASURED 2026-09-30 (offline arcade probe, cd82): the engine
            # accepts action 0 on active frames while never listing it in
            # available_actions, so the mask check cannot apply to it.
            return True
        if step.action not in self._last_legal:
            return False
        if step.action == _CLICK_ACTION:
            return (
                step.x is not None
                and step.y is not None
                and 0 <= int(step.x) < _GRID_SIZE
                and 0 <= int(step.y) < _GRID_SIZE
            )
        return True

    def _next_emission(self) -> tuple[Step, str] | None:
        if self._retry_step is not None:
            step, kind = self._retry_step
            self._retry_step = None
            return step, kind
        for _ in range(_EMISSION_SCAN_LIMIT):
            if self._level_abstain or not self._engaged:
                return None
            if self._phase == "reset":
                return _RESET_STEP, "reset"
            if self._phase == "execute":
                program = self._exec_program
                if program is None or self._exec_pos >= len(program):
                    self._exec_program = None
                    self._phase = "reset"
                    continue
                step = program[self._exec_pos]
                if not self._is_legal(step):
                    # The banked program no longer fits this board.
                    if self._root_fp is not None:
                        self._banked.pop(self._root_fp, None)
                    self._exec_program = None
                    self._phase = "reset"
                    continue
                return step, "execute"
            node = self._nodes.get(self._target_fp or b"")
            if self._phase == "replay":
                if node is None:
                    self._phase = "reset"
                    continue
                if self._replay_pos >= len(node.prefix):
                    self._phase = "expand"
                    continue
                step = node.prefix[self._replay_pos]
                if not self._is_legal(step):
                    self._skip_target()
                    self._phase = "reset"
                    continue
                return step, "replay"
            if self._phase == "expand":
                if node is None or node.next_branch >= len(node.branches):
                    self._next_traversal(self._last_fp)
                    continue
                step = node.branches[node.next_branch]
                if not self._is_legal(step):
                    node.next_branch += 1  # a branch the live board refuses
                    continue
                return step, "expand"
            return None
        # Scan stalled without an emittable step: abstain this turn; the
        # traversal restarts from a RESET on the next one.
        self._phase = "reset"
        return None


__all__ = [
    "CLICK_CAP",
    "DEPTH_LIMIT",
    "LEVEL_ACTION_BUDGET",
    "STUCK_OBSERVE_TURNS",
    "OnlineSearchLayer",
    "Step",
]
