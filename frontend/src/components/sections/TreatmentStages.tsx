import { getTranslations } from "next-intl/server";
import { ScanLine, Wrench, Anchor, Sparkles } from "lucide-react";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Reveal } from "@/components/ui/Reveal";

const ICONS = [ScanLine, Wrench, Anchor, Sparkles];

/** Implantatsiya bosqichlari — scroll-reveal stepper (Tier A niyati, asset'siz, har qurilmada). */
export async function TreatmentStages() {
  const t = await getTranslations("pages.stages");
  const stages = [1, 2, 3, 4].map((i) => ({
    title: t(`s${i}t`),
    desc: t(`s${i}d`),
    Icon: ICONS[i - 1],
  }));

  return (
    <Section tone="muted">
      <SectionHeading eyebrow="Implantatsiya" title={t("title")} lead={t("lead")} />
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stages.map((s, i) => (
          <Reveal key={i} delay={i * 120}>
            <div className="relative h-full rounded-2xl border border-line bg-surface p-6">
              <span className="absolute right-5 top-5 font-display text-4xl font-extrabold text-brand-100">
                {i + 1}
              </span>
              <span className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-brand-50 text-brand">
                <s.Icon className="h-6 w-6" aria-hidden />
              </span>
              <h3 className="mt-4 font-display text-lg font-bold text-ink">{s.title}</h3>
              <p className="mt-2 text-sm text-ink-muted">{s.desc}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
