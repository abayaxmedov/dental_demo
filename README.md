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

## Holat

**Faza 1 — skelet.** Backend: settings split, core abstract modellar, `/healthz/`, OpenAPI schema.
Frontend: `[locale]` routing, uch tilli bosh sahifa, til almashtirgich. Keyingi ishlar — `TODO.md`.
