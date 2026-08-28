import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import credits from "@/data/media-credits.json";
import { buildAlternates, localePath } from "@/lib/seo";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { Badge } from "@/components/ui/Badge";

type Params = Promise<{ locale: string }>;

/**
 * Media atributsiya sahifasi (AUDIT-2026-08-29 / T-FIX-06).
 *
 * 28 seed rasmdan 14 tasi **CC-BY** — bu litsenziya muallifni koʻrsatishni HUQUQIY jihatdan
 * TALAB qiladi. Ilgari atributsiya faqat repo ichidagi `ASSETS_LICENSES.md` da edi, yaʼni
 * sotib olgan klinika saytida hech qayerda koʻrinmasdi. Endi footer'dan havola qilinadi.
 *
 * Maʼlumot `src/data/media-credits.json` dan; u backend `seed_assets/manifest.json` dan
 * generatsiya qilinadi va `manage.py check_asset_licenses` ikkalasi mos ekanini tekshiradi.
 */
export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pages.mediaCredits" });
  return {
    title: t("title"),
    description: t("lead"),
    alternates: buildAlternates({ pathname: "/media-litsenziyalar", currentLocale: locale as never }),
  };
}

export default async function MediaCreditsPage({ params }: { params: Params }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("pages.mediaCredits");
  const tc = await getTranslations("nav");

  const required = credits.filter((c) => c.attributionRequired);
  const free = credits.filter((c) => !c.attributionRequired);

  return (
    <Section width="4xl">
      <Breadcrumbs
        items={[
          { label: tc("home"), href: localePath("/", locale as never) },
          { label: t("title") },
        ]}
      />
      <SectionHeading as="h1" title={t("title")} lead={t("lead")} />

      <h2 className="mb-3 text-lg font-bold text-ink">{t("attrRequired")}</h2>
      <CreditTable rows={required} labels={{ file: t("colFile"), author: t("colAuthor"), license: t("colLicense"), source: t("source") }} />

      <h2 className="mb-3 mt-10 text-lg font-bold text-ink">{t("attrFree")}</h2>
      <CreditTable rows={free} labels={{ file: t("colFile"), author: t("colAuthor"), license: t("colLicense"), source: t("source") }} />

      <p className="mt-8 rounded-xl bg-surface-muted px-4 py-3 text-sm text-ink-muted">{t("note")}</p>
    </Section>
  );
}

type Row = (typeof credits)[number];

function CreditTable({
  rows,
  labels,
}: {
  rows: Row[];
  labels: { file: string; author: string; license: string; source: string };
}) {
  if (!rows.length) return null;
  return (
    <div className="overflow-x-auto rounded-2xl border border-line bg-surface">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-line text-xs uppercase tracking-wider text-ink-subtle">
          <tr>
            <th scope="col" className="px-4 py-3 font-semibold">{labels.file}</th>
            <th scope="col" className="px-4 py-3 font-semibold">{labels.author}</th>
            <th scope="col" className="px-4 py-3 font-semibold">{labels.license}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {rows.map((c) => (
            <tr key={c.file}>
              <td className="px-4 py-3 font-mono text-xs text-ink-muted">{c.file}</td>
              <td className="px-4 py-3 text-ink">{c.author}</td>
              <td className="whitespace-nowrap px-4 py-3">
                {c.licenseUrl ? (
                  <a href={c.licenseUrl} rel="license noopener nofollow" target="_blank" className="text-brand hover:underline">
                    <Badge tone="brand">{c.license}</Badge>
                  </a>
                ) : (
                  <Badge tone="neutral">{c.license}</Badge>
                )}
                {c.sourceUrl ? (
                  <>
                    {" "}
                    <a href={c.sourceUrl} rel="noopener nofollow" target="_blank" className="text-xs text-ink-subtle hover:text-brand">
                      ({labels.source})
                    </a>
                  </>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
