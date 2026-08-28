import type { Metadata } from "next";
import { setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Button, ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Rating } from "@/components/ui/Rating";
import { Avatar } from "@/components/ui/Avatar";

export const metadata: Metadata = { robots: { index: false, follow: false } };

type Params = Promise<{ locale: string }>;
const SWATCHES = [
  ["brand", "bg-brand", "teal · matn 4.6:1"],
  ["brand-600", "bg-brand-600", "tugma hover"],
  ["brand-100", "bg-brand-100", "avatar/soft"],
  ["accent", "bg-accent", "accent · 1.9:1 — MATN EMAS"],
  ["ink", "bg-ink", "matn"],
  ["line", "bg-line", "chegara"],
];

export default async function StyleGuide({ params }: { params: Params }) {
  const { locale } = await params;
  if (process.env.NODE_ENV === "production" && process.env.STYLE_GUIDE !== "1") notFound();
  setRequestLocale(locale);
  return (
    <Section>
      <SectionHeading as="h1" eyebrow="Ichki" title="Style guide" lead="Dizayn tokenlari va komponentlar (klinikaga koʻrsatilmaydi)." />
      <div className="space-y-12">
        <div>
          <h2 className="mb-3 font-display text-xl font-bold text-ink">Ranglar</h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            {SWATCHES.map(([name, cls, note]) => (
              <div key={name}>
                <div className={`h-16 rounded-xl ${cls} ring-1 ring-line`} />
                <p className="mt-1.5 text-sm font-medium text-ink">{name}</p>
                <p className="text-xs text-ink-subtle">{note}</p>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h2 className="mb-3 font-display text-xl font-bold text-ink">Tipografika</h2>
          <p className="font-display text-5xl font-extrabold text-ink">Manrope 800</p>
          <p className="mt-2 text-lg text-ink-muted">Inter 400 — asosiy matn slate-600 rangda.</p>
        </div>
        <div>
          <h2 className="mb-3 font-display text-xl font-bold text-ink">Tugmalar</h2>
          <div className="flex flex-wrap items-center gap-3">
            <Button>Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="ghost">Ghost</Button>
            <Button disabled>Disabled</Button>
            <ButtonLink href="/" size="lg">Link lg</ButtonLink>
          </div>
        </div>
        <div>
          <h2 className="mb-3 font-display text-xl font-bold text-ink">Komponentlar</h2>
          <div className="flex flex-wrap items-center gap-4">
            <Badge tone="promo">Aksiya</Badge>
            <Badge tone="brand">Brand</Badge>
            <Badge tone="neutral">Neutral</Badge>
            <Rating value={4} showValue />
            <Avatar name="Dilshod Raximov" size={56} />
            <Card className="p-4">Card</Card>
          </div>
        </div>
      </div>
    </Section>
  );
}
