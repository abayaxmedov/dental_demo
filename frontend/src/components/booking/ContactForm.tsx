"use client";

import { useEffect, useRef, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Loader2 } from "lucide-react";
import { createLead, fetchFormToken } from "@/lib/api";

export function ContactForm() {
  const t = useTranslations("pages.contact");
  const tb = useTranslations("booking");
  const locale = useLocale();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("+998 ");
  const [message, setMessage] = useState("");
  const [consent, setConsent] = useState(false);
  const [honey, setHoney] = useState("");
  const [state, setState] = useState<"idle" | "sending" | "done">("idle");
  const token = useRef("");

  useEffect(() => {
    fetchFormToken().then((tk) => (token.current = tk));
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (state === "sending") return;
    setState("sending");
    const r = await createLead({
      kind: "contact", name: name.trim(), phone, message: message.trim(),
      locale, consent, form_token: token.current, referral_note_2: honey,
      source_page: "/aloqa",
    });
    setState(r.ok ? "done" : "idle");
  }

  if (state === "done") {
    return <p className="rounded-2xl border border-brand/30 bg-brand-50 px-5 py-6 text-center text-brand-700">{t("sent")}</p>;
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div>
        <label htmlFor="c-name" className="mb-1.5 block text-sm font-medium text-ink">{t("name")}</label>
        <input id="c-name" value={name} onChange={(e) => setName(e.target.value)} required minLength={2}
          className="w-full rounded-xl border border-line px-4 py-3 text-base focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20" />
      </div>
      <div>
        <label htmlFor="c-phone" className="mb-1.5 block text-sm font-medium text-ink">{t("phone")}</label>
        <input id="c-phone" type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} required
          className="w-full rounded-xl border border-line px-4 py-3 text-base focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20" />
      </div>
      <div>
        <label htmlFor="c-msg" className="mb-1.5 block text-sm font-medium text-ink">{t("message")}</label>
        <textarea id="c-msg" value={message} onChange={(e) => setMessage(e.target.value)} rows={3}
          className="w-full rounded-xl border border-line px-4 py-3 text-base focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20" />
      </div>
      <div aria-hidden className="absolute left-[-9999px] h-0 w-0 overflow-hidden">
        <label>Referral<input tabIndex={-1} autoComplete="off" value={honey} onChange={(e) => setHoney(e.target.value)} /></label>
      </div>
      <label className="flex items-start gap-2.5 text-sm text-ink-muted">
        <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} required className="mt-0.5 h-4 w-4 rounded border-line text-brand" />
        <span>{tb("consent")}</span>
      </label>
      <button type="submit" disabled={state === "sending" || !consent}
        className="inline-flex min-h-11 items-center justify-center gap-2 rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-40">
        {state === "sending" ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
        {t("send")}
      </button>
    </form>
  );
}
