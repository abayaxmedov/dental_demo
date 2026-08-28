"use client";

import { useLocale } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";
import { useLocaleAlternates } from "./locale-alternates";

const LABELS: Record<string, string> = { uz: "OʻZ", ru: "РУ", en: "EN" };

/**
 * Til almashtirgich. Detail sahifalarda server hisoblagan `hrefs` (tarjima qilingan slug bilan)
 * kontekstdan olinadi; statik sahifalarda joriy pathname'ni almashtiradi.
 */
export function LangSwitcher() {
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();
  const { hrefs } = useLocaleAlternates();

  return (
    <div className="flex items-center gap-1" role="group" aria-label="Til">
      {routing.locales.map((loc) => {
        const active = loc === locale;
        const cls =
          "inline-flex min-h-11 min-w-11 items-center justify-center rounded px-3 text-sm font-semibold transition " +
          (active ? "bg-brand-600 text-white" : "text-slate-500 hover:text-brand-700");
        if (hrefs?.[loc]) {
          return (
            <a
              key={loc}
              href={hrefs[loc]}
              aria-current={active ? "true" : undefined}
              className={cls}
            >
              {LABELS[loc]}
            </a>
          );
        }
        return (
          <button
            key={loc}
            type="button"
            // fallback faqat statik sahifalarda (dynamic routelarda hrefs kontekstdan keladi)
            onClick={() => router.replace(pathname as "/", { locale: loc })}
            aria-current={active ? "true" : undefined}
            className={cls}
          >
            {LABELS[loc]}
          </button>
        );
      })}
    </div>
  );
}
