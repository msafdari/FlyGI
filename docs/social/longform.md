# Long form — Hacker News, Reddit, blog

Technical audiences that will check the numbers. Lead with the method, not the
hook, and put the negative result in the title.

---

## Title options

Discovery frame, not defeat frame. See [VIRALITY_NOTES.md](VIRALITY_NOTES.md).

1. A fruit-fly connectome is provably not random — 3.59x. It still didn't help.
2. 166,700 neurons, 0 trainable parameters, and the controls nobody runs
3. I wired a complete fly brain to an AI benchmark, then tried to prove myself
   wrong

---

## Body

The complete MaleCNS v1.0 adult male *Drosophila* central nervous system —
166,700 neurons, 24,559,055 directed synaptic connections — is running in the
decision loop of an ARC-AGI-3 agent, with zero trainable parameters.

The first thing I measured was the best thing I measured, so it goes first.

**The fly's connectivity is provably not random.** Rewiring it while preserving
every neuron's in-degree, out-degree and the full weight multiset — changing
only which neuron contacts which — drops the signed spectral radius from
**0.8289 to 0.2360 / 0.2348 / 0.2219** across three independent seeds. A 3.59x
separation. Excitation and inhibition are organised so they don't cancel the way
a degree-matched shuffle does.

That is a real, reproducible property of evolved neural architecture, and it
survives the strictest null I could construct.

Then I asked whether it helped, which is the part that's usually missing.

### The attribution problem

A connectome is anatomy. It is not a model. To run one you have to supply
everything the anatomy doesn't: dynamics, an input encoding, an output decoding,
normalisation, initial state.

Concretely, in my system: the ARC grid is projected into sensory neurons, and
descending-neuron activity is mapped to game actions. Neither mapping exists in
the fly. Real descending neurons encode things like "turn left at this rate" for
a body that isn't present.

So when the composite system does something, the credit is ambiguous between the
evolved circuit and the two adapters I wrote. Calling the inputs
"photoreceptors" doesn't resolve it.

### The controls

- **Directed degree-preserving rewiring.** Every neuron keeps its exact in- and
  out-degree and the full weight multiset; only the partners change. Three
  independent seeds, ten double-edge swaps per edge, each retaining 0.51% of the
  real edge set.
- **Parameter-matched bypass.** Identical interface budget, recurrent gain set
  to zero, projection retargeted so its readout is actually driven — 389,471
  interface non-zeros against the real condition's 390,272.
- **Positive control.** A reservoir deliberately placed at the edge of chaos, so
  that if everything scores zero I can tell "the connectome doesn't help" from
  "my harness can't express help from any graph." It retains ~400× more state
  than the real graph.
- **Held-out games**, and uncertainty clustered on games rather than rows —
  because a deterministic policy produced byte-identical traces across all five
  seeds, and treating those as replicates would claim 5× the evidence it had.

### What the controls said

**No benchmark advantage.** The structural separation above did not translate
into a single point of ARC performance.

- Random legal action selection: 0.097568. The connectome: 0.064751.
- Interface-matched bypass: tied the connectome exactly, 0.190476 each, solving
  one game apiece — different games.
- Real vs degree-preserving null on score: mean difference −0.0569, 95% CI
  [−0.171, +0.000], permutation p = 1.0000, with 1 of 25 games carrying the
  entire difference.

### Four things I got wrong, found by measuring

1. **The coordinate head.** "Smart" click targeting — aim at changed cells, avoid
   repeats — explores **3.29× less than uniform random clicking** in the six
   games where clicking is the only legal action. Random solved a game that my
   version never has. Six tests passed; none compared it to random. It shipped in
   two competition submissions.

2. **The trained readout.** A 520-parameter head over the frozen graph scored
   0.885805 on its training games and **exactly 0.000000** on held-out ones. The
   headline number looked like a 1.49× gain until I split it.

3. **The deleted reward system.** My own transmitter configuration zeroed
   modulatory neurons, which deleted **129,132 dopaminergic connections** into
   Kenyon cells and 3,195 into mushroom-body output neurons. I had removed the
   fly's reinforcement-learning pathway and then measured that it couldn't learn.

4. **A silently inert learning rule.** Once the pathway was restored, plasticity
   still moved **exactly zero weight** for 60 turns: connectome activity is ~1e-6
   and the weights ~1e-3, so updates landed near 1e-18 and rounded to zero in
   float32. A nonzero gate on 59 of 60 turns, and nothing happening.

### Retraction

I earlier believed the connectome reached the first level "in far fewer actions
than random." That came from comparing **scores on a single game**, not measured
action counts, which weren't being recorded. Measured properly: **143.0 actions
against random's 144.0.** Indistinguishable, and random completed three times as
often.

### Leaderboard

**{{BEST_SCORE}}**. {{BEST_RANK_LINE}}

### The point

A fly brain is remarkable at being a fly. Nothing selected it for inferring
symbolic rules from coloured squares, and a fair test might well confirm it
can't. That's a legitimate result — but only if the test is fair, and only if
you built the things that could have said otherwise.

The demos are the easy part. The controls are the science.

Repo, with hashes, preregistered criteria, failed assumptions and the
retraction: {{REPO_LINK}}

---

## Notes

- Expect "did you try X?" — the honest answer for most X is no, and the repo's
  limitations section lists them.
- Do not name other projects. At least one published connectome study reported a
  parameter-matched control that beat its own connectome condition, so a blanket
  "nobody runs controls" is false and would be correctly called out.
