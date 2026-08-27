import type { Metadata } from "next";
import { setRequestLocale } from "next-intl/server";
import { ManageAppointment } from "@/components/booking/ManageAppointment";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
  referrer: "no-referrer",
};

export default async function ManagePage({
  params,
}: {
  params: Promise<{ locale: string; token: string }>;
}) {
  const { locale, token } = await params;
  setRequestLocale(locale);
  return (
    <div className="min-h-dvh bg-surface-muted">
      <div className="mx-auto max-w-xl px-4 py-16">
        <ManageAppointment token={token} />
      </div>
    </div>
  );
}
