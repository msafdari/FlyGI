"""Exact-state graph and generic cross-level effect-model contracts."""

from __future__ import annotations

import math

import pytest

from flygi.controller.state_graph import (
    ActionCandidate,
    EffectModel,
    ReplayStep,
    StateCollisionError,
    StateGraph,
    StateGraphError,
)


def _state(
    graph: StateGraph,
    name: str,
    candidates: tuple[ActionCandidate, ...] = (),
) -> bytes:
    canonical = name.encode("ascii")
    key = graph.state_key(canonical)
    graph.upsert_state(key, canonical, candidates)
    return key


def _record(
    graph: StateGraph,
    source: bytes,
    candidate: ActionCandidate,
    destination: bytes | None,
    *,
    changed: bool = True,
    novel: bool = False,
    fatal: bool = False,
    advanced: bool = False,
):
    return graph.record_transition(
        source,
        candidate,
        destination,
        changed=changed,
        novel=novel,
        fatal=fatal,
        advanced=advanced,
    )


def test_action_candidate_is_validated_ordered_and_serialized_canonically() -> None:
    simple = ActionCandidate(2)
    earlier = ActionCandidate(1)
    click_a = ActionCandidate(6, x=3, y=7)
    click_b = ActionCandidate(6, x=3, y=8)

    assert sorted((click_b, simple, click_a, earlier)) == [
        earlier,
        simple,
        click_a,
        click_b,
    ]
    assert simple.payload == {}
    assert click_a.payload == {"x": 3, "y": 7}
    assert ActionCandidate.from_bytes(simple.to_bytes()) == simple
    assert ActionCandidate.from_bytes(click_a.to_bytes()) == click_a

    with pytest.raises(ValueError, match="RESET"):
        ActionCandidate(0)
    with pytest.raises(ValueError, match="both x and y"):
        ActionCandidate(6)
    with pytest.raises(ValueError, match="only ACTION6"):
        ActionCandidate(2, x=1, y=1)
    with pytest.raises(ValueError, match="canonical"):
        ActionCandidate.from_bytes(bytes((2, 1, 1)))


def test_state_visits_merge_candidate_expansion_and_verify_collisions() -> None:
    graph = StateGraph()
    first = ActionCandidate(1)
    second = ActionCandidate(2)
    key = b"compact-key"

    node = graph.upsert_state(key, b"exact pixels and mask", (first,))
    same_node = graph.upsert_state(key, b"exact pixels and mask", (second,))

    assert same_node is node
    assert node.visits == 2
    assert node.ordered_candidates == (first, second)
    with pytest.raises(StateCollisionError, match="collision"):
        graph.upsert_state(key, b"different exact state")


def test_no_ops_are_counted_and_nondeterministic_edges_are_not_replayed() -> None:
    graph = StateGraph()
    candidate = ActionCandidate(1)
    source = _state(graph, "source", (candidate,))
    other = _state(graph, "other")

    stats = _record(
        graph,
        source,
        candidate,
        source,
        changed=False,
        novel=False,
    )
    assert stats.attempts == 1
    assert stats.no_op_count == 1
    assert stats.deterministic_destination == source
    assert graph.safe_replay_edges(source) == (ReplayStep(source, candidate, source),)

    _record(graph, source, candidate, other, changed=True, novel=True)
    assert stats.attempts == 2
    assert stats.changed_count == 1
    assert stats.novel_count == 1
    assert stats.destination_counts == tuple(sorted(((source, 1), (other, 1))))
    assert stats.deterministic_destination is None
    assert graph.safe_replay_edges(source) == ()


def test_fatal_bans_are_exact_state_local_and_never_safe_replay_edges() -> None:
    graph = StateGraph()
    candidate = ActionCandidate(4)
    first = _state(graph, "first", (candidate,))
    second = _state(graph, "second", (candidate,))

    stats = _record(
        graph,
        first,
        candidate,
        None,
        changed=False,
        fatal=True,
    )

    assert stats.fatal_count == 1
    assert candidate in graph.node(first).hard_bans
    assert candidate not in graph.node(second).hard_bans
    assert graph.node(second).frontier_candidates == (candidate,)
    assert graph.safe_replay_edges(first) == ()


def test_bfs_crosses_cycles_in_forward_direction_and_returns_exact_replay_steps() -> None:
    graph = StateGraph()
    a_to_b = ActionCandidate(1)
    b_to_a = ActionCandidate(2)
    b_to_c = ActionCandidate(3)
    unexplored = ActionCandidate(4)
    a = _state(graph, "a", (a_to_b,))
    b = _state(graph, "b", (b_to_a, b_to_c))
    c = _state(graph, "c", (unexplored,))

    _record(graph, a, a_to_b, b)
    _record(graph, b, b_to_a, a)
    _record(graph, b, b_to_c, c)

    assert graph.nearest_reachable_frontier(a) == (
        ReplayStep(a, a_to_b, b),
        ReplayStep(b, b_to_c, c),
    )
    assert graph.nearest_reachable_frontier(c) == ()

    # Once C's only frontier is consumed, it cannot infer reverse edges back to
    # A even if A later gains a new candidate.
    _record(graph, c, unexplored, c, changed=False)
    graph.merge_candidates(a, (ActionCandidate(5),))
    assert graph.nearest_reachable_frontier(c) is None


