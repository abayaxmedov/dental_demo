"""
Oʻzbek (lotin) va rus matnlari uchun slugify (T-P1-12).
`unidecode` yalangʻoch holda `oʻ`/`gʻ` ni buzadi, shuning uchun oʻz jadvalimiz.
"""

import re
import unicodedata

# Oʻzbek lotin maxsus harflari. Tartib muhim: koʻp belgili kombinatsiyalar oldin.
UZ_MAP = {
    "oʻ": "o",
    "Oʻ": "o",
    "o‘": "o",
    "O‘": "o",
    "o'": "o",
    "O'": "o",
    "gʻ": "g",
    "Gʻ": "g",
    "g‘": "g",
    "G‘": "g",
    "g'": "g",
    "G'": "g",
    "sh": "sh",
    "ch": "ch",
    "ʼ": "",
    "ʻ": "",
    "‘": "",
    "’": "",
    "`": "",
}

# Kirill (rus + oʻzbek kirill) → lotin.
CYRILLIC_MAP = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "j",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "i",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
    "ў": "o",
    "қ": "q",
    "ғ": "g",
    "ҳ": "h",
}


def slugify_uz(value: str, max_length: int = 200) -> str:
    """Oʻzbek/rus matnini URL-xavfsiz slug'ga aylantiradi."""
    if not value:
        return ""

    text = value.strip()

    # 1) Oʻzbek maxsus belgilari
    for src, dst in UZ_MAP.items():
        text = text.replace(src, dst)

    # 2) Kirill → lotin (registrni saqlab)
    out = []
    for ch in text:
        lower = ch.lower()
        if lower in CYRILLIC_MAP:
            out.append(CYRILLIC_MAP[lower])
        else:
            out.append(ch)
    text = "".join(out)

    # 3) Qolgan diakritiklarni tashlash
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))

    # 4) Normalizatsiya
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")

    return text[:max_length].rstrip("-")
