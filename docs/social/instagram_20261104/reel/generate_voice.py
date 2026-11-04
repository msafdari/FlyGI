"""Generate the approved Reel narration and retain its alignment transcript.

Requires the existing OPENAI_API_KEY environment variable. Never prints it.
Audio, API transcripts and generated diagnostics remain in ignored results/.
This is publication tooling, not part of the scientific agent.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import time
import wave

from openai import OpenAI

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / "results/social/instagram_20261104/reel"
SCRIPT = (HERE / "voice_script.txt").read_text().strip()
DELIVERY = (
    "You are recording a short science-story voiceover. Read the supplied script "
    "exactly, with no added words, introduction, signoff or stage directions. "
    "Use an adult, warm, natural, conversational English voice: curious and lightly "
    "excited, like sharing a surprising experiment with a friend. Varied, expressive "
    "phrasing and a relaxed smile in the voice. No robotic cadence, advertising "
    "announcer delivery, exaggerated hype, or imitation of any real person. "
    "Aim for about 45 to 50 seconds overall. The six counted numbers One, Two, "
    "Three, Four, Five, Six must each stand alone, with a clear 0.7 to 1 second "
    "pause before the next number, so six game clicks can be shown in sync. "
    "Give 'level one cleared' a small, delighted lift. Emphasize the contrast "
    "with 'a hundred and ninety-nine'. End with inviting curiosity."
)


def generate_realtime(client: OpenAI, output: Path) -> dict:
    chunks, transcript = [], ""
    usage = None
    started = time.monotonic()
    with client.realtime.connect(
        model="gpt-realtime-2.1",
        websocket_connection_options={"open_timeout": 20},
    ) as conn:
        conn.session.update(session={
            "type": "realtime", "output_modalities": ["audio"],
            "audio": {"input": {"turn_detection": None}, "output": {
                "format": {"type": "audio/pcm", "rate": 24000}, "voice": "cedar",
            }},
            "instructions": DELIVERY, "max_output_tokens": 4096,
        })
        conn.conversation.item.create(item={
            "type": "message", "role": "user",
            "content": [{"type": "input_text", "text": SCRIPT}],
        })
        conn.response.create()
        for event in conn:
            if time.monotonic() - started > 150:
                raise TimeoutError("Voice generation exceeded 150 seconds")
            if event.type == "error":
                raise RuntimeError(f"Realtime API: {event.error.code}: {event.error.message}")
            if event.type == "response.output_audio.delta":
                chunks.append(base64.b64decode(event.delta))
            elif event.type == "response.output_audio_transcript.done":
                transcript += event.transcript
            elif event.type == "response.done":
                if event.response.status != "completed":
                    raise RuntimeError(f"Voice status {event.response.status}")
                usage = event.response.usage.model_dump() if event.response.usage else None
                break
    if not chunks:
        raise RuntimeError("No audio returned")
    with wave.open(str(output), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(24000)
        handle.writeframes(b"".join(chunks))
    return {"model": "gpt-realtime-2.1", "voice": "cedar",
            "response_transcript": transcript, "usage": usage}


def generate_speech(client: OpenAI, output: Path) -> dict:
    # ASSUMPTION: this still-supported legacy endpoint is an acceptable fallback
    # only when the requested Realtime model is unavailable. Record its identity.
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts", voice="cedar", input=SCRIPT,
        instructions=DELIVERY, response_format="wav",
    ) as response:
        response.stream_to_file(output)
    return {"model": "gpt-4o-mini-tts", "voice": "cedar"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fallback-speech", action="store_true")
    parser.add_argument("--transcribe-only", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / "voiceover.wav"
    client = OpenAI(timeout=150, max_retries=0)
    if args.transcribe_only:
        metadata = json.loads((OUT / "voice_generation.json").read_text())
    else:
        if output.exists():
            raise FileExistsError("Preserve the existing take before generating another")
        metadata = generate_speech(client, output) if args.fallback_speech else generate_realtime(client, output)
        metadata.update({"script": SCRIPT, "delivery": DELIVERY,
                         "audio_sha256": hashlib.sha256(output.read_bytes()).hexdigest()})
        with wave.open(str(output), "rb") as handle:
            metadata["duration_seconds"] = handle.getnframes() / handle.getframerate()
        (OUT / "voice_generation.json").write_text(json.dumps(metadata, indent=2) + "\n")
        print("Generated", metadata["model"], metadata["duration_seconds"], "seconds", flush=True)
    with output.open("rb") as handle:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=handle, language="en", response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
        ).model_dump()
    (OUT / "voice_alignment.json").write_text(json.dumps(transcript, indent=2) + "\n")
    # ASSUMPTION: ASR timestamps approximate audible word boundaries. Check the
    # count sequence and rendered replay timing; do not present them as ground truth.
    words = transcript.get("words", [])
    counts = []
    expected = ["one", "two", "three", "four", "five", "six"]
    for index in range(len(words) - 5):
        tokens = [re.sub(r"[^a-z]", "", w["word"].lower()) for w in words[index:index+6]]
        if tokens == expected:
            counts = words[index:index+6]
            break
    (OUT / "count_alignment.json").write_text(json.dumps(counts, indent=2) + "\n")
    print("Transcript:", transcript["text"], flush=True)
    print("Count timings:", counts, flush=True)
    if not counts:
        raise ValueError("Could not locate the six counted actions in ASR")


if __name__ == "__main__":
    main()
