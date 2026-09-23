# Experiment league

Generated 2026-09-23T19:18:58.357868+00:00 by `scripts/league.py`. Do not edit;
edit `EXPERIMENTS.yaml` and regenerate. Verdicts come from clustered
bootstrap CIs on complete matched pairs only; partial runs never get one.

| condition | regime | status | rows | score | levels | vs baseline | baseline |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| sg-controller-only | controller-only | complete | 75 | 0.1947 | 20 | — | — |
| sg-fly-real | gain0.9-dead | complete | 75 | 0.2163 | 20 | +0.0216 [-0.166,+0.186] p=0.838 -> null | sg-controller-only |
| sg-fly-gridhash | gain0.9-dead | complete | 75 | 0.1797 | 9 | -0.0150 [-0.150,+0.100] p=0.765 -> null | sg-controller-only |
| sg-fly-null | gain0.9-dead | complete | 75 | 0.1443 | 14 | -0.0720 [-0.214,+0.026] p=0.441 -> null | sg-fly-real |
| sg-fly-real-1800 | gain0.9-dead | complete | 25 | 0.2454 | 9 | +0.0002 [+0.000,+0.001] p=1.000 -> null | sg-fly-real |
| sg-g2-nolearn | gain2.0-modulators | complete | 75 | 0.2034 | 21 | +0.0088 [-0.068,+0.108] p=0.862 -> null | sg-controller-only |
| sg-g2-learn | gain2.0-modulators | complete | 75 | 0.2035 | 18 | +0.0000 [-0.002,+0.003] p=1.000 -> null | sg-g2-nolearn |
| sg-g2-learn-rewired | gain2.0-modulators | killed | 29 | 0.1503 | 9 | partial: +0.0630 (29 pairs, no verdict) | sg-g2-learn |
| sg-g2-learn-shuffled | gain2.0-modulators | killed | 33 | 0.0767 | 5 | partial: +0.0000 (33 pairs, no verdict) | sg-g2-learn |
| sg-lc | gain2.0-modulators | complete | 75 | 0.2412 | 16 | +0.0378 [-0.068,+0.150] p=0.526 -> null | sg-g2-nolearn |
| sg-t4t5 | gain2.0-modulators | complete | 75 | 0.1754 | 13 | -0.0280 [-0.163,+0.094] p=0.557 -> null | sg-g2-nolearn |
| sg-cx | gain2.0-modulators | killed | 30 | 0.0551 | 5 | partial: -0.0301 (30 pairs, no verdict) | sg-g2-nolearn |
| sg-bioeye-lc | gain2.0-modulators | complete | 75 | 0.2504 | 16 | +0.0092 [-0.121,+0.174] p=0.818 -> null | sg-lc |
| sg-bioeye-lc-permuted | gain2.0-modulators | running | 25 | 0.3287 | 5 | partial: +0.1073 (25 pairs, no verdict) | sg-bioeye-lc |
| sg-bioeye-t4t5 | gain2.0-modulators | running | 24 | 0.2250 | 7 | partial: +0.0724 (24 pairs, no verdict) | sg-t4t5 |
| real-signed | gain0.9-dead | complete | 125 | 0.1905 | 5 | +0.0000 [-0.571,+0.571] p=1.000 -> null | no-graph-bypass |
| no-graph-bypass | gain0.9-dead | complete | 125 | 0.1905 | 5 | — | — |
| null-degree-preserving | gain0.9-dead | complete | 125 | 0.0000 | 0 | -0.1905 [-0.571,+0.000] p=1.000 -> null | real-signed |
| real-signed-focused | gain0.9-dead | complete | 125 | 0.1143 | 3 | — | — |
| real-signed-loop-escape | gain0.9-dead | complete | 75 | 0.1270 | 2 | -0.0635 [-0.381,+0.190] p=1.000 -> null | real-signed |
| eff-real-signed | gain0.9-dead | complete | 75 | 0.0648 | 2 | +0.0640 [+0.000,+0.192] p=1.000 -> null | eff-no-graph-bypass |
| eff-no-graph-bypass | gain0.9-dead | complete | 75 | 0.0008 | 1 | — | — |
| eff-null-degree-preserving | gain0.9-dead | complete | 75 | 0.0079 | 3 | -0.0569 [-0.171,+0.000] p=1.000 -> null | eff-real-signed |
| sweep800-escape | gain0.9-dead | complete | 25 | 0.1905 | 1 | — | — |
| sweep1600-mild | gain0.9-dead | complete | 25 | 0.1913 | 3 | — | — |
| mb-frozen | gain0.9-dead | complete | 25 | 0.0014 | 1 | — | — |
| mb-plastic | gain0.9-dead | complete | 25 | 0.0053 | 1 | +0.0039 [+0.000,+0.012] p=1.000 -> null | mb-frozen |
| mb-plastic-rewired | gain0.9-dead | complete | 25 | 0.0009 | 1 | -0.0044 [-0.013,+0.000] p=1.000 -> null | mb-plastic |
| head-trained | gain0.9-dead | complete | 25 | 0.2835 | 2 | +0.0881 [-0.470,+0.628] p=1.000 -> null | full-nocentroid |
| head-trained-blind | gain0.9-dead | complete | 25 | 0.0000 | 0 | -0.2835 [-0.739,+0.000] p=0.505 -> null | head-trained |
| retinotopic | gain0.9-dead | complete | 25 | 0.0032 | 1 | -0.1922 [-0.581,+0.006] p=0.495 -> null | full-nocentroid |
| click-coorduniform | gain0.9-dead | complete | 18 | 0.0000 | 0 | -0.0101 [-0.030,+0.000] p=0.500 -> null | click-nocentroid |
| click-coordhot | gain0.9-dead | complete | 18 | 0.0000 | 0 | -0.0101 [-0.030,+0.000] p=0.500 -> null | click-nocentroid |
| click-nocentroid | gain0.9-dead | complete | 18 | 0.0101 | 3 | — | — |
| full-nocentroid | gain0.9-dead | complete | 25 | 0.1954 | 2 | +0.0049 [+0.000,+0.015] p=1.000 -> null | real-signed-loop-escape |
| sg-mbdr-nolearn | gain2.0-modulators | missing | 0 | 0.0000 | 0 | — | sg-g2-nolearn |
| sg-mbdr-learn | gain2.0-modulators | missing | 0 | 0.0000 | 0 | — | sg-mbdr-nolearn |
| sg-mbdr-learn-rewired | gain2.0-modulators | missing | 0 | 0.0000 | 0 | — | sg-mbdr-learn |
| sg-mbdr-learn-shuffled | gain2.0-modulators | missing | 0 | 0.0000 | 0 | — | sg-mbdr-learn |

