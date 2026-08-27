import type { ComponentProps, ElementType, ReactNode } from "react";

/** Kartochka: 1px chegara, hover'da teal + koʻtarilish. */
export function Card({
  as,
  interactive = false,
  className = "",
  children,
  ...rest
}: {
  as?: ElementType;
  interactive?: boolean;
  className?: string;
  children: ReactNode;
} & ComponentProps<"div">) {
  const Tag = as ?? "div";
  const hover = interactive
    ? "transition hover:border-brand hover:shadow-lg hover:-translate-y-0.5"
    : "";
  return (
    <Tag
      className={`rounded-2xl border border-line bg-surface ${hover} ${className}`}
      {...rest}
    >
      {children}
    </Tag>
  );
}
