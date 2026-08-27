import { ChevronRight } from "lucide-react";
import { SITE_URL } from "@/lib/seo";
import { JsonLd } from "./JsonLd";

export type Crumb = { label: string; href?: string };

/** Vizual breadcrumb + BreadcrumbList JSON-LD (bir manba — drift yoʻq). href = resolved locale-path. */
export function Breadcrumbs({ items }: { items: Crumb[] }) {
  const ld = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((it, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: it.label,
      ...(it.href ? { item: SITE_URL + it.href } : {}),
    })),
  };
  return (
    <nav aria-label="breadcrumb" className="mb-6">
      <ol className="flex flex-wrap items-center gap-1.5 text-sm text-ink-subtle">
        {items.map((it, i) => (
          <li key={i} className="flex items-center gap-1.5">
            {it.href ? (
              <a href={it.href} className="hover:text-brand">
                {it.label}
              </a>
            ) : (
              <span className="text-ink-muted" aria-current="page">
                {it.label}
              </span>
            )}
            {i < items.length - 1 && (
              <ChevronRight className="h-3.5 w-3.5 text-ink-subtle" aria-hidden />
            )}
          </li>
        ))}
      </ol>
      <JsonLd data={ld} />
    </nav>
  );
}
