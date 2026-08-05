#!/usr/bin/env python3
"""Pinoy Mystery Reel Maker — creates one original, complete mystery reel per run.

Place each story's vertical clips in assets/horror/001/, assets/horror/002/, etc. The Reel contains narration only.
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
VIDEO_DIR = ROOT / "assets" / "horror"
PROGRESS_FILE = ROOT / "mystery_progress.json"
TARGET_W, TARGET_H = 1080, 1920
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}
VOICE = os.environ.get("REEL_VOICE", "fil-PH-AngeloNeural")
END_FREEZE_SECONDS = 1.5
END_FADE_SECONDS = 1.0

# Each story has a complete ending. Add future original stories at the end.
STORIES = [
    {
        "number": 1,
        "header": "Ang Pinto na Hindi Dapat Buksan",
        "body": "Noong nagsimula si Marco bilang night guard sa isang lumang paaralan, iisa lang ang bilin sa kanya: Huwag mong bubuksan ang pinto sa dulo ng ikatlong palapag. Tuwing alas-dose ng gabi, may maririnig kang tatlong katok. Kahit anong mangyari, huwag mong papansinin. Sa ikatlong gabi, narinig niya ang tatlong katok. Maya-maya, may mahinang boses na nagsabi, 'Tulungan mo ako.' Hindi siya gumalaw. Ilang minuto ang lumipas at dumating ang principal na halatang kinakabahan. Sinabi nito, 'Salamat... kung binuksan mo ang pinto, wala ka na sana rito.' Kinaumagahan, ipinakita sa kanya ang lumang litrato ng paaralan. Nakita niya ang parehong pinto... pero limampung taon na pala itong sementado at wala nang daan papunta roon.",
        "caption": "🚪 Pinoy Mystery #001 — Ang Pinto na Hindi Dapat Buksan\n\n⚠️ Fictional story • For entertainment only.\nIkaw ba? Bubuksan mo ba ang pinto o susundin mo ang bilin?\n\n#PinoyMystery #TagalogMystery #FictionalStory #Reels #ShortStory",
    },
    {
        "number": 2,
        "header": "Ang Huling Tawag",
        "body": "Habang naglalakad pauwi si Carlo, may narinig siyang cellphone na paulit-ulit na tumutunog sa isang bakanteng waiting shed. Nang sagutin niya ito, isang mahinang boses ang nagsabi, 'Huwag kang lilingon.' Hindi siya lumingon. Ilang segundo lang ang lumipas, rumagasa ang isang truck at winasak ang waiting shed. Kinabukasan, nabalitaan niyang may taong namatay sa parehong lugar... eksaktong oras ng tawag na sinagot niya.",
        "caption": "📱 Pinoy Mystery #002 — Ang Huling Tawag\n\n⚠️ Fictional story • For entertainment only.\n👻 Presented by AngKulitPranks\n\nKung ikaw si Carlo, susundin mo ba ang babala?\n\n#AngKulitPranks #PinoyMystery #TagalogMystery #FictionalStory #Reels",
    },
    {
        "number": 3,
        "header": "Ang CCTV Replay",
        "body": "Unang gabi ni Ben bilang guwardiya sa isang lumang opisina. Habang nanonood ng CCTV, may nakita siyang lalaking nakasuot ng security uniform na mabilis na tumatakbo papunta sa emergency exit. Agad niya itong hinabol, pero walang tao sa buong gusali. Pagbalik niya sa monitor, nakita niyang ang lalaking tumatakbo ay siya mismo. Ilang segundo lang ang lumipas, isang malakas na pagsabog ang yumanig sa kabilang palapag.",
        "caption": "📹 Pinoy Mystery #003 — Ang CCTV Replay\n\n👻 Presented by AngKulitPranks\n\n⚠️ Fictional story • For entertainment only.\n\n👇 Ano kaya ang tinatakbuhan ni Ben sa CCTV?\n\n#AngKulitPranks\n#PinoyMystery\n#TagalogMystery\n#FictionalStory\n#Reels",
    },
    {
        "number": 4,
        "header": "Ang Babae sa Room 308",
        "body": "Nag-check in si Adrian sa isang lumang hotel para magpahinga matapos ang mahabang biyahe. Habang naghihintay ng pagkain, may kumatok sa pinto. Pagbukas niya, isang tahimik na babae ang nakatayo sa hallway. Nakangiti lang ito at sinabi, 'Huwag mong bubuksan ang pinto kapag may kumatok ulit.' Bago pa siya makapagtanong, umalis na ang babae. Makalipas ang ilang minuto, may tatlong malalakas na katok. Hindi niya binuksan ang pinto. Kinaumagahan, sinabi ng receptionist na walang ibang guest sa palapag na iyon buong gabi.",
        "caption": "🏨 Pinoy Mystery #004 — Ang Babae sa Room 308\n\n👻 Presented by AngKulitPranks\n\n⚠️ Fictional story • For entertainment only.\n\n👇 Bubuksan mo ba ang pinto kung ikaw si Adrian?\n\n#AngKulitPranks #PinoyMystery #TagalogMystery #FictionalStory #Reels",
    },
    {
        "number": 5,
        "header": "Ang Maling Send",
        "body": "Habang nasa opisina, gusto lang sana ni Mia i-message ang boyfriend niyang si Ethan ng, 'Love you, babe. Miss na kita.' Pero sa sobrang pagmamadali, kay Boss Reyes niya ito naipadala. Nanlamig si Mia nang makita ang pangalan sa chat. Buong umaga siyang kabadong naghihintay ng magiging reaksyon ni Boss Reyes. Bago matapos ang araw, dumaan si Boss Reyes sa kanyang desk, ngumiti, at sinabing, 'Mukhang hindi para sa akin 'yan. Paki-send na lang muna ang report bago matapos ang araw.' Napatawa ang buong opisina habang si Mia ay halos matunaw sa hiya.",
        "caption": "😂 Love Comedy #005 — Ang Maling Send\n\n💕 Presented by AngKulitPranks\n\n⚠️ Fictional story • For entertainment only.\n\n👇 Ano ang gagawin mo kung ikaw si Mia?\n\n#AngKulitPranks #LoveComedy #OfficeHumor #FictionalStory #Reels",
    },
    {
        "number": 6,
        "header": "My Ex is My New Coworker",
        "body": "Excited si Mia sa unang araw niya sa bagong opisina. Pagpasok niya sa meeting room, halos mabitawan niya ang hawak na kape nang makita niyang si Ethan ang isa sa mga empleyadong naghihintay. Dalawang taon na silang hiwalay at ni minsan ay hindi na nagkita. Nagkatitigan sila nang ilang segundo bago sabay umiwas ng tingin na parang walang nangyari. Maya-maya, pumasok si Boss Reyes na may dalang folder at ngumiti. 'Welcome sa team, Mia. Simula ngayong araw, ikaw at si Ethan ang magiging partners sa bagong project.' Napabuntong-hininga si Mia habang napakamot na lang si Ethan. Mukhang mas mahaba pa ang project kaysa sa moving on nila.",
        "caption": "😂 Love Comedy #006 — My Ex is My New Coworker\n\n💕 Presented by AngKulitPranks\n\n⚠️ Fictional story • For entertainment only.\n\n👇 Kakayanin mo bang makatrabaho ang ex mo araw-araw?\n\n#AngKulitPranks #LoveComedy #OfficeHumor #FictionalStory #Reels",
    },
    {
        "number": 7,
        "header": "Ang Badminton Queen",
        "body": "Nag-organisa si Boss Reyes ng company badminton tournament. Akala ng lahat, mahihirapan si Mia dahil tahimik lang siya sa opisina. Pero sa unang rally pa lang, tumalon siya at nagpakawala ng napakalakas na smash. Napa-wow ang buong court. Sunod-sunod ang puntos ni Mia hanggang siya ang manalo. Lumapit si Ethan at napangiti. 'Hindi mo sinabi na dating badminton champion ka pala.' Ngumiti si Mia. 'Hindi mo rin naman tinanong.'",
        "caption": "🏸 Love Comedy #007 — Ang Badminton Queen\n\n💕 Presented by AngKulitPranks\n\n⚠️ Fictional story • For entertainment only.\n\n👇 May talent ka bang ikinagulat ng mga kaibigan o katrabaho mo?\n\n#AngKulitPranks #LoveComedy #Badminton #OfficeHumor #FictionalStory",
    },
    {
        "number": 8,
        "header": "Ikaw Na Nga Tinulungan, Ikaw Pa Masama",
        "body": "Nakakapagod tumulong sa taong ang akala, obligasyon mo na silang tulungan. Sa umpisa, simpleng pabor lang. Hanggang sa halos trabaho na nila ang ginagawa mo. Pero noong minsan ka lang tumanggi dahil ikaw naman ang nahihirapan... ikaw pa ang naging masama. Ang sakit, no? Kahit ilang beses kang umintindi, isang beses ka lang hindi pumayag... doon ka pa nila hinusgahan. Doon mo mare-realize... hindi pala nila na-appreciate ang kabaitan mo. Nasanay lang silang lagi kang nagsasakripisyo.",
        "caption": "💔 Real Life Story #008 — Ikaw Na Nga Tinulungan, Ikaw Pa Masama\n\n💕 Presented by AngKulitPranks\n\n⚠️ Fictional story inspired by everyday office situations.\n\n👇 Naranasan mo na bang ikaw na ang tumulong, ikaw pa ang naging masama?\n\n#AngKulitPranks #RealLifeStory #OfficeLife #Relatable #FictionalStory #WorkDrama",
    },
]

def natural_key(path: Path) -> list:
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", path.name)]


def duration(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def has_audio(path: Path) -> bool:
    """Return True when the source video contains at least one audio stream."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return bool(result.stdout.strip())


