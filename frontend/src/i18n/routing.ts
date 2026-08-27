import { defineRouting } from "next-intl/routing";

// Uch til, URL-prefiksli (ADR-002/016). Default uz ham prefikslanadi.
export const routing = defineRouting({
  locales: ["uz", "ru", "en"],
  defaultLocale: "uz",
  localePrefix: "always",
});

export type Locale = (typeof routing.locales)[number];
