#!/usr/bin/env node
/**
 * Brauzer viewport gate (T-RESP-10). Tizim Chrome'ini `puppeteer-core` bilan boshqaradi
 * (Chromium yuklamaydi). Layout/merosga bogʻliq — statik lint hal qila olmaydigan —
 * narsalarni HAQIQIY qurilma oʻlchamlarida oʻlchaydi.
 *
 * ┌─ SOXTA-GATE BOʻLMASLIK SHARTNOMASI (T-FIX-13 saboqi — skript sarlavhasida qoladi) ─┐
 * │ 1. `|| true` yoʻq, top-level try/catch yoʻq.                                       │
 * │ 2. Chrome topilmasa       → exit 1 ("CHROME_PATH oʻrnating"). SKIP EMAS.           │
 * │ 3. Server yetib boʻlmasa  → exit 1 ("make fe-run ishga tushiring"). SKIP EMAS.     │
 * │ 4. Qamrov assertion       → tekshirilgan juftliklar EXPECTED ga teng boʻlmasa yoki  │
 * │    birorta sahifada 0 interaktiv element boʻlsa → exit 1 (selektor/route buzilgani  │
 * │    uchun jimgina oʻtib ketmasin).                                                  │
 * │ 5. Sahifa non-2xx / evaluate exceptionDetails → exit 1, retry-and-forgive YOʻQ.    │
 * └────────────────────────────────────────────────────────────────────────────────────┘
 *
 * Ishlatish:  make fe-test-viewports   (boshqa terminalda `make fe-run` + `make be-run`)
 * Muhit:      BASE_URL (default http://localhost:3000), CHROME_PATH, --fast (4×5)
 */
import { existsSync } from "node:fs";
import { execSync } from "node:child_process";
import puppeteer from "puppeteer-core";

const BASE_URL = (process.env.BASE_URL || "http://localhost:3000").replace(/\/$/, "");
const FAST = process.argv.includes("--fast");

// ── Chrome topish (2-shart) ──
function findChrome() {
  if (process.env.CHROME_PATH) {
    if (existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
    fail(`CHROME_PATH koʻrsatildi, lekin fayl yoʻq: ${process.env.CHROME_PATH}`);
  }
  const candidates = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
  ];
  for (const c of candidates) if (existsSync(c)) return c;
  for (const bin of ["google-chrome", "chromium", "chromium-browser"]) {
    try {
      const p = execSync(`command -v ${bin}`, { stdio: ["ignore", "pipe", "ignore"] })
        .toString()
        .trim();
      if (p) return p;
    } catch {
      /* keyingisi */
    }
  }
  fail("Chrome topilmadi. CHROME_PATH ni Chrome binary'ga oʻrnating.");
}

function fail(msg) {
  console.error(`✗ ${msg}`);
  process.exit(1);
}

// ── Matritsa ──
const VIEWPORTS_FULL = [
  { w: 320, h: 568 }, { w: 360, h: 640 }, { w: 390, h: 844 }, { w: 430, h: 932 },
  { w: 744, h: 1133 }, { w: 768, h: 1024 }, { w: 820, h: 1180 }, { w: 1023, h: 768 },
];
const VIEWPORTS_FAST = [{ w: 320, h: 568 }, { w: 390, h: 844 }, { w: 768, h: 1024 }, { w: 1023, h: 768 }];
const ROUTES_FULL = [
  "/uz", "/uz/narxlar", "/uz/xizmatlar", "__SERVICE__", "/uz/ishlarimiz",
  "/uz/haqimizda", "/uz/aloqa", "/uz/galereya", "/uz/blog", "/ru",
];
const ROUTES_FAST = ["/uz", "/uz/narxlar", "/uz/ishlarimiz", "/uz/aloqa", "/uz/galereya"];

const VIEWPORTS = FAST ? VIEWPORTS_FAST : VIEWPORTS_FULL;
let ROUTES = FAST ? ROUTES_FAST : ROUTES_FULL;

