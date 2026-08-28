# Oq Marvarid Dental — demo

Stomatologiya klinikalari uchun sotiladigan **demo veb-sayt**. Bir marta quriladi, har bir
klinika uchun `manage.py reskin` bilan 30 daqiqada qayta brendlanadi. Vizual mezon — Colorlib
**Prodent**, lekin har jihatdan undan yaxshiroq va bir nechta joyda **haqiqiy 3D** bilan.

- **Frontend:** Next.js 16 (App Router, SSR/SSG) · React 19 · TypeScript · Tailwind 4 · next-intl (uz/ru/en) — `frontend/`
- **Backend:** Django 5.2 + **DRF** (headless API) · PostgreSQL 17 — `backend/`
- **3D:** three.js + @react-three/fiber (Faza 4)
- **Bozor:** Toshkent va viloyat xususiy klinikalari · Telegram xabarnoma · +998

> Nega Next.js + headless DRF (React) — [ADR-016](ARCHITECTURE_DECISIONS.md). Buyurtmachi frontend
> React boʻlishini talab qildi; Next.js SSR/SSG SEO'ni saqlaydi (Yandex/Google indekslashi).

## Loyiha hujjatlari (ichki jurnal — `.gitignore` da, ADR-015)

| Fayl | Vazifasi |
|---|---|
| `PROJECT_HISTORY.md` | Umumiy jurnal (har sessiya boshida oʻqiladi) |
| `ARCHITECTURE_DECISIONS.md` | ADR-lar + stek + data model + API + 3D reja |
| `CHANGELOG.md` | Kod oʻzgarishlari (diff bilan) |
| `TODO.md` | Roadmap + commit hajmidagi tasklar |
| `HANDOVER.md` | Sotib olgan klinika uchun qoʻllanma (keyin) |
| `ASSETS_LICENSES.md` | Har rasm/model/font litsenziyasi |

## Tez boshlash (lokal dev)

```bash
# 1. Ma'lumotlar bazasi (PostgreSQL 17)
make db-up

# 2. Backend (Django DRF) — :8000
make be-install          # birinchi marta
cp backend/.env.example backend/.env
make be-migrate
make be-run              # http://localhost:8000/api/v1/docs/  ·  /admin/  ·  /healthz/

# 3. Frontend (Next.js) — :3000
make fe-install          # birinchi marta
make fe-run              # http://localhost:3000/uz  (/ru /en)
```

Backend `.env` da `DATABASE_URL` boʻsh boʻlsa dev'da **sqlite** ishlatiladi (tez `check` uchun).
Haqiqiy ish uchun `DATABASE_URL=postgres://dental:dental@localhost:5432/dental` qoʻying.

## Monorepo tuzilishi

To'liq daraxt: `ARCHITECTURE_DECISIONS.md` → C-qism. Qisqacha:

```
backend/   Django DRF (config/ + apps/), headless /api/v1/ + /admin/
frontend/  Next.js (src/app/[locale]/), uch tilli, SSR/SSG
deploy/    nginx, systemd, cron, backup (Faza 1 oxiri)
```

## Ishlash koʻrsatkichlari — Lighthouse (mobil)

Sotuv daʼvosi ("har jihatdan Prodent'dan yaxshiroq") oʻlchandi. Lighthouse mobil, bizning
prod build vs **jonli Prodent demo** (`preview.colorlib.com/theme/prodent`):

Raqamlar **ikki xil run**dan olingan, shuning uchun ustunlar ajratilgan — bitta ustunga
aralashtirish notoʻgʻri boʻlardi (bu avval shunday edi, audit tuzatdi):

| Kategoriya         | Lokal **prod** build | Origin mos **dev** run | Prodent (jonli) |
|--------------------|:--------------------:|:----------------------:|:---------------:|
| Performance        | **88–94**            | 64¹                    | 64              |
| Accessibility      | **100**              | **100**                | 80              |
| Best Practices     | 96–100²              | **100**                | 96              |
| SEO                | 92³                  | **100**                | 66              |
| CLS (layout shift) | **0**                | —                      | 0.001           |
| TBT (bloklanish)   | **18–24 ms**         | —                      | 103 ms          |
| LCP                | ~3.0–3.9 s⁴          | —                      | 9.1 s           |

**Aniq xulosa:** Accessibility, SEO, CLS, TBT va LCP boʻyicha **ishonchli oldinda**;
Performance boʻyicha sezilarli oldinda (88–94 vs 64); **Best Practices boshsahifada teng**
(96 vs 96, xizmatlar sahifasida 100). Yaʼni "mutlaqo har bir mezonda oldinda" degan avvalgi
daʼvo **notoʻgʻri** edi — BP da durang.

> ¹ Dev build minifikatsiyasiz va HMR bilan ishlaydi — dev'dagi Performance balli oʻlchov
> sifatida ahamiyatsiz, u yerda faqat a11y/BP/SEO ishonchli.
> ² Lokal prod'da `errors-in-console`: prod CSP `upgrade-insecure-requests` http backend
> rasmlarini https'ga koʻtaradi va lokalda ular yiqiladi. HTTPS media host'da yoʻqoladi.
> ³ Lokal prod'da `canonical`: test URL (`127.0.0.1:PORT`) sozlangan `NEXT_PUBLIC_SITE_URL`
> bilan mos emas. Haqiqiy domenda yoʻqoladi (origin mos dev run buni tasdiqlaydi: 100).
> ⁴ LCP haqiqiy prod'da media host HTTPS + CDN boʻlgach yaxshilanadi.

> ⚠️ **Loyihaning oʻz qabul mezoni** (`TODO.md`): Lighthouse mobil **≥ 95**/100/100/100.
> Performance **88–94** — bu chiziqdan **past**, yaʼni band hali **yopilmagan**. Asosiy sabab
> qodir desktopdagi 3D chunk emas (mobil uni yuklamaydi), balki media host va rasm
> yetkazib berish — deploy (HTTPS + CDN) dan keyin qayta oʻlchanadi.

## Holat

**Faza 0–4 ✓ · Faza 5 (sifat) davom etmoqda.** To'liq booking oqimi (slot engine, Telegram,
`/qabul/[token]` — koʻrish/bekor/koʻchirish), 16+ sahifa uch tilda, SEO (sitemap/robots/JSON-LD/
hreflang/OG/PWA manifest), 2 WebGL sahna, xavfsizlik header'lari + CSP, a11y (WCAG 2 A/AA),
Vitest + i18n parity gate. Batafsil — `PROJECT_HISTORY.md` / `TODO.md`.
