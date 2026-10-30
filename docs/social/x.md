# X / Twitter

Structure follows [VIRALITY_NOTES.md](VIRALITY_NOTES.md): awe → real finding →
surprise → pratfall → principle. Do **not** open with the negative result; it is
low-arousal negative, the weakest opening the evidence identifies.

---

## Single post

A complete fruit-fly brain played an AI reasoning benchmark.

166,700 neurons. 24,559,055 synapses. 0 trainable parameters.

And its wiring is provably not random — 3.59× the spectral radius of exact
degree-matched rewirings.

Then I ran the controls, and it got interesting. 🪰🧵

---

## Thread (9 posts)

**1/**
A complete fruit-fly brain played an AI reasoning benchmark.

166,700 neurons. 24,559,055 synapses. The entire adult *Drosophila* CNS,
reconstructed from electron microscopy, made every decision during the
controlled runs.

0 trainable parameters.

🪰🧵

**2/**
First real finding, and it surprised me:

**the fly's wiring is provably not random.**

Signed spectral radius 3.59× that of exact degree-preserving rewirings — same
neurons, same connection counts, same weights, shuffled partners.

Excitation and inhibition are arranged so they don't cancel.

**3/**
That result survives the strict version of the test: preserve every neuron's
in-degree AND out-degree AND the full weight multiset. Three independent seeds.

Half a billion years of selection leaves a signature you can measure in one
number.

**4/**
Then I asked the question almost no connectome demo asks.

Did it actually *help*?

**5/**
Because here's the thing about wiring a connectome to a task: you don't just add
the connectome.

You write an encoder to feed it.
You write a decoder to read it.

Neither exists in the fly. They're new networks, wrapped around the old one.

**6/**
So when it performs — which part performed? The 500-million-year-old circuit, or
the two adapters you wrote on Tuesday?

I built the things that could answer it:

• degree-preserving rewirings
• a bypass with the brain deleted, same interface budget
• a positive control tuned to succeed
• held-out games

**7/**
The answer: no advantage — from ANY of them.
Even the positive control, tuned to succeed, moved no score (both decision
CIs span zero): the zeros bound my interface, not just the fly.

Random action selection outscored it, 0.098 to 0.065.
The brain-free bypass tied it exactly.
p = 1.00, confidence interval through zero, the whole difference from 1 game of
25.

**8/**
And the humbling part.

My "smart" click targeting explores **3.29× less than clicking at random** in
the games where clicking is the only legal move. I shipped it. Twice.

A trained readout: 0.886 on its training games. **0.000** held out.

I also found I'd deleted the fly's entire reward pathway — 129,132 connections —
then measured that it couldn't learn.

**9/**
Score: **{{BEST_SCORE}}**

A fly brain is extraordinary — at being a fly. Nothing selected it for symbolic
puzzles on a screen.

The wiring is real. The advantage never showed — not from the fly, not from any
graph this harness tested. Both of those are results, and you only get the
second one if you build the thing that can say no.

{{REPO_LINK}} 🪰

---

## Notes

- Posts 2–3 are the awe payload. They are why anyone reads post 7.
- Post 8 is the Pratfall moment and the one most likely to be quoted — it only
  works *after* competence is established, which is what 1–3 do.
- Never name another project. At least one published connectome study reported a
  parameter-matched control that beat its own connectome condition.
