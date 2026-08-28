import { getTranslations } from "next-intl/server";
import { Phone, CalendarCheck } from "lucide-react";
import type { ClinicSettings } from "@/lib/api";
import { telHref } from "@/lib/format";
import Image from "next/image";
import { SceneGuard } from "@/components/three/SceneGuard";

export async function Hero({ settings }: { settings: ClinicSettings | null }) {
  const t = await getTranslations("hero");
  const phone = settings?.phone_primary ?? "+998712004040";

  return (
    <section className="relative overflow-hidden border-b border-line bg-gradient-to-b from-brand-50 to-surface">
      <div className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-16 sm:py-20 md:grid-cols-2 lg:py-24">
        <div>
          <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-brand">
            {t("eyebrow")}
          </p>
          <h1 className="font-display max-w-xl text-4xl font-extrabold leading-[1.08] tracking-[-0.02em] text-ink sm:text-5xl md:text-4xl lg:text-6xl">
            {t("title")}
          </h1>
          <p className="mt-5 max-w-lg text-lg leading-relaxed text-ink-muted">
            {settings?.tagline || t("subtitle")}
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a
              href="#qabul"
              className="inline-flex min-h-11 items-center gap-2 rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:opacity-90"
            >
              <CalendarCheck className="h-4 w-4" aria-hidden />
              {t("ctaBook")}
            </a>
            <a
              href={telHref(phone)}
              className="inline-flex min-h-11 items-center gap-2 rounded-full border border-line px-6 py-3 text-sm font-semibold text-ink transition hover:border-brand hover:text-brand"
            >
              <Phone className="h-4 w-4" aria-hidden />
              {t("ctaCall")}
            </a>
          </div>
        </div>
        <div className="md:pl-6">
          <div className="hero-stage relative aspect-[4/3] overflow-hidden rounded-2xl bg-gradient-to-br from-brand-100 to-brand-50 shadow-xl">
            {/* Poster — mobil/zaif qurilmada LCP elementi. Qodir desktopda `globals.css`
                uni YASHIRADI (3D toʻgʻridan-toʻgʻri chiqsin), SceneGuard yiqilsa qaytariladi. */}
            {settings?.hero_image?.src ? (
              <Image
                src={settings.hero_image.src}
                alt={settings?.name ?? "Oq Marvarid Dental"}
                fill
                priority
                sizes="(min-width:1024px) 40rem, 100vw"
                className="hero-poster object-cover"
              />
            ) : null}
            {/* 3D tish — faqat qodir desktop'da, darhol mount boʻladi (ADR-011) */}
            <SceneGuard />
          </div>
        </div>
      </div>
    </section>
  );
}
