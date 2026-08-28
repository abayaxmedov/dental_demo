import { getTranslations } from "next-intl/server";
import type { Faq as FaqItem } from "@/lib/api";
import { Section, SectionHeading } from "@/components/ui/Section";

export async function Faq({ faqs }: { faqs: FaqItem[] }) {
  const t = await getTranslations("nav");
  if (!faqs.length) return null;

  return (
    <Section tone="muted" width="3xl">
      <SectionHeading title="FAQ" />
      <div className="divide-y divide-line rounded-2xl border border-line bg-surface">
        {faqs.slice(0, 8).map((f) => (
          <details key={f.id} className="group px-6 py-4">
            <summary className="flex min-h-11 cursor-pointer list-none items-center font-medium text-ink marker:hidden [&::-webkit-details-marker]:hidden">
              <span className="flex items-start justify-between gap-4">
                {f.question}
                <span
                  className="mt-1 shrink-0 text-brand transition group-open:rotate-45"
                  aria-hidden
                >
                  +
                </span>
              </span>
            </summary>
            <p className="mt-3 text-sm leading-relaxed text-ink-muted">{f.answer}</p>
          </details>
        ))}
      </div>
      <p className="sr-only">{t("contact")}</p>
    </Section>
  );
}
