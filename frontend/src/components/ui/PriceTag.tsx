import { getTranslations } from "next-intl/server";
import { currencyLabel, formatSum } from "@/lib/format";

/** "dan 350 000 soʻm" yoki "Bepul" — bosh sahifa teaser'i va Narxlar sahifasi uchun bitta format. */
export async function PriceTag({
  value,
  currency,
  locale,
}: {
  value: string | number;
  currency?: string | null;
  locale: string;
}) {
  const t = await getTranslations("pages.prices");
  if (Number(value) === 0) return <span className="font-semibold text-brand">{t("free")}</span>;
  return (
    <span className="whitespace-nowrap">
      <span className="text-sm font-normal text-ink-subtle">{t("from")} </span>
      <span className="font-semibold text-ink">{formatSum(value, locale)}</span>
      <span className="text-sm font-normal text-ink-subtle"> {currencyLabel(currency, locale)}</span>
    </span>
  );
}
