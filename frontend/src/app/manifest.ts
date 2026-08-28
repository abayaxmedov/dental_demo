import type { MetadataRoute } from "next";
import { getSiteSettings } from "@/lib/api";
import { BRAND_THEME_COLOR, SURFACE_BG_COLOR } from "@/lib/theme";

// PWA manifest — `/manifest.webmanifest` sifatida serve qilinadi (SEO/mobil hardening,
// yoʻnalish C). Klinika nomi backend'dan olinadi → reskin avtomatik aks etadi.
// `dynamic`ni majburlamaymiz: build vaqtida bir marta hisoblanadi (SSG bilan mos).
export default async function manifest(): Promise<MetadataRoute.Manifest> {
  const settings = await getSiteSettings("uz");
  const name = settings?.name ?? "Oq Marvarid Dental";
  return {
    name,
    // short_name ≤ ~12 belgi (home-screen yorligʻi) — ilk ikki soʻz, aks holda toʻliq nom.
    short_name: name.split(" ").slice(0, 2).join(" ").slice(0, 12) || name,
    description: settings?.tagline || undefined,
    start_url: "/",
    display: "standalone",
    background_color: SURFACE_BG_COLOR,
    theme_color: BRAND_THEME_COLOR,
    // PWA oʻrnatish mezoni 192 VA 512 ni talab qiladi — ilgari eng kattasi 128 edi,
    // shuning uchun "PWA manifest" daʼvosi amalda ishlamasdi (AUDIT T-FIX-18).
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
      { src: "/favicon.ico", sizes: "any", type: "image/x-icon" },
    ],
  };
}
