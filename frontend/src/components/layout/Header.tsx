import { getTranslations } from "next-intl/server";
import { Menu } from "lucide-react";
import Image from "next/image";
import type { ClinicSettings } from "@/lib/api";
import type { ComponentProps } from "react";
import { Link } from "@/i18n/navigation";
import { NavLink } from "./NavLink";

export async function Header({ settings }: { settings: ClinicSettings | null }) {
  const t = await getTranslations("nav");
  const name = settings?.name ?? "Oq Marvarid Dental";
  const logo = settings?.logo?.src;

  type NavHref = ComponentProps<typeof Link>["href"];
  const links: { key: string; href: NavHref }[] = [
    { key: "services", href: "/xizmatlar" },
    { key: "doctors", href: "/shifokorlar" },
    { key: "cases", href: "/ishlarimiz" },
    { key: "reviews", href: "/sharhlar" },
    { key: "blog", href: "/blog" },
    { key: "contact", href: "/aloqa" },
  ];
  // Narxlar faqat koʻrinsa (ADR: prices_visible)
  if (settings?.prices_visible !== false) {
    links.splice(1, 0, { key: "prices", href: "/narxlar" });
  }

  const [first, ...rest] = name.split(" ");

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-surface/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3.5">
        <Link href="/" className="flex items-center gap-2">
          {logo ? (
            <Image src={logo} alt={name} width={140} height={38} className="h-9 w-auto" />
          ) : (
            <span className="font-display text-xl font-extrabold tracking-tight text-brand">
              {first} <span className="text-ink">{rest.join(" ")}</span>
            </span>
          )}
        </Link>

        <nav className="hidden gap-7 text-sm font-medium md:flex">
          {links.map((l) => (
            <NavLink key={l.key} href={l.href}>
              {t(l.key)}
            </NavLink>
          ))}
        </nav>

        {/* Mobil menyu — JS'siz disclosure */}
        <details className="relative md:hidden">
          <summary className="flex h-10 w-10 cursor-pointer list-none items-center justify-center rounded-lg text-ink [&::-webkit-details-marker]:hidden">
            <Menu className="h-6 w-6" aria-hidden />
            <span className="sr-only">Menyu</span>
          </summary>
          <nav className="absolute right-0 z-50 mt-2 w-56 rounded-xl border border-line bg-surface p-2 shadow-lg">
            {links.map((l) => (
              <NavLink
                key={l.key}
                href={l.href}
                className="block rounded-lg px-3 py-2.5 text-sm font-medium"
              >
                {t(l.key)}
              </NavLink>
            ))}
          </nav>
        </details>
      </div>
    </header>
  );
}
