import { getTranslations } from "next-intl/server";
import type { PriceItem } from "@/lib/api";
import { formatSum } from "@/lib/format";

export async function Prices({
  prices,
  locale,
}: {
  prices: PriceItem[];
  locale: string;
}) {
  const t = await getTranslations("nav");
  // Bosh sahifada teaser — birinchi 8 qator
  const rows = prices.slice(0, 8);
  if (!rows.length) return null;

  return (
    <section id="narxlar" className="border-b border-slate-100 bg-slate-50/60 scroll-mt-20">
      <div className="mx-auto max-w-4xl px-4 py-16 sm:py-20">
        <h2 className="font-display text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
          {t("prices")}
        </h2>
        <div className="mt-10 overflow-hidden rounded-2xl border border-slate-200 bg-white">
          <table className="w-full text-left text-sm">
            <tbody className="divide-y divide-slate-100">
              {rows.map((p) => (
                <tr key={p.id} className="transition hover:bg-slate-50">
                  <td className="px-5 py-4">
                    <span className="font-medium text-slate-900">{p.title}</span>
                    {p.is_promo && p.promo_note ? (
                      <span className="ml-2 rounded bg-accent/15 px-2 py-0.5 text-xs font-semibold text-amber-700">
                        {p.promo_note}
                      </span>
                    ) : null}
                    {p.unit ? (
                      <span className="ml-2 text-xs text-slate-400">/ {p.unit}</span>
                    ) : null}
                  </td>
                  <td className="whitespace-nowrap px-5 py-4 text-right font-semibold text-slate-900">
                    {Number(p.price_from) === 0 ? (
                      <span className="text-brand">—</span>
                    ) : (
                      <>
                        <span className="text-xs font-normal text-slate-400">
                          {p.qualifier}{" "}
                        </span>
                        {formatSum(p.price_from, locale)}
                        <span className="ml-1 text-xs font-normal text-slate-400">
                          {p.currency}
                        </span>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
