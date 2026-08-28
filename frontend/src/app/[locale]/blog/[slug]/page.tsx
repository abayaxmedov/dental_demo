import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { getPost, getSeoRoutes } from "@/lib/api";
import { buildAlternates, localeHrefs, localePath, ogBase, ogFor } from "@/lib/seo";
import { routing } from "@/i18n/routing";
import { formatDate } from "@/lib/format";
import { Section } from "@/components/ui/Section";
import { ImageFrame } from "@/components/ui/ImageFrame";
import { Prose } from "@/components/ui/Prose";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { JsonLd } from "@/components/ui/JsonLd";
import { SetLocaleHrefs } from "@/components/layout/locale-alternates";
import { PROSE } from "@/lib/image-sizes";

type Params = Promise<{ locale: string; slug: string }>;
export const dynamicParams = true;

export async function generateStaticParams() {
  const r = await getSeoRoutes("uz");
  if (!r) return [];
  return r.posts.flatMap((p) => routing.locales.map((locale) => ({ locale, slug: p.slugs[locale] })));
}

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale, slug } = await params;
  const p = await getPost(locale, slug);
  if (!p) return {};
  return {
    title: p.meta_title || p.title,
    description: p.meta_description || p.excerpt,
    alternates: buildAlternates({ pathname: "/blog/[slug]", slugsByLocale: p.alternates as never, currentLocale: locale as never }),
    openGraph: { ...ogBase(locale), type: "article", images: [ogFor(p)], publishedTime: p.published_at ?? undefined },
  };
}

export default async function PostDetail({ params }: { params: Params }) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  const p = await getPost(locale, slug);
  if (!p) notFound();
  const t = await getTranslations("pages.blog");
  const tc = await getTranslations("pages.crumbs");
  const hrefs = localeHrefs("/blog/[slug]", p.alternates as never);
  const ld = {
    "@context": "https://schema.org", "@type": "Article", headline: p.title,
    image: p.cover?.src || undefined, datePublished: p.published_at || undefined,
    dateModified: p.updated_at || undefined,
    author: p.author_name ? { "@type": "Person", name: p.author_name } : undefined,
  };

  return (
    <Section width="3xl">
      <SetLocaleHrefs hrefs={hrefs} />
      <JsonLd data={ld} />
      <Breadcrumbs items={[
        { label: tc("home"), href: localePath("/", locale as never) },
        { label: t("title"), href: localePath("/blog", locale as never) },
        { label: p.title },
      ]} />
      <h1 className="font-display text-3xl font-extrabold leading-tight tracking-tight text-ink sm:text-4xl">{p.title}</h1>
      <p className="mt-3 text-sm text-ink-subtle">
        {formatDate(p.published_at ?? null, locale)}
        {p.author_name ? ` · ${p.author_name}` : ""}
        {p.reading_time ? ` · ${p.reading_time} ${t("readTime")}` : ""}
      </p>
      {p.cover ? <div className="mt-6"><ImageFrame image={p.cover} alt={p.title} ratio="16/9" priority sizes={PROSE} /></div> : null}
      {p.excerpt ? <p className="mt-6 text-lg font-medium text-ink-muted">{p.excerpt}</p> : null}
      {p.body ? <div className="mt-6"><Prose text={p.body} /></div> : null}
    </Section>
  );
}
