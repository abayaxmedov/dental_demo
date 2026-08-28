import type { Metadata, Viewport } from "next";
import { Inter, Manrope } from "next/font/google";
import { NextIntlClientProvider, hasLocale } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { routing } from "@/i18n/routing";
import { getSiteSettings } from "@/lib/api";
import { OG_LOCALE, SITE_URL } from "@/lib/seo";
import { BRAND_THEME_COLOR, isHexColor } from "@/lib/theme";
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

// Mobil brauzer xromining rangi = brend teal (globals.css --brand bilan mos).
export const viewport: Viewport = {
  themeColor: BRAND_THEME_COLOR,
  colorScheme: "light",
};

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "meta" });
  const settings = await getSiteSettings(locale);
  const name = settings?.name ?? "Oq Marvarid Dental";
  return {
    metadataBase: new URL(SITE_URL),
    title: { default: t("title"), template: `%s — ${name}` },
    description: t("description"),
    applicationName: name,
    manifest: "/manifest.webmanifest",
    // iOS manzil/sana/kodni telefon havolasiga aylantirib buzmasin.
    formatDetection: { telephone: false, address: false, date: false },
    appleWebApp: { capable: true, title: name, statusBarStyle: "default" },
    // Sotsial karta uchun DEFAULT'lar. `title`/`description` ATAYLAB berilmaydi:
    // metadata "shallow merge" qiladi va `openGraph`ni BUTUNLAY almashtiradi, shuning uchun
    // bu yerda aniq title yozilsa, oʻzining openGraph'i yoʻq sahifalar (narxlar, shifokorlar,
    // blog roʻyxati…) BOSH SAHIFA sarlavhasini ulashardi. Title berilmasa Next uni har
    // sahifaning oʻz `title`idan toʻldiradi — toʻgʻri xatti-harakat (AUDIT T-FIX-04).
    openGraph: {
      type: "website",
      siteName: name,
      locale: OG_LOCALE[locale] ?? "uz_UZ",
      images: [{ url: "/og-default.png", width: 1200, height: 630, alt: name }],
    },
    twitter: {
      card: "summary_large_image",
      images: ["/og-default.png"],
    },
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

  // ADR-004: brand rang YAGONA manba (ClinicSettings) → <html>ga inline CSS custom property
  // sifatida injeksiya. globals.css `:root` defaultlarini ustma-ust bosadi (inline > stylesheet),
  // color-mix rampasi (`--brand-50…`) shu injeksiya qilingan `--brand`dan HOSILA boʻladi.
  // Shu tufayli `reskin` bitta hex oʻzgartirsa butun shkala moslashadi. SSR — FOUC yoʻq.
  // Faqat HAQIQIY hex injeksiya qilinadi — yaroqsiz qiymat globals.css defaultini buzmasin
  // (T-FIX-05: `;` bilan CSS qoʻshilishi yoki koʻrinmas CTA).
  const theme = settings?.theme;
  const themeVars: Record<string, string> = {};
  if (theme) {
    if (isHexColor(theme.brand)) themeVars["--brand"] = theme.brand;
    if (isHexColor(theme.accent)) themeVars["--accent"] = theme.accent;
    if (isHexColor(theme.ink)) themeVars["--ink"] = theme.ink;
    if (isHexColor(theme.surface)) themeVars["--surface"] = theme.surface;
  }
  const themeStyle = Object.keys(themeVars).length
    ? (themeVars as React.CSSProperties)
    : undefined;

  return (
    <html
      lang={locale}
      className={`${inter.variable} ${manrope.variable}`}
      style={themeStyle}
    >
      <body className="min-h-dvh bg-surface text-ink antialiased">
        <NextIntlClientProvider>
          <LocaleAlternatesProvider>
            <a
              href="#main"
              className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[60] focus:rounded-lg focus:bg-brand focus:px-4 focus:py-2 focus:text-white"
            >
              Asosiy kontentga oʻtish
            </a>
            <header>
              <Topbar settings={settings} locale={locale} />
              <Header settings={settings} />
            </header>
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
