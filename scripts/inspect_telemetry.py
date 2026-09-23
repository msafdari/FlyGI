#!/usr/bin/env python3
"""Summarize or query telemetry logs written by any instrumented component.

Telemetry is only useful if reading it is easier than reading the source that
produced it. This is the reader: it answers what a run did, when, where, how long
each stage took, and why it ended, without the caller knowing any event names.

    uv run python scripts/inspect_telemetry.py                  # recent runs
    uv run python scripts/inspect_telemetry.py --run <run_id>   # one run in full
    uv run python scripts/inspect_telemetry.py --run <id> --events eval.row.end
    uv run python scripts/inspect_telemetry.py --failures       # only bad endings
    uv run python scripts/inspect_telemetry.py --json           # machine-readable

The ``--json`` form emits one object per run with the same fields as the table,
so another tool can consume it without parsing the display.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "results" / "telemetry"


def read_events(path: Path) -> list[dict[str, Any]]:
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            # A run killed mid-write leaves a partial final line. Keeping the
            # complete events is the whole point of an append-only log.
            continue
    return events


def summarize(path: Path) -> dict[str, Any]:
    events = read_events(path)
    if not events:
        return {"file": path.name, "status": "empty", "events": 0}
    start = next((e for e in events if e["event"] == "run.start"), None)
    end = next((e for e in reversed(events) if e["event"] == "run.end"), None)
    start_data = (start or {}).get("data", {})
    end_data = (end or {}).get("data", {})
    levels = Counter(e.get("level", "info") for e in events)
    phases = [
        (e["data"]["name"], e["data"]["duration_s"])
        for e in events
        if e["event"] == "phase.end" and "duration_s" in e.get("data", {})
    ]
    return {
        "file": path.name,
        "run_id": events[0].get("run_id"),
        "component": events[0].get("component"),
        "started": events[0].get("ts"),
        # A run with no run.end was killed or is still going; say so rather than
        # reporting it as a failure or silently as a success.
        "status": end_data.get("status", "incomplete_or_running"),
        "reason": end_data.get("reason"),
        "duration_s": end_data.get("duration_s", events[-1].get("elapsed_s")),
        "events": len(events),
        "warnings": levels.get("warning", 0),
        "errors": levels.get("error", 0),
        "counters": end_data.get("counters", {}),
        "git_commit": (start_data.get("git_commit") or "")[:8] or None,
        "git_dirty": start_data.get("git_dirty"),
        "argv": start_data.get("argv"),
        "slowest_phases": sorted(phases, key=lambda x: -x[1])[:3],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--run", default=None, help="run_id or filename substring")
    parser.add_argument("--component", default=None)
    parser.add_argument("--events", nargs="+", default=None, help="event names to print")
    parser.add_argument("--failures", action="store_true", help="only runs that did not end ok")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.dir.is_dir():
        print(f"no telemetry directory at {args.dir}")
        return 0
    files = sorted(args.dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if args.run:
        files = [p for p in files if args.run in p.name]
    summaries = [summarize(p) for p in files]
    if args.component:
        summaries = [s for s in summaries if s.get("component") == args.component]
    if args.failures:
        summaries = [s for s in summaries if s.get("status") != "ok"]
    summaries = summaries[: args.limit]

    if args.events and args.run:
        for path in files:
            for event in read_events(path):
                if event["event"] in args.events:
                    print(json.dumps(event, sort_keys=True))
        return 0
    if args.as_json:
        print(json.dumps(summaries, indent=2, sort_keys=True, default=str))
        return 0

    if not summaries:
        print("no telemetry runs matched")
        return 0
    print(f"{'component':26} {'status':22} {'dur(s)':>9} {'ev':>5} {'warn':>5} {'err':>4}  started")
    for s in summaries:
        print(
            f"{s.get('component')!s:26} {s.get('status')!s:22} "
            f"{float(s.get('duration_s') or 0):>9.1f} {s.get('events', 0):>5} "
            f"{s.get('warnings', 0):>5} {s.get('errors', 0):>4}  {s.get('started')}"
        )
        if s.get("reason"):
            print(f"{'':26} reason: {s['reason']}")
        if s.get("counters"):
            print(f"{'':26} counters: {s['counters']}")
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("inspect_telemetry", main))
