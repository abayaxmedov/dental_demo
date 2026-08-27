import type { Metadata } from "next";
import { Inter, Manrope } from "next/font/google";
import { NextIntlClientProvider, hasLocale } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { routing } from "@/i18n/routing";
import { getSiteSettings } from "@/lib/api";
import { SITE_URL } from "@/lib/seo";
import { LocaleAlternatesProvider } from "@/components/layout/locale-alternates";
import { Topbar } from "@/components/layout/Topbar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { MobileActionBar } from "@/components/layout/MobileActionBar";
import "../globals.css";

const inter = Inter({
  subsets: ["latin", "latin-ext", "cyrillic"],
  variable: "--font-inter",
  display: "swap",
});
const manrope = Manrope({
  subsets: ["latin", "latin-ext", "cyrillic"],
  variable: "--font-manrope",
  display: "swap",
});

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "meta" });
  const settings = await getSiteSettings(locale);
  return {
    metadataBase: new URL(SITE_URL),
    title: { default: t("title"), template: `%s — ${settings?.name ?? "Oq Marvarid Dental"}` },
    description: t("description"),
    verification: {
      google: settings?.google_verification || undefined,
      yandex: settings?.yandex_verification || undefined,
    },
  };
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }
  setRequestLocale(locale);
  const settings = await getSiteSettings(locale);

  return (
    <html lang={locale} className={`${inter.variable} ${manrope.variable}`}>
      <body className="min-h-dvh bg-surface text-ink antialiased">
        <NextIntlClientProvider>
          <LocaleAlternatesProvider>
            <a
              href="#main"
              className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[60] focus:rounded-lg focus:bg-brand focus:px-4 focus:py-2 focus:text-white"
            >
              Asosiy kontentga oʻtish
            </a>
            <Topbar settings={settings} locale={locale} />
            <Header settings={settings} />
            <main id="main" tabIndex={-1}>
              {children}
            </main>
            <Footer settings={settings} locale={locale} />
            <MobileActionBar settings={settings} />
          </LocaleAlternatesProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
