"""Telemetry must survive the conditions that make it worth having.

These are not format tests. Each one covers a way telemetry has to behave when
something goes wrong, because a log that only works on the happy path is a log
that is absent exactly when it is needed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from flygi.telemetry import NULL_RUN, current_run, entrypoint, instrument, run_or_null


def _events(directory: Path) -> list[dict]:
    path = next(iter(directory.glob("*.jsonl")))
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_a_run_records_where_and_how_it_started(tmp_path: Path) -> None:
    with instrument("unit", directory=tmp_path, note="hello"):
        pass
    start = _events(tmp_path)[0]
    assert start["event"] == "run.start"
    for key in ("argv", "cwd", "pid", "host", "platform", "python", "packages", "cpu_count"):
        assert key in start["data"], f"run.start cannot answer 'where': missing {key}"
    assert start["data"]["note"] == "hello"


def test_a_failed_run_records_why_it_failed(tmp_path: Path) -> None:
    """A log that simply stops cannot be distinguished from one still running."""

    with pytest.raises(ValueError), instrument("unit", directory=tmp_path):
        raise ValueError("deliberate")
    end = _events(tmp_path)[-1]
    assert end["event"] == "run.end"
    assert end["data"]["status"] == "failed"
    assert "deliberate" in end["data"]["reason"]


def test_an_interrupted_run_is_distinguished_from_a_failure(tmp_path: Path) -> None:
    with pytest.raises(KeyboardInterrupt), instrument("unit", directory=tmp_path):
        raise KeyboardInterrupt
    assert _events(tmp_path)[-1]["data"]["status"] == "interrupted"


def test_phases_record_their_own_duration_and_outcome(tmp_path: Path) -> None:
    with instrument("unit", directory=tmp_path) as run:
        with run.phase("ok_phase"):
            pass
        with pytest.raises(RuntimeError), run.phase("bad_phase"):
            raise RuntimeError("inner")
    ends = {e["data"]["name"]: e["data"] for e in _events(tmp_path) if e["event"] == "phase.end"}
    assert ends["ok_phase"]["ok"] is True
    assert ends["bad_phase"]["ok"] is False
    assert "inner" in ends["bad_phase"]["reason"]
    assert ends["ok_phase"]["duration_s"] >= 0.0


def test_emission_never_takes_down_the_run(tmp_path: Path) -> None:
    """A six-hour evaluation must not die because a payload was odd."""

    class Unserializable:
        def __repr__(self) -> str:
            raise RuntimeError("cannot repr")

    with instrument("unit", directory=tmp_path) as run:
        run.info("weird", value={1, 2, 3})
        run.info("worse", value=Unserializable())
    end = _events(tmp_path)[-1]
    assert end["data"]["status"] == "ok"


def test_events_are_ordered_even_within_one_timestamp(tmp_path: Path) -> None:
    with instrument("unit", directory=tmp_path) as run:
        for index in range(50):
            run.info("tick", index=index)
    sequences = [e["seq"] for e in _events(tmp_path)]
    assert sequences == sorted(sequences)
    assert len(set(sequences)) == len(sequences)


def test_counters_are_summarized_at_the_end(tmp_path: Path) -> None:
    with instrument("unit", directory=tmp_path) as run:
        run.count("rows", 2)
        run.count("rows")
        run.count("levels", 5)
    counters = _events(tmp_path)[-1]["data"]["counters"]
    assert counters == {"levels": 5.0, "rows": 3.0}


def test_decisions_and_warnings_must_carry_a_reason(tmp_path: Path) -> None:
    with instrument("unit", directory=tmp_path) as run:
        run.decision("chose", reason="config said so")
        run.warning("odd", reason="value out of band")
    by_event = {e["event"]: e for e in _events(tmp_path)}
    assert by_event["chose"]["data"]["reason"] == "config said so"
    assert by_event["odd"]["level"] == "warning"


def test_secrets_are_not_captured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAGGLE_API_TOKEN", "super-secret")
    monkeypatch.setenv("FLYGI_RUNTIME_DIR", "/attached/runtime")
    with instrument("unit", directory=tmp_path):
        pass
    environment = _events(tmp_path)[0]["data"]["environment"]
    assert "KAGGLE_API_TOKEN" not in environment, "a secret reached the telemetry log"
    assert environment["FLYGI_RUNTIME_DIR"] == "/attached/runtime"


def test_uninstrumented_code_gets_a_no_op_rather_than_a_crash() -> None:
    """Modules imported by tests have no run; they must not need to branch."""

    assert current_run() is None
    stand_in = run_or_null()
    assert stand_in is NULL_RUN
    stand_in.info("ignored", value=1)
    stand_in.count("nothing")
    with stand_in.phase("also ignored"):
        pass


def test_entrypoint_returns_the_exit_code_and_flags_nonzero(tmp_path: Path) -> None:
    assert entrypoint("unit", lambda: 0) == 0
    assert entrypoint("unit", lambda: None) == 0
    assert entrypoint("unit", lambda: 3) == 3


def test_a_clean_systemexit_is_not_a_failure(tmp_path: Path) -> None:
    """argparse --help exits this way; recording it as failed poisons the log."""

    with pytest.raises(SystemExit), instrument("unit", directory=tmp_path):
        raise SystemExit(0)
    assert _events(tmp_path)[-1]["data"]["status"] == "ok"


def test_a_nonzero_systemexit_is_a_failure(tmp_path: Path) -> None:
    with pytest.raises(SystemExit), instrument("unit", directory=tmp_path):
        raise SystemExit(2)
    end = _events(tmp_path)[-1]["data"]
    assert end["status"] == "failed"
    assert end["exit_code"] == 2
