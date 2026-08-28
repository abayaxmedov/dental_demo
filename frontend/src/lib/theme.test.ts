import { describe, expect, it } from "vitest";
import { isHexColor } from "@/lib/theme";

describe("isHexColor", () => {
  it("haqiqiy hex shakllarini qabul qiladi", () => {
    for (const v of ["#0E7C86", "#0e7c86", "#fff", "#FFFA", "#0E7C86FF"]) {
      expect(isHexColor(v), v).toBe(true);
    }
  });
  it("CSS injeksiyasi va yaroqsiz ranglarni rad etadi", () => {
    // Aynan shu qiymatlar `<html style>` ga tushib CTA'larni koʻrinmas qilardi (T-FIX-05).
    for (const v of ["a;zoom:9", "red;x:1", "teal", "0E7C86", "#0E7C8", "#GGGGGG", "", "#"]) {
      expect(isHexColor(v), v).toBe(false);
    }
  });
  it("matn boʻlmagan qiymatni rad etadi", () => {
    for (const v of [null, undefined, 123, {}, []]) expect(isHexColor(v)).toBe(false);
  });
});
