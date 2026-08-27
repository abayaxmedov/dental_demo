import type { ComponentProps, ReactNode } from "react";

/** Kartochka: 1px chegara, hover'da teal + koʻtarilish. */
export function Card({
  interactive = false,
  className = "",
  children,
  ...rest
}: {
  interactive?: boolean;
  className?: string;
  children: ReactNode;
} & ComponentProps<"div">) {
  const hover = interactive
    ? "transition hover:border-brand hover:shadow-lg hover:-translate-y-0.5"
    : "";
  return (
    <div className={`rounded-2xl border border-line bg-surface ${hover} ${className}`} {...rest}>
      {children}
    </div>
  );
}
