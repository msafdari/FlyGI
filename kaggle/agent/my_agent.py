"""Official ARC-AGI-3 ``MyAgent`` adapter for the FlyGI connectome policy.

The competition framework imports this module and requires the class and method
names below. All behavior lives in ``flygi.arc`` so the scientific core never
imports Kaggle or the official agent harness.

The evaluation notebook runs with internet disabled, so the compiled MaleCNS
runtime is attached as a Kaggle Dataset and discovered on disk. It is loaded and
hash-verified exactly once per process, not once per game: the framework builds
one ``MyAgent`` per game, and a 24-million-edge graph must not be re-read each
time. If no runtime is attached, the adapter falls back to the deterministic
random-legal policy and says so, rather than pretending a connectome ran.
"""

from __future__ import annotations

import hashlib
import os
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
_KAGGLE_INPUT = Path("/kaggle/input")
_RUNTIME_HINTS = ("flygi-malecns-runtime", "flygi")

_LOADED: dict[str, Any] = {}


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
        _LOADED.update(
            {
                "available": True,
                "config": config,
                "runtime_dir": runtime_dir,
                "bundle": assembled.bundle,
                "projection": assembled.projection,
                "interface": assembled.describe(),
            }
        )
    except Exception as exc:  # A broken asset must be reported, never silent.
        _LOADED.update({"available": False, "reason": f"{type(exc).__name__}: {exc}"})
    return _LOADED


def _seed_for_game(game_id: str) -> int:
    """Create a process-independent replay seed from the framework game id."""

    digest = hashlib.sha256(game_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


class MyAgent(Agent):
    """FlyGI connectome agent, with an explicit random fallback."""

    MAX_ACTIONS = 80

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # ``rng_seed`` is a FlyGI-only testing/replay override and must not be
        # forwarded to the official Agent constructor.
        rng_seed = kwargs.pop("rng_seed", None)
        super().__init__(*args, **kwargs)
        if _ARC_IMPORT_ERROR is not None or GameAction is None:
            raise RuntimeError(
                "The ARC adapter requires the official 'arcengine' and "
                "'agents' packages. The dependency-free flygi.arc core can "
                "still be imported and tested without them."
            ) from _ARC_IMPORT_ERROR

        shared = _shared_runtime()
        if shared.get("available"):
            from flygi.arc.factory import build_connectome_policy

            assembled = build_connectome_policy(
                shared["config"],
                GameAction,
                runtime_dir=shared["runtime_dir"],
                bundle=shared["bundle"],
                projection=shared["projection"],
            )
            self._policy = assembled.policy
            self._mode = "connectome"
            self._detail = (
                f"{shared['bundle'].node_count} nodes / "
                f"{shared['bundle'].edge_count} edges, K={self._policy.internal_steps}"
            )
        else:
            seed = _seed_for_game(str(self.game_id)) if rng_seed is None else int(rng_seed)
            self._policy = RandomLegalPolicy(GameAction, seed=seed)
            self._mode = "random-legal"
            self._detail = str(shared.get("reason", "unknown"))
        print(f"FlyGI agent mode={self._mode} ({self._detail})", flush=True)

    @property
    def name(self) -> str:
        return f"{super().name}.{self.MAX_ACTIONS}.{self._mode}"

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        del frames
        return self._policy.is_done(latest_frame)

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
        del frames
        return self._policy.choose_action(latest_frame)  # type: ignore[return-value]
