import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { MapPin, Phone, Clock, Send } from "lucide-react";
import { getSiteSettings } from "@/lib/api";
import { buildAlternates, localePath } from "@/lib/seo";
import { formatPhone, telHref } from "@/lib/format";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Breadcrumbs } from "@/components/ui/Breadcrumbs";
import { ContactForm } from "@/components/booking/ContactForm";

type Params = Promise<{ locale: string }>;
const WD: Record<string, string[]> = {
  uz: ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"],
  ru: ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
  en: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
};

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "pages.contact" });
  return { title: t("title"), description: t("lead"), alternates: buildAlternates({ pathname: "/aloqa", currentLocale: locale as never }) };
}

export default async function ContactPage({ params }: { params: Params }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const settings = await getSiteSettings(locale);
  const t = await getTranslations("pages.contact");
  const tc = await getTranslations("pages.crumbs");
  const phone = settings?.phone_primary || "+998712004040";
  const days = WD[locale] ?? WD.uz;
  const hours = (settings?.working_hours ?? []).slice().sort((a, b) => a.weekday - b.weekday);

  return (
    <Section>
      <Breadcrumbs items={[{ label: tc("home"), href: localePath("/", locale as never) }, { label: t("title") }]} />
      <SectionHeading as="h1" title={t("title")} lead={t("lead")} />
      <div className="grid gap-10 md:grid-cols-2">
        <div className="space-y-6">
          {settings?.address ? (
            <div className="flex gap-3">
              <MapPin className="mt-0.5 h-5 w-5 shrink-0 text-brand" aria-hidden />
              <div><p className="font-semibold text-ink">{t("address")}</p><p className="text-ink-muted">{settings.address}</p></div>
            </div>
          ) : null}
          <div className="flex gap-3">
            <Phone className="mt-0.5 h-5 w-5 shrink-0 text-brand" aria-hidden />
            <div><p className="font-semibold text-ink">{t("phone")}</p><a href={telHref(phone)} className="text-brand hover:underline">{formatPhone(phone)}</a></div>
          </div>
          {settings?.telegram_username ? (
            <div className="flex gap-3">
              <Send className="mt-0.5 h-5 w-5 shrink-0 text-brand" aria-hidden />
              <div><p className="font-semibold text-ink">Telegram</p><a href={`https://t.me/${settings.telegram_username}`} className="text-brand hover:underline">@{settings.telegram_username}</a></div>
            </div>
          ) : null}
          {hours.length ? (
            <div className="flex gap-3">
              <Clock className="mt-0.5 h-5 w-5 shrink-0 text-brand" aria-hidden />
              <div>
                <p className="font-semibold text-ink">{t("hours")}</p>
                <div className="mt-1 max-w-xs overflow-x-auto">
                <table className="w-full text-sm text-ink-muted">
                  <tbody>
                    {hours.map((h) => (
                      <tr key={h.weekday}><td className="pr-4">{days[h.weekday]}</td><td>{h.is_closed ? "—" : `${h.opens?.slice(0, 5)}–${h.closes?.slice(0, 5)}`}</td></tr>
                    ))}
                  </tbody>
                </table>
                </div>
              </div>
            </div>
          ) : null}
          {(settings?.yandex_maps_url || settings?.two_gis_url) ? (
            <a href={settings?.yandex_maps_url || settings?.two_gis_url || "#"} target="_blank" rel="noopener"
              className="inline-flex min-h-11 items-center gap-2 rounded-full border border-line px-5 text-sm font-semibold text-ink hover:border-brand hover:text-brand">
              {t("directions")}
            </a>
          ) : null}
        </div>
        <div className="rounded-2xl border border-line p-6">
          <h2 className="mb-4 font-display text-lg font-bold text-ink">{t("form")}</h2>
          <ContactForm />
        </div>
      </div>
    </Section>
  );
}
