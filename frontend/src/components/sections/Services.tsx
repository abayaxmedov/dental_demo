import { getTranslations } from "next-intl/server";
import { Clock } from "lucide-react";
import type { Service } from "@/lib/api";

export async function Services({ services }: { services: Service[] }) {
  const t = await getTranslations("nav");
  if (!services.length) return null;

  return (
    <section id="xizmatlar" className="border-b border-slate-100 bg-slate-50/60 scroll-mt-20">
      <div className="mx-auto max-w-6xl px-4 py-16 sm:py-20">
        <h2 className="font-display text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
          {t("services")}
        </h2>
        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((s) => (
            <article
              key={s.id}
              className="group rounded-2xl border border-slate-200 bg-white p-6 transition hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-lg"
            >
              <h3 className="font-display text-lg font-bold text-slate-900 group-hover:text-brand">
                {s.title}
              </h3>
              <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-slate-600">
                {s.excerpt}
              </p>
              <p className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-slate-400">
                <Clock className="h-3.5 w-3.5" aria-hidden />
                {s.duration_minutes} min
              </p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
