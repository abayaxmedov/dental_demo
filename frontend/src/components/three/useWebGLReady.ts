"use client";

import { useEffect, useState } from "react";

export type WebGLStatus = "pending" | "ready" | "unsupported";

/** Telefon/planshetda shundan kam RAM (GB) boʻlsa — poster qoladi. Faqat Chromium beradi. */
const MIN_TOUCH_DEVICE_MEMORY_GB = 4;

/**
 * WebGL sahnasi shu qurilmada ishga tushsinmi? (ADR-011, ADR-023).
 *
 * Ikki rejim:
 *  - **desktop** — `(min-width:1024px)` + `(pointer:fine)`. Bu ikki shart +
 *    `prefers-reduced-motion` ATAYLAB CSS'da ham takrorlangan (globals.css `.hero-stage`),
 *    chunki desktopda hero posteri shu media query bilan yashiriladi. Ikkalasi bir xil boʻlishi SHART.
 *  - **touch** (`allowTouch`) — telefon/planshet. Poster LCP boʻlib koʻrinadi, sahna sahifa
 *    `load` + idle'dan keyin mount qilinadi va chaqiruvchi uni poster ustiga crossfade qiladi.
 *    Qoʻshimcha shart: `deviceMemory` < 4 GB → poster (zaif Android).
 *
 * Umumiy shartlar (reduced-motion / saveData / 2g / WebGL2) yiqilsa status `unsupported`
 * boʻladi va chaqiruvchi poster'ni qaytaradi.
 *
 * `immediate` — faqat desktop hero uchun: poster koʻrsatilmagani sababli idle'ni kutish faqat
 * boʻsh panelni uzaytiradi. Ekrandan pastdagi sahnalar (tish xaritasi) idle kutadi.
 */
export function useWebGLStatus({
  immediate = false,
  allowTouch = false,
}: { immediate?: boolean; allowTouch?: boolean } = {}): WebGLStatus {
  const [status, setStatus] = useState<WebGLStatus>("pending");

  useEffect(() => {
    const mm = (q: string) => window.matchMedia(q).matches;
    const bail = () => setStatus("unsupported");

    const desktop = mm("(min-width: 1024px)") && mm("(pointer: fine)");
    if (!desktop && !allowTouch) return bail();
    if (mm("(prefers-reduced-motion: reduce)")) return bail();

    const nav = navigator as {
      connection?: { saveData?: boolean; effectiveType?: string };
      deviceMemory?: number;
    };
    if (nav.connection?.saveData) return bail();
    if (nav.connection?.effectiveType && /(^|\s)(slow-)?2g/.test(nav.connection.effectiveType)) {
      return bail();
    }
    if (!desktop && nav.deviceMemory && nav.deviceMemory < MIN_TOUCH_DEVICE_MEMORY_GB) {
      return bail();
    }

    try {
      if (!document.createElement("canvas").getContext("webgl2")) return bail();
    } catch {
      return bail();
    }

    if (immediate && desktop) {
      setStatus("ready");
      return;
    }

    const w = window as Window & {
      requestIdleCallback?: (cb: () => void, o?: { timeout: number }) => number;
      cancelIdleCallback?: (h: number) => void;
    };
    let idle: number | undefined;
    let timer: number | undefined;
    const schedule = () => {
      if (w.requestIdleCallback) {
        idle = w.requestIdleCallback(() => setStatus("ready"), { timeout: 2000 });
      } else {
        timer = window.setTimeout(() => setStatus("ready"), 400);
      }
    };

    // Touch: poster (LCP) va sahifa toʻliq yuklanmaguncha three.js chunk'i tarmoqni band qilmasin.
    const waitLoad = !desktop && document.readyState !== "complete";
    if (waitLoad) window.addEventListener("load", schedule, { once: true });
    else schedule();

    return () => {
      if (waitLoad) window.removeEventListener("load", schedule);
      if (idle !== undefined) w.cancelIdleCallback?.(idle);
      if (timer !== undefined) clearTimeout(timer);
    };
  }, [immediate, allowTouch]);

  return status;
}

/** Eski, boolean API — ekrandan pastdagi sahnalar shuni ishlatadi. */
export function useWebGLReady(opts?: { immediate?: boolean }): boolean {
  return useWebGLStatus(opts) === "ready";
}
