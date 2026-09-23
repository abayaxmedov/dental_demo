import { getLocale, getTranslations } from "next-intl/server";
import {
  ChevronRight,
  Clock,
  Images,
  MapPin,
  Menu,
  MessageSquareQuote,
  Newspaper,
  Phone,
  Send,
  Stethoscope,
  UserRound,
  Wallet,
  X,
  type LucideIcon,
} from "lucide-react";
import Image from "next/image";
import type { ClinicSettings } from "@/lib/api";
import type { ComponentProps } from "react";
import { Link } from "@/i18n/navigation";
import { formatPhone, summariseHours, telHref } from "@/lib/format";
import { NavLink } from "./NavLink";
import { CloseMenuOnNav } from "./CloseMenuOnNav";

type NavHref = ComponentProps<typeof Link>["href"];

function Logo({ settings }: { settings: ClinicSettings | null }) {
  const name = settings?.name ?? "Oq Marvarid Dental";
  const logo = settings?.logo?.src;
  const [first, ...rest] = name.split(" ");
  return (
    <Link href="/" className="flex min-h-11 min-w-0 items-center gap-2">
      {logo ? (
        // Logo 520×140 — telefonda kattaroq (h-12), aks holda "DENTAL" yozuvi oʻqilmaydi.
        <Image src={logo} alt={name} width={178} height={48} className="h-12 w-auto md:h-10" />
      ) : (
        <span className="truncate font-display text-2xl font-extrabold tracking-tight text-brand md:text-xl">
          {first} <span className="text-ink">{rest.join(" ")}</span>
        </span>
      )}
    </Link>
  );
}

export async function Header({ settings }: { settings: ClinicSettings | null }) {
  const t = await getTranslations("nav");
  const tt = await getTranslations("topbar");
  const th = await getTranslations("hero");
  const locale = await getLocale();

  const links: { key: string; href: NavHref; icon: LucideIcon }[] = [
    { key: "services", href: "/xizmatlar", icon: Stethoscope },
    { key: "doctors", href: "/shifokorlar", icon: UserRound },
    { key: "cases", href: "/ishlarimiz", icon: Images },
    { key: "reviews", href: "/sharhlar", icon: MessageSquareQuote },
    { key: "blog", href: "/blog", icon: Newspaper },
    { key: "contact", href: "/aloqa", icon: Phone },
  ];
  // Narxlar faqat koʻrinsa (ADR: prices_visible)
  if (settings?.prices_visible !== false) {
    links.splice(1, 0, { key: "prices", href: "/narxlar", icon: Wallet });
  }

  const phone = settings?.phone_primary || "+998712004040";
  const address = settings?.address || tt("address");
  const hours = summariseHours(settings?.working_hours, locale) ?? tt("hours");
  const tg = settings?.telegram_username;

  // Banner landmark'i va sticky layout'dagi <header> da — bu yerda faqat nav qatori.
  // Mobilda backdrop-blur YOʻQ: u `fixed` bolalar uchun containing block yaratadi va
  // toʻliq ekranli menyu header ichiga qamalib qolardi.
  return (
    <div className="border-b border-line bg-surface md:bg-surface/90 md:backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-2.5 md:py-3.5">
        <Logo settings={settings} />

        <nav className="hidden gap-4 text-sm font-medium md:flex lg:gap-7">
          {links.map((l) => (
            <NavLink key={l.key} href={l.href} className="inline-flex min-h-11 items-center">
              {t(l.key)}
            </NavLink>
          ))}
        </nav>

        {/*
          Mobil menyu — JS'siz disclosure, toʻliq ekranli sheet.
          Ochiq holatda <summary> oʻzi `fixed` boʻlib sheet ustidagi ✕ tugmaga aylanadi —
          shuning uchun JS'siz ham yopiladi. Scroll lock: globals.css (`html:has(...)`).
        */}
        <details data-mobile-menu className="group md:hidden">
          <summary
            aria-label={t("menu")}
            className="relative z-[70] flex h-11 w-11 cursor-pointer list-none items-center justify-center rounded-full text-ink transition hover:bg-brand-50 group-open:fixed group-open:right-4 group-open:top-3 group-open:bg-surface-muted [&::-webkit-details-marker]:hidden"
          >
            <Menu className="h-6 w-6 group-open:hidden" aria-hidden />
            <X className="hidden h-6 w-6 group-open:block" aria-hidden />
          </summary>

          <div className="mobile-menu-sheet fixed inset-0 z-[60] flex flex-col overflow-y-auto overscroll-contain bg-surface">
            <div className="flex items-center border-b border-line px-4 py-2.5 pr-20">
              <Logo settings={settings} />
            </div>

            <nav aria-label={t("menu")} className="px-3 py-3">
              {links.map((l) => (
                <NavLink
                  key={l.key}
                  href={l.href}
                  inactiveClassName="text-ink"
                  className="group/item flex min-h-14 items-center gap-3 rounded-xl px-2 text-base font-semibold transition active:bg-brand-50 aria-[current=page]:bg-brand-50"
                >
                  <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand group-aria-[current=page]/item:bg-brand group-aria-[current=page]/item:text-white">
                    <l.icon className="h-5 w-5" aria-hidden />
                  </span>
                  {t(l.key)}
                  <ChevronRight className="ml-auto h-5 w-5 text-ink-subtle" aria-hidden />
                </NavLink>
              ))}
            </nav>

            <div className="mt-auto space-y-4 border-t border-line bg-surface-muted px-4 pb-8 pt-5">
              <Link
                href={{ pathname: "/", hash: "qabul" }}
                className="flex min-h-12 w-full items-center justify-center rounded-full bg-brand px-6 text-base font-semibold text-white shadow-sm"
              >
                {th("ctaBook")}
              </Link>
              <ul className="space-y-3 text-sm text-ink-muted">
                <li>
                  <a href={telHref(phone)} className="inline-flex min-h-11 items-center gap-3 text-base font-semibold text-ink">
                    <Phone className="h-5 w-5 shrink-0 text-brand" aria-hidden />
                    {formatPhone(phone)}
                  </a>
                </li>
                {tg ? (
                  <li>
                    <a href={`https://t.me/${tg}`} className="inline-flex min-h-11 items-center gap-3 font-medium text-ink">
                      <Send className="h-5 w-5 shrink-0 text-brand" aria-hidden />@{tg}
                    </a>
                  </li>
                ) : null}
                <li className="flex gap-3">
                  <MapPin className="mt-0.5 h-5 w-5 shrink-0 text-brand" aria-hidden />
                  {address}
                </li>
                <li className="flex gap-3">
                  <Clock className="h-5 w-5 shrink-0 text-brand" aria-hidden />
                  {hours}
                </li>
              </ul>
            </div>
          </div>
        </details>
        <CloseMenuOnNav />
      </div>
    </div>
  );
}
