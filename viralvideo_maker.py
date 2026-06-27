#!/usr/bin/env python3
"""
Meme Reel Maker - Relationship & Single Life Edition 💕😂
Generates cheeky relationship/dating/single-life jokes via Groq,
overlays bold text ON TOP of your Facebook-ready videos,
then posts to Facebook Reels.

Folder layout:
  assets/videos/   ← your pre-made FB-compatible .mp4 clips
  output/          ← generated reel saved here
"""

import os
import sys
import random
import textwrap
import subprocess
from pathlib import Path

# ── Auto-install missing packages ──────────────────────────────────────────────
def _ensure_packages(*packages):
    import importlib.util
    missing = [p for p in packages if not importlib.util.find_spec(p)]
    if missing:
        print(f"[Setup] Installing: {missing}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *missing])

_ensure_packages("Pillow", "requests", "groq")

import requests
from groq import Groq


# ── Env vars ───────────────────────────────────────────────────────────────────
def _require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        print(f"\n❌ Missing env var: '{name}'")
        print(f"   → GitHub repo → Settings → Secrets → Actions → Add: {name}\n")
        sys.exit(1)
    return val

GROQ_API_KEY    = _require_env("GROQ_API_KEY")
FB_ACCESS_TOKEN = _require_env("FB_ACCESS_TOKEN")
FB_PAGE_ID      = _require_env("FB_PAGE_ID")


# ── Paths ──────────────────────────────────────────────────────────────────────
VIDEOS_DIR  = Path("assets/prettyaivideos")
OUTPUT_DIR  = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_VIDEO = OUTPUT_DIR / "reel.mp4"


# ══════════════════════════════════════════════════════════════════════════════
# 1. JOKE FORMATS  —  cheeky relationship / single life humor
# ══════════════════════════════════════════════════════════════════════════════

JOKE_THEMES = [

    # ── Format A: "X says / Me:" reaction style ───────────────────────────────
    {
        "style": "reaction",
        "prompt": (
            "You are a cheeky adult humor meme page. Write a funny relatable meme about "
            "relationships, dating, or being single — the kind that makes people say 'lol same'. "
            "Topics can include: couples arguing over dumb stuff, being in a relationship vs being single, "
            "dating red flags, love language fails, situationships, late-night texting, etc. "
            "Keep it cheeky and fun — NOT explicit or vulgar.\n\n"
            "Reply with EXACTLY 3 lines, no intro, no markdown, no explanation:\n"
            "Line 1: SPEAKER: [who speaks, e.g. 'My partner', 'Him', 'Her', 'My single friends']\n"
            "Line 2: SETUP: [what they say or do, max 12 words]\n"
            "Line 3: REACTOR: [who reacts, e.g. 'Me', 'My bank account', 'My pillow']\n"
            "ONLY output those 3 lines."
        ),
    },

    # ── Format B: Observation / fun fact headline ─────────────────────────────
    {
        "style": "headline",
        "prompt": (
            "You are a cheeky adult humor meme page. Write ONE funny observation or 'fun fact' "
            "about relationships, dating, or single life. "
            "Style examples: 'Fun fact: being single means you never have to argue about the thermostat', "
            "'Nobody talks about how peaceful it is eating your food without someone asking for a bite', "
            "'Relationship milestone: having your own blanket'. "
            "Keep it witty, relatable, slightly cheeky — NOT vulgar or explicit. "
            "Max 25 words. Output ONLY the text, nothing else."
        ),
    },

    # ── Format C: Single life benefit fact ───────────────────────────────────
    {
        "style": "benefit",
        "prompt": (
            "You are a cheeky meme page celebrating single life. Write ONE short funny "
            "'benefit of being single' statement. "
            "Examples: 'Benefit of being single: the whole bed is yours', "
            "'Being single means zero unsolicited opinions about your food choices'. "
            "Keep it funny and relatable, NOT explicit. Max 20 words. Output ONLY the text."
        ),
    },

    # ── Format D: Relationship struggle truth ─────────────────────────────────
    {
        "style": "truth",
        "prompt": (
            "You are a cheeky relationship humor meme page. Write ONE short funny truth "
            "about being in a relationship that couples will immediately recognize. "
            "Examples: 'In a relationship you stop asking where to eat and start arguing about it instead', "
            "'Couples therapy but make it: debating what to watch for 45 mins then falling asleep'. "
            "Keep it funny and real, NOT explicit. Max 25 words. Output ONLY the text."
        ),
    },
]


# ── Text styling ───────────────────────────────────────────────────────────────
FONT_SIZE     = 62
TEXT_WRAP     = 22
TEXT_COLOR    = "white"
SHADOW_COLOR  = "black"
SHADOW_OFFSET = 3       # px shadow for readability on any background


# ══════════════════════════════════════════════════════════════════════════════
# 2. JOKE GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_joke() -> tuple[str, str]:
    """Returns (overlay_text, fb_caption)."""
    fmt    = random.choice(JOKE_THEMES)
    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": fmt["prompt"]}],
        temperature=0.92,
        max_tokens=140,
    )
    raw = response.choices[0].message.content.strip()
    print(f"[Groq] Style={fmt['style']}  Raw:\n{raw}\n")

    # ── Parse reaction format (3 lines) ───────────────────────────────────────
    if fmt["style"] == "reaction":
        import re
        lines = [re.sub(r'\*+', '', l).strip() for l in raw.splitlines()
                 if re.sub(r'\*+', '', l).strip()]

        speaker  = None
        setup    = None
        reactor  = None

        for line in lines:
            if re.match(r'SPEAKER\s*:', line, re.IGNORECASE):
                speaker = line.split(':', 1)[1].strip()
            elif re.match(r'SETUP\s*:', line, re.IGNORECASE):
                setup = line.split(':', 1)[1].strip()
            elif re.match(r'REACTOR\s*:', line, re.IGNORECASE):
                reactor = line.split(':', 1)[1].strip()

        # Positional fallback
        if not all([speaker, setup, reactor]) and len(lines) >= 3:
            def _val(l):
                return l.split(':', 1)[1].strip() if ':' in l else l
            speaker  = speaker  or _val(lines[0])
            setup    = setup    or _val(lines[1])
            reactor  = reactor  or _val(lines[2])

        speaker  = speaker  or "Them"
        setup    = setup    or "..."
        reactor  = reactor  or "Me"

        overlay = f"{speaker}: {setup}\n\n{reactor}:"
        caption = f"{speaker}: {setup}\n{reactor}: 💀😂\n\n#relationshiphumor #datinglife #singlelife #memes #funny"

    # ── All other formats: plain text ─────────────────────────────────────────
    else:
        overlay = raw
        tags = {
            "headline": "#relationshipmemes #datinghumor #couplegoals #funny",
            "benefit":  "#singlelife #singleandthriving #singlehumor #memes",
            "truth":    "#couplehumor #relationshiptruth #married #relatable",
        }.get(fmt["style"], "#memes #funny")
        caption = f"{raw}\n\n{tags}"

    return overlay, caption


