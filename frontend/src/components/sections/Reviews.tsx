import { getTranslations } from "next-intl/server";
import type { Review } from "@/lib/api";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Card } from "@/components/ui/Card";
import { Rating } from "@/components/ui/Rating";
import { Badge } from "@/components/ui/Badge";

const SOURCE_LABEL: Record<string, string> = {
  google: "Google",
  "2gis": "2GIS",
  yandex: "Yandex",
  instagram: "Instagram",
  manual: "",
};

export async function Reviews({
  reviews,
  summary,
}: {
  reviews: Review[];
  summary: { average: number; total: number } | null;
}) {
  const t = await getTranslations("nav");
  if (!reviews.length) return null;

  return (
    <Section id="sharhlar" tone="surface">
      <SectionHeading
        title={t("reviews")}
        action={
          summary?.total ? (
            <p className="text-sm text-ink-subtle">
              <span className="text-lg font-bold text-ink">{summary.average}</span>
              <span className="text-accent"> ★ </span>
              <span>· {summary.total}</span>
            </p>
          ) : undefined
        }
      />
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {reviews.slice(0, 6).map((r) => {
          // Schema'da `rating`/`source` ixtiyoriy (model default'i bor) — himoyalanamiz.
          const rating = r.rating ?? 5;
          const sourceLabel = r.source ? SOURCE_LABEL[r.source] : "";
          return (
            <Card key={r.id} className="p-6">
              <figure>
                <Rating value={rating} />
                <blockquote className="mt-3 text-sm leading-relaxed text-ink-muted">
                  {r.text}
                </blockquote>
                <figcaption className="mt-4 flex items-center justify-between text-xs">
                  <span className="font-semibold text-ink">{r.author_name}</span>
                  {sourceLabel ? <Badge tone="neutral">{sourceLabel}</Badge> : null}
                </figcaption>
              </figure>
            </Card>
          );
        })}
      </div>
    </Section>
  );
}
