"""Configuration loading for the versioned FlyGI build and runtime pipeline."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when a configuration cannot be interpreted safely."""


@dataclass(frozen=True)
class SourceConfig:
    url: str
    sha256: str | None = None


@dataclass(frozen=True)
class DataConfig:
    release: str = "male-cns:v1.0"
    weights_path: Path = Path("data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather")
    annotations_path: Path = Path("data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather")
    neurotransmitters_path: Path = Path("data/raw/body-neurotransmitters-male-cns-v1.0.feather")
    output_dir: Path = Path("data/processed/male-cns-v1.0")
    manifest_dir: Path = Path("data/manifests")
    sources: Mapping[str, SourceConfig] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphConfig:
    matrix_convention: str = "W[post_index, pre_index]"
    output_dir: Path = Path("data/processed/male-cns-v1.0")
    weight_transform: str = "log1p"
    sign_mode: str = "unsigned"
    modulator_treatment: str = "zero"
    unknown_transmitter_treatment: str = "zero"
    normalization: str = "incoming_l1"
    spectral_radius: float | None = None
    epsilon: float = 1e-8
    allow_self_edges: bool = True
    node_filter_column: str | None = None
    node_filter_values: tuple[object, ...] | None = None
    body_id_dtype: str = "uint64"
    weight_dtype: str = "float32"


@dataclass(frozen=True)
class DynamicsConfig:
    backend: str = "rate"
    execution_backend: str = "scipy-csr-cpu"
    activation: str = "tanh"
    internal_steps: int = 2
    leak: float = 0.3
    recurrent_gain: float = 0.9
    bias: float = 0.0
    frozen_graph: bool = True
    initial_state: str = "zeros"
    state_dtype: str = "float32"


