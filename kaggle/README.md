# Kaggle adapter

This directory is the thin deployment boundary between FlyGI and the official
ARC-AGI-3 competition harness. The implementation deliberately keeps
`src/flygi` free of imports from Kaggle, `arcengine`, and the official agent
framework.

## Verified upstream contract

The Milestone 0 adapter was checked on 2026-09-19 against these official
sources:

- [ARC-AGI-3 Kaggle Starter](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter/tree/eeb1535404f321d280a8f9194bbc1d7aca5f05fc), commit `eeb1535404f321d280a8f9194bbc1d7aca5f05fc`.
- [ARC-AGI-3-Agents](https://github.com/arcprize/ARC-AGI-3-Agents/tree/4743e7d0aaae0ded0d98a89a7e282e63564cd58b), commit `4743e7d0aaae0ded0d98a89a7e282e63564cd58b`.
- [ARCEngine](https://github.com/arcprize/ARCEngine/tree/b495c6acaf253c9681cd7b75c4299d352e9ce6f8), commit `b495c6acaf253c9681cd7b75c4299d352e9ce6f8`.

The resulting assumptions are:

1. The submission class subclasses `agents.agent.Agent`, is named `MyAgent`,
   and implements `is_done(frames, latest_frame)` plus
   `choose_action(frames, latest_frame)`.
2. `arcengine.FrameData.available_actions` is a list of integer action IDs.
   The adapter resolves only those IDs, so it cannot sample an action outside
   the current game's declared mask.
3. `GameAction.RESET` has ID 0; `ACTION1` through `ACTION7` have IDs 1 through
   7. `ACTION6` is the complex action and requires integer `x` and `y` values
   in the inclusive range 0 to 63.
4. `NOT_PLAYED` and `GAME_OVER` require `RESET`; `WIN` ends the agent loop.
5. The official starter targets Python 3.12 and generates an internet-disabled
   Kaggle notebook. Runtime code and later connectome assets must therefore be
   available before evaluation.

The upstream starter's sample chooses from the whole enum. FlyGI intentionally
uses the frame's `available_actions` mask because this repository's baseline is
a *random legal* agent.

## Local smoke test

The test uses tiny stand-ins for `arcengine` and `agents`, so contributors can
validate adapter wiring before installing the competition runtime:

```bash
pytest tests/test_kaggle_smoke.py
```

An actual local game still requires Python 3.12, `arc-agi`, and a checkout of
the official ARC-AGI-3-Agents framework as described by the
[official starter](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter).

## Offline source bundle

`make notebook` builds this source bundle deterministically and embeds it in the
generated Milestone 0 notebook, including the `PYTHONPATH` handoff to the
framework subprocess. To build the same runtime as a standalone artifact:

```bash
python kaggle/build_assets.py
```

The output is `kaggle/dist/flygi_runtime.zip`. A future full-graph submission
can publish this alongside compiled graph assets in a Kaggle Dataset instead of
embedding it. The standalone bundle's manifest records every bundled source
hash and the upstream interface revisions.

Milestone 0 does **not** bundle a connectome. Later packaging must add compiled
graph arrays and their provenance manifest beside this runtime zip; the
evaluation notebook must never download MaleCNS or call neuPrint.
