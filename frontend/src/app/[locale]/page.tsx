import { setRequestLocale } from "next-intl/server";
import { Topbar } from "@/components/layout/Topbar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Hero } from "@/components/sections/Hero";
import { Counters } from "@/components/sections/Counters";
import { Services } from "@/components/sections/Services";
import { Doctors } from "@/components/sections/Doctors";
import { Prices } from "@/components/sections/Prices";
import { Reviews } from "@/components/sections/Reviews";
import { Faq } from "@/components/sections/Faq";
import { Booking } from "@/components/sections/Booking";
import {
  getDoctors,
  getFaqs,
  getPrices,
  getReviewSummary,
  getReviews,
  getServices,
  getSiteSettings,
} from "@/lib/api";

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
      <Topbar settings={settings} locale={locale} />
      <Header settings={settings} />
      <main>
        <Hero settings={settings} />
        <Counters settings={settings} locale={locale} />
        <Services services={featuredServices} />
        <Prices prices={prices} locale={locale} />
        <Doctors doctors={doctors} />
        <Reviews reviews={reviews} summary={summary} />
        <Faq faqs={faqs} />
        <Booking services={allServices} doctors={doctors} settings={settings} />
      </main>
      <Footer settings={settings} locale={locale} />
    </>
  );
}
