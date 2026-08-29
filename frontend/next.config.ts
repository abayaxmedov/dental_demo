import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin();

// Media host — rasm `src` shu yerdan keladi. Dev'da backend (127.0.0.1:8000),
// prod'da ommaviy domen. next/image faqat allowlist'dagi host'ni optimallashtiradi.
const MEDIA_URL = process.env.NEXT_PUBLIC_MEDIA_URL ?? "http://127.0.0.1:8000";
const media = new URL(`${MEDIA_URL}/media/**`);

// Xavfsizlik header'lari (Faza 5 — yoʻnalish C). CSP client fetch/rasm host'lariga
// bogʻlangan; origin'larni env'dan olamiz.
const API_ORIGIN = new URL(process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").origin;
const MEDIA_ORIGIN = new URL(MEDIA_URL).origin;
// DIQQAT: `headers()` SOʻROV vaqtida emas, `next build`/`next dev` START vaqtida bir marta
// hisoblanadi va natija build chiqishiga QOTIB qoladi (avvalgi izoh buning teskarisini
// daʼvo qilardi — notoʻgʻri edi, AUDIT T-FIX-17). Amalda qiymatlar baribir toʻgʻri chiqadi,
// chunki `next dev` NODE_ENV=development, `next build` esa production bilan ishlaydi va
// sayt oʻzi build qilingan hostda serve qilinadi. Lekin OQIBATI bor: API/media origin va
// NODE_ENV **build vaqtida** qotadi — env oʻzgarsa QAYTA BUILD kerak (deploy checklist).
const isDev = process.env.NODE_ENV !== "production";
// SITE_HTTPS — domen + TLS bilan deploy qilinsagina `true`. IP-only HTTP demo'da `false`
// (default): `upgrade-insecure-requests` va HSTS OʻCHIRILADI, aks holda brauzer barcha
// soʻrovni https'ga koʻtaradi-yu, TLS yoʻqligi uchun sayt butunlay ochilmaydi. Backend
// `prod.py` dagi SITE_HTTPS bilan JUFT — ikkalasini birga oʻzgartirib qayta build qiling.
const httpsEnabled = process.env.SITE_HTTPS === "true";

// CSP — SSG bilan mos varianti. Nonce + `strict-dynamic` (Next hujjati tavsiyasi)
// ATAYLAB ISHLATILMADI: u dinamik render talab qiladi va 121 static sahifani
// oʻldiradi (Lighthouse/ISR arxitekturasiga zid). Buning oʻrniga `'unsafe-inline'`
// (SSG'da nonce yoʻq) + qolgan barcha yoʻnalishlar qatʼiy qulflangan. Kontent bizning
// ishonchli backend'dan keladi va React default'da escape qiladi — XSS yuzasi past.
const csp = [
  `default-src 'self'`,
  `base-uri 'self'`,
  `object-src 'none'`,
  `frame-ancestors 'none'`, // clickjacking — bizni hech kim <iframe>ga sola olmaydi
  `frame-src 'self'`, // saytda tashqi iframe yoʻq (xarita — tashqi <a> havola)
  `form-action 'self'`,
  `img-src 'self' data: blob: ${MEDIA_ORIGIN}`,
  `font-src 'self'`, // next/font oʻzi-hostlaydi
  `style-src 'self' 'unsafe-inline'`, // Tailwind + inline stillar
  `script-src 'self' 'unsafe-inline'${isDev ? " 'unsafe-eval'" : ""}`, // dev: React refresh
  `connect-src 'self' ${API_ORIGIN}${isDev ? " ws://localhost:* ws://127.0.0.1:*" : ""}`,
  `worker-src 'self' blob:`,
  `manifest-src 'self'`,
  // Faqat TLS bilan — HTTP/IP deploy'da bu sahifani buzadi (yuqoridagi SITE_HTTPS izohi).
  ...(httpsEnabled ? [`upgrade-insecure-requests`] : []),
].join("; ");

const securityHeaders = [
  { key: "Content-Security-Policy", value: csp },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" }, // frame-ancestors'ning eski-brauzer dublikati
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "X-DNS-Prefetch-Control", value: "on" },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=(), browsing-topics=()",
  },
  // HSTS faqat haqiqiy HTTPS deploy'da — HTTP/IP demo'da brauzerni https'ga qulflab qoʻyadi.
  ...(httpsEnabled
    ? [{ key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" }]
    : []),
];

const nextConfig: NextConfig = {
  // Docker deploy uchun minimal runtime chiqishi (server.js + faqat kerakli node_modules).
  // Image `frontend/Dockerfile` `.next/standalone` ni nusxalaydi (ADR-021).
  output: "standalone",
  poweredByHeader: false, // Next versiyasini oshkor qilmaymiz
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
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
  // Prod media proxy (ADR-021). Prod'da backend media URL'lari ROOT-relative (`/media/...`,
  // MEDIA_PUBLIC_BASE=/), shuning uchun next/image ularni "local" deb biladi va OPTIMIZER
  // ularni shu server orqali oladi → bu rewrite ichki nginx'ga uzatadi. Natijada optimizer
  // instance'ning ommaviy IP'siga urinmaydi (EC2 hairpin yoʻq), rasm optimizatsiyasi SAQLANADI.
  // Brauzerdagi og:image esa `metadataBase` bilan mutlaq ommaviy URL boʻladi. Dev'da
  // MEDIA_REWRITE_TARGET boʻsh → rewrite yoʻq (dev backend mutlaq media URL beradi).
  async rewrites() {
    const target = process.env.MEDIA_REWRITE_TARGET;
    return target ? [{ source: "/media/:path*", destination: `${target}/media/:path*` }] : [];
  },
};

export default withNextIntl(nextConfig);
