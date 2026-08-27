import type { MetadataRoute } from "next";
import { getSeoRoutes } from "@/lib/api";
import { localePath, SITE_URL } from "@/lib/seo";
import { routing } from "@/i18n/routing";
import type { AppPathname } from "@/i18n/routing";

// Statik routelar (default locale'da bitta yozuv, alternates bilan)
const STATIC: { path: AppPathname; priority: number; freq: MetadataRoute.Sitemap[number]["changeFrequency"] }[] = [
  { path: "/", priority: 1, freq: "weekly" },
  { path: "/xizmatlar", priority: 0.9, freq: "weekly" },
  { path: "/narxlar", priority: 0.9, freq: "weekly" },
  { path: "/shifokorlar", priority: 0.8, freq: "monthly" },
  { path: "/ishlarimiz", priority: 0.8, freq: "monthly" },
  { path: "/galereya", priority: 0.6, freq: "monthly" },
  { path: "/sharhlar", priority: 0.7, freq: "monthly" },
  { path: "/blog", priority: 0.6, freq: "weekly" },
  { path: "/aloqa", priority: 0.7, freq: "monthly" },
  { path: "/faq", priority: 0.6, freq: "monthly" },
  { path: "/haqimizda", priority: 0.6, freq: "monthly" },
  { path: "/maxfiylik-siyosati", priority: 0.3, freq: "yearly" },
];

function entry(path: AppPathname, slug: string | undefined, priority: number, freq: MetadataRoute.Sitemap[number]["changeFrequency"], lastModified?: string): MetadataRoute.Sitemap[number] {
  const languages: Record<string, string> = {};
  for (const loc of routing.locales) languages[loc] = SITE_URL + localePath(path, loc, slug);
  return {
    url: SITE_URL + localePath(path, routing.defaultLocale, slug),
    lastModified: lastModified ? new Date(lastModified) : undefined,
    changeFrequency: freq,
    priority,
    alternates: { languages },
  };
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const routes = await getSeoRoutes("uz");
  const out: MetadataRoute.Sitemap = STATIC.map((s) => entry(s.path, undefined, s.priority, s.freq));
  if (routes) {
    for (const s of routes.services) out.push(entry("/xizmatlar/[slug]", s.slugs.uz, 0.7, "monthly", s.updated_at));
    for (const d of routes.doctors) out.push(entry("/shifokorlar/[slug]", d.slugs.uz, 0.6, "monthly", d.updated_at));
    for (const p of routes.posts) out.push(entry("/blog/[slug]", p.slugs.uz, 0.5, "monthly", p.updated_at));
  }
  return out;
}
