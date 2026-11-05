# X release thread (v6, restored voice, November 4)

*(The live thread is this text, reposted on November 4 after the November 3
flat version was taken down at the user's request. Order: post 1 first, each
later post as a reply in the same thread. Attach media/cover.png to 1,
fig1_ladder_vs_hidden.png to 3, fig3_controls_both_ways.png to 4 and
fig2_verdict_matrix.png to 7. Each [TAG: ...] slot is resolved in the composer
to the official account the typeahead shows, or the slot text is deleted;
never a guessed handle. Lengths with slot text, URLs counted as 23:
245/263/273/270/270/236/259/215/250. Post 5 is the October 31 post rewritten to
the paired eye-map result; the 2.59x, 11.59x and 4.5x figures never appear.
Every number has a row in docs/social/FACTS.md.)*

**1/**

Scientists mapped every connection in a fruit fly's brain. I spent weeks betting that map could earn its keep on an AI reasoning benchmark. It lost all season. I published every loss. Days ago, it finally won one back. Here is the whole story. 🧵

**2/**

The bet: a fly brain's complete wiring map from [TAG: HHMI Janelia Research Campus]. 166,700 neurons. About 25 million connections. And one rule to keep me honest: every fly circuit must beat a scrambled copy of itself. Same connections per neuron, random wiring.

**3/**

The humbling came first. My own hand-built game strategies grew my local score about 52x, 0.55 to 28.74. On the hidden games at [TAG: Kaggle]: 0.15, three times. 0.15 is what an agent earns when nothing it knows matches anything it sees. My cleverness bought nothing there.

**4/**

It got worse. The fly's motion detectors and its learning center passed their biology checks, then lost the AI tasks to scrambled copies of their own wiring. Memory: real 0.600, scrambled 0.800. Motion: 0.3875 vs 0.4306. On these tasks the scramble beat the real wiring.

**5/**

One thing looked like a survivor: the fly's eye map. Pure anatomy, no training. On one game it cleared level one in 6 actions where the scrambled map took 199, then 15 vs 255. Across all 14 runs where both finished, the median cost ratio was 1.06. One game, not a trend.

**6/**

Then the finale. The fly's internal compass, the circuit it uses to track which way it faces, had failed in all three earlier versions I built. There was one thing I had never given it: electrical properties fitted for each neuron type.

**7/**

Once I fitted each neuron type's electrical properties, via Biswas et al.'s published recipe applied once to the wiring counts, the compass (a simplified model) held direction: 8/8 angles, 0.0° off. None of the three scrambled copies formed a working compass.

**8/**

The fine print is the flex: that win earns zero benchmark points. My fitted numbers differ from the published ones, flagged. And all sixteen of my score predictions were wrong. Published too. Honesty is the product.

**9/**

Every biology-helps-AI claim should have to beat a scrambled copy of itself. Mine did, once, after losing all season in public. Full writeup with [TAG: ARC Prize]:
https://www.kaggle.com/competitions/arc-prize-2026-paper-track/writeups/flygi-connectome-attribution-audit
Deep dive: https://www.linkedin.com/feed/update/urn:li:activity:7523777525907357697/
#ARCPrize #AI #neuroscience
