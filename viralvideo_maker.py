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
            "You write viral meme captions for a relationship humor page on Facebook Reels.\n\n"
            "Write a SHORT reaction meme about relationships, dating, or single life.\n"
            "The joke must be instantly relatable — someone should read it and say 'omg that's me'.\n\n"
            "EXACT FORMAT — output ONLY these 3 lines, nothing else, no intro, no markdown:\n"
            "SPEAKER: [one person, e.g. Her, Him, My boyfriend, My girlfriend, My situationship, My ex]\n"
            "SETUP: [what they say or do — short, max 10 words, must be specific and funny]\n"
            "REACTOR: [who reacts — e.g. Me, My anxiety, My wallet, My pillow, My single friends]\n\n"
            "GOOD EXAMPLES:\n"
            "SPEAKER: Her\nSETUP: We need to talk\nREACTOR: My heart rate:\n\n"
            "SPEAKER: Him\nSETUP: I'm not mad, I'm just disappointed\nREACTOR: Me knowing it's worse:\n\n"
            "SPEAKER: My girlfriend\nSETUP: I'm fine\nREACTOR: The next 3 hours:\n\n"
            "SPEAKER: My ex\nSETUP: Texts at 2am: you up?\nREACTOR: My self respect:\n\n"
            "Now write a NEW one. Must be funny and make sense. ONLY output the 3 lines."
        ),
    },

    # ── Format B: Relatable observation ───────────────────────────────────────
    {
        "style": "observation",
        "prompt": (
            "You write viral meme captions for a relationship humor page on Facebook Reels.\n\n"
            "Write ONE short funny observation about relationships, dating, or being single.\n"
            "It must describe a very specific, relatable situation — not vague or generic.\n\n"
            "GOOD EXAMPLES (copy this style exactly):\n"
            "- In a relationship, 'what's wrong?' becomes 'nothing' for 10 mins then 3 hours of explaining.\n"
            "- Nobody talks about how loud your apartment is after a breakup.\n"
            "- Dating in 2024: 3 months of talking, 0 labels, full situationship.\n"
            "- Couples be having the same argument with different toppings every week.\n"
            "- Being in love is great until you have to decide where to eat.\n\n"
            "BAD EXAMPLES (do NOT write like this — too vague):\n"
            "- Relationships are complicated.\n"
            "- Being single has its perks.\n\n"
            "Write ONE new funny observation. Max 30 words. Output ONLY the text, no quotes, no intro."
        ),
    },

    # ── Format C: Single life perk ────────────────────────────────────────────
    {
        "style": "singleperk",
        "prompt": (
            "You write viral meme captions for a relationship humor page on Facebook Reels.\n\n"
            "Write ONE funny perk of being single — specific, relatable, and a little petty.\n\n"
            "GOOD EXAMPLES (copy this style exactly):\n"
            "- Being single means the fries you ordered are ALL yours. Every single one.\n"
            "- Single perk: your phone never blows up at 11pm asking where you are.\n"
            "- No relationship means no one is eating the last slice you were saving since morning.\n"
            "- Being single is waking up on a Saturday with zero obligations and zero guilt.\n"
            "- Single life means the blanket stays on your side. Forever.\n\n"
            "BAD EXAMPLES (too generic — do NOT write like this):\n"
            "- Being single means freedom.\n"
            "- You can do what you want when single.\n\n"
            "Write ONE new single perk. Max 28 words. Output ONLY the text, no quotes, no intro."
        ),
    },

    # ── Format D: Relationship truth ──────────────────────────────────────────
    {
        "style": "truth",
        "prompt": (
            "You write viral meme captions for a relationship humor page on Facebook Reels.\n\n"
            "Write ONE funny but painfully true fact about being in a relationship.\n"
            "It must be specific — describe an exact moment or pattern couples experience.\n\n"
            "GOOD EXAMPLES (copy this style exactly):\n"
            "- Relationship level unlocked: you stop saying 'I love you' and start saying 'did you eat?'\n"
            "- In a relationship you don't argue about big things. You argue about how someone chews.\n"
            "- Real intimacy is telling your partner the WiFi password on the first night they stay over.\n"
            "- The moment you're officially a couple is when they start sending you memes at 7am.\n"
            "- You know it's serious when you start arguing about how to load the dishwasher.\n\n"
            "BAD EXAMPLES (too vague — do NOT write like this):\n"
            "- Relationships need communication.\n"
            "- Being with someone takes work.\n\n"
            "Write ONE new relationship truth. Max 30 words. Output ONLY the text, no quotes, no intro."
        ),
    },
]


# ── Text styling ───────────────────────────────────────────────────────────────
FONT_SIZE_HEADER    = 80     # BIG BOLD ALL CAPS header
FONT_SIZE_BODY      = 52     # smaller italic body
STROKE_WIDTH_HEADER = 9      # thick stroke for header
STROKE_WIDTH_BODY   = 6      # slightly thinner for body


