# X release thread

Post the nine entries in order after the LinkedIn URL is available. Replace the final bracketed URL with the published post. Labels are for the composer and do not go in the posts. Attach the revised cover to 1, the score chart (fig1) to 3, the probe comparisons (fig3) to 6 and the verdict table including the compass (fig2) to 8. The text is complete without tags.

**1/**

I tested a fruit fly's wiring on ARC-AGI-3. Scrambled circuits scored higher on both my memory and motion tests. The real wiring had its moment in a different experiment. I put its compass in the dark.

**2/**

The MaleCNS team mapped the fly's nervous system. My model kept 166,700 neurons and nearly 25 million connections. To see what the anatomy bought me, I kept each cell's connection counts in the rewired pathways and changed who talked to whom.

**3/**

First, my own code got a reality check. I wrote 13 strategies for the public games. My local score went from 0.55 to 28.74. Four games solved outright. On Kaggle, the baseline and both upgrades scored 0.15, 0.15, 0.15.

**4/**

What ran on Kaggle? A controller that learned which clicks changed the screen. It used a static map of the fly's eye. The simulated neurons were off in all three entries. In the local map test both controllers learned from clicks and used the same neural tie-breaker.

**5/**

On one game, the eye map took 6 actions to clear level one. Its scrambled twin took 199. Next seed, 15 vs 255. Third seed, only the real map finished. Across all 14 runs where both finished, the median cost ratio was 1.06. One game can make a great headline.

**6/**

On held-out ARC games, I rewarded one frame and punished another. The memory circuit picked the rewarded frame's lookalike 60% of the time. Rewired, 80%. A readout of the motion circuit got the direction right 38.75% of the time. Rewired, 43.06%.

**7/**

For the compass test I used Biswas et al.'s recipe. I pooled 88 neurons into 16 units, averaged equivalent positions around the ring and fitted the strengths between them. I placed a peak of activity at a known heading and let the model run in darkness.

**8/**

Two settings held all eight starting headings. Drift rounded to 0.0°. Same search, three rewired graphs, zero qualifying fits. My fitted values differ from the paper's. The experiment tested whether the peak stayed where I put it. Turning and steering are still open.

**9/**

My record on predictions tied to score was 0 for 16. Next time a model seems to remember something, give its scrambled twin the same test.

Paper and figures: https://www.kaggle.com/competitions/arc-prize-2026-paper-track/writeups/flygi-connectome-attribution-audit
Code: https://github.com/msafdari/FlyGI
LinkedIn: https://www.linkedin.com/feed/update/urn:li:activity:7523777525907357697/
