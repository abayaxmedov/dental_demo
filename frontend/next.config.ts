import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin();

// Media host — rasm `src` shu yerdan keladi. Dev'da backend (127.0.0.1:8000),
// prod'da ommaviy domen. next/image faqat allowlist'dagi host'ni optimallashtiradi.
const MEDIA_URL = process.env.NEXT_PUBLIC_MEDIA_URL ?? "http://127.0.0.1:8000";
const media = new URL(`${MEDIA_URL}/media/**`);

const nextConfig: NextConfig = {
  images: {
    formats: ["image/avif", "image/webp"],
    // Next 16: sifat darajalarini aniq ro'yxatlash shart.
    qualities: [75],
    minimumCacheTTL: 60 * 60 * 24 * 30,
    remotePatterns: [
      {
        protocol: media.protocol.replace(":", "") as "http" | "https",
        hostname: media.hostname,
        port: media.port,
        pathname: "/media/**",
      },
    ],
    // Next 16 xususiy IP (localhost/127.0.0.1) ga yechiladigan remote rasmni
    // optimallashtirishni rad etadi (SSRF himoyasi). Bizda XAVFSIZ, chunki:
    // remotePatterns YUQORIDA, dangerouslyAllowLocalIP dan MUSTAQIL enforce qilinadi
    // (image-optimizer.js: hasRemoteMatch → keyin fetchExternalImage) — ya'ni optimizer
    // faqat shu bitta media host'idan rasm ola oladi, ixtiyoriy ichki manzildan emas.
    // Prod'da MEDIA host ommaviy domen bo'ladi va bu bayroq umuman ishlatilmaydi.
    // (NODE_ENV sharti ishlamaydi: qiymat `next build` paytida qotadi, u esa doim production.)
    dangerouslyAllowLocalIP: true,
  },
};

export default withNextIntl(nextConfig);
