import { MapPin, Phone, Send } from "lucide-react";
import type { ClinicSettings } from "@/lib/api";
import { telHref } from "@/lib/format";

/** Yopishqoq pastki panel (mobil) — real deeplinklar. */
export function MobileActionBar({ settings }: { settings: ClinicSettings | null }) {
  const phone = settings?.phone_primary || "+998712004040";
  const tg = settings?.telegram_username;
  const map = settings?.yandex_maps_url || settings?.two_gis_url;
  const items = [
    { icon: Phone, label: "Qoʻngʻiroq", href: telHref(phone) },
    tg ? { icon: Send, label: "Telegram", href: `https://t.me/${tg}` } : null,
    map ? { icon: MapPin, label: "Manzil", href: map } : null,
  ].filter(Boolean) as { icon: typeof Phone; label: string; href: string }[];

  return (
    <>
      <div
        className="fixed inset-x-0 bottom-0 z-50 grid border-t border-line bg-surface/95 backdrop-blur md:hidden"
        style={{
          gridTemplateColumns: `repeat(${items.length}, 1fr)`,
          paddingBottom: "env(safe-area-inset-bottom)",
        }}
      >
        {items.map((it) => (
          <a
            key={it.label}
            href={it.href}
            className="flex min-h-14 flex-col items-center justify-center gap-0.5 text-xs font-medium text-ink-muted active:bg-brand-50"
          >
            <it.icon className="h-5 w-5 text-brand" aria-hidden />
            {it.label}
          </a>
        ))}
      </div>
      {/* spacer — panel footer'ni yopmasin (CLS 0) */}
      <div className="h-14 md:hidden" aria-hidden />
    </>
  );
}
