import { MapPin, Clock, Phone } from "lucide-react";
import { getTranslations } from "next-intl/server";
import type { ClinicSettings } from "@/lib/api";
import { formatPhone, telHref } from "@/lib/format";
import { LangSwitcher } from "./LangSwitcher";

const WEEKDAYS_SHORT: Record<string, string[]> = {
  uz: ["Du", "Se", "Ch", "Pa", "Ju", "Sha", "Yak"],
  ru: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
  en: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
};

/** Ish vaqtini "Du–Sha 09:00–19:00" koʻrinishida qisqartiradi. */
function summariseHours(
  hours: ClinicSettings["working_hours"] | undefined,
  locale: string,
): string | null {
  if (!hours?.length) return null;
  const open = hours.filter((h) => !h.is_closed && h.opens && h.closes);
  if (!open.length) return null;

  const names = WEEKDAYS_SHORT[locale] ?? WEEKDAYS_SHORT.uz;
  const hhmm = (t: string) => t.slice(0, 5);
  const first = open[0];
  const last = open[open.length - 1];
  const span =
    open.length === 1 ? names[first.weekday] : `${names[first.weekday]}–${names[last.weekday]}`;
  return `${span} ${hhmm(first.opens!)}–${hhmm(first.closes!)}`;
}

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
    <div className="border-b border-slate-100 bg-slate-50 text-sm text-slate-600">
      <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-x-5 gap-y-1">
          <span className="inline-flex items-center gap-1.5">
            <MapPin className="h-4 w-4 shrink-0 text-brand" aria-hidden />
            {address}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Clock className="h-4 w-4 shrink-0 text-brand" aria-hidden />
            {hours}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href={telHref(phone)}
            className="inline-flex items-center gap-1.5 font-semibold text-slate-800 hover:text-brand"
          >
            <Phone className="h-4 w-4 shrink-0 text-brand" aria-hidden />
            {formatPhone(phone)}
          </a>
          <LangSwitcher />
        </div>
      </div>
    </div>
  );
}
