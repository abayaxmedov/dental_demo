"use client";

import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";
import { ChevronLeft, ChevronRight, X } from "lucide-react";
import type { GalleryImage } from "@/lib/api";
import { ImageFrame } from "@/components/ui/ImageFrame";
import { FULLSCREEN, GALLERY_GRID } from "@/lib/image-sizes";

type Labels = { title: string; close: string; prev: string; next: string };

/**
 * Galereya: telefonda ham 2 ustunli grid; bosilganda toʻliq ekranli koʻrish.
 * Koʻrish oynasi — native <dialog> (Escape, fokus tuzogʻi bepul) ichida CSS scroll-snap lenta:
 * telefonda barmoq bilan varaqlanadi, desktopda ‹ › tugmalar va klaviatura strelkalari.
 */
export function GalleryGrid({ images, labels }: { images: GalleryImage[]; labels: Labels }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const strip = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [index, setIndex] = useState(0);

  const show = (i: number) => {
    setIndex(i);
    setOpen(true);
    dialog.current?.showModal();
  };

  // Ochilganda kerakli slaydga darhol (animatsiyasiz) oʻtamiz
  useEffect(() => {
    if (!open) return;
    const el = strip.current;
    if (el) el.scrollLeft = index * el.clientWidth;
    // faqat ochilish paytida
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const go = useCallback((dir: number) => {
    const el = strip.current;
    if (!el) return;
    el.scrollBy({ left: dir * el.clientWidth, behavior: "smooth" });
  }, []);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") go(1);
      if (e.key === "ArrowLeft") go(-1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, go]);

  return (
    <>
      <div className="grid grid-cols-2 gap-2 sm:gap-4 md:grid-cols-3">
        {images.map((g, i) => (
          <figure key={g.id}>
            <button
              type="button"
              onClick={() => show(i)}
              className="block w-full rounded-2xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
              aria-label={g.alt || g.caption || labels.title}
            >
              <ImageFrame
                image={g.image}
                alt={g.alt || g.caption || labels.title}
                ratio="4/3"
                sizes={GALLERY_GRID}
                rounded="rounded-xl sm:rounded-2xl"
              />
            </button>
            {g.caption ? (
              <figcaption className="mt-1.5 line-clamp-1 text-xs text-ink-subtle">{g.caption}</figcaption>
            ) : null}
          </figure>
        ))}
      </div>

      <dialog
        ref={dialog}
        // Kechikkan "close" hodisasi qayta ochilgan oynani boʻshatmasin — haqiqiy holatga qaraymiz
        onClose={() => {
          if (!dialog.current?.open) setOpen(false);
        }}
        className="m-0 h-dvh max-h-none w-full max-w-none bg-ink p-0 text-white backdrop:bg-ink"
        aria-label={labels.title}
      >
        {open ? (
          <div className="relative flex h-full flex-col">
            <div className="flex items-center justify-between px-4 py-2">
              <span className="text-sm tabular-nums text-white/80">
                {index + 1} / {images.length}
              </span>
              <button
                type="button"
                onClick={() => dialog.current?.close()}
                className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-white/10 hover:bg-white/20"
                aria-label={labels.close}
              >
                <X className="h-6 w-6" aria-hidden />
              </button>
            </div>

            <div
              ref={strip}
              onScroll={(e) => {
                const el = e.currentTarget;
                setIndex(Math.round(el.scrollLeft / el.clientWidth));
              }}
              className="flex min-h-0 flex-1 snap-x snap-mandatory overflow-x-auto overscroll-contain [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
            >
              {images.map((g, i) => (
                <figure key={g.id} className="flex w-full shrink-0 snap-center flex-col">
                  <div className="relative min-h-0 flex-1">
                    {g.image?.src && Math.abs(i - index) <= 1 ? (
                      <Image
                        src={g.image.src}
                        alt={g.alt || g.caption || labels.title}
                        fill
                        sizes={FULLSCREEN}
                        className="object-contain"
                      />
                    ) : null}
                  </div>
                  {g.caption ? (
                    <figcaption className="px-4 py-3 text-center text-sm text-white/80">{g.caption}</figcaption>
                  ) : null}
                </figure>
              ))}
            </div>

            <button
              type="button"
              onClick={() => go(-1)}
              disabled={index === 0}
              className="absolute left-3 top-1/2 hidden h-12 w-12 -translate-y-1/2 items-center justify-center rounded-full bg-white/10 hover:bg-white/20 disabled:opacity-30 md:inline-flex"
              aria-label={labels.prev}
            >
              <ChevronLeft className="h-7 w-7" aria-hidden />
            </button>
            <button
              type="button"
              onClick={() => go(1)}
              disabled={index === images.length - 1}
              className="absolute right-3 top-1/2 hidden h-12 w-12 -translate-y-1/2 items-center justify-center rounded-full bg-white/10 hover:bg-white/20 disabled:opacity-30 md:inline-flex"
              aria-label={labels.next}
            >
              <ChevronRight className="h-7 w-7" aria-hidden />
            </button>
          </div>
        ) : null}
      </dialog>
    </>
  );
}
