"use client";

import dynamic from "next/dynamic";
import { useWebGLReady } from "./useWebGLReady";

const HeroTooth = dynamic(() => import("./HeroTooth").then((m) => m.HeroTooth), { ssr: false });

/** Hero 3D tishni faqat qodir qurilmada mount qiladi (ADR-011). Aks holda poster qoladi. */
export function SceneGuard() {
  const ready = useWebGLReady();
  return ready ? <HeroTooth /> : null;
}
