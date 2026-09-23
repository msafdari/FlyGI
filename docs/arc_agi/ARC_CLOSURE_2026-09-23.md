# ARC closure report — 2026-09-23

Written per `CLAUDE_CODE_REFACTOR_HANDOFF.md` §4.4 after the queue drained.
Every number below is **measured**; expectations and decisions are labelled.

## Final comparisons

| Comparison | Δ score | 95% CI | p | Levels | Verdict |
| --- | ---: | --- | ---: | --- | --- |
| permuted vs bioeye-lc (H-COLOUR-MAP) | +0.022 | [-0.108,+0.198] | 0.974 | 15 v 16 | null — mapping is convention |
| bioeye-t4t5 vs t4t5 (H-RETINOTOPY-COLOUR) | +0.0717 | [+0.005,+0.156] | 0.070 | 22 v 13 | **HELPS (borderline)** |
| retdec vs bioeye-lc, full 25 | -0.159 | [-0.364,-0.003] | 0.126 | 21 v 16 | HURTS on score, +5 levels |
| retdec, click-19 (preregistered primary) | -0.209 | [-0.475,-0.007] | 0.120 | 20 v 15 | HURTS on score, +5 levels |
| retdec, click-dominant-9 (secondary) | -0.444 | [-0.914,-0.012] | 0.124 | 14 v 9 | HURTS on score, +5 levels |

Claim-tier reading: the T4/T5 HELPS is one CI grazing zero among ~14 complete
comparisons and its permutation p is 0.070 — *measured, borderline, and honest
about both*. The retdec result is the project's breadth/depth trade at its
sharpest: measured 3.5-cell click localization converted into MORE first levels
on MORE games and LESS score at every endpoint, consistently signed across all
three. Localization is not what the score rewards.

## Provenance

| Condition | Bundle sha256 (16) | Checkpoint sha256 (16) | Launch commit | Dirty |
| --- | --- | --- | --- | --- |
| sg-bioeye-lc-permuted | 21dc7bbc34d873a4 | f821144723d25b05 | 2cf2098 | yes |
| sg-bioeye-t4t5 | 6d1a7f312b0e3914 | da338055dbe79249 | 2cf2098 | yes |
| sg-bioeye-lc-retdec | eebb3c7d05ecd827 | 0cd91bd88485a047 | d28b789 | yes |
| sg-bioeye-lc-surprise | none (killed 18/75) | 2efee81beec61660 | d28b789 | yes |

Config SHA-256s matched the handoff's frozen table byte-for-byte at adoption
and at each launch (telemetry-verified for the 2cf2098/d28b789 arms).
Baselines (sg-lc, sg-t4t5, sg-bioeye-lc) predate telemetry; launch commits
ce9c3c6/dd6aa27 reconstructed from session history.

## Source-equivalence audit — comparison-matched, hash grade

A baseline row (sg-bioeye-lc config, seed 0, ls20, 600 actions) replayed under
current HEAD reproduced its dd6aa27-era `replay_trace_sha256` **byte-
identically**. Every non-treatment code path across the commit range — spmv
threading, telemetry, efference plumbing, factory gating, config parsing — is
therefore behaviourally inert as executed. All three closed comparisons
classify **source-different but comparison-matched**. Residual risk: the
`git_dirty=true` flags mean uncommitted content at launch is unrecorded;
mitigated by the hash replay and by every treatment being config-opt-in.

## Run history and recovery events

Launch order: sg-lc/sg-t4t5 (scrambled controls) → sg-bioeye-lc (restarted
once at 15/75 onto the threaded build; resume verified) → permuted+t4t5
(waiter-chained, fired once each) → retdec+surprise (waiter-chained, fired once
each). One laptop sleep (~1 h) suspended and cleanly resumed the decoder arms.
sg-bioeye-lc-surprise was **killed at 18/75** by Mustafa's priority decision to
reach the refactor; killed, not falsified. No duplicate launches. No failed,
duplicate, or invalid rows in any final bundle (12-point validation PASS,
75/75 matched coverage each). `seed_diverse_traces=false` on all arms: some
games yield deterministic traces across seeds, which is why every statistic
clusters on games.

## Deviations from the handoff

Submission 3 (`56503750`, bio-eye T4/T5 + surprise decoder + efference copy)
was assembled and submitted DURING the queue on Mustafa's explicit instruction,
overriding the no-submit clause by the handoff's own authority ordering.
Scored 0.00 (hidden set), consistent with both priors. The running arms were
untouched (imported code) and the audit above covers the shipped commit range.

## Legacy MBdr battery

Not launched. Registry disposition: **deferred**. H-MB-LEARNING remains open;
the invalidation of its first test (0.00% sensory input to KCs) stands, and
Experiment 000 supersedes this formulation with exact populations, compartment
gating, and a degree-exact bipartite null (the legacy rewire preserves
MBON-side degree only — a known gap the refactor must not inherit).

## Reusable vs ARC-specific (per the movement map)

Reusable, stable interfaces: `src/flygi/telemetry.py`, `src/flygi/dynamics/spmv.py`
(bit-identity contract documented), `src/flygi/evaluation/` (game-clustered
paired stats), `scripts/{league,analyze_endpoints,validate_closure,resume_runs,
inspect_telemetry}.py`, `EXPERIMENTS.yaml` registry pattern, connectome
acquisition/manifest modules.
ARC-specific (Experiment 002, freeze before moving): `src/flygi/arc/**`,
`src/flygi/controller/**`, `src/flygi/encoding/**` (incl. `mb_bus.py` —
quarantined from Experiment 000), `src/flygi/decoding/**`,
`src/flygi/plasticity/mushroom_body.py` (legacy MB model),
`scripts/evaluate_state_graph.py`, all `configs/literal_rate_*` and
`configs/kaggle_*`.
Untracked, must not be lost: `.fly-or-fake-work/` (not ours; untouched),
`CLAUDE_CODE_REFACTOR_HANDOFF.md` (Codex's; committal is Codex's call).
Known bugs the refactor must not inherit: the legacy rewire's non-exact null;
`csr_matrix(copy=False)` copies anyway (guarded in spmv, documented in
docs/performance.md); inhibition cannot sparsify signed-tanh units (rectified
eligibility exists; per-population activation remains future work).
