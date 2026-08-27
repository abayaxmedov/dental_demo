"""
Demo content: "Oq Marvarid Dental" (ADR H-qism).
Qoida: nol lorem ipsum · nol "Prodent" · barcha telefon +998 · pul soʻmda · Asia/Tashkent.

Ishlatish:
    python manage.py seed_demo            # yoʻq boʻlsa yaratadi (idempotent)
    python manage.py seed_demo --reset    # avval demo content'ni tozalaydi
"""

import pathlib
from datetime import date, time, timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone, translation

from apps.appointments.models import Appointment, AppointmentStatus
from apps.blog.models import Post
from apps.cases.models import CasePair
from apps.core import seed_content as sc
from apps.core.models import ClinicSettings, StatCounter, WorkingHours
from apps.gallery.models import GalleryImage
from apps.leads.models import Lead
from apps.pages.models import StaticPage
from apps.reviews.models import Review
from apps.services.models import Faq, PriceItem, Service, ServiceCategory
from apps.team.models import Doctor, DoctorSchedule, TimeOff

M = Decimal  # qisqartma


# ─────────────────────────── Sozlamalar ───────────────────────────
CLINIC = {
    "name": {"uz": "Oq Marvarid Dental", "ru": "Oq Marvarid Dental", "en": "Oq Marvarid Dental"},
    "tagline": {
        "uz": "Toshkentdagi zamonaviy stomatologiya markazi",
        "ru": "Современный стоматологический центр в Ташкенте",
        "en": "A modern dental centre in Tashkent",
    },
    "about_short": {
        "uz": "2014-yildan beri Yunusobodda oilaviy stomatologiya. Raqamli diagnostika, "
        "ogʻriqsiz davolash va implantatsiya boʻyicha 3 000 dan ortiq muvaffaqiyatli ish.",
        "ru": "Семейная стоматология в Юнусабаде с 2014 года. Цифровая диагностика, "
        "безболезненное лечение и более 3 000 успешных имплантаций.",
        "en": "A family dental practice in Yunusobod since 2014. Digital diagnostics, "
        "painless treatment and over 3,000 successful implant cases.",
    },
    "address": {
        "uz": "Toshkent, Yunusobod tumani, Amir Temur shoh koʻchasi 108",
        "ru": "Ташкент, Юнусабадский район, проспект Амира Темура 108",
        "en": "108 Amir Temur Ave, Yunusobod, Tashkent",
    },
    "license_text": {
        "uz": "Litsenziya: Sogʻliqni saqlash vazirligi, № 12-04578, 2014-yil 12-mart",
        "ru": "Лицензия: Министерство здравоохранения, № 12-04578, 12 марта 2014 г.",
        "en": "Licence: Ministry of Health, No. 12-04578, 12 March 2014",
    },
}

WORKING_HOURS = [
    (0, time(9, 0), time(19, 0), False, {"uz": "", "ru": "", "en": ""}),
    (1, time(9, 0), time(19, 0), False, {"uz": "", "ru": "", "en": ""}),
    (2, time(9, 0), time(19, 0), False, {"uz": "", "ru": "", "en": ""}),
    (3, time(9, 0), time(19, 0), False, {"uz": "", "ru": "", "en": ""}),
    (4, time(9, 0), time(19, 0), False, {"uz": "", "ru": "", "en": ""}),
    (
        5,
        time(9, 0),
        time(16, 0),
        False,
        {"uz": "Qisqa kun", "ru": "Короткий день", "en": "Short day"},
    ),
    (6, None, None, True, {"uz": "Dam olish kuni", "ru": "Выходной", "en": "Closed"}),
]

COUNTERS = [
    ({"uz": "yillik tajriba", "ru": "лет опыта", "en": "years of practice"}, 12, "", "award"),
    (
        {"uz": "baxtli bemor", "ru": "довольных пациентов", "en": "happy patients"},
        8500,
        "+",
        "smile",
    ),
    ({"uz": "mutaxassis", "ru": "специалистов", "en": "specialists"}, 14, "", "users"),
    (
        {"uz": "oʻrnatilgan implant", "ru": "установленных имплантов", "en": "implants placed"},
        3000,
        "+",
        "activity",
    ),
]

CATEGORIES = [
    ("terapiya", {"uz": "Terapiya", "ru": "Терапия", "en": "Therapy"}, "stethoscope"),
    (
        "jarrohlik",
        {
            "uz": "Jarrohlik va implantatsiya",
            "ru": "Хирургия и имплантация",
            "en": "Surgery & implants",
        },
        "scissors",
    ),
    ("ortodontiya", {"uz": "Ortodontiya", "ru": "Ортодонтия", "en": "Orthodontics"}, "align-left"),
    (
        "gigiyena",
        {"uz": "Gigiyena va estetika", "ru": "Гигиена и эстетика", "en": "Hygiene & aesthetics"},
        "sparkles",
    ),
]

# (cat_key, uz, ru, en, excerpt_uz, excerpt_ru, excerpt_en, duration, featured, order)
SERVICES = [
    (
        "jarrohlik",
        "Implantatsiya",
        "Имплантация",
        "Dental implants",
        "Bitta tishdan toʻliq jagʻgacha — Koreya va Shveytsariya implantlari, 10 yillik kafolat.",
        "От одного зуба до полной челюсти — корейские и швейцарские импланты, гарантия 10 лет.",
        "From a single tooth to a full arch — Korean and Swiss implants, 10-year warranty.",
        90,
        True,
        1,
    ),
    (
        "gigiyena",
        "Estetik plombalash",
        "Эстетическая реставрация",
        "Aesthetic fillings",
        "Nanokompozit materiallar bilan tabiiy rangga toʻliq mos plomba.",
        "Пломбы из нанокомпозита с точным подбором natural-оттенка.",
        "Nano-composite fillings colour-matched to your natural enamel.",
        45,
        True,
        2,
    ),
    (
        "gigiyena",
        "Professional gigiyena",
        "Профессиональная гигиена",
        "Professional hygiene",
        "Air Flow va ultratovush bilan tosh va gʻubor tozalash, ogʻriqsiz.",
        "Снятие камня и налёта ультразвуком и Air Flow, безболезненно.",
        "Ultrasonic and Air Flow scaling — comfortable and thorough.",
        40,
        True,
        3,
    ),
    (
        "ortodontiya",
        "Breketlar",
        "Брекеты",
        "Braces",
        "Metall, keramik va shaffof breket tizimlari; 3D rejalashtirish bilan.",
        "Металлические, керамические и прозрачные брекет-системы с 3D-планированием.",
        "Metal, ceramic and clear bracket systems with 3D treatment planning.",
        60,
        True,
        4,
    ),
    (
        "terapiya",
        "Ildiz kanali davolash",
        "Лечение каналов",
        "Root canal treatment",
        "Mikroskop ostida endodontik davolash — bitta seansda, ogʻriqsiz.",
        "Эндодонтическое лечение под микроскопом — за один визит, без боли.",
        "Endodontic treatment under a microscope — often in a single visit.",
        75,
        True,
        5,
    ),
    (
        "jarrohlik",
        "Aqli tish olib tashlash",
        "Удаление зуба мудрости",
        "Wisdom tooth removal",
        "Murakkab holatlar ham — KLKT diagnostikasi va yumshoq anesteziya bilan.",
        "Даже сложные случаи — с КЛКТ-диагностикой и мягкой анестезией.",
        "Including complex cases — with CBCT imaging and gentle anaesthesia.",
        60,
        True,
        6,
    ),
    (
        "terapiya",
        "Karies davolash",
        "Лечение кариеса",
        "Cavity treatment",
        "Erta bosqichda ogʻriqsiz davolash, tish toʻqimasini maksimal saqlagan holda.",
        "Безболезненное лечение на ранней стадии с максимальным сохранением тканей.",
        "Early-stage treatment that preserves as much tooth structure as possible.",
        40,
        False,
        7,
    ),
    (
        "gigiyena",
        "Tishlarni oqartirish",
        "Отбеливание зубов",
        "Teeth whitening",
        "ZOOM 4 texnologiyasi — bir seansda 6–8 tongacha yorqinroq.",
        "Технология ZOOM 4 — на 6–8 тонов светлее за один сеанс.",
        "ZOOM 4 whitening — 6 to 8 shades lighter in a single session.",
        60,
        False,
        8,
    ),
    (
        "jarrohlik",
        "Suyak toʻqimasi tiklash",
        "Костная пластика",
        "Bone grafting",
        "Implantatsiyadan oldin suyak hajmini tiklash (sinus-lifting).",
        "Восстановление объёма кости перед имплантацией (синус-лифтинг).",
        "Restoring bone volume before implant placement (sinus lift).",
        90,
        False,
        9,
    ),
    (
        "ortodontiya",
        "Elayner (shaffof kappa)",
        "Элайнеры",
        "Clear aligners",
        "Koʻrinmas kappalar bilan tishlarni tekislash — olib-kiyish mumkin.",
        "Выравнивание зубов прозрачными каппами — можно снимать.",
        "Discreet, removable aligners that straighten teeth gradually.",
        45,
        False,
        10,
    ),
    (
        "terapiya",
        "Bolalar stomatologiyasi",
        "Детская стоматология",
        "Paediatric dentistry",
        "3 yoshdan boshlab — bolani qoʻrqitmaydigan muhit va oʻyin orqali moslashuv.",
        "С 3 лет — дружелюбная атмосфера и адаптация через игру.",
        "From age three — a friendly setting and play-based adaptation.",
        30,
        False,
        11,
    ),
    (
        "gigiyena",
        "Vinirlar",
        "Виниры",
        "Veneers",
        "E.max keramik vinirlar — tabassum dizayni raqamli maketi bilan.",
        "Керамические виниры E.max с цифровым макетом улыбки.",
        "E.max ceramic veneers with a digital smile design preview.",
        90,
        False,
        12,
    ),
    (
        "jarrohlik",
        "Protezlash",
        "Протезирование",
        "Prosthetics",
        "Toj, koʻprik va olinadigan protezlar — sirkoniy va keramika.",
        "Коронки, мосты и съёмные протезы — цирконий и керамика.",
        "Crowns, bridges and dentures in zirconia and ceramic.",
        75,
        False,
        13,
    ),
    (
        "terapiya",
        "Milk kasalliklari davolash",
        "Лечение дёсен",
        "Gum treatment",
        "Gingivit va parodontit — Vector terapiya bilan kompleks davolash.",
        "Гингивит и пародонтит — комплексное лечение с Vector-терапией.",
        "Gingivitis and periodontitis — comprehensive care with Vector therapy.",
        50,
        False,
        14,
    ),
]

