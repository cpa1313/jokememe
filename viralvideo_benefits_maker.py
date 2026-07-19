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
    {
        "heading": "DAHILAN NG MAITIM NA SINGIT OR KIFFY",
        "benefits": [
            "Pag-aahit at pagkakaron ng dry skin.",
            "Pagsusuot ng masisikip na damit pambaba.",
            "Side effects ng mga gamot na pang-regulate ng hormones, kolesterol at steroids.",
            "Katabaan at mataas ang sugar level.",
            "Genetics at hormonal imbalance.",
            "Pagkakaroon ng mga sakit “sakit sa pituitary ng thyroid gland, kanser, diabetes, sakit sa pituitary at thyroid gland).",
        ],
        "caption": (
            "DAHILAN NG MAITIM NA SINGIT OR KIFFY\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "BAWAL GAWIN PAGKATAPOS KUMAIN",
        "benefits": [
            "HUMIGA (can cause acid reflux).",
            "Magbuhat ng mabibigat (pwedeng sumakit ang tiyan)",
            "Matulog (hindi matutunawan pwedeng bangungutin)",
            "Bum3mbang (pwede maduwal sa sobrang kabusugan)",
        ],
        "caption": (
            "BAWAL GAWIN PAGKATAPOS KUMAIN\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "BENEPISYO NG F***INK?",
        "benefits": [
            "Nakakatulong ito para mabawasan ang TIMBANG.",
            "Nakakatulong ito sa pag-improve ng health ng heart at brain natin.",
            "Napapababa nito ang Risk na magkaroon ng Diabetes.",
            "Yang ang benepisyo ng F-A-S-T-I-N-G.",
        ],
        "caption": (
            "BENEPISYO NG F***INK?\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "MAAARING DAHILAN NG PAGLIIT NG ARI NG LALAKI",
        "benefits": [
            "Obesity (sobrang katabaan) tumatago ang ari dahil sa laki ng tiyan.",
            "Pagkaka-edad at Erectile Dysfunction.",
            "Prostate surgery.",
            "Peyronie's disease kondisyon kung saan nagkakaroon ng abnormal na (plague) sa loob ng ari, na nagiging sanhi ng pananakit, pagkurba, at nito.",
            "Malamig na Klima (umuurong ang ari).",
        ],
        "caption": (
            "MAAARING DAHILAN NG PAGLIIT NG ARI NG LALAKI\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "MGA KAILANGANG IPATEST BAGO MAKIPAGB3MBANG",
        "benefits": [
            "HIV.",
            "Pap smear (babae).",
            "Chlamydia Test.",
            "Herpes.",
            "Sp3rm count sa lalaki (baka baog).",
            "Psychological exam (As needed, baka may saltik)",
        ],
        "caption": (
            "MGA KAILANGANG IPATEST BAGO MAKIPAGB3MBANG\n\n"
            "Note: Bago makipagb3mbang, siguraduhing malinis, para safe na safe at stress free.\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "BAKIT NAGSASARILI ANG MGA IBANG BABAE",
        "benefits": [
            "Hindi na niyayaya ng partner.",
            "LDR or malayo ang partner.",
            "Bitin sa partner.",
            "Hindi magaling ang partner.",
            "Mga walang partner (Hindilahat).",
            "Sariling kagustuhan.",
            "Maliit ang partner.",
            "Kapag wala sa mood ang lalaki pero in heat sya.",
            "Kapag sobrang lasing ang lalaki pero ikaw gusto.",
        ],
        "caption": (
            "BAKIT NAGSASARILI ANG MGA IBANG BABAE\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "BAKIT TINOTOPAK ANG MGA BABAE",
        "benefits": [
            "Masyadong sensitive.",
            "walang pera.",
            "Baka malapit na magmenopause.",
            "Mood swings or hormonal changes.",
            "Kulang sa B3MBANG.",
        ],
        "caption": (
            "BAKIT TINOTOPAK ANG MGA BABAE\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "DAHILAN BAKIT NAG-OOVERTHINK ANG LALAKI",
        "benefits": [
            "Kasi takot sila sa sarili nilang multo.",
            "Kaunti lang sa mga lalaki ang ganyan.",
            "Meron silang trust issue.",
            "Walang tiwala sa sarili nya mismo.",
            "Mahina ang self confidence kaya nag iisip.",
            "Pangit ang tingin nya sa sarili nya.",
            "Kasi ayaw nila mangyari sa kanila yung ginagawa din nila.",
        ],
        "caption": (
            "DAHILAN BAKIT NAG-OOVERTHINK ANG LALAKI\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "BAKIT AYAW KANA KAB3MBANG NG PARTNER MO?",
        "benefits": [
            "Bad breath ka.",
            "Mabaho ang katawan.",
            "Sira-sira ang ngipin.",
            "Madumi ang kuko.",
            "Malaki ang tivan.",
            "Hindi magaling sa k@ma.",
            "Boring or walang thrill.",
            "Mabaho ang singit at kili2.",
        ],
        "caption": (
            "BAKIT AYAW KANA KAB3MBANG NG PARTNER MO?\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "NAGSESELOS ANG BABAE KAPAG...",
        "benefits": [
            "May kausap kang ibang babae.",
            "May nagchat sayong chix.",
            "May kainuman kang girl.",
            "Bestfriend mo ay babae.",
            "Puso ka ng puso sa post ngiba.",
            "tinitigasan ka sa ibang babae.",
        ],
        "caption": (
            "NAGSESELOS ANG BABAE KAPAG...\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "EXERCISE PARA SA KIFFY",
        "benefits": [
            "Gawin ang KEGEL EXERCISE (ang pelvic muscles na nagsusuporta sa kiffy ng babae).",
            "Paano gawin KEGEL EXERCISE: Yung feeling na nagpipigil kayo ng ihi (close open)",
            "Recommended din ito para sa mga nakakaranas ng balisawsaw or hirap sa pag-ihi.",
        ],
        "caption": (
            "EXERCISE PARA SA KIFFY\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "SENYALES NA SWERTE ANG BABAE SA PARTNER NYA",
        "benefits": [
            "Hindi ka minumura.",
            "Walang bisyo.",
            "Nirerespeto at ginagalang ka.",
            "Good provider.",
            "Mas magaling magluto.",
            "Kakampi mo maintindihin.",
            "Sinusuportahan ka sa gusto mo.",
            "Magaling sa lahat especially sa k@ma.",
        ],
        "caption": (
            "SENYALES NA SWERTE ANG BABAE SA PARTNER NYA\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "DAPAT GAWIN NG MGA BABAE PARA MAKAIWAS SA UTI",
        "benefits": [
            "Umihi pagkatapos makipagb3mbang.",
            "Tamang paglilinis ng kiffy.",
            "Regular Pag-inom ng tubig.",
            "Huwag pigilin ang ihi.",
            "Magsuot ng cotton napanty at iwasan ang sobrang masisikip.",
            "uminom ng fresh pagkatapos makipag b3mbang.",
        ],
        "caption": (
            "DAPAT GAWIN NG MGA BABAE PARA MAKAIWAS SA UTI\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "PABORITO NG MGA BABAE",
        "benefits": [
            "Kumain",
            "Manlambing",
            "Magbunganga",
            "Bumukaka.",
        ],
        "caption": (
            "PABORITO NG MGA BABAE\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "KAILAN DAPAT MAGPATEST NG HIV",
        "benefits": [
            "Active sa bmbang (lalo na kung iba-iba ang partner).",
            "Hindi gumagamit ng proteksyon kapag nakipagb3mbang sa iba or bagong kakilala.",
            "Gumagamit ng tinuturok na bawal na gamot at naghihiraman ng karayom.",
            "Kapag ang partner mo ay nalaman mong nakipagb3mbang sa iba.",
            "Buntis (bahagi ng regular na prenatal screening).",
            "Natusok ng karayom ng pasyenteng may HIV.",
        ],
        "caption": (
            "KAILAN DAPAT MAGPATEST NG HIV\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "SAAN MAGALING ANG BABAE",
        "benefits": [
            "Magaling mag-alaga, gagawin kang baby.",
            "Maasikaso sa lahat ng bagay.",
            "Masipag lalo na pag nadiligan.",
            "Magaling magluto.",
            "At syempre magaling sa ano.",
        ],
        "caption": (
            "SAAN MAGALING ANG BABAE\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "SAAN MAGALING ANG LALAKI",
        "benefits": [
            "Magaling mambola (hindi lahat).",
            "Magaling mambabae pero juts naman (hindi lahat).",
            "Feeling strong pero one round lang naman kaya.",
            "Feeling magaling pero seconds lang tapos na.",
            "Puro salita, kulang sa gawa.",
            "Magaling mangGhost after makatikim.",
        ],
        "caption": (
            "SAAN MAGALING ANG LALAKI\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "SECRET NG MGA LALAKI NA AYAW NILANG MALAMAN NG IBA",
        "benefits": [
            "hindi pa sya tuli.",
            "Maliit ang ano nya.",
            "paminta.",
            "Chickboy (Pwede sa boy or girl).",
            "v1rgin pa sya.",
        ],
        "caption": (
            "SECRET NG MGA LALAKI NA AYAW NILANG MALAMAN NG IBA\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "ILANG CALORIES BA ANG NABUBURN DURING B3MBANG",
        "benefits": [
            "LALAKI: approx 100 calories sa loob ng 30 minuto ng intense na b3mbang.",
            "BABAE: Approx 69 calories.",
            "Based sa research, humigit kumulang 3 to 5 to calories per minute ng pakikipagb3mbng",
            "Pero, ang bilang ng mga calorie na nabuburn mo ay nakadepende sa intensity ng session, tagal, at mga posisyon.",
        ],
        "caption": (
            "ILANG CALORIES BA ANG NABUBURN DURING B3MBANG\n\n"
            "Note: Ang b3mbng ay hindi nagbuburn ng kasing dami ng calories gaya ng moderate intensity exercise, pero meron pa din talagang nabuburn.\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "SENYALES NA HEALTHY ANG SEMILYA NG LALAKI",
        "benefits": [
            "kulay gatas hanggang sa mapusyaw na dilaw.",
            "malapot at malagkit kapag inilabas, ngunit nagiging likido pagkatapos ng 15-30 mins.",
            "Dami: Mayroon 1 to 5ml (halos isang kutsarita) bawat labas.",
            "Amoy bahagyaw tulad ng chlorine o bleach dahil sa mga protina at mineral nito.",
        ],
        "caption": (
            "SENYALES NA HEALTHY ANG SEMILYA NG LALAKI\n\n"
            "NOTE: Upang makasiguro sa kalidad ng semilya pagdating sa bilang, galaw (motility), at hugis (morphology)ng sp3rm, isang propesyunal na pagsusuri ang kailangan.\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "BA LUNUKIN ANG SMLYA NG LALAKI?",
        "benefits": [
            "Oo kung....",
            "Kung sa iisang partner, na malusog at walang uri ng sakit.",
            "Kung walang HIV, Chlamydia, Gonorrhea, Syphilis, at Hepatitis B ang partner.",
            "Kung ikaw ay walang singaw, dumudugong gilagid, o bukas na sugat ng bibig.",
            "Kung walang Allergy sa protina ng smlya (Bagamat bihira, may mga taong may human seminal plasma hypersensitivity. Maaari itong magdulot ng pangangati, pamumula, pamamaga).",
            "Ang semilya ay binubuo (fructose) at iba pang bitamina mineral na natural na natutunaw ng tiyan kaya safe.",
        ],
        "caption": (
            "BA LUNUKIN ANG SMLYA NG LALAKI?\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "MANGYAYARI SA BABAE KAPAG WALANG BMBANG",
        "benefits": [
            "Nagdudulot ng vaginal dryness.",
            "Nagiging prone sa mood swings at pagiging irritable.",
            "Hirap matulog, kulang sa physical release.",
            "Bumababa ang confidence.",
            "Dumadami ang stress at pimples; hirap mag-relax.",
            "Mahina ang energy, at madali magkasakit.",
            "Nanunuyot ang balat, at mabilis makatanda.",
            "Nawawala ang bonding at excitement sa mag-partner.",
        ],
        "caption": (
            "MANGYAYARI SA BABAE KAPAG WALANG BMBANG\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "MATAGAL LABASAN ANG BABAE KAPAG",
        "benefits": [
            "maliit yong saging.",
            "Kulang sa rom@nsa.",
            "Sobrang lasing.",
            "Pag napipilitan lang.",
            "Stressed at may iniisip.",
            "Wala sa mood.",
            "Hindi magaling ang partner.",
        ],
        "caption": (
            "MATAGAL LABASAN ANG BABAE KAPAG\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "MATAGAL LABASAN ANG LALAKI KAPAG",
        "benefits": [
            "Sobrang lasing.",
            "Naiinitan.",
            "Paiba iba ang posisyon.",
            "Pag hindi na kaya ng 2nd round at pinipilit na lang.",
            "Gusto nya tagalan, kapag pinipigilan nya para sulitin ang isang round.",
            "hindi sya nalil! bug@n sa partner nya.",
        ],
        "caption": (
            "MATAGAL LABASAN ANG LALAKI KAPAG\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "DAPAT GAWIN KAPAG LASING ANG BABAE",
        "benefits": [
            "Huwag hayaang magmaneho.",
            "Huwag pabayaan matapos ang inom.",
            "Huwag iiwan mag-isa at ipagkatiwala sa iba.",
            "Painumin ng tubig hindi madehydrate.",
            "Wag pagsa- samantalahan.",
            "wag videohan.",
        ],
        "caption": (
            "DAPAT GAWIN KAPAG LASING ANG BABAE\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "PWEDENG MANGYARI KAPAG NAKIPAG BMBANG NANG LASING",
        "benefits": [
            "Maiputok sa loob, at mabuntis nang wala sa oras.",
            "Sa sobrang kalasingan, hindi mo na pala partner ang kabmbangan mo.",
            "Yung iba, hindi nakakatapos, nabibitin dahil lasing na.",
            "Baka magsuka ka habang binebmbang.",
            "Hindi mo maeenjoy dahil hilo ka na.",
            "Nagiging wild, mas gumagaling sa foreplay.",
        ],
        "caption": (
            "PWEDENG MANGYARI KAPAG NAKIPAG BMBANG NANG LASING\n\n"
            "Tandaan: Ang alcohol is a downer, depressant. Kaya pag nasosobrahan ka ng alcohol, inaantok o bigla ka na lang matutulog.\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "SENYALES NA KA NA SA PAGLULU",
        "benefits": [
            "Kapag nakakaapekto na ito sa iyong trabaho at daily activities.",
            "Kapag nakakaapapekto naito sayong relasyon.",
            "Kapag araw-araw ito na lang naiisip mo: KUNG PAANO KA MAGSASARILI.",
            "Feeling guilty ka na dahi maraming beses mo tong ginagawa sa isang araw at tingin mo naaadik ka na.",
            "kapag hindi kana nalilibugan sa partner mo.",
        ],
        "caption": (
            "SENYALES NA KA NA SA PAGLULU\n\n"
            "Paalala: Ang sobra ay nakakasama din!!.\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "HUWAG MAKIPAG B3MBANG KAPAG...",
        "benefits": [
            "Ayaw pa makabuntis or mabuntis agad.",
            "Estudyante ka pa lang/teenager.",
            "Sobrang lasing or hindi kakilala.",
            "May UTI, STD, HIV or any infection sa ari.",
            "partner ng iba ang bineb3mbang mo.",
        ],
        "caption": (
            "HUWAG MAKIPAG B3MBANG KAPAG...\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "Rason bakit nagsasarili Kahit may partner na...",
        "benefits": [
            "LDR (malayo ang partner).",
            "nakasanayan na ang pagsasarili.",
            "stressed sa partner, ginawang pamparelax.",
            "sariling kagustuhan.",
            "may pinapantasya sya, na hindi nya partner.",
            "iwas tukso na makagawa ng kakaiba, kaya nagsarili na lang.",
            "bored sa partner nya.",
            "biglang may napanood or Nakita.",
        ],
        "caption": (
            "Rason bakit nagsasarili Kahit may partner na...\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "EPEKTO NG PAGLALAGAY NG BOLITAS SA ARI",
        "benefits": [
            "Maaaring makasugat sa kiffy ng partner.",
            "Prone sa infection.",
            "maari kang matetano.",
            "may kirot or sakit during b3mbang.",
            "Nakakaipit ng ari, pwede maapektuhan ang pagtigas.",
        ],
        "caption": (
            "EPEKTO NG PAGLALAGAY NG BOLITAS SA ARI\n\n"
            "PAAALA: Sa lalaki na may bolitas who develop erectile dysfunction, or nabaog, or nagka-cancer ang isa nilang SINISISI ay ang kanilang BOLITAS!!\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "BAKIT HINDI DAPAT KUMAIN NG MADAMI BAGO MAGB3MBANG?",
        "benefits": [
            "Pwede magkaron ng kabag.",
            "Maaaring makaramdam ng discomfort.",
            "Pwede magkaron ng bad breath.",
            "Feeling bloated.",
            "Baka hindi ka matunawan (indigestion)",
            "Baka bigla kang mautot.",
            "Hindi makakaperform ng maayos dahil sa sobrang kabusugan.",
        ],
        "caption": (
            "BAKIT HINDI DAPAT KUMAIN NG MADAMI BAGO MAGB3MBANG?\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "BENEPISYO NG PAGLIGO NG SABAY",
        "benefits": [
            "Nakababawas ng stress.",
            "Nagpapabuti ng koneksyon at relasyon.",
            "Nakatitipid sa oras at tubig.",
            "Nakatutulong din ito sa pagrerelax ng mga kalamnan.",
            "Pagpapababa ng tensyon sa buong katawan.",
            "Pagpapakita ng pag-aalaga sa isa't isa.",
        ],
        "caption": (
            "BENEPISYO NG PAGLIGO NG SABAY\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "ILANG BESES BA DAPAT ANG HEALTHY COUPLE MAG B3MBANG BASE SA AGE?",
        "benefits": [
            "20s: 1-3x a week or more.",
            "30s: 1-2 times a week.",
            "40s: Average once a week.",
            "50s: Once a month or almost zero.",
            "Sa gusto mabuntis: Makipagt@lik tuwing 2-3days especially “kapag ovulation.",
            "GOOD s3x: ay hindi kailangang araw-araw pero dapat itong gawin kapag parehong gusto at hindi stressed.",
            "Kapag regular ang b3mbang, may health benefits ito: reducing stress, improving sleep quality, improving fitness.",
        ],
        "caption": (
            "ILANG BESES BA DAPAT ANG HEALTHY COUPLE MAG B3MBANG BASE SA AGE?\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "TIPS PARA HINDI MAWALA ANG INTIMACY SA RELASYON",
        "benefits": [
            "Bigyan niyo pa rin ng oras ang isat isa kahit busy “Kasi intimacy unti-unting nawawala kapag puro routine nalang relasyon niyo.",
            'Huwag hayaang puro stress at away nalang laman ng relasyon “Dapat marunong parin kayong gumawa ng moments" together.',
            "Magkaroon ng deep talks na totoo at sinasabuhay “Hindi lang tungkol sa problema pati thoughts, feelings at little moments sa araw niyo.",
            "Matutong mag appreciate sa malilit na bagay nafifeel na valued siya mas lumalalim ang emotional connection niyo.",
            "Huwag hayaan mawala ang physical affection holding hands; lambingan, at bmbang para manatiling connected.",
        ],
        "caption": (
            "TIPS PARA HINDI MAWALA ANG INTIMACY SA RELASYON\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "B3mbang PARA SA KALUSUGAN",
        "benefits": [
            "After ng bmbang -babae:gustong A makipag-usap.",
            "Maaaring magmukhang mas bata ang mga mag partner na madalas ang b3mbang.",
            "Pagkatapos ng b3mbng, ang katawan ay nakakaramdam ng pagkarelax at feeling healthy.",
            "Kissing for 20secs can increase sexu@l desire.",
            "Pwede mag burn ng calories kapag umabot ng 30mins.",
            "Makakatulong ng mahimbing at good mood.",
        ],
        "caption": (
            "B3mbang PARA SA KALUSUGAN\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "BAKIT SUMASAKIT ANG KIFFY DURING BMBANG?",
        "benefits": [
            "Kulang sa lubircant -atleast 5-10mins na labing labing muna.",
            "Mga babae na nasa pre-menopausal or nagpapadede (sila ang nakakaranas ng dryness).",
            "Mga gumagamit ng birth control tulad ng pills, depo implant, etc.",
            "Kapag may UTI or Yeast infection or STI.",
            "Babaeng nakakaranas nc vaginismus or involuntary spasm sa Kiffy.",
            "Medical conditions like endometriosis, pelvic inflammatory disease, at ovarian cyst.",
            "masyadong malaki yong s@ging nya.",
        ],
        "caption": (
            "BAKIT SUMASAKIT ANG KIFFY DURING BMBANG?\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "MGA DAPAT IWASAN NG LALAKI PARA SAPAT ANG TIME SA B3MBANG",
        "benefits": [
            "Mga nakakasira sa ugat ng ari ng lalaki....",
            "Yosi, Sobrang alak, Pagpupuyat, DrOga.",
            "Magkaron ng STD.",
            "Magkaron ng Diabetes.",
            "Sobrang naiinitan ang ari (pwedeng maluto ang balls)",
            "Pagsuot ng sobrang sikip na pambaba.",
            "Matagal na pag-upo or sobrang pagba-bike.",
        ],
        "caption": (
            "MGA DAPAT IWASAN NG LALAKI PARA SAPAT ANG TIME SA B3MBANG\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "MALING GINAGAWA NG LALAKI DURING BMBANG...",
        "benefits": [
            "Kulang sa labing labing.",
            "Banat agad kahit tuyo pa.",
            "nauuna pa syang matapos.",
            "Namimilit kahit wala sa mood ang babae.",
            "Sobrang tagal matapos dry na ang babae.",
            "Wala nang pansinan or hindi na nag-uusap after.",
            "Nagyayaya ng lasing, kaya mas tumatagal",
            "Basta makatapos lang.",
        ],
        "caption": (
            "MALING GINAGAWA NG LALAKI DURING BMBANG...\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "GAWIN PARA HINDI KA IWAN NG PARTNER MO",
        "benefits": [
            "Huwag puro pagbubunganga, nakakapangit yan.",
            "Kahit pagod na sa gawaing bahay, huwag magpakalosyang.",
            "Iwasan ang stress, nakakababa ng immune system.",
            "Magpaganda pa din kahit nasa bahay lang.",
            "Gawing exercise ang gawaing Bahay.",
            "iBuko Juice mo sya.",
        ],
        "caption": (
            "GAWIN PARA HINDI KA IWAN NG PARTNER MO\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "DAPAT GAWIN PARA HINDI MAGKASAKIT ANG ARI NG LALAKI",
        "benefits": [
            "Gumamit ng proteksyon para makaiwas sa STD/HIV.",
            "Huwag makipagbembang sa hindi mo kilala, or paiba iba ang partner.",
            "Huwag hawakan ang ari ng sobrang higpit upang maiwasan ang sugat o pamamaga.",
            "Regular na paghugas sa ari ng hindi sobrang tapang na sabon.",
            "Huwag magpigil ng ihi upang maiwasan ang impeksyon sa daluyan ng ihi.",
            "Tamang diet at lifestyle -iwasan ang paninigarilyo at pag-inom ng alak para makaiwas sa Erectile dysfunction.",
        ],
        "caption": (
            "DAPAT GAWIN PARA HINDI MAGKASAKIT ANG ARI NG LALAKI\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "MGA TAONG AYAW SA BEMBANG",
        "benefits": [
            "ito ay tinatawag na \"ASEXUAL\".",
            "isang asexual na tao ay nakararanas ng kakaunti o walang attraction sa iba.",
            "kakulangan ng interest sa mga sexual narelasyon o Gawain.",
            "maaring mayroon o wala rin silang nararamdamang emotional, physical, o romantic attraction sa iba.",
            "may iba na naming may karelasyon ngunit walang b3mbang na nagaganap.",
        ],
        "caption": (
            "MGA TAONG AYAW SA BEMBANG\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "GAMITIN PARA HINDI MABUNTIS",
        "benefits": [
            "Family planning method tulad ng (Con-dom)",
            "/Depo/Injectables.",
            "Pills.",
            "implant.",
            "IUD.",
            "Cervix Mucus Method.",
            "Vasectomy.",
            "Bilateral Tubal Ligation.",
            "Withdrawal method (para lang to sa mga expert).",
        ],
        "caption": (
            "GAMITIN PARA HINDI MABUNTIS\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "DAPAT GAWIN PARA HINDI BUMAHO ANC ARI NG LALAKI",
        "benefits": [
            "Hugasan ang ari at singit araw2 tuwing maliligo.",
            "Linisin ang ilalim ng Foreskin (Kung hindi pa tuli).",
            "Patuyuing mabuti Siguraduhing tuyo ang ari at singit bago magsuot ng brief para maiwasan ang fungi at bacteria.",
            "Magsuot ng maluwag at cotton na brief o boxer shorts para makahinga ang balat at hindi magpawis ng husto.",
            "Regular na trim o gupitan ang pubic hair para walang kakapitan or pagsstayan ang bacteria.",
            "Palitan agad ang underwear pagkatapos mag-exercise.",
            "wag bum3mbang ng Kahit sino sino.",
        ],
        "caption": (
            "DAPAT GAWIN PARA HINDI BUMAHO ANC ARI NG LALAKI\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "GAWIN KUNG GUSTO MAGBALIK ang ALINDOG",
        "benefits": [
            "Magpapawis magwalking, magjogging, kahit nasa Bahay.",
            "Umiwas or bawasan ang pagkain na mataas ang sugar juice, white rice, cakes, etc.",
            "Umiwas sa mga taong lagi kang niyayaya kumain.",
            "Umiwas sa mga taong nangdodown sa pagbabalik alindog mo.",
        ],
        "caption": (
            "GAWIN KUNG GUSTO MAGBALIK ang ALINDOG\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "KAILANGAN NG LALAKI SA PARTNER NYA",
        "benefits": [
            "RESPECT (hindi mo pinapahiya sa harap ng tropa nya at hindi kinukumpara sa ibang lalaki)",
            "PEACE (walang stress, less drama).",
            "APPRECIATION (kahit simpleng effort nila malaking bagay na naaappreciate sila ng partner nilang babae).",
            "LOYALTY (physical and emotional).",
            "SUPPORT (yung may paghuhugutan sila ng lakas at hindi puro kontra).",
            "CONSISTENCY (hindi yung sweet ka ngayon, bukas cold kana).",
            "REASSURANCE (kahit sila kailangan ng assurance na loyal at faithful ka).",
            "bigyan mo sya ng Buko Juice habang tulog.",
        ],
        "caption": (
            "KAILANGAN NG LALAKI SA PARTNER NYA\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "senyales na wala nang gana ang lalaki sayo",
        "benefits": [
            "Madaling mainis or irritable kapag kausap ka.",
            "Laging busy or may dahilan para hindi ka makausap.",
            "Mas madalas sa cellphone or socmed kesa makipag-usap sayo.",
            "Maikli lang or malamig sumagot.",
            "Mas madalas kasama ang tropa or ibang tao.",
            "Hindi na sya interesado sa opinyon mo.",
            "Wala nang paki at hinahayaan ka nalang Kahit magalit ka pa.",
        ],
        "caption": (
            "senyales na wala nang gana ang lalaki sayo\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "Dapt mong GAWIN KAPAG LASING ANG BABAE",
        "benefits": [
            "Alagaan, wag mong b3mbangin.",
            "huwag mong videohan.",
            "Mas makulit pa yan sayo kapag lasing, alalayan mo lang.",
            "Painumin ng maraming tubig.",
            "Huwag nang patulan kapag minumura ka sa mga kasalanan mo.",
        ],
        "caption": (
            "Dapt mong GAWIN KAPAG LASING ANG BABAE\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "GAWIN KAPAG LASING ANG LALAKI",
        "benefits": [
            "Huwag awayin at bungangaan lalo na kapag lasing.",
            "Painumin ng madaming tubig para ma-rehydrate.",
            "Alagaan at bigyan ng sapat na pahinga.",
            "Kapag makulit pa din, huwag mo na lang pansinin.",
        ],
        "caption": (
            "GAWIN KAPAG LASING ANG LALAKI\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "ANONG GINAGAWA NYO AFTER BEMBANG",
        "benefits": [
            "Maghugas para makaiwas sa infection.",
            "bigyan ng Buku Juice si mister para sa may ROUND 2.",
            "cuddle.",
            "Emotional care.",
            "Physical care.",
            "Sweet talks.",
        ],
        "caption": (
            "ANONG GINAGAWA NYO AFTER BEMBANG\n\n"
            "Importante ang after care para mapanatili ang trust bonding, at connection.\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "SENYALES NA MATAAS ANG EMOTIONAL “INTELLIGENCE NG N PARTNER MO\".",
        "benefits": [
            "Marunong makinig bago sumagot.",
            "Hindi sinusuklian ang init ng ulo mo (laging kalmado at mahinahon).",
            "Marunong umamin kapag mali (bihira nga lang sa babae).",
            "Alam nyang hindi lang sya lagi ang bida.",
            "Marunong magbago kapag nasaktan ka.",
            "Meron syang empathy (hindi nya minamadali ang healing mo).",
            "Hindi gumaganti (marunong umunawa kesa manghusga).",
            "magaling sa romansa bago ka b3mbangin.",
        ],
        "caption": (
            "SENYALES NA MATAAS ANG EMOTIONAL “INTELLIGENCE NG N PARTNER MO\".\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "SAFE BA MAKIPAG BEMBANG HABANG BUNTIS",
        "benefits": [
            "Yes kapag...",
            "Walang pagdurugo or bleeding habang nagbubuntis.",
            "Walang senyales ng abort!on or pagkalaglag.",
            "Atleast 4months pataas na ang tiyan.",
            "Kung hindi nakakaranas ng cramps or paninigas ng tiyan.",
            "Walang infection sa pwerta.",
        ],
        "caption": (
            "SAFE BA MAKIPAG BEMBANG HABANG BUNTIS\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "Bakit natuturn off ang lalaki during b3mbang",
        "benefits": [
            "may amor or mabaho ang kiffs.",
            "hindi marunong gumalaw or tamad.",
            "tumatawa at hindi nagcoconcentrate.",
            "bad breath.",
            "may putok.",
            "nakatulala at nakatitig ng matagal.",
            "nagsabi ka ng pangalan ng ibang lalake.",
        ],
        "caption": (
            "Bakit natuturn off ang lalaki during b3mbang\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "MAAARING DAHILAN BAKIT HIRAP MABUNTIS ANG BABAE",
        "benefits": [
            "PCOS at Hormonal Imbalance.",
            "Edad 35 pataas.",
            "Issue sa Fallopian Tubes o Uterus.",
            "Lifestyle Factors katabaan o kapayatan, mataas na stress, at labis na pag-inom ng alak.",
            "Timing at Fertile Window “hindi sapat ng pakik!pagt@lik sa fertile window.",
        ],
        "caption": (
            "MAAARING DAHILAN BAKIT HIRAP MABUNTIS ANG BABAE\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "DAPAT GAWIN SA PARTNER",
        "benefits": [
            "Kapag nagselos, i-reassure mo.",
            "Kapag wala sa mood, lambingin mo.",
            "Wag yung wala ka na ngang gagawin, sinabayan mo pa.",
        ],
        "caption": (
            "DAPAT GAWIN SA PARTNER\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "best time to get pregnant.",
        "benefits": [
            "Kung nasa early 20s at may trabaho na.",
            "Kung ready ka na at may ipon kahit paano.",
            "Kapag ready ka na emotionally.",
            "Kapag kaya mo nang tanggapin maging Nanay/Tatay.",
            "Kung may partner na madiskarte at maalaga.",
        ],
        "caption": (
            "best time to get pregnant.\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "HUWAG GAWIN KAPAG MAY UTI",
        "benefits": [
            "Huwag magpigil sa ihi.",
            "Iwasan uminom ng may Caffeine at Alkohol.",
            "Iwasan ang pagkain ng maanghang at acidic.",
            "Huwag gumamit ng matapang na sabon, spray, o douche.",
            "Huwag mag Self-Medication.",
            "Huwag makipag B3mb@ng!.",
        ],
        "caption": (
            "HUWAG GAWIN KAPAG MAY UTI\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "cravings ng trentahin.",
        "benefits": [
            "peaceful workplace.",
            "travel.",
            "savings.",
            "mahimbing at kumpletong tulog.",
            "n@ked full body massage.",
            "magpa-yummy.",
            "kumain ng masarap (totoong pagkain).",
        ],
        "caption": (
            "cravings ng trentahin.\n\n"
            "#MikaNurseDaily #healthtips #tips #reels"
        ),
    },
    {
        "heading": "PAANO MAINLOVE ANG LALAKI",
        "benefits": [
            "Binibigay ang lahat.",
            "marunong umiyak.",
            "Sobra manuyo pag galit ang babae.",
            "Ikaw lang ang maganda sa mata nya.",
            "Faithful at loyal sigurado.",
            "ihi lang ang pahinga kapag bin3mbang ka.",
        ],
        "caption": (
            "PAANO MAINLOVE ANG LALAKI\n\n"
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
