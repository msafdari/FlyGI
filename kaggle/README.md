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

## Publishing a connectome submission

The notebook runs with internet disabled, so the compiled MaleCNS runtime must
be attached as a Kaggle Dataset before it can be a connectome run. Without it
the ordinary notebook preflight and an official competition rerun both fail
closed. A missing or corrupt asset can therefore never silently turn a FlyGI
submission into a random-agent result.

Every ordinary notebook run imports the adapter without starting a game,
discovers the attached runtime, verifies every manifest output hash, assembles
the policy, and prints one machine-readable log line beginning
`FLYGI_PREFLIGHT=`. For the current signed bundle, that JSON must report
`mode=connectome`, `verified=true`, 166,700 nodes, 24,559,055 edges, `K=4`,
release `male-cns:v1.0`, heuristic signs, and the verified output digests.

The random-legal adapter path is retained only for local import/unit smokes. It
requires the explicit constructor argument `allow_random_fallback=True` or the
environment variable `FLYGI_ALLOW_RANDOM_FALLBACK=1`; an official competition
rerun ignores both opt-ins and still fails closed.

The order matters. `notebooks/kernel-metadata.json` already declares
`dataset_sources`, so pushing the notebook before the dataset exists will fail.

```bash
# 1. Stage and self-verify the offline bundle (uploads nothing).
uv run python scripts/package_kaggle_dataset.py --config configs/literal_rate_signed.yaml

# 2. Review kaggle/dist/dataset/, then publish it privately. ~95 MB.
KAGGLE_API_TOKEN=$(cat .kaggle/access_token) uv run kaggle datasets create \
  -p kaggle/dist/dataset --dir-mode zip

# 3. Build and push the notebook. This does not spend a submission.
make submit

# 4. Confirm the ordinary run log contains a verified FLYGI_PREFLIGHT JSON line.
make status
```

Later dataset updates use `kaggle datasets version -p kaggle/dist/dataset -m "<message>"`.

Publishing a dataset and spending a competition submission are outward-facing
actions on the account owner's behalf. Passing the local acceptance gates does
not confer standing permission for either; each needs explicit authorization.
