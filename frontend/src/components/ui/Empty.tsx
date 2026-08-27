import type { ReactNode } from "react";

/** Boʻsh holat (backend oʻchsa yoki qator yoʻq boʻlsa). */
export function Empty({
  title,
  hint,
  action,
}: {
  title: string;
  hint?: string;
  action?: ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-line bg-surface-muted px-6 py-16 text-center">
      <p className="font-display text-lg font-bold text-ink">{title}</p>
      {hint ? <p className="mt-2 text-sm text-ink-subtle">{hint}</p> : null}
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}
