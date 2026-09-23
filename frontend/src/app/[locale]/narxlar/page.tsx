import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { getPrices, getServiceCategories, getSiteSettings } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Badge } from "@/components/ui/Badge";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { Empty } from "@/components/ui/Empty";
import { AnchorButton } from "@/components/ui/Button";
import { PriceTag } from "@/components/ui/PriceTag";

type Params = Promise<{ locale: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pages.prices" });
  return { title: t("title"), description: t("lead"), alternates: buildAlternates({ pathname: "/narxlar", currentLocale: locale as never }) };
}

export default async function PricesPage({ params }: { params: Params }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const [settings, prices, categories] = await Promise.all([
    getSiteSettings(locale),
    getPrices(locale),
    getServiceCategories(locale),
  ]);
  if (settings && settings.prices_visible === false) notFound();

  const t = await getTranslations("pages.prices");
  const tc = await getTranslations("pages.crumbs");
  const byCat = new Map<string, typeof prices>();
  for (const p of prices) {
    const k = p.category_slug ?? "—";
    if (!byCat.has(k)) byCat.set(k, []);
    byCat.get(k)!.push(p);
  }
  const catTitle = new Map(categories.map((c) => [c.slug, c.title]));
  const phone = settings?.phone_primary || "+998712004040";
  const groups = [...byCat.entries()];

  return (
    <Section width="4xl">
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("title") }]} />
      <SectionHeading as="h1" title={t("title")} lead={t("lead")} />
      {prices.length === 0 ? (
        <Empty title={t("hidden")} action={<AnchorButton href={`tel:${phone.replace(/\s/g, "")}`}>{phone}</AnchorButton>} />
      ) : (
        <>
          {/* Kategoriya chip'lari — uzun sahifada kerakli boʻlimga tez oʻtish. Header ostida
              yopishib turadi (mobil header 69px, md+ 73px). */}
          {groups.length > 1 ? (
            <nav
              aria-label={t("title")}
              className="sticky top-[69px] z-30 -mx-4 mb-8 flex gap-2 overflow-x-auto overscroll-x-contain border-b border-line bg-surface/95 px-4 py-2.5 backdrop-blur [scrollbar-width:none] sm:-mx-6 sm:px-6 md:top-[73px] lg:-mx-8 lg:px-8"
            >
              {groups.map(([slug]) => (
                <a
                  key={slug}
                  href={`#cat-${slug}`}
                  className="inline-flex min-h-11 shrink-0 items-center rounded-full border border-line bg-surface px-4 text-sm font-medium text-ink transition hover:border-brand hover:text-brand"
                >
                  {catTitle.get(slug) ?? slug}
                </a>
              ))}
            </nav>
          ) : null}
        <div className="space-y-10">
          {groups.map(([slug, items]) => (
            <div key={slug} id={`cat-${slug}`} className="scroll-mt-40">
              <h2 className="mb-4 font-display text-xl font-bold text-ink">{catTitle.get(slug) ?? slug}</h2>
              {/* overflow-x-auto: uzun narx 320px'da kesilmasin, scroll qilinsin (T-RESP-01) */}
              <div className="overflow-x-auto overscroll-x-contain rounded-2xl border border-line">
                <table className="w-full text-sm">
                  <tbody>
                    {items.map((p) => (
                      <tr key={p.id} className="border-b border-line last:border-0">
                        <td className="px-3 py-3.5 text-ink sm:px-4">
                          {p.title}
                          {p.is_promo ? <span className="ml-2"><Badge tone="promo">{p.promo_note || "Aksiya"}</Badge></span> : null}
                          {p.unit ? <span className="mt-0.5 block text-xs text-ink-subtle">{p.unit}</span> : null}
                        </td>
                        <td className="px-3 py-3.5 text-right sm:px-4">
                          <PriceTag value={p.price_from} currency={p.currency} locale={locale} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
        </>
      )}

      <div className="mt-12 rounded-2xl border border-line bg-surface-muted p-6 text-center sm:p-8">
        <h2 className="font-display text-xl font-bold text-ink">{t("callTitle")}</h2>
        <p className="mt-2 text-ink-muted">{t("callLead")}</p>
        <div className="mt-5">
          <AnchorButton href={`tel:${phone.replace(/\s/g, "")}`}>{phone}</AnchorButton>
        </div>
      </div>
    </Section>
  );
}
