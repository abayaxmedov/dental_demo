import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { getDoctor, getSeoRoutes, getSiteSettings } from "@/lib/api";
import { buildAlternates, localeHrefs, localePath, ogBase, ogFor, SITE_URL } from "@/lib/seo";
import { routing } from "@/i18n/routing";
import { Link } from "@/i18n/navigation";
import { Section } from "@/components/ui/Section";
import { Card } from "@/components/ui/Card";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Prose } from "@/components/ui/Prose";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { JsonLd } from "@/components/ui/JsonLd";
import { ButtonLink } from "@/components/ui/Button";
import { SetLocaleHrefs } from "@/components/layout/locale-alternates";

type Params = Promise<{ locale: string; slug: string }>;
const LANG: Record<string, string> = { uz: "OʻZ", ru: "РУ", en: "EN", tr: "TR" };

export const dynamicParams = true;

export async function generateStaticParams() {
  const routes = await getSeoRoutes("uz");
  if (!routes) return [];
  return routes.doctors.flatMap((d) =>
    routing.locales.map((locale) => ({ locale, slug: d.slugs[locale] })),
  );
}

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale, slug } = await params;
  // settings — og:site_name uchun; Next bir render ichida bir xil fetch'ni dedup qiladi.
  const [d, settings] = await Promise.all([getDoctor(locale, slug), getSiteSettings(locale)]);
  if (!d) return {};
  return {
    title: d.meta_title || d.full_name,
    description: d.meta_description || d.bio?.slice(0, 160),
    alternates: buildAlternates({ pathname: "/shifokorlar/[slug]", slugsByLocale: d.alternates as never, currentLocale: locale as never }),
    openGraph: { ...ogBase(locale, settings?.name), type: "profile", images: [ogFor(d)] },
  };
}

export default async function DoctorDetail({ params }: { params: Params }) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  const [d, settings] = await Promise.all([getDoctor(locale, slug), getSiteSettings(locale)]);
  if (!d) notFound();
  const t = await getTranslations("pages.doctors");
  const tc = await getTranslations("pages.crumbs");
  const hrefs = localeHrefs("/shifokorlar/[slug]", d.alternates as never);

  const ld = {
    "@context": "https://schema.org", "@type": "Physician",
    "@id": `${SITE_URL}${localePath("/shifokorlar/[slug]", locale as never, slug)}#physician`,
    name: d.full_name, jobTitle: d.specialization, description: d.bio || undefined,
    image: d.photo?.src || undefined, alumniOf: d.education || undefined,
    knowsLanguage: d.languages || undefined, worksFor: { "@id": `${SITE_URL}/#dentist` },
  };

  return (
    <Section width="4xl">
      <SetLocaleHrefs hrefs={hrefs} />
      <JsonLd data={ld} />
      <Breadcrumbs items={[
        { label: tc("home"), href: localePath("/", locale as never) },
        { label: t("title"), href: localePath("/shifokorlar", locale as never) },
        { label: d.full_name },
      ]} />

      <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
        <Avatar image={d.photo} name={d.full_name} size={128} />
        <div>
          <h1 className="font-display text-3xl font-extrabold tracking-tight text-ink">{d.full_name}</h1>
          <p className="mt-1 text-lg text-brand">{d.specialization}</p>
          <div className="mt-3 flex flex-wrap items-center gap-2 text-sm text-ink-subtle">
            <span>{d.experience_years} {t("years")}</span>
            {(d.languages ?? []).map((l) => <Badge key={l} tone="neutral">{LANG[l] ?? l.toUpperCase()}</Badge>)}
          </div>
        </div>
      </div>

      {d.bio ? <div className="mt-8"><Prose text={d.bio} /></div> : null}

      {d.education ? (
        <div className="mt-8">
          <h2 className="mb-2 font-display text-lg font-bold text-ink">{t("education")}</h2>
          <p className="text-ink-muted">{d.education}</p>
        </div>
      ) : null}
      {d.certificates ? (
        <div className="mt-6">
          <h2 className="mb-2 font-display text-lg font-bold text-ink">{t("certificates")}</h2>
          <p className="text-ink-muted">{d.certificates}</p>
        </div>
      ) : null}

      {d.services?.length ? (
        <div className="mt-8">
          <h2 className="mb-3 font-display text-lg font-bold text-ink">{t("services")}</h2>
          <div className="flex flex-wrap gap-2">
            {d.services.map((s) => (
              <Link key={s.id} href={{ pathname: "/xizmatlar/[slug]", params: { slug: s.slug ?? "" } }}
                className="inline-flex min-h-11 items-center rounded-full border border-line px-3 text-sm text-ink-muted hover:border-brand hover:text-brand">
                {s.title}
              </Link>
            ))}
          </div>
        </div>
      ) : null}

      {d.is_bookable && settings?.booking_enabled !== false ? (
        <div className="mt-10">
          <ButtonLink href="/" size="lg">{t("book")}</ButtonLink>
        </div>
      ) : null}
    </Section>
  );
}
