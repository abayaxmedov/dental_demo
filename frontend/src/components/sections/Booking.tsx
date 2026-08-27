import { getTranslations } from "next-intl/server";
import { BookingForm } from "@/components/booking/BookingForm";
import type { ClinicSettings, Doctor, Service } from "@/lib/api";

export async function Booking({
  services,
  doctors,
  settings,
}: {
  services: Service[];
  doctors: Doctor[];
  settings: ClinicSettings | null;
}) {
  const t = await getTranslations("booking");
  if (!services.length) return null;

  return (
    <section id="qabul" className="border-b border-slate-100 bg-white scroll-mt-20">
      <div className="mx-auto max-w-2xl px-4 py-16 sm:py-20">
        <h2 className="font-display text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
          {t("title")}
        </h2>
        <p className="mt-2 text-slate-500">{t("subtitle")}</p>
        <div className="mt-8">
          <BookingForm
            services={services}
            doctors={doctors.filter((d) => d.is_bookable)}
            phone={settings?.phone_primary ?? "+998712004040"}
            telegram={settings?.telegram_username ?? null}
          />
        </div>
      </div>
    </section>
  );
}
