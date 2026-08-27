import { defineRouting } from "next-intl/routing";

/**
 * Uch til, URL-prefiksli (ADR-002). Segmentlar HAM tarjima qilinadi (pathnames):
 * /uz/xizmatlar · /ru/uslugi · /en/services. Fayl tizimi ichki (uz) nomlarda qoladi;
 * proxy ru/en segmentlarini ichki nomga rewrite qiladi.
 *
 * `/qabul/[token]` ATAYLAB tarjima QILINMAYDI — u Telegram'da yuborilgan jonli havola,
 * segmentini oʻzgartirish eski havolalarni buzadi (bemorga maʼnosiz ham).
 */
export const routing = defineRouting({
  locales: ["uz", "ru", "en"],
  defaultLocale: "uz",
  localePrefix: "always",
  pathnames: {
    "/": "/",
    "/haqimizda": { uz: "/haqimizda", ru: "/o-nas", en: "/about" },
    "/xizmatlar": { uz: "/xizmatlar", ru: "/uslugi", en: "/services" },
    "/xizmatlar/[slug]": {
      uz: "/xizmatlar/[slug]",
      ru: "/uslugi/[slug]",
      en: "/services/[slug]",
    },
    "/narxlar": { uz: "/narxlar", ru: "/tseny", en: "/prices" },
    "/shifokorlar": { uz: "/shifokorlar", ru: "/vrachi", en: "/doctors" },
    "/shifokorlar/[slug]": {
      uz: "/shifokorlar/[slug]",
      ru: "/vrachi/[slug]",
      en: "/doctors/[slug]",
    },
    "/ishlarimiz": { uz: "/ishlarimiz", ru: "/nashi-raboty", en: "/our-work" },
    "/galereya": { uz: "/galereya", ru: "/galereya", en: "/gallery" },
    "/sharhlar": { uz: "/sharhlar", ru: "/otzyvy", en: "/reviews" },
    "/blog": "/blog",
    "/blog/[slug]": "/blog/[slug]",
    "/aloqa": { uz: "/aloqa", ru: "/kontakty", en: "/contact" },
    "/faq": "/faq",
    "/maxfiylik-siyosati": {
      uz: "/maxfiylik-siyosati",
      ru: "/politika-konfidentsialnosti",
      en: "/privacy-policy",
    },
    "/qabul/[token]": "/qabul/[token]",
    "/style-guide": "/style-guide",
  },
});

export type Locale = (typeof routing.locales)[number];
export type AppPathname = keyof typeof routing.pathnames;
