"use client";

import { useRef, useState } from "react";
import Image from "next/image";
import type { ImageLike } from "@/lib/api";

/** Before/After slider — sudraladigan tutqich (pointer+touch+klaviatura), clip-path (CLS 0). */
export function CaseSlider({
  before,
  after,
  beforeLabel,
  afterLabel,
  alt,
}: {
  before: ImageLike;
  after: ImageLike;
  beforeLabel: string;
  afterLabel: string;
  alt: string;
}) {
  const [pos, setPos] = useState(50);
  const ref = useRef<HTMLDivElement>(null);

  const move = (clientX: number) => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    setPos(Math.min(100, Math.max(0, ((clientX - r.left) / r.width) * 100)));
  };

  return (
    <div
      ref={ref}
      className="relative aspect-[4/3] w-full select-none overflow-hidden rounded-2xl bg-brand-50"
      onPointerMove={(e) => e.buttons === 1 && move(e.clientX)}
      onPointerDown={(e) => move(e.clientX)}
    >
      {after?.src ? (
        <Image src={after.src} alt={`${alt} — ${afterLabel}`} fill sizes="(min-width:1024px) 50vw, 100vw" className="object-cover" />
      ) : null}
      <div className="absolute inset-0" style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }}>
        {before?.src ? (
          <Image src={before.src} alt={`${alt} — ${beforeLabel}`} fill sizes="(min-width:1024px) 50vw, 100vw" className="object-cover" />
        ) : null}
      </div>
      <span className="absolute left-2 top-2 rounded bg-black/60 px-2 py-0.5 text-xs font-medium text-white">{beforeLabel}</span>
      <span className="absolute right-2 top-2 rounded bg-black/60 px-2 py-0.5 text-xs font-medium text-white">{afterLabel}</span>
      <div
        role="slider"
        aria-label={alt}
        aria-valuenow={Math.round(pos)}
        aria-valuemin={0}
        aria-valuemax={100}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "ArrowLeft") setPos((p) => Math.max(0, p - 5));
          if (e.key === "ArrowRight") setPos((p) => Math.min(100, p + 5));
        }}
        className="absolute inset-y-0 z-10 flex w-1 cursor-ew-resize items-center justify-center bg-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand"
        style={{ left: `calc(${pos}% - 2px)` }}
      >
        <span className="grid h-8 w-8 place-items-center rounded-full bg-white shadow-md ring-1 ring-line">
          <span className="text-xs text-brand">◂▸</span>
        </span>
      </div>
    </div>
  );
}
