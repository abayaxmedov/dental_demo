#!/usr/bin/env node
/**
 * i18n xabar kalitlari parity tekshiruvi (Faza 5 — tech debt D).
 *
 * next-intl uch til fayli (`messages/{uz,ru,en}.json`) bir XIL kalit daraxtiga ega boʻlishi
 * shart — aks holda `t('...')` ba'zi tilda runtime'da yiqiladi yoki xom kalitni koʻrsatadi.
 * Bu skript `scripts/lint-colors.sh` naqshiga ergashadi (dep yoʻq, `npm run test` gate qiladi).
 *
 * Chiqish kodi:
 *   0 — barcha til bir xil leaf kalitlarga ega (boʻsh qiymatlar faqat ogohlantiradi)
 *   1 — kamida bitta tilda kalit yetishmaydi / ortiqcha (HARD FAIL, merge blocker)
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const MSG_DIR = join(HERE, "..", "messages");
const LOCALES = ["uz", "ru", "en"];
const REFERENCE = "uz"; // uz — asosiy til (ADR-002 defaultLocale)

/** Nested obyektdan "a.b.c" leaf yoʻllarini yigʻadi. */
function leafPaths(obj, prefix = "") {
  const out = [];
  for (const [k, v] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) out.push(...leafPaths(v, path));
    else out.push(path);
  }
  return out;
}

/** Leaf yoʻl → qiymat xaritasi (boʻsh qiymat tekshiruvi uchun). */
function leafMap(obj, prefix = "") {
  const out = {};
  for (const [k, v] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) Object.assign(out, leafMap(v, path));
    else out[path] = v;
  }
  return out;
}

const maps = {};
for (const loc of LOCALES) {
  try {
    maps[loc] = leafMap(JSON.parse(readFileSync(join(MSG_DIR, `${loc}.json`), "utf8")));
  } catch (err) {
    console.error(`✗ messages/${loc}.json oʻqib boʻlmadi: ${err.message}`);
    process.exit(1);
  }
}

const refKeys = new Set(leafPaths(JSON.parse(readFileSync(join(MSG_DIR, `${REFERENCE}.json`), "utf8"))));
let hardFail = false;
const warnings = [];

for (const loc of LOCALES) {
  const keys = new Set(Object.keys(maps[loc]));
  if (loc !== REFERENCE) {
    const missing = [...refKeys].filter((k) => !keys.has(k));
    const extra = [...keys].filter((k) => !refKeys.has(k));
    if (missing.length) {
      hardFail = true;
      console.error(`✗ ${loc}: ${REFERENCE}'da bor, lekin yetishmaydigan ${missing.length} kalit:`);
      for (const k of missing) console.error(`    - ${k}`);
    }
    if (extra.length) {
      hardFail = true;
      console.error(`✗ ${loc}: ${REFERENCE}'da yoʻq ortiqcha ${extra.length} kalit:`);
      for (const k of extra) console.error(`    + ${k}`);
    }
  }
  // Boʻsh qiymat — tarjima qilinmagan (faqat ogohlantirish)
  for (const [k, v] of Object.entries(maps[loc])) {
    if (typeof v === "string" && v.trim() === "") warnings.push(`${loc}: boʻsh qiymat → ${k}`);
  }
}

if (warnings.length) {
  console.warn(`⚠ ${warnings.length} boʻsh qiymat (tarjima kerak):`);
  for (const w of warnings) console.warn(`    ${w}`);
}

if (hardFail) {
  console.error("\n✗ Xabar kalitlari parity BUZILDI — til fayllari sinxron emas.");
  process.exit(1);
}

console.log(`✓ Xabar kalitlari parity OK — ${refKeys.size} kalit × ${LOCALES.length} til sinxron.`);
