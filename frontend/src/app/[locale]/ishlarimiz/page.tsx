import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { getCases } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { Empty } from "@/components/ui/Empty";
import { CaseSlider } from "@/components/ui/CaseSlider";

type Params = Promise<{ locale: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pages.cases" });
  return { title: t("title"), description: t("lead"), alternates: buildAlternates({ pathname: "/ishlarimiz", currentLocale: locale as never }) };
}

export default async function CasesPage({ params }: { params: Params }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const cases = await getCases(locale);
  const t = await getTranslations("pages.cases");
  const tc = await getTranslations("pages.crumbs");

  return (
    <Section>
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("title") }]} />
      <SectionHeading title={t("title")} lead={t("lead")} />
      {cases.length === 0 ? (
        <Empty title={t("title")} />
      ) : (
        <div className="grid gap-8 lg:grid-cols-2">
          {cases.map((c) => (
            <Card key={c.id} className="overflow-hidden p-4">
              <CaseSlider before={c.image_before} after={c.image_after} beforeLabel={t("before")} afterLabel={t("after")} alt={c.title} />
              <div className="p-2 pt-4">
                <h2 className="font-display text-lg font-bold text-ink">{c.title}</h2>
                {c.treatment_summary ? <p className="mt-1 text-sm text-ink-muted">{c.treatment_summary}</p> : null}
                <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                  {c.service_title ? <Badge tone="brand">{c.service_title}</Badge> : null}
                  {c.duration_note ? <span className="text-ink-subtle">{c.duration_note}</span> : null}
                </div>
                {c.caption ? <p className="mt-3 rounded-lg border-l-2 border-accent bg-accent-100/40 px-3 py-2 text-xs text-ink-muted">{c.caption}</p> : null}
              </div>
            </Card>
          ))}
        </div>
      )}
    </Section>
  );
}
