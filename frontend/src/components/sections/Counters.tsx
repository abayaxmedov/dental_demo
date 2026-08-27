import type { ClinicSettings } from "@/lib/api";
import { formatSum } from "@/lib/format";

export function Counters({
  settings,
  locale,
}: {
  settings: ClinicSettings | null;
  locale: string;
}) {
  const counters = settings?.counters ?? [];
  if (!counters.length) return null;

  return (
    <section className="border-b border-slate-100 bg-white">
      <div className="mx-auto grid max-w-6xl grid-cols-2 gap-6 px-4 py-14 sm:py-16 lg:grid-cols-4">
        {counters.map((c) => (
          <div key={c.id} className="text-center">
            <div className="font-display text-4xl font-extrabold text-brand sm:text-5xl">
              {formatSum(c.value, locale)}
              {c.suffix}
            </div>
            <div className="mt-1 text-sm text-slate-500">{c.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
