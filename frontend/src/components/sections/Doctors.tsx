import { getTranslations } from "next-intl/server";
import type { Doctor } from "@/lib/api";

const LANG_LABEL: Record<string, string> = { uz: "OʻZ", ru: "РУ", en: "EN", tr: "TR" };

export async function Doctors({ doctors }: { doctors: Doctor[] }) {
  const t = await getTranslations("nav");
  if (!doctors.length) return null;

  return (
    <section id="shifokorlar" className="border-b border-slate-100 bg-white scroll-mt-20">
      <div className="mx-auto max-w-6xl px-4 py-16 sm:py-20">
        <h2 className="font-display text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
          {t("doctors")}
        </h2>
        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {doctors.map((d) => (
            <article key={d.id} className="rounded-2xl border border-slate-200 bg-white p-6">
              <div
                className="mb-4 h-16 w-16 rounded-full bg-gradient-to-br from-brand-100 to-brand-50 ring-1 ring-brand-200"
                aria-hidden
              />
              <h3 className="font-display text-lg font-bold text-slate-900">{d.full_name}</h3>
              <p className="mt-1 text-sm text-brand">{d.specialization}</p>
              <div className="mt-4 flex items-center gap-3 text-xs text-slate-500">
                <span>{d.experience_years} yil</span>
                {d.languages?.length ? (
                  <span className="flex gap-1">
                    {d.languages.map((l) => (
                      <span
                        key={l}
                        className="rounded bg-slate-100 px-1.5 py-0.5 font-medium text-slate-600"
                      >
                        {LANG_LABEL[l] ?? l.toUpperCase()}
                      </span>
                    ))}
                  </span>
                ) : null}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
