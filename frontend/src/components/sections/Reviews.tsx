import { getTranslations } from "next-intl/server";
import { Star } from "lucide-react";
import type { Review } from "@/lib/api";

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
    <section id="sharhlar" className="border-b border-slate-100 bg-white scroll-mt-20">
      <div className="mx-auto max-w-6xl px-4 py-16 sm:py-20">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <h2 className="font-display text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
            {t("reviews")}
          </h2>
          {summary?.total ? (
            <p className="text-sm text-slate-500">
              <span className="text-lg font-bold text-slate-900">{summary.average}</span>
              <span className="text-accent"> ★ </span>
              <span>· {summary.total}</span>
            </p>
          ) : null}
        </div>
        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {reviews.slice(0, 6).map((r) => {
            // Schema'da `rating`/`source` ixtiyoriy (model default'i bor) — himoyalanamiz.
            const rating = r.rating ?? 5;
            const sourceLabel = r.source ? SOURCE_LABEL[r.source] : "";
            return (
            <figure key={r.id} className="rounded-2xl border border-slate-200 bg-white p-6">
              <div className="flex items-center gap-0.5" aria-label={`${rating} / 5`}>
                {Array.from({ length: 5 }, (_, i) => (
                  <Star
                    key={i}
                    className={
                      i < rating ? "h-4 w-4 fill-accent text-accent" : "h-4 w-4 text-slate-200"
                    }
                    aria-hidden
                  />
                ))}
              </div>
              <blockquote className="mt-3 text-sm leading-relaxed text-slate-600">
                {r.text}
              </blockquote>
              <figcaption className="mt-4 flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-900">{r.author_name}</span>
                {sourceLabel ? (
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-slate-500">
                    {sourceLabel}
                  </span>
                ) : null}
              </figcaption>
            </figure>
            );
          })}
        </div>
      </div>
    </section>
  );
}
