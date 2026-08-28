"use client";

import { useEffect } from "react";
import { usePathname } from "@/i18n/navigation";

/**
 * Mobil `<details>` menyusini navigatsiyada va Escape'da yopadi (T-RESP-05).
 *
 * Nega kerak: `<details>` layout segmentida yashaydi, App Router esa soft-navigatsiyada
 * layout DOM'ini remount qilmaydi — shuning uchun havola bosilgach menyu OCHIQ qolib,
 * yangi sahifa ustida osilib turardi. Native `<details>` Escape'da ham yopilmaydi.
 *
 * Server `Header` client'ga aylantirilmaydi — JS'siz `<details>` baseline saqlanadi;
 * bu kichik client hamroh faqat ochiq menyularni yopadi.
 */
export function CloseMenuOnNav() {
  const pathname = usePathname();

  useEffect(() => {
    document
      .querySelectorAll<HTMLDetailsElement>("details[data-mobile-menu][open]")
      .forEach((d) => {
        d.open = false;
      });
  }, [pathname]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      document
        .querySelectorAll<HTMLDetailsElement>("details[data-mobile-menu][open]")
        .forEach((d) => {
          d.open = false;
        });
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  return null;
}