# ══════════════════════════════════════════════════════════════════════════════
# 2. JOKE GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_joke() -> tuple[str, str, str]:
    """
    Returns (header_text, body_text, fb_caption).
    header_text -> BIG BOLD ALL CAPS (top)
    body_text   -> smaller italic-style (bottom)
    """
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

        header  = f"{speaker.upper()} SAID:"
        body    = f"{setup}\n\n{reactor}:"
        caption = f"{speaker}: {setup}\n{reactor}: 💀😂\n\n#relationshiphumor #datinglife #singlelife #memes #funny"

    # ── Observation / singleperk / truth — split into header + body ──────────
    else:
        import re as _re
        parts = _re.split(r'(?<=[.,:!?])\s+', raw, maxsplit=1)
        if len(parts) == 2 and len(parts[0]) >= 8:
            header = parts[0].upper()
            body   = parts[1]
        else:
            words  = raw.split()
            mid    = max(2, len(words) // 2)
            header = " ".join(words[:mid]).upper()
            body   = " ".join(words[mid:])

        tags = {
            "observation": "#relationshipmemes #datinghumor #couplegoals #funny",
            "singleperk":  "#singlelife #singleandthriving #singlehumor #memes",
            "truth":       "#couplehumor #relationshiptruth #married #relatable",
        }.get(fmt["style"], "#memes #funny")
        caption = f"{raw}\n\n{tags}"

    print(f"[Text] Header: {header!r}")
    print(f"[Text] Body:   {body!r}")
    return header, body, caption


# ══════════════════════════════════════════════════════════════════════════════
# 3. RENDER TEXT PNG  (Pillow — reliable cross-platform)
# ══════════════════════════════════════════════════════════════════════════════

def render_text_png(header: str, body: str, width: int, height: int, output_png: Path) -> None:
    """
    Two-layer text style (like the Brock Lesnar meme):
      - Header: BIG, BOLD, ALL CAPS, white with thick black stroke
      - Body:   Medium, italic, white with stroke, centered below header
    Rendered on a fully transparent PNG overlaid on the video.
    """
    import math
    from PIL import Image, ImageDraw, ImageFont

    img  = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bold_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    italic_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-BI.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf",
    ]

    def load_font(candidates, size):
        for p in candidates:
            if os.path.exists(p):
                print(f'[Font] {p}')
                return ImageFont.truetype(p, size)
        import urllib.request
        fallback = Path('/tmp/meme_font.ttf')
        if not fallback.exists():
            print('[Font] Downloading Roboto Bold fallback...')
            urllib.request.urlretrieve(
                'https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Bold.ttf',
                str(fallback),
            )
        return ImageFont.truetype(str(fallback), size)

    font_header = load_font(bold_candidates,   FONT_SIZE_HEADER)
    font_body   = load_font(italic_candidates, FONT_SIZE_BODY)

    WHITE = (255, 255, 255, 255)
    BLACK = (0,   0,   0,   255)

    def wrap_px(text, font, max_width):
        words = text.split()
        lines, current = [], ''
        for word in words:
            test = (current + ' ' + word).strip()
            w = draw.textlength(test, font=font)
            if w <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return '\n'.join(lines)

    def draw_stroked(pos, text, font, fill, stroke_col, stroke_w, spacing=14):
        x, y = pos
        for angle in range(0, 360, 12):
            rad = math.radians(angle)
            ox  = int(math.cos(rad) * stroke_w)
            oy  = int(math.sin(rad) * stroke_w)
            draw.multiline_text((x + ox, y + oy), text, font=font,
                                fill=stroke_col, spacing=spacing, align='center')
        draw.multiline_text((x, y), text, font=font,
                            fill=fill, spacing=spacing, align='center')

    pad   = int(width * 0.08)
    max_w = width - pad * 2

    wrapped_header = wrap_px(header.upper(), font_header, max_w)
    wrapped_body   = wrap_px(body,           font_body,   max_w)

    hb = draw.multiline_textbbox((0, 0), wrapped_header, font=font_header, spacing=10)
    bb = draw.multiline_textbbox((0, 0), wrapped_body,   font=font_body,   spacing=14)
    h_w, h_h = hb[2] - hb[0], hb[3] - hb[1]
    b_w, b_h = bb[2] - bb[0], bb[3] - bb[1]
    gap      = int(FONT_SIZE_HEADER * 0.5)
    total_h  = h_h + gap + b_h
    start_y  = (height - total_h) // 2 - int(height * 0.03)
    hx = (width - h_w) // 2
    bx = (width - b_w) // 2
    by = start_y + h_h + gap

    draw_stroked((hx, start_y), wrapped_header, font_header,
                 WHITE, BLACK, STROKE_WIDTH_HEADER, spacing=10)
    draw_stroked((bx, by), wrapped_body, font_body,
                 WHITE, BLACK, STROKE_WIDTH_BODY, spacing=14)

    img.save(str(output_png))
    print(f'[Text PNG] Saved -> {output_png}')

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


def build_video(header: str, body: str, output_path: Path) -> None:
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
    render_text_png(header, body, vid_w, vid_h, text_png)

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
    header, body, caption = generate_joke()
    print(f"[Header]\n{header}\n[Body]\n{body}\n")
    print(f"[Caption]\n{caption}\n")

    print("[Step 2] Building video with FFmpeg…")
    build_video(header, body, OUTPUT_VIDEO)

    print("[Step 3] Posting to Facebook Reels…")
    post_id = post_to_facebook_reel(OUTPUT_VIDEO, caption)
    print(f"\n✅ Published! Video ID: {post_id}")


if __name__ == "__main__":
    main()
