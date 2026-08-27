import { getPathname } from "@/i18n/navigation";
import { type AppPathname, type Locale, routing } from "@/i18n/routing";

export const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"
).replace(/\/$/, "");

type SlugsByLocale = Partial<Record<Locale, string>>;

/** Berilgan route + locale uchun to'liq (prefiksli) yo'l — masalan "/ru/uslugi/implantatsiya". */
export function localePath(
  pathname: AppPathname,
  locale: Locale,
  slug?: string,
): string {
  const href = slug ? { pathname, params: { slug } } : pathname;
  // getPathname localePrefix:"always" bilan prefiksli yo'l qaytaradi.
  return getPathname({ href: href as never, locale });
}

/** hreflang + canonical: har locale uchun to'liq URL. slugsByLocale — detail sahifalar uchun. */
export function buildAlternates({
  pathname,
  slugsByLocale,
  currentLocale,
}: {
  pathname: AppPathname;
  slugsByLocale?: SlugsByLocale;
  currentLocale: Locale;
}): { canonical: string; languages: Record<string, string> } {
  const languages: Record<string, string> = {};
  for (const loc of routing.locales) {
    languages[loc] = SITE_URL + localePath(pathname, loc, slugsByLocale?.[loc]);
  }
  languages["x-default"] = languages[routing.defaultLocale];
  return {
    canonical: SITE_URL + localePath(pathname, currentLocale, slugsByLocale?.[currentLocale]),
    languages,
  };
}

/** hrefs (locale→to'liq yo'l) — LangSwitcher uchun (prefiksli, domensiz). */
export function localeHrefs(
  pathname: AppPathname,
  slugsByLocale?: SlugsByLocale,
): Record<Locale, string> {
  const out = {} as Record<Locale, string>;
  for (const loc of routing.locales) {
    out[loc] = localePath(pathname, loc, slugsByLocale?.[loc]);
  }
  return out;
}

type OgSource = { og_image?: { src: string } | null; cover?: { src: string } | null; photo?: { src: string } | null };

/** OG rasm URL'i: og_image → cover/photo → default. */
export function ogFor(entity?: OgSource | null): string {
  return (
    entity?.og_image?.src ||
    entity?.cover?.src ||
    entity?.photo?.src ||
    `${SITE_URL}/og-default.png`
  );
}
