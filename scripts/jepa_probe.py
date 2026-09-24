#!/usr/bin/env python3
"""H-JEPA-SPONTANEOUS probe: does N_t already carry predictive structure?

Implements the protocol frozen in EXPERIMENTS.yaml
(protocol_frozen_2026_09_24) -- see that block for every registered choice.
Summary of the machinery:

  * One shared sample set per game: t in [W_eff, T-6] whose (t, t+5) window
    crosses no RESET action and no GAME_OVER/WIN frame, so every horizon and
    every arm scores the identical samples. W_eff = max(ESP washout, 7) so
    the deepest delay embedding (L=8) is always fully defined.
  * Dual/Gram ridge, one probe per (arm, outer fold): per-feature z-score
    (train rows only, 1e-8 floor), per-target centering (train mean), Grams
    accumulated in feature blocks so no arm ever materialises a full
    standardized matrix. Lambda from a 9-point grid (1e-2..1e6), selected by
    inner game-level CV (4 inner folds) with full re-standardization.
  * Metrics per test game per horizon: change-masked pooled R^2 (primary),
    unmasked pooled R^2, macro per-dim R^2, beat-the-copy-floor fraction.
    The copy floor B0a (y_hat_{t+k} = y_t) is scored on the same masks.
  * Controls: horizon 0 in the same sweep; shuffled-time (within-game target
    permutation, identical protocol) for the real arm; memory curve
    (targets y_{t-j}) for the state arms; state-health diagnostics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STREAMS = ROOT / "results" / "jepa" / "streams"
STATES = ROOT / "results" / "jepa" / "states"
ESP = ROOT / "results" / "jepa" / "esp.json"
OUT = ROOT / "results" / "jepa" / "probe_results.json"
CONFIG = ROOT / "configs" / "literal_rate_bioeye_t4t5.yaml"

HORIZONS = (0, 1, 2, 3, 4, 5)
MAX_K = 5
DECIDING_K = 1
LAMBDAS = np.logspace(-2, 6, 9)
FOLD_SEED = 20260924
INNER_FOLDS = 4
B2_DEPTHS = (1, 2, 4, 8)
B2P_SEEDS = (0, 1, 2)
B2P_DIM = 29291
MEMORY_LAGS = tuple(range(1, 9))
BLOCK = 8192
RESET_ACTION_ID = 0
TERMINAL_STATES = ("GAME_OVER", "WIN")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _build_projection() -> tuple[Any, np.ndarray]:
    from flygi.config import load_config
    from flygi.encoding.retinotopic import build_columnar_colour_projection

    config = load_config(CONFIG)
    projection = build_columnar_colour_projection(Path(config.graph.output_dir), 166_700)
    occupied = np.unique(projection._column_key)
    if occupied.size != 892:
        raise RuntimeError(f"expected 892 occupied columns, found {occupied.size}")
    return projection, occupied


def load_game_data() -> dict[str, dict[str, Any]]:
    """Targets, eligibility, and per-game arrays for every captured game."""

    projection, occupied = _build_projection()
    esp = json.loads(ESP.read_text())
    washout = esp["recommended_washout"]
    if washout is None:
        # Registered fallback (protocol_frozen_2026_09_24): trajectories from
        # different initial states did not merge, so every claim is
        # per-trajectory -- specifically the zeros-init trajectory, which is
        # what the deployed agent actually runs. W falls back to the
        # criterion's frame-50 bound as a transient burn-in.
        washout = esp["criterion"]["fallback_frame"]
        print("ESP did not converge: claims are per-trajectory (zeros init)", flush=True)
    # Floor of 8: the deepest delay embedding needs t-7 and the memory curve
    # needs t-8; a smaller washout would wrap indices at the stream start.
    w_eff = max(int(washout), max(MEMORY_LAGS))

    games: dict[str, dict[str, Any]] = {}
    for stream_path in sorted(STREAMS.glob("*.npz")):
        with np.load(stream_path) as archive:
            grids = np.asarray(archive["grids"], dtype=np.int8)
            actions = np.asarray(archive["action_ids"])
            states = archive["states"]
        frame_count = grids.shape[0]
        targets = np.empty((frame_count, occupied.size * 15), dtype=np.float32)
        for index in range(frame_count):
            histogram = projection.column_histogram(grids[index])
            targets[index] = histogram[occupied, :].astype(np.float32).ravel()
        terminal = np.isin(states, TERMINAL_STATES)
        eligible = []
        for t in range(w_eff, frame_count - MAX_K - 1):
            window_actions = actions[t : t + MAX_K]
            window_frames = terminal[t + 1 : t + MAX_K + 1]
            if (window_actions == RESET_ACTION_ID).any() or window_frames.any():
                continue
            eligible.append(t)
        games[stream_path.stem] = {
            "targets": targets,
            "eligible": np.asarray(eligible, dtype=np.int64),
        }
    total = sum(g["eligible"].size for g in games.values())
    print(f"loaded {len(games)} games, washout={w_eff}, eligible samples={total}", flush=True)
    return games


def _state_features(condition: str, game: str) -> np.ndarray:
    with np.load(STATES / condition / f"{game}.npz") as archive:
        return np.asarray(archive["states"])  # float16 (T, 29291)


def _delay_rows(targets: np.ndarray, rows: np.ndarray, depth: int) -> np.ndarray:
    parts = [targets[rows - j] for j in range(depth)]
    return np.concatenate(parts, axis=1)


class _B2Prime:
    """Fixed seeded sparse sign projection of the L=4 embedding, then tanh."""

    def __init__(self, seed: int, input_dim: int) -> None:
        from sklearn.random_projection import SparseRandomProjection

        self._proj = SparseRandomProjection(
            n_components=B2P_DIM,
            density=1.0 / np.sqrt(input_dim),
            random_state=seed,
        )
        self._proj.fit(np.zeros((1, input_dim), dtype=np.float32))

    def transform(self, block: np.ndarray) -> np.ndarray:
        return np.tanh(self._proj.transform(block)).astype(np.float32)


def make_arm_loader(arm: str, games: dict[str, dict[str, Any]]):
    """Return fn(game, rows) -> float32 feature matrix for those frame rows."""

    if arm in {"real", "null", "bypass"}:
        cache: dict[str, np.ndarray] = {}

        def load_state(game: str, rows: np.ndarray) -> np.ndarray:
            if game not in cache:
                cache[game] = _state_features(arm, game)
            return cache[game][rows].astype(np.float32)

        return load_state
    if arm == "b1":
        return lambda game, rows: games[game]["targets"][rows]
    if arm.startswith("b2_l"):
        depth = int(arm.removeprefix("b2_l"))
        return lambda game, rows: _delay_rows(games[game]["targets"], rows, depth)
    if arm.startswith("b2p_s"):
        seed = int(arm.removeprefix("b2p_s"))
        projector = _B2Prime(seed, input_dim=4 * games_first_dim(games))

        def load_b2p(game: str, rows: np.ndarray) -> np.ndarray:
            return projector.transform(_delay_rows(games[game]["targets"], rows, 4))

        return load_b2p
    if arm == "oracle":
        return lambda game, rows: _delay_rows(games[game]["targets"], rows, 8)
    raise ValueError(f"unknown arm {arm!r}")


def games_first_dim(games: dict[str, dict[str, Any]]) -> int:
    return next(iter(games.values()))["targets"].shape[1]


def _stack(
    loader, games: dict[str, dict[str, Any]], names: list[str]
) -> tuple[np.ndarray, list[tuple[str, int, int]]]:
    blocks, spans, cursor = [], [], 0
    for name in names:
        rows = games[name]["eligible"]
        block = loader(name, rows)
        blocks.append(block)
        spans.append((name, cursor, cursor + block.shape[0]))
        cursor += block.shape[0]
    return np.concatenate(blocks, axis=0), spans


def _standardize_stats(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std = np.maximum(std, 1e-8)
    return mean.astype(np.float32), std.astype(np.float32)


def _gram(a: np.ndarray, b: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    """(a-mean)/std @ ((b-mean)/std).T, feature-blocked, float64-accumulated.

    Normalized by feature count so Gram entries are O(1) regardless of arm
    dimensionality: the frozen protocol shares ONE lambda grid across arms
    of 13,380..107,040 features, which is only a like-for-like penalty if
    K does not scale with d. Float64 accumulation keeps rounding noise far
    below the smallest grid lambda (float32 accumulation produced negative
    eigenvalues bigger than 1e-2 and a potrf failure on the real data).
    """

    out = np.zeros((a.shape[0], b.shape[0]), dtype=np.float64)
    for start in range(0, a.shape[1], BLOCK):
        stop = min(start + BLOCK, a.shape[1])
        sa = (a[:, start:stop] - mean[start:stop]) / std[start:stop]
        sb = (b[:, start:stop] - mean[start:stop]) / std[start:stop]
        out += (sa @ sb.T).astype(np.float64)
    out /= a.shape[1]
    return out


def _solve_dual(
    k_train: np.ndarray, y_train: np.ndarray, lam: float
) -> tuple[np.ndarray, np.ndarray]:
    from scipy.linalg import cho_factor, cho_solve

    n = k_train.shape[0]
    kernel = (k_train + k_train.T) * 0.5 + lam * np.eye(n)
    try:
        factor = cho_factor(kernel, lower=True, check_finite=False)
    except np.linalg.LinAlgError:
        # Last-resort jitter, orders below any grid lambda; logged loudly.
        jitter = 1e-8 * float(np.trace(k_train)) / n
        print(f"cholesky jitter engaged: {jitter:.3e}", flush=True)
        factor = cho_factor(kernel + jitter * np.eye(n), lower=True, check_finite=False)
    # RHS solved in column chunks: a single float64 copy of all 13,380
    # targets plus its solution cost ~1.4 GB and, run three-wide, took the
    # whole machine down. Chunking bounds the transient to ~250 MB.
    alpha = np.empty(y_train.shape, dtype=np.float32)
    for start in range(0, y_train.shape[1], 2048):
        stop = min(start + 2048, y_train.shape[1])
        alpha[:, start:stop] = cho_solve(
            factor, y_train[:, start:stop].astype(np.float64), check_finite=False
        ).astype(np.float32)
    return factor, alpha


def _target_matrix(games: dict[str, dict[str, Any]], names: list[str], k: int) -> np.ndarray:
    return np.concatenate([games[n]["targets"][games[n]["eligible"] + k] for n in names], axis=0)


def _score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_now: np.ndarray,
    train_mean: np.ndarray,
) -> dict[str, float]:
    changed = y_true != y_now
    centred = y_true - train_mean
    sse = (y_true - y_pred) ** 2
    sse_floor = (y_true - y_now) ** 2
    tss = centred**2

    def pooled(mask: np.ndarray) -> float:
        denom = float(tss[mask].sum())
        return 1.0 - float(sse[mask].sum()) / denom if denom > 0 else float("nan")

    every = np.ones_like(changed)
    dim_var = tss.sum(axis=0)
    live = dim_var > 0
    macro = (
        float(np.mean(1.0 - sse.sum(axis=0)[live] / dim_var[live])) if live.any() else float("nan")
    )
    beat_floor = (
        float(np.mean(sse.sum(axis=0)[live] < sse_floor.sum(axis=0)[live]))
        if live.any()
        else float("nan")
    )
    return {
        "masked_r2": pooled(changed) if changed.any() else float("nan"),
        "unmasked_r2": pooled(every),
        "macro_r2": macro,
        "beat_floor_fraction": beat_floor,
        "changed_fraction": float(changed.mean()),
        "copy_masked_r2": (
            1.0 - float(sse_floor[changed].sum()) / float(tss[changed].sum())
            if changed.any() and tss[changed].sum() > 0
            else float("nan")
        ),
    }


def _folds(names: list[str], count: int, seed: int) -> list[list[str]]:
    rng = np.random.default_rng(seed)
    shuffled = list(names)
    rng.shuffle(shuffled)
    return [shuffled[i::count] for i in range(count)]


def _select_lambda(
    loader,
    games: dict[str, dict[str, Any]],
    train_names: list[str],
    horizons: tuple[int, ...],
) -> float:
    """Inner game-level CV over the registered grid; full re-standardization.

    Implementation note (uniform across arms, recorded in the result doc):
    the inner selection scores a seeded 1024-dim subsample of the 13,380
    targets, which cuts the inner solve cost ~13x without touching the
    outer evaluation, and the same subsample is used for every arm.
    """

    dim = games_first_dim(games)
    subsample = np.random.default_rng(FOLD_SEED + 3).choice(dim, size=min(1024, dim), replace=False)
    inner = _folds(train_names, INNER_FOLDS, FOLD_SEED + 1)
    losses = np.zeros(len(LAMBDAS))
    for fold in inner:
        fit_names = [n for n in train_names if n not in fold]
        x_fit, _ = _stack(loader, games, fit_names)
        x_val, _ = _stack(loader, games, fold)
        mean, std = _standardize_stats(x_fit)
        k_fit = _gram(x_fit, x_fit, mean, std)
        k_val = _gram(x_val, x_fit, mean, std)
        for k in horizons:
            y_fit = _target_matrix(games, fit_names, k)[:, subsample]
            y_val = _target_matrix(games, fold, k)[:, subsample]
            y_mean = y_fit.mean(axis=0)
            for index, lam in enumerate(LAMBDAS):
                _, alpha = _solve_dual(k_fit, y_fit - y_mean, float(lam))
                pred = k_val @ alpha + y_mean
                losses[index] += float(((y_val - pred) ** 2).sum())
        del x_fit, x_val, k_fit, k_val
    return float(LAMBDAS[int(np.argmin(losses))])


def run_arm(
    arm: str,
    games: dict[str, dict[str, Any]],
    horizons: tuple[int, ...],
    *,
    shuffle_targets: bool = False,
    memory_lags: tuple[int, ...] = (),
) -> dict[str, Any]:
    from flygi.telemetry import run_or_null

    telemetry = run_or_null()
    names = sorted(games)
    outer = _folds(names, 5, FOLD_SEED)
    per_game: dict[str, dict[str, Any]] = {n: {} for n in names}
    lambdas_chosen: list[float] = []
    dof_by_fold: list[float] = []
    shuffle_rng = np.random.default_rng(FOLD_SEED + 7)
    shuffled_rows: dict[str, np.ndarray] = {}
    if shuffle_targets:
        for n in names:
            rows = games[n]["eligible"].copy()
            shuffle_rng.shuffle(rows)
            shuffled_rows[n] = rows

    loader = make_arm_loader(arm, games)
    for fold_index, test_names in enumerate(outer):
        train_names = [n for n in names if n not in test_names]
        lam = _select_lambda(loader, games, train_names, tuple(h for h in horizons if h > 0))
        lambdas_chosen.append(lam)
        x_train, _ = _stack(loader, games, train_names)
        mean, std = _standardize_stats(x_train)
        k_train = _gram(x_train, x_train, mean, std)
        x_test, test_spans = _stack(loader, games, test_names)
        k_test = _gram(x_test, x_train, mean, std)
        del x_train, x_test

        # Effective degrees of freedom at the selected lambda, via a
        # Rademacher stochastic trace estimate on the hardened solver.
        from scipy.linalg import cho_solve

        n = k_train.shape[0]
        probes = np.random.default_rng(FOLD_SEED + 11).choice([-1.0, 1.0], size=(n, 8))
        factor, _ = _solve_dual(k_train, np.zeros((n, 1), dtype=np.float32), lam)
        trace_inv = float(
            np.mean(np.sum(probes * cho_solve(factor, probes, check_finite=False), axis=0))
        )
        effective_dof = float(n - lam * trace_inv)

        def targets_for(names_list: list[str], k: int) -> np.ndarray:
            if shuffle_targets:
                return np.concatenate(
                    [games[n]["targets"][shuffled_rows[n] + k] for n in names_list], axis=0
                )
            return _target_matrix(games, names_list, k)

        all_ks = list(horizons) + [-j for j in memory_lags]
        for k in all_ks:
            y_train = targets_for(train_names, k)
            y_mean = y_train.mean(axis=0)
            _, alpha = _solve_dual(k_train, y_train - y_mean, lam)
            pred = k_test @ alpha + y_mean
            for name, start, stop in test_spans:
                rows = games[name]["eligible"]
                y_true = games[name]["targets"][rows + k]
                y_now = games[name]["targets"][rows]
                scores = _score(y_true, pred[start:stop], y_now, y_mean)
                per_game[name][str(k)] = scores
        telemetry.info(
            "jepa.probe.fold", arm=arm, fold=fold_index, lam=lam, effective_dof=effective_dof
        )
        print(
            f"{arm}: fold {fold_index + 1}/5 done (lambda={lam:g}, dof={effective_dof:.0f})",
            flush=True,
        )
        dof_by_fold.append(effective_dof)
        del k_train, k_test
    return {
        "per_game": per_game,
        "lambdas": lambdas_chosen,
        "effective_dof": dof_by_fold,
        "shuffled": shuffle_targets,
    }


def state_health(games: dict[str, dict[str, Any]]) -> dict[str, Any]:
    report: dict[str, Any] = {}
    meta = json.loads((STATES / "real" / "meta.json").read_text())
    segments = meta["segments"]
    for condition in ("real", "null", "bypass"):
        if not (STATES / condition / "meta.json").exists():
            continue
        saturated, variances, sample = [], {seg: [] for seg in segments}, []
        for name in sorted(games):
            states = _state_features(condition, name).astype(np.float32)
            saturated.append(float((np.abs(states) > 0.99).mean()))
            for seg, (start, stop) in segments.items():
                sample_var = float(states[:, start:stop].var())
                variances[seg].append(sample_var)
            sample.append(states[::8])
        stacked = np.concatenate(sample, axis=0)
        stacked -= stacked.mean(axis=0)
        singular = np.linalg.svd(stacked, compute_uv=False)
        eig = singular**2
        participation = float(eig.sum() ** 2 / (eig**2).sum())
        report[condition] = {
            "saturation_fraction": float(np.mean(saturated)),
            "population_variance": {seg: float(np.mean(v)) for seg, v in variances.items()},
            "participation_ratio_subsampled": participation,
        }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--arms",
        nargs="+",
        default=[
            "real",
            "b1",
            "b2_l1",
            "b2_l2",
            "b2_l4",
            "b2_l8",
            "oracle",
            "b2p_s0",
            "b2p_s1",
            "b2p_s2",
            "null",
            "bypass",
        ],
    )
    parser.add_argument("--skip-controls", action="store_true")
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args(argv)
    global OUT
    if args.out is not None:
        OUT = Path(args.out)

    games = load_game_data()
    results: dict[str, Any] = {
        "protocol": "EXPERIMENTS.yaml H-JEPA-SPONTANEOUS protocol_frozen_2026_09_24",
        "config_sha256": _sha256(CONFIG),
        "esp": json.loads(ESP.read_text())["recommended_washout"],
        "deciding_cell": {"k": DECIDING_K, "metric": "masked_r2"},
        "arms": {},
    }
    if OUT.exists():
        # Laptop-sleep resilience: completed arms in the checkpoint are kept.
        previous = json.loads(OUT.read_text())
        if previous.get("config_sha256") == results["config_sha256"]:
            results["arms"] = previous.get("arms", {})
            print(f"resuming: {sorted(results['arms'])} already done", flush=True)
    for arm in args.arms:
        if arm in results["arms"]:
            continue
        memory = MEMORY_LAGS if arm in {"real", "null", "bypass"} else ()
        results["arms"][arm] = run_arm(arm, games, HORIZONS, memory_lags=memory)
        OUT.write_text(json.dumps(results, indent=2) + "\n")
        print(f"checkpointed after arm {arm}", flush=True)
    if not args.skip_controls:
        results["shuffled_time_real"] = run_arm(
            "real", games, tuple(h for h in HORIZONS if h > 0), shuffle_targets=True
        )
        results["state_health"] = state_health(games)
    OUT.write_text(json.dumps(results, indent=2) + "\n")
    print(f"probe complete -> {OUT}")
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("jepa_probe", main))
