import { getTranslations } from "next-intl/server";
import { ButtonLink } from "@/components/ui/Button";

export default async function NotFound() {
  const t = await getTranslations("nav");
  return (
    <div className="mx-auto flex max-w-xl flex-col items-center px-4 py-24 text-center">
      {/* Dekorativ raqam — matn sifatida oʻqilmaydi (h1 haqiqiy xabarni beradi).
          `aria-hidden` + kuchaytirilgan rang: 1.47:1 kontrast axe da yiqilardi (T-FIX-18). */}
      <p className="font-display text-7xl font-extrabold text-brand-400" aria-hidden="true">
        404
      </p>
      <h1 className="mt-4 font-display text-2xl font-bold text-ink">Sahifa topilmadi</h1>
      <p className="mt-2 text-ink-muted">
        Siz qidirgan sahifa mavjud emas yoki koʻchirilgan.
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <ButtonLink href="/">{t("home")}</ButtonLink>
        <ButtonLink href="/xizmatlar" variant="secondary">
          {t("services")}
        </ButtonLink>
        <ButtonLink href="/aloqa" variant="secondary">
          {t("contact")}
        </ButtonLink>
      </div>
    </div>
  );
}
