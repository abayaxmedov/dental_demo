import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { Clock } from "lucide-react";
import { getServiceCategories, getServices } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { Link } from "@/i18n/navigation";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Card } from "@/components/ui/Card";
import { ImageFrame } from "@/components/ui/ImageFrame";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { Empty } from "@/components/ui/Empty";
import { ToothMapSection } from "@/components/three/ToothMapSection";
import { CARD_3UP } from "@/lib/image-sizes";

type Params = Promise<{ locale: string }>;
type Search = Promise<{ category?: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pages.services" });
  return { title: t("title"), description: t("lead"), alternates: buildAlternates({ pathname: "/xizmatlar", currentLocale: locale as never }) };
}

export default async function ServicesPage({ params, searchParams }: { params: Params; searchParams: Search }) {
  const { locale } = await params;
  const { category } = await searchParams;
  setRequestLocale(locale);
  const [services, categories] = await Promise.all([
    getServices(locale, category ? { category } : {}),
    getServiceCategories(locale),
  ]);
  const t = await getTranslations("pages.services");
  const tc = await getTranslations("pages.crumbs");

  return (
    <Section>
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("title") }]} />
      <SectionHeading as="h1" title={t("title")} lead={t("lead")} />

      {!category ? (
        <ToothMapSection
          items={services.filter((s) => s.is_featured).slice(0, 7).map((s) => ({ slug: s.slug ?? "", title: s.title }))}
          hint={t("all")}
        />
      ) : null}

      <div className="mb-8 flex flex-wrap gap-2">
        <Link href="/xizmatlar" className={`inline-flex min-h-11 items-center rounded-full border px-4 text-sm font-medium ${!category ? "border-brand bg-brand text-white" : "border-line text-ink-muted hover:border-brand"}`}>
          {t("all")}
        </Link>
        {categories.map((c) => (
          <Link key={c.id} href={{ pathname: "/xizmatlar", query: { category: c.slug } }}
            className={`inline-flex min-h-11 items-center rounded-full border px-4 text-sm font-medium ${category === c.slug ? "border-brand bg-brand text-white" : "border-line text-ink-muted hover:border-brand"}`}>
            {c.title}
          </Link>
        ))}
      </div>

      {services.length === 0 ? (
        <Empty title={t("title")} />
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((s) => (
            <Link key={s.id} href={{ pathname: "/xizmatlar/[slug]", params: { slug: s.slug ?? "" } }}>
              <Card interactive className="flex h-full flex-col overflow-hidden">
                <ImageFrame image={s.cover} alt={s.title} ratio="3/2" rounded="" sizes={CARD_3UP} />
                <div className="flex flex-1 flex-col p-5">
                  <h2 className="font-display text-lg font-bold text-ink">{s.title}</h2>
                  <p className="mt-2 line-clamp-2 flex-1 text-sm text-ink-muted">{s.excerpt}</p>
                  <p className="mt-3 inline-flex items-center gap-1.5 text-xs text-ink-subtle">
                    <Clock className="h-3.5 w-3.5" aria-hidden /> {s.duration_minutes} {t("min")}
                  </p>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </Section>
  );
}
