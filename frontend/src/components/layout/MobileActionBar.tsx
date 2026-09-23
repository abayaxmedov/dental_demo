import { CalendarCheck, MapPin, Phone, Send } from "lucide-react";
import { getTranslations } from "next-intl/server";
import type { ClinicSettings } from "@/lib/api";
import { Link } from "@/i18n/navigation";
import { telHref } from "@/lib/format";

/**
 * Yopishqoq pastki panel (mobil) — real deeplinklar + asosiy CTA "Yozilish" (qabul formasi).
 * Yozilish tugmasi ATAYLAB kengroq va rangli: bu saytning asosiy konversiya yoʻli.
 */
export async function MobileActionBar({ settings }: { settings: ClinicSettings | null }) {
  const t = await getTranslations("mobileBar");
  const phone = settings?.phone_primary || "+998712004040";
  const tg = settings?.telegram_username;
  const map = settings?.yandex_maps_url || settings?.two_gis_url;
  const items = [
    { icon: Phone, label: t("call"), href: telHref(phone) },
    tg ? { icon: Send, label: t("telegram"), href: `https://t.me/${tg}` } : null,
    map ? { icon: MapPin, label: t("map"), href: map } : null,
  ].filter(Boolean) as { icon: typeof Phone; label: string; href: string }[];

  return (
    <>
      <nav
        aria-label={t("label")}
        className="fixed inset-x-0 bottom-0 z-40 grid border-t border-line bg-surface/95 backdrop-blur lg:hidden"
        style={{
          gridTemplateColumns: `repeat(${items.length}, 1fr) 1.5fr`,
          // Xavfsiz-zona pastki paddingi OLIB TASHLANDI: viewport-fit=cover oʻrnatilmagan,
          // shuning uchun u 0 edi (oʻlik kod, T-RESP-06 / AUDIT).
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
        <Link
          href={{ pathname: "/", hash: "qabul" }}
          className="m-1.5 flex flex-col items-center justify-center gap-0.5 rounded-xl bg-brand text-xs font-semibold text-white shadow-sm active:opacity-90"
        >
          <CalendarCheck className="h-5 w-5" aria-hidden />
          {t("book")}
        </Link>
      </nav>
      {/* spacer — panel footer'ni yopmasin (CLS 0) */}
      <div className="h-14 lg:hidden" aria-hidden />
    </>
  );
}