def next_story() -> tuple[int, int, dict[str, str]]:
    try:
        state = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}
    if not STORIES:
        raise RuntimeError("STORIES is empty; add at least one approved story before creating a Reel.")
    index = int(state.get("next_story_index", 0)) % len(STORIES)
    story = STORIES[index]
    return index, int(story["number"]), story


def load_progress() -> dict:
    try:
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_progress(story_index: int, story_number: int, next_video_index: int) -> None:
    """Record the story position for the next run."""
    PROGRESS_FILE.write_text(json.dumps({
        "next_story_index": (story_index + 1) % len(STORIES),
        "last_story_number": story_number,
        "next_video_index": next_video_index,
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


def split_sentences(text: str) -> list[str]:
    """Split narration into short, natural one-to-two-line subtitle phrases."""
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
    subtitles = []
    max_chars = 74

    for sentence in sentences:
        # Prefer breaks at commas so each subtitle still sounds natural.
        phrases = [part.strip() for part in re.split(r"(?<=,)\s+", sentence) if part.strip()]
        current = ""
        for phrase in phrases:
            candidate = f"{current} {phrase}".strip()
            if current and len(candidate) > max_chars:
                subtitles.append(current)
                current = phrase
            else:
                current = candidate
        if current:
            # Split an unusually long phrase safely at word boundaries.
            words = current.split()
            chunk = ""
            for word in words:
                candidate = f"{chunk} {word}".strip()
                if chunk and len(candidate) > max_chars:
                    subtitles.append(chunk)
                    chunk = word
                else:
                    chunk = candidate
            if chunk:
                subtitles.append(chunk)

    return subtitles


def render_slide(story_title: str, label: str, text: str, output: Path) -> None:
    """Render the heading in yellow boxes and story text as clean subtitles."""
    image = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Keep the original first-frame design: each title line sits inside its own
    # rounded yellow box. The creator credit appears directly beneath the heading.
    is_opening = text == story_title
    if is_opening:
        heading_font = font(62)
        heading = text.upper()
        lines = wrap(draw, heading, heading_font, 850)
        while len(lines) > 2 and heading_font.size > 48:
            heading_font = font(heading_font.size - 2)
            lines = wrap(draw, heading, heading_font, 850)

        box_pad_x, box_pad_y = 22, 10
        line_gap = 12
        y = 170
        for line in lines:
            left, top, right, bottom = draw.textbbox((0, 0), line, font=heading_font)
            text_w, text_h = right - left, bottom - top
            box = (
                TARGET_W // 2 - text_w // 2 - box_pad_x,
                y - box_pad_y,
                TARGET_W // 2 + text_w // 2 + box_pad_x,
                y + text_h + box_pad_y,
            )
            draw.rounded_rectangle(box, radius=14, fill=(250, 216, 108, 245))
            draw.text(
                (TARGET_W // 2, y - top),
                line,
                anchor="ma",
                font=heading_font,
                fill=(0, 0, 0, 255),
            )
            y = box[3] + line_gap

        credit_font = font(30)
        draw.text(
            (TARGET_W // 2, y + 20),
            "AI Short Film by @AngKulitPranks",
            anchor="ma",
            font=credit_font,
            fill=(255, 255, 255, 245),
            stroke_width=3,
            stroke_fill=(0, 0, 0, 210),
        )
    else:
        text_font = font(58)
        lines = wrap(draw, text, text_font, 900)

        # Keep subtitles to two readable lines and inside the social-video safe area.
        while len(lines) > 2 and text_font.size > 42:
            text_font = font(text_font.size - 2)
            lines = wrap(draw, text, text_font, 900)

        line_gap = 14
        block_height = len(lines) * text_font.size + max(0, len(lines) - 1) * line_gap
        y = 1510 - block_height // 2
        for line in lines:
            draw.text(
                (540, y),
                line,
                anchor="ma",
                font=text_font,
                fill=(255, 255, 255, 255),
                stroke_width=5,
                stroke_fill=(0, 0, 0, 235),
            )
            y += text_font.size + line_gap

    # After the opening credit, keep a smaller signature on all story frames.
    if not is_opening:
        watermark_font = font(34)
        draw.text(
            (TARGET_W - 42, 62),
            "@AngKulitPranks",
            anchor="ra",
            font=watermark_font,
            fill=(255, 255, 255, 205),
            stroke_width=3,
            stroke_fill=(0, 0, 0, 175),
        )
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


def next_backgrounds(story_number: int, required_duration: float) -> tuple[list[Path], int]:
    """Start at 1.mp4 in the matching story folder and take clips in numeric order."""
    story_video_dir = VIDEO_DIR / f"{story_number:03d}"
    clips = sorted(
        (p for p in story_video_dir.glob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS),
        key=natural_key,
    )
    if not clips:
        raise FileNotFoundError(
            f"No background clips found for Pinoy Mystery #{story_number:03d}. "
            f"Add videos to {story_video_dir.relative_to(ROOT)}/"
        )

    # Every reel deliberately begins with the first numbered clip (1.mp4).
    # The clips advance only within that reel, never from a previous workflow run.
    video_index = 0
    selected, covered = [], 0.0
    # Keep moving through the numbered files. Cycle only if every available clip is too short.
    while covered < required_duration:
        clip = clips[video_index % len(clips)]
        clip_duration = duration(clip)
        if clip_duration <= 0:
            raise RuntimeError(f"Background video has no usable duration: {clip}")
        selected.append(clip)
        covered += clip_duration
        video_index += 1
    return selected, video_index


def output_video_path(story_number: int, story: dict[str, str]) -> Path:
    # A readable, filesystem-safe filename based on the first line of the story.
    title = re.sub(r"[^a-z0-9]+", "-", story["header"].lower()).strip("-")
    title = title[:70].rstrip("-") or "pinoy-mystery"
    return OUTPUT_DIR / f"pinoy-mystery-{story_number:03d}-{title}.mp4"


def build_reel(story_number: int, story: dict[str, str], output_video: Path) -> int:
    # Title plus one sentence per card: easy to read, with motion used sparingly.
    beats = [("AI Short Film by @AngKulitPranks", story["header"])]
    sentences = split_sentences(story["body"])
    for index, sentence in enumerate(sentences):
        label = "THE ENDING" if index == len(sentences) - 1 else "THE STORY"
        beats.append((label, sentence))

    pngs, wavs, times = [], [], []
    for index, (label, text) in enumerate(beats):
        png, wav = OUTPUT_DIR / f"slide_{index}.png", OUTPUT_DIR / f"voice_{index}.wav"
        render_slide(story["header"], label, text, png)
        pngs.append(png); wavs.append(wav); times.append(narration(text, wav))
    manifest = OUTPUT_DIR / "audio.txt"
    manifest.write_text("".join(f"file '{p.resolve()}'\n" for p in wavs), encoding="utf-8")
    audio = OUTPUT_DIR / "narration.wav"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest), "-c:a", "pcm_s16le", str(audio)], check=True)
    total = sum(times)
    # The story ends when narration ends. Keep enough source audio available so it can
    # continue beneath the frozen frame and fade together with the picture.
    ending_duration = total + END_FREEZE_SECONDS + END_FADE_SECONDS
    fade_start = total + END_FREEZE_SECONDS
    background_videos, next_video_index = next_backgrounds(story_number, ending_duration)
    print(
        f"Using backgrounds for Pinoy Mystery #{story_number:03d}: "
        + ", ".join(video.name for video in background_videos)
    )

    # Concatenate numbered clips in order. The final selected clip is allowed to finish,
    # even if it extends beyond the narration; pad only as a safety net for a short source.
    filters = []
    for index, _video in enumerate(background_videos):
        label = f"bg{index}"
        filters.append(
            f"[{index}:v]scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
            f"crop={TARGET_W}:{TARGET_H},"
            f"fps=30,setsar=1,format=yuv420p[{label}]"
        )
    background_times = [duration(video) for video in background_videos]
    background_duration = sum(background_times)
    reel_duration = total
    filters.append(
        "".join(f"[bg{index}]" for index in range(len(background_videos)))
        + f"concat=n={len(background_videos)}:v=1:a=0,"
        + f"tpad=stop_mode=clone:stop_duration={total:.3f}[base]"
    )
    previous, start_time = "base", 0.0
    for i, slide_time in enumerate(times):
        end_time = start_time + slide_time
        # Gentle intro movement only: a small, slow one-time drift (no rapid shaking).
        # Story sentences remain completely steady for comfortable reading.
        if i == 0:
            x = r"if(lt(t\,0.650)\,3*sin(9*t)\,0)"
            y = r"if(lt(t\,0.650)\,2*sin(7*t)\,0)"
        else:
            x = y = "0"
        filters.append(
            f"[{len(background_videos) + i}:v]scale={TARGET_W}:{TARGET_H}[s{i}];"
            rf"[{previous}][s{i}]overlay=x='{x}':y='{y}':enable='between(t\,{start_time:.3f}\,{end_time:.3f})'[v{i}]"
        )
        previous, start_time = f"v{i}", end_time

    # One mild visual interruption is placed at a random safe point after the intro.
    # It is a single, low-contrast colour offset—never flashing, flickering, noisy, or repeated.
    glitch_start = random.uniform(max(1.0, total * 0.28), max(1.2, total * 0.78))
    glitch_end = min(total - 0.15, glitch_start + 0.12)
    filters.append(
        f"[{previous}]split=2[clean_for_overlay][clean_for_blend];"
        f"[clean_for_blend]split=2[blend_original][glitch_source];"
        f"[glitch_source]rgbashift=rh=4:bh=-4:gv=2[glitched];"
        f"[blend_original][glitched]blend=all_mode=average[mild_glitch];"
        rf"[clean_for_overlay][mild_glitch]overlay=enable='between(t\,{glitch_start:.3f}\,{glitch_end:.3f})'[final]"
    )
    previous = "final"

    # K-drama-style ending: hold the final story frame, then gently fade it to black.
    filters.append(
        f"[{previous}]trim=duration={reel_duration:.3f},setpts=PTS-STARTPTS,"
        f"tpad=stop_mode=clone:stop_duration={END_FREEZE_SECONDS + END_FADE_SECONDS:.3f},"
        f"fade=t=out:st={fade_start:.3f}:d={END_FADE_SECONDS:.3f}:color=black[ending_video]"
    )
    previous = "ending_video"

    # Mix narration at 100% with the original background-video sound at 20%.
    # Silent source clips receive matching silence so audio stays synchronized.
    background_audio_labels = []
    for index, (video, clip_time) in enumerate(zip(background_videos, background_times)):
        label = f"bga{index}"
        if has_audio(video):
            filters.append(
                f"[{index}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                f"volume=0.20,atrim=duration={clip_time:.3f},asetpts=PTS-STARTPTS[{label}]"
            )
        else:
            filters.append(
                f"anullsrc=r=48000:cl=stereo,atrim=duration={clip_time:.3f},"
                f"asetpts=PTS-STARTPTS[{label}]"
            )
        background_audio_labels.append(f"[{label}]")

    filters.append(
        "".join(background_audio_labels)
        + f"concat=n={len(background_audio_labels)}:v=0:a=1,"
        + f"apad,atrim=duration={ending_duration:.3f}[background_audio]"
    )
    narration_input = len(background_videos) + len(pngs)
    filters.append(
        f"[{narration_input}:a]aresample=48000,"
        f"aformat=sample_fmts=fltp:channel_layouts=stereo,volume=1.0,"
        f"apad,atrim=duration={ending_duration:.3f}[narration_audio]"
    )
    filters.append(
        "[narration_audio][background_audio]"
        "amix=inputs=2:duration=longest:normalize=0,"
        f"alimiter=limit=0.95,atrim=duration={ending_duration:.3f},"
        f"afade=t=out:st={fade_start:.3f}:d={END_FADE_SECONDS:.3f},"
        f"apad,atrim=duration={ending_duration:.3f}[ending_audio]"
    )

    command = ["ffmpeg", "-y"]
    for background_video in background_videos:
        command += ["-i", str(background_video)]
    for png in pngs:
        command += ["-loop", "1", "-i", str(png)]
    command += ["-i", str(audio), "-filter_complex", ";".join(filters), "-map", f"[{previous}]", "-map", "[ending_audio]", "-t", f"{ending_duration:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(output_video)]
    subprocess.run(command, check=True)
    return next_video_index



def main() -> None:
    # Render just one complete story per run, then advance to the next story.
    story_index, number, story = next_story()
    print(f"Making Pinoy Mystery #{number:03d}: {story['header']}")
    video_path = output_video_path(number, story)
    next_video_index = build_reel(number, story, video_path)
    save_progress(story_index, number, next_video_index)
    print(f"Rendered video saved to: {video_path}")


if __name__ == "__main__":
    main()
