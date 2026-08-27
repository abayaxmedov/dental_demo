import type { ComponentProps, ReactNode } from "react";
import { Link } from "@/i18n/navigation";

const VARIANTS = {
  primary: "bg-brand text-white hover:opacity-90 shadow-sm",
  secondary: "border border-line text-ink hover:border-brand hover:text-brand",
  ghost: "text-brand hover:bg-brand-50",
} as const;
const SIZES = { md: "px-5 py-2.5 text-sm", lg: "px-6 py-3.5 text-base" } as const;

type Common = {
  variant?: keyof typeof VARIANTS;
  size?: keyof typeof SIZES;
  className?: string;
  children: ReactNode;
};

function cls(v: keyof typeof VARIANTS, s: keyof typeof SIZES, extra = "") {
  return `inline-flex min-h-11 items-center justify-center gap-2 rounded-full font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-40 ${VARIANTS[v]} ${SIZES[s]} ${extra}`;
}

/** Ichki havola tugmasi (tiplangan pathname). */
export function ButtonLink({
  href,
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...rest
}: Common & ComponentProps<typeof Link>) {
  return (
    <Link href={href} className={cls(variant, size, className)} {...rest}>
      {children}
    </Link>
  );
}

/** Oddiy <a> (tel:, t.me, tashqi). */
export function AnchorButton({
  href,
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...rest
}: Common & ComponentProps<"a">) {
  return (
    <a href={href} className={cls(variant, size, className)} {...rest}>
      {children}
    </a>
  );
}

/** Haqiqiy <button>. */
export function Button({
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...rest
}: Common & ComponentProps<"button">) {
  return (
    <button className={cls(variant, size, className)} {...rest}>
      {children}
    </button>
  );
}
