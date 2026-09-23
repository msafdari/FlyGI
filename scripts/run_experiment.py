#!/usr/bin/env python3
"""Milestone 4 paired experiment entry point reserved by the repository contract."""


def main() -> None:
    raise SystemExit(
        "Paired ARC experiments are intentionally deferred until controls exist in Milestone 4."
    )


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("run_experiment", main))