# (service_title_uz | None, cat_key, uz, ru, en, from, to, unit_uz, promo)
PRICES = [
    (
        "Implantatsiya",
        "jarrohlik",
        "Osstem implant (Koreya) oʻrnatish",
        "Установка импланта Osstem (Корея)",
        "Osstem implant (Korea) placement",
        4_500_000,
        5_200_000,
        "1 implant",
        False,
    ),
    (
        "Implantatsiya",
        "jarrohlik",
        "Straumann implant (Shveytsariya)",
        "Имплант Straumann (Швейцария)",
        "Straumann implant (Switzerland)",
        8_900_000,
        10_500_000,
        "1 implant",
        False,
    ),
    (
        "Implantatsiya",
        "jarrohlik",
        "All-on-4 toʻliq jagʻ",
        "All-on-4 полная челюсть",
        "All-on-4 full arch",
        42_000_000,
        None,
        "1 jagʻ",
        False,
    ),
    (
        "Aqli tish olib tashlash",
        "jarrohlik",
        "Oddiy olib tashlash",
        "Простое удаление",
        "Simple extraction",
        350_000,
        500_000,
        "1 tish",
        False,
    ),
    (
        "Aqli tish olib tashlash",
        "jarrohlik",
        "Murakkab olib tashlash (retinirlangan)",
        "Сложное удаление (ретинированный)",
        "Complex extraction (impacted)",
        900_000,
        1_400_000,
        "1 tish",
        False,
    ),
    (
        "Suyak toʻqimasi tiklash",
        "jarrohlik",
        "Sinus-lifting (yopiq)",
        "Синус-лифтинг (закрытый)",
        "Sinus lift (closed)",
        3_200_000,
        None,
        "1 tomon",
        False,
    ),
    (
        "Protezlash",
        "jarrohlik",
        "Sirkoniy toj",
        "Циркониевая коронка",
        "Zirconia crown",
        2_800_000,
        3_500_000,
        "1 tish",
        False,
    ),
    (
        "Protezlash",
        "jarrohlik",
        "Metall-keramika toj",
        "Металлокерамическая коронка",
        "Metal-ceramic crown",
        1_400_000,
        None,
        "1 tish",
        False,
    ),
    (
        "Karies davolash",
        "terapiya",
        "Yuzaki karies",
        "Поверхностный кариес",
        "Surface cavity",
        350_000,
        None,
        "1 tish",
        False,
    ),
    (
        "Karies davolash",
        "terapiya",
        "Chuqur karies",
        "Глубокий кариес",
        "Deep cavity",
        550_000,
        750_000,
        "1 tish",
        False,
    ),
    (
        "Ildiz kanali davolash",
        "terapiya",
        "Bir kanalli tish",
        "Одноканальный зуб",
        "Single-canal tooth",
        800_000,
        None,
        "1 tish",
        False,
    ),
    (
        "Ildiz kanali davolash",
        "terapiya",
        "Uch kanalli tish",
        "Трёхканальный зуб",
        "Three-canal tooth",
        1_600_000,
        2_100_000,
        "1 tish",
        False,
    ),
    (
        "Milk kasalliklari davolash",
        "terapiya",
        "Vector terapiya",
        "Vector-терапия",
        "Vector therapy",
        1_200_000,
        None,
        "1 seans",
        False,
    ),
    (
        "Bolalar stomatologiyasi",
        "terapiya",
        "Bolalar uchun plomba",
        "Детская пломба",
        "Child filling",
        300_000,
        None,
        "1 tish",
        False,
    ),
    (
        "Bolalar stomatologiyasi",
        "terapiya",
        "Ftorlash (profilaktika)",
        "Фторирование",
        "Fluoride treatment",
        250_000,
        None,
        "1 seans",
        True,
    ),
    (
        "Estetik plombalash",
        "gigiyena",
        "Nanokompozit restavratsiya",
        "Нанокомпозитная реставрация",
        "Nano-composite restoration",
        700_000,
        950_000,
        "1 tish",
        False,
    ),
    (
        "Professional gigiyena",
        "gigiyena",
        "Kompleks gigiyena (Air Flow + ultratovush)",
        "Комплексная гигиена (Air Flow + ультразвук)",
        "Full hygiene (Air Flow + ultrasonic)",
        450_000,
        None,
        "1 seans",
        True,
    ),
    (
        "Tishlarni oqartirish",
        "gigiyena",
        "ZOOM 4 kabinet oqartirish",
        "Кабинетное отбеливание ZOOM 4",
        "ZOOM 4 in-office whitening",
        2_400_000,
        None,
        "2 jagʻ",
        True,
    ),
    (
        "Vinirlar",
        "gigiyena",
        "E.max keramik vinir",
        "Керамический винир E.max",
        "E.max ceramic veneer",
        3_900_000,
        4_600_000,
        "1 tish",
        False,
    ),
    (
        "Breketlar",
        "ortodontiya",
        "Metall breket tizimi (2 jagʻ)",
        "Металлическая брекет-система (2 челюсти)",
        "Metal braces (both arches)",
        8_500_000,
        None,
        "toʻliq kurs",
        False,
    ),
    (
        "Breketlar",
        "ortodontiya",
        "Keramik breket tizimi (2 jagʻ)",
        "Керамическая брекет-система (2 челюсти)",
        "Ceramic braces (both arches)",
        12_000_000,
        14_000_000,
        "toʻliq kurs",
        False,
    ),
    (
        "Elayner (shaffof kappa)",
        "ortodontiya",
        "Elayner toʻliq kurs",
        "Элайнеры полный курс",
        "Full aligner course",
        18_000_000,
        26_000_000,
        "toʻliq kurs",
        False,
    ),
    (
        None,
        "terapiya",
        "Konsultatsiya va koʻrik",
        "Консультация и осмотр",
        "Consultation and examination",
        0,
        None,
        "1 tashrif",
        False,
    ),
    (
        None,
        "terapiya",
        "KLKT (3D rentgen)",
        "КЛКТ (3D-снимок)",
        "CBCT (3D scan)",
        250_000,
        None,
        "1 tasvir",
        False,
    ),
]

UNITS = {
    "1 implant": {"uz": "1 implant", "ru": "1 имплант", "en": "per implant"},
    "1 tish": {"uz": "1 tish", "ru": "1 зуб", "en": "per tooth"},
    "1 jagʻ": {"uz": "1 jagʻ", "ru": "1 челюсть", "en": "per arch"},
    "1 seans": {"uz": "1 seans", "ru": "1 сеанс", "en": "per session"},
    "1 tomon": {"uz": "1 tomon", "ru": "1 сторона", "en": "per side"},
    "1 tashrif": {"uz": "1 tashrif", "ru": "1 визит", "en": "per visit"},
    "1 tasvir": {"uz": "1 tasvir", "ru": "1 снимок", "en": "per scan"},
    "2 jagʻ": {"uz": "2 jagʻ", "ru": "2 челюсти", "en": "both arches"},
    "toʻliq kurs": {"uz": "toʻliq kurs", "ru": "полный курс", "en": "full course"},
}

