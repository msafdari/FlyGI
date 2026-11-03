# LinkedIn release copy

Paste the text below the rule. Attach the current `media/fig1_ladder_vs_hidden.png` and `media/fig2_verdict_matrix.png`, in that order. The first graphic covers Kaggle. The second includes the fitted compass result. Where the composer offers the verified pages, tag ARC Prize Foundation, Kaggle and Howard Hughes Medical Institute in place. The post also works as plain text.

---

I tested a fruit fly's wiring on ARC-AGI-3. On my memory test and my motion test, the scrambled circuits scored higher. The real wiring pulled ahead in the dark.

I started with a map of 166,700 neurons and nearly 25 million connections from the MaleCNS project at HHMI Janelia and its partners. A wiring diagram tells you which cells talk to which, and how many synaptic contacts they make. It doesn't tell you how hard one cell drives the next.

I wanted to know what that map could buy an agent faced with a game it had never seen. So I gave my simulated circuits opponents. Each scrambled copy kept the number of connections going into and out of each cell in the rewired pathways. I changed who talked to whom.

On held-out ARC games, I showed the learning circuit one rewarded frame and one punished frame. It picked the rewarded frame's lookalike 60% of the time. Its scrambled copy got 80%. The fly's motion circuit read the direction of a moving pattern with 38.75% accuracy. Scrambled, it got 43.06%.

Then my own code took its turn. I wrote thirteen strategies for the public games. The local score jumped 52-fold. Four complete wins. On Kaggle the baseline and both upgrades scored 0.15, 0.15, 0.15. Those agents used a static map of the fly's eye and an online click predictor. The simulated neurons were switched off. My log of predictions tied to score stands at 0 for 16.

I tested the eye map locally with the same learning rule and neural tie-breaker in both agents. On one public game, the controller cleared level one in 6 actions. Scramble the map and it took 199. The next seed was 15 versus 255. Across all 14 runs where both versions finished level one, the median cost ratio was only 1.06. I would have told a very different story if I'd stopped at that game.

The fly's compass gave me a way to test memory directly. I used Biswas and colleagues' recipe to turn the wiring counts of 88 compass neurons into a symmetric model with 16 units and fitted connection strengths. I set a peak of activity at a known heading and watched where it went in darkness.

Two settings held all eight starting headings. The drift rounded to 0.0 degrees. I ran the same search on three scrambled copies. It found no fit on any of them. My fitted values differ from the paper's. What I could measure was a model built from the real counts remembering where I put the peak.

If you're building a world model, try this on your favorite result. Scramble the part you think is doing the remembering. Give its twin the same fitting budget. See which memory survives.

Paper on Kaggle: https://www.kaggle.com/competitions/arc-prize-2026-paper-track/writeups/flygi-connectome-attribution-audit
Code and experiment log: https://github.com/msafdari/FlyGI

#ARCPrize #WorldModels #Neuroscience
