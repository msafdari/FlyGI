# Instagram

Visual-first. The carousel does the work; the caption is short. Nothing here
should require reading a table on a phone.

---

## Carousel, 8 slides

Awe first, the real finding second, the twist late. See
[VIRALITY_NOTES.md](VIRALITY_NOTES.md).

**Slide 1 — hook**
Full-bleed connectome render.
> A FRUIT FLY BRAIN
> PLAYED AN AI BENCHMARK

**Slide 2 — scale**
Three numbers, huge type, one per line.
> 166,700 neurons
> 24,559,055 synapses
> 0 trainable parameters

**Slide 3 — the pipeline**
Simple left-to-right diagram: game screen → [encoder] → fly brain → [decoder] →
action.
> The brain is real.
> The two boxes on either side? I wrote those.

**Slide 4 — the finding**
Two bars, dramatic difference.
> The fly's wiring is
> PROVABLY NOT RANDOM
> 3.59× the spectral radius
> of degree-matched rewirings

**Slide 5 — the question**
Pipeline diagram again, the two adapter boxes highlighted.
> So when it works…
> which part worked?

**Slide 6 — the controls**
Four icons, four lines.
> Rewire it randomly, keep every degree
> Delete the brain, keep the wrapper
> A control built to succeed
> Games it has never seen

**Slide 7 — the twist**
> …and it still didn't help.
> Random beat it. The brain-free version tied it.
> Even the control built to succeed moved nothing —
> the zeros bound my harness, not just the fly.

**Slide 8 — the point**
> Anyone can post the demo.
> The controls are the science.
> {{REPO_LINK}}

---

## Caption

A complete fruit-fly connectome — 166,700 neurons, 25 million connections —
played an AI reasoning benchmark with zero trainable parameters during the
controlled runs. 🪰

The first finding surprised me: its wiring is provably not random. Rewire it
while keeping every neuron's connection count and every weight, and the real
thing still has 3.59× the spectral radius. Evolution leaves a signature you can
measure in one number.

Then the part that usually gets left out: I built the controls. A rewired
version that keeps every neuron's connection count. A version with the brain
deleted entirely. Games it had never seen.

And it still didn't beat random action selection — and neither did the
control built to succeed, which is the part that bounds the harness itself,
not just the fly.

My own "smart" clicking turned out to be 3.29× worse than clicking at random. I
shipped that twice before I checked.

Score: {{BEST_SCORE}}

Posting the negative result, because that's the part that makes it science
rather than content. Everything's in the repo — controls, hashes, failed
assumptions, the claim I had to retract.

#connectomics #neuroscience #artificialintelligence #openscience #drosophila
#computationalneuroscience #machinelearning #arcagi

---

## Notes

- Slides 3 and 4 are the whole argument. If only two slides get looked at, those
  are the two that should.
- Render suggestion: use the actual graph, not stock fly imagery. The credibility
  is in it being a real reconstruction.
