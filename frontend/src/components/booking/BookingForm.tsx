"use client";

import { useEffect, useRef, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { CalendarCheck, Check, Loader2, Phone } from "lucide-react";
import {
  createBooking,
  fetchFormToken,
  fetchSlots,
  type ApiDay,
  type ApiSlot,
  type BookingResult,
  type Doctor,
  type Problem,
  type Service,
} from "@/lib/api";
import { formatDayChip, formatWhen } from "@/lib/format";

type Props = {
  services: Service[];
  doctors: Doctor[];
  phone: string;
  telegram: string | null;
};

function uuid() {
  // crypto.randomUUID secure-context'da bor; fallback bilan
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

function groupByPartOfDay(slots: ApiSlot[]) {
  const buckets: Record<string, ApiSlot[]> = { morning: [], afternoon: [], evening: [] };
  for (const s of slots) {
    const h = Number(s.label.slice(0, 2));
    if (h < 12) buckets.morning.push(s);
    else if (h < 17) buckets.afternoon.push(s);
    else buckets.evening.push(s);
  }
  return buckets;
}

export function BookingForm({ services, doctors, phone, telegram }: Props) {
  const t = useTranslations("booking");
  const tc = useTranslations("common");
  const locale = useLocale();

  const [serviceId, setServiceId] = useState<number | "">(services[0]?.id ?? "");
  // Kun tasmasi klaviatura navigatsiyasi uchun (T-FIX-12).
  const dayRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const [doctorId, setDoctorId] = useState<number | "">("");
  const [days, setDays] = useState<ApiDay[]>([]);
  const [dayIdx, setDayIdx] = useState(0);
  const [slot, setSlot] = useState<ApiSlot | null>(null);
  // Tanlangan kun chipini koʻrinishga suramiz — klinika bir necha kun yopiq boʻlsa,
  // birinchi boʻsh kun oʻngda qolib, bemor faqat greyed chiplarni koʻrardi (T-RESP-08).
  useEffect(() => {
    dayRefs.current[dayIdx]?.scrollIntoView({ inline: "center", block: "nearest" });
  }, [dayIdx]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [bookingEnabled, setBookingEnabled] = useState(true);

  const [name, setName] = useState("");
  const [phoneVal, setPhoneVal] = useState("+998 ");
  const [comment, setComment] = useState("");
  const [consent, setConsent] = useState(false);
  const [honeypot, setHoneypot] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BookingResult | null>(null);

  const formTokenRef = useRef<string>("");
  const idemRef = useRef<string>(uuid());
  const abortRef = useRef<AbortController | null>(null);

  // form-token'ni forma ochilganda olamiz
  useEffect(() => {
    fetchFormToken().then((tk) => (formTokenRef.current = tk));
  }, []);

  // slotlarni service/doctor o'zgarganda qayta olamiz (abort bilan)
  useEffect(() => {
    if (!serviceId) return;
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    setLoadingSlots(true);
    fetchSlots({ service: serviceId, doctor: doctorId || null, signal: ac.signal })
      .then((res) => {
        if (ac.signal.aborted) return;
        if (res) {
          setBookingEnabled(res.booking_enabled);
          setDays(res.days);
          setDayIdx((prev) => {
            const firstOpen = res.days.findIndex((d) => d.slots.length > 0);
            return firstOpen >= 0 ? firstOpen : prev;
          });
        }
        setSlot(null);
      })
      .finally(() => {
        if (!ac.signal.aborted) setLoadingSlots(false);
      });
    return () => ac.abort();
  }, [serviceId, doctorId]);

  /** Strelka/Home/End bilan faqat BOʻSH kunlar orasida harakat (APG radiogroup, T-FIX-12). */
  function moveDay(dir: 1 | -1 | "home" | "end") {
    const open = days.map((d, i) => (d.slots.length ? i : -1)).filter((i) => i >= 0);
    if (!open.length) return;
    let next: number;
    if (dir === "home") next = open[0];
    else if (dir === "end") next = open[open.length - 1];
    else {
      const pos = open.indexOf(dayIdx);
      next = pos === -1 ? open[0] : open[(pos + dir + open.length) % open.length];
    }
    setDayIdx(next);
    setSlot(null);
    dayRefs.current[next]?.focus();
  }

  async function refreshSlotsFrom(available?: { days: ApiDay[] }) {
    if (available?.days?.length) {
      setDays((prev) => {
        const map = new Map(prev.map((d) => [d.date, d]));
        for (const d of available.days) map.set(d.date, d);
        return [...map.values()].sort((a, b) => a.date.localeCompare(b.date));
      });
    } else {
      const res = await fetchSlots({ service: serviceId, doctor: doctorId || null });
      if (res) setDays(res.days);
    }
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (submitting || !slot || !serviceId) return;
    setSubmitting(true);
    setError(null);

    const body = {
      service: serviceId,
      doctor: slot.doctor_ids.length === 1 ? slot.doctor_ids[0] : doctorId || null,
      starts_at: slot.start_utc,
      patient_name: name.trim(),
      phone: phoneVal,
      comment: comment.trim(),
      locale,
      consent,
      consent_text_version: "v1",
      form_token: formTokenRef.current,
      idempotency_key: idemRef.current,
      referral_note_2: honeypot,
    };

    const r = await createBooking(body, idemRef.current);
    setSubmitting(false);

    if (r.ok) {
      setResult(r.data);
      if (typeof history !== "undefined") history.replaceState(null, "", "?done=1");
      return;
    }
    const p: Problem = r.problem;
    if (p.code === "slot_taken" || p.code === "slot_unavailable" || p.code === "no_doctor_available") {
      await refreshSlotsFrom(p.available);
      setSlot(null);
      idemRef.current = uuid(); // yangi urinish uchun yangi kalit
      setError(p.detail || t("selectTime"));
    } else if (p.code === "booking_disabled") {
      setBookingEnabled(false);
    } else {
      setError(p.detail || t("errors.networkTitle"));
    }
  }

  if (result) return <SuccessCard result={result} locale={locale} phone={phone} />;

  if (!bookingEnabled) {
    return (
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
        {t("bookingDisabled")}{" "}
        <a href={`tel:${phone.replace(/\s/g, "")}`} className="font-semibold underline">
          {phone}
        </a>
      </div>
    );
  }

  const activeDay = days[dayIdx];
  const buckets = activeDay ? groupByPartOfDay(activeDay.slots) : null;

  return (
    <form onSubmit={submit} className="space-y-6" aria-busy={submitting}>
      {/* Xizmat */}
      <div>
        <label htmlFor="bk-service" className="mb-1.5 block text-sm font-medium text-slate-700">
          {t("service")}
        </label>
        <select
          id="bk-service"
          value={serviceId}
          onChange={(e) => setServiceId(Number(e.target.value))}
          className="w-full rounded-xl border border-slate-300 px-4 py-3 text-base focus:border-brand focus:ring-2 focus:ring-brand/20"
        >
          {services.map((s) => (
            <option key={s.id} value={s.id}>
              {s.title}
            </option>
          ))}
        </select>
      </div>

      {/* Shifokor */}
      <div>
        <label htmlFor="bk-doctor" className="mb-1.5 block text-sm font-medium text-slate-700">
          {t("doctor")}
        </label>
        <select
          id="bk-doctor"
          value={doctorId}
          onChange={(e) => setDoctorId(e.target.value ? Number(e.target.value) : "")}
          className="w-full rounded-xl border border-slate-300 px-4 py-3 text-base focus:border-brand focus:ring-2 focus:ring-brand/20"
        >
          <option value="">{t("anyDoctor")}</option>
          {doctors.map((d) => (
            <option key={d.id} value={d.id}>
              {d.full_name} — {d.specialization}
            </option>
          ))}
        </select>
      </div>

      {/* Kun tasmasi */}
      <div>
        <span className="mb-1.5 block text-sm font-medium text-slate-700">{t("day")}</span>
        {/*
          APG radiogroup: bitta tab stop (roving tabindex) + strelkalar bilan tanlash.
          Ilgari 15 ta chip ham tab stop edi, strelkalar ishlamasdi, `aria-disabled`
          chiplar bosilaverardi va yorliq kontrasti 1.42:1 edi (AUDIT T-FIX-12).
        */}
        <div
          className="flex snap-x snap-mandatory gap-2 overflow-x-auto overscroll-x-contain pb-2"
          role="radiogroup"
          aria-label={t("day")}
          onKeyDown={(e) => {
            const move = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 } as const;
            if (e.key in move) {
              e.preventDefault();
              moveDay(move[e.key as keyof typeof move]);
            } else if (e.key === "Home" || e.key === "End") {
              e.preventDefault();
              moveDay(e.key === "Home" ? "home" : "end");
            }
          }}
        >
          {days.map((d, i) => {
            const disabled = d.slots.length === 0;
            const { wd, dm } = formatDayChip(d.date, locale);
            return (
              <button
                key={d.date}
                type="button"
                role="radio"
                ref={(el) => {
                  dayRefs.current[i] = el;
                }}
                aria-checked={i === dayIdx}
                disabled={disabled}
                tabIndex={i === dayIdx ? 0 : -1}
                onClick={() => {
                  setDayIdx(i);
                  setSlot(null);
                }}
                className={
                  "flex min-h-11 min-w-[64px] shrink-0 snap-start flex-col items-center justify-center rounded-xl border px-3 py-2 text-xs transition " +
                  (i === dayIdx
                    ? "border-brand bg-brand text-white"
                    : disabled
                      ? "border-line bg-surface-muted text-ink-subtle"
                      : "border-slate-300 text-ink-muted hover:border-brand")
                }
              >
                <span className="font-semibold uppercase">{wd}</span>
                <span>{dm}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Vaqt gridi */}
      <div aria-live="polite">
        <span className="mb-1.5 block text-sm font-medium text-slate-700">{t("time")}</span>
        {loadingSlots ? (
          <p className="flex items-center gap-2 py-4 text-sm text-ink-subtle">
            <Loader2 className="h-4 w-4 animate-spin" /> {t("loadingSlots")}
          </p>
        ) : !activeDay || activeDay.slots.length === 0 ? (
          <p className="py-4 text-sm text-ink-subtle">
            {activeDay?.closed_reason === "clinic_closed" ? t("closedDay") : t("noSlots")}
          </p>
        ) : (
          <div className="space-y-3">
            {(["morning", "afternoon", "evening"] as const).map((part) =>
              buckets && buckets[part].length ? (
                <div key={part}>
                  <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-ink-subtle">
                    {t(part)}
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {buckets[part].map((s) => (
                      <button
                        key={s.start_utc}
                        type="button"
                        aria-pressed={slot?.start_utc === s.start_utc}
                        onClick={() => setSlot(s)}
                        className={
                          "min-h-11 min-w-[64px] rounded-lg border px-3 py-2 text-sm font-medium transition " +
                          (slot?.start_utc === s.start_utc
                            ? "border-brand bg-brand text-white"
                            : "border-slate-300 text-slate-700 hover:border-brand hover:text-brand")
                        }
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null,
            )}
          </div>
        )}
      </div>

      {/* Bemor maydonlari */}
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="bk-name" className="mb-1.5 block text-sm font-medium text-slate-700">
            {t("name")}
          </label>
          <input
            id="bk-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            minLength={2}
            placeholder={t("namePlaceholder")}
            className="w-full rounded-xl border border-slate-300 px-4 py-3 text-base focus:border-brand focus:ring-2 focus:ring-brand/20"
          />
        </div>
        <div>
          <label htmlFor="bk-phone" className="mb-1.5 block text-sm font-medium text-slate-700">
            {t("phone")}
          </label>
          <input
            id="bk-phone"
            type="tel"
            value={phoneVal}
            onChange={(e) => setPhoneVal(e.target.value)}
            required
            className="w-full rounded-xl border border-slate-300 px-4 py-3 text-base focus:border-brand focus:ring-2 focus:ring-brand/20"
          />
        </div>
      </div>

      <div>
        <label htmlFor="bk-comment" className="mb-1.5 block text-sm font-medium text-slate-700">
          {t("comment")}
        </label>
        <textarea
          id="bk-comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          rows={2}
          className="w-full rounded-xl border border-slate-300 px-4 py-3 text-base focus:border-brand focus:ring-2 focus:ring-brand/20"
        />
      </div>

      {/* Honeypot — odam ko'rmaydi */}
      <div aria-hidden="true" className="absolute left-[-9999px] h-0 w-0 overflow-hidden">
        <label>
          Referral
          <input
            tabIndex={-1}
            autoComplete="off"
            value={honeypot}
            onChange={(e) => setHoneypot(e.target.value)}
          />
        </label>
      </div>

      {/* Rozilik */}
      <label className="flex min-h-11 items-start gap-2.5 py-1.5 text-sm text-slate-600">
        <input
          type="checkbox"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
          required
          className="mt-0.5 h-4 w-4 rounded border-slate-300 text-brand focus:ring-brand"
        />
        <span>
          {t("consent")}{" "}
          <a href={`/${locale}/maxfiylik-siyosati`} className="text-brand underline">
            ({t("consentLink")})
          </a>
        </span>
      </label>

      {error && (
        <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={submitting || !slot || !consent}
        className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-brand px-6 py-3.5 text-sm font-semibold text-white shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
      >
        {submitting ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" /> {t("submitting")}
          </>
        ) : (
          <>
            <CalendarCheck className="h-4 w-4" /> {t("submit")}
          </>
        )}
      </button>
    </form>
  );
}

function SuccessCard({
  result,
  locale,
  phone,
}: {
  result: BookingResult;
  locale: string;
  phone: string;
}) {
  const t = useTranslations("booking.success");
  const when = formatWhen(result.starts_at, locale);
  return (
    <div role="status" className="rounded-2xl border border-brand/30 bg-brand-50 p-8 text-center">
      <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-brand/10">
        <Check className="h-7 w-7 text-brand" />
      </div>
      <h3 className="font-display text-2xl font-extrabold text-slate-900">{t("title")}</h3>
      <p className="mt-2 text-slate-700">{when}</p>
      <div className="mt-5 inline-block rounded-xl border-2 border-dashed border-brand/40 px-6 py-3">
        <span className="block text-xs uppercase tracking-wide text-ink-subtle">{t("code")}</span>
        <span className="font-mono text-xl font-bold tracking-widest text-slate-900">
          {result.code}
        </span>
      </div>
      <p className="mt-4 text-sm text-brand">
        {result.notified ? `${t("notified")} ✓` : t("notifyPending")}
      </p>
      <p className="mt-1 text-sm text-slate-500">{t("next")}</p>
      <div className="mt-6">
        <a
          href={`/${locale}/qabul/${result.cancel_token}`}
          className="inline-flex items-center gap-2 rounded-full border border-slate-300 px-5 py-2.5 text-sm font-semibold text-slate-800 hover:border-brand hover:text-brand"
        >
          {t("manage")}
        </a>
        <p className="mt-2 text-xs text-ink-subtle">{t("manageHint")}</p>
      </div>
    </div>
  );
}
