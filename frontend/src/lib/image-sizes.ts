/**
 * `next/image` `sizes` presetlari (T-RESP-07).
 *
 * `sizes` literal STRINGLARI FAQAT shu faylda yashaydi — `lint-responsive.mjs` R3 qoidasi
 * shuni majbur qiladi. Sabab: literal string komponent ichida qolsa, grid oʻzgarganda
 * (T-RESP-06 kabi) drift qiladi va telefon/planshetga desktop oʻlchamli rasm yuboriladi.
 *
 * Har preset elementning HAQIQIY kengligini (max-w-6xl = 1152px konteyner ichida) ortча
 * eʼlon qiladi (hech qachon kam emas), lekin brauzer nomzodini keraksiz kattalashtirmaydi.
 * Etalon: `blog/[slug]` — konteyner cap'iga aniq mos `(min-width:768px) 48rem, 100vw`.
 */

/** 3 ustunli karta gridi (`sm:grid-cols-2 lg:grid-cols-3`): 100vw → 48vw (640) → 33vw (1024) → ~23rem (cap). */
export const CARD_3UP =
  "(min-width:1216px) 23rem, (min-width:1024px) 31vw, (min-width:640px) 48vw, 100vw";

/** Yarim kenglik (`md:grid-cols-2` — hero/case/about, T-RESP-06 dan keyin). */
export const HALF = "(min-width:1216px) 34rem, (min-width:768px) 50vw, 100vw";

/** Prose kengligidagi rasm (`Section width="3xl"` = 768px cap). */
export const PROSE = "(min-width:768px) 48rem, 100vw";

/** Toʻliq kenglikdagi kontent rasmi (`Section width="4xl"` = 896px cap). */
export const CONTENT_4XL = "(min-width:1024px) 56rem, 100vw";