def test_bfs_chooses_a_nearest_frontier_with_deterministic_tie_order() -> None:
    graph = StateGraph()
    to_b = ActionCandidate(1)
    to_c = ActionCandidate(2)
    b_frontier = ActionCandidate(3)
    c_frontier = ActionCandidate(4)
    a = _state(graph, "a", (to_b, to_c))
    b = _state(graph, "b", (b_frontier,))
    c = _state(graph, "c", (c_frontier,))

    _record(graph, a, to_b, b)
    _record(graph, a, to_c, c)

    assert graph.nearest_reachable_frontier(a) == (ReplayStep(a, to_b, b),)


def test_nonfatal_transition_requires_a_registered_destination() -> None:
    graph = StateGraph()
    candidate = ActionCandidate(1)
    source = _state(graph, "source", (candidate,))

    with pytest.raises(StateGraphError, match="destination"):
        _record(graph, source, candidate, None, fatal=False)
    with pytest.raises(StateGraphError, match="registered"):
        _record(graph, source, candidate, b"unknown", fatal=False)


def test_effect_model_learns_simple_effect_novelty_advancement_and_soft_death() -> None:
    model = EffectModel()
    productive = ActionCandidate(1)
    dangerous = ActionCandidate(2)
    prior = model.priority(productive)

    for _ in range(4):
        model.observe(
            productive,
            effect=True,
            novel=True,
            fatal=False,
            advanced=True,
        )
        model.observe(
            dangerous,
            effect=False,
            novel=False,
            fatal=True,
            advanced=False,
        )

    productive_estimate = model.estimate(productive)
    dangerous_estimate = model.estimate(dangerous)
    assert productive_estimate.effect_probability > 0.5
    assert productive_estimate.novelty_probability > 0.5
    assert productive_estimate.advancement_probability > 0.5
    assert productive_estimate.priority > prior
    assert dangerous_estimate.fatal_probability > 0.5
    assert dangerous_estimate.priority < prior
    assert math.isfinite(dangerous_estimate.priority)
    assert model.observation_count == 8


def test_click_effects_generalize_by_observed_color_and_coarse_region() -> None:
    model = EffectModel(coarse_region_bins=4)
    observed = ActionCandidate(6, x=5, y=5)
    same_color = ActionCandidate(6, x=40, y=40)
    same_region = ActionCandidate(6, x=10, y=10)
    unrelated = ActionCandidate(6, x=50, y=10)
    prior = model.priority(unrelated, clicked_color=4)

    for _ in range(6):
        model.observe(
            observed,
            clicked_color=3,
            effect=True,
            novel=True,
            fatal=False,
            advanced=False,
        )

    assert model.priority(same_color, clicked_color=3) > prior
    assert model.priority(same_region, clicked_color=4) > prior
    assert model.priority(unrelated, clicked_color=4) == pytest.approx(prior)
    assert model.observation_count == 6


def test_effect_model_persists_across_levels_and_resets_only_for_a_new_game() -> None:
    model = EffectModel()
    candidate = ActionCandidate(7)
    model.start_level()
    model.observe(
        candidate,
        effect=True,
        novel=True,
        fatal=False,
        advanced=False,
    )
    learned = model.estimate(candidate)

    model.start_level()
    assert model.levels_started == 2
    assert model.estimate(candidate) == learned
    assert model.observation_count == 1

    model.reset_game()
    reset = model.estimate(candidate)
    assert model.levels_started == 0
    assert model.observation_count == 0
    assert reset.evidence == 0.0
    assert reset.effect_probability == 0.5
    assert reset != learned


def test_effect_model_optimism_bonus_decays_with_evidence() -> None:
    model = EffectModel(
        effect_weight=0.0,
        novelty_weight=0.0,
        advancement_bonus=0.0,
        death_penalty=0.0,
        exploration_bonus=1.0,
    )
    candidate = ActionCandidate(3)
    untried = model.estimate(candidate)

    for _ in range(8):
        model.observe(
            candidate,
            effect=False,
            novel=False,
            fatal=False,
            advanced=False,
        )

    tried = model.estimate(candidate)
    assert untried.evidence == 0.0
    assert untried.exploration_bonus == 1.0
    assert tried.evidence == 8.0
    assert tried.exploration_bonus == pytest.approx(1.0 / 3.0)
    assert tried.priority < untried.priority
