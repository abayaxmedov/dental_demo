import { getTranslations } from "next-intl/server";
import { Clock } from "lucide-react";
import type { Service } from "@/lib/api";
import { Link } from "@/i18n/navigation";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Card } from "@/components/ui/Card";
import { ImageFrame } from "@/components/ui/ImageFrame";
import { ButtonLink } from "@/components/ui/Button";
import { Reveal } from "@/components/ui/Reveal";
import { TiltCard } from "@/components/ui/TiltCard";
import { CARD_3UP } from "@/lib/image-sizes";

export async function Services({ services }: { services: Service[] }) {
  const t = await getTranslations("nav");
  const tp = await getTranslations("pages.services");
  if (!services.length) return null;

  return (
    <Section id="xizmatlar" tone="muted">
      <SectionHeading
        title={t("services")}
        action={<ButtonLink href="/xizmatlar" variant="secondary">{tp("all")}</ButtonLink>}
      />
      <Reveal>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((s) => (
            <Link key={s.id} href={{ pathname: "/xizmatlar/[slug]", params: { slug: s.slug ?? "" } }}>
              <TiltCard>
                <Card interactive className="flex h-full flex-col overflow-hidden">
              <ImageFrame image={s.cover} alt={s.title} ratio="3/2" rounded="" sizes={CARD_3UP} />
              <div className="flex flex-1 flex-col p-5">
                <h3 className="font-display text-lg font-bold text-ink">{s.title}</h3>
                <p className="mt-2 line-clamp-2 flex-1 text-sm text-ink-muted">{s.excerpt}</p>
                  <p className="mt-4 inline-flex items-center gap-1.5 text-xs text-ink-subtle">
                    <Clock className="h-3.5 w-3.5" aria-hidden /> {s.duration_minutes} {tp("min")}
                  </p>
                </div>
                </Card>
              </TiltCard>
            </Link>
          ))}
        </div>
      </Reveal>
    </Section>
  );
}
