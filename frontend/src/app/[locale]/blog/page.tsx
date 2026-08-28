import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { getPosts } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { formatDate } from "@/lib/format";
import { Link } from "@/i18n/navigation";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Card } from "@/components/ui/Card";
import { ImageFrame } from "@/components/ui/ImageFrame";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { Empty } from "@/components/ui/Empty";

type Params = Promise<{ locale: string }>;
type Search = Promise<{ q?: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pages.blog" });
  return { title: t("title"), description: t("lead"), alternates: buildAlternates({ pathname: "/blog", currentLocale: locale as never }) };
}

export default async function BlogPage({ params, searchParams }: { params: Params; searchParams: Search }) {
  const { locale } = await params;
  const { q } = await searchParams;
  setRequestLocale(locale);
  const posts = await getPosts(locale, q ? { q } : {});
  const t = await getTranslations("pages.blog");
  const tc = await getTranslations("pages.crumbs");

  return (
    <Section>
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("title") }]} />
      <SectionHeading as="h1" title={t("title")} lead={t("lead")} />
      <form className="mb-8 max-w-md" action="" method="get">
        <input name="q" defaultValue={q ?? ""} placeholder={t("search")} aria-label={t("search")}
          className="w-full rounded-full border border-line px-5 py-2.5 text-base focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20" />
      </form>
      {posts.length === 0 ? (
        <Empty title={t("empty")} />
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {posts.map((p) => (
            <Link key={p.id} href={{ pathname: "/blog/[slug]", params: { slug: p.slug ?? "" } }}>
              <Card interactive className="flex h-full flex-col overflow-hidden">
                <ImageFrame image={p.cover} alt={p.title} ratio="16/9" rounded="" sizes="(min-width:1024px) 33vw, 100vw" />
                <div className="flex flex-1 flex-col p-5">
                  <h2 className="font-display text-lg font-bold leading-snug text-ink">{p.title}</h2>
                  <p className="mt-2 line-clamp-2 flex-1 text-sm text-ink-muted">{p.excerpt}</p>
                  <p className="mt-3 text-xs text-ink-subtle">
                    {formatDate(p.published_at ?? null, locale)}
                    {p.reading_time ? ` · ${p.reading_time} ${t("readTime")}` : ""}
                  </p>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </Section>
  );
}
