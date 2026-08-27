"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Loader2, XCircle } from "lucide-react";
import {
  cancelAppointment,
  fetchAppointment,
  type PublicAppointment,
} from "@/lib/api";
import { formatWhen } from "@/lib/format";
import { RescheduleFlow } from "./RescheduleFlow";

export function ManageAppointment({ token }: { token: string }) {
  const t = useTranslations("manage");
  const locale = useLocale();
  const [appt, setAppt] = useState<PublicAppointment | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [reason, setReason] = useState("");
  const [showCancel, setShowCancel] = useState(false);
  const [showResched, setShowResched] = useState(false);

  useEffect(() => {
    fetchAppointment(token, locale)
      .then(setAppt)
      .finally(() => setLoading(false));
  }, [token]);

  async function doCancel() {
    setCancelling(true);
    const r = await cancelAppointment(token, reason);
    setCancelling(false);
    if (r.ok) {
      setAppt((a) => (a ? { ...a, status: "cancelled_by_patient", can_cancel: false, can_reschedule: false } : a));
      setShowCancel(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-slate-400">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  if (!appt) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center">
        <XCircle className="mx-auto mb-3 h-10 w-10 text-slate-300" />
        <h1 className="font-display text-xl font-bold text-slate-900">{t("notFound")}</h1>
        <p className="mt-2 text-sm text-slate-500">{t("notFoundHint")}</p>
        <a href={`/${locale}`} className="mt-5 inline-block text-sm font-semibold text-brand">
          {t("back")}
        </a>
      </div>
    );
  }

  const when = formatWhen(appt.starts_at, locale);
  const cancelled = appt.status.startsWith("cancelled");

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl font-extrabold text-slate-900">{t("title")}</h1>
        <span
          className={
            "rounded-full px-3 py-1 text-xs font-semibold " +
            (cancelled
              ? "bg-slate-100 text-slate-500"
              : appt.status === "confirmed"
                ? "bg-brand/10 text-brand"
                : "bg-amber-100 text-amber-700")
          }
        >
          {t(`status.${appt.status}` as never)}
        </span>
      </div>

      <div className="mt-6 space-y-3 text-sm">
        <Row label={t("when")} value={when} />
        {appt.service_title && <Row label={t("service")} value={appt.service_title} />}
        {appt.doctor_name && (
          <Row label={t("doctor")} value={`${appt.doctor_name}${appt.doctor_specialization ? ` — ${appt.doctor_specialization}` : ""}`} />
        )}
        <Row label="" value={<span className="font-mono font-bold tracking-widest">{appt.code}</span>} />
      </div>

      {(appt.can_cancel || appt.can_reschedule) && !showCancel && !showResched && (
        <div className="mt-8 flex flex-wrap gap-3">
          {appt.can_reschedule && (
            <button
              onClick={() => setShowResched(true)}
              className="rounded-full bg-brand px-5 py-2.5 text-sm font-semibold text-white hover:opacity-90"
            >
              {t("reschedule")}
            </button>
          )}
          {appt.can_cancel && (
            <button
              onClick={() => setShowCancel(true)}
              className="rounded-full border border-red-200 px-5 py-2.5 text-sm font-semibold text-red-600 hover:bg-red-50"
            >
              {t("cancel")}
            </button>
          )}
        </div>
      )}

      {showResched && (
        <RescheduleFlow
          token={token}
          serviceId={appt.service_id ?? null}
          doctorId={appt.doctor_id ?? null}
          onDone={(startsAt) => {
            setAppt((a) => (a ? { ...a, starts_at: startsAt } : a));
            setShowResched(false);
          }}
        />
      )}

      {showCancel && (
        <div className="mt-8 rounded-xl border border-red-200 bg-red-50 p-5">
          <p className="text-sm font-medium text-red-800">{t("cancelConfirm")}</p>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder={t("cancelReason")}
            rows={2}
            className="mt-3 w-full rounded-lg border border-red-200 px-3 py-2 text-sm"
          />
          <div className="mt-3 flex gap-2">
            <button
              onClick={doCancel}
              disabled={cancelling}
              className="inline-flex items-center gap-2 rounded-full bg-red-600 px-5 py-2 text-sm font-semibold text-white disabled:opacity-50"
            >
              {cancelling && <Loader2 className="h-4 w-4 animate-spin" />}
              {t("cancel")}
            </button>
            <button
              onClick={() => setShowCancel(false)}
              className="rounded-full px-4 py-2 text-sm font-medium text-slate-500"
            >
              {t("back")}
            </button>
          </div>
        </div>
      )}

      {cancelled && (
        <p className="mt-6 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-500">{t("cancelled")}</p>
      )}
    </div>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 border-b border-slate-100 pb-3">
      <span className="text-slate-400">{label}</span>
      <span className="text-right font-medium text-slate-900">{value}</span>
    </div>
  );
}
