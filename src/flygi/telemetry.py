"""Structured execution telemetry for every runnable component.

Result bundles already record *provenance*: which graph, which config, which
game, hashed. What they have never recorded is *execution* -- what the run did,
in what order, how long each part took, what it decided and why, and how it
ended. That lived in ad-hoc ``print`` calls whose format differed per script, so
reconstructing a run meant reading the source that produced it.

This module is the single place that changes. Every runnable component opens a
``Run``, emits typed events, and closes it. Each event is one JSON object on one
line:

    {"ts":"2026-09-23T10:41:07.123456+00:00","elapsed_s":12.34,
     "run_id":"20260923T104055Z-evaluate_state_graph-a1b2c3d4",
     "component":"evaluate_state_graph","event":"eval.row.end","level":"info",
     "seq":417,"data":{...}}

The five questions a reader or tool should be able to answer without the source:

- **what** -- ``event`` plus ``data``; names are dotted and hierarchical.
- **when** -- ``ts`` is wall clock, ``elapsed_s`` is monotonic since run start,
  and ``seq`` orders events even when two share a timestamp.
- **where** -- the ``run.start`` event carries git commit and dirty flag, host,
  platform, Python and package versions, pid, argv, cwd, and the resolved paths
  and SHA-256 of every config the run read.
- **how** -- ``phase.begin``/``phase.end`` bracket the stages, each ``phase.end``
  carrying its own duration, so a slow run can be attributed without profiling.
- **why** -- every decision, skip, fallback, warning and failure carries a
  ``reason`` string. An event that changes what the run does and cannot say why
  is a bug in the instrumentation.

Design choices, stated because they constrain consumers:

- **JSONL, append-only, one event per line.** Survives a killed process: a run
  that dies mid-way leaves every event up to that point, which is exactly when
  telemetry matters most. The repository already checkpoints result rows this
  way and several runs have been recovered from those files.
- **The console stays human-readable.** Telemetry is written to a file; the
  terminal keeps its existing prose. Machines read the file, people read the
  terminal, and neither is degraded for the other.
- **Never fatal.** A telemetry failure must not take down a six-hour evaluation,
  so emission swallows its own errors and records that it did.
- **No secrets.** Environment capture is an explicit allowlist, never the whole
  environment, because tokens live there.
"""

from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = "flygi.telemetry"
SCHEMA_VERSION = 1

# ASSUMPTION: these are the environment variables worth recording. The whole
# environment is deliberately NOT captured because credentials live there. Add
# names here when a run's behaviour depends on one; never add a secret.
_ENVIRONMENT_ALLOWLIST = (
    "FLYGI_ALLOW_RANDOM_FALLBACK",
    "FLYGI_RUNTIME_DIR",
    "KAGGLE_IS_COMPETITION_RERUN",
    "CI",
    "FORCE_COLOR",
    "PLAYWRIGHT_BROWSERS_PATH",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
)

DEFAULT_TELEMETRY_DIR = Path("results") / "telemetry"


