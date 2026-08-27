import type { ReactNode } from "react";

const TONES = {
  promo: "bg-accent-100 text-accent-700",
  brand: "bg-brand-50 text-brand-700",
  neutral: "bg-slate-100 text-slate-600",
} as const;

export function Badge({
  tone = "neutral",
  children,
}: {
  tone?: keyof typeof TONES;
  children: ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${TONES[tone]}`}
    >
      {children}
    </span>
  );
}