def _optional_int(value: object, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{name} must be an integer or null")
    return int(value)


@dataclass(frozen=True)
class EncoderConfig:
    """Declared, nonlearned ARC-to-sensory interface."""

    kind: str = "sparse_projection"
    sensory_superclass: str = "ol_sensory"
    connections_per_neuron: int = 64
    input_scale: float = 1.0
    trainable: bool = False
    per_game_rules: bool = False
    # Retinotopic encoder only. Channel assignment is a declared heuristic,
    # not a physiological claim, so it lives here to be varied and ablated.
    on_types: tuple[str, ...] = ()
    off_types: tuple[str, ...] = ()
    change_types: tuple[str, ...] = ()
    change_gain: float = 1.0
    # Falsification control for the retinotopic_colour encoder's largest
    # ASSUMPTION: colour c drives medulla type index c % 15, a coding convention
    # with no biological motivation. A seed here permutes which type carries
    # which colour, keeping the collision structure and everything else fixed.
    # If a permuted assignment scores the same, the specific mapping carries
    # nothing and only categorical-plus-retinotopic structure matters.
    colour_permutation_seed: int | None = None
    # HYPOTHESIS H-MB-INPUT-BUS (assumption G): present the screen's colour
    # composition to the antennal lobe as an odour mixture, driving the 627
    # uniglomerular projection neurons whose 22,581 direct synapses reach 94%
    # of Kenyon cells. ARC has no odours; this is a declared invention about
    # the mushroom body as associative memory, never a claim about olfaction.
    mb_input_bus: str | None = None
    mb_input_scale: float = 1.0
    # HYPOTHESIS H-EFFERENCE: deliver the agent's previous action to Johnston's
    # organ (672 antennal mechanosensory neurons) so the circuits that read
    # state -- including the forward model and the mushroom body -- know what
    # the agent just did. Measured: the bio-eye encoder reads only the grid,
    # so without this the agent is blind to its own actions.
    efference_copy: str | None = None
    efference_scale: float = 1.0


@dataclass(frozen=True)
class DecoderConfig:
    """Declared, nonlearned readout-to-action interface."""

    kind: str = "literal"
    readout: str = "descending_neurons"
    # Where click coordinates come from. "readout_blocks" is the deployed
    # head: axis scores from body-id-ordered blocks of the readout, measured
    # at 23.5-cell localization error (chance is 37.2). "retinotopic_state"
    # reads |state change| back through the optic-lobe column map (measured
    # 0.8 cells); "retinotopic_surprise" reads |state - expectation| where
    # the expectation is the frozen connectome advanced on the previous
    # frame -- its own forward model, zero trained parameters, one extra
    # network advance per turn (H-RETINO-DECODER).
    coordinate_source: str = "readout_blocks"
    # HYPOTHESIS H-RECLICK-SEAT (constants frozen in EXPERIMENTS.yaml before
    # implementation): a per-game coordinate memory written after each click --
    # "surprise" deposits the fly forward-model's surprise at the clicked
    # coordinate, "griddiff" (the trivial-alternative writer) deposits the raw
    # change-mask mass -- and preference() pays a bonus for returning there.
    # Encodes the measured 29/38 re-click clearing regularity into the seat.
    reclick_memory: str = "none"
    action_slots: int = 8
    coordinate_head: str = "literal_factorized_bins"
    sampling_method: str = "zscore_softmax_categorical"
    action_temperature: float = 0.15
    coordinate_temperature: float = 0.2
    decision_seed_policy: str = "explicit_per_policy_or_config_derived"
    coordinate_fallback: str = "novelty_centroid"
    unchanged_click_exploration: str = "seeded_untried_uniform"
    readout_normalization: str = "adaptive"
    adaptation_rate: float = 0.1
    clip: float = 10.0
    loop_escape_enabled: bool = False
    loop_escape_exploration_bonus: float = 0.0
    loop_escape_unchanged_failure_penalty: float = 0.0
    loop_escape_state_hash: str = "blake2b_128"
    loop_escape_coordinate_memory: str = "per_observation"
    trainable: bool = False


@dataclass(frozen=True)
class PlasticityConfig:
    """Reward-modulated plasticity at Kenyon-cell-to-MBON synapses.

    Disabled by default. Every pre-existing config and every recorded result
    therefore describes a fully frozen graph, and enabling this is an explicit,
    recorded decision rather than a drift in defaults.
    """

    enabled: bool = False
    site: str = "kenyon_cell_to_mbon"
    learning_rate: float = 0.05
    decay: float = 0.01
    weight_ceiling_scale: float = 2.0
    reward_scale: float = 1.0
    reward_source: str = "observation_change"
    level_reward: float = 1.0
    reset_on_new_environment: bool = True
    rewire_mushroom_body_seed: int | None = None


@dataclass(frozen=True)
class StateLifetimeConfig:
    """Declared lifetime of the persistent connectome state."""

    reset_on_new_environment: bool = True
    preserve_across_levels: bool = True
    preserve_across_actions: bool = True
    preserve_after_game_over_reset: bool = True


@dataclass(frozen=True)
class ControllerConfig:
    """Generic online state/effect controller, disabled for frozen baselines.

    The controller is deliberately configured beside the connectome rather
    than smuggled into its decoder.  Historical literal-policy configs omit
    this section and therefore remain byte-for-byte behaviorally unchanged.
    """

    enabled: bool = False
    kind: str = "state_graph"
    state_hash: str = "blake2b_128"
    mask_freeze_after: int = 8
    volatile_threshold: float = 0.25
    volatile_min_changes: int = 2
    ui_border_width: int = 4
    component_min_area: int = 1
    component_limit: int = 64
    coarse_cell_size: int = 8
    max_candidate_tier: int = 2
    max_clicks_per_tier: int = 64
    effect_exploration_bonus: float = 1.5
    advancement_bonus: float = 0.6
    death_penalty: float = 0.4
    replan_cooldown: int = 3
    # HYPOTHESIS H-MB-LEARNING-DENSE. The fair null was measured under a 31:1
    # punishment-dominated, ~8-events-per-episode teaching signal. This routes
    # the controller's per-turn outcomes to dopamine as well: a NOVEL
    # destination (canonical graph novelty AND a changed frame) sends a small
    # reward to PAM, a NOOP a small punishment to PPL1, familiar EFFECTs send
    # nothing. MEASURED before implementation (2026-09-24): change-gated
    # novelty is action-dependent at p<0.05 on 64/75 rows (binomial null 3.8).
    # Dense drive is budgeted: dense_budget terminal-equivalents per game,
    # split evenly between valences with hard per-side caps, so ~500 dense
    # events cannot sweep weights to the clip band.
    dense_reinforcement: bool = False
    dense_budget: float = 2.0
    # HYPOTHESIS H-CONSEQUENCE-COUPLING (EXPERIMENTS.yaml, premise measured
    # 2026-09-24): an online logistic head over LOCAL click-patch content,
    # seated in the PRIMARY ranking term. "none" is byte-identical to the
    # champion. "retinotopic" reads the patch through the fly's compiled
    # cell->column map (the load-bearing element under test);
    # "retinotopic_permuted", "pixel_patch" and "rote" are its preregistered
    # controls. weight is in the priority+exploration scale; the bonus is
    # weight*(2p-1), zero until the head has seen outcomes.
    click_head: str = "none"
    click_head_weight: float = 1.0
    click_head_learning_rate: float = 0.3
    click_head_seed: int = 20260924
    # HYPOTHESIS (calibration, registered 2026-09-24): the first treatment
    # arm's breadth loss came from the SUPPRESSION side of the bonus.
    # negative_scale 1.0 keeps the symmetric bonus; 0.0 is boost-only --
    # the head may promote predicted-changers, never demote an untried
    # click below its normal exploration rank.
    click_head_negative_scale: float = 1.0
    # HYPOTHESIS (deadline-fallback, registered 2026-09-24 evening): head
    # bonus active only while turns-since-last-level-advance < deadline.
    # 0 = no deadline (always active; preserves every prior arm). D=100
    # preregistered from measured payoff steps (all head wins by step 56).
    click_head_deadline: int = 0
    # HYPOTHESIS (defragmentation, registered 2026-09-25): similarity-aware
    # novelty via locality-sensitive state tags. "none" is byte-identical.
    # A new-but-tag-similar state reads as familiar for LEARNING signals
    # (novelty posterior, dense reinforcement) while graph bookkeeping stays
    # exact. "retino_tags_permuted" is the fly-attribution control.
    state_similarity: str = "none"
    state_similarity_threshold: float = 0.9


@dataclass(frozen=True)
class CircuitConfig:
    """Declared, anatomy-targeted circuit calibrations.

    Each field names a specific pathway measured in the graph and scales it for
    a stated physiological reason. This is the sanctioned alternative to global
    knobs: WORKLOG section 9 showed no global gain delivers both biological KC
    sparsity and a readout clear of the numerical floor, because KC->KC
    recurrence (85.3% of KC input) swamps APL inhibition (2.4%).
    """

    # HYPOTHESIS H-APL: strengthening the fly's own sparsification circuit --
    # the GABAergic APL neuron's 4,633 inhibitory synapses onto Kenyon cells,
    # the complete KC->APL->KC negative feedback loop measured present and
    # correctly signed in this graph -- restores biological KC sparsity
    # (0.05-0.11 active) where global gain provably cannot. Literature: Lin et
    # al. 2014 showed disrupting this loop destroys sparse coding and
    # discrimination of similar stimuli. 1.0 means anatomy as measured.
    apl_to_kc_gain: float = 1.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.apl_to_kc_gain) or self.apl_to_kc_gain <= 0:
            raise ConfigError("circuit.apl_to_kc_gain must be finite and positive")


