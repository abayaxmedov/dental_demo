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
      <SectionHeading eyebrow={t("eyebrow")} title={t("title")} lead={t("lead")} />
      {/* Telefonda — ixcham vertikal timeline (ikonkalar chiziq bilan ulangan); sm+ — kartalar. */}
      <div className="grid sm:grid-cols-2 sm:gap-5 lg:grid-cols-4">
        {stages.map((s, i) => (
          <Reveal key={i} delay={i * 120}>
            <div
              className={`relative flex h-full gap-4 sm:block sm:rounded-2xl sm:border sm:border-line sm:bg-surface sm:p-6 ${i < stages.length - 1 ? "pb-7 sm:pb-6" : ""}`}
            >
              {i < stages.length - 1 ? (
                <span aria-hidden className="absolute bottom-0 left-6 top-12 w-px bg-brand-100 sm:hidden" />
              ) : null}
              <span className="absolute right-5 top-5 hidden font-display text-4xl font-extrabold text-brand-100 sm:block">
                {i + 1}
              </span>
              <span className="relative inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand">
                <s.Icon className="h-6 w-6" aria-hidden />
              </span>
              <div className="min-w-0 pt-1 sm:pt-0">
                <h3 className="font-display text-lg font-bold text-ink sm:mt-4">
                  <span className="text-brand sm:hidden">{i + 1}. </span>
                  {s.title}
                </h3>
                <p className="mt-1 text-sm text-ink-muted sm:mt-2">{s.desc}</p>
              </div>
            </div>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
