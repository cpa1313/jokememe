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

def get_next_joke() -> dict:
    """Returns the next joke in order. Loops back to start when list ends."""
    # Load progress
    if PROGRESS_FILE.exists():
        try:
            data      = json.loads(PROGRESS_FILE.read_text())
            last_index = int(data.get("last_index", -1))
        except Exception:
            last_index = -1
    else:
        last_index = -1

    next_index = (last_index + 1) % len(JOKES)
    joke       = JOKES[next_index]

    # Save progress
    PROGRESS_FILE.write_text(json.dumps({
        "last_index": next_index,
        "last_header": joke["header"],
    }, ensure_ascii=False, indent=2))

    print(f"[Joke] Index {next_index + 1}/{len(JOKES)}: {joke['header']}")
    return joke


# ══════════════════════════════════════════════════════════════════════════════
# 3. RENDER TEXT PNG
# ══════════════════════════════════════════════════════════════════════════════

FONT_SIZE_HEADER    = 38
FONT_SIZE_BODY      = 38
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

    top_pad = int(height * 0.06)
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

def pick_random_video() -> Path:
    exts  = {".mp4", ".mov", ".webm", ".avi"}
    files = [f for f in VIDEOS_DIR.iterdir() if f.suffix.lower() in exts]
    if not files:
        raise FileNotFoundError(f"No video files found in {VIDEOS_DIR}")
    chosen = random.choice(files)
    print(f"[Video] Picked: {chosen}")
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
    video_file           = pick_random_video()
    duration, vid_w, vid_h = get_video_info(video_file)
    video_has_audio      = has_audio(video_file)

    print(f"[Video] {vid_w}x{vid_h} | {duration:.1f}s | audio={video_has_audio}")

    text_png = OUTPUT_DIR / "text_overlay.png"
    render_text_png(header, body, vid_w, vid_h, text_png)

    filter_complex = (
        "[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
        "pad={w}:{h}:(ow-iw)/2:(oh-ih)/2[vid];"
        "[1:v]scale={w}:{h}[txt];"
        "[vid][txt]overlay=0:0[vout]"
    ).format(w=vid_w, h=vid_h)

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
