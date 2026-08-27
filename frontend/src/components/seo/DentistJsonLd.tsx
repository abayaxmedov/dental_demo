import type { ClinicSettings } from "@/lib/api";
import { SITE_URL } from "@/lib/seo";
import { JsonLd } from "@/components/ui/JsonLd";

const DAY = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

/** Bosh sahifa uchun Dentist/LocalBusiness JSON-LD (barqaror @id — boshqa entity'lar bogʻlanadi). */
export function DentistJsonLd({
  settings,
  summary,
}: {
  settings: ClinicSettings | null;
  summary?: { average: number; total: number } | null;
}) {
  if (!settings) return null;
  const hours = (settings.working_hours ?? []).filter((h) => !h.is_closed && h.opens && h.closes);
  const sameAs = [settings.instagram_url, settings.facebook_url, settings.youtube_url, settings.telegram_channel_url].filter(Boolean);

  const data = {
    "@context": "https://schema.org",
    "@type": "Dentist",
    "@id": `${SITE_URL}/#dentist`,
    name: settings.name,
    url: SITE_URL,
    image: settings.hero_image?.src || settings.logo?.src || undefined,
    logo: settings.logo?.src || undefined,
    telephone: settings.phone_primary || undefined,
    email: settings.email || undefined,
    address: settings.address
      ? { "@type": "PostalAddress", streetAddress: settings.address, addressLocality: "Toshkent", addressCountry: "UZ" }
      : undefined,
    geo: settings.map_lat && settings.map_lng
      ? { "@type": "GeoCoordinates", latitude: settings.map_lat, longitude: settings.map_lng }
      : undefined,
    openingHoursSpecification: hours.map((h) => ({
      "@type": "OpeningHoursSpecification",
      dayOfWeek: `https://schema.org/${DAY[h.weekday]}`,
      opens: h.opens?.slice(0, 5),
      closes: h.closes?.slice(0, 5),
    })),
    priceRange: "$$",
    areaServed: "Toshkent",
    sameAs: sameAs.length ? sameAs : undefined,
    aggregateRating: summary && summary.total > 0
      ? { "@type": "AggregateRating", ratingValue: summary.average, reviewCount: summary.total }
      : undefined,
  };
  return <JsonLd data={data} />;
}
