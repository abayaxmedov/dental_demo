"use client";

import { useEffect, useState } from "react";

export type WebGLStatus = "pending" | "ready" | "unsupported";

/**
 * WebGL sahnasi shu qurilmada ishga tushsinmi? (ADR-011).
 *
 * Uch shart — `(min-width:1024px)`, `(pointer:fine)`, `prefers-reduced-motion` —
 * ATAYLAB CSS'da ham takrorlangan (globals.css `.hero-stage`), chunki hero posteri
 * shu media query bilan yashiriladi. Ikkalasi bir xil boʻlishi SHART.
 * Qolgan shartlar (WebGL2 / saveData / 2g) faqat JS'da bilinadi — ular yiqilsa
 * status `unsupported` boʻladi va chaqiruvchi poster'ni qaytaradi.
 *
 * `immediate` — hero uchun: poster koʻrsatilmagani sababli idle'ni kutish faqat
 * boʻsh panelni uzaytiradi. Ekrandan pastdagi sahnalar (tish xaritasi) idle kutadi.
 */
export function useWebGLStatus({ immediate = false }: { immediate?: boolean } = {}): WebGLStatus {
  const [status, setStatus] = useState<WebGLStatus>("pending");

  useEffect(() => {
    const mm = (q: string) => window.matchMedia(q).matches;
    const bail = () => setStatus("unsupported");

    if (!mm("(min-width: 1024px)")) return bail();
    if (!mm("(pointer: fine)")) return bail();
    if (mm("(prefers-reduced-motion: reduce)")) return bail();

    const conn = (navigator as { connection?: { saveData?: boolean; effectiveType?: string } })
      .connection;
    if (conn?.saveData) return bail();
    if (conn?.effectiveType && /(^|\s)(slow-)?2g/.test(conn.effectiveType)) return bail();

    try {
      if (!document.createElement("canvas").getContext("webgl2")) return bail();
    } catch {
      return bail();
    }

    if (immediate) {
      setStatus("ready");
      return;
    }

    const w = window as Window & {
      requestIdleCallback?: (cb: () => void, o?: { timeout: number }) => number;
      cancelIdleCallback?: (h: number) => void;
    };
    if (w.requestIdleCallback) {
      const h = w.requestIdleCallback(() => setStatus("ready"), { timeout: 2000 });
      return () => w.cancelIdleCallback?.(h);
    }
    const h = window.setTimeout(() => setStatus("ready"), 400);
    return () => clearTimeout(h);
  }, [immediate]);

  return status;
}

/** Eski, boolean API — ekrandan pastdagi sahnalar shuni ishlatadi. */
export function useWebGLReady(opts?: { immediate?: boolean }): boolean {
  return useWebGLStatus(opts) === "ready";
}
