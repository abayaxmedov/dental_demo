/**
 * Telefon karuseli (<640px) → sm+ da oddiy grid. JS'siz: CSS scroll-snap.
 * Konteyner Section paddingidan chiqib (-mx-4) ekran chetigacha suriladi; keyingi karta
 * ~18% koʻrinib turadi — "surish mumkin" degan tabiiy ishora.
 * Grid ustunlari chaqiruvchida (`sm:grid-cols-2 lg:grid-cols-3`).
 */
export const CAROUSEL =
  "-mx-4 flex snap-x snap-mandatory scroll-px-4 gap-4 overflow-x-auto overscroll-x-contain px-4 pb-3 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden sm:mx-0 sm:grid sm:gap-5 sm:overflow-visible sm:px-0 sm:pb-0";

/** Karusel elementi: telefonda 82% kenglik, sm+ da grid katagi. */
export const CAROUSEL_ITEM = "w-[82%] shrink-0 snap-start sm:w-auto";
