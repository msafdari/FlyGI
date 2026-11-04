# Six clicks, a map from a fly's eye

[Published Reel](https://www.instagram.com/safdari.mustafa/reel/DfVpJsYBfqZ/),
November 4, 2026, on the public `safdari.mustafa` Instagram account.

A portrait Instagram Reel showing the six actual actions of the historical
local r11l seed-1 run. Narration uses OpenAI `gpt-realtime-2.1`, voice `cedar`.
The existing fly illustrations introduce the story; the game sequence is
an authenticated replay, including the native frames returned by the game.

## Ready-to-post files

Generated media lives under ignored `results/social/instagram_20261104/reel/`:

- `flygi-six-clicks-reel.mp4`: 1080 x 1920, 30 fps, H.264, AAC, fast start.
- `cover.jpg`: portrait cover matching the carousel design.
- `preview.jpg`: ten-frame review sheet.
- `voiceover.wav`: original narration; no added music.

Use [caption.txt](caption.txt) when posting. The caption discloses the
AI-generated narration and illustrations and identifies the actual game replay.
The reel is authored to leave room for Instagram's right and bottom controls.
Check the platform's crop and cover preview before sharing.

## What is shown

The selected run clears level one in six clicks. All six before/after hashes
match the archived trial. Markers use the recorded payload coordinates,
`x = column, y = row`; they do not reconstruct the policy's old internal
coordinate convention. All returned native animation frames are preserved
in their original order. The next screen after completion belongs to level
two and is explicitly labeled that way.

ASSUMPTION: native game frames have order but no declared display duration.
The video spaces them for human viewing and labels the sequence a paced
replay. Spoken word timestamps provide editorial synchronization, not a
measurement of the original agent's wall-clock speed. The native frames,
action count, game coordinates and outcome remain unchanged.

The comparison is a historical local run using an anatomical visual grouping,
an online learned click head, and an active neural tie-breaker. The rearranged
map run took 199 actions to clear the same first level. This is a standout
example, not a broad capability claim: the wider 25-game experiment had
17/75 versus 16/75 first-level completions. The later 0.15 leaderboard agent
is a distinct artifact with neuronal dynamics off.

## Reproduction and review

1. Run `.venv/bin/python docs/social/instagram_20261104/reel/replay.py` to
   recreate the game frames from the local source archive and cached game.
2. The existing narration and timestamp files are reusable. Generating a new
   take with `generate_voice.py` calls the paid OpenAI API and requires
   `OPENAI_API_KEY`; it is not part of the renderer. Never record the key.
3. Run `python3 docs/social/instagram_20261104/reel/render.py` using an
   environment with Playwright, Chromium and FFmpeg. Network requests are
   blocked during layout rendering. The current cues intentionally target
   the recorded 39.75-second take and must be re-aligned for a new take.
4. Inspect `preview.jpg`, play the MP4, and verify its streams with `ffprobe`.
   The script checks screenshot hashes, layout bounds and exact action count.

[replay_provenance.json](replay_provenance.json) records the game evidence;
[voice_provenance.json](voice_provenance.json) records the exact model,
delivery instructions, usage and audio QA;
[render_provenance.json](render_provenance.json) records the final MP4 hash
and timing. Original game frames, audio, intermediate renders and the MP4
stay outside normal Git history.
