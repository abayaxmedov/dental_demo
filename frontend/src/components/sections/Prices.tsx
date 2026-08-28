import { getTranslations } from "next-intl/server";
import type { PriceItem } from "@/lib/api";
import { formatSum } from "@/lib/format";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Badge } from "@/components/ui/Badge";

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
    <Section id="narxlar" tone="muted" width="4xl">
      <SectionHeading title={t("prices")} />
      {/* overflow-x-auto (overflow-hidden EMAS): 320px'da uzun narx kesilib yo'qolmasin,
          scroll qilinsin (T-RESP-01). Naqsh: media-litsenziyalar/page.tsx. */}
      <div className="overflow-x-auto overscroll-x-contain rounded-2xl border border-line bg-surface">
        <table className="w-full text-left text-sm">
          <tbody className="divide-y divide-line">
            {rows.map((p) => (
              <tr key={p.id} className="transition hover:bg-surface-muted">
                <td className="px-3 py-4 sm:px-5">
                  <span className="font-medium text-ink">{p.title}</span>
                  {p.is_promo && p.promo_note ? (
                    <span className="ml-2">
                      <Badge tone="promo">{p.promo_note}</Badge>
                    </span>
                  ) : null}
                  {p.unit ? (
                    <span className="ml-2 text-xs text-ink-subtle">/ {p.unit}</span>
                  ) : null}
                </td>
                <td className="whitespace-nowrap px-3 py-4 text-right font-semibold text-ink sm:px-5">
                  {Number(p.price_from) === 0 ? (
                    <span className="text-brand">—</span>
                  ) : (
                    <>
                      <span className="text-xs font-normal text-ink-subtle">
                        {p.qualifier}{" "}
                      </span>
                      {formatSum(p.price_from, locale)}
                      <span className="ml-1 text-xs font-normal text-ink-subtle">
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
    </Section>
  );
}
