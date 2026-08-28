# Jonli demo skripti (sotuvchi uchun)

**Maqsad:** ~10 daqiqada klinika egasiga qiymatni koʻrsatish. Tartib — eng kuchli taassurotdan.
**Oldindan:** telefon + noutbukda demo ochiq; Telegram xabarnoma ISHLAYOTGANIga ishonch hosil qiling
(`python manage.py test_telegram`); backend + frontend ishlab tursin.

> 🎯 "Wow" nuqtalari: (1) qabul → Telegram darhol · (2) bemor oʻzi koʻchiradi · (3) reskin 30 sniya ·
> (4) 3D · (5) Lighthouse Prodent bilan yonma-yon.

---

## 0. Ochilish (30 soniya)
"Bu — klinikangiz uchun tayyor sayt. Uch tilda, onlayn qabul bilan. Keling, bemor koʻzi bilan koʻramiz."
Bosh sahifani oching — **3D tishni** kutib turing (aylanadi). "Bu sizning raqobatchida yoʻq."

## 1. Bemor qabulga yoziladi (2 daq) — ENG MUHIM
1. "Qabulga yozilish" → xizmat tanlang (masalan Implantatsiya).
2. Shifokor + **boʻsh vaqtni** tanlang — "vaqtlar real, ish jadvalidan chiqadi, band boʻlgani koʻrinmaydi."
3. Ism + telefon (`90 123 45 67`) + rozilik → yuboring.
4. ⚡ **Telegram'ni koʻrsating** — xabar DARHOL tushdi. "Administrator hech narsa qilmadi. Bemor uxlab
   yotganda ham qabul tushadi."

## 2. Bemor oʻzi boshqaradi (1 daq)
1. Tasdiq sahifasidagi **havolani** oching (`/qabul/<kod>`).
2. "Boshqa vaqtga koʻchirish" → yangi vaqt → tasdiq. "Bemor sizga qoʻngʻiroq qilmasdan oʻzi koʻchirdi.
   Administrator vaqti tejaladi."
3. (ixtiyoriy) "Bekor qilish" — slot avtomatik boʻshaydi.

## 3. Admin panel (1.5 daq)
1. `/admin/` → **Qabullar** — hozirgina yaratilgan qabul shu yerda.
2. **Murojaatlar (Lead)** — qoʻngʻiroq soʻrovlari.
3. **Narxlar** — bitta qatorni oʻzgartiring, saqlang → "saytda darhol yangilanadi, dasturchi kerak emas."
4. **Xizmatlar/Shifokorlar** — "hammasini oʻzingiz boshqarasiz."

## 4. Reskin — 30 soniyada sizniki (1.5 daq) — KUCHLI
> ⚙️ **Oldindan shart:** `REVALIDATE_SECRET` backend `.env` va frontend `.env.local` da BIR XIL
> boʻlsin. Shunda `reskin` tugagach kesh avtomatik tozalanadi va oʻzgarish **darhol** koʻrinadi.
> Buyruq chiqishida `✓ Frontend keshi tozalandi` qatorini koʻrishingiz shart — koʻrmasangiz
> `make warm` ni ishlating (aks holda oʻzgarish ISR muddati, 5 daqiqagacha, kutadi).

1. Terminalda: `make reskin CONFIG=prospect.yml ARGS=--dry-run` — oʻzgarishlar roʻyxatini koʻrsating
   (til boʻyicha: `name_uz/ru/en`, `tagline_uz/ru/en` — "uch tilda ham almashadi" deb ayting).
2. `make reskin CONFIG=prospect.yml` → `✓ Frontend keshi tozalandi` → sahifani yangilang.
3. "Nom, rang, logotip — hammasi oʻzgardi, **uch tilda ham**. **Bitta rang** butun saytni moslaydi.
   Sizning klinikangiz uchun 30 daqiqada tayyorlaymiz." (rangni prospekt brendiga oldindan sozlab
   qoʻying — taassurot kuchli.)

## 5. Mobil + 3D (1 daq)
1. **Telefonda** oching — pastdagi tezkor panel: Qoʻngʻiroq / Telegram / Manzil. "Mijoz bir bosishda
   qoʻngʻiroq qiladi."
2. Xizmatlar sahifasi — **bosiladigan tish xaritasi** (3D). "Interaktiv, raqobatchida yoʻq."

## 6. Yakuniy zarba: tezlik + SEO (1 daq)
1. `README.md` dagi Lighthouse jadvalini oching — **Prodent bilan yonma-yon**.
2. "Performance 88–94 vs 64, Accessibility 100 vs 80, SEO 100 vs 66. Google tez va qulay saytlarni
   yuqoriroq koʻrsatadi — bu koʻproq bemor demakdir."

## 7. Yopish (30 soniya)
"Sayt tayyor, sizning brendingiz bilan `__` kunda ishga tushadi. Uch paketimiz bor —" → `PRICING.md`.
E'tirozlar uchun pastga qarang.

---

## Tez-tez e'tirozlar

| E'tiroz | Javob |
|---|---|
| "Qimmat" | "Bir bemor implant = paket narxidan koʻp. Sayt oyiga bir necha qabul keltirsa qoplanadi." |
| "Menda Instagram bor" | "Instagram — reklama, sayt — qabul + Google'da topilish. Sayt Instagram'ni bosh sahifada koʻrsatadi." |
| "Oʻzim boshqara olamanmi?" | "Ha — admin panel oddiy, video qoʻllanma bор. Start paketi aynan shuning uchun." |
| "Onlayn toʻlov bormi?" | "Payme/Click qoʻshsa boʻladi — alohida faza sifatida hujjatlashtirilgan." |
| "Ma'lumot xavfsizmi?" | "Ha — mahalliy hosting, HTTPS, spam himoyasi, muntazam backup." |

> Demo tugagach: yaratilgan test qabullarni admin'dan tozalang; reskin'ni original brendga qaytaring.
