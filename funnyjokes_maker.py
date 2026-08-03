#!/usr/bin/env python3
"""Funny Jokes Reel Maker — creates and publishes one narrated Facebook Reel per run.

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
PROGRESS_FILE = ROOT / "funnyjokes_progress.json"
TARGET_W, TARGET_H = 1080, 1920
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}
VOICE = os.environ.get("REEL_VOICE", "fil-PH-AngeloNeural")

# Each joke is rendered as: hook → setup → punchline. Add future jokes at the end.
# Jokes imported exactly from viralvideo_maker.py. Add future entries at the end.
JOKES = [
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
        "header": 'Pag ikaw ang kasama ko… Tinatamad na ako…',
        "body": 'Kase ang sarap magpahinga sa piling mo.',
        "caption": 'Pag ikaw ang kasama ko… Tinatamad na ako… Kase ang sarap magpahinga sa piling mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
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
        "header": 'andami mo namang babae!',
        "body": 'sino ba talaga laman ng puso mo? Ewan ko! ikaw may-ari nito tapos ako tatanungin mo.',
        "caption": 'andami mo namang babae! sino ba talaga laman ng puso mo? Ewan ko! ikaw may-ari nito tapos ako tatanungin mo. 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Lips mo ba yan o dessert',
        "body": 'Kasi gusto ko nang tikman',
        "caption": 'Lips mo ba yan o dessert Kasi gusto ko nang tikman 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Your lips look lonely',
        "body": 'mind if I join them with mine',
        "caption": 'Your lips look lonely, mind if I join them with mine 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Gusto mo ba ng kape kasi',
        "body": 'ikaw ang nagpapagising sa bawat umaga ko',
        "caption": 'Gusto mo ba ng kape kasi ikaw ang nagpapagising sa bawat umaga ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
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
        "header": 'Electric fan ka ba kasi',
        "body": 'gusto kong nasa harap mo lagi',
        "caption": 'Electric fan ka ba kasi gusto kong nasa harap mo lagi 😏\n\n#flirty #taglish #funnyfilipino #reels',
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
        "header": 'Panyo ka ba kasi ikaw',
        "body": 'gusto kong hawakan pag pinapawisan ako',
        "caption": 'Panyo ka ba kasi ikaw gusto kong hawakan pag pinapawisan ako 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Bed sheet ka ba kasi',
        "body": 'gusto kong magkulong kasama ka',
        "caption": 'Bed sheet ka ba kasi gusto kong magkulong kasama ka 😏\n\n#flirty #taglish #funnyfilipino #reels',
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
        "header": 'Puno ka ba kasi',
        "body": 'gusto kong umakyat sayo',
        "caption": 'Puno ka ba kasi gusto kong umakyat sayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Timplado ka ba kasi',
        "body": 'swak na swak ka sakin',
        "caption": 'Timplado ka ba kasi swak na swak ka sakin 😏\n\n#flirty #taglish #funnyfilipino #reels',
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
        "header": 'Kapag yumakap ako sayo',
        "body": 'hindi na kita bibitawan',
        "caption": 'Kapag yumakap ako sayo hindi na kita bibitawan 😏\n\n#flirty #taglish #funnyfilipino #reels',
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
        "header": 'Ikaw ba ang oras',
        "body": 'kasi tinatanggal mo pasensya ko',
        "caption": 'Ikaw ba ang oras kasi tinatanggal mo pasensya ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Banig ka ba dahil',
        "body": 'gusto kong humiga tayo',
        "caption": 'Banig ka ba dahil gusto kong humiga tayo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Labi mo ba',
        "body": 'reusable gusto kong balik-balikan',
        "caption": 'Labi mo ba reusable gusto kong balik-balikan 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Pwede bang ako',
        "body": 'muna hawakan mo ngayon',
        "caption": 'Pwede bang ako muna hawakan mo ngayon 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Miss mo ba lips ko',
        "body": 'ako miss ko na lips mo',
        "caption": 'Miss mo ba lips ko ako miss ko na lips mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Kung nandito ka ngayon nakahiga',
        "body": 'ka na sa dibdib ko',
        "caption": 'Kung nandito ka ngayon nakahiga ka na sa dibdib ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Pillow ka ba gusto',
        "body": 'kong yakapin buong gabi',
        "caption": 'Pillow ka ba gusto kong yakapin buong gabi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Pwede ka ba',
        "body": 'ngayon need kita',
        "caption": 'Pwede ka ba ngayon need kita 😏\n\n#flirty #taglish #funnyfilipino #reels',
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
        "header": 'Pwede bang matulog ako',
        "body": 'sa loob ng yakap mo',
        "caption": 'Pwede bang matulog ako sa loob ng yakap mo 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'May lisensya ka',
        "body": 'ba sa pang-aakit',
        "caption": 'May lisensya ka ba sa pang-aakit 😏\n\n#flirty #taglish #funnyfilipino #reels',
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
        "header": 'Gusto kong maramdaman bawat',
        "body": 'hinga mo sa leeg ko',
        "caption": 'Gusto kong maramdaman bawat hinga mo sa leeg ko 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Pwede bang ilapit mo',
        "body": 'yung labi mo dito',
        "caption": 'Pwede bang ilapit mo yung labi mo dito 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Gusto kong pakinggan boses',
        "body": 'mo habang nilalambing kita',
        "caption": 'Gusto kong pakinggan boses mo habang nilalambing kita 😏\n\n#flirty #taglish #funnyfilipino #reels',
    },
{
        "header": 'Ang sarap mo',
        "body": 'sigurong samahan buong gabi',
        "caption": 'Ang sarap mo sigurong samahan buong gabi 😏\n\n#flirty #taglish #funnyfilipino #reels',
    }
]



def natural_key(path: Path) -> list:
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", path.name)]


def duration(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def next_joke() -> tuple[int, dict[str, str]]:
    try:
        state = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}
    if not JOKES:
        raise RuntimeError("JOKES is empty; add at least one approved joke before creating a Reel.")
    index = int(state.get("next_joke_index", 0)) % len(JOKES)
    return index + 1, JOKES[index]


def save_progress(joke_number: int) -> None:
    """Advance only after Facebook confirms the Reel was published."""
    PROGRESS_FILE.write_text(json.dumps({
        "next_joke_index": joke_number % len(JOKES),
        "last_joke_number": joke_number,
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


def render_slide(joke_number: int, stage: int, text: str, output: Path) -> None:
    image = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    accent = (255, 205, 46, 255)
    draw.rounded_rectangle((55, 190, 1025, 1610), radius=42, fill=(8, 13, 32, 205), outline=accent, width=5)
    draw.text((540, 300), "FUNNY JOKES", anchor="mm", font=font(52), fill=accent)
    labels = ("FIRST LINE", "SECOND LINE")
    draw.text((540, 410), labels[stage], anchor="mm", font=font(33), fill=(180, 205, 255, 255))
    text_font = font(74 if len(text) < 58 else 60)
    lines = wrap(draw, text, text_font, 830)
    y = 820 - len(lines) * 42
    for line in lines:
        draw.text((540, y), line, anchor="mm", font=text_font, fill=(255, 255, 255, 255))
        y += text_font.size + 22
    draw.text((540, 1500), f"JOKE #{joke_number}  •  FOLLOW FOR MORE", anchor="mm", font=font(27), fill=(198, 208, 230, 255))
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


def output_video_path(joke_number: int, joke: dict[str, str]) -> Path:
    # A readable, filesystem-safe filename based on the first line of the joke.
    title = re.sub(r"[^a-z0-9]+", "-", joke["header"].lower()).strip("-")
    title = title[:70].rstrip("-") or "funny-joke"
    return OUTPUT_DIR / f"funny-joke-{joke_number:03d}-{title}.mp4"


def build_reel(joke_number: int, joke: dict[str, str], output_video: Path) -> None:
    pngs, wavs, times = [], [], []
    for stage, line in enumerate((joke["header"], joke["body"])):
        png, wav = OUTPUT_DIR / f"slide_{stage}.png", OUTPUT_DIR / f"voice_{stage}.wav"
        render_slide(joke_number, stage, line, png)
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
    command = ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(background(joke_number))]
    for png in pngs:
        command += ["-loop", "1", "-i", str(png)]
    command += ["-i", str(audio), "-filter_complex", ";".join(filters), "-map", f"[{previous}]", "-map", f"{len(pngs)+1}:a", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(output_video)]
    subprocess.run(command, check=True)



def main() -> None:
    number, joke = next_joke()
    print(f"Making joke {number}: {joke['header']}")
    video_path = output_video_path(number, joke)
    build_reel(number, joke, video_path)
    save_progress(number)
    print(f"Rendered video saved to: {video_path}")


if __name__ == "__main__":
    main()
