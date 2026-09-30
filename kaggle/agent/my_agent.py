"""Official ARC-AGI-3 ``MyAgent`` adapter for the FlyGI connectome policy.

The competition framework imports this module and requires the class and method
names below. All behavior lives in ``flygi.arc`` so the scientific core never
imports Kaggle or the official agent harness.

The evaluation notebook runs with internet disabled, so the compiled MaleCNS
runtime is attached as a Kaggle Dataset and discovered on disk. It is loaded and
hash-verified exactly once per process, not once per game: the framework builds
one ``MyAgent`` per game, and a 24-million-edge graph must not be re-read each
time. Competition reruns fail closed when that runtime is absent or invalid.
The random-legal policy remains available only through an explicit smoke-test
opt-in; it must never silently replace FlyGI in an official evaluation.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from pathlib import Path
from typing import Any

from flygi.arc import RandomLegalPolicy

_ARC_IMPORT_ERROR: ModuleNotFoundError | None = None

try:
    from arcengine import FrameData, GameAction
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by import smoke
    _ARC_IMPORT_ERROR = exc
    FrameData = Any  # type: ignore[misc,assignment]
    GameAction = None  # type: ignore[assignment]

try:
    # The official ARC-AGI-3-Agents checkout is placed on sys.path by the
    # starter both locally and in its generated Kaggle notebook.
    from agents.agent import Agent
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by import smoke
    _ARC_IMPORT_ERROR = _ARC_IMPORT_ERROR or exc

    class Agent:  # type: ignore[no-redef]
        """Import-only fallback with an actionable runtime failure below."""

        MAX_ACTIONS = 80

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            del args
            self.game_id = str(kwargs.get("game_id", "unconfigured"))

        @property
        def name(self) -> str:
            return f"{self.game_id}.{self.__class__.__name__.lower()}"


# Candidate locations for the attached runtime, most specific first.
_RUNTIME_ENV_VAR = "FLYGI_RUNTIME_DIR"
_FALLBACK_ENV_VAR = "FLYGI_ALLOW_RANDOM_FALLBACK"
_COMPETITION_RERUN_ENV_VAR = "KAGGLE_IS_COMPETITION_RERUN"
_KAGGLE_INPUT = Path("/kaggle/input")
_RUNTIME_HINTS = ("flygi-malecns-runtime", "flygi")
_REQUIRED_VERIFIED_OUTPUTS = frozenset({"graph.npz", "node_metadata.npz", "groups.npz"})
_PREFLIGHT_PREFIX = "FLYGI_PREFLIGHT="

_LOADED: dict[str, Any] = {}

# Competition notebooks may run for up to nine hours. At 600 actions per game
# and a pessimistic 300 ms per action, 25 games take about 75 minutes and even
# 100 games stay under five hours, so the budget is safe for any plausible
# hidden set. The guard exists because a notebook that overruns loses the whole
# submission and the day's quota with it: past the deadline every agent reports
# itself done, which ends its game cleanly and preserves the levels already
# completed rather than failing the run.
_WALL_CLOCK_DEADLINE_SECONDS = float(os.environ.get("FLYGI_DEADLINE_SECONDS", 8.4 * 3600))
_PROCESS_STARTED = time.monotonic()


def _deadline_exceeded() -> bool:
    return (time.monotonic() - _PROCESS_STARTED) >= _WALL_CLOCK_DEADLINE_SECONDS


class RuntimePreflightError(RuntimeError):
    """Raised when a verified connectome is required but unavailable."""


def _candidate_runtime_dirs() -> list[Path]:
    declared = os.environ.get(_RUNTIME_ENV_VAR)
    candidates: list[Path] = []
    if declared:
        candidates.append(Path(declared))
    if _KAGGLE_INPUT.is_dir():
        for entry in sorted(_KAGGLE_INPUT.iterdir()):
            if not entry.is_dir():
                continue
            if any(hint in entry.name.lower() for hint in _RUNTIME_HINTS):
                candidates.extend([entry / "runtime", entry])
    return candidates


def _find_runtime() -> tuple[Path, Path] | None:
    """Return ``(runtime_dir, config_path)`` for the first complete bundle."""

    for candidate in _candidate_runtime_dirs():
        if not (candidate / "graph.npz").is_file():
            continue
        for config in (
            candidate / "config.yaml",
            candidate.parent / "config.yaml",
        ):
            if config.is_file():
                return candidate, config
    return None


def _find_controller_config(runtime_dir: Path, config_path: Path) -> Path | None:
    """Return the packaged controller declaration, if the dataset carries one.

    Absent, the adapter builds the pure connectome policy exactly as before, so
    an existing dataset keeps producing a byte-identical agent. Present, the fly
    moves into the controller's tie position -- the submission gate requires the
    connectome to stay load-bearing, so there is no controller-only mode here.
    """

    for candidate in (
        runtime_dir / "controller.yaml",
        config_path.parent / "controller.yaml",
    ):
        if candidate.is_file():
            return candidate
    return None


def _shared_runtime() -> dict[str, Any]:
    """Load, verify and cache the connectome once for the whole process."""

    if _LOADED:
        return _LOADED

    located = _find_runtime()
    if located is None:
        _LOADED.update({"available": False, "reason": "no attached FlyGI runtime found"})
        return _LOADED

    runtime_dir, config_path = located
    try:
        from flygi.arc.factory import build_connectome_policy
        from flygi.config import load_config

        config = load_config(config_path)
        assembled = build_connectome_policy(
            config, GameAction, runtime_dir=runtime_dir, bundle=None
        )
        verified_outputs = {Path(path).name for path in assembled.bundle.verified_hashes}
        missing_hashes = sorted(_REQUIRED_VERIFIED_OUTPUTS - verified_outputs)
        if missing_hashes:
            raise ValueError(
                f"runtime manifest did not hash every deployment array; missing {missing_hashes}"
            )
        controller_path = _find_controller_config(runtime_dir, config_path)
        controller_config = None
        head_cell_columns = None
        head_column_count = 0
        if controller_path is not None:
            controller_config = load_config(controller_path)
            if not controller_config.controller.enabled:
                raise ValueError(
                    f"{controller_path.name} is attached but controller.enabled is false"
                )
            # H-CONSEQUENCE-COUPLING: the click head's retinal map compiles
            # once from the attached runtime; the online head itself is
            # per-game state built at Agent construction.
            if controller_config.controller.click_head.startswith("retinotopic"):
                from flygi.controller.click_head import load_cell_columns

                head_cell_columns, head_column_count = load_cell_columns(runtime_dir)
        _LOADED.update(
            {
                "available": True,
                "config": config,
                "controller_config": controller_config,
                "controller_path": controller_path,
                "head_cell_columns": head_cell_columns,
                "head_column_count": head_column_count,
                "runtime_dir": runtime_dir,
                "bundle": assembled.bundle,
                "projection": assembled.projection,
                "interface": assembled.describe(),
            }
        )
    except Exception as exc:  # A broken asset must be reported, never silent.
        _LOADED.update({"available": False, "reason": f"{type(exc).__name__}: {exc}"})
    return _LOADED


def _runtime_identity(shared: dict[str, Any]) -> dict[str, Any]:
    """Return a stable, JSON-serializable identity for a verified runtime."""

    if not shared.get("available"):
        return {
            "mode": "unavailable",
            "reason": str(shared.get("reason", "unknown")),
            "verified": False,
        }

    bundle = shared["bundle"]
    interface = shared["interface"]
    verified_hashes = {
        Path(path).name: digest for path, digest in sorted(bundle.verified_hashes.items())
    }
    controller_config = shared.get("controller_config")
    deploy_fly_tiebreak = (
        None
        if controller_config is None
        else bool(getattr(controller_config.controller, "deploy_fly_tiebreak", True))
    )
    neuronal_dynamics_active = controller_config is None or bool(deploy_fly_tiebreak)
    if controller_config is None:
        mode = "connectome"
    elif neuronal_dynamics_active:
        mode = "controller-fly"
    else:
        mode = "controller-light"
    return {
        "controller": (
            None if shared.get("controller_path") is None else Path(shared["controller_path"]).name
        ),
        "click_head": (
            None if controller_config is None else controller_config.controller.click_head
        ),
        "fap_library": (
            None
            if controller_config is None
            else bool(getattr(controller_config.controller, "fap_library", False))
        ),
        "search_layer": (
            None
            if controller_config is None
            else bool(getattr(controller_config.controller, "search_layer", False))
        ),
        "click_head_deadline": (
            None if controller_config is None else controller_config.controller.click_head_deadline
        ),
        "click_head_coordinate_convention": (
            None
            if controller_config is None
            else controller_config.controller.click_head_coordinate_convention
        ),
        "deploy_fly_tiebreak": deploy_fly_tiebreak,
        "state_similarity": (
            None if controller_config is None else controller_config.controller.state_similarity
        ),
        "edges": int(bundle.edge_count),
        "internal_steps": int(interface["internal_steps"]),
        "mode": mode,
        "neuronal_dynamics_active": neuronal_dynamics_active,
        "nodes": int(bundle.node_count),
        "release": str(bundle.manifest.get("release")),
        "sign_mode": str(bundle.manifest.get("preprocessing", {}).get("sign_mode")),
        "verified": True,
        "verified_output_hashes": verified_hashes,
    }


def preflight_runtime(*, emit: bool = True) -> dict[str, Any]:
    """Discover, load and hash-verify the attached connectome without a game.

    The ordinary Kaggle notebook calls this before producing its dummy output.
    A single prefixed JSON line makes the exact runtime identity easy to inspect
    in the kernel log and easy for automation to parse.
    """

    identity = _runtime_identity(_shared_runtime())
    if not identity["verified"]:
        raise RuntimePreflightError(
            "FlyGI connectome runtime preflight failed: " + str(identity["reason"])
        )
    if emit:
        print(
            _PREFLIGHT_PREFIX + json.dumps(identity, sort_keys=True, separators=(",", ":")),
            flush=True,
        )
    return identity


def _environment_opt_in(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


_INSTANCE_COUNTER: dict[str, int] = {}
_INSTANCE_LOCK = threading.Lock()


def _seed_for_game(game_id: str) -> int:
    """Process-independent seed, distinct PER INSTANCE of the same game.

    The environment score is the max over runs, so replaying a game is free
    expected upside for a stochastic policy -- but only if replays actually
    diverge. Mixing an instance counter into the digest makes the Nth replay
    of a game a genuinely different rollout while staying deterministic for
    a given (game, instance) pair.
    """

    with _INSTANCE_LOCK:
        nonce = _INSTANCE_COUNTER.get(game_id, 0)
        _INSTANCE_COUNTER[game_id] = nonce + 1
    digest = hashlib.sha256(f"{game_id}#{nonce}".encode()).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


class MyAgent(Agent):
    """FlyGI connectome agent, with a smoke-test-only random fallback."""

    # Measured 2026-09-22: nine of the twelve level completions observed across
    # all four conditions of the 500-action public sweep required MORE than 80
    # actions, and r11l was only ever completed at 164, 191 and 333 actions. The
    # previous 80-action ceiling could not reach those games at all. The
    # scorecard caps a game by the level weight completed, so a larger budget
    # only adds completion opportunities; it never slows a completion that would
    # have happened sooner. Competition notebooks may run nine hours, which at
    # the observed 136-164 ms per action leaves ample headroom here.
    MAX_ACTIONS = 200_000

    # THE SIX-ZEROS BUG (found 2026-09-25 by the local competition-mode
    # gateway battery): the base Agent.__init__ calls start_recording()
    # when record=True -- which Swarm ALWAYS passes at the Kaggle rerun --
    # and start_recording reads self.name, whose override below used
    # self._mode before our __init__ had set it. Every agent construction
    # raised AttributeError inside the swarm thread; main.py's own thread
    # exited 0; the notebook's return-code check passed; the pre-opened
    # empty scorecard scored 0.00. Every local test had passed record=False,
    # the one condition that differed from the rerun. Class-level defaults
    # make construction-order safe forever.
    _mode = "constructing"
    _detail = "agent still constructing"

    # Transport resilience: the framework's env.step returns None on ANY
    # HTTP failure (10s timeout, no retry), do_action_request then raises,
    # and the game's thread dies permanently while the notebook still exits
    # 0 -- a silent per-game death measured as a community failure mode.
    # Retry transient failures; after persistent failure, end the game
    # cleanly instead of killing the thread.
    _TRANSPORT_RETRIES = 4

    def do_action_request(self, action):  # type: ignore[override]
        last_error = None
        for attempt in range(self._TRANSPORT_RETRIES):
            try:
                return super().do_action_request(action)
            except ValueError as exc:
                last_error = exc
                time.sleep(min(2.0 * (attempt + 1), 8.0))
        self._transport_dead = True
        print(
            "FLYGI_TRANSPORT_DEAD="
            + json.dumps(
                {
                    "game_id": str(self.game_id),
                    "error": (
                        "persistent empty frame"
                        if last_error is None
                        else f"{type(last_error).__name__}: {last_error}"
                    ),
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
            flush=True,
        )
        # ASSUMPTION: after persistent transport failure the server-side game
        # cannot be advanced safely, but returning the last valid frame lets the
        # official loop reach is_done() and cleanup() instead of losing this
        # thread to an exception. Check with a gateway that drops four replies;
        # if cleanup does not close the scorecard, this fallback is invalid.
        frames = getattr(self, "frames", None)
        if frames:
            return frames[-1]
        raise RuntimeError("transport failed before the agent received a frame") from last_error

    def append_frame(self, frame: FrameData) -> None:
        """Keep only the current frame and omit per-turn replay serialization.

        Swarm forces ``record=True`` and the upstream implementation otherwise
        stores every full frame twice: in ``self.frames`` and as JSONL. The
        35-minute gateway battery measured 2.104 GiB across its 25 recording
        files, so an 8.4-hour run projects to roughly 30.3 GiB of redundant
        JSONL before accounting for the in-memory frame copies.

        ASSUMPTION: FlyGI is Markov at the adapter boundary. Both methods the
        framework calls discard the historical ``frames`` argument; all needed
        memory lives inside ``self._policy``. The comparison gate requires the
        deterministic short gateway run to preserve the prior level/action
        milestone and score. If a future policy reads frame history, this
        override must not ship.

        The official gateway owns the scorecard; the local Recorder is only a
        replay/debug copy. Suppressing it does not suppress scored actions or
        final scorecard closure.
        """

        self.frames[:] = [frame]
        guid = getattr(frame, "guid", None)
        if guid:
            self.guid = guid

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # ``rng_seed`` is a FlyGI-only testing/replay override and must not be
        # forwarded to the official Agent constructor.
        rng_seed = kwargs.pop("rng_seed", None)
        allow_random_fallback = bool(kwargs.pop("allow_random_fallback", False))
        super().__init__(*args, **kwargs)
        if _ARC_IMPORT_ERROR is not None or GameAction is None:
            raise RuntimeError(
                "The ARC adapter requires the official 'arcengine' and "
                "'agents' packages. The dependency-free flygi.arc core can "
                "still be imported and tested without them."
            ) from _ARC_IMPORT_ERROR

        decision_seed = _seed_for_game(str(self.game_id)) if rng_seed is None else int(rng_seed)
        shared = _shared_runtime()
        if shared.get("available") and shared.get("controller_config") is not None:
            from flygi.controller import StateGraphPolicy

            # Deploy profile: the full-graph tie-break is measured score-inert
            # (four independent arms, exact nulls) and costs ~100x the
            # per-action latency of everything else combined -- under the
            # rerun's parallel-swarm regime that latency is the binding
            # budget. deploy_fly_tiebreak=false keeps the measured engineering
            # controller (static retinotopic metadata, tags) and drops the only
            # component that actually advances fly-neuron dynamics.
            fly = None
            if getattr(
                shared["controller_config"].controller, "deploy_fly_tiebreak", True
            ) or not hasattr(shared["controller_config"].controller, "deploy_fly_tiebreak"):
                from flygi.controller.fly_tiebreak import FlyTiebreaker

                fly = FlyTiebreaker(
                    shared["config"],
                    runtime_dir=shared["runtime_dir"],
                    bundle=shared["bundle"],
                    projection=shared["projection"],
                )
            controller = shared["controller_config"].controller
            state_tags = None
            if controller.state_similarity != "none":
                from flygi.controller.state_tags import RetinoTagRegistry

                state_tags = RetinoTagRegistry(
                    shared["runtime_dir"],
                    threshold=controller.state_similarity_threshold,
                    permute_retinotopy=(controller.state_similarity == "retino_tags_permuted"),
                )
            click_head = None
            if controller.click_head != "none":
                from flygi.controller.click_head import OnlineClickHead

                click_head = OnlineClickHead(
                    controller.click_head,
                    cell_columns=shared.get("head_cell_columns"),
                    column_count=int(shared.get("head_column_count") or 0),
                    weight=controller.click_head_weight,
                    learning_rate=controller.click_head_learning_rate,
                    permutation_seed=controller.click_head_seed,
                    negative_scale=controller.click_head_negative_scale,
                    coordinate_convention=controller.click_head_coordinate_convention,
                )
            fap = None
            if getattr(controller, "fap_library", False):
                from flygi.controller.fap_library import FapExecutor

                fap = FapExecutor()
            search = None
            if getattr(controller, "search_layer", False):
                from flygi.controller.search_layer import OnlineSearchLayer

                search = OnlineSearchLayer()
            self._policy = StateGraphPolicy(
                GameAction,
                controller,
                decision_seed=decision_seed,
                fly=fly,
                click_head=click_head,
                state_tags=state_tags,
                fap=fap,
                search=search,
            )
            self._mode = "controller-fly" if fly is not None else "controller-light"
            self._detail = (
                f"{shared['bundle'].node_count} nodes / "
                f"{shared['bundle'].edge_count} edges in the tie position"
                if fly is not None
                else "light profile: retinotopic head + tags, tie seat off"
            )
            # Kaggle debugging happens through stdout alone, so the exact agent
            # identity -- encoder kind, coordinate source, efference state,
            # graph size -- is emitted machine-readably once per game.
            print(
                "FLYGI_AGENT="
                + json.dumps(
                    {
                        "game_id": str(self.game_id),
                        **(fly.describe() if fly is not None else {"tie_seat": "off (light)"}),
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                    default=str,
                ),
                flush=True,
            )
        elif shared.get("available"):
            from flygi.arc.factory import build_connectome_policy

            assembled = build_connectome_policy(
                shared["config"],
                GameAction,
                runtime_dir=shared["runtime_dir"],
                bundle=shared["bundle"],
                projection=shared["projection"],
                decision_seed=decision_seed,
            )
            self._policy = assembled.policy
            self._mode = "connectome"
            self._detail = (
                f"{shared['bundle'].node_count} nodes / "
                f"{shared['bundle'].edge_count} edges, K={self._policy.internal_steps}"
            )
        else:
            reason = str(shared.get("reason", "unknown"))
            competition_rerun = bool(os.environ.get(_COMPETITION_RERUN_ENV_VAR))
            fallback_opted_in = allow_random_fallback or _environment_opt_in(_FALLBACK_ENV_VAR)
            if competition_rerun or not fallback_opted_in:
                context = (
                    "official competition rerun" if competition_rerun else "adapter construction"
                )
                raise RuntimePreflightError(
                    f"FlyGI connectome runtime is required for {context}: {reason}. "
                    f"Random fallback is disabled; {_FALLBACK_ENV_VAR}=1 is only "
                    "for non-competition smoke tests."
                )
            self._policy = RandomLegalPolicy(GameAction, seed=decision_seed)
            self._mode = "random-legal"
            self._detail = reason
        self._deadline_reported = False
        print(f"FlyGI agent mode={self._mode} ({self._detail})", flush=True)

    @property
    def name(self) -> str:
        return f"{super().name}.{self.MAX_ACTIONS}.{self._mode}"

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        del frames
        if getattr(self, "_transport_dead", False):
            return True
        if _deadline_exceeded():
            if not self._deadline_reported:
                self._deadline_reported = True
                print(
                    "FLYGI_DEADLINE: wall-clock guard reached; ending games cleanly "
                    "to preserve completed levels",
                    flush=True,
                )
            return True
        return self._policy.is_done(latest_frame)

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
        del frames
        try:
            action = self._policy.choose_action(latest_frame)
        except Exception as exc:
            # Fail visible, then DEGRADE, never die: a raised exception kills
            # this game's Swarm thread permanently (measured: tu93 at turn
            # 2,446 -- 'no legal nonfatal candidate' -- an edge only reachable
            # past the old 600-action cap). A random legal action keeps the
            # game alive; completed levels are already banked server-side.
            print(
                "FLYGI_ERROR="
                + json.dumps(
                    {
                        "game_id": str(self.game_id),
                        "turn": getattr(self, "_flygi_turns", 0),
                        "error": f"{type(exc).__name__}: {exc}",
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                flush=True,
            )
            from flygi.arc import RandomLegalPolicy

            fallback = getattr(self, "_flygi_fallback", None)
            if fallback is None:
                fallback = RandomLegalPolicy(
                    GameAction, seed=_seed_for_game(f"fallback:{self.game_id}")
                )
                self._flygi_fallback = fallback
            action = fallback.choose_action(latest_frame)
        self._flygi_turns = getattr(self, "_flygi_turns", 0) + 1
        budget_setter = getattr(self._policy, "set_remaining_action_budget", None)
        if callable(budget_setter):
            # Registered gate-(a) amendment: the rerun's budget is MAX_ACTIONS
            # minus turns taken -- effectively uncapped, so the search layer
            # engages there while short local rows keep it idle.
            budget_setter(self.MAX_ACTIONS - self._flygi_turns)
        if self._flygi_turns % 100 == 0:
            diagnostics = getattr(self._policy, "diagnostics", None)
            if callable(diagnostics):
                snapshot = diagnostics()
                print(
                    "FLYGI_DIAG="
                    + json.dumps(
                        {
                            "game_id": str(self.game_id),
                            "turn": self._flygi_turns,
                            "fly_decisive_rate": snapshot.get("fly_decisive_rate"),
                            "states": snapshot.get("states_discovered"),
                            "outcomes": snapshot.get("outcomes"),
                            "fap_fired": snapshot.get("fap_fired_turns"),
                            "fap_errors": snapshot.get("fap_errors"),
                            "search_engaged": snapshot.get("search_engaged_turns"),
                            "search_found": snapshot.get("search_programs_found"),
                        },
                        sort_keys=True,
                        separators=(",", ":"),
                        default=str,
                    ),
                    flush=True,
                )
        return action  # type: ignore[return-value]
