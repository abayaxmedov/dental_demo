"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Loader2 } from "lucide-react";
import { fetchSlots, rescheduleAppointment, type ApiDay } from "@/lib/api";
import { formatDayChip } from "@/lib/format";

/** Qabulni boshqa vaqtga koʻchirish — slot picker + reschedule chaqiruvi. */
export function RescheduleFlow({
  token,
  serviceId,
  doctorId,
  onDone,
}: {
  token: string;
  serviceId: number | null;
  doctorId: number | null;
  onDone: (startsAt: string) => void;
}) {
  const t = useTranslations("manage");
  const locale = useLocale();
  const [days, setDays] = useState<ApiDay[]>([]);
  const [dayIdx, setDayIdx] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchSlots({ service: serviceId ?? undefined, doctor: doctorId ?? undefined, exclude: token })
      .then((res) => {
        if (res) {
          setDays(res.days);
          const first = res.days.findIndex((d) => d.slots.length > 0);
          if (first >= 0) setDayIdx(first);
        }
      })
      .finally(() => setLoading(false));
  }, [serviceId, doctorId, token]);

  async function pick(startUtc: string) {
    setSubmitting(true);
    setErr(null);
    const r = await rescheduleAppointment(token, startUtc, locale);
    setSubmitting(false);
    if (r.ok) onDone(r.data.starts_at);
    else setErr(r.problem.detail || t("noSlots"));
  }

  if (loading)
    return (
      <p className="flex items-center gap-2 py-6 text-sm text-ink-subtle">
        <Loader2 className="h-4 w-4 animate-spin" /> {t("loadingSlots")}
      </p>
    );

  const active = days[dayIdx];
  return (
    <div className="mt-6 rounded-xl border border-line bg-surface-muted p-5">
      <p className="mb-3 font-medium text-ink">{t("rescheduleTitle")}</p>
      <div className="mb-3 flex gap-2 overflow-x-auto pb-1">
        {days.map((d, i) => {
          const disabled = d.slots.length === 0;
          const { wd, dm } = formatDayChip(d.date, locale);
          return (
            <button
              key={d.date}
              type="button"
              disabled={disabled}
              onClick={() => setDayIdx(i)}
              className={
                "flex min-w-[60px] shrink-0 flex-col items-center rounded-lg border px-2.5 py-1.5 text-xs " +
                (i === dayIdx
                  ? "border-brand bg-brand text-white"
                  : disabled
                    ? "border-line text-ink-subtle opacity-50"
                    : "border-line text-ink-muted hover:border-brand")
              }
            >
              <span className="font-semibold uppercase">{wd}</span>
              <span>{dm}</span>
            </button>
          );
        })}
      </div>
      {active && active.slots.length ? (
        <div className="flex flex-wrap gap-2">
          {active.slots.map((s) => (
            <button
              key={s.start_utc}
              type="button"
              disabled={submitting}
              onClick={() => pick(s.start_utc)}
              className="rounded-lg border border-line px-3 py-2 text-sm font-medium text-ink hover:border-brand hover:text-brand disabled:opacity-50"
            >
              {s.label}
            </button>
          ))}
        </div>
      ) : (
        <p className="text-sm text-ink-subtle">{t("noSlots")}</p>
      )}
      {submitting ? (
        <p className="mt-3 flex items-center gap-2 text-sm text-ink-subtle">
          <Loader2 className="h-4 w-4 animate-spin" /> …
        </p>
      ) : null}
      {err ? <p className="mt-3 text-sm text-red-600">{err}</p> : null}
    </div>
  );
}
