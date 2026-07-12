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
HEADING_SECONDS = 4.0  # Relative display weight for the heading.
SLIDE_SECONDS = 3.0    # Relative display weight for each benefit.
# 0 = invisible; 255 = solid yellow. 150 shows the video through the box.
YELLOW_BOX_ALPHA = 150

# Add new topics ONLY at the bottom. Each topic is: heading first, then benefits.
POSTS = [
    {
        "heading": "Benepisyo sa pagtulog nang walang pantyyy",
        "benefits": [
            "Nakakatulong iwasan ang Fungal at Bacterial Growth",
            "Nakakabawas ng Skin Irritation at Chafing",
            "Mas magandang quality ng tulog",
            "Nakakatulong sa Temperature Regulation ng katawan",
            "Mas maayos na ventilation sa intimate area",
            "Nakakatulong sa relaxation at preskong pakiramdam",
        ],
        "caption": (
            "Benepisyo sa pagtulog nang walang pantyyy\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "Iwasan para hindi lumaki ang tiyan",
        "benefits": [
            "Sugary drinks, juices, milktea",
            "Refined carbohydrates (tinapay, pasta, pastries, cookies, biscuits)",
            "Saturated fats (fried chicken, burger, fries, delata, sausages, junkfoods)",
            "Alcoholic beverages",
        ],
        "caption": (
            "Iwasan para hindi lumaki ang tiyan\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "senyales na matanda kana",
        "benefits": [
            "Antukin kana (gusto mo nalang nakahiga palagi)",
            "madalas na sumakit ang likod mo",
            "Nanonood ka ng mga ingrown videos",
            "Hindi na kaya ang 2 rounds",
        ],
        "caption": (
            "senyales na matanda kana\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "iwasang gawin kapag lasing ang lalaki",
        "benefits": [
            "Maghanap ng away",
            "Magmaoy",
            "Tumabi sa hindi jowa (baka makasuhan ka pa)",
            "Makipagkarera sa pag drive (mapapabilis ang buhay mo)",
            "Umuwi sa ibang Bahay",
            "Makipagbmbang sa kainuman (Iwas STD/HIV or makabuntis nang hindi kilala)",
        ],
        "caption": (
            "iwasang gawin kapag lasing ang lalaki\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "problema ng mga lalaki kaya kulang sa stamina",
        "benefits": [
            "Naninigarilyo",
            "pag-inom ng alak",
            "Kulang sa CoQ10",
            "Sedentary lifestyle",
            "Kulang sa regular na ehersisyo",
            "Hindi sapat ang tulog",
            "Stress at mental health issues",
            "Obesity",
            "Type 2 Diabetes at high blood pressure",
            "Mababang testosterone level",
        ],
        "caption": (
            "problema ng mga lalaki kaya kulang sa stamina\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "maaaring dahilan ng mabahong ki!iifffyyy",
        "benefits": [
            "Bacterial Vaginosis",
            "Vaginal candidiasis",
            "Trichomoniasis",
            "Naiwang tampon o ibang bagay sa loob ng kiiiffffs",
            "pawis at hindi magandang bentilasyon sa ar1",
            "pagbabago sa normal na bacteria ng puwerta dahil sa regla, pakikipagtalik, o paggamit ng vaginal douches",
            "paiba-iba ang b3mbang partner",
        ],
        "caption": (
            "maaaring dahilan ng mabahong ki!iifffyyy\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "benepisyo ng pagtulog na walang brief",
        "benefits": [
            "Nakakatulong sa sp3erm health ng lalaki, iwas mainitan",
            "Pinipigilan ang bacterial at fungal growth sa ari",
            "Mas magandang daloy ng dugo at circulation",
            "Mas malamig at presko ang katawan habang natutulog",
            "Mas komportable at mas mahimbing na tulog",
        ],
        "caption": (
            "benepisyo ng pagtulog na walang brief\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "sakit na makukuha sa pakikipag halikan",
        "benefits": [
            "Infectious Mononucleosis (Kissing Disease)",
            "Oral Herpes (Cold Sores)",
            "Sipon at trangkaso (Colds and Flu)",
            "Syphilis mouth sores",
            "Chlamydia",
            "Gonorhea",
            "Germs that can cause GUM DISEASE",
        ],
        "caption": (
            "sakit na makukuha sa pakikipag halikan\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "Kapag matagal na walang b3mbaaang ang babae",
        "benefits": [
            "Mas sumisikip o mas ramdam ang penetration kapag nagging active ulit",
            "Mas madaling ma-stress at mainis (hindi lahat)",
            "Bumababa ang libido",
            "Nagbabago ang mood at pagiging emotionally responsive",
            "Posibleng bumaba ang natural lubrication ng katawan",
        ],
        "caption": (
            "Kapag matagal na walang b3mbaaang ang babae\n\n"
            "NOTE: Hindi naman lahat, pero karaniwan sa babae ganito ang mararanasan.\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "Senyales na sobra na sa gadgets ang mga bata",
        "benefits": [
            "Mahirap na siyang patulugin",
            "Maiksi na ang pasensya at magagalitin",
            "Ayaw ng makikipaglaro sa labas",
            "Paggising sa umaga, cellphone agad ang unang hinahanap",
            "Hindi na sya masyado nagsasalita dahil tutuk na sa cellphone",
            "Ayaw na niyang kumain kapag walang cellphone",
            "Laging may sumpong Lalo na sa kapag hindi bininigay ang cellphone",
        ],
        "caption": (
            "Senyales na sobra na sa gadgets ang mga bata\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "Humahaba pa ba ang saging ng lalake sa paglulu?",
        "benefits": [
            "Hindi!!!!",
            "Nagsstart ang paglaki ng saging during puberty around 12-18 years old",
            "Natitigil ang paglaki after puberty around 18-21 years old.",
            "Average size ng mga Pinoy ay 4.0 to 5.1 inches",
            "Huwag ka na umasa, ganyan na talaga yan",
            "Magpapayat ka or itigil ang pagyoyosi para magmukang malaki",
        ],
        "caption": (
            "Humahaba pa ba ang saging ng lalake sa paglulu?\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "Bakit nagfa-fake org@sm ang mga babae",
        "benefits": [
            "Hindi na sya masaya sayo",
            "Wala sya sa mood, pinagbigyan ka lang",
            "Para mapagbigyan nalang ang partner Kahit hindi gusto",
            "Para hindi magduda ang partner",
            "Para lang matapos na ang b3mbang",
            "Para hindi masaktan ang partner",
            "Mapapansin mo nagfake kapag hindi sobrang wet",
            "Kapag after nyo matapos, hindi sya ganun ka-happy tingnan or hindi na makikipag-usap or walang lambing",
        ],
        "caption": (
            "Bakit nagfa-fake org@sm ang mga babae\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "dahilan ng biglang pag lock ng Kiiifffyyy",
        "benefits": [
            "Trauma or pang-aabuso",
            "Takot o anxiety sa pakikipagtal!k",
            "Paniniwala na masama ang paki2pagtal1k",
            "Stress or problema sa partner",
            "Pinilit makipagb3mbang Kahit ayaw nito",
        ],
        "caption": (
            "dahilan ng biglang pag lock ng Kiiifffyyy\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "nauubos ba ang sem!lya ng lalaki kapag madalas maglulu?",
        "benefits": [
            "NO!!",
            "Pansamantalang pinapakunti lang nito ang sperm count sa madalas maglulu",
            "Hindi nauubusan ng semilya ang mga lalake habang sila'y nabubuhay",
            "pero habang tumatanda ang lalaki, maaaring bumaba ang kalidad, dami, at bilis ng sp3rm.",
            "Ang kakayahang magproduce ng semilya ay maaring maapektuhan ng mga bisyo (tulad ng paninigarilyo at alak), kakakulangan sa bitamina, at mga sakit.",
            "Base sa pag-aaral: 21x a month na paglulu para makaiwas sa Prostate Cancer",
        ],
        "caption": (
            "nauubos ba ang sem!lya ng lalaki kapag madalas maglulu?\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "Tamang pag-aalaga sa singit",
        "benefits": [
            "Iwasan ang sobrang pagkuskos at pagkamot ng sobra, mas lalong iitim ang balat",
            "Iwasan ang matamis ng pagkain",
            "Iwasan magshave palagi or madalas (pwede itong ma-irritate at mangati)",
            "Iwasan ibilad sa araw matagal",
            "huwag magsuot ng masikip na short at underwear para iwas Friction",
        ],
        "caption": (
            "Tamang pag-aalaga sa singit\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
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
    # Fill the full source-video duration every time. The heading keeps a little
    # more screen time than each benefit, while all slides automatically become
    # shorter for quick clips and longer for long clips.
    timing_weights = [HEADING_SECONDS] + [SLIDE_SECONDS] * len(post["benefits"])
    seconds_per_weight = duration / sum(timing_weights)
    slide_times = [weight * seconds_per_weight for weight in timing_weights]
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
    start = 0.0
    for i, slide_time in enumerate(slide_times):
        end = start + slide_time
        filters.append(f"[{i + 1}:v]scale={TARGET_W}:{TARGET_H}[t{i}]")
        filters.append(f"[{previous}][t{i}]overlay=0:0:enable='between(t,{start:.3f},{end:.3f})'[v{i + 1}]")
        previous = f"v{i + 1}"
        start = end

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