DOCTORS = [
    (
        "Dilshod Raximov",
        "Дилшод Рахимов",
        "Dilshod Rakhimov",
        {
            "uz": "Implantolog, jarroh-stomatolog",
            "ru": "Имплантолог, хирург-стоматолог",
            "en": "Implantologist, oral surgeon",
        },
        14,
        {
            "uz": "Toshkent tibbiyot akademiyasi (2010). Straumann va Osstem boʻyicha xalqaro sertifikat.",
            "ru": "Ташкентская медицинская академия (2010). Международные сертификаты Straumann и Osstem.",
            "en": "Tashkent Medical Academy (2010). International Straumann and Osstem certification.",
        },
        "uz,ru,en",
        1,
    ),
    (
        "Nigora Yusupova",
        "Нигора Юсупова",
        "Nigora Yusupova",
        {"uz": "Ortodont", "ru": "Ортодонт", "en": "Orthodontist"},
        9,
        {
            "uz": "TashPMI (2015). Damon va Invisalign tizimlari boʻyicha sertifikatlangan.",
            "ru": "ТашПМИ (2015). Сертифицирована по системам Damon и Invisalign.",
            "en": "Tashkent Paediatric Medical Institute (2015). Damon and Invisalign certified.",
        },
        "uz,ru",
        2,
    ),
    (
        "Kamola Ergasheva",
        "Камола Эргашева",
        "Kamola Ergasheva",
        {
            "uz": "Terapevt-stomatolog, endodontist",
            "ru": "Терапевт-стоматолог, эндодонтист",
            "en": "Restorative dentist, endodontist",
        },
        11,
        {
            "uz": "Toshkent davlat stomatologiya instituti (2013). Mikroskopik endodontiya boʻyicha malaka.",
            "ru": "Ташкентский государственный стоматологический институт (2013). Специализация — эндодонтия под микроскопом.",
            "en": "Tashkent State Dental Institute (2013). Specialist in microscope endodontics.",
        },
        "uz,ru",
        3,
    ),
    (
        "Sardor Toshmatov",
        "Сардор Тошматов",
        "Sardor Toshmatov",
        {"uz": "Ortoped-stomatolog", "ru": "Ортопед-стоматолог", "en": "Prosthodontist"},
        16,
        {
            "uz": "TashMI (2008). Sirkoniy protezlash va raqamli tabassum dizayni boʻyicha ekspert.",
            "ru": "ТашМИ (2008). Эксперт по циркониевому протезированию и цифровому дизайну улыбки.",
            "en": "Tashkent Medical Institute (2008). Expert in zirconia prosthetics and digital smile design.",
        },
        "uz,ru,en",
        4,
    ),
    (
        "Malika Qodirova",
        "Малика Кадырова",
        "Malika Qodirova",
        {"uz": "Bolalar stomatologi", "ru": "Детский стоматолог", "en": "Paediatric dentist"},
        7,
        {
            "uz": "TashPMI (2017). Bolalar bilan ishlash psixologiyasi boʻyicha qoʻshimcha taʼlim.",
            "ru": "ТашПМИ (2017). Дополнительное образование по детской психологии.",
            "en": "Tashkent Paediatric Medical Institute (2017). Additional training in child psychology.",
        },
        "uz,ru",
        5,
    ),
]

REVIEWS = [
    (
        "Aziza Karimova",
        5,
        {
            "uz": "Implantatsiya qildirdim, umuman ogʻriq sezmadim. Dilshod aka har bosqichni tushuntirib bordi.",
            "ru": "Делала имплантацию — совсем не было больно. Дилшод объяснял каждый этап.",
            "en": "I had an implant placed and felt no pain at all. Dilshod explained every step.",
        },
        "google",
        "https://maps.google.com/",
        30,
    ),
    (
        "Jasur Toshpoʻlatov",
        5,
        {
            "uz": "Bolamni Malika shifokorga olib bordim — qoʻrqmadi, aksincha yana bormoqchi.",
            "ru": "Привёл ребёнка к Малике — не испугался, наоборот, хочет прийти снова.",
            "en": "I took my son to Malika — he wasn't scared and actually wants to go back.",
        },
        "2gis",
        "https://2gis.uz/",
        45,
    ),
    (
        "Nodira Ismoilova",
        5,
        {
            "uz": "Breket qoʻydirganimga 8 oy boʻldi, natija allaqachon koʻrinib turibdi.",
            "ru": "Ношу брекеты 8 месяцев — результат уже виден.",
            "en": "Eight months into my braces and the result is already visible.",
        },
        "manual",
        "",
        60,
    ),
    (
        "Bekzod Rahmonov",
        5,
        {
            "uz": "Gigiyenaga bordim, 40 daqiqada tishlar butunlay boshqacha boʻldi. Narxi ham halol.",
            "ru": "Ходил на гигиену — за 40 минут зубы стали совершенно другими. Цена честная.",
            "en": "Went in for hygiene — 40 minutes and my teeth felt completely different. Fair price too.",
        },
        "google",
        "https://maps.google.com/",
        20,
    ),
    (
        "Zilola Abdullayeva",
        5,
        {
            "uz": "Vinir qoʻydirdim. Sardor aka avval raqamli maket koʻrsatdi, natija aynan shunday chiqdi.",
            "ru": "Поставила виниры. Сардор сначала показал цифровой макет — результат точно такой.",
            "en": "I had veneers done. Sardor showed a digital preview first and the result matched exactly.",
        },
        "instagram",
        "",
        75,
    ),
    (
        "Oybek Nazarov",
        4,
        {
            "uz": "Kanal davoladim, sifat yaxshi. Faqat navbat biroz kutdirdi.",
            "ru": "Лечил каналы, качество хорошее. Только в очереди немного подождал.",
            "en": "Had a root canal — good quality. Only downside was a short wait.",
        },
        "yandex",
        "https://yandex.uz/maps/",
        90,
    ),
    (
        "Dilnoza Sattorova",
        5,
        {
            "uz": "Aqli tishimni olishdi, qoʻrqib borgandim — 20 daqiqada tugadi.",
            "ru": "Удаляли зуб мудрости, шла со страхом — закончилось за 20 минут.",
            "en": "I was nervous about my wisdom tooth — it was over in 20 minutes.",
        },
        "google",
        "https://maps.google.com/",
        15,
    ),
    (
        "Rustam Yoʻldoshev",
        5,
        {
            "uz": "Butun oilamiz shu yerda davolanadi. Toza, zamonaviy, xodimlar xushmuomala.",
            "ru": "Вся наша семья лечится здесь. Чисто, современно, персонал вежливый.",
            "en": "Our whole family goes here. Clean, modern, and the staff are courteous.",
        },
        "2gis",
        "https://2gis.uz/",
        120,
    ),
    (
        "Shahnoza Yusupova",
        5,
        {
            "uz": "Oqartirish qildirdim — tabiiy koʻrinadi, sunʼiy emas. Juda mamnunman.",
            "ru": "Сделала отбеливание — выглядит естественно, не искусственно. Очень довольна.",
            "en": "I had whitening done — it looks natural, not artificial. Very pleased.",
        },
        "manual",
        "",
        50,
    ),
    (
        "Farrux Ahmedov",
        5,
        {
            "uz": "Protez qoʻydirdim, 3 yildan beri hech qanday muammo yoʻq.",
            "ru": "Поставил протез — уже 3 года никаких проблем.",
            "en": "Had a prosthesis fitted — three years on, no problems at all.",
        },
        "manual",
        "",
        200,
    ),
    (
        "Gulnora Xolmatova",
        4,
        {
            "uz": "Narxlar shaffof, oldindan aytishdi. Bu juda muhim.",
            "ru": "Цены прозрачные, всё сказали заранее. Это очень важно.",
            "en": "Prices are transparent and quoted upfront. That matters a lot.",
        },
        "yandex",
        "https://yandex.uz/maps/",
        35,
    ),
    (
        "Ulugʻbek Mirzayev",
        5,
        {
            "uz": "KLKT tasvirini oʻsha kuni berishdi, boshqa klinikaga borish shart boʻlmadi.",
            "ru": "КЛКТ-снимок отдали в тот же день, не пришлось ехать в другую клинику.",
            "en": "They did the CBCT scan the same day — no need to visit another clinic.",
        },
        "google",
        "https://maps.google.com/",
        10,
    ),
]

