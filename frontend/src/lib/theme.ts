// Metadata rang literallari (theme-color, PWA manifest) — bular CSS'dan OLDIN oʻqiladi,
// shuning uchun CSS token (`var(--brand)`) ishlatib boʻlmaydi va xom hex SHART.
// globals.css `--brand`/`--surface` bilan qoʻlda sinxron; reskin ikkalasini ham yangilaydi.
// (Bu `.ts` fayl — lint:colors faqat `.tsx` ni tekshiradi, shuning uchun bu yagona ruxsat.)
export const BRAND_THEME_COLOR = "#0e7c86";
export const SURFACE_BG_COLOR = "#ffffff";

const HEX_RE = /^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/;

/**
 * Backend'dan kelgan rang hex ekanini tekshiradi.
 *
 * Qiymat `<html style="--brand:…">` ga injeksiya qilinadi, shuning uchun ishonchsiz
 * qiymat (a) `;` bilan boshqa CSS deklaratsiyasini qoʻshib yuborishi, (b) yaroqsiz rang
 * boʻlib `bg-brand` ni SHAFFOF qilib, oq matnli CTA'larni koʻrinmas qilishi mumkin.
 * Backend'da ham validator bor (HEX_COLOR_VALIDATOR) — bu ikkinchi qatlam, chunki eski
 * yozuvlar migratsiyadan oldin saqlangan boʻlishi mumkin (AUDIT-2026-08-29 / T-FIX-05).
 */
export function isHexColor(value: unknown): value is string {
  return typeof value === "string" && HEX_RE.test(value);
}
