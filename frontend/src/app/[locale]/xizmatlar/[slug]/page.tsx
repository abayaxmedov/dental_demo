import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { Clock } from "lucide-react";
import { getSeoRoutes, getService, getSiteSettings } from "@/lib/api";
import { buildAlternates, localeHrefs, localePath, ogBase, ogFor, SITE_URL } from "@/lib/seo";
import { routing } from "@/i18n/routing";
import { formatSum } from "@/lib/format";
import { Link } from "@/i18n/navigation";
import { Section } from "@/components/ui/Section";
import { Card } from "@/components/ui/Card";
import { Avatar } from "@/components/ui/Avatar";
import { Prose } from "@/components/ui/Prose";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { JsonLd } from "@/components/ui/JsonLd";
import { ButtonLink } from "@/components/ui/Button";
import { SetLocaleHrefs } from "@/components/layout/locale-alternates";

type Params = Promise<{ locale: string; slug: string }>;
export const dynamicParams = true;

export async function generateStaticParams() {
  const r = await getSeoRoutes("uz");
  if (!r) return [];
  return r.services.flatMap((s) => routing.locales.map((locale) => ({ locale, slug: s.slugs[locale] })));
}

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale, slug } = await params;
  // settings — og:site_name uchun; Next bir render ichida bir xil fetch'ni dedup qiladi.
  const [s, settings] = await Promise.all([getService(locale, slug), getSiteSettings(locale)]);
  if (!s) return {};
  return {
    title: s.meta_title || s.title,
    description: s.meta_description || s.excerpt,
    alternates: buildAlternates({ pathname: "/xizmatlar/[slug]", slugsByLocale: s.alternates as never, currentLocale: locale as never }),
    openGraph: { ...ogBase(locale, settings?.name), type: "article", images: [ogFor(s)] },
  };
}

export default async function ServiceDetail({ params }: { params: Params }) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  const [s, settings] = await Promise.all([getService(locale, slug), getSiteSettings(locale)]);
  if (!s) notFound();
  const t = await getTranslations("pages.services");
  const tc = await getTranslations("pages.crumbs");
  const hrefs = localeHrefs("/xizmatlar/[slug]", s.alternates as never);
  const prices = settings?.prices_visible === false ? [] : (s.prices ?? []);

  const ld: object[] = [{
    "@context": "https://schema.org", "@type": "MedicalProcedure",
    name: s.title, description: s.meta_description || s.excerpt,
    procedureType: "https://schema.org/TherapeuticProcedure",
    ...(s.body ? { howPerformed: s.body } : {}),
  }];
  if (s.faqs?.length) {
    ld.push({
      "@context": "https://schema.org", "@type": "FAQPage",
      mainEntity: s.faqs.map((f) => ({ "@type": "Question", name: f.question, acceptedAnswer: { "@type": "Answer", text: f.answer } })),
    });
  }

  return (
    <Section width="4xl">
      <SetLocaleHrefs hrefs={hrefs} />
      {ld.map((d, i) => <JsonLd key={i} data={d} />)}
      <Breadcrumbs items={[
        { label: tc("home"), href: localePath("/", locale as never) },
        { label: t("title"), href: localePath("/xizmatlar", locale as never) },
        { label: s.title },
      ]} />

      <h1 className="font-display text-3xl font-extrabold tracking-tight text-ink sm:text-4xl">{s.title}</h1>
      <p className="mt-3 max-w-2xl text-lg text-ink-muted">{s.excerpt}</p>
      <p className="mt-3 inline-flex items-center gap-1.5 text-sm text-ink-subtle">
        <Clock className="h-4 w-4" aria-hidden /> {s.duration_minutes} {t("min")}
      </p>

      {s.cover ? (
        <div className="mt-8">
          <ImageFrameBlock src={s.cover.src ?? undefined} alt={s.title} />
        </div>
      ) : null}

      {s.body ? <div className="mt-8"><Prose text={s.body} /></div> : null}

      {prices.length ? (
        <div className="mt-10 overflow-x-auto overscroll-x-contain rounded-2xl border border-line">
          <table className="w-full text-sm">
            <tbody>
              {prices.map((p) => (
                <tr key={p.id} className="border-b border-line last:border-0">
                  <td className="px-3 py-3.5 text-ink sm:px-4">{p.title}</td>
                  <td className="whitespace-nowrap px-3 py-3.5 text-right font-semibold text-ink sm:px-4">
                    {formatSum(p.price_from, locale)} {p.currency === "UZS" ? "soʻm" : p.currency}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {s.doctors?.length ? (
        <div className="mt-10">
          <h2 className="mb-4 font-display text-xl font-bold text-ink">{t("relatedDoctors")}</h2>
          <div className="flex flex-wrap gap-4">
            {s.doctors.map((d) => (
              <Link key={d.id} href={{ pathname: "/shifokorlar/[slug]", params: { slug: d.slug ?? "" } }} className="flex items-center gap-3">
                <Avatar image={d.photo} name={d.full_name} size={48} />
                <span className="text-sm"><span className="block font-semibold text-ink">{d.full_name}</span><span className="text-brand">{d.specialization}</span></span>
              </Link>
            ))}
          </div>
        </div>
      ) : null}

      {s.faqs?.length ? (
        <div className="mt-10">
          <h2 className="mb-4 font-display text-xl font-bold text-ink">FAQ</h2>
          <div className="divide-y divide-line rounded-2xl border border-line">
            {s.faqs.map((f) => (
              <details key={f.id} className="group px-4 py-3">
                <summary className="cursor-pointer list-none font-medium text-ink [&::-webkit-details-marker]:hidden">{f.question}</summary>
                <p className="mt-2 text-sm text-ink-muted">{f.answer}</p>
              </details>
            ))}
          </div>
        </div>
      ) : null}

      {settings?.booking_enabled !== false ? (
        <div className="mt-10"><ButtonLink href="/" size="lg">{t("book")}</ButtonLink></div>
      ) : null}
    </Section>
  );
}

import { ImageFrame } from "@/components/ui/ImageFrame";
function ImageFrameBlock({ src, alt }: { src?: string; alt: string }) {
  return <ImageFrame image={src ? { src } : null} alt={alt} ratio="16/9" sizes="(min-width:1024px) 56rem, 100vw" priority />;
}
