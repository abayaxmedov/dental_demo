import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { getDoctors, getGallery, getSiteSettings } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { Counters } from "@/components/sections/Counters";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Avatar } from "@/components/ui/Avatar";
import { ImageFrame } from "@/components/ui/ImageFrame";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { ButtonLink } from "@/components/ui/Button";
import { Link } from "@/i18n/navigation";

type Params = Promise<{ locale: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const settings = await getSiteSettings(locale);
  const t = await getTranslations({ locale, namespace: "nav" });
  return {
    title: t("about"),
    description: settings?.about_short || settings?.default_meta_description || undefined,
    alternates: buildAlternates({ pathname: "/haqimizda", currentLocale: locale as never }),
  };
}

export default async function AboutPage({ params }: { params: Params }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const [settings, doctors, gallery] = await Promise.all([
    getSiteSettings(locale), getDoctors(locale), getGallery(locale, { category: "clinic" }),
  ]);
  const t = await getTranslations("nav");
  const td = await getTranslations("pages.doctors");
  const tc = await getTranslations("pages.crumbs");

  return (
    <>
      <Section>
        <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("about") }]} />
        <SectionHeading title={t("about")} lead={settings?.tagline || undefined} />
        <div className="grid gap-8 lg:grid-cols-2 lg:items-center">
          <div className="space-y-4 text-ink-muted leading-relaxed">
            {(settings?.about_short || "").split(/\n\n+/).filter(Boolean).map((p, i) => <p key={i}>{p}</p>)}
            {settings?.license_text ? <p className="rounded-xl border border-line bg-surface-muted px-4 py-3 text-sm">{settings.license_text}</p> : null}
          </div>
          {gallery[0] ? <ImageFrame image={gallery[0].image} alt={gallery[0].alt || t("about")} ratio="4/3" priority sizes="(min-width:1024px) 40rem, 100vw" /> : null}
        </div>
      </Section>

      <div className="border-b border-line bg-surface-muted">
        <Counters settings={settings} locale={locale} />
      </div>

      {doctors.length ? (
        <Section>
          <SectionHeading title={td("title")} action={<ButtonLink href="/shifokorlar" variant="secondary">{td("title")}</ButtonLink>} />
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {doctors.slice(0, 4).map((d) => (
              <Link key={d.id} href={{ pathname: "/shifokorlar/[slug]", params: { slug: d.slug ?? "" } }} className="flex flex-col items-center text-center">
                <Avatar image={d.photo} name={d.full_name} size={88} />
                <p className="mt-3 font-semibold text-ink">{d.full_name}</p>
                <p className="text-sm text-brand">{d.specialization}</p>
              </Link>
            ))}
          </div>
        </Section>
      ) : null}
    </>
  );
}