FAQS = [
    (
        {
            "uz": "Implantatsiya ogʻriqlimi?",
            "ru": "Имплантация — это больно?",
            "en": "Is getting an implant painful?",
        },
        {
            "uz": "Yoʻq. Muolaja mahalliy anesteziya ostida oʻtkaziladi va odatda 40–60 daqiqa davom etadi. Anesteziya taʼsiri tugagach yengil noqulaylik boʻlishi mumkin — u 2–3 kunda oʻtadi.",
            "ru": "Нет. Процедура проходит под местной анестезией и занимает 40–60 минут. После её окончания возможен лёгкий дискомфорт, который проходит за 2–3 дня.",
            "en": "No. The procedure is done under local anaesthetic and usually takes 40–60 minutes. Mild discomfort afterwards typically settles within two to three days.",
        },
    ),
    (
        {
            "uz": "Implant qancha xizmat qiladi?",
            "ru": "Сколько служит имплант?",
            "en": "How long do implants last?",
        },
        {
            "uz": "Toʻgʻri parvarish va yiliga ikki marta profilaktik koʻrikda implantlar 20 yil va undan koʻproq xizmat qiladi. Biz oʻrnatgan implantlarga 10 yillik kafolat beramiz.",
            "ru": "При правильном уходе и профилактическом осмотре дважды в год импланты служат 20 лет и более. Мы даём гарантию 10 лет.",
            "en": "With proper care and check-ups twice a year, implants last 20 years or more. We provide a 10-year warranty.",
        },
    ),
    (
        {
            "uz": "Bolani necha yoshdan olib kelish kerak?",
            "ru": "С какого возраста приводить ребёнка?",
            "en": "At what age should a child first visit?",
        },
        {
            "uz": "Birinchi tashrif birinchi tish chiqqandan keyin, taxminan 1 yoshda tavsiya etiladi. Davolash uchun emas — bolani muhitga oʻrgatish uchun.",
            "ru": "Первый визит рекомендуется после прорезывания первого зуба, примерно в 1 год. Не для лечения, а для знакомства с обстановкой.",
            "en": "We recommend a first visit after the first tooth appears, around age one — not for treatment, but to get comfortable with the setting.",
        },
    ),
    (
        {
            "uz": "Toʻlovni boʻlib toʻlash mumkinmi?",
            "ru": "Можно ли оплатить в рассрочку?",
            "en": "Do you offer instalment payments?",
        },
        {
            "uz": "Ha. 3, 6 va 12 oylik boʻlib toʻlash mavjud. Shartlarni registraturada yoki telefon orqali aniqlashtiring.",
            "ru": "Да. Доступна рассрочка на 3, 6 и 12 месяцев. Условия уточняйте на ресепшене или по телефону.",
            "en": "Yes. We offer 3, 6 and 12-month instalment plans. Ask at reception or call us for details.",
        },
    ),
    (
        {
            "uz": "Gigiyenani qanchalik tez-tez qilish kerak?",
            "ru": "Как часто делать гигиену?",
            "en": "How often should I have a hygiene visit?",
        },
        {
            "uz": "Yiliga ikki marta. Breket taqadiganlar va chekuvchilarga har 3–4 oyda bir marta tavsiya qilinadi.",
            "ru": "Дважды в год. Тем, кто носит брекеты, и курящим — раз в 3–4 месяца.",
            "en": "Twice a year. Every three to four months if you wear braces or smoke.",
        },
    ),
    (
        {
            "uz": "Homiladorlik davrida tish davolash mumkinmi?",
            "ru": "Можно ли лечить зубы при беременности?",
            "en": "Can I have dental treatment while pregnant?",
        },
        {
            "uz": "Ha, ikkinchi trimestr eng qulay davr. Homiladorlik haqida albatta oldindan xabar bering — biz xavfsiz anesteziya va himoya vositalarini tanlaymiz.",
            "ru": "Да, второй триместр — оптимальный период. Обязательно предупредите о беременности — мы подберём безопасную анестезию и защиту.",
            "en": "Yes — the second trimester is the best window. Do tell us in advance so we can choose safe anaesthesia and protection.",
        },
    ),
    (
        {
            "uz": "Breketni necha yosh qoʻysa boʻladi?",
            "ru": "В каком возрасте можно ставить брекеты?",
            "en": "What age can braces be fitted?",
        },
        {
            "uz": "Doimiy tishlar toʻliq chiqqach, odatda 12 yoshdan. Kattalar uchun yosh chegarasi yoʻq — 40 va 50 yoshdagi bemorlarimiz ham bor.",
            "ru": "После полной смены зубов, обычно с 12 лет. Для взрослых ограничений нет — у нас лечатся пациенты 40 и 50 лет.",
            "en": "Once the permanent teeth are through, usually from age 12. There's no upper limit — we treat patients in their forties and fifties.",
        },
    ),
    (
        {
            "uz": "Qabulga yozilmasdan kelsam boʻladimi?",
            "ru": "Можно прийти без записи?",
            "en": "Can I walk in without an appointment?",
        },
        {
            "uz": "Oʻtkir ogʻriq holatida — albatta, biz sizni navbatsiz qabul qilamiz. Rejali muolajalar uchun oldindan yozilish vaqtingizni tejaydi.",
            "ru": "При острой боли — конечно, примем без очереди. Для плановых процедур запись экономит ваше время.",
            "en": "For acute pain — absolutely, we'll see you without a queue. For planned treatment, booking ahead saves you time.",
        },
    ),
    (
        {
            "uz": "Anesteziyaga allergiyam bor, nima qilay?",
            "ru": "У меня аллергия на анестезию, что делать?",
            "en": "I'm allergic to anaesthetic — what should I do?",
        },
        {
            "uz": "Konsultatsiyada albatta ayting. Bizda bir necha xil preparat bor va allergiya sinovini oʻtkazish imkoniyati mavjud.",
            "ru": "Обязательно скажите на консультации. У нас есть несколько препаратов и возможность провести аллергопробу.",
            "en": "Please mention it at your consultation. We stock several different agents and can arrange allergy testing.",
        },
    ),
    (
        {
            "uz": "KLKT (3D rentgen) zararli emasmi?",
            "ru": "КЛКТ вредно?",
            "en": "Is a CBCT scan harmful?",
        },
        {
            "uz": "Zamonaviy KLKT nurlanishi juda past — bir tasvir taxminan bir soatlik samolyot parvozidagi tabiiy fon nurlanishiga teng.",
            "ru": "Излучение современного КЛКТ очень низкое — один снимок сопоставим с естественным фоном за час авиаперелёта.",
            "en": "Modern CBCT exposure is very low — one scan is comparable to the natural background radiation of an hour-long flight.",
        },
    ),
    (
        {
            "uz": "Oqartirish emalga zarar qiladimi?",
            "ru": "Отбеливание портит эмаль?",
            "en": "Does whitening damage enamel?",
        },
        {
            "uz": "Professional oqartirish emalni yemirmaydi. Muolajadan keyin 48 soat davomida rangli ichimlik va ovqatdan saqlanish kifoya.",
            "ru": "Профессиональное отбеливание не разрушает эмаль. После процедуры достаточно 48 часов воздержаться от красящих продуктов.",
            "en": "Professional whitening doesn't erode enamel. Just avoid staining food and drink for 48 hours afterwards.",
        },
    ),
    (
        {
            "uz": "Kafolat beriladimi?",
            "ru": "Даёте ли вы гарантию?",
            "en": "Do you provide a warranty?",
        },
        {
            "uz": "Ha. Plombalarga 2 yil, protezlarga 5 yil, implantlarga 10 yil kafolat. Kafolat shartlari shartnomada yoziladi.",
            "ru": "Да. На пломбы — 2 года, на протезы — 5 лет, на импланты — 10 лет. Условия прописаны в договоре.",
            "en": "Yes — two years on fillings, five on prosthetics and ten on implants. The terms are set out in your treatment agreement.",
        },
    ),
    (
        {
            "uz": "Qaysi tillarda xizmat koʻrsatasiz?",
            "ru": "На каких языках вы обслуживаете?",
            "en": "What languages do you speak?",
        },
        {
            "uz": "Oʻzbek va rus tillarida — barcha shifokorlar. Ingliz tilida — Dilshod Raximov va Sardor Toshmatov.",
            "ru": "На узбекском и русском — все врачи. На английском — Дилшод Рахимов и Сардор Тошматов.",
            "en": "Uzbek and Russian with every dentist. English with Dilshod Rakhimov and Sardor Toshmatov.",
        },
    ),
    (
        {"uz": "Avtoturargoh bormi?", "ru": "Есть ли парковка?", "en": "Is there parking?"},
        {
            "uz": "Ha, bino oldida bepul avtoturargoh mavjud. Metro «Shahriston» bekatidan 5 daqiqalik piyoda yoʻl.",
            "ru": "Да, перед зданием бесплатная парковка. От станции метро «Шахристан» — 5 минут пешком.",
            "en": "Yes, there's free parking in front of the building. It's a five-minute walk from Shahriston metro station.",
        },
    ),
]

