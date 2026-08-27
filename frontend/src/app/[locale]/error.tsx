"use client";

export default function Error({ retry }: { error: Error; retry: () => void }) {
  return (
    <div className="mx-auto flex max-w-xl flex-col items-center px-4 py-24 text-center">
      <h1 className="font-display text-2xl font-bold text-ink">Texnik nosozlik</h1>
      <p className="mt-2 text-ink-muted">
        Kutilmagan xatolik yuz berdi. Iltimos, qayta urinib koʻring.
      </p>
      <button
        onClick={retry}
        className="mt-8 inline-flex min-h-11 items-center rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white hover:opacity-90"
      >
        Qayta urinish
      </button>
    </div>
  );
}
