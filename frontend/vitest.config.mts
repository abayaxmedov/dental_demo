import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

// Faza 5 (tech debt D) — sof mantiq (lib/) uchun unit testlar. RSC/next-intl server
// komponentlari jsdom'da render qilinmaydi; shuning uchun `node` muhiti va faqat
// `*.test.ts` (komponent .tsx testlari emas). `@/` alias tsconfig bilan mos.
export default defineConfig({
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
    globals: false,
  },
});
