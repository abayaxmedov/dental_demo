import Image from "next/image";
import type { ImageLike } from "@/lib/api";
import { CARD_3UP } from "@/lib/image-sizes";

type Props = {
  image: ImageLike;
  alt: string;
  sizes?: string;
  ratio?: string; // "4/3", "16/9", "1/1"
  priority?: boolean;
  rounded?: string;
  className?: string;
};

/** Rasm ramkasi — src boʻlsa next/image, boʻlmasa brend gradient (fallback). CLS=0. */
export function ImageFrame({
  image,
  alt,
  sizes = CARD_3UP,
  ratio = "4/3",
  priority = false,
  rounded = "rounded-2xl",
  className = "",
}: Props) {
  const src = image?.src;
  return (
    <div
      className={`relative overflow-hidden bg-gradient-to-br from-brand-100 to-brand-50 ${rounded} ${className}`}
      style={{ aspectRatio: ratio }}
    >
      {src ? (
        <Image
          src={src}
          alt={alt}
          fill
          sizes={sizes}
          priority={priority}
          className="object-cover"
        />
      ) : (
        <span
          className="absolute inset-0 grid place-items-center text-brand-400"
          aria-hidden="true"
        >
          <svg width="40%" height="40%" viewBox="0 0 24 24" fill="currentColor" opacity="0.5">
            <path d="M12 2C8 2 6 4 6 8c0 3 1 5 1.5 8 .3 2 .8 4 2 4s1.2-3 2.5-3 1.3 3 2.5 3 1.7-2 2-4c.5-3 1.5-5 1.5-8 0-4-2-6-6-6z" />
          </svg>
        </span>
      )}
    </div>
  );
}
