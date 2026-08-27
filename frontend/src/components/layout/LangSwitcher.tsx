"use client";

import { useLocale } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";

const LABELS: Record<string, string> = { uz: "OʻZ", ru: "РУ", en: "EN" };

// Til almashtirgich: joriy sahifani saqlaydi (T-P1-14 ekvivalenti).
export function LangSwitcher() {
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="flex items-center gap-1" role="group" aria-label="Til">
      {routing.locales.map((loc) => (
        <button
          key={loc}
          type="button"
          onClick={() => router.replace(pathname, { locale: loc })}
          aria-current={loc === locale ? "true" : undefined}
          className={
            "rounded px-2 py-1 text-xs font-semibold transition " +
            (loc === locale
              ? "bg-teal-600 text-white"
              : "text-slate-500 hover:text-teal-700")
          }
        >
          {LABELS[loc]}
        </button>
      ))}
    </div>
  );
}