# ══════════════════════════════════════════════════════════════════════════════
# 3. RENDER TEXT PNG  (Pillow — reliable cross-platform)
# ══════════════════════════════════════════════════════════════════════════════

def render_text_png(text: str, width: int, height: int, output_png: Path) -> None:
    """
    Renders white text with a black drop-shadow on a TRANSPARENT background.
    This PNG is then overlaid on the video via FFmpeg.
    """
    from PIL import Image, ImageDraw, ImageFont

    img  = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # fully transparent
    draw = ImageDraw.Draw(img)

    # ── Font candidates ────────────────────────────────────────────────────────
    font = None
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            print(f"[Font] Using: {p}")
            font = ImageFont.truetype(p, FONT_SIZE)
            break

    if font is None:
        import urllib.request
        fallback = Path("/tmp/meme_font.ttf")
        if not fallback.exists():
            print("[Font] Downloading Roboto Bold fallback…")
            urllib.request.urlretrieve(
                "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Bold.ttf",
                str(fallback),
            )
        font = ImageFont.truetype(str(fallback), FONT_SIZE)

    # ── Wrap text ──────────────────────────────────────────────────────────────
    wrapped_lines = []
    for para in text.split("\n"):
        if para.strip() == "":
            wrapped_lines.append("")
        else:
            wrapped_lines.extend(textwrap.wrap(para, width=TEXT_WRAP) or [""])
    wrapped = "\n".join(wrapped_lines)

    # ── Measure total text block size to center it ─────────────────────────────
    bbox   = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=16)
    txt_w  = bbox[2] - bbox[0]
    txt_h  = bbox[3] - bbox[1]
    x      = (width  - txt_w) // 2   # horizontally centered
    y      = (height - txt_h) // 2   # vertically centered

    # ── Draw shadow then main text ─────────────────────────────────────────────
    off = SHADOW_OFFSET
    for dx, dy in [(-off, -off), (off, -off), (-off, off), (off, off),
                   (0, off),     (0, -off),   (off, 0),    (-off, 0)]:
        draw.multiline_text((x + dx, y + dy), wrapped, font=font,
                            fill=SHADOW_COLOR, spacing=16, align="center")

    draw.multiline_text((x, y), wrapped, font=font,
                        fill=TEXT_COLOR, spacing=16, align="center")

    img.save(str(output_png))
    print(f"[Text PNG] Saved → {output_png}")


# ══════════════════════════════════════════════════════════════════════════════
# 4. VIDEO ASSEMBLY  (pure FFmpeg)
# ══════════════════════════════════════════════════════════════════════════════

def pick_random_video() -> Path:
    exts  = {".mp4", ".mov", ".webm", ".avi"}
    files = [f for f in VIDEOS_DIR.iterdir() if f.suffix.lower() in exts]
    if not files:
        raise FileNotFoundError(f"No video files found in {VIDEOS_DIR}")
    chosen = random.choice(files)
    print(f"[Video] Picked: {chosen}")
    return chosen


