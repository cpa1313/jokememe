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
            "You are a meme generator. Reply with EXACTLY 3 lines, no intro, no explanation, no markdown.\n"
            "Line 1: SETUP_LABEL: [who speaks, e.g. Recruiter]\n"
            "Line 2: SETUP: [what they say, max 12 words]\n"
            "Line 3: PUNCHLINE_LABEL: [who reacts, e.g. Me]\n"
            "Make it relatable, modern and punchy. ONLY output those 3 lines."
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
def _find_font() -> str:
    """Return first existing bold font path, or a bare name as last resort."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            print(f"[Font] Using: {p}")
            return p
    print("[Font] WARNING: no font found in known paths — using bare name")
    return "DejaVuSans-Bold"

FONT_PATH   = _find_font()
FONT_SIZE   = 55          # px — big enough for mobile
TEXT_COLOR  = "black"
TEXT_WRAP   = 26          # chars per line
PADDING_X   = 40          # px from left edge
PADDING_TOP = 260         # push text toward bottom of the white zone


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
        setup_label     = None
        setup           = None
        punchline_label = None

        # Strip markdown and collect non-empty lines
        lines = [re.sub(r'\*+', '', l).strip() for l in raw.splitlines() if re.sub(r'\*+', '', l).strip()]

        # Strategy 1: regex key matching
        for line in lines:
            if re.match(r'SETUP_LABEL\s*:', line, re.IGNORECASE):
                val = line.split(':', 1)[1].strip()
                if val: setup_label = val
            elif re.match(r'SETUP\s*:', line, re.IGNORECASE):
                val = line.split(':', 1)[1].strip()
                if val: setup = val
            elif re.match(r'PUNCHLINE_LABEL\s*:', line, re.IGNORECASE):
                val = line.split(':', 1)[1].strip()
                if val: punchline_label = val

        # Strategy 2: positional fallback — just grab line values in order
        if not all([setup_label, setup, punchline_label]) and len(lines) >= 3:
            print("[Parser] Regex fallback: using positional line extraction")
            def extract_val(line):
                return line.split(':', 1)[1].strip() if ':' in line else line
            setup_label     = setup_label     or extract_val(lines[0])
            setup           = setup           or extract_val(lines[1])
            punchline_label = punchline_label or extract_val(lines[2])

        # Final defaults if all else fails
        setup_label     = setup_label     or "Them"
        setup           = setup           or "..."
        punchline_label = punchline_label or "Me"

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


def has_audio_stream(video_file: Path) -> bool:
    """Returns True if the video file contains at least one audio stream."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=index",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_file)],
        capture_output=True, text=True
    )
    return bool(result.stdout.strip())


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

    video_has_audio = has_audio_stream(video_file)
    print(f"[Video] Has audio stream: {video_has_audio}")

    wrapped = wrap_text(overlay_text)

    # Escape special FFmpeg drawtext characters
    def esc(s: str) -> str:
        return (s.replace("\\", "\\\\")
                  .replace("'",  "\u2019")   # curly apostrophe — safe in drawtext
                  .replace(":",  "\\:")
                  .replace(",",  "\\,")
                  .replace("\n", "\\n"))     # literal \n required by drawtext

    escaped_text = esc(wrapped)

    # drawtext filter — black text, left-aligned, on white background zone
    drawtext_main = (
        f"drawtext=fontfile='{FONT_PATH}':"
        f"text='{escaped_text}':"
        f"fontcolor={TEXT_COLOR}:fontsize={FONT_SIZE}:"
        f"x={PADDING_X}:y={PADDING_TOP}:"
        f"line_spacing=16:"
        f"shadowcolor=gray@0.4:shadowx=2:shadowy=2"
    )

    # Layout: 1920px tall = 480px WHITE text zone on top + 1440px video below
    TEXT_ZONE_H = 480
    VIDEO_H     = 1920 - TEXT_ZONE_H   # 1440

    # Scale+pad the video to fill the bottom zone exactly, then composite onto
    # a white 1080x1920 canvas — text is always in the clear white area at top
    video_filters = (
        # 1. Scale video to FILL the bottom video zone (crop to avoid black bars)
        "[0:v]"
        f"scale=1080:{VIDEO_H}:force_original_aspect_ratio=increase,"
        f"crop=1080:{VIDEO_H}"
        "[vid];"
        # 2. White full-frame canvas
        f"color=white:s=1080x1920:r=30[bg];"
        # 3. Overlay video at y=TEXT_ZONE_H
        f"[bg][vid]overlay=0:{TEXT_ZONE_H}[composed];"
        # 4. Draw black text left-aligned in the white zone at top
        f"[composed]{drawtext_main}[vout]"
    )

    # 5. Audio: mix video audio + music if video has audio, else use music only
    if video_has_audio:
        audio_filters = ";[0:a][1:a]amix=inputs=2:duration=shortest:weights=1 0.15[aout]"
    else:
        audio_filters = f";[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS[aout]"

    filter_complex = video_filters + audio_filters

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
