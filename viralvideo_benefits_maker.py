#!/usr/bin/env python3
"""Benefit Reel Maker — renders a heading, then numbered benefits, and posts to Facebook Reels."""
import json
import os
import subprocess
import sys
from pathlib import Path


def _ensure_packages(*packages):
    import importlib.util
    missing = [p for p in packages if not importlib.util.find_spec(p)]
    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *missing])

_ensure_packages("PIL", "requests")
import requests


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment setting: {name}")
    return value


FB_ACCESS_TOKEN = require_env("FB_ACCESS_TOKEN")
FB_PAGE_ID = require_env("FB_PAGE_ID")
VIDEOS_DIR = Path("assets/prettyaivideos")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_VIDEO = OUTPUT_DIR / "reel.mp4"
PROGRESS_FILE = Path("benefits_progress.json")
TARGET_W, TARGET_H = 1080, 1920
SLIDE_SECONDS = 3.0  # Heading and each benefit stay visible for this many seconds.
# 0 = invisible; 255 = solid yellow. 150 shows the video through the box.
YELLOW_BOX_ALPHA = 150

# Add new topics ONLY at the bottom. Each topic is: heading first, then benefits.
POSTS = [
    {
        "heading": "Benepisyo sa pagtulog nang walang pantyyy",
        "benefits": [
            "Nakakatulong iwasan ang Fungal at bacterial growth",
            "Nakakabawas ng Skin irritation at Chafing",
        ],
        "caption": (
            "Benepisyo sa pagtulog nang walang pantyyy\n\n"
            "#healthtips #tips #reels"
        ),
    },
    # {
    #     "heading": "Ilagay ang heading dito",
    #     "benefits": ["Unang benepisyo", "Pangalawang benepisyo"],
    #     "caption": "Heading at caption dito\n\n#healthtips #tips #reels",
    # },
]


def load_progress() -> dict:
    try:
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_progress(data: dict) -> None:
    PROGRESS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def next_post() -> dict:
    data = load_progress()
    index = (int(data.get("last_index", -1)) + 1) % len(POSTS)
    post = POSTS[index]
    data.update(last_index=index, last_heading=post["heading"])
    save_progress(data)
    return post


def pick_next_video() -> Path:
    files = sorted(p for p in VIDEOS_DIR.iterdir() if p.suffix.lower() in {".mp4", ".mov", ".webm", ".avi"})
    if not files:
        raise FileNotFoundError(f"No video found in {VIDEOS_DIR}")
    data = load_progress()
    names = [p.name for p in files]
    previous = data.get("last_video_name", "")
    index = (names.index(previous) + 1) % len(files) if previous in names else 0
    data["last_video_name"] = files[index].name
    save_progress(data)
    return files[index]


def video_duration(path: Path) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def has_audio(path: Path) -> bool:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=index",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], capture_output=True, text=True)
    return bool(result.stdout.strip())


def render_slide(text: str, output_png: Path, is_heading: bool = False) -> None:
    """Make one yellow rounded-text slide, placed high enough for Reel controls."""
    if is_heading:
        text = text.upper()
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    font_path = next((p for p in font_paths if Path(p).exists()), font_paths[0])

    # Make the all-caps heading larger and emphatic; benefits remain easy to read.
    max_width = 900
    starting_size = 88 if is_heading else 72
    for size in range(starting_size, 34, -2):
        font = ImageFont.truetype(font_path, size)
        words, lines, line = text.split(), [], ""
        for word in words:
            trial = f"{line} {word}".strip()
            if draw.textlength(trial, font=font) <= max_width:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        if len(lines) <= 4:
            break

    line_gap, box_pad_x, box_pad_y, box_gap = 10, 34, 18, 4
    bounds = [draw.textbbox((0, 0), line, font=font) for line in lines]
    heights = [b[3] - b[1] + box_pad_y * 2 for b in bounds]
    total_height = sum(heights) + box_gap * (len(lines) - 1)
    y = max(210, (TARGET_H - total_height) // 5)

    for line, bound, box_h in zip(lines, bounds, heights):
        text_w = bound[2] - bound[0]
        x1 = (TARGET_W - text_w) // 2 - box_pad_x
        x2 = (TARGET_W + text_w) // 2 + box_pad_x
        draw.rounded_rectangle((x1, y, x2, y + box_h), radius=24, fill=(255, 244, 165, YELLOW_BOX_ALPHA))
        text_y = y + box_pad_y - bound[1]
        draw.text(((TARGET_W - text_w) // 2, text_y), line, font=font, fill=(0, 0, 0, 255))
        y += box_h + box_gap
    image.save(output_png)


def build_video(post: dict, output_path: Path) -> None:
    video = pick_next_video()
    duration = video_duration(video)
    slides = [post["heading"]] + [f"{i}. {benefit}" for i, benefit in enumerate(post["benefits"], 1)]
    # Fit all slides into short clips; leave the video clean after the final slide on longer clips.
    seconds_each = min(SLIDE_SECONDS, duration / len(slides))
    pngs = []
    for i, slide in enumerate(slides):
        png = OUTPUT_DIR / f"text_overlay_{i}.png"
        render_slide(slide, png, is_heading=(i == 0))
        pngs.append(png)

    filters = [
        f"[0:v]scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
        f"crop={TARGET_W}:{TARGET_H}[v0]"
    ]
    previous = "v0"
    for i in range(len(pngs)):
        start, end = i * seconds_each, (i + 1) * seconds_each
        filters.append(f"[{i + 1}:v]scale={TARGET_W}:{TARGET_H}[t{i}]")
        filters.append(f"[{previous}][t{i}]overlay=0:0:enable='between(t,{start:.3f},{end:.3f})'[v{i + 1}]")
        previous = f"v{i + 1}"

    command = ["ffmpeg", "-y", "-i", str(video)]
    for png in pngs:
        command += ["-loop", "1", "-i", str(png)]
    command += ["-filter_complex", ";".join(filters), "-map", f"[{previous}]"]
    if has_audio(video):
        command += ["-map", "0:a?", "-c:a", "aac", "-b:a", "128k"]
    else:
        command += ["-an"]
    command += ["-t", f"{duration:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-movflags", "+faststart", str(output_path)]
    subprocess.run(command, check=True)


def post_to_facebook_reel(video_path: Path, caption: str) -> str:
    base_url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/video_reels"
    started = requests.post(base_url, data={"upload_phase": "start", "access_token": FB_ACCESS_TOKEN})
    started.raise_for_status()
    data = started.json()
    video_id = data["video_id"]
    upload_url = data.get("upload_url", f"https://rupload.facebook.com/video-upload/v25.0/{video_id}")
    with video_path.open("rb") as file:
        uploaded = requests.post(upload_url, headers={
            "Authorization": f"OAuth {FB_ACCESS_TOKEN}", "offset": "0",
            "file_size": str(video_path.stat().st_size), "Content-Type": "application/octet-stream",
        }, data=file)
    uploaded.raise_for_status()
    finished = requests.post(base_url, data={
        "upload_phase": "finish", "video_id": video_id, "access_token": FB_ACCESS_TOKEN,
        "description": caption, "video_state": "PUBLISHED",
    })
    finished.raise_for_status()
    return video_id


def main():
    post = next_post()
    print(f"Making: {post['heading']}")
    build_video(post, OUTPUT_VIDEO)
    print(f"Published Facebook reel: {post_to_facebook_reel(OUTPUT_VIDEO, post['caption'])}")


if __name__ == "__main__":
    main()
