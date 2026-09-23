import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { getGallery } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { Section, SectionHeading } from "@/components/ui/Section";
import { GalleryGrid } from "@/components/ui/GalleryGrid";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { Empty } from "@/components/ui/Empty";

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
  const tn = await getTranslations("nav");

  return (
    <Section>
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("title") }]} />
      <SectionHeading as="h1" title={t("title")} lead={t("lead")} />
      {images.length === 0 ? (
        <Empty title={t("title")} />
      ) : (
        <GalleryGrid
          images={images}
          labels={{ title: t("title"), close: tn("close"), prev: t("prev"), next: t("next") }}
        />
      )}
    </Section>
  );
}
