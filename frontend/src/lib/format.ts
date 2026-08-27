/** Formatlash yordamchilari — soʻm, telefon, sana. */

const LOCALE_MAP: Record<string, string> = { uz: "uz-UZ", ru: "ru-RU", en: "en-US" };

/** 4500000 → "4 500 000" (minglik ajratgich bilan). */
export function formatSum(value: string | number, locale = "uz"): string {
  const n = typeof value === "string" ? Number(value) : value;
  if (!Number.isFinite(n)) return String(value);
  return new Intl.NumberFormat(LOCALE_MAP[locale] ?? "uz-UZ", {
    maximumFractionDigits: 0,
  })
    .format(n)
    .replace(/ /g, " ");
}

/** "+998712004040" → "+998 71 200 40 40" */
export function formatPhone(raw: string): string {
  const m = /^\+998(\d{2})(\d{3})(\d{2})(\d{2})$/.exec(raw);
  return m ? `+998 ${m[1]} ${m[2]} ${m[3]} ${m[4]}` : raw;
}

/** `tel:` uchun — boʻshliqsiz. */
export const telHref = (raw: string) => `tel:${raw.replace(/[^\d+]/g, "")}`;

export function formatDate(iso: string | null, locale = "uz"): string {
  if (!iso) return "";
  return new Intl.DateTimeFormat(LOCALE_MAP[locale] ?? "uz-UZ", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(iso));
}

// Intl'ning uz-locale qo'llab-quvvatlashi zaif ("M08") — o'zbekcha oylarni qo'lda beramiz.
const UZ_MONTHS = ["yanvar", "fevral", "mart", "aprel", "may", "iyun",
  "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"];
const UZ_WEEKDAYS = ["yakshanba", "dushanba", "seshanba", "chorshanba", "payshanba", "juma", "shanba"];

/** Qabul vaqtini locale bo'yicha formatlaydi (Asia/Tashkent). uz uchun qo'lda. */
export function formatWhen(iso: string, locale = "uz"): string {
  const d = new Date(iso);
  if (locale === "uz") {
    // Tashkent lokal qismlarini olamiz
    const parts = new Intl.DateTimeFormat("en-GB", {
      timeZone: "Asia/Tashkent", weekday: undefined, day: "numeric",
      month: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit", hour12: false,
    }).formatToParts(d);
    const get = (t: string) => parts.find((p) => p.type === t)?.value ?? "";
    const day = Number(get("day"));
    const month = Number(get("month")) - 1;
    const wd = new Date(
      Number(get("year")), month, day,
    ).getDay();
    return `${day}-${UZ_MONTHS[month]}, ${UZ_WEEKDAYS[wd]} · ${get("hour")}:${get("minute")}`;
  }
  return d.toLocaleString(locale === "ru" ? "ru-RU" : "en-US", {
    weekday: "long", day: "numeric", month: "long",
    hour: "2-digit", minute: "2-digit", timeZone: "Asia/Tashkent",
  });
}

const UZ_WD_SHORT = ["yak", "du", "se", "ch", "pa", "ju", "sha"];
const UZ_MON_SHORT = ["yan", "fev", "mar", "apr", "may", "iyn", "iyl", "avg", "sen", "okt", "noy", "dek"];

/** Kun tasmasi uchun {weekday, dayMonth}. uz qo'lda, ru/en Intl. */
export function formatDayChip(dateStr: string, locale = "uz"): { wd: string; dm: string } {
  const d = new Date(dateStr + "T00:00:00");
  if (locale === "uz") {
    return { wd: UZ_WD_SHORT[d.getDay()], dm: `${d.getDate()} ${UZ_MON_SHORT[d.getMonth()]}` };
  }
  const loc = locale === "ru" ? "ru-RU" : "en-US";
  return {
    wd: d.toLocaleDateString(loc, { weekday: "short" }),
    dm: d.toLocaleDateString(loc, { day: "numeric", month: "short" }),
  };
}