BLOG_POSTS = [
    (
        {
            "uz": "Implantatsiyadan keyin nima qilish kerak",
            "ru": "Что делать после имплантации",
            "en": "What to do after an implant",
        },
        {
            "uz": "Implant oʻrnatilgandan keyingi birinchi hafta natijani belgilaydi. Nima mumkin, nima mumkin emas — qadam-baqadam.",
            "ru": "Первая неделя после установки импланта определяет результат. Что можно и чего нельзя — по шагам.",
            "en": "The first week after implant placement shapes the result. Here's what to do — and what to avoid.",
        },
        {
            "uz": "Birinchi 24 soat ichida issiq ovqat va ichimlikdan saqlaning. Muolaja joyiga muz bosish shishni kamaytiradi — 10 daqiqa bosib, 10 daqiqa dam bering.\n\nBirinchi hafta davomida qattiq ovqat chaynamang va operatsiya qilingan tomonda ovqatlanmang. Tish yuvishni tashlab qoʻymang — faqat muolaja joyini ehtiyotkorlik bilan aylanib oʻting.\n\nShifokor yozgan antibiotik va ogʻriq qoldiruvchini toʻliq kursda iching. Chekish — implant tushib ketishining eng koʻp uchraydigan sababi; kamida 2 hafta saqlaning.\n\nShish 3-kundan keyin ham kuchayib borsa yoki harorat koʻtarilsa — darhol klinikaga murojaat qiling.",
            "ru": "В первые 24 часа откажитесь от горячей еды и напитков. Лёд на область уменьшает отёк: 10 минут прикладывать, 10 минут перерыв.\n\nВ течение первой недели не жуйте твёрдую пищу и не ешьте на прооперированной стороне. Не бросайте чистку зубов — просто аккуратно обходите область вмешательства.\n\nПропейте назначенный антибиотик и обезболивающее полным курсом. Курение — самая частая причина отторжения импланта; воздержитесь минимум 2 недели.\n\nЕсли отёк усиливается после 3-го дня или поднялась температура — сразу обратитесь в клинику.",
            "en": "Avoid hot food and drink for the first 24 hours. Ice on the area reduces swelling — ten minutes on, ten minutes off.\n\nFor the first week, skip hard foods and don't chew on the treated side. Keep brushing, just work carefully around the surgical site.\n\nFinish the full course of any antibiotics and painkillers you were prescribed. Smoking is the most common cause of implant failure — avoid it for at least two weeks.\n\nIf swelling increases after day three or you develop a fever, contact the clinic immediately.",
        },
        0,
        3,
    ),
    (
        {
            "uz": "Bolalarda kariesning oldini olish",
            "ru": "Профилактика кариеса у детей",
            "en": "Preventing cavities in children",
        },
        {
            "uz": "Sut tishlari baribir tushadi degan fikr eng qimmatga tushadigan xato. Nega va nima qilish kerak.",
            "ru": "«Молочные всё равно выпадут» — самая дорогая ошибка. Почему и что делать.",
            "en": "\"They're only baby teeth\" is the costliest myth in paediatric dentistry. Here's why.",
        },
        {
            "uz": "Sut tishidagi karies doimiy tish kurtagiga taʼsir qiladi va uning emalini zaiflashtiradi. Shuning uchun sut tishi ham davolanadi.\n\nBirinchi tish chiqqandan boshlab kuniga ikki marta yumshoq choʻtka bilan tozalang. 3 yoshgacha guruch donasi hajmidagi, keyin noʻxat hajmidagi ftorli pasta yetarli.\n\nKechasi shirin ichimlik yoki sut bilan uxlatmang — bu «boʻtalar karisi»ning asosiy sababi.\n\nHar 6 oyda profilaktik koʻrik va kerak boʻlsa fissuralarni germetiklash kariesni 80% gacha kamaytiradi.",
            "ru": "Кариес молочного зуба влияет на зачаток постоянного и ослабляет его эмаль. Поэтому молочные зубы тоже лечат.\n\nЧистите зубы дважды в день мягкой щёткой с момента прорезывания первого зуба. До 3 лет достаточно пасты размером с рисовое зерно, затем — с горошину.\n\nНе укладывайте ребёнка спать со сладким напитком или молоком — это главная причина «бутылочного кариеса».\n\nОсмотр каждые 6 месяцев и герметизация фиссур снижают риск кариеса до 80%.",
            "en": "Decay in a baby tooth affects the developing permanent tooth beneath it and weakens its enamel. That's why baby teeth are treated too.\n\nBrush twice daily with a soft brush from the moment the first tooth appears. A rice-grain of fluoride paste until age three, then a pea-sized amount.\n\nNever put a child to bed with a sweet drink or milk — it's the main cause of bottle caries.\n\nCheck-ups every six months and fissure sealants where needed cut cavity risk by up to 80%.",
        },
        0,
        12,
    ),
    (
        {
            "uz": "Breket yoki elayner: qaysi birini tanlash",
            "ru": "Брекеты или элайнеры: что выбрать",
            "en": "Braces or aligners: which to choose",
        },
        {
            "uz": "Ikkalasi ham tishni tekislaydi, lekin har xil holatda. Halol taqqoslash.",
            "ru": "Оба выравнивают зубы, но подходят в разных случаях. Честное сравнение.",
            "en": "Both straighten teeth, but they suit different cases. An honest comparison.",
        },
        {
            "uz": "Breket murakkab holatlarda kuchliroq: tishlar juda qiyshiq boʻlsa, tishlash buzilgan boʻlsa yoki tish burilishi katta boʻlsa — breket ishonchliroq natija beradi.\n\nElayner esteti kroq va olib qoʻyish mumkin, lekin kuniga 20–22 soat taqilishi shart. Intizom boʻlmasa natija kechikadi.\n\nNarx: breket 8,5 mln soʻmdan, elayner 18 mln soʻmdan boshlanadi.\n\nQaysi biri sizga mos ekanini KLKT tasviri va ogʻiz maketisiz aytib boʻlmaydi. Konsultatsiya bepul — kelib koʻring.",
            "ru": "Брекеты сильнее в сложных случаях: выраженная скученность, нарушенный прикус или значительный поворот зуба — брекеты дают более предсказуемый результат.\n\nЭлайнеры эстетичнее и снимаются, но носить их нужно 20–22 часа в сутки. Без дисциплины результат затягивается.\n\nЦена: брекеты — от 8,5 млн сум, элайнеры — от 18 млн сум.\n\nЧто подойдёт именно вам, нельзя сказать без КЛКТ и слепка. Консультация бесплатная.",
            "en": "Braces are stronger in complex cases: severe crowding, bite problems or significantly rotated teeth all respond more predictably to fixed braces.\n\nAligners are more discreet and removable, but must be worn 20–22 hours a day. Without that discipline, treatment drags on.\n\nCost: braces from 8.5m so'm, aligners from 18m so'm.\n\nWhich suits you can't be decided without a CBCT scan and an impression. The consultation is free.",
        },
        0,
        20,
    ),
    (
        {
            "uz": "Tish ogʻrigʻida uyda nima qilish mumkin",
            "ru": "Что можно сделать дома при зубной боли",
            "en": "What you can do at home for toothache",
        },
        {
            "uz": "Shifokorga yetguncha holatni yengillashtiradigan — va aksincha, zarar qiladigan — narsalar.",
            "ru": "Что облегчит состояние до визита к врачу — и что, наоборот, навредит.",
            "en": "What helps until you can see a dentist — and what makes things worse.",
        },
        {
            "uz": "Iliq tuzli suv bilan chayqang (bir stakan suvga yarim choy qoshiq tuz). Bu yalligʻlanishni biroz kamaytiradi.\n\nOgʻriq qoldiruvchi iching — ibuprofen odatda tish ogʻrigʻida paratsetamolga qaraganda samaraliroq.\n\n**Qilmang:** aspirinni tishga bosmang — u shilliq qavatni kuydiradi. Issiq kompress qoʻymang — yiring boʻlsa, u tarqalishini tezlashtiradi.\n\nOgʻriq 2 kundan ortiq davom etsa, yuz shishsa yoki harorat koʻtarilsa — bu shoshilinch holat, kutmang.",
            "ru": "Полощите тёплой солёной водой (половину чайной ложки соли на стакан). Это немного снимет воспаление.\n\nПримите обезболивающее — при зубной боли ибупрофен обычно эффективнее парацетамола.\n\n**Не делайте:** не прикладывайте аспирин к зубу — он вызывает ожог слизистой. Не грейте — при гнойном процессе это ускорит распространение.\n\nЕсли боль длится больше 2 дней, отекло лицо или поднялась температура — это неотложная ситуация, не ждите.",
            "en": "Rinse with warm salt water (half a teaspoon per glass). It takes the edge off the inflammation.\n\nTake a painkiller — ibuprofen usually works better than paracetamol for dental pain.\n\n**Don't:** put aspirin directly on the tooth — it burns the soft tissue. Don't apply heat — if there's an abscess, warmth spreads it faster.\n\nIf pain lasts more than two days, your face swells, or you develop a fever, treat it as urgent.",
        },
        0,
        40,
    ),
    (
        {
            "uz": "Professional gigiyena: nima uchun choʻtka yetarli emas",
            "ru": "Профгигиена: почему щётки недостаточно",
            "en": "Why brushing alone isn't enough",
        },
        {
            "uz": "Uy sharoitida yetib bormaydigan 30% yuza va u yerda nima sodir boʻladi.",
            "ru": "30% поверхностей, недоступных дома, и что там происходит.",
            "en": "The 30% of tooth surface you can't reach at home — and what happens there.",
        },
        {
            "uz": "Choʻtka tish yuzasining taxminan 70% ini tozalaydi. Qolgan qismi — tishlar orasi va milk osti — u yerda gʻubor toʻplanadi va 24–72 soat ichida qattiq toshga aylanadi.\n\nToshni faqat ultratovush bilan olib tashlash mumkin. Uni «kuchliroq choʻtkalash» bilan yoʻqotib boʻlmaydi — aksincha, emal yeyiladi va milk chekinadi.\n\nMuolaja 40 daqiqa davom etadi: ultratovush, Air Flow va sayqallash. Ogʻriqsiz.\n\nYiliga ikki marta gigiyena parodontit va tish yoʻqotishning eng arzon profilaktikasi.",
            "ru": "Щётка очищает около 70% поверхности зуба. Остальное — межзубные промежутки и поддесневая область, где скапливается налёт и за 24–72 часа превращается в твёрдый камень.\n\nКамень снимается только ультразвуком. «Чистить сильнее» не поможет — наоборот, стирается эмаль и опускается десна.\n\nПроцедура занимает 40 минут: ультразвук, Air Flow и полировка. Безболезненно.\n\nГигиена дважды в год — самая дешёвая профилактика пародонтита и потери зубов.",
            "en": "A toothbrush cleans roughly 70% of the tooth surface. The rest — between teeth and below the gumline — collects plaque that hardens into calculus within 24–72 hours.\n\nCalculus can only be removed with ultrasonics. Brushing harder won't shift it; it just wears enamel and recedes the gum.\n\nThe appointment takes 40 minutes: ultrasonic scaling, Air Flow and polishing. Painless.\n\nHygiene twice a year is the cheapest insurance against gum disease and tooth loss.",
        },
        0,
        55,
    ),
    (
        {
            "uz": "Sirkoniy va metall-keramika tojlar farqi",
            "ru": "Разница между циркониевыми и металлокерамическими коронками",
            "en": "Zirconia vs metal-ceramic crowns",
        },
        {
            "uz": "Narx farqi ikki baravar. Qachon ortiqcha toʻlash maʼnoli, qachon yoʻq.",
            "ru": "Разница в цене — вдвое. Когда переплата оправдана, а когда нет.",
            "en": "The price gap is roughly double. When the extra cost is worth it — and when it isn't.",
        },
        {
            "uz": "Metall-keramika ishonchli va arzonroq, lekin metall asos yorugʻlikni oʻtkazmaydi — shuning uchun old tishlarda biroz «oʻlik» koʻrinadi va yillar oʻtib milk chetida koʻkish chiziq paydo boʻlishi mumkin.\n\nSirkoniy yorugʻlikni tabiiy tish kabi oʻtkazadi va milkka doʻstona. Old tishlar va tabassum zonasi uchun aynan shu tavsiya etiladi.\n\nOrqa tishlarda, chaynash yuki katta boʻlgan joyda, ikkalasi ham bardosh beradi — u yerda metall-keramika mantiqiy tanlov.\n\nQisqasi: koʻrinadigan joyga sirkoniy, koʻrinmaydigan joyga metall-keramika.",
            "ru": "Металлокерамика надёжна и дешевле, но металлический каркас не пропускает свет — на передних зубах коронка выглядит «глухой», а через годы у края десны может появиться синеватая полоска.\n\nЦирконий пропускает свет как естественный зуб и дружелюбен к десне. Именно его рекомендуют для фронтальной зоны улыбки.\n\nНа жевательных зубах, где нагрузка выше, справляются оба — там металлокерамика логичный выбор.\n\nКоротко: цирконий — на видимое, металлокерамика — на невидимое.",
            "en": "Metal-ceramic is reliable and cheaper, but the metal core blocks light — on front teeth the crown looks flat, and a bluish line can appear at the gum margin over the years.\n\nZirconia transmits light like natural enamel and is kinder to the gum. It's the recommended choice for the smile zone.\n\nOn back teeth, where chewing load matters more than looks, both perform well — metal-ceramic is the sensible pick there.\n\nIn short: zirconia where it shows, metal-ceramic where it doesn't.",
        },
        0,
        70,
    ),
]

