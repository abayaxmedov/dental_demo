"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { useRouter } from "@/i18n/navigation";
import { useWebGLReady } from "./useWebGLReady";
import type { ToothItem } from "./ToothMap";

const ToothMap = dynamic(() => import("./ToothMap").then((m) => m.ToothMap), { ssr: false });

/**
 * Interaktiv tish xaritasi (ADR-011 2-sahna). Faqat qodir desktop'da koʻrinadi —
 * aks holda hech narsa (pastdagi xizmatlar gridi asosiy navigatsiya boʻlib qoladi).
 */
export function ToothMapSection({ items, hint }: { items: ToothItem[]; hint: string }) {
  const ready = useWebGLReady();
  const router = useRouter();
  const [hovered, setHovered] = useState<number | null>(null);
  if (!ready || items.length === 0) return null;

  return (
    <div className="mb-10 hidden rounded-2xl border border-line bg-gradient-to-b from-brand-50 to-surface lg:block">
      <div className="relative h-64">
        <ToothMap
          items={items}
          onHover={setHovered}
          onSelect={(slug) => router.push({ pathname: "/xizmatlar/[slug]", params: { slug } })}
        />
        <div className="pointer-events-none absolute inset-x-0 bottom-3 text-center">
          <span className="rounded-full bg-surface/90 px-4 py-1.5 text-sm font-medium text-ink shadow-sm">
            {hovered !== null ? items[hovered].title : hint}
          </span>
        </div>
      </div>
    </div>
  );
}
