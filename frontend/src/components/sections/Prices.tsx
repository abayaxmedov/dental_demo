import { getTranslations } from "next-intl/server";
import type { PriceItem } from "@/lib/api";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { PriceTag } from "@/components/ui/PriceTag";

export async function Prices({
  prices,
  locale,
}: {
  prices: PriceItem[];
  locale: string;
}) {
  const t = await getTranslations("nav");
  const tp = await getTranslations("pages.services");
  // Bosh sahifada teaser — birinchi 8 qator
  const rows = prices.slice(0, 8);
  if (!rows.length) return null;

  return (
    <Section id="narxlar" tone="muted" width="4xl">
      <SectionHeading
        title={t("prices")}
        action={<ButtonLink href="/narxlar" variant="secondary">{tp("all")}</ButtonLink>}
      />
      {/* Jadval EMAS, roʻyxat: telefonda nom toʻliq kenglikni oladi, birlik nom ostida,
          narx oʻngda bir qatorda (oldin nom 2–3 qatorga sinardi). */}
      <ul className="divide-y divide-line rounded-2xl border border-line bg-surface">
        {rows.map((p) => (
          <li key={p.id} className="flex items-center justify-between gap-4 px-4 py-3.5 sm:px-5">
            <div className="min-w-0">
              <p className="font-medium text-ink">
                {p.title}
                {p.is_promo && p.promo_note ? (
                  <span className="ml-2 align-middle">
                    <Badge tone="promo">{p.promo_note}</Badge>
                  </span>
                ) : null}
              </p>
              {p.unit ? <p className="mt-0.5 text-xs text-ink-subtle">{p.unit}</p> : null}
            </div>
            <div className="shrink-0 text-right">
              <PriceTag value={p.price_from} currency={p.currency} locale={locale} />
            </div>
          </li>
        ))}
      </ul>
    </Section>
  );
}
