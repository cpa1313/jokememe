#!/usr/bin/env python3
"""Pinoy Mystery Reel Maker — creates five original narrated mystery reels for GitHub.

Place vertical clips in assets/videos/. The Reel contains narration only.
"""
import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path


def ensure_packages(*packages: str) -> None:
    import importlib.util
    missing = [package for package in packages if importlib.util.find_spec(package) is None]
    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *missing])


ensure_packages("PIL")
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
VIDEO_DIR = ROOT / "assets" / "videos"
PROGRESS_FILE = ROOT / "mystery_progress.json"
TARGET_W, TARGET_H = 1080, 1920
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}
VOICE = os.environ.get("REEL_VOICE", "fil-PH-AngeloNeural")

# Each story is rendered as: hook → setup → punchline. Add future storys at the end.
# Storys imported exactly from viralvideo_maker.py. Add future entries at the end.
STORIES = [
    {
        "header": "Ang Huling Pasahero",
        "body": "Sa huling biyahe ni Ben, may babaeng tahimik na sumakay sa taxi. Pagbaba nito, lumang resibo ang iniabot na may petsang sampung taon na ang nakalipas. Sa likod, nakasulat: Salamat sa pagsundo mo sa akin, Tatay.",
        "caption": "Pinoy Mystery #001 — Ang Huling Pasahero\n\nFictional story • For entertainment only.\nIkaw, itutuloy mo ba ang biyahe?\n\n#PinoyMystery #TagalogHorror #FictionalStory #Reels",
    },
    {
        "header": "Ang Kumatok sa Unit 12",
        "body": "Tuwing 3:13 ng madaling araw, may tatlong katok sa pinto ni Mara. Sinabi ng guard na huwag niya itong buksan. Ang Unit 12 raw ay bakante mula nang masunog ang gusali. Ngunit isang gabi, narinig niya ang boses ng kapatid niyang matagal nang nawawala.",
        "caption": "Pinoy Mystery #002 — Ang Kumatok sa Unit 12\n\nFictional story • For entertainment only.\nBubuksan mo ba ang pinto?\n\n#PinoyMystery #TagalogHorror #FictionalStory #Reels",
    },
    {
        "header": "Ang Voice Message Bukas",
        "body": "Nakatanggap si Paolo ng voice message mula sa sarili niyang numero. Boses niya iyon, nanginginig: Huwag kang sasakay sa bus mamayang alas-siyete. Akala niya biro lang. Pagsapit ng alas-siyete, nakita niyang nakaparada ang bus sa tapat ng bahay nila, walang driver at walang laman.",
        "caption": "Pinoy Mystery #003 — Ang Voice Message Bukas\n\nFictional story • For entertainment only.\nSasagot ka ba sa sarili mong tawag?\n\n#PinoyMystery #TagalogHorror #FictionalStory #Reels",
    },
    {
        "header": "Ang Aklat na Walang Pahina",
        "body": "May nakita si Liza sa lumang library na aklat na walang laman ang bawat pahina. Nang isulat niya ang pangalan niya sa unang pahina, unti-unting lumitaw ang buong araw niya. Sa huling pahina, may isang linyang hindi pa nangyayari: Huwag mong lilingunin ang anino sa likod mo.",
        "caption": "Pinoy Mystery #004 — Ang Aklat na Walang Pahina\n\nFictional story • For entertainment only.\nLilingon ka ba?\n\n#PinoyMystery #TagalogHorror #FictionalStory #Reels",
    },
    {
        "header": "Ang Larawang May Isang Sobra",
        "body": "Pagkatapos ng reunion, binilang ni Nico ang mga tao sa larawan: sampu lang silang magkakaibigan. Ngunit may labing-isang mukha sa likod nila, nakangiti sa dilim. Nang i-zoom niya ang larawan, nakita niyang siya mismo ang taong nawawala sa grupo.",
        "caption": "Pinoy Mystery #005 — Ang Larawang May Isang Sobra\n\nFictional story • For entertainment only.\nSino ang nasa larawan?\n\n#PinoyMystery #TagalogHorror #FictionalStory #Reels",
    },
]



def natural_key(path: Path) -> list:
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", path.name)]


def duration(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def next_story() -> tuple[int, dict[str, str]]:
    try:
        state = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}
    if not STORIES:
        raise RuntimeError("STORIES is empty; add at least one approved story before creating a Reel.")
    index = int(state.get("next_story_index", 0)) % len(STORIES)
    return index + 1, STORIES[index]


def save_progress(story_number: int) -> None:
    """Record the last rendered story number."""
    PROGRESS_FILE.write_text(json.dumps({
        "next_story_index": story_number % len(STORIES),
        "last_story_number": story_number,
    }, indent=2), encoding="utf-8")


def wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if not current or draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    return lines + ([current] if current else [])


def font(size: int):
    for candidate in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def render_slide(story_number: int, stage: int, text: str, output: Path) -> None:
    image = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    accent = (255, 205, 46, 255)
    draw.rounded_rectangle((55, 190, 1025, 1610), radius=42, fill=(8, 13, 32, 205), outline=accent, width=5)
    draw.text((540, 300), "PINOY MYSTERY", anchor="mm", font=font(52), fill=accent)
    labels = ("THE MYSTERY", "THE TWIST")
    draw.text((540, 410), labels[stage], anchor="mm", font=font(33), fill=(180, 205, 255, 255))
    text_font = font(74 if len(text) < 58 else 60)
    lines = wrap(draw, text, text_font, 830)
    y = 820 - len(lines) * 42
    for line in lines:
        draw.text((540, y), line, anchor="mm", font=text_font, fill=(255, 255, 255, 255))
        y += text_font.size + 22
    draw.text((540, 1500), f"FICTIONAL STORY #{story_number}  •  FOLLOW FOR MORE", anchor="mm", font=font(27), fill=(198, 208, 230, 255))
    image.save(output)


def narration(text: str, output: Path) -> float:
    raw = output.with_suffix(".mp3")
    for attempt in range(4):
        result = subprocess.run([sys.executable, "-m", "edge_tts", "--voice", VOICE, "--text", text, "--write-media", str(raw)], capture_output=True, text=True)
        if result.returncode == 0 and raw.exists() and raw.stat().st_size:
            break
        time.sleep(2 ** attempt)
    else:
        raise RuntimeError("Voice generation failed. Please try again.")
    seconds = duration(raw) + 0.55
    subprocess.run(["ffmpeg", "-y", "-i", str(raw), "-af", "apad=pad_dur=0.55", "-t", f"{seconds:.3f}", "-c:a", "pcm_s16le", str(output)], check=True)
    raw.unlink(missing_ok=True)
    return seconds


def background(sequence: int) -> Path:
    clips = sorted((p for p in VIDEO_DIR.glob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS), key=natural_key)
    if not clips:
        raise FileNotFoundError("No background clips found. Add a vertical video to assets/videos/.")
    return clips[(sequence - 1) % len(clips)]


def output_video_path(story_number: int, story: dict[str, str]) -> Path:
    # A readable, filesystem-safe filename based on the first line of the story.
    title = re.sub(r"[^a-z0-9]+", "-", story["header"].lower()).strip("-")
    title = title[:70].rstrip("-") or "pinoy-mystery"
    return OUTPUT_DIR / f"pinoy-mystery-{story_number:03d}-{title}.mp4"


def build_reel(story_number: int, story: dict[str, str], output_video: Path) -> None:
    pngs, wavs, times = [], [], []
    for stage, line in enumerate((story["header"], story["body"])):
        png, wav = OUTPUT_DIR / f"slide_{stage}.png", OUTPUT_DIR / f"voice_{stage}.wav"
        render_slide(story_number, stage, line, png)
        pngs.append(png); wavs.append(wav); times.append(narration(line, wav))
    manifest = OUTPUT_DIR / "audio.txt"
    manifest.write_text("".join(f"file '{p.resolve()}'\n" for p in wavs), encoding="utf-8")
    audio = OUTPUT_DIR / "narration.wav"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest), "-c:a", "pcm_s16le", str(audio)], check=True)
    total = sum(times)
    filters = [f"[0:v]scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,crop={TARGET_W}:{TARGET_H},eq=brightness=-0.16:saturation=0.8[base]"]
    previous, start = "base", 0.0
    for i, slide_time in enumerate(times):
        end = start + slide_time
        filters.append(f"[{i + 1}:v]scale={TARGET_W}:{TARGET_H}[s{i}];[{previous}][s{i}]overlay=enable='between(t\\,{start:.3f}\\,{end:.3f})'[v{i}]")
        previous, start = f"v{i}", end
    command = ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(background(story_number))]
    for png in pngs:
        command += ["-loop", "1", "-i", str(png)]
    command += ["-i", str(audio), "-filter_complex", ";".join(filters), "-map", f"[{previous}]", "-map", f"{len(pngs)+1}:a", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(output_video)]
    subprocess.run(command, check=True)



def main() -> None:
    # Produce all five original stories in one run. Existing files with the same
    # titles are replaced, so rerunning the workflow is safe.
    for number, story in enumerate(STORIES, start=1):
        print(f"Making Pinoy Mystery {number}: {story['header']}")
        video_path = output_video_path(number, story)
        build_reel(number, story, video_path)
        print(f"Rendered video saved to: {video_path}")


if __name__ == "__main__":
    main()
