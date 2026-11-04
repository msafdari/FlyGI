# A map from a fly's eye

Six finished Instagram cards for a general audience, plus a Story teaser.

Upload `exports/01-flygi.jpg` through `06-flygi.jpg`, in that order, with
[caption.txt](caption.txt). Each card is 1080 × 1350. Keep the portrait crop.
Add the alt text below through the post's accessibility controls.

The 1080 × 1920 [Story teaser](exports/story-teaser.jpg) leaves space for a
link sticker beneath the arrow. Link the published carousel or the
[project](https://github.com/msafdari/FlyGI). The post works without account
tags. Add verified MaleCNS/HHMI and ARC Prize tags if those accounts are
available in the composer. A URL in the caption is a human-readable pointer.

[Preview of all six](exports/preview.jpg) · [Editable layout](carousel.html)

## Story and evidence

The post follows the local eye-map comparison. Its borrowed ingredient is
the anatomical arrangement used by a learned click predictor. Both local
arms also have the same active neural tie-breaker. It presents the standout
r11l result and the 17/75 versus 16/75 wider outcome on adjacent cards.
The [publication factsheet](../../arenas/task1_arc_paper/factsheet.md#eye-map-action-audit)
contains all paired counts and their definitions. Actions include resets.
The compass is a separate experiment and is a candidate for a later post.

The original Instagram draft has been superseded. The later leaderboard
agents scored 0.15 using static anatomy with neuronal dynamics disabled.
These cards describe the historical local comparison, which used active
dynamics. No new trial or leaderboard submission was run for this post.

Slide 2 is a 64 × 64 game frame enlarged with nearest-neighbor sampling and
the official ARC palette. Its replay matched all six before-frame and all
six after-frame hashes of the archived r11l seed-1 run. After the sixth
action the environment already displays level two. That secondary image
is kept beside the start frame with the explicit label in
[game_provenance.json](game_provenance.json). The carousel uses only the
starting frame. Raw frame grids and the replay helper are under ignored
`results/social/instagram_20261104/`.

The two fly illustrations were generated with the built-in image tool.
They express the story visually and are labeled as illustrations. Exact
prompts are in [image_prompts.json](image_prompts.json). Layout, typography,
statistics and screenshots were composed separately in HTML. The generated
art was inspected before use. All six cards were inspected together at
phone scale, and export checks cover dimensions, missing assets and text
clipping. The small dots on card 5 represent individual runs, with 75 per
row and exactly 17 or 16 highlighted.

## Alt text

1. A golden fruit fly with translucent wings stands beside a glowing pixel
   puzzle on a dark teal background. Text reads, “I gave an AI a map from a
   fly’s eye. Then I gave it a puzzle game.” This is an illustration.
2. An actual screen from the public ARC-AGI-3 game r11l. Purple and gray
   pixel shapes sit in a dark circular area. Text reads, “An AI game.
   No instruction manual. Try a click. Watch what changes. Figure out how
   to win.”
3. An illustrated close-up of a fly’s compound eye connects to a grid of
   colored squares. Text explains that the program borrowed the layout
   of the fly’s visual cells to group parts of its game screen.
4. The same local puzzle needed 6 actions with the visual map and 199 with
   the rearranged map. Another run needed 15 versus 255. On the remaining
   run the visual map cleared level one in 57 actions and the other did
   not clear it within 600. Actions include resets.
5. A grid shows first-level completions across 75 runs of 25 public games.
   The visual map cleared 17 and the rearranged map cleared 16. Text says
   the big gap belonged to one game.
6. The illustrated fly returns beneath “What else could we borrow from
   nature?” The closing text invites readers to follow FlyGI, Mustafa
   Safdari’s public experiment.

## Rendering

Use a Python environment containing Playwright and its Chromium browser.
Run `python3 docs/social/instagram_20261104/render.py` from the repository.
The script renders local assets with network requests blocked. On macOS a
sandboxed browser may require permission to start. Recheck the preview
when editing text or images.

The posting ZIP contains the six cards, Story teaser, caption and this
README. The local archive lives in ignored `results/social/instagram_20261104/`.
