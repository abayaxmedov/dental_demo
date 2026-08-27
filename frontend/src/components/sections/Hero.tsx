import { getTranslations } from "next-intl/server";
import { Phone, CalendarCheck } from "lucide-react";
import type { ClinicSettings } from "@/lib/api";
import { telHref } from "@/lib/format";

export async function Hero({ settings }: { settings: ClinicSettings | null }) {
  const t = await getTranslations("hero");
  const phone = settings?.phone_primary ?? "+998712004040";

  return (
    <section className="relative overflow-hidden border-b border-slate-100 bg-gradient-to-b from-brand-50 to-white">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:py-28">
        <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-brand">
          {t("eyebrow")}
        </p>
        <h1 className="font-display max-w-2xl text-4xl font-extrabold leading-[1.08] tracking-tight text-slate-900 sm:text-6xl">
          {t("title")}
        </h1>
        <p className="mt-5 max-w-xl text-lg leading-relaxed text-slate-600">
          {settings?.tagline || t("subtitle")}
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <a
            href="#qabul"
            className="inline-flex items-center gap-2 rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:opacity-90"
          >
            <CalendarCheck className="h-4 w-4" aria-hidden />
            {t("ctaBook")}
          </a>
          <a
            href={telHref(phone)}
            className="inline-flex items-center gap-2 rounded-full border border-slate-300 px-6 py-3 text-sm font-semibold text-slate-800 transition hover:border-brand hover:text-brand"
          >
            <Phone className="h-4 w-4" aria-hidden />
            {t("ctaCall")}
          </a>
        </div>
      </div>
    </section>
  );
}
