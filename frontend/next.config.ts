import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin();

const nextConfig: NextConfig = {
  images: {
    formats: ["image/avif", "image/webp"],
    // Backend media (dev). Prod'da real host qoʻshiladi.
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/media/**" },
    ],
  },
};

export default withNextIntl(nextConfig);