def get_video_info(video: Path) -> tuple[float, int, int]:
    """Returns (duration_secs, width, height) via ffprobe."""
    # Duration
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True
    )
    duration = float(r.stdout.strip()) if r.stdout.strip() else 59.0

    # Dimensions
    r2 = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(video)],
        capture_output=True, text=True
    )
    try:
        w, h = map(int, r2.stdout.strip().split(","))
    except Exception:
        w, h = 1080, 1920   # safe FB Reel default

    return duration, w, h


def has_audio(video: Path) -> bool:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=index",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True
    )
    return bool(r.stdout.strip())


def build_video(overlay_text: str, output_path: Path) -> None:
    """
    Overlays bold centered text directly on the user-provided video.
    No white bar. No music mixing. Text floats on top of the clip.
    """
    video_file          = pick_random_video()
    duration, vid_w, vid_h = get_video_info(video_file)
    video_has_audio     = has_audio(video_file)

    print(f"[Video] {vid_w}x{vid_h} | {duration:.1f}s | audio={video_has_audio}")

    # ── Render text as transparent PNG matching video dimensions ──────────────
    text_png = OUTPUT_DIR / "text_overlay.png"
    render_text_png(overlay_text, vid_w, vid_h, text_png)

    # ── FFmpeg: overlay transparent PNG on video ───────────────────────────────
    # [0:v] = source video
    # [1:v] = transparent text PNG
    # Scale text PNG to match video size, then overlay at (0,0)

    filter_complex = (
        "[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
        "pad={w}:{h}:(ow-iw)/2:(oh-ih)/2[vid];"
        "[1:v]scale={w}:{h}[txt];"
        "[vid][txt]overlay=0:0[vout]"
    ).format(w=vid_w, h=vid_h)

    # Audio: pass through if exists, else silent
    audio_args = ["-map", "[vout]"]
    if video_has_audio:
        filter_complex += ";[0:a]acopy[aout]"
        audio_args += ["-map", "[aout]", "-c:a", "aac", "-b:a", "128k"]
    else:
        audio_args += ["-an"]

    cmd = [
        "ffmpeg", "-y",
        "-i",  str(video_file),   # input 0 — your video
        "-i",  str(text_png),     # input 1 — text overlay PNG
        "-filter_complex", filter_complex,
        *audio_args,
        "-t",       str(duration),
        "-c:v",     "libx264",
        "-preset",  "fast",
        "-crf",     "23",
        "-movflags", "+faststart",
        str(output_path),
    ]

    print("[FFmpeg] Rendering…")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[FFmpeg STDERR]", result.stderr[-3000:])
        raise RuntimeError("FFmpeg failed — see stderr above")

    size_kb = output_path.stat().st_size // 1024
    print(f"[FFmpeg] Done → {output_path}  ({size_kb} KB)")


# ══════════════════════════════════════════════════════════════════════════════
# 5. FACEBOOK REELS UPLOAD
# ══════════════════════════════════════════════════════════════════════════════

def post_to_facebook_reel(video_path: Path, caption: str) -> str:
    """Three-step Graph API upload: start → upload bytes → finish/publish."""
    file_size = video_path.stat().st_size
    base_url  = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/video_reels"

    # Step 1: Start
    print("[FB] Step 1 — Starting upload session…")
    r1 = requests.post(base_url, data={
        "upload_phase":  "start",
        "access_token":  FB_ACCESS_TOKEN,
    })
    print(f"[FB] Start ({r1.status_code}): {r1.text}")
    r1.raise_for_status()
    resp1 = r1.json()

    if "video_id" not in resp1:
        raise RuntimeError(f"FB start phase missing video_id. Response: {resp1}")

    video_id   = resp1["video_id"]
    upload_url = resp1.get(
        "upload_url",
        f"https://rupload.facebook.com/video-upload/v25.0/{video_id}"
    )
    print(f"[FB] video_id={video_id}")

    # Step 2: Upload bytes
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
    print(f"[FB] Upload ({r2.status_code}): {r2.text}")
    r2.raise_for_status()

    # Step 3: Publish
    print("[FB] Step 3 — Publishing reel…")
    r3 = requests.post(base_url, data={
        "upload_phase":  "finish",
        "video_id":      video_id,
        "access_token":  FB_ACCESS_TOKEN,
        "description":   caption,
        "video_state":   "PUBLISHED",
    })
    print(f"[FB] Publish ({r3.status_code}): {r3.text}")
    r3.raise_for_status()
    return video_id


# ══════════════════════════════════════════════════════════════════════════════
# 6. MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  Meme Reel Maker — Relationship Edition 💕😂")
    print("=" * 60)

    print("\n[Step 1] Generating joke with Groq…")
    overlay_text, caption = generate_joke()
    print(f"[Joke]\n{overlay_text}\n")
    print(f"[Caption]\n{caption}\n")

    print("[Step 2] Building video with FFmpeg…")
    build_video(overlay_text, OUTPUT_VIDEO)

    print("[Step 3] Posting to Facebook Reels…")
    post_id = post_to_facebook_reel(OUTPUT_VIDEO, caption)
    print(f"\n✅ Published! Video ID: {post_id}")


if __name__ == "__main__":
    main()
