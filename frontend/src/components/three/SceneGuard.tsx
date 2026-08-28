"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import { useWebGLStatus } from "./useWebGLReady";

const HeroTooth = dynamic(() => import("./HeroTooth").then((m) => m.HeroTooth), { ssr: false });

/** Chunk sekin/yiqilsa posterni qancha kutib qaytaramiz. */
const CHUNK_TIMEOUT_MS = 6000;

/**
 * Hero 3D tishni qodir desktopda DARHOL mount qiladi (ADR-011).
 *
 * Poster foto `globals.css` da shu media query bilan yashirilgan, shuning uchun bu
 * yerda ikkita fallback SHART — aks holda foydalanuvchi boʻsh panel koʻradi:
 *  1) gate yiqilsa (WebGL2 yoʻq / saveData / 2g) → `hero-3d-failed`;
 *  2) three.js chunk'i 6 s ichida canvas chizmasa (sekin tarmoq / chunk xatosi) → xuddi shunday.
 */
export function SceneGuard() {
  const status = useWebGLStatus({ immediate: true });
  const [failed, setFailed] = useState(false);
  const host = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (status === "unsupported") {
      setFailed(true);
      return;
    }
    if (status !== "ready") return;
    // Canvas haqiqatan paydo boʻldimi? Yoʻq boʻlsa — posterni qaytaramiz.
    const h = window.setTimeout(() => {
      if (!host.current?.querySelector("canvas")) setFailed(true);
    }, CHUNK_TIMEOUT_MS);
    return () => clearTimeout(h);
  }, [status]);

  useEffect(() => {
    const root = document.documentElement;
    if (failed) root.classList.add("hero-3d-failed");
    else root.classList.remove("hero-3d-failed");
    return () => root.classList.remove("hero-3d-failed");
  }, [failed]);

  return (
    <div ref={host} className="contents">
      {status === "ready" && !failed ? <HeroTooth /> : null}
    </div>
  );
}
