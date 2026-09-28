/**
 * Kun chipini FAQAT oʻz gorizontal tasmasi ichida markazga suradi.
 *
 * `scrollIntoView({ inline: "center", block: "nearest" })` ishlatilmaydi: element ekranda
 * boʻlmasa `block: "nearest"` ham BUTUN SAHIFANI vertikal suradi. Birinchi kun band/yopiq
 * boʻlganda (kechqurun, yakshanba) forma birinchi boʻsh kunni tanlardi va sahifa ochilishi bilan
 * pastdagi "Qabulga yozilish" bo'limiga sakrab ketardi.
 */
export function centerChip(chip: HTMLElement | null | undefined) {
  const strip = chip?.parentElement;
  if (!chip || !strip) return;
  const offset = chip.getBoundingClientRect().left - strip.getBoundingClientRect().left;
  strip.scrollTo({ left: strip.scrollLeft + offset - (strip.clientWidth - chip.offsetWidth) / 2 });
}