// Sahifada ishlaydigan audit funksiyasi (barcha B1–B7 tekshiruvlari bitta evaluate'da).
const AUDIT = () => {
  const innerW = window.innerWidth;
  const dpr = window.devicePixelRatio;
  const findings = [];
  const push = (rule, detail) => findings.push({ rule, detail });
  const path = (el) => {
    const bits = [];
    for (let e = el; e && e.nodeType === 1 && bits.length < 4; e = e.parentElement) {
      let s = e.tagName.toLowerCase();
      if (e.className && typeof e.className === "string") s += "." + e.className.trim().split(/\s+/).slice(0, 2).join(".");
      bits.unshift(s);
    }
    return bits.join(">");
  };
  const isHidden = (el, cs) =>
    cs.display === "none" || cs.visibility === "hidden" ||
    el.closest("[aria-hidden='true']") || el.getAttribute("aria-hidden") === "true";

  let interactiveInspected = 0;

  // B1 — sahifa gorizontal overflow
  if (document.documentElement.scrollWidth > innerW + 1) {
    const culprits = [...document.querySelectorAll("*")]
      .filter((e) => { const cs = getComputedStyle(e); return cs.position !== "fixed" && e.getBoundingClientRect().right > innerW + 1; })
      .slice(0, 5).map(path);
    push("B1", `sahifa overflow ${document.documentElement.scrollWidth - innerW}px: ${culprits.join(" | ")}`);
  }

  for (const el of document.querySelectorAll("*")) {
    const cs = getComputedStyle(el);
    // B2 — kesilgan-lekin-scroll qilinmaydigan (narx jadvali VA sigʻmagan h1)
    if (["hidden", "clip"].includes(cs.overflowX) && !isHidden(el, cs) && !(el.className + "").includes("line-clamp")) {
      const r = el.getBoundingClientRect();
      if (r.width > 4 && r.bottom > 0 && el.scrollWidth > el.clientWidth + 4) {
        push("B2", `kesilgan-scroll yoʻq (${el.scrollWidth}>${el.clientWidth}): ${path(el)}`);
      }
    }
  }

  // B3 — tap target. Nuqson: kichik dimensiya <24px (WCAG 2.5.8 AA HARD fail) YOKI ikkala
  // dimensiya ham <44px (iOS target — haqiqatan kichik tugma). Balandligi ≥44 boʻlgan tor
  // matn-nav havolasi (masalan "Blog" 30×44) TAPPABLE — flag qilinmaydi (shovqin boʻlmasin).
  // label krediti + inline/breadcrumb istisno.
  for (const el of document.querySelectorAll("a,button,summary,[role=radio],[role=slider],input:not([type=hidden]),select,textarea")) {
    const cs = getComputedStyle(el);
    if (isHidden(el, cs) || el.tabIndex === -1) continue;
    let r = el.getBoundingClientRect();
    if (r.width <= 4 || r.height <= 4 || r.right < 0 || r.left > innerW) continue;
    interactiveInspected++;
    if (["INPUT", "SELECT", "TEXTAREA"].includes(el.tagName)) { const l = el.closest("label"); if (l) r = l.getBoundingClientRect(); }
    if (el.tagName === "A" && (cs.display === "inline" || el.closest("nav[aria-label='breadcrumb']"))) continue;
    const small = Math.min(r.width, r.height);
    if (small < 24 || (r.width < 44 && r.height < 44))
      push("B3", `${Math.round(r.width)}×${Math.round(r.height)} kichik target: ${path(el)}`);
  }

  // B4 — forma control computed font-size <16 (meros orqali kelganini ham tutadi)
  for (const el of document.querySelectorAll("input:not([type=hidden]):not([type=checkbox]):not([type=radio]),select,textarea")) {
    const cs = getComputedStyle(el);
    if (isHidden(el, cs) || el.tabIndex === -1) continue;
    if (parseFloat(cs.fontSize) < 16) push("B4", `font-size ${cs.fontSize} <16 (iOS zoom): ${path(el)}`);
  }

  // B6 — <1024 da tezkor amallar paneli koʻrinishi shart (konversiya yoʻli)
  if (innerW < 1024) {
    const bar = document.querySelector("nav[aria-label='Tezkor amallar']");
    if (!bar || getComputedStyle(bar).display === "none") push("B6", "Tezkor amallar paneli <1024 da yoʻq/yashirin");
  }

  // B7 — [role=slider] host'i touch-action none|pan-y eʼlon qilsin
  for (const s of document.querySelectorAll("[role=slider]")) {
    const host = s.parentElement;
    if (host && !["none", "pan-y"].includes(getComputedStyle(host).touchAction))
      push("B7", `slider host touch-action=${getComputedStyle(host).touchAction} (none|pan-y kerak): ${path(s)}`);
  }

  return { findings, interactiveInspected };
};

