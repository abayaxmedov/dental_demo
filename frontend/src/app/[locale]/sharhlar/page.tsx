import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { getReviews, getReviewSummary } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Card } from "@/components/ui/Card";
import { Avatar } from "@/components/ui/Avatar";
import { Rating } from "@/components/ui/Rating";
import { Badge } from "@/components/ui/Badge";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { Empty } from "@/components/ui/Empty";

type Params = Promise<{ locale: string }>;
const SOURCE: Record<string, string> = { google: "Google", "2gis": "2GIS", yandex: "Yandex", instagram: "Instagram", manual: "" };

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pages.reviews" });
  return { title: t("title"), description: t("lead"), alternates: buildAlternates({ pathname: "/sharhlar", currentLocale: locale as never }) };
}

export default async function ReviewsPage({ params }: { params: Params }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const [reviews, summary] = await Promise.all([getReviews(locale), getReviewSummary(locale)]);
  const t = await getTranslations("pages.reviews");
  const tc = await getTranslations("pages.crumbs");

  return (
    <Section>
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("title") }]} />
      <SectionHeading title={t("title")} lead={t("lead")} />
      {summary && summary.total > 0 ? (
        <div className="mb-8 flex items-center gap-4 rounded-2xl border border-line bg-surface-muted p-5">
          <span className="font-display text-4xl font-extrabold text-ink">{summary.average}</span>
          <div>
            <Rating value={summary.average} />
            <p className="mt-1 text-sm text-ink-subtle">{summary.total} {t("basedOn")}</p>
          </div>
        </div>
      ) : null}
      {reviews.length === 0 ? (
        <Empty title={t("title")} />
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {reviews.map((r) => (
            <Card key={r.id} className="flex flex-col p-5">
              <div className="flex items-center gap-3">
                <Avatar image={r.author_photo} name={r.author_name} size={44} />
                <div>
                  <p className="font-semibold text-ink">{r.author_name}</p>
                  {r.rating ? <Rating value={r.rating} /> : null}
                </div>
              </div>
              <p className="mt-3 flex-1 text-sm text-ink-muted">{r.text}</p>
              {r.source && SOURCE[r.source] ? (
                <div className="mt-3">
                  {r.source_url ? (
                    <a href={r.source_url} target="_blank" rel="nofollow noopener" className="text-xs text-ink-subtle hover:text-brand">
                      {SOURCE[r.source]} · {t("verified")}
                    </a>
                  ) : <Badge tone="neutral">{SOURCE[r.source]}</Badge>}
                </div>
              ) : null}
            </Card>
          ))}
        </div>
      )}
    </Section>
  );
}