## Hypotheses

| id | status | statement |
| --- | --- | --- |
| H-ANATOMY-TIEBREAK | null | The connectome breaking the controller's ties beats the controller's own deterministic hash. |
| H-STATE-DEPENDENCE | refuted | Any observation-dependent tiebreaker helps; the fly would be incidental. (The deflationary reading of the fly's early partial lead.) |
| H-BUDGET | refuted | Score is limited by the 600-action budget. |
| H-MB-LEARNING | invalidated | Controller-supplied reinforcement through KC->MBON depression improves score. |
| H-OPERATING-POINT | null | Waking the network from the numerical floor (gain 0.9 -> 2.0 on the -modulators graph) improves score by itself. |
| H-RETINOTOPY-COLOUR | null | An input that preserves both retinotopy and categorical colour lets the fly's visual hierarchy (T4/T5, LC) do work that the scrambled projection made impossible. |
| H-COLOUR-MAP | open | The colour->type rule (c % 15) is harmless convention; only the categorical-plus-retinotopic structure matters, not which medulla type carries which colour. (Assumption A of the encoder.) |
| H-PERCEPTION-READOUT | null | Reading high-signal perception populations (LC 16.1x, T4/T5 54.5x the DN activity) beats reading descending neurons -- under scrambled input. |
| H-APL | supported | Strengthening APL feedback inhibition -- the fly's own sparsification circuit -- restores biological KC sparsity (0.05-0.11) at a live operating point, where global gain provably cannot (KC->KC is 85.3% of KC input; the silent-to-latched transition is abrupt). |
| H-MB-INPUT-BUS | open | Driving the mushroom body through its real input pathway (antennal-lobe projection neurons -> Kenyon cells, 2 hops, reaches 4,025/4,064 KCs) gives the learning circuit sensory content, making a fair retest of H-MB-LEARNING possible. ARC has no odours, so any PN drive is a declared invention (assumption G): the claim is about the MB as associative memory, never about olfaction. |
