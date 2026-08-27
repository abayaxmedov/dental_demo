"use client";

import { useEffect, useState } from "react";

/** WebGL sahnasi qodir desktop'da, idle'dan keyin ishga tushsinmi? (ADR-011). */
export function useWebGLReady(): boolean {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const mm = (q: string) => window.matchMedia(q).matches;
    if (!mm("(min-width: 1024px)")) return;
    if (!mm("(pointer: fine)")) return;
    if (mm("(prefers-reduced-motion: reduce)")) return;
    const conn = (navigator as { connection?: { saveData?: boolean; effectiveType?: string } }).connection;
    if (conn?.saveData) return;
    if (conn?.effectiveType && /(^|\s)(slow-)?2g/.test(conn.effectiveType)) return;
    try {
      if (!document.createElement("canvas").getContext("webgl2")) return;
    } catch {
      return;
    }
    const w = window as Window & {
      requestIdleCallback?: (cb: () => void, o?: { timeout: number }) => number;
      cancelIdleCallback?: (h: number) => void;
    };
    if (w.requestIdleCallback) {
      const h = w.requestIdleCallback(() => setReady(true), { timeout: 2000 });
      return () => w.cancelIdleCallback?.(h);
    }
    const h = window.setTimeout(() => setReady(true), 400);
    return () => clearTimeout(h);
  }, []);
  return ready;
}
