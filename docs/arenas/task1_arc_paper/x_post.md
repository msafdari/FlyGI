# X post draft

*(Post AFTER the repo is public. Option A is a single post; Option B is a
thread. Attach media/cover.png to the lead post; figures 1–3 to thread
tweets as marked. Character counts exclude the link, which X shortens.)*

## Option A — single post (270 chars as X counts it)

> I audited the complete fruit-fly connectome (166,700 neurons) on
> ARC-AGI-3, with controls. Scored agents used only its static eye map
> (dynamics off): beat its scrambled twin 4.5x. Engineered scaffold: ~52x
> locally, ZERO hidden transfer (0.15 x3). github.com/msafdari/FlyGI

## Option B — thread

**1/** (attach cover.png)
Dozens of projects wired the newly mapped fly connectomes to Doom this
September. We put one on ARC-AGI-3 instead — with matched controls
(degree-preserving rewires, scrambled twins) on every claim. The results cut
in both directions. 🧵

**2/** (attach fig1_ladder_vs_hidden.png)
Our engineered scaffold (13 hand-built game grammars) grew the local score
~52x: 0.55 → 28.74 on matched runs. On Kaggle's hidden games: 0.15, 0.15,
0.15 — the abstention floor. Grammar transfer to unseen games measured
exactly zero, three times.

**3/**
The one fly component we actually deployed — the eye's static anatomical map,
straight from the connectome — no dynamics, zero training — completed first levels at
2.59x the human action baseline vs 11.59x for a scrambled-map twin. A 4.5x
gap attributable to anatomy alone. Small, real, control-backed.

**4/** (attach fig3_controls_both_ways.png)
The deep circuits are the twist: our class-2 mushroom-body and class-2.5 T4/T5 models PASSED their biology
benchmarks — then both lost the ARC task to
their own shuffled twins (0.600 vs 0.800; 0.3875 vs 0.4306). The wiring is
real. On pixel grids, at these fidelities, it points the wrong way.

**5/** (attach fig2_verdict_matrix.png)
Same instrument, pointed at ourselves: our tested, shipped coordinate head
explored 3.29x LESS than random clicking. A trained head was genuinely
connectome-dependent — and generalized zero. Well-tested and worse than
random are compatible.

**6/**
Why publish a 0.15? Because "brain plays game" demos are everywhere and
attribution is almost nowhere — no demo we found runs validation, input
gates and controls together. Validate the biology → gate the input → test vs
rewired twins. Everything's open — code, worklog, preregistrations, and our
ARC Prize 2026 Paper Track writeup:
github.com/msafdari/FlyGI
