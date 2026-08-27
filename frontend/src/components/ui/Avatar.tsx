import Image from "next/image";
import type { ImageLike } from "@/lib/api";

/** Shifokor/sharh avatari — rasm yoki initsial fallback (brend doira). */
export function Avatar({
  image,
  name,
  size = 64,
  className = "",
}: {
  image?: ImageLike;
  name: string;
  size?: number;
  className?: string;
}) {
  const initials = name
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? "")
    .join("");
  const alt = image?.alt || name;
  return (
    <span
      className={`relative inline-block shrink-0 overflow-hidden rounded-full ${className}`}
      style={{ width: size, height: size }}
    >
      {image?.src ? (
        <Image src={image.src} alt={alt} fill sizes={`${size}px`} className="object-cover" />
      ) : (
        <span
          className="grid h-full w-full place-items-center bg-brand-100 font-display font-bold text-brand-700"
          style={{ fontSize: size * 0.36 }}
          aria-hidden="true"
        >
          {initials}
        </span>
      )}
    </span>
  );
}