// B5 — sizes sogʻligʻi (rasm YUKLANGACH oʻlchanadi, alohida)
const AUDIT_IMAGES = async () => {
  const dpr = window.devicePixelRatio;
  const imgs = [...document.querySelectorAll("img")].filter((i) => /_next\/image/.test(i.currentSrc || i.src || ""));
  imgs.forEach((i) => (i.loading = "eager"));
  await Promise.all(imgs.map((i) => (i.decode ? i.decode().catch(() => {}) : null)));
  const findings = [];
  for (const img of imgs) {
    const src = img.currentSrc || img.src;
    const w = Number(new URL(src, location.href).searchParams.get("w"));
    const rect = img.getBoundingClientRect();
    const needed = rect.width * dpr;
    if (w && needed > 0 && w > needed * 2)
      findings.push({ rule: "B5", detail: `picked ${w}px, kerak ~${Math.round(needed)}px (>2×): ${src.slice(0, 60)}` });
  }
  return findings;
};

async function main() {
  const chrome = findChrome();

  // 3-shart: server yetib boʻladimi (SKIP EMAS)
  let probe;
  try {
    probe = await fetch(`${BASE_URL}/uz`, { signal: AbortSignal.timeout(5000) });
  } catch (e) {
    fail(`Server yetib boʻlmadi (${BASE_URL}): ${e.message}. \`make fe-run\` ishga tushiring yoki BASE_URL bering.`);
  }
  if (!probe.ok) fail(`Server ${BASE_URL}/uz → HTTP ${probe.status} (2xx kutilgan).`);

  // __SERVICE__ ni haqiqiy slug bilan almashtiramiz (sitemap'dan)
  try {
    const sm = await (await fetch(`${BASE_URL}/sitemap.xml`, { signal: AbortSignal.timeout(5000) })).text();
    const m = sm.match(/\/uz\/xizmatlar\/([a-z0-9-]+)</);
    ROUTES = ROUTES.map((r) => (r === "__SERVICE__" ? (m ? `/uz/xizmatlar/${m[1]}` : "/uz/xizmatlar") : r));
  } catch {
    ROUTES = ROUTES.map((r) => (r === "__SERVICE__" ? "/uz/xizmatlar" : r));
  }

  const EXPECTED = VIEWPORTS.length * ROUTES.length;
  const browser = await puppeteer.launch({ executablePath: chrome, headless: "new", args: ["--no-sandbox", "--disable-gpu"] });

  let pairs = 0;
  let totalInteractive = 0;
  const allFindings = [];

  try {
    for (const vp of VIEWPORTS) {
      const page = await browser.newPage();
      await page.setViewport({ width: vp.w, height: vp.h, deviceScaleFactor: 2, isMobile: vp.w < 768, hasTouch: vp.w < 1024 });
      for (const route of ROUTES) {
        const url = `${BASE_URL}${route}`;
        const resp = await page.goto(url, { waitUntil: "networkidle2", timeout: 30000 });
        if (!resp || !resp.ok()) fail(`${url} @${vp.w} → HTTP ${resp ? resp.status() : "yoʻq"} (2xx kutilgan).`);
        let res, imgFindings;
        try {
          res = await page.evaluate(AUDIT);
          imgFindings = await page.evaluate(AUDIT_IMAGES);
        } catch (e) {
          fail(`evaluate xatosi ${url} @${vp.w}: ${e.message}`);
        }
        // 4-shart: har sahifada kamida bitta interaktiv element boʻlishi shart
        if (res.interactiveInspected === 0) fail(`${url} @${vp.w}: 0 interaktiv element — selektor/route buzilgan?`);
        totalInteractive += res.interactiveInspected;
        for (const f of [...res.findings, ...imgFindings]) allFindings.push({ vp: `${vp.w}×${vp.h}`, route, ...f });
        pairs++;
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }

  // 4-shart: qamrov
  if (pairs !== EXPECTED) fail(`Qamrov: ${pairs}/${EXPECTED} juftlik tekshirildi (kutilgan ${EXPECTED}).`);
  if (totalInteractive === 0) fail("Hech qanday interaktiv element tekshirilmadi — audit buzilgan.");

  if (allFindings.length) {
    console.error(`✗ Viewport gate — ${allFindings.length} topilma (${pairs}/${EXPECTED} juftlik):`);
    const byVp = {};
    for (const f of allFindings) (byVp[`${f.vp} ${f.route}`] ??= []).push(f);
    for (const [k, list] of Object.entries(byVp)) {
      console.error(`  ${k}`);
      for (const f of list) console.error(`      [${f.rule}] ${f.detail}`);
    }
    process.exit(1);
  }

  console.log(`✓ Viewport gate toza — ${pairs}/${EXPECTED} juftlik, ${totalInteractive} interaktiv element (B1–B7).`);
}

await main();
