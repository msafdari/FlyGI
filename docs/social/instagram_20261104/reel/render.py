"""Compose authenticated replay frames and a generated narration into a Reel.

Run from the repo root with system Python (Playwright + Chromium installed).
This is editorial composition; it does not run or change the agent policy.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
OUT = ROOT / "results/social/instagram_20261104/reel"
FRAMES = OUT / "rendered"
ASSETS = SOURCE.parent / "assets"
FPS = 30


def read(name):
    return json.loads((OUT / name).read_text())


def duration(path):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]))


manifest = read("manifest.json")
alignment = read("voice_alignment.json")
counts = read("count_alignment.json")
assert len(counts) == len(manifest["actions"]) == 6
for snapshot in manifest["snapshots"]:
    assert hashlib.sha256((OUT / snapshot["endpoint"]).read_bytes()).hexdigest() == snapshot["endpoint_sha256"]
assert manifest["snapshots"][-1]["levels_completed"] == 1

# ASSUMPTION: word timestamps are accurate enough for editorial synchronization,
# not ground-truth speech boundaries. The spoken counts and complete six-action
# order are checked against count_alignment.json; a different take needs new cues.
# Captions use the approved script, not Whisper's "We arranged" mistranscription.
cues = [
    (0.00, "I gave my AI something surprising."),
    (2.72, "A map from a fruit fly’s eye."),
    (5.48, "Scientists mapped how its visual cells are arranged."),
    (8.52, "I borrowed that layout"),
    (9.38, "to help my program organize what it sees."),
    (12.54, "Then I gave it a puzzle with no instructions."),
    (15.74, "Watch these six clicks."),
    *[(entry["start"], entry["word"].capitalize() + ".") for entry in counts],
    (24.60, "And… level one cleared."),
    (27.28, "Rearrange the map,"),
    (28.40, "and the same program took 199 actions."),
    (32.08, "Across 25 games, the overall results were close."),
    (35.72, "But this puzzle gave me a clue."),
    (38.02, "What else could we borrow from nature?"),
]
assert abs(duration(OUT / "voiceover.wav") - 39.75) < 0.15, "New narration needs re-alignment"
END = duration(OUT / "voiceover.wav") + 2.0
events = {0.0, 5.48, 12.54, 15.74, 26.16, 27.28, 32.08, 38.02, END}
events.update(t for t, _ in cues)
game_events = [(12.54, "endpoint-00.png", None, 0)]
for i, (count, action) in enumerate(zip(counts, manifest["actions"]), start=1):
    start = count["start"]
    click = [action["payload"]["x"], action["payload"]["y"]]
    events.add(start)
    # Show the actual click position on the pre-action frame for 0.18 seconds.
    game_events.append((start, f"endpoint-{i - 1:02d}.png", click, i))
    native = manifest["snapshots"][i]["native_frames"]
    # ASSUMPTION: native frames have order but no declared display time. Pace them
    # evenly for viewing; preserve every returned frame and label this a replay.
    finish = min(counts[i]["start"] - .18, start + .9) if i < 6 else 26.16
    for j, filename in enumerate(native):
        time = start + .18 + j * (finish - start - .18) / max(1, len(native) - 1)
        game_events.append((time, filename, None, i))
        events.add(time)
game_events.sort()


def state(time):
    caption = next(text for when, text in reversed(cues) if when <= time)
    s = dict(art=(ASSETS / "fly-puzzle.png").as_uri(), caption=caption,
             headline="I gave an AI<br>a map from<br><em>a fly’s eye.</em>",
             footer="A FlyGI experiment · AI-generated narration and illustrations")
    if 5.48 <= time < 12.54:
        s.update(style="eyescene", art=(ASSETS / "eye-map.png").as_uri(),
                 headline="A tiny idea<br><em>from nature.</em>",
                 subline="Borrowing the arrangement of visual cells")
    elif 12.54 <= time < 27.28:
        _, filename, click, number = next(e for e in reversed(game_events) if e[0] <= time)
        s.update(style="gamescene", art="", game=(OUT / filename).as_uri(),
                 headline="A puzzle.<br><em>No instructions.</em>" if time < 15.74 else
                 "Watch the<br><em>six actual clicks.</em>" if time < 26.16 else
                 "Level one<br><em>cleared.</em>",
                 counter=f"CLICK {number} / 6" if number else "START",
                 click=click,
                 subline="The actual game. Click markers added for clarity." if time < 26.16 else
                 "Level two has unlocked. This is its starting screen.",
                 footer="Local ARC-AGI-3 · r11l · Paced replay\nGame © ARC Prize Foundation")
    elif 27.28 <= time < 32.08:
        s.update(style="statsscene", art="", compare=True,
                 headline="One puzzle.<br><em>A huge difference.</em>",
                 subline="Same program. Changed visual map.<br>One local run · first-level completion",
                 footer="ARC-AGI-3 public game r11l · Actions include resets")
    elif 32.08 <= time < 38.02:
        s.update(style="statsscene", art="", broader=True,
                 headline="The wider test?<br><em>Much closer.</em>",
                 subline="First-level completions<br>25 public games × 3 runs per version",
                 footer="The standout was one game. The full results are public.")
    elif time >= 38.02:
        s.update(headline="What else could<br>we borrow<br><em>from nature?</em>", cta=True,
                 footer="FlyGI · Mustafa Safdari · Code and results are public")
        if time > 39.5:
            s["caption"] = ""
    return s


def validate(page):
    issues = page.locator('#stage').evaluate('''stage => {
      const bounds=stage.getBoundingClientRect(), issues=[];
      for(const id of ['headline','caption','subline','footer','cta']) {
        const el=document.getElementById(id);if(getComputedStyle(el).display==='none')continue;
        if(el.scrollWidth>el.clientWidth+1)issues.push(id+' horizontal overflow');
        const r=el.getBoundingClientRect();if(r.bottom>1760)issues.push(id+' below safe area');
      } return issues;
    }''')
    if issues:
        raise ValueError(issues)


def run():
    FRAMES.mkdir(parents=True, exist_ok=True)
    times = sorted(events)
    sequence = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":1080,"height":1920},device_scale_factor=1)
        page.route('**/*', lambda route: route.continue_() if route.request.url.startswith('file:') else route.abort())
        page.goto((SOURCE / "layout.html").as_uri())
        for i, time in enumerate(times[:-1]):
            s = state(time)
            page.evaluate("state => window.setState(state)", s)
            validate(page)
            path = FRAMES / f"{i:03d}.png"
            page.screenshot(path=path)
            sequence.append({"start":time,"duration":times[i+1]-time,"frame":str(path.relative_to(ROOT)),"scene":s})
        # Cover is authored at full portrait resolution, independent of Instagram cropping.
        cover = state(0); cover.update(caption="Six actual clicks. See what happened.")
        page.evaluate("state => window.setState(state)",cover)
        page.screenshot(path=OUT / "cover.jpg",type="jpeg",quality=95)
        samples = [0, 6, 13, 17.4, 22.4, 25.6, 26.3, 29, 34, 38.5]
        preview_paths=[]
        for i,t in enumerate(samples):
            page.evaluate("state => window.setState(state)",state(t))
            path=FRAMES / f"preview-{i}.jpg"
            page.screenshot(path=path,type='jpeg',quality=90)
            preview_paths.append(path)
        tiles=''.join(f'<div><img src="{path.as_uri()}"><p>{t:.1f}s</p></div>' for path,t in zip(preview_paths,samples))
        page.set_content('<style>body{margin:0;padding:10px;background:#172323;color:white;font:20px Arial;display:grid;grid-template-columns:repeat(5,216px);gap:10px}img{width:216px;height:384px}p{margin:4px 0 12px}</style>'+tiles)
        page.wait_for_function('Array.from(document.images).every(im=>im.complete&&im.naturalWidth>0)')
        page.set_viewport_size({"width":1140,"height":876})
        page.screenshot(path=OUT / "preview.jpg",type='jpeg',quality=94,full_page=True)
        browser.close()
    (OUT / "timeline.json").write_text(json.dumps(sequence,indent=2)+'\n')
    concat=OUT / "frames.txt"
    lines=[]
    for item in sequence:
        lines += [f"file '{ROOT / item['frame']}'",f"duration {item['duration']:.9f}"]
    lines += [f"file '{ROOT / sequence[-1]['frame']}'"]
    concat.write_text('\n'.join(lines)+'\n')
    target=OUT / "flygi-six-clicks-reel.mp4"
    subprocess.run([
        'ffmpeg','-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(concat),
        '-i',str(OUT/'voiceover.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','medium',
        '-crf','19','-pix_fmt','yuv420p','-r',str(FPS),'-fps_mode','cfr','-c:a','aac','-b:a','192k',
        '-af','apad=pad_dur=2','-t',str(END),'-movflags','+faststart',str(target),
    ],check=True)
    metadata={"video":str(target.relative_to(ROOT)),"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
              "duration_seconds":duration(target),"dimensions":[1080,1920],"fps":FPS,"codec":"H264/AAC",
              "native_frames_preserved":sum(s['native_frame_count'] for s in manifest['snapshots']),
              "count_alignment_seconds":[e['start'] for e in counts],"end_of_level_one_seconds":26.16,
              "narration":"voiceover.wav","editorial_timing":"Returned native frames paced for viewing; click markers match recorded payload x=column,y=row."}
    (SOURCE/'render_provenance.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(metadata,indent=2),flush=True)


if __name__ == '__main__':
    run()
