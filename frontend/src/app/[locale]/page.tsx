import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { Hero } from "@/components/sections/Hero";
import { Counters } from "@/components/sections/Counters";
import { Services } from "@/components/sections/Services";
import { Doctors } from "@/components/sections/Doctors";
import { Prices } from "@/components/sections/Prices";
import { Reviews } from "@/components/sections/Reviews";
import { Faq } from "@/components/sections/Faq";
import { Booking } from "@/components/sections/Booking";
import { DentistJsonLd } from "@/components/seo/DentistJsonLd";
import { buildAlternates } from "@/lib/seo";
import {
  getDoctors,
  getFaqs,
  getPrices,
  getReviewSummary,
  getReviews,
  getServices,
  getSiteSettings,
} from "@/lib/api";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "meta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: buildAlternates({ pathname: "/", currentLocale: locale as never }),
    openGraph: { type: "website", images: ["/og-default.png"] },
  };
}

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  // Barcha maʼlumot parallel olinadi — waterfall yoʻq.
  const [settings, featuredServices, allServices, doctors, prices, reviews, summary, faqs] =
    await Promise.all([
      getSiteSettings(locale),
      getServices(locale, { featured: true }),
      getServices(locale),
      getDoctors(locale),
      getPrices(locale),
      getReviews(locale, { featured: true }),
      getReviewSummary(locale),
      getFaqs(locale),
    ]);

  return (
    <>
      <DentistJsonLd settings={settings} summary={summary} />
      <Hero settings={settings} />
      <Counters settings={settings} locale={locale} />
      <Services services={featuredServices} />
      <Prices prices={prices} locale={locale} />
      <Doctors doctors={doctors} />
      <Reviews reviews={reviews} summary={summary} />
      <Faq faqs={faqs} />
      <Booking services={allServices} doctors={doctors} settings={settings} />
    </>
  );
}
