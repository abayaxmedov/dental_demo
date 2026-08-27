"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";

// R3F chunk faqat guard oʻtganda va idle'da yuklanadi (initial bundle'ga tegmaydi).
const HeroTooth = dynamic(() => import("./HeroTooth").then((m) => m.HeroTooth), { ssr: false });

/**
 * ADR-011 SceneGuard: WebGL sahnasini faqat qodir qurilmada ishga tushiradi.
 * Har qanday tekshiruv tushsa — hech narsa render qilinmaydi (poster qoladi).
 */
export function SceneGuard() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const mm = (q: string) => window.matchMedia(q).matches;
    if (!mm("(min-width: 1024px)")) return; // faqat desktop
    if (!mm("(pointer: fine)")) return; // touch emas
    if (mm("(prefers-reduced-motion: reduce)")) return;
    const conn = (navigator as { connection?: { saveData?: boolean; effectiveType?: string } }).connection;
    if (conn?.saveData) return;
    if (conn?.effectiveType && /(^|\s)(slow-)?2g/.test(conn.effectiveType)) return; // faqat haqiqatan sekin ulanish
    try {
      const c = document.createElement("canvas");
      if (!c.getContext("webgl2")) return; // WebGL2 shart
    } catch {
      return;
    }
    const w = window as Window & {
      requestIdleCallback?: (cb: () => void, o?: { timeout: number }) => number;
      cancelIdleCallback?: (h: number) => void;
    };
    if (w.requestIdleCallback) {
      const handle = w.requestIdleCallback(() => setReady(true), { timeout: 2000 });
      return () => w.cancelIdleCallback?.(handle);
    }
    const handle = window.setTimeout(() => setReady(true), 400);
    return () => clearTimeout(handle);
  }, []);

  if (!ready) return null;
  return <HeroTooth />;
}