STATIC_PAGES = [
    (
        "privacy",
        {"uz": "Maxfiylik siyosati", "ru": "Политика конфиденциальности", "en": "Privacy policy"},
        {
            "uz": "Ushbu siyosat «Oq Marvarid Dental» klinikasi saytida shaxsiy maʼlumotlarni qanday yigʻishi va qayta ishlashini tushuntiradi.\n\n**Qanday maʼlumot yigʻamiz.** Qabulga yozilish yoki qoʻngʻiroq buyurtma qilish formasi orqali: ismingiz, telefon raqamingiz va (ixtiyoriy) elektron pochtangiz hamda tanlagan xizmatingiz. Biz formalar orqali tashxis, kasallik tarixi yoki boshqa tibbiy maʼlumot **soʻramaymiz**.\n\n**Nima uchun.** Faqat siz bilan bogʻlanish, qabul vaqtini tasdiqlash va eslatma yuborish uchun.\n\n**Kim koʻradi.** Maʼlumotlar klinikaning registratura xodimlariga va tegishli shifokorga koʻrinadi. Uchinchi shaxslarga sotilmaydi va berilmaydi.\n\n**Qayerda saqlanadi.** Serverlar Oʻzbekiston Respublikasi hududida joylashgan.\n\n**Qancha saqlanadi.** Murojaat va yakunlangan qabullar 12 oydan keyin avtomatik oʻchiriladi yoki anonimlashtiriladi.\n\n**Sizning huquqingiz.** Istalgan vaqtda +998 71 200 40 40 raqamiga qoʻngʻiroq qilib maʼlumotlaringizni oʻchirishni soʻrashingiz mumkin.",
            "ru": "Настоящая политика объясняет, как клиника «Oq Marvarid Dental» собирает и обрабатывает персональные данные на сайте.\n\n**Какие данные мы собираем.** Через форму записи или заказа звонка: имя, номер телефона и (по желанию) электронную почту, а также выбранную услугу. Мы **не запрашиваем** через формы диагноз, историю болезни или иные медицинские сведения.\n\n**Зачем.** Только чтобы связаться с вами, подтвердить время приёма и отправить напоминание.\n\n**Кто видит.** Данные доступны администраторам ресепшена и соответствующему врачу. Третьим лицам не продаются и не передаются.\n\n**Где хранятся.** Серверы расположены на территории Республики Узбекистан.\n\n**Сколько хранятся.** Обращения и завершённые приёмы удаляются или обезличиваются через 12 месяцев.\n\n**Ваши права.** Вы можете в любой момент позвонить на +998 71 200 40 40 и попросить удалить ваши данные.",
            "en": "This policy explains how Oq Marvarid Dental collects and processes personal data through this website.\n\n**What we collect.** Through the booking or call-back form: your name, phone number, optionally your email, and the service you selected. We do **not** ask for diagnoses, medical history or other clinical information through web forms.\n\n**Why.** Solely to contact you, confirm your appointment time and send reminders.\n\n**Who sees it.** Reception staff and the relevant dentist. It is never sold or passed to third parties.\n\n**Where it is stored.** On servers located within the Republic of Uzbekistan.\n\n**How long.** Enquiries and completed appointments are deleted or anonymised after 12 months.\n\n**Your rights.** You may call +998 71 200 40 40 at any time to request deletion of your data.",
        },
    ),
    (
        "offer",
        {"uz": "Ommaviy oferta", "ru": "Публичная оферта", "en": "Public offer"},
        {
            "uz": "Sayt orqali qabulga yozilish klinikaga tashrif vaqtini band qilish taklifidir va tibbiy xizmat koʻrsatish shartnomasi hisoblanmaydi.\n\nDavolash shartnomasi klinikada, koʻrikdan soʻng, yozma ravishda tuziladi. Saytdagi narxlar maʼlumot uchun va yakuniy emas — aniq summa koʻrikdan va davolash rejasidan keyin belgilanadi.\n\nQabulni bekor qilish yoki koʻchirish uchun tashrifdan kamida 2 soat oldin xabar berishingizni soʻraymiz.",
            "ru": "Запись через сайт является предложением забронировать время визита и не является договором оказания медицинских услуг.\n\nДоговор на лечение заключается в клинике письменно после осмотра. Цены на сайте носят справочный характер и не являются окончательными — точная сумма определяется после осмотра и составления плана лечения.\n\nПросим сообщать об отмене или переносе приёма не позднее чем за 2 часа до визита.",
            "en": "Booking through this website is an offer to reserve a visit time and does not constitute a contract for medical services.\n\nA treatment agreement is signed at the clinic, in writing, after examination. Prices shown here are indicative, not final — the exact amount is set after examination and treatment planning.\n\nPlease let us know at least two hours in advance if you need to cancel or reschedule.",
        },
    ),
    (
        "terms",
        {"uz": "Foydalanish shartlari", "ru": "Условия использования", "en": "Terms of use"},
        {
            "uz": "Saytdagi matnlar umumiy maʼlumot uchun va shifokor maslahatining oʻrnini bosmaydi. Har qanday simptom yoki ogʻriqda mutaxassisga murojaat qiling.\n\nSayt materiallari (matn, rasm, logotip) klinikaga tegishli. Ularni tijorat maqsadida koʻchirish uchun yozma ruxsat kerak.\n\nBiz saytni istalgan vaqtda yangilash yoki oʻzgartirish huquqini saqlab qolamiz.",
            "ru": "Материалы сайта носят общий информационный характер и не заменяют консультацию врача. При любых симптомах или боли обратитесь к специалисту.\n\nМатериалы сайта (тексты, изображения, логотип) принадлежат клинике. Для коммерческого копирования требуется письменное разрешение.\n\nМы оставляем за собой право обновлять и изменять сайт в любое время.",
            "en": "Content on this site is general information and does not replace a dentist's advice. If you have symptoms or pain, please see a professional.\n\nSite materials (text, images, logo) belong to the clinic. Written permission is required for commercial reuse.\n\nWe reserve the right to update or change the site at any time.",
        },
    ),
]


# ─────────────────────────── Yordamchilar ───────────────────────────
def set_i18n(obj, field: str, values: dict) -> None:
    """
    Tarjima qilinadigan maydonni uchala tilda oʻrnatadi.

    Tartib muhim: bazaviy maydon AVVAL yoziladi (modeltranslation uni faol til
    ustuniga koʻchiradi), soʻng har bir til ustuni aniq yoziladi — shunda oxirgi
    soʻz til ustunlarida qoladi va bazaviy ustun uz qiymatini saqlaydi.
    """
    setattr(obj, field, values["uz"])
    for lang, text in values.items():
        setattr(obj, f"{field}_{lang}", text)


SEED_ASSETS = Path(settings.BASE_DIR) / "apps" / "core" / "seed_assets"


def attach_image(obj, field: str, rel_path: str) -> bool:
    """seed_assets/ dan rasmni ImageField'ga idempotent ulaydi (deterministik nom).
    Asset yoʻq boʻlsa jimgina oʻtkazadi — dizayn fallback'i ishlaydi. save=False."""
    src = SEED_ASSETS / rel_path
    if not src.exists():
        return False
    f = obj._meta.get_field(field)
    upload_to = f.upload_to if isinstance(f.upload_to, str) else ""
    basename = rel_path.split("/")[-1]
    target = pathlib.Path(settings.MEDIA_ROOT) / upload_to / basename
    if target.exists():
        target.unlink()  # qayta yozish — accumulation yoʻq
    with open(src, "rb") as fh:
        getattr(obj, field).save(basename, File(fh), save=False)
    return True


