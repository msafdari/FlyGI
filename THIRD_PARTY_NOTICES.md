# Third-party notices

FlyGI interoperates with and follows interface patterns from the following ARC
Prize projects. Their code is not relicensed by FlyGI.

## ARC-AGI-3 Kaggle Starter

The local-play and generated-notebook workflows follow the public starter at
commit [`eeb1535404f321d280a8f9194bbc1d7aca5f05fc`](https://github.com/arcprize/ARC-AGI-3-Kaggle-Starter/tree/eeb1535404f321d280a8f9194bbc1d7aca5f05fc).
The pinned commit does not contain a root `LICENSE` file, so this repository
records the reference and does not assert a license for that starter.

## ARC-AGI-3-Agents

FlyGI's setup command checks out commit
[`4743e7d0aaae0ded0d98a89a7e282e63564cd58b`](https://github.com/arcprize/ARC-AGI-3-Agents/tree/4743e7d0aaae0ded0d98a89a7e282e63564cd58b)
into an ignored local vendor directory.

MIT License

Copyright (c) 2025 ARC Prize

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## ARCEngine

The adapter contract was checked against commit
[`b495c6acaf253c9681cd7b75c4299d352e9ce6f8`](https://github.com/arcprize/ARCEngine/tree/b495c6acaf253c9681cd7b75c4299d352e9ce6f8).

MIT License

Copyright (c) 2026 ARC Prize Foundation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## flyvis pretrained parameters (embedded derivative)

`docs/fidelity2/flyvis_trained_params.json` aggregates per-type/per-pair
parameter summaries derived from the released pretrained ensemble
(flow/0000) of [flyvis](https://github.com/TuragaLab/flyvis) 1.2.0
(Lappalainen et al. 2024, Nature 634:1132; full provenance, download
checksums and derivation are recorded inside the JSON itself). flyvis is
MIT-licensed (Copyright (c) 2023 Janne K. Lappalainen, Fabian D. Tschopp,
Mason McGill, Jakob H. Macke, Srinivas C. Turaga). The derived summaries
are redistributed here under that license's terms with this notice.

## Pisokas, Heinze & Webb 2020 fly circuit fixture (embedded derivative)

`tests/data/pisokas_fly_connectivity.npz` embeds the 60-neuron idealized
fly head-direction circuit (connectivity labels and class weights) from
the published modeling code of Pisokas, Heinze & Webb 2020 (eLife
9:e53985), repository
[johnpi/eLife_Pisokas_Heinze_Webb_2019](https://github.com/johnpi/eLife_Pisokas_Heinze_Webb_2019)
(MIT License). It is used as the validation gate for the class-3
instruments; the physiology constants pinned in those instruments cite
the same source.

## ARC-AGI-3 state-graph references

FlyGI's Phase 1 controller is a native implementation informed by generic
exploration mechanisms described in two public agents. Their source trees are
not vendored, and public-game-specific rules were deliberately excluded.

- Shlok Sah's
  [FrugalExplorer](https://github.com/shloksah/arc-agi-3-agent/tree/7dccef15650fa00ef1db1c21cc7279adcf4a9e2a),
  pinned at `7dccef15650fa00ef1db1c21cc7279adcf4a9e2a`, is licensed
  under MIT No Attribution (MIT-0). It motivated the training-free action-effect
  prior, component-grounded candidate set, and return-to-frontier pattern.
- Will Dick's
  [Blind Squirrel](https://github.com/wd13ca/ARC-AGI-3-Agents/tree/641c00ef6b149527e5268927a664a6a6d6bb13fa),
  pinned at `641c00ef6b149527e5268927a664a6a6d6bb13fa`, is licensed under
  MIT. It was consulted for the empirical directed-state-graph design.

FlyGI reimplements these ideas against its own dependency-free policy boundary,
with collision-checked BLAKE2b identities, empirical multi-successor edges,
seeded deterministic ties, and no named-game branches, hard-coded ARC colors,
or imported game logic.
