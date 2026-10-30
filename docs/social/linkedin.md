# LinkedIn

Structure follows [VIRALITY_NOTES.md](VIRALITY_NOTES.md): awe → real finding →
surprise → pratfall → principle.

The Pratfall Effect is why the failures land late rather than early: admitting a
mistake raises likability **for someone already seen as competent**. Opening with
the failure spends credibility that has not been established yet.

---

## Draft A — recommended

**A complete fruit-fly brain played an AI reasoning benchmark.**

166,700 neurons. 24,559,055 synaptic connections. The entire central nervous
system of an adult male *Drosophila*, reconstructed from electron microscopy,
making every decision inside an ARC-AGI-3 agent during the controlled runs.

Zero trainable parameters. No network learned this. It is the fly's own wiring,
in the loop.

**The first result genuinely surprised me.**

The fly's connectivity is *provably* not random.

I rewired it while preserving everything a skeptic would demand — every neuron's
incoming and outgoing connection count, and the exact set of synaptic weights —
changing only *which* neuron connects to which. Three independent rewirings.

The real connectome's signed spectral radius came out **3.59× higher**.
Excitation and inhibition are organised so that they don't cancel the way a
degree-matched shuffle does.

Half a billion years of selection leaves a signature you can measure in a single
number. That, to me, is the good part.

**Then I asked the question that connectome demos usually skip.**

Did it help?

Because here's what people don't always say out loud: when you connect a
connectome to a task, you don't just add the connectome. You write an encoder to
feed it and a decoder to read it. Neither exists in the fly — real descending
neurons encode things like "turn left at this rate," for a body that isn't
there.

So when the system performs, which part performed? The 500-million-year-old
circuit, or the two adapters you wrote last Tuesday?

That question has an answer. It just requires building things that can tell you
you're wrong.

**So I built them:**

→ a degree-preserving rewiring — same neurons, same degrees, same weights,
random partners
→ a parameter-matched bypass — same interface, graph deleted entirely
→ a positive control tuned to succeed — a reservoir pushed into the regime
reservoir computing calls good
→ held-out games, so in-sample gains can't pass as generalisation

**What they said: no advantage — from any graph I tested.**

Random action selection outscored the connectome, 0.098 to 0.065. The brain-free
bypass tied it exactly. Real versus rewired: p = 1.00, a confidence interval
spanning zero, and the entire difference resting on one game out of twenty-five.
And the kicker: the positive control, tuned to succeed, ALSO moved no score —
0.0137, both decision CIs spanning zero — so the zeros bound my interface, not
the fly. Under this harness, no tested
graph moved the score; what a better harness would say remains open.

**And then the controls turned on me.**

My "smart" click targeting — aim where the screen changed, don't repeat squares —
explores **3.29× less than clicking at random**, in the games where clicking is
the only legal move. I shipped it in two competition submissions before I checked
it against the dumbest possible alternative.

A trained readout scored 0.886 on its training games and **exactly 0.000** on
held-out ones.

And I discovered my own configuration had deleted **129,132 dopaminergic
connections** — the fly's entire reward-learning pathway — after which I had
carefully measured that it couldn't learn.

Leaderboard: **{{BEST_SCORE}}**. {{BEST_RANK_LINE}}

**Why post this?**

A fly brain is extraordinary — at being a fly. Flight control at 200 wingbeats a
second, visual navigation, odour tracking, associative learning. Nothing selected
it for inferring symbolic rules from coloured squares, and a fair test may well
confirm that.

The wiring is real. The advantage never showed — not from the fly, not from any
graph my harness tested. Both are results — and you only get the
second one if you build the thing that could have said no.

Everything is in the repo: the controls, the hashes, the preregistered criteria,
the failed assumptions, and the one claim I had to retract when I measured it
properly.

{{REPO_LINK}}

#Connectomics #AI #Neuroscience #ARCAGI #OpenScience #MachineLearning

---

## Draft B — shorter

**A complete fruit-fly brain played an AI benchmark.** 166,700 neurons.
24,559,055 synapses. Zero trainable parameters.

The first finding surprised me: its wiring is *provably* not random. Rewire it
while preserving every neuron's connection count and every weight, and the real
connectome still has **3.59×** the spectral radius. Evolution leaves a signature
you can measure.

Then I asked whether it helped.

When you wire a connectome to a task, you also write an encoder and a decoder.
Those are new networks around the biological one. So which part performed?

I built the controls: a degree-preserving rewiring, a bypass with the graph
deleted, held-out games.

Answer: no advantage — from anything. Random beat it. The bypass tied it.
p = 1.00. Even the positive control, a reservoir tuned into the known-good
long-memory regime, moved no score (0.0137; both decision CIs span zero):
under this interface, no tested graph moved score.

Then I found my own "smart" clicking was 3.29× worse than clicking at random —
shipped in two submissions before I compared it to the obvious alternative.

The wiring is real. The advantage never showed — from the fly or from any graph
this harness tested. Both are results.

{{REPO_LINK}}

---

## Notes

- Do not name other projects. "Mine included" is stronger and safer.
- If the score is still 0.00, say so plainly. A zero with controls beats a small
  number without them, and the drafts work either way.
- Strongest first comment: the retraction. "I had to withdraw one finding when I
  measured it properly" signals the discipline is real, not decorative.
