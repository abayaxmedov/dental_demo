#!/usr/bin/env node
/**
 * Statik responsive lint (T-RESP-09). `check-messages.mjs` naqshi: dep yoʻq, server yoʻq,
 * tarmoq yoʻq → oʻtkazib yuborish uchun SABAB YOʻQ (T-FIX-13 saboqi: soxta gate boʻlmasin).
 * `npm run test` (va `make fe-test`) shu skriptni chaqiradi.
 *
 * FAQAT string-manba'dan ISHONCHLI hal qilinadigan qoidalar bu yerda. Layout/merosga
 * bogʻliq narsalar (tap target oʻlchami, computed font-size) — brauzer gate'ida (T-RESP-10).
 *
 * Chiqish kodi: 0 — toza · 1 — kamida bitta buzilish (HARD FAIL).
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, relative } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "..", "src");
const IMAGE_SIZES_FILE = join("lib", "image-sizes.ts"); // R3 uchun yagona ruxsat etilgan joy

/** src/ ostidagi barcha .ts/.tsx fayllar. */
function walk(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) out.push(...walk(p));
    else if (/\.(tsx?|jsx?)$/.test(name)) out.push(p);
  }
  return out;
}

const files = walk(SRC);
const problems = [];
const add = (file, line, msg) => problems.push({ rel: relative(SRC, file), line, msg });

for (const file of files) {
  const rel = relative(SRC, file);
  const text = readFileSync(file, "utf8");
  const lines = text.split("\n");

  lines.forEach((line, i) => {
    const n = i + 1;

    // R1 — har `<table` oldingi 3 ta boʻsh-boʻlmagan qatorda `overflow-x-auto` boʻlishi shart.
    // `overflow-hidden` jimgina kesadi (narx jadvali bugi, T-RESP-01).
    if (/<table[\s>]/.test(line)) {
      const window = [];
      for (let j = i; j >= 0 && window.length < 4; j--) {
        if (lines[j].trim()) window.push(lines[j]);
      }
      if (!window.some((l) => /overflow-x-auto|overflow-x-scroll/.test(l))) {
        add(file, n, "<table> ni `overflow-x-auto` oʻrashsiz — 320px'da jimgina kesiladi (R1)");
      }
    }

    // R2 — forma control'lari `text-base` boʻlishi shart (iOS 16px'dan kichikda zoom qiladi).
    // Faqat className string ichida `<input/select/textarea` boʻlgan JSX qatorlarini emas —
    // control JSX ochilishini qidiramiz; checkbox/radio/hidden va honeypot (tabIndex={-1}) istisno.
    if (/<(input|select|textarea)\b/.test(line)) {
      const isExempt =
        /type=["'](checkbox|radio|hidden)["']/.test(line) || /tabIndex=\{-1\}/.test(line);
      if (!isExempt) {
        // className shu qatorda yoki keyingi 2 qatorda boʻlishi mumkin
        const block = lines.slice(i, i + 3).join(" ");
        if (/text-sm|text-xs/.test(block) && !/text-base/.test(block)) {
          add(file, n, "forma control'i `text-sm/xs` — iOS fokusda zoom qiladi, `text-base` kerak (R2)");
        }
      }
    }

    // R3 — `sizes="…"` literal FAQAT lib/image-sizes.ts da (grid oʻzgarsa drift qilmasin).
    if (/\bsizes=["']/.test(line) && !rel.endsWith(IMAGE_SIZES_FILE) && !rel.split(/[\\/]/).join("/").endsWith(IMAGE_SIZES_FILE.split(/[\\/]/).join("/"))) {
      add(file, n, "`sizes=\"…\"` literal — presetni `lib/image-sizes.ts` dan import qiling (R3)");
    }

    // R4 — `100vh`/`min-h-screen`/`h-screen`/`w-screen` taqiqlanadi (`min-h-dvh` qulflanadi).
    const banned = line.match(/\b(100vh|min-h-screen|h-screen|w-screen)\b/);
    if (banned) {
      add(file, n, `\`${banned[1]}\` ishlatilgan — mobil brauzer xromi uchun \`dvh\` ishlating (R4)`);
    }

    // R5 — `lg:grid-cols-`/`lg:columns-` boʻlsa `md:`/`sm:` bosqichi ham boʻlsin (planshet gate'i).
    for (const [pat, step] of [
      [/lg:grid-cols-/, /(md|sm):grid-cols-/],
      [/lg:columns-/, /(md|sm):columns-/],
    ]) {
      if (pat.test(line) && !step.test(line)) {
        add(file, n, "`lg:` grid/columns bor, lekin `md:`/`sm:` bosqichi yoʻq — planshet telefon layoutini oladi (R5)");
      }
    }
  });

  // R6 — `env(safe-area-inset` ishlatilsa layout `viewportFit:"cover"` boʻlishi shart (aks holda 0 = oʻlik kod).
  if (/env\(safe-area-inset/.test(text)) {
    const layout = readFileSync(join(SRC, "app", "[locale]", "layout.tsx"), "utf8");
    if (!/viewportFit:\s*["']cover["']/.test(layout)) {
      add(file, 0, "`env(safe-area-inset…)` ishlatilgan, lekin layout `viewportFit:\"cover\"` emas → qiymat 0 (oʻlik kod) (R6)");
    }
  }
}

if (problems.length) {
  console.error("✗ Responsive lint — buzilishlar:");
  for (const p of problems) console.error(`    ${p.rel}:${p.line}  ${p.msg}`);
  console.error(`\n✗ ${problems.length} ta responsive buzilish (HARD FAIL).`);
  process.exit(1);
}

console.log(`✓ Responsive lint toza — ${files.length} fayl (R1–R6).`);
