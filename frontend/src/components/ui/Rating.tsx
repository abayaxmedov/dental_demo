import { Star } from "lucide-react";

/** Yulduz reytingi (accent to'ldirish — matn emas, a11y-xavfsiz). */
export function Rating({
  value,
  max = 5,
  showValue = false,
}: {
  value: number;
  max?: number;
  showValue?: boolean;
}) {
  return (
    <span
      className="inline-flex items-center gap-0.5"
      role="img"
      aria-label={`${value} / ${max}`}
    >
      {Array.from({ length: max }, (_, i) => (
        <Star
          key={i}
          className={
            i < Math.round(value)
              ? "h-4 w-4 fill-accent text-accent"
              : "h-4 w-4 text-slate-300"
          }
          aria-hidden="true"
        />
      ))}
      {showValue ? <span className="ml-1 text-sm font-semibold text-ink">{value}</span> : null}
    </span>
  );
}