class Command(BaseCommand):
    help = "Demo content yaratadi: Oq Marvarid Dental (uz/ru/en)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Avval mavjud demo content'ni oʻchiradi.",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        # Seed davomida faol til qatʼiy uz — aks holda bazaviy ustunlarga
        # tasodifiy til qiymati tushadi.
        with translation.override("uz"):
            self._seed(**opts)

    def _seed(self, **opts):
        if opts["reset"]:
            self._reset()

        self._settings()
        self._hours()
        self._counters()
        cats = self._categories()
        services = self._services(cats)
        self._prices(cats, services)
        self._faqs()
        doctors = self._doctors()
        self._schedules(doctors)
        self._link_services_to_doctors(services, doctors)
        self._reviews()
        self._blog(doctors)
        self._cases(services, doctors)
        self._gallery()
        self._pages()
        self._appointments(doctors, services)
        self._leads(services)

        self.stdout.write(self.style.SUCCESS("\n✓ Demo content tayyor — Oq Marvarid Dental"))
        self._summary()

    # ---------- reset ----------
    def _reset(self):
        self.stdout.write("Demo content oʻchirilmoqda…")
        for model in (
            Appointment,
            Lead,
            Post,
            CasePair,
            GalleryImage,
            Review,
            PriceItem,
            Faq,
            Service,
            ServiceCategory,
            DoctorSchedule,
            TimeOff,
            Doctor,
            StaticPage,
            StatCounter,
            WorkingHours,
        ):
            model.objects.all().delete()

    # ---------- core ----------
    def _settings(self):
        s = ClinicSettings.load()
        for field, values in CLINIC.items():
            set_i18n(s, field, values)
        s.phone_primary = "+998712004040"
        s.phone_secondary = "+998901234567"
        s.telegram_username = "oqmarvarid_clinic"
        s.telegram_channel_url = "https://t.me/oqmarvarid_clinic"
        s.instagram_url = "https://instagram.com/oqmarvarid_dental"
        s.email = "info@oqmarvarid.uz"
        s.brand_color, s.accent_color = "#0E7C86", "#F2A65A"
        s.map_lat, s.map_lng = M("41.363500"), M("69.288700")
        s.yandex_maps_url = "https://yandex.uz/maps/10335/tashkent/"
        s.two_gis_url = "https://2gis.uz/tashkent"
        s.legal_entity_name = 'MChJ "OQ MARVARID DENTAL"'
        s.prices_visible = True
        s.booking_enabled = True
        attach_image(s, "logo", "brand/logo.png")
        attach_image(s, "favicon", "brand/favicon.png")
        attach_image(s, "hero_image", "hero/hero.jpg")
        attach_image(s, "og_image", "og/og-default.png")
        s.save()
        self.stdout.write("  · sozlamalar (+ brand rasmlari)")

    def _hours(self):
        for weekday, opens, closes, closed, note in WORKING_HOURS:
            wh, _ = WorkingHours.objects.get_or_create(weekday=weekday)
            wh.opens, wh.closes, wh.is_closed = opens, closes, closed
            set_i18n(wh, "note", note)
            wh.save()
        self.stdout.write("  · ish vaqti (7 kun)")

    def _counters(self):
        for order, (label, value, suffix, icon) in enumerate(COUNTERS, 1):
            c, _ = StatCounter.objects.get_or_create(value=value, defaults={"order": order})
            set_i18n(c, "label", label)
            c.suffix, c.icon, c.order = suffix, icon, order
            c.save()
        self.stdout.write(f"  · counterlar ({len(COUNTERS)})")

    # ---------- services ----------
    def _categories(self):
        out = {}
        for order, (key, titles, icon) in enumerate(CATEGORIES, 1):
            cat, _ = ServiceCategory.objects.get_or_create(
                slug_uz=key, defaults={"title": titles["uz"]}
            )
            set_i18n(cat, "title", titles)
            for lang in ("uz", "ru", "en"):
                setattr(cat, f"slug_{lang}", key)
            cat.slug, cat.order, cat.icon = key, order, icon
            cat.save()
            out[key] = cat
        self.stdout.write(f"  · kategoriyalar ({len(out)})")
        return out

    def _services(self, cats):
        from apps.core.utils.slugify_uz import slugify_uz

        out = {}
        for cat_key, uz, ru, en, ex_uz, ex_ru, ex_en, dur, featured, order in SERVICES:
            svc, _ = Service.objects.get_or_create(
                slug_uz=slugify_uz(uz),
                defaults={"category": cats[cat_key], "title": uz},
            )
            svc.category = cats[cat_key]
            set_i18n(svc, "title", {"uz": uz, "ru": ru, "en": en})
            set_i18n(svc, "excerpt", {"uz": ex_uz, "ru": ex_ru, "en": ex_en})
            for lang, text in (("uz", uz), ("ru", ru), ("en", en)):
                setattr(svc, f"slug_{lang}", slugify_uz(text))
            svc.slug = slugify_uz(uz)
            svc.duration_minutes, svc.is_featured, svc.order = dur, featured, order
            if uz in sc.SERVICE_BODIES:
                set_i18n(svc, "body", sc.SERVICE_BODIES[uz])
            if uz in sc.SERVICE_COVERS:
                attach_image(svc, "cover", sc.SERVICE_COVERS[uz])
            svc.save()
            out[uz] = svc
        self.stdout.write(
            f"  · xizmatlar ({len(out)}, {sum(1 for s in SERVICES if s[8])} featured)"
        )
        return out

    def _prices(self, cats, services):
        for order, (svc_title, cat_key, uz, ru, en, pfrom, pto, unit, promo) in enumerate(
            PRICES, 1
        ):
            item, _ = PriceItem.objects.get_or_create(
                title_uz=uz,
                category=cats[cat_key],
                defaults={"price_from": M(pfrom), "title": uz},
            )
            set_i18n(item, "title", {"uz": uz, "ru": ru, "en": en})
            set_i18n(item, "unit", UNITS.get(unit, {"uz": unit, "ru": unit, "en": unit}))
            set_i18n(item, "qualifier", {"uz": "dan boshlab", "ru": "от", "en": "from"})
            item.service = services.get(svc_title)
            item.price_from = M(pfrom)
            item.price_to = M(pto) if pto else None
            item.is_promo, item.order = promo, order
            if promo:
                set_i18n(item, "promo_note", {"uz": "Aksiya", "ru": "Акция", "en": "Promo"})
            item.save()
        self.stdout.write(f"  · narxlar ({len(PRICES)})")

    def _faqs(self):
        for order, (q, a) in enumerate(FAQS, 1):
            faq, _ = Faq.objects.get_or_create(
                question_uz=q["uz"], defaults={"question": q["uz"], "answer": a["uz"]}
            )
            set_i18n(faq, "question", q)
            set_i18n(faq, "answer", a)
            faq.order = order
            faq.save()
        self.stdout.write(f"  · FAQ ({len(FAQS)})")

    # ---------- team ----------
    def _doctors(self):
        from apps.core.utils.slugify_uz import slugify_uz

        out = {}
        for uz, ru, en, spec, years, edu, langs, order in DOCTORS:
            doc, _ = Doctor.objects.get_or_create(
                slug_uz=slugify_uz(uz), defaults={"full_name": uz, "specialization": spec["uz"]}
            )
            set_i18n(doc, "full_name", {"uz": uz, "ru": ru, "en": en})
            set_i18n(doc, "specialization", spec)
            set_i18n(doc, "education", edu)
            for lang, text in (("uz", uz), ("ru", ru), ("en", en)):
                setattr(doc, f"slug_{lang}", slugify_uz(text))
            doc.slug = slugify_uz(uz)
            doc.experience_years, doc.languages_spoken, doc.order = years, langs, order
            doc.is_bookable = doc.is_active = True
            if uz in sc.DOCTOR_BIOS:
                set_i18n(doc, "bio", sc.DOCTOR_BIOS[uz])
            if uz in sc.DOCTOR_CERTS:
                set_i18n(doc, "certificates", sc.DOCTOR_CERTS[uz])
            if uz in sc.DOCTOR_ALTS:
                set_i18n(doc, "photo_alt", sc.DOCTOR_ALTS[uz])
            if uz in sc.DOCTOR_PHOTOS:
                attach_image(doc, "photo", sc.DOCTOR_PHOTOS[uz])
            doc.save()
            out[uz] = doc
        self.stdout.write(f"  · shifokorlar ({len(out)})")
        return out

    def _schedules(self, doctors):
        DoctorSchedule.objects.all().delete()
        for doc in doctors.values():
            for weekday in range(0, 6):  # Du–Sha
                DoctorSchedule.objects.create(
                    doctor=doc,
                    weekday=weekday,
                    start_time=time(9, 0),
                    end_time=time(16, 0) if weekday == 5 else time(19, 0),
                    slot_minutes=30,
                    break_start=time(13, 0),
                    break_end=time(14, 0),
                )
        # 2 ta dam olish — slot engine ularni koʻrinarli chiqarib tashlashi uchun
        TimeOff.objects.all().delete()
        now = timezone.now()
        docs = list(doctors.values())
        TimeOff.objects.create(
            doctor=docs[1],
            starts_at=now + timedelta(days=5),
            ends_at=now + timedelta(days=12),
            reason="Malaka oshirish kursi",
        )
        TimeOff.objects.create(
            doctor=None,
            starts_at=now + timedelta(days=20),
            ends_at=now + timedelta(days=21),
            reason="Bayram — klinika yopiq",
        )
        self.stdout.write(f"  · jadvallar ({DoctorSchedule.objects.count()}) + dam olish (2)")

    def _link_services_to_doctors(self, services, doctors):
        by_spec = {
            "Implantatsiya": ["Dilshod Raximov", "Sardor Toshmatov"],
            "Aqli tish olib tashlash": ["Dilshod Raximov"],
            "Suyak toʻqimasi tiklash": ["Dilshod Raximov"],
            "Protezlash": ["Sardor Toshmatov"],
            "Vinirlar": ["Sardor Toshmatov"],
            "Breketlar": ["Nigora Yusupova"],
            "Elayner (shaffof kappa)": ["Nigora Yusupova"],
            "Ildiz kanali davolash": ["Kamola Ergasheva"],
            "Karies davolash": ["Kamola Ergasheva"],
            "Milk kasalliklari davolash": ["Kamola Ergasheva"],
            "Bolalar stomatologiyasi": ["Malika Qodirova"],
            "Estetik plombalash": ["Kamola Ergasheva", "Sardor Toshmatov"],
            "Professional gigiyena": ["Kamola Ergasheva", "Malika Qodirova"],
            "Tishlarni oqartirish": ["Sardor Toshmatov"],
        }
        for svc_title, doc_names in by_spec.items():
            svc = services.get(svc_title)
            if svc:
                svc.doctors.set([doctors[n] for n in doc_names if n in doctors])

    # ---------- content ----------
    def _reviews(self):
        today = date.today()
        for order, (name, rating, text, source, url, days_ago) in enumerate(REVIEWS, 1):
            r, _ = Review.objects.get_or_create(
                author_name=name, defaults={"rating": rating, "text": text["uz"]}
            )
            set_i18n(r, "text", text)
            r.rating, r.source, r.source_url = rating, source, url
            r.reviewed_at = today - timedelta(days=days_ago)
            r.is_featured = order <= 4
            r.order = order
            r.save()
        self.stdout.write(f"  · sharhlar ({len(REVIEWS)})")

    def _blog(self, doctors):
        from apps.core.utils.slugify_uz import slugify_uz

        authors = list(doctors.values())
        now = timezone.now()
        for i, (title, excerpt, body, _unused, days_ago) in enumerate(BLOG_POSTS):
            post, _ = Post.objects.get_or_create(
                slug_uz=slugify_uz(title["uz"]), defaults={"title": title["uz"], "body": body["uz"]}
            )
            set_i18n(post, "title", title)
            set_i18n(post, "excerpt", excerpt)
            set_i18n(post, "body", body)
            for lang, text in title.items():
                setattr(post, f"slug_{lang}", slugify_uz(text))
            post.slug = slugify_uz(title["uz"])
            post.author = authors[i % len(authors)]
            post.published_at = now - timedelta(days=days_ago)
            post.is_published = True
            if i in sc.BLOG_COVERS:
                attach_image(post, "cover", sc.BLOG_COVERS[i])
            post.save()
        self.stdout.write(f"  · blog ({len(BLOG_POSTS)})")

    def _cases(self, services, doctors):
        from apps.core.utils.slugify_uz import slugify_uz

        for order, case in enumerate(sc.CASES, 1):
            title_uz = case["title"]["uz"]
            obj, _ = CasePair.objects.get_or_create(
                slug_uz=slugify_uz(title_uz), defaults={"title": title_uz}
            )
            set_i18n(obj, "title", case["title"])
            for lang, text in case["title"].items():
                setattr(obj, f"slug_{lang}", slugify_uz(text))
            obj.slug = slugify_uz(title_uz)
            set_i18n(obj, "treatment_summary", case["summary"])
            set_i18n(obj, "duration_note", case["duration"])
            # "Demo namunasi" izohi caption sifatida
            set_i18n(obj, "caption", {lang: sc.demo_note(lang) for lang in ("uz", "ru", "en")})
            obj.service = services.get(case["service"])
            obj.doctor = doctors.get(case["doctor"])
            obj.consent_on_file = True
            obj.is_published = True
            obj.is_featured = case["featured"]
            obj.order = order
            attach_image(obj, "image_before", case["before"])
            attach_image(obj, "image_after", case["after"])
            obj.save()
        self.stdout.write(f"  · ishlarimiz / before-after ({len(sc.CASES)})")

    def _gallery(self):
        for order, (rel, category, cap) in enumerate(sc.GALLERY, 1):
            obj, created = GalleryImage.objects.get_or_create(
                caption_uz=cap["uz"], defaults={"category": category}
            )
            set_i18n(obj, "caption", cap)
            set_i18n(obj, "alt", cap)
            obj.category = category
            obj.order = order
            attach_image(obj, "image", rel)
            obj.save()
        self.stdout.write(f"  · galereya ({len(sc.GALLERY)})")

    def _pages(self):
        for key, title, body in STATIC_PAGES:
            page, _ = StaticPage.objects.get_or_create(
                key=key, defaults={"title": title["uz"], "body": body["uz"]}
            )
            set_i18n(page, "title", title)
            set_i18n(page, "body", body)
            page.save()
        self.stdout.write(f"  · statik sahifalar ({len(STATIC_PAGES)})")

    # ---------- demo faoliyat ----------
    def _appointments(self, doctors, services):
        """Admin birinchi kirishda tirik koʻrinishi uchun."""
        Appointment.objects.all().delete()
        docs = list(doctors.values())
        svcs = list(services.values())
        now = timezone.localtime()
        today_9 = now.replace(hour=9, minute=0, second=0, microsecond=0)

        rows = [
            (
                "Aziza Karimova",
                "+998901112233",
                0,
                0,
                today_9 + timedelta(hours=1),
                AppointmentStatus.CONFIRMED,
            ),
            (
                "Bekzod Rahmonov",
                "+998902223344",
                1,
                3,
                today_9 + timedelta(hours=3),
                AppointmentStatus.CONFIRMED,
            ),
            (
                "Nodira Ismoilova",
                "+998903334455",
                2,
                4,
                today_9 + timedelta(days=1, hours=2),
                AppointmentStatus.PENDING,
            ),
            (
                "Jasur Toshpoʻlatov",
                "+998904445566",
                4,
                10,
                today_9 + timedelta(days=1, hours=5),
                AppointmentStatus.PENDING,
            ),
            (
                "Dilnoza Sattorova",
                "+998905556677",
                0,
                5,
                today_9 - timedelta(days=3),
                AppointmentStatus.COMPLETED,
            ),
            (
                "Oybek Nazarov",
                "+998906667788",
                3,
                12,
                today_9 - timedelta(days=7, hours=-2),
                AppointmentStatus.NO_SHOW,
            ),
        ]
        for name, phone, doc_i, svc_i, starts, status in rows:
            svc = svcs[svc_i % len(svcs)]
            Appointment.objects.create(
                doctor=docs[doc_i % len(docs)],
                service=svc,
                patient_name=name,
                phone=phone,
                starts_at=starts,
                ends_at=starts + timedelta(minutes=svc.duration_minutes),
                status=status,
                source=Appointment.Source.WEB,
                consent_given_at=starts - timedelta(days=1),
                consent_text_version="v1",
            )
        self.stdout.write(f"  · qabullar ({len(rows)})")

    def _leads(self, services):
        Lead.objects.all().delete()
        svcs = list(services.values())
        rows = [
            (
                "Shahnoza Yusupova",
                "+998907778899",
                Lead.Kind.CALLBACK,
                Lead.Status.NEW,
                0,
                "Oqartirish narxini bilmoqchiman",
            ),
            (
                "Rustam Yoʻldoshev",
                "+998908889900",
                Lead.Kind.PRICE_REQUEST,
                Lead.Status.NEW,
                1,
                "Implant uchun boʻlib toʻlash bormi?",
            ),
            (
                "Gulnora Xolmatova",
                "+998909990011",
                Lead.Kind.CONTACT,
                Lead.Status.IN_PROGRESS,
                3,
                "Bolam uchun konsultatsiya",
            ),
            (
                "Ulugʻbek Mirzayev",
                "+998901234500",
                Lead.Kind.CALLBACK,
                Lead.Status.WON,
                5,
                "Breket boʻyicha maslahat",
            ),
            ("Farrux Ahmedov", "+998902345600", Lead.Kind.CALLBACK, Lead.Status.LOST, 9, ""),
        ]
        for name, phone, kind, status, svc_i, msg in rows:
            Lead.objects.create(
                name=name,
                phone=phone,
                kind=kind,
                status=status,
                service=svcs[svc_i % len(svcs)],
                message=msg,
                locale="uz",
                source_page="/uz/",
                consent_given_at=timezone.now(),
            )
        self.stdout.write(f"  · murojaatlar ({len(rows)})")

    def _summary(self):
        rows = [
            ("Xizmat kategoriyasi", ServiceCategory.objects.count()),
            ("Xizmat", Service.objects.count()),
            ("Narx", PriceItem.objects.count()),
            ("FAQ", Faq.objects.count()),
            ("Shifokor", Doctor.objects.count()),
            ("Shifokor jadvali", DoctorSchedule.objects.count()),
            ("Sharh", Review.objects.count()),
            ("Blog maqolasi", Post.objects.count()),
            ("Statik sahifa", StaticPage.objects.count()),
            ("Qabul", Appointment.objects.count()),
            ("Murojaat", Lead.objects.count()),
        ]
        width = max(len(r[0]) for r in rows) + 2
        for label, count in rows:
            self.stdout.write(f"    {label:<{width}} {count:>3}")
