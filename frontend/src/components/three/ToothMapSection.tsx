"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { useRouter } from "@/i18n/navigation";
import { ArrowRight } from "lucide-react";
import { useWebGLStatus } from "./useWebGLReady";
import type { ToothItem } from "./ToothMap";

const ToothMap = dynamic(() => import("./ToothMap").then((m) => m.ToothMap), { ssr: false });

/**
 * Interaktiv tish xaritasi (ADR-011 2-sahna, ADR-024). Desktop va telefonda.
 * Gate yiqilsa — hech narsa (pastdagi xizmatlar gridi asosiy navigatsiya boʻlib qoladi).
 * Telefonda tanlangan tish nomi tugmaga aylanadi (2-bosishga alternativa).
 */
export function ToothMapSection({
  items,
  hint,
  tapHint,
}: {
  items: ToothItem[];
  hint: string;
  tapHint: string;
}) {
  const ready = useWebGLStatus({ allowTouch: true }) === "ready";
  const router = useRouter();
  const [hovered, setHovered] = useState<{ i: number; touch: boolean } | null>(null);
  const [touchUser, setTouchUser] = useState(
    () => typeof window !== "undefined" && window.matchMedia("(hover: none)").matches,
  );
  if (!ready || items.length === 0) return null;

  const open = (slug: string) => router.push({ pathname: "/xizmatlar/[slug]", params: { slug } });

  return (
    <div
      className="mb-10 rounded-2xl border border-line bg-gradient-to-b from-brand-50 to-surface"
      onPointerDown={(e) => setTouchUser(e.pointerType !== "mouse")}
    >
      <div className="relative h-80 lg:h-64">
        <ToothMap
          items={items}
          onHover={(i, touch) => setHovered(i === null ? null : { i, touch })}
          onSelect={open}
        />
        <div className="pointer-events-none absolute inset-x-0 bottom-3 text-center">
          {hovered?.touch ? (
            <button
              type="button"
              onClick={() => open(items[hovered.i].slug)}
              className="pointer-events-auto inline-flex min-h-11 items-center gap-1.5 rounded-full bg-brand px-5 text-sm font-semibold text-white shadow-sm"
            >
              {items[hovered.i].title}
              <ArrowRight className="h-4 w-4" aria-hidden />
            </button>
          ) : (
            <span className="rounded-full bg-surface/90 px-4 py-1.5 text-sm font-medium text-ink shadow-sm">
              {hovered !== null ? items[hovered.i].title : touchUser ? tapHint : hint}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
