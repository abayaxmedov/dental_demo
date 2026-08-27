import { getTranslations } from "next-intl/server";
import { MapPin, Phone, Send } from "lucide-react";
import type { ClinicSettings } from "@/lib/api";
import { formatPhone, telHref } from "@/lib/format";

const WEEKDAYS: Record<string, string[]> = {
  uz: ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"],
  ru: ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
  en: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
};

export async function Footer({
  settings,
  locale,
}: {
  settings: ClinicSettings | null;
  locale: string;
}) {
  const t = await getTranslations();
  const names = WEEKDAYS[locale] ?? WEEKDAYS.uz;
  const phone = settings?.phone_primary ?? "+998712004040";
  const hhmm = (v: string | null | undefined) => (v ? v.slice(0, 5) : "");

  return (
    <footer id="aloqa" className="bg-slate-900 text-slate-300 scroll-mt-20">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-16 sm:grid-cols-2 lg:grid-cols-3">
        <div>
          <p className="font-display text-lg font-extrabold text-white">
            {settings?.name ?? "Oq Marvarid Dental"}
          </p>
          <p className="mt-3 text-sm leading-relaxed text-slate-400">
            {settings?.about_short}
          </p>
          {settings?.license_text ? (
            <p className="mt-4 text-xs text-slate-400">{settings.license_text}</p>
          ) : null}
        </div>

        <div>
          <p className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">
            {t("nav.contact")}
          </p>
          <ul className="space-y-3 text-sm">
            <li className="flex items-start gap-2">
              <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-brand" aria-hidden />
              <span>{settings?.address}</span>
            </li>
            <li>
              <a href={telHref(phone)} className="flex items-center gap-2 hover:text-white">
                <Phone className="h-4 w-4 shrink-0 text-brand" aria-hidden />
                {formatPhone(phone)}
              </a>
            </li>
            {settings?.telegram_username ? (
              <li>
                <a
                  href={`https://t.me/${settings.telegram_username}`}
                  className="flex items-center gap-2 hover:text-white"
                >
                  <Send className="h-4 w-4 shrink-0 text-brand" aria-hidden />@
                  {settings.telegram_username}
                </a>
              </li>
            ) : null}
          </ul>
        </div>

        <div>
          <p className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">
            {t("topbar.hours")}
          </p>
          <ul className="space-y-1.5 text-sm">
            {settings?.working_hours?.map((h) => (
              <li key={h.weekday} className="flex justify-between gap-4">
                <span className="text-slate-400">{names[h.weekday]}</span>
                <span className={h.is_closed ? "text-slate-400" : "text-slate-200"}>
                  {h.is_closed ? h.note || "—" : `${hhmm(h.opens)}–${hhmm(h.closes)}`}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="border-t border-slate-800">
        <div className="mx-auto max-w-6xl px-4 py-5 text-xs text-slate-400">
          © {new Date().getFullYear()} {settings?.legal_entity_name ?? settings?.name}
        </div>
      </div>
    </footer>
  );
}
