#!/usr/bin/env python3
"""
Meme Reel Maker - Generates funny meme videos with text overlays
Uses Groq AI to generate jokes, overlays them on videos, adds music,
then posts to Facebook Reels.
"""

import os
import sys
import random
import textwrap
import requests
import subprocess
from pathlib import Path
from groq import Groq

def _require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        print(f"\n❌ ERROR: Environment variable '{name}' is missing or empty!")
        print(f"   → Go to your GitHub repo → Settings → Secrets and variables → Actions")
        print(f"   → Add a secret named: {name}\n")
        import sys; sys.exit(1)
    return val

GROQ_API_KEY    = _require_env("GROQ_API_KEY")
FB_ACCESS_TOKEN = _require_env("FB_ACCESS_TOKEN")
FB_PAGE_ID      = _require_env("FB_PAGE_ID")

VIDEOS_DIR  = Path("assets/videos")
MUSIC_DIR   = Path("assets/music")
OUTPUT_DIR  = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_VIDEO = OUTPUT_DIR / "reel.mp4"

# ── Meme formats (mirrors the 3 styles you showed) ─────────────────────────
MEME_FORMATS = [
    # Format A: "X says Y  /  Z says:"  →  reaction video
    {
        "template": "{setup_label}: {setup}\n\n{punchline_label}:",
        "prompt": (
            "Write a short, funny 2-line meme joke in this exact format:\n"
            "SETUP_LABEL: <who is speaking first, e.g. 'Recruiter', 'Teacher', 'Boss'>\n"
            "SETUP: <what they say>\n"
            "PUNCHLINE_LABEL: <who reacts, e.g. 'Me', 'That one intern', 'The cat'>\n"
            "Make it relatable, modern and punchy. Max 15 words per line. "
            "Output ONLY those 4 lines, nothing else."
        ),
    },
    # Format B: observation headline  →  funny reaction video
    {
        "template": "{headline}",
        "prompt": (
            "Write a single funny observation/headline meme (like 'FIFA forcing players to have "
            "multiple hydration breaks to get a few ads in'). "
            "It should be a relatable, slightly absurd take on everyday life, sports, or work. "
            "Max 20 words. Output ONLY the headline, nothing else."
        ),
    },
]

# ── Text styling constants ──────────────────────────────────────────────────
FONT_PATH   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE   = 52          # px — big enough for mobile
TEXT_COLOR  = "black"
TEXT_WRAP   = 28          # chars per line
PADDING_X   = 40          # px from left edge
PADDING_TOP = 60          # px from top of text zone


# ══════════════════════════════════════════════════════════════════════════════
# 1. JOKE GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_joke(fmt: dict) -> tuple[str, str]:
    """
    Returns (overlay_text, caption_for_fb).
    """
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": fmt["prompt"]}],
        temperature=0.9,
        max_tokens=120,
    )
    raw = response.choices[0].message.content.strip()
    print(f"[Groq] Raw response:\n{raw}\n")

    # ── Parse format A ──────────────────────────────────────────────────────
    if "SETUP_LABEL" in fmt["prompt"]:
        import re
        # Robust parsing: strip markdown bold markers, handle any casing/spacing
        setup_label     = "Them"
        setup           = "..."
        punchline_label = "Me"
        for line in raw.splitlines():
            clean = re.sub(r'\*+', '', line).strip()  # remove **bold** markers
            if re.match(r'SETUP_LABEL\s*:', clean, re.IGNORECASE):
                val = clean.split(':', 1)[1].strip()
                if val: setup_label = val
            elif re.match(r'SETUP\s*:', clean, re.IGNORECASE):
                val = clean.split(':', 1)[1].strip()
                if val: setup = val
            elif re.match(r'PUNCHLINE_LABEL\s*:', clean, re.IGNORECASE):
                val = clean.split(':', 1)[1].strip()
                if val: punchline_label = val
        print(f"[Parsed] setup_label={setup_label!r}  setup={setup!r}  punchline_label={punchline_label!r}")
        overlay_text    = f"{setup_label}: {setup}\n\n{punchline_label}:"
        caption         = f"{setup_label}: {setup}\n{punchline_label}: 😂\n\n#memes #funny #relatable"
    else:
        # Format B — plain headline
        overlay_text = raw
        caption      = f"{raw}\n\n#memes #funny #lol"

    return overlay_text, caption


# ══════════════════════════════════════════════════════════════════════════════
# 2. VIDEO ASSEMBLY  (pure FFmpeg — no opencv dependency)
# ══════════════════════════════════════════════════════════════════════════════

def pick_random(directory: Path, extensions: list[str]) -> Path:
    files = [f for f in directory.iterdir() if f.suffix.lower() in extensions]
    if not files:
        raise FileNotFoundError(f"No files with {extensions} found in {directory}")
    return random.choice(files)


def wrap_text(text: str, width: int = TEXT_WRAP) -> str:
    lines = []
    for para in text.split("\n"):
        if para.strip() == "":
            lines.append("")
        else:
            lines.extend(textwrap.wrap(para, width=width) or [""])
    return "\n".join(lines)


