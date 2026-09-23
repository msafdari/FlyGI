#!/usr/bin/env python3
"""Recover interrupted evaluation runs after a reboot, crash, or kill.

Every completed row of every evaluation is already checkpointed to
`<condition>.rows.jsonl`, and rows are independent and deterministic given
(seed, game), so an interrupted run loses at most the row that was in flight.
What was missing is the recovery step itself: after a reboot the exact launch
command lives nowhere a human can be relied on to find it.

It does live somewhere a machine can: telemetry records every run's full argv
at `run.start`. This tool joins three facts --

  1. a telemetry run of `evaluate_state_graph` exists with no `run.end`
     status of `ok` (killed, crashed, rebooted, or still running),
  2. its condition has a checkpoint with completed rows,
  3. no final result bundle for that condition exists,

-- and prints the exact command to continue each such run, `--resume` and all.
Nothing is executed unless `--exec` is passed, and a process currently running
for the same condition is detected and skipped, so this is safe to run at any
time, including while arms are healthy.

    uv run python scripts/resume_runs.py          # show what would be resumed
    uv run python scripts/resume_runs.py --exec   # actually relaunch them
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TELEMETRY = ROOT / "results" / "telemetry"
RESULTS = ROOT / "results" / "connectome_agent"


def _events(path: Path) -> list[dict[str, Any]]:
    out = []
    try:
        for line in path.read_text().splitlines():
            if line.strip():
                out.append(json.loads(line))
    except (OSError, json.JSONDecodeError):
        pass
    return out


def _condition_from_argv(argv: list[str]) -> str | None:
    for index, token in enumerate(argv):
        if token == "--condition" and index + 1 < len(argv):
            return argv[index + 1]
    return None


def _running_conditions() -> set[str]:
    try:
        listing = subprocess.run(
            ["ps", "-axo", "command"], capture_output=True, text=True, timeout=10, check=False
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    found = set()
    for line in listing.splitlines():
        if "evaluate_state_graph" in line and "--condition" in line:
            parts = line.split()
            condition = _condition_from_argv(parts)
            if condition:
                found.add(condition)
    return found


def find_resumable() -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for path in sorted(TELEMETRY.glob("*evaluate_state_graph*.jsonl")):
        events = _events(path)
        if not events:
            continue
        start = next((e for e in events if e["event"] == "run.start"), None)
        if start is None:
            continue
        argv = list(start.get("data", {}).get("argv") or [])
        condition = _condition_from_argv(argv)
        if not condition:
            continue
        end = next((e for e in reversed(events) if e["event"] == "run.end"), None)
        status = (end or {}).get("data", {}).get("status", "no-run.end")
        # newest telemetry run per condition wins
        latest[condition] = {"argv": argv, "status": status, "telemetry": path.name}

    running = _running_conditions()
    resumable = []
    for condition, record in sorted(latest.items()):
        bundle = RESULTS / f"{condition}.json"
        checkpoint = RESULTS / f"{condition}.rows.jsonl"
        if bundle.exists():
            continue  # finished; nothing to do
        if record["status"] == "ok":
            continue  # ended cleanly without a bundle here (moved output); leave it
        rows = 0
        if checkpoint.exists():
            rows = sum(1 for line in checkpoint.read_text().splitlines() if line.strip())
        # argv[0] is the script path as invoked; rebuild as `uv run python <script> ...`
        script_and_args = record["argv"]
        if "--resume" not in script_and_args:
            script_and_args = [*script_and_args, "--resume"]
        resumable.append(
            {
                "condition": condition,
                "rows_completed": rows,
                "last_status": record["status"],
                "currently_running": condition in running,
                "command": ["uv", "run", "python", *script_and_args],
                "telemetry": record["telemetry"],
            }
        )
    return resumable


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exec", action="store_true", dest="execute")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    from flygi.telemetry import run_or_null

    telemetry = run_or_null()
    resumable = find_resumable()
    telemetry.info(
        "resume.scan",
        candidates=len(resumable),
        running=sum(1 for r in resumable if r["currently_running"]),
    )
    if args.as_json:
        print(json.dumps(resumable, indent=2))
        return 0
    if not resumable:
        print("nothing to resume: every known run either finished or is not resumable")
        return 0
    for record in resumable:
        state = "RUNNING (skip)" if record["currently_running"] else "resumable"
        print(
            f"{record['condition']:26} {record['rows_completed']:>3} rows done  "
            f"last={record['last_status']:<12} {state}"
        )
        print(f"    {' '.join(record['command'])}")
        if args.execute and not record["currently_running"]:
            telemetry.decision(
                "resume.launch",
                reason=f"no bundle, {record['rows_completed']} rows checkpointed, not running",
                condition=record["condition"],
            )
            log_path = ROOT / "results" / f"resume-{record['condition']}.log"
            with open(log_path, "ab") as log:
                subprocess.Popen(  # argv comes from our own telemetry
                    record["command"],
                    cwd=ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            print("    -> launched")
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("resume_runs", main))
