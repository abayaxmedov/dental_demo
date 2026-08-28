/** Oddiy matn bloki — \n\n boʻyicha paragraflarga boʻladi (markdown/HTML yoʻq, xavfsiz). */
export function Prose({ text, className = "" }: { text: string; className?: string }) {
  const paras = (text || "").split(/\n\n+/).filter(Boolean);
  return (
    <div className={`space-y-4 break-words text-ink-muted leading-relaxed ${className}`}>
      {paras.map((p, i) => (
        <p key={i}>{p}</p>
      ))}
    </div>
  );
}