def get_video_duration(video_file: Path) -> float:
    """Returns the duration of the video in seconds using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_file)],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 59.0  # fallback if ffprobe fails


def build_video(overlay_text: str, output_path: Path) -> None:
    """
    Picks a random video + music, overlays text at the top (white bg, black text,
    left-aligned), mixes in background music at low volume, matches source video duration.
    """
    video_file = pick_random(VIDEOS_DIR, [".mp4", ".mov", ".webm", ".avi"])
    music_file = pick_random(MUSIC_DIR,  [".mp3", ".wav", ".aac", ".m4a"])

    print(f"[Video] Using video: {video_file}")
    print(f"[Music] Using music: {music_file}")

    # Get actual video duration
    duration = get_video_duration(video_file)
    print(f"[Video] Duration: {duration:.2f}s")

    wrapped = wrap_text(overlay_text)

    # Escape special FFmpeg drawtext characters
    def esc(s: str) -> str:
        return (s.replace("\\", "\\\\")
                  .replace("'",  "\u2019")   # curly apostrophe — safe in drawtext
                  .replace(":",  "\\:")
                  .replace(",",  "\\,"))

    escaped_text = esc(wrapped)

    # drawtext filter — black text, left-aligned, on white background zone
    drawtext_main = (
        f"drawtext=fontfile='{FONT_PATH}':"
        f"text='{escaped_text}':"
        f"fontcolor={TEXT_COLOR}:fontsize={FONT_SIZE}:"
        f"x={PADDING_X}:y={PADDING_TOP}:"
        f"line_spacing=14"
    )

    # Layout: 1920px tall = 480px WHITE text zone on top + 1440px video below
    TEXT_ZONE_H = 480
    VIDEO_H     = 1920 - TEXT_ZONE_H   # 1440

    # Scale+pad the video to fill the bottom zone exactly, then composite onto
    # a white 1080x1920 canvas — text is always in the clear white area at top
    filter_complex = (
        # 1. Scale video to fill the bottom video zone (letterbox if needed)
        "[0:v]"
        f"scale=1080:{VIDEO_H}:force_original_aspect_ratio=decrease,"
        f"pad=1080:{VIDEO_H}:(ow-iw)/2:(oh-ih)/2:color=white"
        "[vid];"
        # 2. White full-frame canvas
        f"color=white:s=1080x1920:r=30[bg];"
        # 3. Overlay video at y=TEXT_ZONE_H
        f"[bg][vid]overlay=0:{TEXT_ZONE_H}[composed];"
        # 4. Draw black text left-aligned in the white zone at top
        f"[composed]{drawtext_main}[vout];"
        # 5. Mix original audio with background music at 15% volume
        "[0:a][1:a]amix=inputs=2:duration=shortest:weights=1 0.15[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_file),
        "-i", str(music_file),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-t", str(duration),           # match actual source video length
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_path),
    ]

    print(f"[FFmpeg] Running…")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[FFmpeg STDERR]", result.stderr[-2000:])
        raise RuntimeError("FFmpeg failed — see stderr above")

    print(f"[FFmpeg] Output: {output_path}  ({output_path.stat().st_size // 1024} KB)")


# ══════════════════════════════════════════════════════════════════════════════
# 3. FACEBOOK REELS UPLOAD  (two-step: initialise → upload → publish)
# ══════════════════════════════════════════════════════════════════════════════

def post_to_facebook_reel(video_path: Path, caption: str) -> str:
    """
    Uploads a video as a Facebook Reel using the Graph API.
    Uses the correct 3-step flow: start → upload bytes → finish/publish.
    Returns the published video ID.
    """
    file_size = video_path.stat().st_size
    base_url  = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/video_reels"

    # ── Step 1: Start upload session ─────────────────────────────────────────
    print("[FB] Step 1 — Starting upload session…")
    r1 = requests.post(base_url, data={
        "upload_phase":  "start",
        "access_token":  FB_ACCESS_TOKEN,
    })
    print(f"[FB] Start response ({r1.status_code}): {r1.text}")
    r1.raise_for_status()
    resp1 = r1.json()

    # Guard: must have at least video_id
    if "video_id" not in resp1:
        raise RuntimeError(f"FB start phase missing video_id. Full response: {resp1}")

    video_id = resp1["video_id"]
    # Newer Graph API (v25+) returns upload_url directly instead of upload_session_id
    upload_url = resp1.get(
        "upload_url",
        f"https://rupload.facebook.com/video-upload/v25.0/{video_id}"
    )
    print(f"[FB] video_id={video_id}  upload_url={upload_url}")

    # ── Step 2: Upload raw bytes ──────────────────────────────────────────────
    print("[FB] Step 2 — Uploading video bytes…")
    with open(video_path, "rb") as fh:
        video_bytes = fh.read()

    r2 = requests.post(
        upload_url,
        headers={
            "Authorization": f"OAuth {FB_ACCESS_TOKEN}",
            "offset":        "0",
            "file_size":     str(file_size),
            "Content-Type":  "application/octet-stream",
        },
        data=video_bytes,
    )
    print(f"[FB] Upload response ({r2.status_code}): {r2.text}")
    r2.raise_for_status()

    # ── Step 3: Finish & publish ──────────────────────────────────────────────
    print("[FB] Step 3 — Publishing reel…")
    r3 = requests.post(base_url, data={
        "upload_phase":  "finish",
        "video_id":      video_id,
        "access_token":  FB_ACCESS_TOKEN,
        "description":   caption,
        "video_state":   "PUBLISHED",
    })
    print(f"[FB] Publish response ({r3.status_code}): {r3.text}")
    r3.raise_for_status()
    return video_id


# ══════════════════════════════════════════════════════════════════════════════
# 4. MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    fmt = random.choice(MEME_FORMATS)
    print("[Step 1] Generating joke with Groq…")
    overlay_text, caption = generate_joke(fmt)
    print(f"[Joke]\n{overlay_text}\n")

    print("[Step 2] Building video with FFmpeg…")
    build_video(overlay_text, OUTPUT_VIDEO)

    print("[Step 3] Posting to Facebook Reels…")
    post_id = post_to_facebook_reel(OUTPUT_VIDEO, caption)
    print(f"[Done] Published! Video ID: {post_id}")


if __name__ == "__main__":
    main()
