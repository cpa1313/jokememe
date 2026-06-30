#!/usr/bin/env python3
"""
Viral Video Maker 😏
Posts your jokes in order on Facebook Reels daily.
Add new jokes at the BOTTOM of the JOKES list — order is always preserved.

Folder layout:
  assets/prettyaivideos/  ← your FB-compatible .mp4 clips
  jokes.json              ← auto-created, tracks which joke was last posted
  output/                 ← generated reel saved here
"""

import os
import sys
import json
import random
import subprocess
from pathlib import Path

# ── Auto-install missing packages ─────────────────────────────────────────────
def _ensure_packages(*packages):
    import importlib.util
    missing = [p for p in packages if not importlib.util.find_spec(p)]
    if missing:
        print(f"[Setup] Installing: {missing}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *missing])

_ensure_packages("Pillow", "requests")

import requests


# ── Env vars ───────────────────────────────────────────────────────────────────
def _require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        print(f"\n❌ Missing env var: '{name}'")
        print(f"   → GitHub repo → Settings → Secrets → Actions → Add: {name}\n")
        sys.exit(1)
    return val

FB_ACCESS_TOKEN = _require_env("FB_ACCESS_TOKEN")
FB_PAGE_ID      = _require_env("FB_PAGE_ID")


# ── Paths ──────────────────────────────────────────────────────────────────────
VIDEOS_DIR    = Path("assets/prettyaivideos")
OUTPUT_DIR    = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_VIDEO  = OUTPUT_DIR / "reel.mp4"

# ── Target resolution: 9:16 portrait for mobile Reels/Shorts ──────────────
TARGET_W = 1080
TARGET_H = 1920
PROGRESS_FILE = Path("jokes_progress.json")


# ══════════════════════════════════════════════════════════════════════════════
# 1. YOUR JOKES LIST — add new jokes at the BOTTOM only!
#    Each joke has:
#      "header" → bold text shown on top
#      "body"   → italic text shown below
#      "caption"→ Facebook post caption (can include hashtags)
# ══════════════════════════════════════════════════════════════════════════════

JOKES = [
    {
        "header": "lagi mo akong inuubos,",
        "body": "ang sarap mo kasi eh",
        "caption": "lagi mo akong inuubos, ang sarap mo kasi eh \U0001f60f\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": "sagad na sagad na pasensya ko,",
        "body": "sana ibang sagad naman maranasan ko",
        "caption": "sagad na sagad na pasensya ko, sana ibang sagad naman maranasan ko \U0001f60f\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": "Ang galing ko daw manamit,",
        "body": "ang hindi nila alam mas magaling ako kapag walang damit",
        "caption": "Ang galing ko daw manamit, ang hindi nila alam mas magaling ako kapag walang damit \U0001f60f\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": "Pwede moko sandalan pag may problema ka,",
        "body": "pwede ka rin pumatong para malutas na",
        "caption": "Pwede moko sandalan pag may problema ka, pwede ka rin pumatong para malutas na \U0001f60f\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": "Ikakagalit ba ng magic sarap",
        "body": "kung ang tunay na sarap sakin mo lang malalasap",
        "caption": "Ikakagalit ba ng magic sarap kung ang tunay na sarap sakin mo lang malalasap \U0001f60f\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": "lagi nalang ako kinakain ng kalungkutan,",
        "body": "ganon na ba ako kasarap?",
        "caption": "lagi nalang ako kinakain ng kalungkutan, ganon na ba ako kasarap? \U0001f60f\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": "mahalin mo lagi sarili mo",
        "body": "tapos idamay mo na rin ako",
        "caption": "mahalin mo lagi sarili mo tapos idamay mo na rin ako \U0001f60f\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": "baliktarin mo yung yehey oh diba walang nagbago,",
        "body": "ikaw pa rin gusto ko",
        "caption": "baliktarin mo yung yehey oh diba walang nagbago, ikaw pa rin gusto ko \U0001f60f\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": "ang ganda-ganda ng pangalan ko",
        "body": "tapos tatawagin mo lang akong love? aba isa pa nga",
        "caption": "ang ganda-ganda ng pangalan ko tapos tatawagin mo lang akong love? aba isa pa nga \U0001f60f\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Taxi ka ba?',
        "body": 'Kasi habang tumatagal lalo akong napapamahal sayo.',
        "caption": 'Taxi ka ba? Kasi habang tumatagal lalo akong napapamahal sayo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pag mayaman na ko, ititira kita sa mansyon ko.',
        "body": 'Pero ngayong mahirap pa ko, dito ka muna sa puso ko.',
        "caption": 'Pag mayaman na ko, ititira kita sa mansyon ko. Pero ngayong mahirap pa ko, dito ka muna sa puso ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hindi na ako gagamit pa ng GOOGLE,',
        "body": 'dahil nung nakilala kita, the SEARCH is over.',
        "caption": 'Hindi na ako gagamit pa ng GOOGLE, dahil nung nakilala kita, the SEARCH is over. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Para tayong packaging tape saka balahibo sa legs,',
        "body": 'masakit paghiwalayin.',
        "caption": 'Para tayong packaging tape saka balahibo sa legs, masakit paghiwalayin. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang ingay mo ah!',
        "body": 'Pag ikaw di pa nanahimik tatakpan ko na yang bibig mo.. NG LABI KO.',
        "caption": 'Ang ingay mo ah! Pag ikaw di pa nanahimik tatakpan ko na yang bibig mo.. NG LABI KO. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Nung bata ako andami kong gusto,',
        "body": 'ngayon IKAW na lang.',
        "caption": 'Nung bata ako andami kong gusto, ngayon IKAW na lang. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana piso ka na lang sa kalye,',
        "body": 'para pagnakita kita, akin ka na lang.',
        "caption": 'Sana piso ka na lang sa kalye, para pagnakita kita, akin ka na lang. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Masarap maging TAO,',
        "body": 'pero mas masarap maging TAYO.',
        "caption": 'Masarap maging TAO, pero mas masarap maging TAYO. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Never pa kitang napanaginipan,',
        "body": 'kasi wala ka nman sa utak ko dahil palagi kang nasa puso ko.',
        "caption": 'Never pa kitang napanaginipan, kasi wala ka nman sa utak ko dahil palagi kang nasa puso ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Dalawa lang naman ang bisyo ko..',
        "body": 'Malasing sa pagmamahal mo at isugal ang lahat para sayo.',
        "caption": 'Dalawa lang naman ang bisyo ko.. Malasing sa pagmamahal mo at isugal ang lahat para sayo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pag ikaw ang kasama ko… Tinatamad na ako…',
        "body": 'Kase ang sarap magpahinga sa piling mo.',
        "caption": 'Pag ikaw ang kasama ko… Tinatamad na ako… Kase ang sarap magpahinga sa piling mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Para kang holdaper.',
        "body": 'Lahat ibibigay ko sa yo, wag mo lang akong saktan.',
        "caption": 'Para kang holdaper. Lahat ibibigay ko sa yo, wag mo lang akong saktan. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana naka-off ang ilaw,',
        "body": 'para tayo nalang mag-on.',
        "caption": 'Sana naka-off ang ilaw, para tayo nalang mag-on. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sasali ka ba sa Marathon?',
        "body": 'Parang pinagpapractisan mo isip ko ah, takbo ka ng takbo!',
        "caption": 'Sasali ka ba sa Marathon? Parang pinagpapractisan mo isip ko ah, takbo ka ng takbo! 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana hacker na lang ako',
        "body": 'para HACKIN ka na lang.',
        "caption": 'Sana hacker na lang ako para HACKIN ka na lang. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana SIBUYAS nalang ang PUSO ko',
        "body": 'para iiyak ang sino mang dudurog nito.',
        "caption": 'Sana SIBUYAS nalang ang PUSO ko para iiyak ang sino mang dudurog nito. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang puso ko parang salamin,',
        "body": 'ilang beses mo man basagin pag tiningnan mo nandun ka pa rin.',
        "caption": 'Ang puso ko parang salamin, ilang beses mo man basagin pag tiningnan mo nandun ka pa rin. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Remote control ka ba?',
        "body": 'Kasi kahit malayo ka natuturn on mo ako eh.',
        "caption": 'Remote control ka ba? Kasi kahit malayo ka natuturn on mo ako eh. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Aanhin ko pa ang calculator….',
        "body": 'kung sayo palang solve na ako.',
        "caption": 'Aanhin ko pa ang calculator…. kung sayo palang solve na ako. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Alam mo bang para kitang password,',
        "body": 'kasi akin ka lang at hindi kita kayang ipamigay.',
        "caption": 'Alam mo bang para kitang password, kasi akin ka lang at hindi kita kayang ipamigay. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hindi mo man solo ang INBOX ko…',
        "body": 'ikaw lang naman ang laman ng SENT ITEMS ko.',
        "caption": 'Hindi mo man solo ang INBOX ko… ikaw lang naman ang laman ng SENT ITEMS ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Normal naman akong tao.',
        "body": 'Pero bakit pag iniisip kita, Nababaliw ako?',
        "caption": 'Normal naman akong tao. Pero bakit pag iniisip kita, Nababaliw ako? 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sa lahat ng book isa lang ang gusto kong angkinin.',
        "body": 'ang ti-BOOK ng puso mo!',
        "caption": 'Sa lahat ng book isa lang ang gusto kong angkinin. ang ti-BOOK ng puso mo! 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang pera ginawa para gastusin. Ang pagkain ginawa para kainin.',
        "body": 'Sana ang puso mo ginawa para sa akin.',
        "caption": 'Ang pera ginawa para gastusin. Ang pagkain ginawa para kainin. Sana ang puso mo ginawa para sa akin. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hindi ka lang nangunguna sa NEWS FEED ko,',
        "body": 'MOST RECENT ka na sa isip ko, TOP NEWS ka pa sa PUSO ko.',
        "caption": 'Hindi ka lang nangunguna sa NEWS FEED ko, MOST RECENT ka na sa isip ko, TOP NEWS ka pa sa PUSO ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": "May MALI ba sa 'ken?",
        "body": 'hayaan mo na may TAMA naman ako sayo.',
        "caption": "May MALI ba sa 'ken? hayaan mo na may TAMA naman ako sayo. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Sana sa susunod na gising ko wala ka na sa isip ko.',
        "body": 'nandito ka na sana sa tabi ko.',
        "caption": 'Sana sa susunod na gising ko wala ka na sa isip ko. nandito ka na sana sa tabi ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Para kang Gas Station,',
        "body": 'u fill me up and keep me going.',
        "caption": 'Para kang Gas Station, u fill me up and keep me going. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana naging pwet na lang din ako ng kaldero…',
        "body": 'para lagi akong kini-KISS KISS.',
        "caption": 'Sana naging pwet na lang din ako ng kaldero… para lagi akong kini-KISS KISS. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Stapler ka ba?',
        "body": 'Ako kasi yung papel na handang masaktan makasama ka lang.',
        "caption": 'Stapler ka ba? Ako kasi yung papel na handang masaktan makasama ka lang. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Dahil sa maghapon ka patakbo takbo sa isip,',
        "body": 'ayan nakarating ka tuloy sa puso ko.',
        "caption": 'Dahil sa maghapon ka patakbo takbo sa isip, ayan nakarating ka tuloy sa puso ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sabi nila LIBRE LANG MANGARAP…',
        "body": 'libre ka ba? Ikaw kasi pangarap ko eh.',
        "caption": 'Sabi nila LIBRE LANG MANGARAP… libre ka ba? Ikaw kasi pangarap ko eh. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Screw ka ba?',
        "body": 'Kasi habang umiikot ka sa isip ko, mas lalo kang bumabaon sa puso ko.',
        "caption": 'Screw ka ba? Kasi habang umiikot ka sa isip ko, mas lalo kang bumabaon sa puso ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Para tayong nasa see-saw,',
        "body": "kasi when ur not there, I'm down.",
        "caption": "Para tayong nasa see-saw, kasi when ur not there, I'm down. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Para kong isda kapag nakatingin sayo…',
        "body": 'walang kurap.',
        "caption": 'Para kong isda kapag nakatingin sayo… walang kurap. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gaano man karaming alak ang inumin ko.',
        "body": 'Hindi yun mapapantayan ng tama ko sayo.',
        "caption": 'Gaano man karaming alak ang inumin ko. Hindi yun mapapantayan ng tama ko sayo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Para kang birthday ko,',
        "body": 'kasi nung dumating ka doon na nagsimula ang buhay ko.',
        "caption": 'Para kang birthday ko, kasi nung dumating ka doon na nagsimula ang buhay ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kahit wala ka sa Top News at hindi ka Top Trend,',
        "body": "dont worry you're on TOP of my everything.",
        "caption": "Kahit wala ka sa Top News at hindi ka Top Trend, dont worry you're on TOP of my everything. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Gusto kong MAPAG-ISA!!',
        "body": 'ang PUSO nating DALAWA!',
        "caption": 'Gusto kong MAPAG-ISA!! ang PUSO nating DALAWA! 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Dati gusto lang kita maging friend,',
        "body": 'ngayon gusto na kitang maging cousin… cousintahan.',
        "caption": 'Dati gusto lang kita maging friend, ngayon gusto na kitang maging cousin… cousintahan. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang mundo, umiikot sa araw,',
        "body": 'pero ang mundo ko umiikot sayo ARAW-ARAW.',
        "caption": 'Ang mundo, umiikot sa araw, pero ang mundo ko umiikot sayo ARAW-ARAW. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung may LOVE button sa status mo,',
        "body": 'laspag na mouse ko kakaclick nun.',
        "caption": 'Kung may LOVE button sa status mo, laspag na mouse ko kakaclick nun. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung hindi ka tumatakbo sa isip ko,',
        "body": 'malamang nagpapahinga ka sa puso ko.',
        "caption": 'Kung hindi ka tumatakbo sa isip ko, malamang nagpapahinga ka sa puso ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tubig ka ba?',
        "body": 'Ako kasi yung isda at di ako mabubuhay ng wala ka.',
        "caption": 'Tubig ka ba? Ako kasi yung isda at di ako mabubuhay ng wala ka. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Akala ko sa H nagsisimula ang HAPPINESS,',
        "body": 'bakit yung akin nagsisimula sa U.',
        "caption": 'Akala ko sa H nagsisimula ang HAPPINESS, bakit yung akin nagsisimula sa U. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Nahihilo ako…',
        "body": 'pinapaikot mo kasi ang mundo ko.',
        "caption": 'Nahihilo ako… pinapaikot mo kasi ang mundo ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ahh miss pwede ba kitang ipagtimpla ng kape?',
        "body": 'Corny kase mag I love you eh.',
        "caption": 'Ahh miss pwede ba kitang ipagtimpla ng kape? Corny kase mag I love you eh. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Para kang I.D. ko,',
        "body": 'kasi kapag nawala ka, ALAM NILANG AKIN KA!',
        "caption": 'Para kang I.D. ko, kasi kapag nawala ka, ALAM NILANG AKIN KA! 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Wag mo na kong hanapin sa Dictionary,',
        "body": 'kasi alam mo namang IKAW ang MEANING ko.',
        "caption": 'Wag mo na kong hanapin sa Dictionary, kasi alam mo namang IKAW ang MEANING ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hindi ako pwede sa Saturday, hindi rin ako pwede sa Sunday…',
        "body": "SA'YO lang ako pwede.",
        "caption": "Hindi ako pwede sa Saturday, hindi rin ako pwede sa Sunday… SA'YO lang ako pwede. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Jeep ka ba?',
        "body": "Kasi PARA PO ako sa'yo.",
        "caption": "Jeep ka ba? Kasi PARA PO ako sa'yo. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Iiyak ka ba kapag namatay ako?',
        "body": "pwes umiyak ka na… dahil PATAY na PATAY na ako SA'YO.",
        "caption": "Iiyak ka ba kapag namatay ako? pwes umiyak ka na… dahil PATAY na PATAY na ako SA'YO. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Isang feeling lang naman ang gusto ko eh…',
        "body": 'yon ay ang maka-FEELING ka.',
        "caption": 'Isang feeling lang naman ang gusto ko eh… yon ay ang maka-FEELING ka. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tubig ka ba?',
        "body": 'Ikaw kasi ang bumubuo sa pinaka-malaking bahagi ng mundo ko.',
        "caption": 'Tubig ka ba? Ikaw kasi ang bumubuo sa pinaka-malaking bahagi ng mundo ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kailangan ko ng matutong mag-BUDGET,',
        "body": 'napapaMAHAL na kasi ako sayo.',
        "caption": 'Kailangan ko ng matutong mag-BUDGET, napapaMAHAL na kasi ako sayo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang galing pala mag-bake ng mommy mo…',
        "body": "cuz you're a cutie pie.",
        "caption": "Ang galing pala mag-bake ng mommy mo… cuz you're a cutie pie. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Pinuntahan ko na ang bawat kanto ng kama ko.',
        "body": 'Pero wala talaga akong makitang komportableng posisyon… kundi sa tabi mo.',
        "caption": 'Pinuntahan ko na ang bawat kanto ng kama ko. Pero wala talaga akong makitang komportableng posisyon… kundi sa tabi mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sipon ka ba?',
        "body": 'kasi lagi kang nandyan pag umiiyak ako.',
        "caption": 'Sipon ka ba? kasi lagi kang nandyan pag umiiyak ako. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'BUWAN ka ba?',
        "body": 'kasi ARAW-ARAW namimis kita.',
        "caption": 'BUWAN ka ba? kasi ARAW-ARAW namimis kita. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Engineer ka ba?',
        "body": 'Gusto kasi kita makasama engineer future.',
        "caption": 'Engineer ka ba? Gusto kasi kita makasama engineer future. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'MALL OF ASIA ka ba?',
        "body": 'kasi ayoko MOA-lay ka sa piling ko eh.',
        "caption": 'MALL OF ASIA ka ba? kasi ayoko MOA-lay ka sa piling ko eh. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung iniisip mong mahal kita, think TWICE!',
        "body": 'MAHAL na MAHAL kaya.',
        "caption": 'Kung iniisip mong mahal kita, think TWICE! MAHAL na MAHAL kaya. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Bahala ako sa BUHAY KO ha? ha?',
        "body": 'edi ako na BAHALA SAYO.',
        "caption": 'Bahala ako sa BUHAY KO ha? ha? edi ako na BAHALA SAYO. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Utot ka ba?',
        "body": 'kasi U-TOT me how to love eh.',
        "caption": 'Utot ka ba? kasi U-TOT me how to love eh. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana pasyente mo nalang ako,',
        "body": "para masabi ko ang lahat ng nararamdaman ko sa'yo.",
        "caption": "Sana pasyente mo nalang ako, para masabi ko ang lahat ng nararamdaman ko sa'yo. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Yuck yuck ka Jan?',
        "body": 'YUCKapin kita eh!',
        "caption": 'Yuck yuck ka Jan? YUCKapin kita eh! 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hindi ko pinangarap na maging CASHIER…',
        "body": 'Ayoko kasing MAY-CASHIER sa PUSO MO.',
        "caption": 'Hindi ko pinangarap na maging CASHIER… Ayoko kasing MAY-CASHIER sa PUSO MO. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'ARMY ka ba?',
        "body": 'kasi you AR-MY one and only.',
        "caption": 'ARMY ka ba? kasi you AR-MY one and only. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sayo na tong relo ko oh,',
        "body": 'basta sa akin lang yang oras mo.',
        "caption": 'Sayo na tong relo ko oh, basta sa akin lang yang oras mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Mermaid ka ba?',
        "body": 'kasi pag wala ka SIRE NA araw ko.',
        "caption": 'Mermaid ka ba? kasi pag wala ka SIRE NA araw ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Nine ka ba?',
        "body": "kasi NINE-love na 'ko sayo.",
        "caption": "Nine ka ba? kasi NINE-love na 'ko sayo. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Alam mo lagi kang hinahanap ng mga mata ko…',
        "body": 'kasi EYE love you.',
        "caption": 'Alam mo lagi kang hinahanap ng mga mata ko… kasi EYE love you. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang makuha number mo?',
        "body": 'Para may dahilan na ko para mag load.',
        "caption": 'Pwede bang makuha number mo? Para may dahilan na ko para mag load. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'ISSUE ka ba?',
        "body": 'kasi all I want for Christmas ISSUE.',
        "caption": 'ISSUE ka ba? kasi all I want for Christmas ISSUE. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Paano mo masasabing di kita MAHAL?',
        "body": 'Kung sa bawat pag gising ko IKAW ang hinahanap ko at hindi ang ALMUSAL.',
        "caption": 'Paano mo masasabing di kita MAHAL? Kung sa bawat pag gising ko IKAW ang hinahanap ko at hindi ang ALMUSAL. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang lahat ng bagay ay may hangganan, parang AKO…',
        "body": 'hanggang SAYO lang.',
        "caption": 'Ang lahat ng bagay ay may hangganan, parang AKO… hanggang SAYO lang. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung bulaklak ka, pinitas na kita. Kung unan ka, niyakap na kita.',
        "body": 'Kaso, naging tao ka, kaya minahal nalang kita.',
        "caption": 'Kung bulaklak ka, pinitas na kita. Kung unan ka, niyakap na kita. Kaso, naging tao ka, kaya minahal nalang kita. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kadiliman ka ba?',
        "body": 'kasi kapag nandyan ka wala akong nakikitang iba.',
        "caption": 'Kadiliman ka ba? kasi kapag nandyan ka wala akong nakikitang iba. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sa lahat ng taong nakilala ko, ikaw ang pinaka ayoko!',
        "body": 'pinaka-ayokong mawala sa buhay ko!',
        "caption": 'Sa lahat ng taong nakilala ko, ikaw ang pinaka ayoko! pinaka-ayokong mawala sa buhay ko! 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung sa tingin mo pinaglalaruan lang kita',
        "body": 'try mong pumasok sa puso ko tignan mo kung may kalaro ka.',
        "caption": 'Kung sa tingin mo pinaglalaruan lang kita try mong pumasok sa puso ko tignan mo kung may kalaro ka. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ayoko na ngang mag relo,',
        "body": 'kasi lahat ng oras ko, ibibigay ko na sayo!',
        "caption": 'Ayoko na ngang mag relo, kasi lahat ng oras ko, ibibigay ko na sayo! 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Anong pagkakaiba ng bahay niyo sa puso ko?',
        "body": 'Simple lang, sa bahay niyo may kasama ka, sa puso ko nag-iisa ka.',
        "caption": 'Anong pagkakaiba ng bahay niyo sa puso ko? Simple lang, sa bahay niyo may kasama ka, sa puso ko nag-iisa ka. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hindi man ako ang Royal Prince,',
        "body": 'pwede mo naman akong maging Loyal Prince.',
        "caption": 'Hindi man ako ang Royal Prince, pwede mo naman akong maging Loyal Prince. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Reporter ka ba?',
        "body": 'Pakibalita naman sa buong mundo na mahal kita.',
        "caption": 'Reporter ka ba? Pakibalita naman sa buong mundo na mahal kita. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Magaling ka ba sa Filipino?',
        "body": 'kapag pinagsama ba ang panghalip na IKAW at AKO posible bang maging TAYO?',
        "caption": 'Magaling ka ba sa Filipino? kapag pinagsama ba ang panghalip na IKAW at AKO posible bang maging TAYO? 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang pag-ibig ko sayo ay parang paghinga.',
        "body": 'Bakit ko ititigil kung alam kong hindi ko kaya?',
        "caption": 'Ang pag-ibig ko sayo ay parang paghinga. Bakit ko ititigil kung alam kong hindi ko kaya? 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kapag sinubukan mong silipin ang utak ko…',
        "body": 'para ka lang tumingin sa mga selfie mo.',
        "caption": 'Kapag sinubukan mong silipin ang utak ko… para ka lang tumingin sa mga selfie mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Huwag kang umasta na parang ang yaman-yaman mo.',
        "body": "Eh isa ka lang namang hamak na tambay dito sa puso't isipan ko.",
        "caption": "Huwag kang umasta na parang ang yaman-yaman mo. Eh isa ka lang namang hamak na tambay dito sa puso't isipan ko. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Kapag nakikita kita nawawalan ako ng gana…',
        "body": 'Ganang tumingin sa iba.',
        "caption": 'Kapag nakikita kita nawawalan ako ng gana… Ganang tumingin sa iba. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana antok na lang ako',
        "body": 'para madalaw kita gabi-gabi.',
        "caption": 'Sana antok na lang ako para madalaw kita gabi-gabi. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung sa gitara maririnig ang musika.',
        "body": 'Sa puso ko maririnig mong mahal kita.',
        "caption": 'Kung sa gitara maririnig ang musika. Sa puso ko maririnig mong mahal kita. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana pera na lang ako…',
        "body": "para kung mahulog man ako sa'yo… sasabihin mong 'Akin yan'.",
        "caption": "Sana pera na lang ako… para kung mahulog man ako sa'yo… sasabihin mong 'Akin yan'. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Sana ang pag-ibig mo ay parang takbo ng orasan…',
        "body": 'Laging pakanan… walang kaliwaan.',
        "caption": 'Sana ang pag-ibig mo ay parang takbo ng orasan… Laging pakanan… walang kaliwaan. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sabi nila pag dinilaan mo daw ang pagkain mo wala ng aagaw sayo..',
        "body": 'Dilaan din kaya kita, Para hindi ka na maagaw ng iba?',
        "caption": 'Sabi nila pag dinilaan mo daw ang pagkain mo wala ng aagaw sayo.. Dilaan din kaya kita, Para hindi ka na maagaw ng iba? 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Alam mo bakit maalat ang dagat?',
        "body": "Kasi lahat ng ka-sweetan napunta sa'yo.",
        "caption": "Alam mo bakit maalat ang dagat? Kasi lahat ng ka-sweetan napunta sa'yo. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Sa dinadami ng hayop sa farm,',
        "body": 'COW lang ang gusto ko.',
        "caption": 'Sa dinadami ng hayop sa farm, COW lang ang gusto ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kelan ang birthday ko?',
        "body": 'Nung araw na maging tayo, kasi dun pa lang nagsimula ang buhay ko.',
        "caption": 'Kelan ang birthday ko? Nung araw na maging tayo, kasi dun pa lang nagsimula ang buhay ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede mo ba ako samahan?',
        "body": 'samahan HABANGBUHAY.',
        "caption": 'Pwede mo ba ako samahan? samahan HABANGBUHAY. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tikman mo tong cake. Masarap. Gawa kasi ng nanay ko.',
        "body": 'Ikaw nalang titikman ko. Gawa ka rin naman ng nanay mo eh.',
        "caption": 'Tikman mo tong cake. Masarap. Gawa kasi ng nanay ko. Ikaw nalang titikman ko. Gawa ka rin naman ng nanay mo eh. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'andami mo namang babae!',
        "body": 'sino ba talaga laman ng puso mo? ewan ko! ikaw may-ari nito tapos ako tatanungin mo.',
        "caption": 'andami mo namang babae! sino ba talaga laman ng puso mo? ewan ko! ikaw may-ari nito tapos ako tatanungin mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hindi ako pwede sa Saturday, hindi rin ako pwede sa Sunday…',
        "body": "SA'YO lang ako pwede.",
        "caption": "Hindi ako pwede sa Saturday, hindi rin ako pwede sa Sunday… SA'YO lang ako pwede. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Jeep ka ba?',
        "body": "Kasi PARA PO ako sa'yo.",
        "caption": "Jeep ka ba? Kasi PARA PO ako sa'yo. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Iiyak ka ba kapag namatay ako?',
        "body": "pwes umiyak ka na… dahil PATAY na PATAY na ako SA'YO.",
        "caption": "Iiyak ka ba kapag namatay ako? pwes umiyak ka na… dahil PATAY na PATAY na ako SA'YO. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Isang feeling lang naman ang gusto ko eh…',
        "body": 'yon ay ang maka-FEELING ka.',
        "caption": 'Isang feeling lang naman ang gusto ko eh… yon ay ang maka-FEELING ka. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tubig ka ba? Ikaw kasi ang bumubuo sa pinaka-malaking bahagi ng mundo ko.',
        "body": 'Ikaw kasi ang bumubuo sa pinaka-malaking bahagi ng mundo ko.',
        "caption": 'Tubig ka ba? Ikaw kasi ang bumubuo sa pinaka-malaking bahagi ng mundo ko. Ikaw kasi ang bumubuo sa pinaka-malaking bahagi ng mundo ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kailangan ko ng matutong mag-BUDGET,',
        "body": 'napapaMAHAL na kasi ako sayo.',
        "caption": 'Kailangan ko ng matutong mag-BUDGET, napapaMAHAL na kasi ako sayo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang galing pala mag-bake ng mommy mo…',
        "body": "cuz you're a cutie pie.",
        "caption": "Ang galing pala mag-bake ng mommy mo… cuz you're a cutie pie. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Pinuntahan ko na ang bawat kanto ng kama ko.',
        "body": 'Pero wala talaga akong makitang komportableng posisyon… kundi sa tabi mo.',
        "caption": 'Pinuntahan ko na ang bawat kanto ng kama ko. Pero wala talaga akong makitang komportableng posisyon… kundi sa tabi mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sipon ka ba?',
        "body": 'kasi lagi kang nandyan pag umiiyak ako.',
        "caption": 'Sipon ka ba? kasi lagi kang nandyan pag umiiyak ako. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'BUWAN ka ba?',
        "body": 'kasi ARAW-ARAW namimis kita.',
        "caption": 'BUWAN ka ba? kasi ARAW-ARAW namimis kita. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Engineer ka ba?',
        "body": 'Gusto kasi kita makasama engineer future.',
        "caption": 'Engineer ka ba? Gusto kasi kita makasama engineer future. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'MALL OF ASIA ka ba?',
        "body": 'kasi ayoko MOA-lay ka sa piling ko eh.',
        "caption": 'MALL OF ASIA ka ba? kasi ayoko MOA-lay ka sa piling ko eh. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung iniisip mong mahal kita, think TWICE!',
        "body": 'MAHAL na MAHAL kaya.',
        "caption": 'Kung iniisip mong mahal kita, think TWICE! MAHAL na MAHAL kaya. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Bahala ako sa BUHAY KO ha? ha?',
        "body": 'edi ako na BAHALA SAYO.',
        "caption": 'Bahala ako sa BUHAY KO ha? ha? edi ako na BAHALA SAYO. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Utot ka ba?',
        "body": 'kasi U-TOT me how to love eh.',
        "caption": 'Utot ka ba? kasi U-TOT me how to love eh. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana pasyente mo nalang ako,',
        "body": "para masabi ko ang lahat ng nararamdaman ko sa'yo.",
        "caption": "Sana pasyente mo nalang ako, para masabi ko ang lahat ng nararamdaman ko sa'yo. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Yuck yuck ka Jan?',
        "body": 'YUCKapin kita eh!',
        "caption": 'Yuck yuck ka Jan? YUCKapin kita eh! 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hindi ko pinangarap na maging CASHIER…',
        "body": 'Ayoko kasing MAY-CASHIER sa PUSO MO.',
        "caption": 'Hindi ko pinangarap na maging CASHIER… Ayoko kasing MAY-CASHIER sa PUSO MO. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'ARMY ka ba?',
        "body": 'kasi you AR-MY one and only.',
        "caption": 'ARMY ka ba? kasi you AR-MY one and only. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sayo na tong relo ko oh,',
        "body": 'basta sa akin lang yang oras mo.',
        "caption": 'Sayo na tong relo ko oh, basta sa akin lang yang oras mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Mermaid ka ba?',
        "body": 'kasi pag wala ka SIRE NA araw ko.',
        "caption": 'Mermaid ka ba? kasi pag wala ka SIRE NA araw ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Nine ka ba?',
        "body": "kasi NINE-love na 'ko sayo.",
        "caption": "Nine ka ba? kasi NINE-love na 'ko sayo. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Alam mo lagi kang hinahanap ng mga mata ko…',
        "body": 'kasi EYE love you.',
        "caption": 'Alam mo lagi kang hinahanap ng mga mata ko… kasi EYE love you. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang makuha number mo?',
        "body": 'Para may dahilan na ko para mag load.',
        "caption": 'Pwede bang makuha number mo? Para may dahilan na ko para mag load. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'ISSUE ka ba?',
        "body": 'kasi all I want for Christmas ISSUE.',
        "caption": 'ISSUE ka ba? kasi all I want for Christmas ISSUE. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Paano mo masasabing di kita MAHAL?',
        "body": 'Kung sa bawat pag gising ko IKAW ang hinahanap ko at hindi ang ALMUSAL.',
        "caption": 'Paano mo masasabing di kita MAHAL? Kung sa bawat pag gising ko IKAW ang hinahanap ko at hindi ang ALMUSAL. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang lahat ng bagay ay may hangganan, parang AKO…',
        "body": 'hanggang SAYO lang.',
        "caption": 'Ang lahat ng bagay ay may hangganan, parang AKO… hanggang SAYO lang. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung bulaklak ka, pinitas na kita. Kung unan ka, niyakap na kita.',
        "body": 'Kaso, naging tao ka, kaya minahal nalang kita.',
        "caption": 'Kung bulaklak ka, pinitas na kita. Kung unan ka, niyakap na kita. Kaso, naging tao ka, kaya minahal nalang kita. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kadiliman ka ba?',
        "body": 'kasi kapag nandyan ka wala akong nakikitang iba.',
        "caption": 'Kadiliman ka ba? kasi kapag nandyan ka wala akong nakikitang iba. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sa lahat ng taong nakilala ko, ikaw ang pinaka ayoko!',
        "body": 'pinaka-ayokong mawala sa buhay ko!',
        "caption": 'Sa lahat ng taong nakilala ko, ikaw ang pinaka ayoko! pinaka-ayokong mawala sa buhay ko! 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung sa tingin mo pinaglalaruan lang kita',
        "body": 'try mong pumasok sa puso ko tignan mo kung may kalaro ka.',
        "caption": 'Kung sa tingin mo pinaglalaruan lang kita try mong pumasok sa puso ko tignan mo kung may kalaro ka. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ayoko na ngang mag relo,',
        "body": 'kasi lahat ng oras ko, ibibigay ko na sayo!',
        "caption": 'Ayoko na ngang mag relo, kasi lahat ng oras ko, ibibigay ko na sayo! 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Anong pagkakaiba ng bahay niyo sa puso ko?',
        "body": 'Simple lang, sa bahay niyo may kasama ka, sa puso ko nag-iisa ka.',
        "caption": 'Anong pagkakaiba ng bahay niyo sa puso ko? Simple lang, sa bahay niyo may kasama ka, sa puso ko nag-iisa ka. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hindi man ako ang Royal Prince,',
        "body": 'pwede mo naman akong maging Loyal Prince.',
        "caption": 'Hindi man ako ang Royal Prince, pwede mo naman akong maging Loyal Prince. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Reporter ka ba?',
        "body": 'Pakibalita naman sa buong mundo na mahal kita.',
        "caption": 'Reporter ka ba? Pakibalita naman sa buong mundo na mahal kita. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Magaling ka ba sa Filipino?',
        "body": 'kapag pinagsama ba ang panghalip na IKAW at AKO posible bang maging TAYO?',
        "caption": 'Magaling ka ba sa Filipino? kapag pinagsama ba ang panghalip na IKAW at AKO posible bang maging TAYO? 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang pag-ibig ko sayo ay parang paghinga.',
        "body": 'Bakit ko ititigil kung alam kong hindi ko kaya?',
        "caption": 'Ang pag-ibig ko sayo ay parang paghinga. Bakit ko ititigil kung alam kong hindi ko kaya? 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kapag sinubukan mong silipin ang utak ko…',
        "body": 'para ka lang tumingin sa mga selfie mo.',
        "caption": 'Kapag sinubukan mong silipin ang utak ko… para ka lang tumingin sa mga selfie mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Huwag kang umasta na parang ang yaman-yaman mo.',
        "body": "Eh isa ka lang namang hamak na tambay dito sa puso't isipan ko.",
        "caption": "Huwag kang umasta na parang ang yaman-yaman mo. Eh isa ka lang namang hamak na tambay dito sa puso't isipan ko. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Kapag nakikita kita nawawalan ako ng gana…',
        "body": 'Ganang tumingin sa iba.',
        "caption": 'Kapag nakikita kita nawawalan ako ng gana… Ganang tumingin sa iba. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana antok na lang ako',
        "body": 'para madalaw kita gabi-gabi.',
        "caption": 'Sana antok na lang ako para madalaw kita gabi-gabi. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung sa gitara maririnig ang musika.',
        "body": 'Sa puso ko maririnig mong mahal kita.',
        "caption": 'Kung sa gitara maririnig ang musika. Sa puso ko maririnig mong mahal kita. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sana pera na lang ako…',
        "body": "para kung mahulog man ako sa'yo… sasabihin mong 'Akin yan'.",
        "caption": "Sana pera na lang ako… para kung mahulog man ako sa'yo… sasabihin mong 'Akin yan'. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Sana ang pag-ibig mo ay parang takbo ng orasan…',
        "body": 'Laging pakanan… walang kaliwaan.',
        "caption": 'Sana ang pag-ibig mo ay parang takbo ng orasan… Laging pakanan… walang kaliwaan. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sabi nila pag dinilaan mo daw ang pagkain mo wala ng aagaw sayo..',
        "body": 'Dilaan din kaya kita, para hindi ka na maagaw ng iba?',
        "caption": 'Sabi nila pag dinilaan mo daw ang pagkain mo wala ng aagaw sayo.. Dilaan din kaya kita, para hindi ka na maagaw ng iba? 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Alam mo bakit maalat ang dagat?',
        "body": "Kasi lahat ng ka-sweetan napunta sa'yo.",
        "caption": "Alam mo bakit maalat ang dagat? Kasi lahat ng ka-sweetan napunta sa'yo. 😏\n\n#flirty #taglish #funnyfilipino #reels",
    },
    {
        "header": 'Sa dinadami ng hayop sa farm,',
        "body": 'COW lang ang gusto ko.',
        "caption": 'Sa dinadami ng hayop sa farm, COW lang ang gusto ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kelan ang birthday ko?',
        "body": 'Nung araw na maging tayo, kasi dun pa lang nagsimula ang buhay ko.',
        "caption": 'Kelan ang birthday ko? Nung araw na maging tayo, kasi dun pa lang nagsimula ang buhay ko. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede mo ba ako samahan?',
        "body": 'samahan HABANGBUHAY.',
        "caption": 'Pwede mo ba ako samahan? samahan HABANGBUHAY. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tikman mo tong cake. Masarap. Gawa kasi ng nanay ko.',
        "body": 'Ikaw nalang titikman ko. Gawa ka rin naman ng nanay mo eh.',
        "caption": 'Tikman mo tong cake. Masarap. Gawa kasi ng nanay ko. Ikaw nalang titikman ko. Gawa ka rin naman ng nanay mo eh. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'andami mo namang babae!',
        "body": 'sino ba talaga laman ng puso mo? Ewan ko! ikaw may-ari nito tapos ako tatanungin mo.',
        "caption": 'andami mo namang babae! sino ba talaga laman ng puso mo? Ewan ko! ikaw may-ari nito tapos ako tatanungin mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto mo bang maging kape ko sa umaga',
        "body": 'Para kahit mainit ka, papasok pa rin kita sa bibig ko',
        "caption": 'Gusto mo bang maging kape ko sa umaga Para kahit mainit ka, papasok pa rin kita sa bibig ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Miss ka ba ng electric fan',
        "body": 'Kasi kahit walang hangin, pinapainit mo ako',
        "caption": 'Miss ka ba ng electric fan Kasi kahit walang hangin, pinapainit mo ako 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto mo ng saging Hindi para kainin,',
        "body": 'kundi para maramdaman mo kung gaano ka kaswerte',
        "caption": 'Gusto mo ng saging Hindi para kainin, kundi para maramdaman mo kung gaano ka kaswerte 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tag-ulan na ba o ako',
        "body": 'lang ang basa kapag kasama ka',
        "caption": 'Tag-ulan na ba o ako lang ang basa kapag kasama ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kama ka ba',
        "body": 'Kasi gusto kong mahiga sa\'yo buong gabi',
        "caption": 'Kama ka ba Kasi gusto kong mahiga sa\'yo buong gabi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto mong tikman ang secret',
        "body": 'recipe ko Pampainit at pampasarap',
        "caption": 'Gusto mong tikman ang secret recipe ko Pampainit at pampasarap 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Lips mo ba yan o dessert',
        "body": 'Kasi gusto ko nang tikman',
        "caption": 'Lips mo ba yan o dessert Kasi gusto ko nang tikman 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Naliligo ka ba araw-araw',
        "body": 'Kasi kahit basa ka, nakakaakit ka pa rin',
        "caption": 'Naliligo ka ba araw-araw Kasi kahit basa ka, nakakaakit ka pa rin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang halikan Hindi lang sa labi,',
        "body": 'kundi sa buong katawan',
        "caption": 'Pwede ba kitang halikan Hindi lang sa labi, kundi sa buong katawan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sabon ka ba',
        "body": 'Kasi gusto kong ikuskos ka sa buong katawan ko',
        "caption": 'Sabon ka ba Kasi gusto kong ikuskos ka sa buong katawan ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Init ng panahon o init',
        "body": 'ng katawan kapag kasama kita',
        "caption": 'Init ng panahon o init ng katawan kapag kasama kita 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pipino ka ba',
        "body": 'Kasi ang tigas mo sa paningin ko',
        "caption": 'Pipino ka ba Kasi ang tigas mo sa paningin ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto mo ng massage',
        "body": 'Pero sa kama lang kita gagamutin',
        "caption": 'Gusto mo ng massage Pero sa kama lang kita gagamutin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang i-video',
        "body": 'Para maulit-ulit ko \'yung sarap',
        "caption": 'Pwede ba kitang i-video Para maulit-ulit ko \'yung sarap 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Alarm clock ka ba',
        "body": 'Kasi gusto kong gumising kasama ka at matapos sa iyo',
        "caption": 'Alarm clock ka ba Kasi gusto kong gumising kasama ka at matapos sa iyo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Your lips look lonely',
        "body": 'mind if I join them with mine',
        "caption": 'Your lips look lonely, mind if I join them with mine 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'d sit on your face',
        "body": 'but I don\'t want to break your concentration',
        "caption": 'I\'d sit on your face, but I don\'t want to break your concentration 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You look like a good',
        "body": 'reason to ruin my bed',
        "caption": 'You look like a good reason to ruin my bed 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Shower with me and',
        "body": 'let\'s save water…and lose control',
        "caption": 'Shower with me and let\'s save water…and lose control 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You must be chocolate',
        "body": '\'cause you melt every part of me',
        "caption": 'You must be chocolate, \'cause you melt every part of me 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s skip the talking',
        "body": 'and go straight to moaning',
        "caption": 'Let\'s skip the talking and go straight to moaning 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re magnetic',
        "body": 'pulling my clothes right off',
        "caption": 'You\'re magnetic, pulling my clothes right off 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Is that a snake or are',
        "body": 'you just excited to see me',
        "caption": 'Is that a snake or are you just excited to see me 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s make this night unforgettable… in',
        "body": 'ways the neighbors will complain about',
        "caption": 'Let\'s make this night unforgettable… in ways the neighbors will complain about 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You',
        "body": 'me, and a bottle of oil. Let\'s make that a slippery situation',
        "caption": 'You, me, and a bottle of oil. Let\'s make that a slippery situation 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Light a candle and watch',
        "body": 'how I blow… your mind',
        "caption": 'Light a candle and watch how I blow… your mind 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'d text you something dirty…',
        "body": 'but I\'d rather show you instead',
        "caption": 'I\'d text you something dirty… but I\'d rather show you instead 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'m not Cinderella',
        "body": 'but I\'d still leave something behind at your place',
        "caption": 'I\'m not Cinderella, but I\'d still leave something behind at your place 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s get messy and',
        "body": 'worry about the cleanup later',
        "caption": 'Let\'s get messy and worry about the cleanup later 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Here\'s to us',
        "body": 'naked, tangled, and too hot to handle',
        "caption": 'Here\'s to us, naked, tangled, and too hot to handle 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Are you my bed',
        "body": 'Because I can\'t wait to get inside you',
        "caption": 'Are you my bed Because I can\'t wait to get inside you 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Are you ice cream',
        "body": 'Because I want to lick you until you melt',
        "caption": 'Are you ice cream Because I want to lick you until you melt 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re sweeter than honey',
        "body": 'and I\'m ready to stick to you',
        "caption": 'You\'re sweeter than honey, and I\'m ready to stick to you 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I want to whisper things in',
        "body": 'your ear that\'ll make your thighs tremble',
        "caption": 'I want to whisper things in your ear that\'ll make your thighs tremble 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s skip small talk and',
        "body": 'head straight to your room',
        "caption": 'Let\'s skip small talk and head straight to your room 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re like dessert',
        "body": 'and I\'ve been craving something sweet all day',
        "caption": 'You\'re like dessert, and I\'ve been craving something sweet all day 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'ve got a body that attracts trouble… lucky me',
        "body": 'I love trouble',
        "caption": 'You\'ve got a body that attracts trouble… lucky me, I love trouble 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I want to write a naughty',
        "body": 'story with your body as every word',
        "caption": 'I want to write a naughty story with your body as every word 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You make',
        "body": 'my thoughts wet',
        "caption": 'You make my thoughts wet 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re too hot… we',
        "body": 'might just start a fire',
        "caption": 'You\'re too hot… we might just start a fire 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You make me feel like',
        "body": 'chocolate in the sun… melting',
        "caption": 'You make me feel like chocolate in the sun… melting 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let me unwrap you',
        "body": 'like my favorite gift',
        "caption": 'Let me unwrap you like my favorite gift 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I can think of a few',
        "body": 'things I want my tongue to do',
        "caption": 'I can think of a few things I want my tongue to do 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s lotion each other',
        "body": 'and see where it leads',
        "caption": 'Let\'s lotion each other and see where it leads 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You tie me up',
        "body": 'in ways I can\'t explain',
        "caption": 'You tie me up in ways I can\'t explain 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Are you free tonight or',
        "body": 'just in my dirty thoughts again',
        "caption": 'Are you free tonight or just in my dirty thoughts again 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'m drunk on your pics…',
        "body": 'now I need a taste',
        "caption": 'I\'m drunk on your pics… now I need a taste 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Send a pic',
        "body": 'I\'ll send a fantasy',
        "caption": 'Send a pic, I\'ll send a fantasy 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Your body\'s stuck in',
        "body": 'my mind on repeat',
        "caption": 'Your body\'s stuck in my mind on repeat 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I just imagined you moaning',
        "body": 'my name… should I keep going',
        "caption": 'I just imagined you moaning my name… should I keep going 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'What are you wearing No reason',
        "body": 'just want the mental image',
        "caption": 'What are you wearing No reason, just want the mental image 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You make texting NSFW',
        "body": 'in the best way',
        "caption": 'You make texting NSFW in the best way 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'My keyboard\'s hot… guess who',
        "body": 'made me type with one hand',
        "caption": 'My keyboard\'s hot… guess who made me type with one hand 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'d rather be dreaming of',
        "body": 'you… or dreaming with you',
        "caption": 'I\'d rather be dreaming of you… or dreaming with you 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Want to unlock my dirtiest',
        "body": 'thoughts Just say the word',
        "caption": 'Want to unlock my dirtiest thoughts Just say the word 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s turn this chat into a',
        "body": 'bedtime story… with no clothes involved',
        "caption": 'Let\'s turn this chat into a bedtime story… with no clothes involved 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I want to hear your voice…',
        "body": 'but only if you\'re out of breath',
        "caption": 'I want to hear your voice… but only if you\'re out of breath 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You make my thirst',
        "body": 'worse with every message',
        "caption": 'You make my thirst worse with every message 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'m low on energy',
        "body": 'recharge me with a little tease',
        "caption": 'I\'m low on energy, recharge me with a little tease 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Texting you',
        "body": 'feels like foreplay',
        "caption": 'Texting you feels like foreplay 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Can I be your lollipop',
        "body": 'You know what to do',
        "caption": 'Can I be your lollipop You know what to do 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re so cute',
        "body": 'I want to ruin you in the nicest way',
        "caption": 'You\'re so cute, I want to ruin you in the nicest way 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Are you made of sugar',
        "body": 'Because I\'m craving a taste',
        "caption": 'Are you made of sugar Because I\'m craving a taste 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Can I be your puppy',
        "body": 'So I can lick you everywhere',
        "caption": 'Can I be your puppy So I can lick you everywhere 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re wrapped so nicely… mind',
        "body": 'if I mess it up',
        "caption": 'You\'re wrapped so nicely… mind if I mess it up 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I want to plant kisses all',
        "body": 'over you and see what grows',
        "caption": 'I want to plant kisses all over you and see what grows 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re cuddly but',
        "body": 'dangerous to my self-control',
        "caption": 'You\'re cuddly but dangerous to my self-control 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re magical… especially the',
        "body": 'way you make me feel',
        "caption": 'You\'re magical… especially the way you make me feel 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'d follow you to the bedroom like',
        "body": 'a rainbow to its pot of gold',
        "caption": 'I\'d follow you to the bedroom like a rainbow to its pot of gold 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let me be your',
        "body": 'thorn… sharp and deep',
        "caption": 'Let me be your thorn… sharp and deep 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re too sweet',
        "body": 'I need to dirty you up',
        "caption": 'You\'re too sweet, I need to dirty you up 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'That peach deserves',
        "body": 'attention and I volunteer',
        "caption": 'That peach deserves attention and I volunteer 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s write love letters',
        "body": 'on each other\'s skin',
        "caption": 'Let\'s write love letters on each other\'s skin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You got honey',
        "body": 'I got the spoon',
        "caption": 'You got honey I got the spoon 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re the reason my',
        "body": 'bed feels too empty',
        "caption": 'You\'re the reason my bed feels too empty 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re mine',
        "body": 'now let me prove it all night',
        "caption": 'You\'re mine, now let me prove it all night 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'m not jealous',
        "body": 'but only I get to see you like this',
        "caption": 'I\'m not jealous, but only I get to see you like this 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s turn the living',
        "body": 'room into a love room',
        "caption": 'Let\'s turn the living room into a love room 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I want to kiss every',
        "body": 'inch of you starting now',
        "caption": 'I want to kiss every inch of you starting now 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re my favorite hobby',
        "body": 'and my filthiest thought',
        "caption": 'You\'re my favorite hobby and my filthiest thought 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Your brain is sexy',
        "body": 'but your body\'s got me distracted',
        "caption": 'Your brain is sexy, but your body\'s got me distracted 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Laundry can wait…',
        "body": 'but you can\'t',
        "caption": 'Laundry can wait… but you can\'t 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'ll draw you a',
        "body": 'bath… then join you',
        "caption": 'I\'ll draw you a bath… then join you 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Keep sending those pics.',
        "body": 'My thoughts are getting dirtier',
        "caption": 'Keep sending those pics. My thoughts are getting dirtier 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s waste time',
        "body": 'being naked and loud',
        "caption": 'Let\'s waste time being naked and loud 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You and pizza are',
        "body": 'my two cravings tonight',
        "caption": 'You and pizza are my two cravings tonight 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'d help you undress',
        "body": 'but I might rip something',
        "caption": 'I\'d help you undress, but I might rip something 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You\'re not just my',
        "body": 'girl… you\'re my obsession',
        "caption": 'You\'re not just my girl… you\'re my obsession 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I see stars when I look',
        "body": 'at you… especially when you\'re on top',
        "caption": 'I see stars when I look at you… especially when you\'re on top 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Home is wherever',
        "body": 'I can touch you',
        "caption": 'Home is wherever I can touch you 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Mind if I',
        "body": 'scrub you… everywhere',
        "caption": 'Mind if I scrub you… everywhere 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'The water\'s hot',
        "body": 'but you\'re hotter',
        "caption": 'The water\'s hot, but you\'re hotter 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s soap each other up',
        "body": 'and see where it leads',
        "caption": 'Let\'s soap each other up and see where it leads 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I brought bubbles…',
        "body": 'and some dirty thoughts',
        "caption": 'I brought bubbles… and some dirty thoughts 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Care for a',
        "body": 'soak and a stroke',
        "caption": 'Care for a soak and a stroke 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'I\'ll rinse',
        "body": 'you off… slowly',
        "caption": 'I\'ll rinse you off… slowly 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Lights down',
        "body": 'candles lit, and only skin to touch',
        "caption": 'Lights down, candles lit, and only skin to touch 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Bath with you is',
        "body": 'my therapy with benefits',
        "caption": 'Bath with you is my therapy with benefits 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let me explore every',
        "body": 'inch like a treasure map',
        "caption": 'Let me explore every inch like a treasure map 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'That tub isn\'t the only',
        "body": 'thing I want to get wet',
        "caption": 'That tub isn\'t the only thing I want to get wet 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Your back looks like',
        "body": 'it needs my hands',
        "caption": 'Your back looks like it needs my hands 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s make waves…',
        "body": 'and some moans',
        "caption": 'Let\'s make waves… and some moans 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'The salt in this bath isn\'t',
        "body": 'the only thing making me tingle',
        "caption": 'The salt in this bath isn\'t the only thing making me tingle 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Let\'s boil the',
        "body": 'water with our bodies',
        "caption": 'Let\'s boil the water with our bodies 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'You bring the heat',
        "body": 'I\'ll bring the soap',
        "caption": 'You bring the heat, I\'ll bring the soap 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto mo ba ng kape kasi',
        "body": 'ikaw ang nagpapagising sa bawat umaga ko',
        "caption": 'Gusto mo ba ng kape kasi ikaw ang nagpapagising sa bawat umaga ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Mainit ba dito o ikaw',
        "body": 'lang talaga ang nagpapainit sa akin',
        "caption": 'Mainit ba dito o ikaw lang talaga ang nagpapainit sa akin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang i-download',
        "body": 'para lagi kitang ma-open',
        "caption": 'Pwede ba kitang i-download para lagi kitang ma-open 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Parang signal ka nawawala ka pag',
        "body": 'kailangan kita lalo na sa gabi',
        "caption": 'Parang signal ka nawawala ka pag kailangan kita lalo na sa gabi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kiss ka ba kasi hindi',
        "body": 'kita makuha kahit anong pilit ko',
        "caption": 'Kiss ka ba kasi hindi kita makuha kahit anong pilit ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tol eraser ka ba kasi natatanggal mo',
        "body": 'lahat ng stress ko pag nakikita kita',
        "caption": 'Tol eraser ka ba kasi natatanggal mo lahat ng stress ko pag nakikita kita 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kutsara ka ba kasi bagay',
        "body": 'kang ipasok sa bibig ko',
        "caption": 'Kutsara ka ba kasi bagay kang ipasok sa bibig ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ice cream ka ba kasi',
        "body": 'gusto kitang dilaan hanggang matunaw',
        "caption": 'Ice cream ka ba kasi gusto kitang dilaan hanggang matunaw 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Cake ka ba kasi',
        "body": 'ang sarap mong slice-in',
        "caption": 'Cake ka ba kasi ang sarap mong slice-in 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Electric fan ka ba kasi',
        "body": 'gusto kong nasa harap mo lagi',
        "caption": 'Electric fan ka ba kasi gusto kong nasa harap mo lagi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Mantika ka ba kasi ang',
        "body": 'dulas mong hawakan sa isip ko',
        "caption": 'Mantika ka ba kasi ang dulas mong hawakan sa isip ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kumot ka ba kasi',
        "body": 'gusto kitang yakapin buong gabi',
        "caption": 'Kumot ka ba kasi gusto kitang yakapin buong gabi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Payong ka ba kasi ikaw',
        "body": 'ang sagot sa init ko',
        "caption": 'Payong ka ba kasi ikaw ang sagot sa init ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kamatis ka ba kasi',
        "body": 'gusto kong lamutakin ka',
        "caption": 'Kamatis ka ba kasi gusto kong lamutakin ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Panyo ka ba kasi ikaw',
        "body": 'gusto kong hawakan pag pinapawisan ako',
        "caption": 'Panyo ka ba kasi ikaw gusto kong hawakan pag pinapawisan ako 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ikaw ba ang gabi kasi',
        "body": 'pag naaalala kita tumitigas ako',
        "caption": 'Ikaw ba ang gabi kasi pag naaalala kita tumitigas ako 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang akyatin kasi',
        "body": 'ang taas ng libog ko sayo',
        "caption": 'Pwede ba kitang akyatin kasi ang taas ng libog ko sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hinog ka na ba kasi',
        "body": 'ready na akong pitasin ka',
        "caption": 'Hinog ka na ba kasi ready na akong pitasin ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto mo ba ng massage kasi',
        "body": 'ready ang kamay ko maging marumi',
        "caption": 'Gusto mo ba ng massage kasi ready ang kamay ko maging marumi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Bed sheet ka ba kasi',
        "body": 'gusto kong magkulong kasama ka',
        "caption": 'Bed sheet ka ba kasi gusto kong magkulong kasama ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Para kang elevator',
        "body": 'gusto kitang sakyan paulit-ulit',
        "caption": 'Para kang elevator gusto kitang sakyan paulit-ulit 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Dila ka ba kasi',
        "body": 'nasa utak kita buong araw',
        "caption": 'Dila ka ba kasi nasa utak kita buong araw 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pillow ka ba kasi',
        "body": 'gusto kong sumubsob sayo',
        "caption": 'Pillow ka ba kasi gusto kong sumubsob sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sabon ka ba kasi',
        "body": 'gusto kong dumulas kasama ka',
        "caption": 'Sabon ka ba kasi gusto kong dumulas kasama ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Shower ka ba',
        "body": 'gusto kong sabayan ka',
        "caption": 'Shower ka ba gusto kong sabayan ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Music ka ba gusto',
        "body": 'kitang patugtugin hanggang sumigaw ka',
        "caption": 'Music ka ba gusto kitang patugtugin hanggang sumigaw ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Chocolate ka ba kasi',
        "body": 'gusto kong matikman ka',
        "caption": 'Chocolate ka ba kasi gusto kong matikman ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Netflix ka ba kasi',
        "body": 'gusto kong all-night session sayo',
        "caption": 'Netflix ka ba kasi gusto kong all-night session sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Bedsheet ka ba gusto',
        "body": 'kitang gumulong kasama ko',
        "caption": 'Bedsheet ka ba gusto kitang gumulong kasama ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Init ka ba kasi pag',
        "body": 'lumalapit ka nag-iiba ugali ko',
        "caption": 'Init ka ba kasi pag lumalapit ka nag-iiba ugali ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang ihiga',
        "body": 'kahit wala pa tayong relasyon',
        "caption": 'Pwede ba kitang ihiga kahit wala pa tayong relasyon 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Natutunan ko ba ang math',
        "body": 'kasi gusto kong i-divide legs mo',
        "caption": 'Natutunan ko ba ang math kasi gusto kong i-divide legs mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tag-init ba kasi',
        "body": 'gusto kong maghubad ka',
        "caption": 'Tag-init ba kasi gusto kong maghubad ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Baboy ka ba kasi',
        "body": 'gusto kitang i-roast at i-todo',
        "caption": 'Baboy ka ba kasi gusto kitang i-roast at i-todo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Dila mo ba',
        "body": 'malambot try natin',
        "caption": 'Dila mo ba malambot try natin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Juice ka ba',
        "body": 'gusto kong higupin ka',
        "caption": 'Juice ka ba gusto kong higupin ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Saging ka ba kasi',
        "body": 'bagay ka sa kamay ko',
        "caption": 'Saging ka ba kasi bagay ka sa kamay ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Puno ka ba kasi',
        "body": 'gusto kong umakyat sayo',
        "caption": 'Puno ka ba kasi gusto kong umakyat sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Palette knife ka ba',
        "body": 'kasi ang sarap mong ipahid',
        "caption": 'Palette knife ka ba kasi ang sarap mong ipahid 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Short ka ba',
        "body": 'gusto kong hubarin ka',
        "caption": 'Short ka ba gusto kong hubarin ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Timplado ka ba kasi',
        "body": 'swak na swak ka sakin',
        "caption": 'Timplado ka ba kasi swak na swak ka sakin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sabaw ka ba kasi',
        "body": 'gusto kong isubo lahat',
        "caption": 'Sabaw ka ba kasi gusto kong isubo lahat 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tubig ka ba kasi',
        "body": 'gusto kong papakin ka',
        "caption": 'Tubig ka ba kasi gusto kong papakin ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Cake frosting ka ba kasi',
        "body": 'gusto kong tanggalin gamit dila ko',
        "caption": 'Cake frosting ka ba kasi gusto kong tanggalin gamit dila ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Paprika ka ba kasi ang',
        "body": 'anghang mo sa utak ko',
        "caption": 'Paprika ka ba kasi ang anghang mo sa utak ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang i-kiss hanggang',
        "body": 'mawala pangalan mo sa isip ko',
        "caption": 'Pwede ba kitang i-kiss hanggang mawala pangalan mo sa isip ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ikaw yung tipo ng init',
        "body": 'na hindi ko kaya pigilan',
        "caption": 'Ikaw yung tipo ng init na hindi ko kaya pigilan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang sarap mo sigurong',
        "body": 'yakapin habang walang suot',
        "caption": 'Ang sarap mo sigurong yakapin habang walang suot 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Labi mo ba made',
        "body": 'of sugar gusto kong matikman',
        "caption": 'Labi mo ba made of sugar gusto kong matikman 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang maging',
        "body": 'unan mo kamay ko',
        "caption": 'Pwede bang maging unan mo kamay ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung bibigyan kita ng',
        "body": 'massage handa ka bang umungol',
        "caption": 'Kung bibigyan kita ng massage handa ka bang umungol 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sipa ka ba hindi',
        "body": 'kita masalo sa utak ko',
        "caption": 'Sipa ka ba hindi kita masalo sa utak ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ka bang',
        "body": 'maging dessert ko',
        "caption": 'Pwede ka bang maging dessert ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hips mo ba',
        "body": 'magnet kasi hinahatak ako',
        "caption": 'Hips mo ba magnet kasi hinahatak ako 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang sumiksik',
        "body": 'sayo buong gabi',
        "caption": 'Pwede bang sumiksik sayo buong gabi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kapag yumakap ako sayo',
        "body": 'hindi na kita bibitawan',
        "caption": 'Kapag yumakap ako sayo hindi na kita bibitawan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang sayo ako',
        "body": 'sumandal wala kang bra',
        "caption": 'Pwede bang sayo ako sumandal wala kang bra 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang sarap mo sigurong',
        "body": 'kasama sa malamig na gabi',
        "caption": 'Ang sarap mo sigurong kasama sa malamig na gabi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Parang unan ka',
        "body": 'sobrang gusto kitang yakapin',
        "caption": 'Parang unan ka sobrang gusto kitang yakapin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tingin mo ba kaya',
        "body": 'kong patunayan gaano kita gusto',
        "caption": 'Tingin mo ba kaya kong patunayan gaano kita gusto 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang suotin',
        "body": 'kahit hindi ka kasya sakin',
        "caption": 'Pwede ba kitang suotin kahit hindi ka kasya sakin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ikaw ba ang oras',
        "body": 'kasi tinatanggal mo pasensya ko',
        "caption": 'Ikaw ba ang oras kasi tinatanggal mo pasensya ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pader ka ba gusto',
        "body": 'kong idikit sarili ko sayo',
        "caption": 'Pader ka ba gusto kong idikit sarili ko sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Banig ka ba dahil',
        "body": 'gusto kong humiga tayo',
        "caption": 'Banig ka ba dahil gusto kong humiga tayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Dila mo ba',
        "body": 'ready for service',
        "caption": 'Dila mo ba ready for service 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang',
        "body": 'kalmutin kapag na-excite ako',
        "caption": 'Pwede ba kitang kalmutin kapag na-excite ako 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Punda ka ba gusto',
        "body": 'kong ipasok mukha ko sayo',
        "caption": 'Punda ka ba gusto kong ipasok mukha ko sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kutsilyo ka ba kasi gusto',
        "body": 'mo akong saktan sa libog',
        "caption": 'Kutsilyo ka ba kasi gusto mo akong saktan sa libog 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Candy ka ba',
        "body": 'gusto kong i-lollipop ka',
        "caption": 'Candy ka ba gusto kong i-lollipop ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sabong ka ba',
        "body": 'gusto kong basain ka',
        "caption": 'Sabong ka ba gusto kong basain ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Mantika ka ba ang',
        "body": 'dulas mo sa isip ko',
        "caption": 'Mantika ka ba ang dulas mo sa isip ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang ikaw na',
        "body": 'lang init ko ngayon',
        "caption": 'Pwede bang ikaw na lang init ko ngayon 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Lamesa ka ba kasi',
        "body": 'gusto kong ihiga ka',
        "caption": 'Lamesa ka ba kasi gusto kong ihiga ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kumot ka ba para',
        "body": 'matakpan kita habang gumagalaw tayo',
        "caption": 'Kumot ka ba para matakpan kita habang gumagalaw tayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tubig ka ba gusto',
        "body": 'kitang inumin ng diretsuhan',
        "caption": 'Tubig ka ba gusto kitang inumin ng diretsuhan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang',
        "body": 'pasuotin ng wala',
        "caption": 'Pwede ba kitang pasuotin ng wala 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Legs mo ba',
        "body": 'algebra gusto kong i-open',
        "caption": 'Legs mo ba algebra gusto kong i-open 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Masarap ka sigurong',
        "body": 'sabayan sa pawis',
        "caption": 'Masarap ka sigurong sabayan sa pawis 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang hawakan',
        "body": 'kita kahit saan',
        "caption": 'Pwede bang hawakan kita kahit saan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Bibig mo ba',
        "body": 'elevator gusto kong gamitin',
        "caption": 'Bibig mo ba elevator gusto kong gamitin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba',
        "body": 'kitang sakyan paulit-ulit',
        "caption": 'Pwede ba kitang sakyan paulit-ulit 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Dila ko ready na',
        "body": 'ikaw na lang kulang',
        "caption": 'Dila ko ready na ikaw na lang kulang 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang tikman',
        "body": 'kita nang hindi nag-aalinlangan',
        "caption": 'Pwede bang tikman kita nang hindi nag-aalinlangan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ko bang hawakan legs',
        "body": 'mo hanggang umangat skirt mo',
        "caption": 'Pwede ko bang hawakan legs mo hanggang umangat skirt mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang dalhin',
        "body": 'sa kwarto kahit maaga pa',
        "caption": 'Pwede ba kitang dalhin sa kwarto kahit maaga pa 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Labi mo ba',
        "body": 'reusable gusto kong balik-balikan',
        "caption": 'Labi mo ba reusable gusto kong balik-balikan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gabi ka ba',
        "body": 'gusto kitang pagpagurin',
        "caption": 'Gabi ka ba gusto kitang pagpagurin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Skin mo ang smooth',
        "body": 'parang gusto kong dumulas dyan',
        "caption": 'Skin mo ang smooth parang gusto kong dumulas dyan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang ako',
        "body": 'muna hawakan mo ngayon',
        "caption": 'Pwede bang ako muna hawakan mo ngayon 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang sarap mo sigurong',
        "body": 'i-wrap ng kamay ko',
        "caption": 'Ang sarap mo sigurong i-wrap ng kamay ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gising ka pa may',
        "body": 'gusto akong iparamdam sayo',
        "caption": 'Gising ka pa may gusto akong iparamdam sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung nasa tabi kita',
        "body": 'ngayon wala ka nang suot',
        "caption": 'Kung nasa tabi kita ngayon wala ka nang suot 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sa isip ko ikaw',
        "body": 'ang hinahawakan ko ngayon',
        "caption": 'Sa isip ko ikaw ang hinahawakan ko ngayon 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Miss mo ba lips ko',
        "body": 'ako miss ko na lips mo',
        "caption": 'Miss mo ba lips ko ako miss ko na lips mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'May tanong ako… ready',
        "body": 'ka na ba mabasa',
        "caption": 'May tanong ako… ready ka na ba mabasa 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung nandito ka ngayon nakahiga',
        "body": 'ka na sa dibdib ko',
        "caption": 'Kung nandito ka ngayon nakahiga ka na sa dibdib ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Iniisip mo rin',
        "body": 'ba yung iniisip ko',
        "caption": 'Iniisip mo rin ba yung iniisip ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Nagvibrate phone mo gusto mo',
        "body": 'next time ako na magpavibrate sayo',
        "caption": 'Nagvibrate phone mo gusto mo next time ako na magpavibrate sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang sabihin ko sayo',
        "body": 'lahat ng gusto kong gawin sayo',
        "caption": 'Pwede bang sabihin ko sayo lahat ng gusto kong gawin sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Safe ba DM mo',
        "body": 'para sa maruruming thoughts ko',
        "caption": 'Safe ba DM mo para sa maruruming thoughts ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pillow ka ba gusto',
        "body": 'kong yakapin buong gabi',
        "caption": 'Pillow ka ba gusto kong yakapin buong gabi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Kung video call tayo',
        "body": 'hindi ka tatagal nakadamit',
        "caption": 'Kung video call tayo hindi ka tatagal nakadamit 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ka ba',
        "body": 'ngayon need kita',
        "caption": 'Pwede ka ba ngayon need kita 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto mo ng goodnight',
        "body": 'kiss or bad night kiss',
        "caption": 'Gusto mo ng goodnight kiss or bad night kiss 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Wag ka muna matulog',
        "body": 'may init pa tayong tatapusin',
        "caption": 'Wag ka muna matulog may init pa tayong tatapusin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang hawakan',
        "body": 'ko yang bawal',
        "caption": 'Pwede bang hawakan ko yang bawal 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Malibog ka ba',
        "body": 'wag ka mag-deny',
        "caption": 'Malibog ka ba wag ka mag-deny 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang kainin',
        "body": 'kahit busog na ako',
        "caption": 'Pwede ba kitang kainin kahit busog na ako 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Dede mo ba',
        "body": 'soft gusto kong i-check',
        "caption": 'Dede mo ba soft gusto kong i-check 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ka bang',
        "body": 'i-press sa pader',
        "caption": 'Pwede ka bang i-press sa pader 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Shorts mo ba',
        "body": 'manipis gusto kong tanggalin',
        "caption": 'Shorts mo ba manipis gusto kong tanggalin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang ako',
        "body": 'unang hawakan mo',
        "caption": 'Pwede bang ako unang hawakan mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Siksik ka ba',
        "body": 'gusto kong pasukin',
        "caption": 'Siksik ka ba gusto kong pasukin 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Baby oil ka',
        "body": 'ba gusto kitang ipahid',
        "caption": 'Baby oil ka ba gusto kitang ipahid 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede',
        "body": 'kitang dila-dilaan',
        "caption": 'Pwede kitang dila-dilaan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto mo ba',
        "body": 'ng malalim na hugs',
        "caption": 'Gusto mo ba ng malalim na hugs 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sensya na ha',
        "body": 'pero ang hot mo',
        "caption": 'Sensya na ha pero ang hot mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang',
        "body": 'tikman kahit bawal',
        "caption": 'Pwede ba kitang tikman kahit bawal 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang matulog ako',
        "body": 'sa loob ng yakap mo',
        "caption": 'Pwede bang matulog ako sa loob ng yakap mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Di kita iniisip… binabastos',
        "body": 'kita sa utak ko',
        "caption": 'Di kita iniisip… binabastos kita sa utak ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ikaw ba ang init ng',
        "body": 'araw kasi napapa-hubad mo ko',
        "caption": 'Ikaw ba ang init ng araw kasi napapa-hubad mo ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang pahiram ng katawan',
        "body": 'mo may gagawin lang ako',
        "caption": 'Pwede bang pahiram ng katawan mo may gagawin lang ako 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Lakas mo maka-libog parang joke lang',
        "body": 'pero totoo',
        "caption": 'Lakas mo maka-libog parang joke lang pero totoo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang sabayan',
        "body": 'sa kalokohan at kalibugan',
        "caption": 'Pwede ba kitang sabayan sa kalokohan at kalibugan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang bango mo parang',
        "body": 'gusto kong dilaan ka',
        "caption": 'Ang bango mo parang gusto kong dilaan ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'May lisensya ka',
        "body": 'ba sa pang-aakit',
        "caption": 'May lisensya ka ba sa pang-aakit 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kita i-uwi',
        "body": 'kahit hindi ka nagpaalam',
        "caption": 'Pwede ba kita i-uwi kahit hindi ka nagpaalam 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ikaw ang dahilan bakit',
        "body": 'gusto ko matulog ng naka-hubad',
        "caption": 'Ikaw ang dahilan bakit gusto ko matulog ng naka-hubad 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kita',
        "body": 'hawakan ng konti',
        "caption": 'Pwede ba kita hawakan ng konti 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Hinga ka ba kasi nawawalan',
        "body": 'ako nyan pag kasama kita',
        "caption": 'Hinga ka ba kasi nawawalan ako nyan pag kasama kita 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Tigilan mo nga',
        "body": 'pagiging hot mo',
        "caption": 'Tigilan mo nga pagiging hot mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang ikaw na',
        "body": 'lang ang gabi ko',
        "caption": 'Pwede bang ikaw na lang ang gabi ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Natatawa ako kasi',
        "body": 'ang libog ko sayo',
        "caption": 'Natatawa ako kasi ang libog ko sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede kitang tikman hindi',
        "body": 'ka naman magrereklamo diba',
        "caption": 'Pwede kitang tikman hindi ka naman magrereklamo diba 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Cute mo',
        "body": 'pero mas cute pag walang suot',
        "caption": 'Cute mo pero mas cute pag walang suot 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto kong maramdaman bawat',
        "body": 'hinga mo sa leeg ko',
        "caption": 'Gusto kong maramdaman bawat hinga mo sa leeg ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang',
        "body": 'ihiga ngayon mismo',
        "caption": 'Pwede ba kitang ihiga ngayon mismo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Sabihin mo lang oo at',
        "body": 'wala kang suot sa harap ko',
        "caption": 'Sabihin mo lang oo at wala kang suot sa harap ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang sarap mo',
        "body": 'sigurong hawakan sa dilim',
        "caption": 'Ang sarap mo sigurong hawakan sa dilim 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto kong dumulas',
        "body": 'sa katawan mo',
        "caption": 'Gusto kong dumulas sa katawan mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang dilaan',
        "body": 'ko bawat parte mo',
        "caption": 'Pwede bang dilaan ko bawat parte mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto kong ipikit mo mata mo',
        "body": 'at isipin ako sa katawan mo',
        "caption": 'Gusto kong ipikit mo mata mo at isipin ako sa katawan mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede bang ilapit mo',
        "body": 'yung labi mo dito',
        "caption": 'Pwede bang ilapit mo yung labi mo dito 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto kitang',
        "body": 'pasayawin sa kama',
        "caption": 'Gusto kitang pasayawin sa kama 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Mainit ka ba',
        "body": 'kasi nag-iinit ako',
        "caption": 'Mainit ka ba kasi nag-iinit ako 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto kong pakinggan boses',
        "body": 'mo habang nilalambing kita',
        "caption": 'Gusto kong pakinggan boses mo habang nilalambing kita 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede ba kitang',
        "body": 'lapitan hanggang manginig ka',
        "caption": 'Pwede ba kitang lapitan hanggang manginig ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Gusto kong halikan',
        "body": 'bawat pulgada mo',
        "caption": 'Gusto kong halikan bawat pulgada mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Pwede naa bang',
        "body": 'simulan ang iniisip ko',
        "caption": 'Pwede naa bang simulan ang iniisip ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    {
        "header": 'Ang sarap mo',
        "body": 'sigurong samahan buong gabi',
        "caption": 'Ang sarap mo sigurong samahan buong gabi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
    # ── ADD YOUR NEW JOKES BELOW THIS LINE ────────────────────────────────────
    # Copy the format above. Always add at the BOTTOM. Never rearrange!
    # {
    #     "header": "your first line here,",
    #     "body": "your second line here",
    #     "caption": "full joke text here \U0001f60f\n\n#flirty #taglish #funnyfilipino #reels",
    # },
]


# ══════════════════════════════════════════════════════════════════════════════
# 2. JOKE PICKER — gets next joke in order, saves progress
# ══════════════════════════════════════════════════════════════════════════════

def _load_progress() -> dict:
    """Load the shared progress JSON (or return empty dict on failure)."""
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text())
        except Exception:
            pass
    return {}

def _save_progress(data: dict) -> None:
    """Persist the shared progress JSON."""
    PROGRESS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def get_next_joke() -> dict:
    """Returns the next joke in order. Loops back to start when list ends."""
    data       = _load_progress()
    last_index = int(data.get("last_index", -1))
    next_index = (last_index + 1) % len(JOKES)
    joke       = JOKES[next_index]

    data["last_index"]  = next_index
    data["last_header"] = joke["header"]
    _save_progress(data)

    print(f"[Joke] Index {next_index + 1}/{len(JOKES)}: {joke['header']}")
    return joke


# ══════════════════════════════════════════════════════════════════════════════
# 3. RENDER TEXT PNG
# ══════════════════════════════════════════════════════════════════════════════

FONT_SIZE_HEADER    = 55
FONT_SIZE_BODY      = 55
STROKE_WIDTH_HEADER = 5
STROKE_WIDTH_BODY   = 5


def render_text_png(header: str, body: str, width: int, height: int, output_png: Path) -> None:
    import math
    from PIL import Image, ImageDraw, ImageFont

    img  = Image.new("RGBA", (width, height), (0, 0, 0, 0))
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
                return ImageFont.truetype(p, size)
        import urllib.request
        fallback = Path("/tmp/meme_font.ttf")
        if not fallback.exists():
            urllib.request.urlretrieve(
                "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Bold.ttf",
                str(fallback),
            )
        return ImageFont.truetype(str(fallback), size)

    font_header = load_font(bold_candidates,   FONT_SIZE_HEADER)
    font_body   = load_font(italic_candidates, FONT_SIZE_BODY)

    WHITE = (255, 255, 255, 255)
    BLACK = (0,   0,   0,   255)

    def wrap_px(text, font, max_width):
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = (current + " " + word).strip()
            if draw.textlength(test, font=font) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return "\n".join(lines)

    def draw_stroked(pos, text, font, fill, stroke_col, stroke_w, spacing=14):
        x, y = pos
        for angle in range(0, 360, 12):
            rad = math.radians(angle)
            ox  = int(math.cos(rad) * stroke_w)
            oy  = int(math.sin(rad) * stroke_w)
            draw.multiline_text((x + ox, y + oy), text, font=font,
                                fill=stroke_col, spacing=spacing, align="center")
        draw.multiline_text((x, y), text, font=font,
                            fill=fill, spacing=spacing, align="center")

    pad   = int(width * 0.06)
    max_w = width - pad * 2

    wrapped_header = wrap_px(header, font_header, max_w)
    wrapped_body   = wrap_px(body,   font_body,   max_w)

    hb = draw.multiline_textbbox((0, 0), wrapped_header, font=font_header, spacing=10)
    bb = draw.multiline_textbbox((0, 0), wrapped_body,   font=font_body,   spacing=14)
    h_w, h_h = hb[2] - hb[0], hb[3] - hb[1]
    b_w, b_h = bb[2] - bb[0], bb[3] - bb[1]
    gap      = int(FONT_SIZE_HEADER * 0.5)
    total_h  = h_h + gap + b_h

    top_pad = 200
    start_y = top_pad
    hx = (width - h_w) // 2
    bx = (width - b_w) // 2
    by = start_y + h_h + gap

    draw_stroked((hx, start_y), wrapped_header, font_header,
                 WHITE, BLACK, STROKE_WIDTH_HEADER, spacing=10)
    draw_stroked((bx, by), wrapped_body, font_body,
                 WHITE, BLACK, STROKE_WIDTH_BODY, spacing=14)

    img.save(str(output_png))
    print(f"[Text PNG] Saved -> {output_png}")


# ══════════════════════════════════════════════════════════════════════════════
# 4. VIDEO ASSEMBLY
# ══════════════════════════════════════════════════════════════════════════════

def pick_next_video() -> Path:
    """Returns videos in ascending filename order, looping back after the last.
    Tracks the last-played filename so adding new videos never breaks the sequence."""
    exts  = {".mp4", ".mov", ".webm", ".avi"}
    files = sorted(f for f in VIDEOS_DIR.iterdir() if f.suffix.lower() in exts)
    if not files:
        raise FileNotFoundError(f"No video files found in {VIDEOS_DIR}")

    data            = _load_progress()
    last_video_name = data.get("last_video_name", "")

    # Find where we left off by filename; default to -1 (start from first) if not found
    names = [f.name for f in files]
    last_pos = names.index(last_video_name) if last_video_name in names else -1
    next_pos = (last_pos + 1) % len(files)
    chosen   = files[next_pos]

    data["last_video_name"] = chosen.name
    _save_progress(data)

    print(f"[Video] Picked ({next_pos + 1}/{len(files)}): {chosen.name}")
    return chosen


def get_video_info(video: Path) -> tuple[float, int, int]:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True
    )
    duration = float(r.stdout.strip()) if r.stdout.strip() else 59.0
    r2 = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(video)],
        capture_output=True, text=True
    )
    try:
        w, h = map(int, r2.stdout.strip().split(","))
    except Exception:
        w, h = 1080, 1920
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
    video_file           = pick_next_video()
    duration, vid_w, vid_h = get_video_info(video_file)
    video_has_audio      = has_audio(video_file)

    print(f"[Video] {vid_w}x{vid_h} | {duration:.1f}s | audio={video_has_audio}")

    text_png = OUTPUT_DIR / "text_overlay.png"
    render_text_png(header, body, TARGET_W, TARGET_H, text_png)

    # Scale source video to fill 9:16 portrait (zoom-to-fill, crop excess)
    # This prevents black bars on mobile Reels/Shorts
    filter_complex = (
        "[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
        "crop={w}:{h}[vid];"
        "[1:v]scale={w}:{h}[txt];"
        "[vid][txt]overlay=0:0[vout]"
    ).format(w=TARGET_W, h=TARGET_H)

    audio_args = ["-map", "[vout]"]
    if video_has_audio:
        filter_complex += ";[0:a]acopy[aout]"
        audio_args += ["-map", "[aout]", "-c:a", "aac", "-b:a", "128k"]
    else:
        audio_args += ["-an"]

    cmd = [
        "ffmpeg", "-y",
        "-i",  str(video_file),
        "-i",  str(text_png),
        "-filter_complex", filter_complex,
        *audio_args,
        "-t",        str(duration),
        "-c:v",      "libx264",
        "-preset",   "fast",
        "-crf",      "23",
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
    file_size = video_path.stat().st_size
    base_url  = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/video_reels"

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
    print("  Viral Video Maker 😏")
    print("=" * 60)

    print("\n[Step 1] Getting next joke…")
    joke    = get_next_joke()
    header  = joke["header"]
    body    = joke["body"]
    caption = joke["caption"]
    print(f"  Header:  {header}")
    print(f"  Body:    {body}")
    print(f"  Caption: {caption}\n")

    print("[Step 2] Building video with FFmpeg…")
    build_video(header, body, OUTPUT_VIDEO)

    print("[Step 3] Posting to Facebook Reels…")
    post_id = post_to_facebook_reel(OUTPUT_VIDEO, caption)
    print(f"\n✅ Published! Video ID: {post_id}")


if __name__ == "__main__":
    main()
