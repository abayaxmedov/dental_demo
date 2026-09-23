import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { getFaqs } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { Empty } from "@/components/ui/Empty";
import { JsonLd } from "@/components/ui/JsonLd";

type Params = Promise<{ locale: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pages.faq" });
  return { title: t("title"), description: t("lead"), alternates: buildAlternates({ pathname: "/faq", currentLocale: locale as never }) };
}

export default async function FaqPage({ params }: { params: Params }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const faqs = await getFaqs(locale);
  const t = await getTranslations("pages.faq");
  const tc = await getTranslations("pages.crumbs");
  const ld = { "@context": "https://schema.org", "@type": "FAQPage", mainEntity: faqs.map((f) => ({ "@type": "Question", name: f.question, acceptedAnswer: { "@type": "Answer", text: f.answer } })) };

  return (
    <Section width="3xl">
      {faqs.length ? <JsonLd data={ld} /> : null}
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("title") }]} />
      <SectionHeading as="h1" title={t("title")} lead={t("lead")} />
      {faqs.length === 0 ? (
        <Empty title={t("title")} />
      ) : (
        <div className="divide-y divide-line rounded-2xl border border-line">
          {faqs.map((f) => (
            <details key={f.id} className="group px-4 py-4 sm:px-5">
              <summary className="flex min-h-11 cursor-pointer list-none items-center font-medium text-ink [&::-webkit-details-marker]:hidden">
                <span className="flex w-full items-start justify-between gap-4">
                  {f.question}
                  <span className="shrink-0 text-xl leading-6 text-brand transition group-open:rotate-45" aria-hidden>
                    +
                  </span>
                </span>
              </summary>
              <p className="mt-3 text-sm leading-relaxed text-ink-muted">{f.answer}</p>
            </details>
          ))}
        </div>
      )}
    </Section>
  );
}
