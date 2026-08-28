import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { getGallery } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { Section, SectionHeading } from "@/components/ui/Section";
import { ImageFrame } from "@/components/ui/ImageFrame";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { Empty } from "@/components/ui/Empty";
import { CARD_3UP } from "@/lib/image-sizes";

type Params = Promise<{ locale: string }>;

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pages.gallery" });
  return { title: t("title"), description: t("lead"), alternates: buildAlternates({ pathname: "/galereya", currentLocale: locale as never }) };
}

export default async function GalleryPage({ params }: { params: Params }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const images = await getGallery(locale);
  const t = await getTranslations("pages.gallery");
  const tc = await getTranslations("pages.crumbs");

  return (
    <Section>
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("title") }]} />
      <SectionHeading as="h1" title={t("title")} lead={t("lead")} />
      {images.length === 0 ? (
        <Empty title={t("title")} />
      ) : (
        <div className="columns-1 gap-4 sm:columns-2 md:columns-3 [&>*]:mb-4">
          {images.map((g) => (
            <figure key={g.id} className="break-inside-avoid">
              <ImageFrame image={g.image} alt={g.alt || g.caption || t("title")} ratio="4/3" sizes={CARD_3UP} />
              {g.caption ? <figcaption className="mt-1.5 text-xs text-ink-subtle">{g.caption}</figcaption> : null}
            </figure>
          ))}
        </div>
      )}
    </Section>
  );
}
