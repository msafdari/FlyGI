#!/usr/bin/env python3
"""Milestone 4 entry point reserved by the repository contract."""


def main() -> None:
    raise SystemExit(
        "Null generation is intentionally deferred until Milestone 4; see docs/controls.md."
    )


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("build_nulls", main))
