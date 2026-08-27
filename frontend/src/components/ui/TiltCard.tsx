"use client";

import { useRef, type ReactNode } from "react";

/** Pointer'ga ergashuvchi ≤6° CSS-3D tilt. Touch va reduced-motion'da ishlamaydi. */
export function TiltCard({ children, className = "" }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);

  function onMove(e: React.PointerEvent<HTMLDivElement>) {
    const el = ref.current;
    if (!el || e.pointerType !== "mouse") return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    el.style.transform = `perspective(800px) rotateX(${-py * 6}deg) rotateY(${px * 6}deg)`;
  }
  function reset() {
    if (ref.current) ref.current.style.transform = "";
  }

  return (
    <div
      ref={ref}
      onPointerMove={onMove}
      onPointerLeave={reset}
      className={`transition-transform duration-200 ease-out [transform-style:preserve-3d] ${className}`}
    >
      {children}
    </div>
  );
}
