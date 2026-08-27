import { getTranslations } from "next-intl/server";
import type { Faq as FaqItem } from "@/lib/api";

export async function Faq({ faqs }: { faqs: FaqItem[] }) {
  const t = await getTranslations("nav");
  if (!faqs.length) return null;

  return (
    <section className="border-b border-slate-100 bg-slate-50/60">
      <div className="mx-auto max-w-3xl px-4 py-16 sm:py-20">
        <h2 className="font-display text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
          FAQ
        </h2>
        <div className="mt-8 divide-y divide-slate-200 rounded-2xl border border-slate-200 bg-white">
          {faqs.slice(0, 8).map((f) => (
            <details key={f.id} className="group px-6 py-4">
              <summary className="cursor-pointer list-none font-medium text-slate-900 marker:hidden [&::-webkit-details-marker]:hidden">
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
              <p className="mt-3 text-sm leading-relaxed text-slate-600">{f.answer}</p>
            </details>
          ))}
        </div>
        <p className="sr-only">{t("contact")}</p>
      </div>
    </section>
  );
}
