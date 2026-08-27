import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { getStaticPage } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { Section } from "@/components/ui/Section";
import { Prose } from "@/components/ui/Prose";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";

type Params = Promise<{ locale: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const p = await getStaticPage(locale, "privacy");
  return {
    title: p?.title || "Maxfiylik siyosati",
    description: p?.meta_description || undefined,
    alternates: buildAlternates({ pathname: "/maxfiylik-siyosati", currentLocale: locale as never }),
  };
}

export default async function PrivacyPage({ params }: { params: Params }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const p = await getStaticPage(locale, "privacy");
  if (!p) notFound();
  const tc = await getTranslations("pages.crumbs");
  return (
    <Section width="3xl">
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: p.title }]} />
      <h1 className="font-display text-3xl font-extrabold tracking-tight text-ink">{p.title}</h1>
      <div className="mt-6"><Prose text={p.body} /></div>
    </Section>
  );
}