def _git(*arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip() if completed.returncode == 0 else None


def _package_versions() -> dict[str, str]:
    from importlib.metadata import PackageNotFoundError, version

    found: dict[str, str] = {}
    for name in ("flygi", "numpy", "scipy", "arcengine", "arc-agi", "pandas"):
        try:
            found[name] = version(name)
        except PackageNotFoundError:
            continue
    return found


def sha256_file(path: str | Path) -> str | None:
    """Digest a file, or None if it cannot be read. Never raises."""

    import hashlib

    try:
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
        return digest.hexdigest()
    except OSError:
        return None


@dataclass
class Run:
    """One instrumented execution of one component."""

    component: str
    path: Path
    run_id: str
    started_monotonic: float
    _sequence: int = 0
    _counters: dict[str, float] = field(default_factory=dict)
    _phase_stack: list[tuple[str, float]] = field(default_factory=list)
    _emit_failures: int = 0
    _closed: bool = False

    # -- emission ----------------------------------------------------------
    def emit(self, event: str, level: str = "info", **data: Any) -> None:
        """Append one event. Never raises, never blocks the run."""

        if self._closed:
            return
        self._sequence += 1
        record = {
            "ts": datetime.now(UTC).isoformat(),
            "elapsed_s": round(time.monotonic() - self.started_monotonic, 6),
            "seq": self._sequence,
            "run_id": self.run_id,
            "component": self.component,
            "event": event,
            "level": level,
        }
        if data:
            record["data"] = data
        try:
            line = json.dumps(record, sort_keys=True, default=str, allow_nan=False)
        except Exception:
            # Deliberately broad. ``default=str`` invokes ``__repr__`` on the
            # payload, which is arbitrary user code and can raise anything at
            # all. A six-hour evaluation must not die because one event carried
            # an awkward object, so the event degrades to a warning that names
            # the problem and the run continues.

            self._emit_failures += 1
            line = json.dumps(
                {
                    **{k: v for k, v in record.items() if k != "data"},
                    "level": "warning",
                    "data": {"telemetry_error": "payload was not serializable"},
                },
                sort_keys=True,
            )
        try:
            with open(self.path, "a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        except OSError:
            self._emit_failures += 1

    # Convenience levels. `reason` is mandatory on anything that explains a
    # decision, because "why" is the question logs are worst at answering.
    def info(self, event: str, **data: Any) -> None:
        self.emit(event, "info", **data)

    def decision(self, event: str, *, reason: str, **data: Any) -> None:
        self.emit(event, "info", reason=reason, **data)

    def warning(self, event: str, *, reason: str, **data: Any) -> None:
        self.emit(event, "warning", reason=reason, **data)

    def error(self, event: str, *, reason: str, **data: Any) -> None:
        self.emit(event, "error", reason=reason, **data)

    # -- structure ---------------------------------------------------------
    @contextmanager
    def phase(self, name: str, **data: Any):
        """Bracket a stage so its duration is attributable without profiling."""

        self._phase_stack.append((name, time.monotonic()))
        self.emit("phase.begin", name=name, depth=len(self._phase_stack), **data)
        failed: BaseException | None = None
        try:
            yield self
        except BaseException as exc:
            failed = exc
            raise
        finally:
            _, started = self._phase_stack.pop()
            duration = round(time.monotonic() - started, 6)
            if failed is None:
                self.emit("phase.end", name=name, duration_s=duration, ok=True)
            else:
                self.emit(
                    "phase.end",
                    "error",
                    name=name,
                    duration_s=duration,
                    ok=False,
                    reason=f"{type(failed).__name__}: {failed}",
                )

    def count(self, name: str, amount: float = 1.0) -> None:
        """Accumulate a running total, summarized at run.end."""

        self._counters[name] = self._counters.get(name, 0.0) + amount

    def artifact(self, kind: str, path: str | Path, *, hashed: bool = True, **data: Any) -> None:
        """Record a file this run produced or consumed."""

        resolved = Path(path)
        self.emit(
            "artifact",
            kind=kind,
            path=str(resolved),
            exists=resolved.exists(),
            bytes=resolved.stat().st_size if resolved.is_file() else None,
            sha256=sha256_file(resolved) if hashed and resolved.is_file() else None,
            **data,
        )

    def config(self, path: str | Path, **data: Any) -> None:
        """Record a configuration file the run read, with its digest."""

        self.artifact("config", path, **data)

    def close(self, *, status: str, reason: str | None = None, **data: Any) -> None:
        if self._closed:
            return
        self.emit(
            "run.end",
            "info" if status == "ok" else "error",
            status=status,
            reason=reason,
            duration_s=round(time.monotonic() - self.started_monotonic, 6),
            events=self._sequence,
            counters=dict(sorted(self._counters.items())),
            telemetry_emit_failures=self._emit_failures,
            **data,
        )
        self._closed = True


def _run_identifier(component: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{component}-{uuid.uuid4().hex[:8]}"


@contextmanager
def instrument(
    component: str,
    *,
    argv: list[str] | None = None,
    directory: str | Path | None = None,
    **context: Any,
):
    """Open a telemetry run for one component, and always close it.

    Used as the outermost wrapper of a script's ``main``. The run closes with
    ``ok``, ``failed`` or ``interrupted``, so a log always states how it ended
    rather than simply stopping.
    """

    target = Path(directory) if directory is not None else DEFAULT_TELEMETRY_DIR
    run_id = _run_identifier(component)
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError:
        target = Path(".")
    run = Run(
        component=component,
        path=target / f"{run_id}.jsonl",
        run_id=run_id,
        started_monotonic=time.monotonic(),
    )
    commit = _git("rev-parse", "HEAD")
    dirty = _git("status", "--porcelain")
    run.emit(
        "run.start",
        schema=SCHEMA,
        schema_version=SCHEMA_VERSION,
        argv=list(argv if argv is not None else sys.argv),
        cwd=str(Path.cwd()),
        pid=os.getpid(),
        host=socket.gethostname(),
        platform=platform.platform(),
        python=sys.version.split()[0],
        packages=_package_versions(),
        git_commit=commit,
        git_dirty=bool(dirty) if dirty is not None else None,
        environment={
            name: os.environ[name] for name in _ENVIRONMENT_ALLOWLIST if name in os.environ
        },
        cpu_count=os.cpu_count(),
        **context,
    )
    try:
        yield run
    except KeyboardInterrupt:
        run.close(status="interrupted", reason="KeyboardInterrupt")
        raise
    except SystemExit as exc:
        # argparse exits this way for --help and for a usage error, and scripts
        # end with `raise SystemExit(main())`. Code 0 or None is a normal ending
        # and must not be recorded as a failure, or every --help poisons the
        # failure list and real failures stop standing out.
        code = exc.code
        if code in (0, None):
            run.close(status="ok", exit_code=0)
        else:
            run.close(status="failed", reason=f"SystemExit: {code}", exit_code=code)
        raise
    except BaseException as exc:
        run.close(status="failed", reason=f"{type(exc).__name__}: {exc}")
        raise
    else:
        run.close(status="ok")


def entrypoint(component: str, main: Any, argv: list[str] | None = None) -> int:
    """Run a script's ``main`` inside a telemetry run and return its exit code.

    One line at each script's ``__main__`` gives every component the same
    guarantees: a ``run.start`` recording where and how it was invoked, a
    ``run.end`` recording how it finished, and a recorded cause when it does not
    finish. Scripts that want phase and decision events open them through
    ``current_run()``.
    """

    global _CURRENT
    with instrument(component, argv=argv) as run:
        _CURRENT = run
        try:
            result = main() if argv is None else main(argv)
        finally:
            _CURRENT = None
        code = 0 if result is None else int(result)
        if code != 0:
            run.warning("run.nonzero_exit", reason=f"main returned {code}", exit_code=code)
        return code


_CURRENT: Run | None = None


def current_run() -> Run | None:
    """The telemetry run for the component executing now, if instrumented.

    Returns None when a module is imported by a test or another script rather
    than run as an entry point, so instrumentation never forces a dependency.
    """

    return _CURRENT


class _NullRun:
    """Stands in for a Run when nothing is instrumented, so callers need no branch."""

    def __getattr__(self, _name: str) -> Any:
        def _noop(*_args: Any, **_kwargs: Any) -> None:
            return None

        return _noop

    @contextmanager
    def phase(self, *_args: Any, **_kwargs: Any):
        yield self


NULL_RUN = _NullRun()


def run_or_null() -> Any:
    """``current_run()`` if instrumented, else a no-op stand-in."""

    return _CURRENT if _CURRENT is not None else NULL_RUN
