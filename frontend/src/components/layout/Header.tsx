import { getTranslations } from "next-intl/server";
import type { ClinicSettings } from "@/lib/api";

export async function Header({ settings }: { settings: ClinicSettings | null }) {
  const t = await getTranslations("nav");
  const name = settings?.name ?? "Oq Marvarid Dental";
  const [first, ...rest] = name.split(" ");

  const links = [
    { key: "services", href: "#xizmatlar" },
    { key: "prices", href: "#narxlar" },
    { key: "doctors", href: "#shifokorlar" },
    { key: "reviews", href: "#sharhlar" },
    { key: "contact", href: "#aloqa" },
  ] as const;

  return (
    <header className="sticky top-0 z-40 border-b border-slate-100 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <a href="#" className="font-display text-xl font-extrabold tracking-tight text-brand">
          {first} <span className="text-slate-900">{rest.join(" ")}</span>
        </a>
        <nav className="hidden gap-7 text-sm font-medium text-slate-600 md:flex">
          {links.map((l) => (
            <a key={l.key} href={l.href} className="transition hover:text-brand">
              {t(l.key)}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}
