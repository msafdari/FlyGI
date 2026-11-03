I tested a fruit fly's wiring on ARC-AGI-3. On my held-out memory and motion tasks, both circuits scored higher after I scrambled their connections. My own engineering looked much better at first. My agent with thirteen hand-written game strategies cleared 73 levels and won four public games in a 35-minute run. On Kaggle, the baseline, the two-strategy agent and the thirteen-strategy agent all scored **0.15**.

The question behind FlyGI is which part of an agent's performance the wiring earns. Three experiments gave different answers. On the leaderboard, the agent used a static map of the fly's eye. In held-out ARC memory and motion tests, the real circuits trailed their rewired controls. In a separate model of the fly's compass, the same fitting procedure found a solution on anatomical counts and none on three rewires.

## What went into the agent

ARC-AGI-3 asks an agent to discover what its actions do in unfamiliar interactive games. The [MaleCNS reconstruction](https://male-cns.janelia.org/) gave me 166,700 retained neurons and 24,994,595 directed connections in the deployment build. Each connection has an anatomical count of synaptic contacts. To simulate activity I had to assign signs, convert counts to effective strengths and choose how activity changes over time.

That distinction matters in related work. Lappalainen et al. trained a connectome-constrained visual network on optic flow. Their released flyvis parameters let me test a motion circuit with independently trained visual parameters. A Doom demonstration freezes the brain simulation and trains its action readout. In both cases, asking which component learned the task leads to a more informative comparison than counting neurons. [flyvis paper](https://doi.org/10.1038/s41586-024-07939-3) · [doomFly methods](https://github.com/shreyash-sharma/doomFly/blob/main/docs/how-it-works.md)

I ran the full graph locally as a recurrent network and extracted individual circuits for more detailed models. Before testing a circuit on ARC, I checked whether it reproduced a named biological response and whether the stimulus actually reached it. An early mushroom-body experiment had delivered **0.00%** of the measured input from driven sensory populations. Rewarding a circuit that never received the cue had told me about my interface. Once the checks passed, I held the task and readout procedure fixed and changed the wiring. The control preserved the number of incoming and outgoing connections in the projections being rewired.

## Four public wins and three identical leaderboard scores

The submitted controller tracked game states, chose legal actions and learned which local image patches predicted a visible change after a click. It used the anatomical eye map to group pixels into columns. Later versions added rules for recognizable public games and fell back to the baseline policy when no rule applied. **Recurrent fly-neuron dynamics were off in all three 0.15 submissions.** The preflight recorded `neuronal_dynamics_active=false`.

On the same 25 public games in matched 35-minute competition-mode runs, the baseline scored **0.551859**, two strategies scored **3.044167**, and thirteen scored **28.742260**. Those were the games used to develop the rules. The corresponding Kaggle scores were **0.15, 0.15 and 0.15** (submissions 56620463, 56650224 and 56683298). A 52-fold local score increase bought no increase at the leaderboard's displayed precision. The aggregate scores cannot tell me which rules fired on a hidden game.

## What the eye map changed

On public game `r11l`, my click controller cleared the first level in **6 actions** with the anatomical map and **199** with its map assignments scrambled. On a second seed it took **15 versus 255**. On the third, the anatomical map cleared in **57** and the scrambled map never cleared within 600. These were official actions, including resets, in the historical click-coordinate convention. Both local controllers learned from their clicks and used the same active fly circuit to break ties between actions. The map assignment was the experimental change.

How typical was that game? Over 25 games and three seeds, the two controllers cleared a first level in **17 of 75** runs with the anatomical map and **16 of 75** with the scrambled map. In the 14 game and seed pairs where both cleared, the median ratio of scrambled to anatomical action cost was **1.06**. The large difference belongs to a particular game. The leaderboard never ran a scrambled-eye control.

## What the circuits contributed

**Memory.** I paired one game frame with reward and another with punishment. On held-out games I tested whether the simulated mushroom body ranked variants of the rewarded frame higher. Sensory input reached the memory cells and their activity passed the sparsity check. Accuracy was **60%** with anatomical wiring, **80%** after rewiring its input and output projections, and **40%** when I scrambled which Kenyon cells received credit. A simple perceptron reached **91.7%**. The learning rule benefited from assigning credit to the appropriate cells. The rewired projections produced the higher recognition score.

**Motion.** A visual patch using trained flyvis parameters passed the direction-selectivity check on moving bars. I then trained a readout to infer displacement direction from the simulated cells' activity. Across three splits with four ARC games held out per split, accuracy was **38.75%** with real wiring and **43.06%** after rewiring. Calibration on a biological stimulus established that the patch could signal motion. Its measured accuracy on game frames settled a separate question.

**Sensitivity.** I also tested the whole-graph ARC interface with a recurrent network calibrated to retain activity longer. Its memory half-life increased from one action in the fly model to three, yet neither preregistered score comparison separated it from its controls at the resolution of the test (roughly 0.1 score point). That limits how much the whole-graph results can say about the fly. An interface that misses a known change in memory can miss a useful circuit too.

## The compass in the dark

One feature of the anatomy stood out before any dynamics ran. Connections in the compass circuit clustered at characteristic distances around a ring. Its measured bandedness was **0.5881**, above all 200 degree-preserving rewires (maximum **0.3376**). Earlier simulations could sustain activity while losing the position where it started. A persistent signal and a remembered heading are different measurements.

I applied Biswas et al.'s published fitting recipe to the anatomical counts from 46 EPG and 42 Delta7 neurons. I pooled them into **16 population units**, averaged equivalent positions around the ring and fitted the coupling gains between populations to the equations for a persistent activity peak. I initialized that peak at a known heading and let the model run in darkness. [Biswas et al., methods](https://doi.org/10.1101/2024.11.01.621596)

Given fitted per-type physiology, two of three settings held the pattern at **all eight starting rotations** for 100 model time constants. Angular drift rounded to **0.0°**. The identical search found **zero qualifying fits on three rewired graphs**. My fitted shape parameters differed from the authors' values. The test measures retention of an initialized pattern. Learning a heading from sight and updating it through a turn would require different inputs and tests.

This was the first time in FlyGI that a computation test passed on the strength of the real wiring counts beating their rewired controls under the same fit. An earlier FlyBench experiment included a win against a rewired control as one part of a different test. Neither experiment contributed leaderboard points.

## A test another ARC team can run

My log stands at 0 for 16 on predictions tied to score. Here is the comparison I would want to see alongside the next claimed gain. Keep the decoder, action budget and held-out games fixed. Replace the proposed source of intelligence with its simplest control. Record where the action traces diverge and which levels they clear. Then check that the benchmark can actually detect a known change in the capability you care about.

I learned the value of that last comparison from my own controller. A coordinate picker shipped with six passing tests. On six public click-only games it visited an average of **72 distinct observations**. Random clicking visited **236**. Anyone building a world model from interaction has a reason to care about that gap. A policy that keeps choosing the same place also chooses which evidence its model gets to see. [Code, experiment registry and run records](https://github.com/msafdari/FlyGI)
