import { describe, expect, it } from "vitest";
import {
  formatSum,
  formatPhone,
  telHref,
  formatDayChip,
  formatWhen,
} from "@/lib/format";

describe("formatSum", () => {
  it("guruhlaydi (minglik ajratgich) — ICU ajratgichidan qatʼi nazar", () => {
    // Ajratgich belgisi ICU versiyasiga bogʻliq (NBSP/NNBSP) — raqamlarni tekshiramiz.
    expect(formatSum(4500000).replace(/\D/g, "")).toBe("4500000");
    expect(formatSum(4500000)).toMatch(/4\D500\D000/);
  });
  it("string kirishni qabul qiladi", () => {
    expect(formatSum("350000").replace(/\D/g, "")).toBe("350000");
  });
  it("nolni bosib chiqaradi", () => {
    expect(formatSum(0)).toBe("0");
  });
  it("kasrlarni tashlaydi (maximumFractionDigits: 0)", () => {
    expect(formatSum(1000.9).replace(/\D/g, "")).toBe("1001");
  });
  it("son boʻlmagan kirishni oʻzgartirmasdan qaytaradi", () => {
    expect(formatSum("abc")).toBe("abc");
  });
});

describe("formatPhone", () => {
  it("+998 raqamini bloklab formatlaydi", () => {
    expect(formatPhone("+998712004040")).toBe("+998 71 200 40 40");
  });
  it("mos kelmagan qatorni oʻzgartirmaydi", () => {
    expect(formatPhone("12345")).toBe("12345");
  });
});

describe("telHref", () => {
  it("boʻshliq va belgilarni tozalaydi, + saqlaydi", () => {
    expect(telHref("+998 71 200 40 40")).toBe("tel:+998712004040");
    expect(telHref("+998712004040")).toBe("tel:+998712004040");
  });
});

describe("formatDayChip", () => {
  it("uz — qisqa hafta kuni + kun/oy (2026-08-29 = shanba)", () => {
    expect(formatDayChip("2026-08-29", "uz")).toEqual({ wd: "sha", dm: "29 avg" });
  });
  it("ru — Intl orqali, kun raqamini oʻz ichiga oladi", () => {
    const chip = formatDayChip("2026-08-29", "ru");
    expect(chip.wd).not.toBe("");
    expect(chip.dm).toContain("29");
  });
  it("en — kun raqami va oyni oʻz ichiga oladi", () => {
    const chip = formatDayChip("2026-08-29", "en");
    expect(chip.dm).toContain("29");
    expect(chip.dm).toMatch(/Aug/i);
  });
});

describe("formatWhen", () => {
  it("uz — Asia/Tashkent (UTC+5) da qoʻlda formatlaydi", () => {
    // 05:00Z = 10:00 Tashkent; 2026-08-29 = shanba.
    expect(formatWhen("2026-08-29T05:00:00Z", "uz")).toBe("29-avgust, shanba · 10:00");
  });
  it("uz — UTC yarim tunni keyingi kunga oʻtkazadi (TZ toʻgʻri)", () => {
    // 2026-08-28T20:00Z = 2026-08-29T01:00 Tashkent → kun 29 boʻlishi shart.
    expect(formatWhen("2026-08-28T20:00:00Z", "uz")).toMatch(/^29-avgust/);
  });
  it("en — Asia/Tashkent vaqt zonasida render qiladi", () => {
    const s = formatWhen("2026-08-29T05:00:00Z", "en");
    expect(s).toMatch(/10:00/);
    expect(s).toMatch(/Saturday/i);
  });
});
