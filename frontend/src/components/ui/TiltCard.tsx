"use client";

import { useEffect, useRef, type ReactNode } from "react";

/** Maksimal og'ish (gradus) — sichqoncha va scroll rejimida bir xil. */
const MAX_TILT = 6;

/**
 * ≤6° CSS-3D tilt. Reduced-motion'da ishlamaydi.
 *  - Sichqoncha: pointer'ga ergashadi.
 *  - Touch (hover yoʻq): scroll'ga bogʻlangan — karta ekranning pastidan kirganda orqaga
 *    egilgan, markazda tekis, tepaga chiqib ketayotganda oldinga egiladi.
 */
export function TiltCard({ children, className = "" }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

    let frame = 0;
    const update = () => {
      frame = 0;
      const r = el.getBoundingClientRect();
      const half = window.innerHeight / 2;
      const p = Math.max(-1, Math.min(1, (r.top + r.height / 2 - half) / half));
      el.style.transform = `perspective(800px) rotateX(${(p * MAX_TILT).toFixed(2)}deg)`;
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };

    // Faqat ekrandagi kartalar scroll'ni tinglaydi
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) {
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
      } else {
        window.removeEventListener("scroll", onScroll);
      }
    });
    io.observe(el);
    return () => {
      io.disconnect();
      window.removeEventListener("scroll", onScroll);
      cancelAnimationFrame(frame);
    };
  }, []);

  function onMove(e: React.PointerEvent<HTMLDivElement>) {
    const el = ref.current;
    if (!el || e.pointerType !== "mouse") return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    el.style.transform = `perspective(800px) rotateX(${-py * MAX_TILT}deg) rotateY(${px * MAX_TILT}deg)`;
  }
  function reset(e: React.PointerEvent<HTMLDivElement>) {
    if (e.pointerType === "mouse" && ref.current) ref.current.style.transform = "";
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
