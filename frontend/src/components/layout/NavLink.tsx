"use client";

import type { ComponentProps, ReactNode } from "react";
import { Link, usePathname } from "@/i18n/navigation";
/** Ichki nav havolasi — aktiv holatni ichki pathname (template) boʻyicha aniqlaydi. */
type LinkHref = ComponentProps<typeof Link>["href"];

export function NavLink({
  href,
  children,
  className = "",
  inactiveClassName = "text-ink-muted hover:text-brand",
}: {
  href: LinkHref;
  children: ReactNode;
  className?: string;
  /** Aktiv boʻlmagan holat rangi (mobil menyu toʻqroq matn ishlatadi). */
  inactiveClassName?: string;
}) {
  const pathname = usePathname();
  const target = typeof href === "string" ? href : "";
  const active = target === "/" ? pathname === "/" : !!target && pathname.startsWith(target);
  return (
    <Link
      href={href}
      aria-current={active ? "page" : undefined}
      className={`shrink-0 whitespace-nowrap ${className} ${active ? "text-brand" : inactiveClassName}`}
    >
      {children}
    </Link>
  );
}
