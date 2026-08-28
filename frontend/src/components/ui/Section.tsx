import type { ReactNode } from "react";

const WIDTH: Record<string, string> = {
  "6xl": "max-w-6xl",
  "4xl": "max-w-4xl",
  "3xl": "max-w-3xl",
  "2xl": "max-w-2xl",
};

/** Bir xil vertikal ritm (py-20/28), tone almashinuvi va konteyner. */
export function Section({
  id,
  tone = "surface",
  width = "6xl",
  className = "",
  children,
}: {
  id?: string;
  tone?: "surface" | "muted";
  width?: keyof typeof WIDTH;
  className?: string;
  children: ReactNode;
}) {
  const bg = tone === "muted" ? "bg-surface-muted" : "bg-surface";
  return (
    <section
      id={id}
      className={`scroll-mt-20 border-b border-line ${bg} ${className}`}
    >
      <div className={`mx-auto ${WIDTH[width]} px-4 py-16 sm:px-6 sm:py-20 lg:px-8 lg:py-24`}>{children}</div>
    </section>
  );
}

export function SectionHeading({
  eyebrow,
  title,
  lead,
  action,
  as = "h2",
}: {
  eyebrow?: string;
  title: string;
  lead?: string;
  action?: ReactNode;
  /** Sahifaning yuqori sarlavhasi `as="h1"` boʻlishi shart (a11y: har sahifa 1 ta h1). */
  as?: "h1" | "h2";
}) {
  const Heading = as;
  return (
    <div className="mb-10 flex flex-col gap-4 sm:mb-12 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow ? (
          <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-brand">
            {eyebrow}
          </p>
        ) : null}
        <Heading className="font-display text-3xl font-extrabold leading-tight tracking-[-0.02em] text-ink sm:text-4xl lg:text-[2.75rem]">
          {title}
        </Heading>
        {lead ? <p className="mt-3 max-w-2xl text-ink-muted">{lead}</p> : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}