@dataclass(frozen=True)
class FlyGIConfig:
    schema_version: int
    seed: int
    data: DataConfig
    graph: GraphConfig
    dynamics: DynamicsConfig
    encoder: EncoderConfig = field(default_factory=EncoderConfig)
    decoder: DecoderConfig = field(default_factory=DecoderConfig)
    state: StateLifetimeConfig = field(default_factory=StateLifetimeConfig)
    plasticity: PlasticityConfig = field(default_factory=PlasticityConfig)
    controller: ControllerConfig = field(default_factory=ControllerConfig)
    circuit: CircuitConfig = field(default_factory=CircuitConfig)
    groups: Mapping[str, Any] = field(default_factory=dict)
    future: Mapping[str, Any] = field(default_factory=dict)


def _mapping(value: object, name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a mapping")
    return dict(value)


def load_config(path: str | Path) -> FlyGIConfig:
    """Load Milestone 0-1 settings while preserving declared future sections."""

    config_path = Path(path).resolve()
    path_base = (
        config_path.parent.parent if config_path.parent.name == "configs" else config_path.parent
    )

    def resolved_path(value: object) -> Path:
        candidate = Path(value)
        return candidate if candidate.is_absolute() else path_base / candidate

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"could not read config {config_path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {config_path}: {exc}") from exc

    root = _mapping(raw, "configuration")
    schema_version = int(root.pop("schema_version", 1))
    if schema_version != 1:
        raise ConfigError(f"unsupported schema_version {schema_version}; expected 1")
    experiment = _mapping(root.pop("experiment", None), "experiment")
    legacy_seed = root.pop("seed", 20260919)
    seed = int(experiment.pop("seed", legacy_seed))
    data_raw = _mapping(root.pop("data", None), "data")
    graph_raw = _mapping(root.pop("graph", None), "graph")
    dynamics_raw = _mapping(root.pop("dynamics", None), "dynamics")
    groups = _mapping(root.pop("groups", None), "groups")

    source_raw = _mapping(
        data_raw.pop("sources", root.pop("source_catalog", None)),
        "source_catalog",
    )
    sources: dict[str, SourceConfig] = {}
    for source_name, source_value in source_raw.items():
        source = _mapping(source_value, f"data.sources.{source_name}")
        if "url" not in source:
            raise ConfigError(f"data.sources.{source_name}.url is required")
        digest = source.pop("sha256", None)
        sources[source_name] = SourceConfig(
            url=str(source.pop("url")),
            sha256=None if digest is None else str(digest),
        )
        if source:
            raise ConfigError(f"unknown data.sources.{source_name} keys: {sorted(source)}")

    graph_contract = _mapping(root.pop("graph_contract", None), "graph_contract")
    for key, value in graph_contract.items():
        if key in graph_raw and graph_raw[key] != value:
            raise ConfigError(f"conflicting graph and graph_contract value for {key}")
        graph_raw[key] = value

    raw_dir_value = data_raw.pop("raw_dir", None)
    raw_dir = resolved_path(raw_dir_value if raw_dir_value is not None else "data/raw")
    try:
        data = DataConfig(
            release=str(data_raw.pop("release", "male-cns:v1.0")),
            weights_path=resolved_path(
                data_raw.pop(
                    "weights_path",
                    raw_dir / "connectome-weights-male-cns-v1.0-minconf-0.5.feather",
                )
            ),
            annotations_path=resolved_path(
                data_raw.pop(
                    "annotations_path",
                    raw_dir / "body-annotations-male-cns-v1.0-minconf-0.5.feather",
                )
            ),
            neurotransmitters_path=resolved_path(
                data_raw.pop(
                    "neurotransmitters_path",
                    raw_dir / "body-neurotransmitters-male-cns-v1.0.feather",
                )
            ),
            output_dir=resolved_path(data_raw.pop("output_dir", "data/processed/male-cns-v1.0")),
            manifest_dir=resolved_path(data_raw.pop("manifest_dir", "data/manifests")),
            sources=sources,
        )
        node_filter_column_raw = graph_raw.pop("node_filter_column", None)
        node_filter_values_raw = graph_raw.pop("node_filter_values", None)
        if node_filter_values_raw is not None and not isinstance(
            node_filter_values_raw, (list, tuple)
        ):
            raise ConfigError("graph.node_filter_values must be a list or null")
        graph = GraphConfig(
            matrix_convention=str(graph_raw.pop("matrix_convention", "W[post_index, pre_index]")),
            output_dir=resolved_path(graph_raw.pop("output_dir", "data/processed/male-cns-v1.0")),
            weight_transform=str(graph_raw.pop("weight_transform", "log1p")),
            sign_mode=str(graph_raw.pop("sign_mode", "unsigned")),
            modulator_treatment=str(graph_raw.pop("modulator_treatment", "zero")),
            unknown_transmitter_treatment=str(
                graph_raw.pop("unknown_transmitter_treatment", "zero")
            ),
            normalization=str(graph_raw.pop("normalization", "incoming_l1")),
            spectral_radius=(
                None
                if graph_raw.get("spectral_radius") is None
                else float(graph_raw["spectral_radius"])
            ),
            epsilon=float(graph_raw.pop("epsilon", 1e-8)),
            allow_self_edges=bool(graph_raw.pop("allow_self_edges", True)),
            node_filter_column=(
                None if node_filter_column_raw is None else str(node_filter_column_raw)
            ),
            node_filter_values=(
                None if node_filter_values_raw is None else tuple(node_filter_values_raw)
            ),
            body_id_dtype=str(graph_raw.pop("body_id_dtype", "uint64")),
            weight_dtype=str(graph_raw.pop("weight_dtype", "float32")),
        )
        graph_raw.pop("spectral_radius", None)
        frozen_graph = dynamics_raw.pop("frozen_graph", True)
        if not isinstance(frozen_graph, bool):
            raise ConfigError("dynamics.frozen_graph must be a boolean")
        internal_steps = dynamics_raw.pop("internal_steps", 2)
        if isinstance(internal_steps, bool) or not isinstance(internal_steps, int):
            raise ConfigError("dynamics.internal_steps must be an integer")
        numeric_dynamics: dict[str, float] = {}
        for key, default in (("leak", 0.3), ("recurrent_gain", 0.9), ("bias", 0.0)):
            raw_value = dynamics_raw.pop(key, default)
            if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
                raise ConfigError(f"dynamics.{key} must be numeric")
            numeric_dynamics[key] = float(raw_value)
        dynamics = DynamicsConfig(
            backend=str(dynamics_raw.pop("backend", "rate")),
            execution_backend=str(dynamics_raw.pop("execution_backend", "scipy-csr-cpu")),
            activation=str(dynamics_raw.pop("activation", "tanh")),
            internal_steps=internal_steps,
            leak=numeric_dynamics["leak"],
            recurrent_gain=numeric_dynamics["recurrent_gain"],
            bias=numeric_dynamics["bias"],
            frozen_graph=frozen_graph,
            initial_state=str(dynamics_raw.pop("initial_state", "zeros")),
            state_dtype=str(dynamics_raw.pop("state_dtype", "float32")),
        )

        encoder_raw = dict(root.pop("encoder", {}) or {})
        decoder_raw = dict(root.pop("decoder", {}) or {})
        state_raw = dict(root.pop("state", {}) or {})
        plasticity_raw = dict(root.pop("plasticity", {}) or {})
        controller_raw = dict(root.pop("controller", {}) or {})
        circuit_raw = dict(root.pop("circuit", {}) or {})
        circuit = CircuitConfig(
            apl_to_kc_gain=float(circuit_raw.pop("apl_to_kc_gain", 1.0)),
        )
        if circuit_raw:
            raise ConfigError(f"unknown circuit keys: {sorted(circuit_raw)}")
        encoder = EncoderConfig(
            kind=str(encoder_raw.pop("kind", "sparse_projection")),
            sensory_superclass=str(encoder_raw.pop("sensory_superclass", "ol_sensory")),
            connections_per_neuron=int(encoder_raw.pop("connections_per_neuron", 64)),
            input_scale=float(encoder_raw.pop("input_scale", 1.0)),
            trainable=bool(encoder_raw.pop("trainable", False)),
            per_game_rules=bool(encoder_raw.pop("per_game_rules", False)),
            on_types=tuple(encoder_raw.pop("on_types", ()) or ()),
            off_types=tuple(encoder_raw.pop("off_types", ()) or ()),
            change_types=tuple(encoder_raw.pop("change_types", ()) or ()),
            change_gain=float(encoder_raw.pop("change_gain", 1.0)),
            colour_permutation_seed=_optional_int(
                encoder_raw.pop("colour_permutation_seed", None),
                "encoder.colour_permutation_seed",
            ),
            mb_input_bus=(
                None
                if (mb_bus_raw := encoder_raw.pop("mb_input_bus", None)) is None
                else str(mb_bus_raw)
            ),
            mb_input_scale=float(encoder_raw.pop("mb_input_scale", 1.0)),
            efference_copy=(
                None
                if (efference_raw := encoder_raw.pop("efference_copy", None)) is None
                else str(efference_raw)
            ),
            efference_scale=float(encoder_raw.pop("efference_scale", 1.0)),
        )
        action_temperature_raw = decoder_raw.pop("action_temperature", 0.15)
        coordinate_temperature_raw = decoder_raw.pop("coordinate_temperature", 0.2)
        if isinstance(action_temperature_raw, bool) or not isinstance(
            action_temperature_raw, (int, float)
        ):
            raise ConfigError("decoder.action_temperature must be numeric")
        if isinstance(coordinate_temperature_raw, bool) or not isinstance(
            coordinate_temperature_raw, (int, float)
        ):
            raise ConfigError("decoder.coordinate_temperature must be numeric")
        loop_escape_enabled_raw = decoder_raw.pop("loop_escape_enabled", False)
        if not isinstance(loop_escape_enabled_raw, bool):
            raise ConfigError("decoder.loop_escape_enabled must be a boolean")
        loop_escape_numeric: dict[str, float] = {}
        for key in (
            "loop_escape_exploration_bonus",
            "loop_escape_unchanged_failure_penalty",
        ):
            raw_value = decoder_raw.pop(key, 0.0)
            if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
                raise ConfigError(f"decoder.{key} must be numeric")
            loop_escape_numeric[key] = float(raw_value)
        decoder = DecoderConfig(
            kind=str(decoder_raw.pop("kind", "literal")),
            readout=str(decoder_raw.pop("readout", "descending_neurons")),
            coordinate_source=str(decoder_raw.pop("coordinate_source", "readout_blocks")),
            reclick_memory=str(decoder_raw.pop("reclick_memory", "none")),
            action_slots=int(decoder_raw.pop("action_slots", 8)),
            coordinate_head=str(decoder_raw.pop("coordinate_head", "literal_factorized_bins")),
            sampling_method=str(decoder_raw.pop("sampling_method", "zscore_softmax_categorical")),
            action_temperature=float(action_temperature_raw),
            coordinate_temperature=float(coordinate_temperature_raw),
            decision_seed_policy=str(
                decoder_raw.pop("decision_seed_policy", "explicit_per_policy_or_config_derived")
            ),
            coordinate_fallback=str(decoder_raw.pop("coordinate_fallback", "novelty_centroid")),
            unchanged_click_exploration=str(
                decoder_raw.pop("unchanged_click_exploration", "seeded_untried_uniform")
            ),
            readout_normalization=str(decoder_raw.pop("readout_normalization", "adaptive")),
            adaptation_rate=float(decoder_raw.pop("adaptation_rate", 0.1)),
            clip=float(decoder_raw.pop("clip", 10.0)),
            loop_escape_enabled=loop_escape_enabled_raw,
            loop_escape_exploration_bonus=loop_escape_numeric["loop_escape_exploration_bonus"],
            loop_escape_unchanged_failure_penalty=loop_escape_numeric[
                "loop_escape_unchanged_failure_penalty"
            ],
            loop_escape_state_hash=str(decoder_raw.pop("loop_escape_state_hash", "blake2b_128")),
            loop_escape_coordinate_memory=str(
                decoder_raw.pop("loop_escape_coordinate_memory", "per_observation")
            ),
            trainable=bool(decoder_raw.pop("trainable", False)),
        )
        rewire_seed = plasticity_raw.get("rewire_mushroom_body_seed")
        plasticity = PlasticityConfig(
            enabled=bool(plasticity_raw.pop("enabled", False)),
            site=str(plasticity_raw.pop("site", "kenyon_cell_to_mbon")),
            learning_rate=float(plasticity_raw.pop("learning_rate", 0.05)),
            decay=float(plasticity_raw.pop("decay", 0.01)),
            weight_ceiling_scale=float(plasticity_raw.pop("weight_ceiling_scale", 2.0)),
            reward_scale=float(plasticity_raw.pop("reward_scale", 1.0)),
            reward_source=str(plasticity_raw.pop("reward_source", "observation_change")),
            level_reward=float(plasticity_raw.pop("level_reward", 1.0)),
            reset_on_new_environment=bool(plasticity_raw.pop("reset_on_new_environment", True)),
            rewire_mushroom_body_seed=(
                None
                if plasticity_raw.pop("rewire_mushroom_body_seed", None) is None
                else int(rewire_seed)
            ),
        )
        state = StateLifetimeConfig(
            reset_on_new_environment=bool(state_raw.pop("reset_on_new_environment", True)),
            preserve_across_levels=bool(state_raw.pop("preserve_across_levels", True)),
            preserve_across_actions=bool(state_raw.pop("preserve_across_actions", True)),
            preserve_after_game_over_reset=bool(
                state_raw.pop("preserve_after_game_over_reset", True)
            ),
        )
        controller_enabled_raw = controller_raw.pop("enabled", False)
        if not isinstance(controller_enabled_raw, bool):
            raise ConfigError("controller.enabled must be a boolean")
        controller_integer_defaults = {
            "mask_freeze_after": 8,
            "volatile_min_changes": 2,
            "ui_border_width": 4,
            "component_min_area": 1,
            "component_limit": 64,
            "coarse_cell_size": 8,
            "max_candidate_tier": 2,
            "max_clicks_per_tier": 64,
            "replan_cooldown": 3,
        }
        controller_integers: dict[str, int] = {}
        for key, default in controller_integer_defaults.items():
            raw_value = controller_raw.pop(key, default)
            if isinstance(raw_value, bool) or not isinstance(raw_value, int):
                raise ConfigError(f"controller.{key} must be an integer")
            controller_integers[key] = raw_value
        controller_numeric_defaults = {
            "volatile_threshold": 0.25,
            "effect_exploration_bonus": 1.5,
            "advancement_bonus": 0.6,
            "death_penalty": 0.4,
        }
        controller_numbers: dict[str, float] = {}
        for key, default in controller_numeric_defaults.items():
            raw_value = controller_raw.pop(key, default)
            if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
                raise ConfigError(f"controller.{key} must be numeric")
            controller_numbers[key] = float(raw_value)
        controller = ControllerConfig(
            enabled=controller_enabled_raw,
            kind=str(controller_raw.pop("kind", "state_graph")),
            state_hash=str(controller_raw.pop("state_hash", "blake2b_128")),
            mask_freeze_after=controller_integers["mask_freeze_after"],
            volatile_threshold=controller_numbers["volatile_threshold"],
            volatile_min_changes=controller_integers["volatile_min_changes"],
            ui_border_width=controller_integers["ui_border_width"],
            component_min_area=controller_integers["component_min_area"],
            component_limit=controller_integers["component_limit"],
            coarse_cell_size=controller_integers["coarse_cell_size"],
            max_candidate_tier=controller_integers["max_candidate_tier"],
            max_clicks_per_tier=controller_integers["max_clicks_per_tier"],
            effect_exploration_bonus=controller_numbers["effect_exploration_bonus"],
            advancement_bonus=controller_numbers["advancement_bonus"],
            death_penalty=controller_numbers["death_penalty"],
            replan_cooldown=controller_integers["replan_cooldown"],
            dense_reinforcement=bool(controller_raw.pop("dense_reinforcement", False)),
            dense_budget=float(controller_raw.pop("dense_budget", 2.0)),
            click_head=str(controller_raw.pop("click_head", "none")),
            click_head_weight=float(controller_raw.pop("click_head_weight", 1.0)),
            click_head_learning_rate=float(controller_raw.pop("click_head_learning_rate", 0.3)),
            click_head_seed=int(controller_raw.pop("click_head_seed", 20260924)),
            click_head_negative_scale=float(controller_raw.pop("click_head_negative_scale", 1.0)),
            click_head_deadline=int(controller_raw.pop("click_head_deadline", 0)),
            state_similarity=str(controller_raw.pop("state_similarity", "none")),
            state_similarity_threshold=float(controller_raw.pop("state_similarity_threshold", 0.9)),
        )
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"invalid configuration value: {exc}") from exc

    if data_raw:
        raise ConfigError(f"unknown data keys: {sorted(data_raw)}")
    if graph_raw:
        raise ConfigError(f"unknown graph keys: {sorted(graph_raw)}")
    if dynamics_raw:
        raise ConfigError(f"unknown dynamics keys: {sorted(dynamics_raw)}")
    if encoder_raw:
        raise ConfigError(f"unknown encoder keys: {sorted(encoder_raw)}")
    if decoder_raw:
        raise ConfigError(f"unknown decoder keys: {sorted(decoder_raw)}")
    if state_raw:
        raise ConfigError(f"unknown state keys: {sorted(state_raw)}")
    if plasticity_raw:
        raise ConfigError(f"unknown plasticity keys: {sorted(plasticity_raw)}")
    if controller_raw:
        raise ConfigError(f"unknown controller keys: {sorted(controller_raw)}")
    if graph.weight_transform not in {"raw", "log1p", "sqrt", "binary"}:
        raise ConfigError(f"unsupported weight_transform: {graph.weight_transform}")
    if graph.sign_mode not in {"unsigned", "heuristic"}:
        raise ConfigError(f"unsupported sign_mode: {graph.sign_mode}")
    for field_name in ("modulator_treatment", "unknown_transmitter_treatment"):
        treatment = getattr(graph, field_name)
        if treatment not in {"zero", "positive", "negative", "error"}:
            raise ConfigError(f"unsupported {field_name}: {treatment}")
    if graph.normalization not in {"none", "incoming_l1", "spectral_radius"}:
        raise ConfigError(f"unsupported normalization: {graph.normalization}")
    if graph.epsilon <= 0:
        raise ConfigError("graph.epsilon must be positive")
    if graph.matrix_convention != "W[post_index, pre_index]":
        raise ConfigError("graph.matrix_convention must be exactly 'W[post_index, pre_index]'")
    if graph.body_id_dtype != "uint64":
        raise ConfigError("graph.body_id_dtype must be uint64")
    if graph.weight_dtype != "float32":
        raise ConfigError("graph.weight_dtype must be float32")
    if dynamics.backend != "rate":
        raise ConfigError("dynamics.backend must be rate for the Milestone 2 backend")
    if dynamics.execution_backend != "scipy-csr-cpu":
        raise ConfigError("dynamics.execution_backend must be scipy-csr-cpu")
    if dynamics.activation != "tanh":
        raise ConfigError("dynamics.activation must be tanh")
    if dynamics.internal_steps <= 0:
        raise ConfigError("dynamics.internal_steps must be positive")
    if not 0.0 < dynamics.leak <= 1.0:
        raise ConfigError("dynamics.leak must be in (0, 1]")
    if dynamics.recurrent_gain < 0.0:
        raise ConfigError("dynamics.recurrent_gain must be non-negative")
    if not all(
        math.isfinite(value) for value in (dynamics.leak, dynamics.recurrent_gain, dynamics.bias)
    ):
        raise ConfigError("dynamics numeric values must be finite")
    if not dynamics.frozen_graph and not plasticity.enabled:
        raise ConfigError(
            "dynamics.frozen_graph may only be false when plasticity.enabled is true; "
            "an unfrozen graph without a declared learning rule is just an unguarded graph"
        )
    if dynamics.initial_state != "zeros":
        raise ConfigError("dynamics.initial_state must be zeros")
    if dynamics.state_dtype != "float32":
        raise ConfigError("dynamics.state_dtype must be float32")
    if encoder.kind not in {
        "sparse_projection",
        "retinotopic",
        "retinotopic_colour",
        "bio_visual",
    }:
        raise ConfigError(f"unsupported encoder.kind: {encoder.kind}")
    if not math.isfinite(encoder.change_gain) or encoder.change_gain < 0:
        raise ConfigError("encoder.change_gain must be finite and non-negative")
    overlap = set(encoder.on_types) & set(encoder.off_types)
    if overlap:
        raise ConfigError(f"a cell type cannot be both ON and OFF: {sorted(overlap)}")
    if decoder.reclick_memory not in ("none", "surprise", "griddiff"):
        raise ConfigError(f"unknown decoder.reclick_memory: {decoder.reclick_memory!r}")
    if decoder.coordinate_source not in (
        "readout_blocks",
        "retinotopic_state",
        "retinotopic_surprise",
    ):
        raise ConfigError(f"unknown decoder.coordinate_source: {decoder.coordinate_source!r}")
    if encoder.efference_copy is not None and encoder.efference_copy != "antennal_mechanosensory":
        raise ConfigError(
            f"unsupported encoder.efference_copy: {encoder.efference_copy!r} "
            "(only 'antennal_mechanosensory' is implemented)"
        )
    if not math.isfinite(encoder.efference_scale) or encoder.efference_scale <= 0:
        raise ConfigError("encoder.efference_scale must be finite and positive")
    if encoder.mb_input_bus is not None and encoder.mb_input_bus != "colour_histogram":
        raise ConfigError(
            f"unsupported encoder.mb_input_bus: {encoder.mb_input_bus!r} "
            "(only 'colour_histogram' is implemented)"
        )
    if not math.isfinite(encoder.mb_input_scale) or encoder.mb_input_scale <= 0:
        raise ConfigError("encoder.mb_input_scale must be finite and positive")
    if encoder.colour_permutation_seed is not None and encoder.kind != "retinotopic_colour":
        raise ConfigError(
            "colour_permutation_seed is the falsification control for the "
            "retinotopic_colour encoder and applies to no other kind"
        )
    if encoder.kind not in ("retinotopic", "retinotopic_colour") and (
        encoder.on_types or encoder.off_types or encoder.change_types
    ):
        raise ConfigError(
            "on_types, off_types and change_types apply only to the retinotopic encoder"
        )
    if encoder.connections_per_neuron <= 0:
        raise ConfigError("encoder.connections_per_neuron must be positive")
    if not math.isfinite(encoder.input_scale) or encoder.input_scale <= 0:
        raise ConfigError("encoder.input_scale must be finite and positive")
    if encoder.trainable or encoder.per_game_rules:
        raise ConfigError("the literal encoder must be nonlearned and game-agnostic")
    if decoder.kind != "literal":
        raise ConfigError(f"unsupported decoder.kind: {decoder.kind}")
    if decoder.coordinate_head != "literal_factorized_bins":
        raise ConfigError("unsupported decoder.coordinate_head")
    if decoder.sampling_method != "zscore_softmax_categorical":
        raise ConfigError(f"unsupported decoder.sampling_method: {decoder.sampling_method}")
    if not math.isfinite(decoder.action_temperature) or decoder.action_temperature <= 0:
        raise ConfigError("decoder.action_temperature must be finite and positive")
    if not math.isfinite(decoder.coordinate_temperature) or decoder.coordinate_temperature <= 0:
        raise ConfigError("decoder.coordinate_temperature must be finite and positive")
    if decoder.decision_seed_policy != "explicit_per_policy_or_config_derived":
        raise ConfigError(
            f"unsupported decoder.decision_seed_policy: {decoder.decision_seed_policy}"
        )
    if decoder.coordinate_fallback not in ("novelty_centroid", "factorized"):
        raise ConfigError(f"unsupported decoder.coordinate_fallback: {decoder.coordinate_fallback}")
    if decoder.unchanged_click_exploration != "seeded_untried_uniform":
        raise ConfigError(
            "unsupported decoder.unchanged_click_exploration: "
            f"{decoder.unchanged_click_exploration}"
        )
    if decoder.action_slots != 8:
        raise ConfigError("decoder.action_slots must be 8 for ARC-AGI-3")
    if decoder.readout_normalization not in {"adaptive", "population"}:
        raise ConfigError(
            f"unsupported decoder.readout_normalization: {decoder.readout_normalization}"
        )
    if not 0.0 < decoder.adaptation_rate <= 1.0:
        raise ConfigError("decoder.adaptation_rate must lie in (0, 1]")
    if not math.isfinite(decoder.clip) or decoder.clip <= 0:
        raise ConfigError("decoder.clip must be finite and positive")
    for field_name in (
        "loop_escape_exploration_bonus",
        "loop_escape_unchanged_failure_penalty",
    ):
        value = getattr(decoder, field_name)
        if not math.isfinite(value) or value < 0.0:
            raise ConfigError(f"decoder.{field_name} must be finite and non-negative")
    if decoder.loop_escape_enabled and decoder.loop_escape_exploration_bonus <= 0.0:
        raise ConfigError(
            "decoder.loop_escape_exploration_bonus must be positive when loop escape is enabled"
        )
    if decoder.loop_escape_state_hash != "blake2b_128":
        raise ConfigError(
            f"unsupported decoder.loop_escape_state_hash: {decoder.loop_escape_state_hash}"
        )
    if decoder.loop_escape_coordinate_memory != "per_observation":
        raise ConfigError(
            "unsupported decoder.loop_escape_coordinate_memory: "
            f"{decoder.loop_escape_coordinate_memory}"
        )
    if decoder.trainable:
        raise ConfigError("the literal decoder must be nonlearned")
    if plasticity.site != "kenyon_cell_to_mbon":
        raise ConfigError(
            f"unsupported plasticity.site: {plasticity.site}; the only implemented "
            "site is where Drosophila actually learns"
        )
    if plasticity.reward_source not in {"observation_change", "level_progress", "both"}:
        raise ConfigError(f"unsupported plasticity.reward_source: {plasticity.reward_source}")
    if not math.isfinite(plasticity.learning_rate) or plasticity.learning_rate < 0:
        raise ConfigError("plasticity.learning_rate must be finite and non-negative")
    if not 0.0 <= plasticity.decay <= 1.0:
        raise ConfigError("plasticity.decay must lie in [0, 1]")
    if plasticity.weight_ceiling_scale < 1.0:
        raise ConfigError("plasticity.weight_ceiling_scale must be at least 1")
    if not math.isfinite(plasticity.reward_scale):
        raise ConfigError("plasticity.reward_scale must be finite")
    if plasticity.enabled and dynamics.frozen_graph:
        raise ConfigError(
            "plasticity.enabled requires dynamics.frozen_graph: false; a config "
            "must not claim a frozen graph while modifying its weights"
        )
    if not state.preserve_across_actions:
        raise ConfigError(
            "state.preserve_across_actions must remain true; a recurrent graph "
            "cannot matter if its state does not outlive one decision"
        )
    if controller.kind != "state_graph":
        raise ConfigError(f"unsupported controller.kind: {controller.kind}")
    if controller.state_hash != "blake2b_128":
        raise ConfigError(f"unsupported controller.state_hash: {controller.state_hash}")
    for field_name in (
        "mask_freeze_after",
        "volatile_min_changes",
        "ui_border_width",
        "component_min_area",
        "component_limit",
        "coarse_cell_size",
        "max_clicks_per_tier",
    ):
        if getattr(controller, field_name) <= 0:
            raise ConfigError(f"controller.{field_name} must be positive")
    if controller.max_candidate_tier < 0:
        raise ConfigError("controller.max_candidate_tier must be non-negative")
    if controller.replan_cooldown < 0:
        raise ConfigError("controller.replan_cooldown must be non-negative")
    if controller.ui_border_width > 32:
        raise ConfigError("controller.ui_border_width must not exceed 32")
    if controller.coarse_cell_size > 64:
        raise ConfigError("controller.coarse_cell_size must not exceed 64")
    if not 0.0 < controller.volatile_threshold <= 1.0:
        raise ConfigError("controller.volatile_threshold must lie in (0, 1]")
    for field_name in (
        "effect_exploration_bonus",
        "advancement_bonus",
        "death_penalty",
    ):
        value = getattr(controller, field_name)
        if not math.isfinite(value) or value < 0.0:
            raise ConfigError(f"controller.{field_name} must be finite and non-negative")

    # Name/track are descriptive and remain available to manifests without
    # coupling the shared runtime config to later experimental tracks.
    root["experiment"] = experiment

    return FlyGIConfig(
        schema_version=schema_version,
        seed=seed,
        data=data,
        graph=graph,
        dynamics=dynamics,
        encoder=encoder,
        decoder=decoder,
        state=state,
        plasticity=plasticity,
        controller=controller,
        circuit=circuit,
        groups=groups,
        future=root,
    )
