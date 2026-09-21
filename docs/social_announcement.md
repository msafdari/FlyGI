# FlyGI social announcement drafts

These drafts are intentionally honest about the result. Replace the bracketed
leaderboard line only after Kaggle submission `56444435` finishes. Do not imply
that FlyGI solved ARC-AGI-3 or that biological topology beat its controls.

## LinkedIn

**I made a fly take ARC-AGI-3. 🪰🧠**

Not a fly-shaped neural net. Not a metaphor.

I wired the complete adult male *Drosophila* central-nervous-system connectome
into an ARC-AGI-3 agent:

- 166,700 neurons
- 24,559,055 directed edges
- signed excitatory/inhibitory dynamics
- the full graph in every decision
- zero trainable parameters

And today, FlyGI made its first official ARC-AGI-3 submission.

The honest result is more interesting than a victory lap.

Locally, the frozen agent completed one level of `sp80` in 3 of 5 seeded runs.
It passed all 125 engineering runs with zero crashes, illegal actions, invalid
clicks, or budget violations. Every game produced five genuinely different
seeded traces—so the “replicates” are finally real.

But the connectome did **not** establish an advantage over a carefully matched
bypass. Its wiring has a striking dynamical signature—about 3.59× the spectral
radius of directed degree-preserving nulls under the same signed
normalization—but that structural difference has not translated into better ARC
performance.

That is exactly why I built this as a falsifiable experiment rather than a demo.
The graph must beat controls, not just produce a cool-looking action trace.

What I learned:

1. Making 24.6 million biological connections run inside an interactive agent
   is the easy part compared with designing a fair interface.
2. Deterministic policies can create fake sample size. Seed the actions **and**
   the coordinates.
3. A negative control result is not a failed project. It is the result.
4. “Biologically inspired” means very little unless the biology is causally
   tested against matched alternatives.

Leaderboard status: **[replace when submission 56444435 completes]**

Next up: a matched positive-control reservoir, the full operating-point sweep,
and a small trained readout on the frozen graph.

The fly played ARC. Now the real question begins: did being a fly help?

#AI #Neuroscience #Connectomics #ARCAGI #MachineLearning #OpenScience

## X — single-post version

I made a fly take ARC-AGI-3. 🪰🧠

166,700 neurons. 24,559,055 edges. The full signed connectome in every decision.
0 trainable parameters.

It passed 125/125 local runs and made its first official submission—but it has
not beaten a matched bypass. The honest negative result is the point.

## X — thread version

### 1/7

I made a fly take ARC-AGI-3. 🪰🧠

Not a fly-inspired network. The complete 166,700-neuron, 24,559,055-edge adult
male fruit-fly CNS connectome—inside an interactive ARC agent.

Today it made its first official submission.

### 2/7

FlyGI uses the full graph on every decision:

• signed E/I dynamics
• persistent recurrent state
• descending-neuron readout
• legal-action masking
• seeded action + click exploration
• 0 trainable parameters

No per-game rules. No score-tuned decoder.

### 3/7

The local gate: 25 public games × 5 seeds × 80 actions.

✅ 125/125 valid runs
✅ 0 crashes
✅ 0 illegal actions
✅ 0 invalid coordinates
✅ 5 distinct traces for every game

It completed one `sp80` level in 3/5 seeded runs.

### 4/7

Now the part most demos leave out: controls.

The real fly graph has a strong dynamical signature—~3.59× the spectral radius
of directed degree-preserving nulls under matched signed normalization.

But it did **not** beat an interface-matched graph bypass on ARC.

### 5/7

So no, I have not shown that a fly “understands” ARC.

I showed something narrower and reproducible: a complete connectome can drive a
valid closed-loop agent—and its biological wiring has not yet earned the credit
for performance.

That negative result matters.

### 6/7

The biggest surprise: my first five “seeds” were identical because the policy
was deterministic.

ARC exposed it immediately. The fix was to seed both action sampling and click
coordinates, then choose temperatures without looking at score.

Replication has to be real.

### 7/7

Official submission: `56444435`
Leaderboard: **[replace when complete]**

Next: a matched positive-control reservoir, an operating-point sweep, and a
small trained readout.

The fly played ARC. Now we find out whether being a fly helps. 🪰

## Posting notes

- Best visual: a clean three-panel image showing the fly/connectome, the
  166,700-node → ARC action pipeline, and the honest result table.
- Strongest first comment: “The repo includes the negative control, failed
  assumptions, exact hashes, and worklog—not just the headline.” Add a public
  repository or write-up link only after one exists.
- If the leaderboard score is zero, say so plainly. The hook still works because
  the engineering and controlled negative result are the story.
- If the submission fails technically, do not use “reached the leaderboard.”
  Change it to “made its first official submission attempt” and name the failure.
