import { MapPin, Clock, Phone } from "lucide-react";
import { getTranslations } from "next-intl/server";
import type { ClinicSettings } from "@/lib/api";
import { formatPhone, summariseHours, telHref } from "@/lib/format";
import { LangSwitcher } from "./LangSwitcher";

export async function Topbar({
  settings,
  locale,
}: {
  settings: ClinicSettings | null;
  locale: string;
}) {
  const t = await getTranslations("topbar");
  const address = settings?.address || t("address");
  const phone = settings?.phone_primary || "+998712004040";
  const hours = summariseHours(settings?.working_hours, locale) ?? t("hours");

  return (
    <div className="border-b border-line bg-surface-muted text-sm text-ink-muted">
      {/* Telefonda faqat telefon + til: manzil va ish vaqti mobil menyuda (Header). */}
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-0.5 md:py-2">
        <div className="hidden flex-wrap items-center gap-x-5 gap-y-1 md:flex">
          <span className="inline-flex items-center gap-1.5">
            <MapPin className="h-4 w-4 shrink-0 text-brand" aria-hidden />
            {address}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Clock className="h-4 w-4 shrink-0 text-brand" aria-hidden />
            {hours}
          </span>
        </div>
        <div className="flex w-full items-center justify-between gap-2 md:w-auto md:justify-start md:gap-4">
          <a
            href={telHref(phone)}
            className="inline-flex min-h-11 items-center gap-1.5 whitespace-nowrap font-semibold text-ink hover:text-brand"
          >
            {/* 320px ekranda raqam + 3 til tugmasi sigʻishi uchun ikonka yashiriladi */}
            <Phone className="h-4 w-4 shrink-0 text-brand max-[359px]:hidden" aria-hidden />
            {formatPhone(phone)}
          </a>
          <LangSwitcher />
        </div>
      </div>
    </div>
  );
}
