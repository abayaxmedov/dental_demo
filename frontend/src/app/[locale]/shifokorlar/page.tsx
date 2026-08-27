import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { getDoctors } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { Link } from "@/i18n/navigation";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Card } from "@/components/ui/Card";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { Empty } from "@/components/ui/Empty";

type Params = Promise<{ locale: string }>;
const LANG: Record<string, string> = { uz: "OʻZ", ru: "РУ", en: "EN", tr: "TR" };

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pages.doctors" });
  return { title: t("title"), description: t("lead"), alternates: buildAlternates({ pathname: "/shifokorlar", currentLocale: locale as never }) };
}

export default async function DoctorsPage({ params }: { params: Params }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const doctors = await getDoctors(locale);
  const t = await getTranslations("pages.doctors");
  const tc = await getTranslations("pages.crumbs");

  return (
    <Section>
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("title") }]} />
      <SectionHeading title={t("title")} lead={t("lead")} />
      {doctors.length === 0 ? (
        <Empty title={t("title")} />
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {doctors.map((d) => (
            <Link key={d.id} href={{ pathname: "/shifokorlar/[slug]", params: { slug: d.slug ?? "" } }}>
              <Card interactive className="flex h-full gap-4 p-5">
                <Avatar image={d.photo} name={d.full_name} size={72} />
                <div className="min-w-0">
                  <h2 className="font-display text-lg font-bold text-ink">{d.full_name}</h2>
                  <p className="mt-0.5 text-sm text-brand">{d.specialization}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-ink-subtle">
                    <span>{d.experience_years} {t("years")}</span>
                    {(d.languages ?? []).map((l) => (
                      <Badge key={l} tone="neutral">{LANG[l] ?? l.toUpperCase()}</Badge>
                    ))}
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </Section>
  );
}
