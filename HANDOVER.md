# HANDOVER — sayt egasiga qoʻllanma

Bu hujjat saytni **sotib olgan klinika** uchun. Texnik bilim talab qilmaydi; texnik
qadamlarni sizga sotgan/oʻrnatgan mutaxassis bajaradi, siz bu yerdan nazorat qilasiz.

> ⚠️ **Ishga tushirishdan OLDIN 4 ta majburiy qadam** (pastda "1. Birinchi ishga tushirish").
> Bular bajarilmasa sayt demo holatida qoladi (namuna rasmlar, demo admin, namuna litsenziya).

---

## 0. Nima sotib oldingiz

Uch tilli (oʻzbek / rus / ingliz) stomatologiya sayti:

- **Onlayn qabulga yozilish** — bemor xizmat + shifokor + vaqt tanlaydi, tasdiq Telegram'ga keladi.
- **Bemor oʻzi boshqaradi** — `/qabul/<kod>` havolasi orqali koʻrish / bekor qilish / **boshqa vaqtga koʻchirish**.
- **Admin panel** (`/admin/`) — qabullar, murojaatlar (lead), xizmatlar, shifokorlar, narxlar, bloglar, sharhlar.
- **Telegram xabarnoma** — har yangi qabul/murojaat klinikaning Telegram'iga tushadi.
- **SEO tayyor** — Google/Yandex uchun sitemap, hreflang, structured data; Lighthouse mobil ballari
  Prodent shablonidan sezilarli yuqori (tafsilot va oʻlchov usuli — `README.md`).
- **3D** — bosh sahifada aylanuvchi tish, xizmatlar sahifasida bosiladigan tish xaritasi.

---

## 1. Birinchi ishga tushirish (majburiy 4 qadam)

### 1.1 Brendni oʻzgartirish (reskin)
Klinika nomi, ranglari, logotipi, telefonlari `reskin` buyrugʻi bilan bir marta oʻrnatiladi:

```bash
make reskin CONFIG=prospect.yml
```

`prospect.yml` namunasi — `deploy/reskin/prospect.example.yml`. Faqat oʻzgartirmoqchi boʻlgan
qatorlarni toʻldiring. **Bitta brand rang** butun sayt rang shkalasini avtomatik moslaydi (ADR-004).
Avval koʻrish uchun: `make reskin CONFIG=prospect.yml ARGS=--dry-run`.

**Uch til:** matnli maydonlar (nom, shior, manzil, "biz haqimizda") uchala tilda ham yangilanadi.
Oddiy matn yozsangiz — uchala tilga bir xil; `{uz:…, ru:…, en:…}` yozsangiz — har til alohida.
Til berilmasa buyruq **ogohlantiradi** (rus sahifada eski matn qolib ketmasin).

**Kesh:** `.env` dagi `REVALIDATE_SECRET` frontend `.env.local` bilan bir xil boʻlsa, reskin
tugagach kesh avtomatik tozalanadi (`✓ Frontend keshi tozalandi`). Aks holda `make warm` ni
ishlating yoki oʻzgarish 5 daqiqagacha kutadi.

### 1.2 Namuna rasmlarni almashtirish  ⚠️ HUQUQIY
Demo'dagi 28 ta namuna rasmning **14 tasi CC-BY** litsenziyasida — bu litsenziya **muallifni
koʻrsatishni majbur qiladi**; qolgani CC0 (majburiyatsiz). Shuning uchun saytda
`/media-litsenziyalar` sahifasi bor va u footer'dan havola qilingan — **uni oʻchirmang**,
toki shu rasmlar saytda tursa.

Ishga tushirishdan oldin:
- Shifokor portretlari, klinika/ishlar (before/after) rasmlarini **oʻz rasmlaringiz** bilan almashtiring
  (bu ayni paytda atributsiya majburiyatidan ham xalos qiladi).
- Model release (rasmga tushgan odamning yozma roziligi) boʻlishi shart.
- Toʻliq roʻyxat: saytda `/media-litsenziyalar`, repoda `ASSETS_LICENSES.md`.
- Rasm almashtirilganda `manage.py check_asset_licenses` roʻyxat va sahifa sinxronligini tekshiradi.

### 1.3 Namuna litsenziya matnini almashtirish
Footer'dagi litsenziya/yuridik matn namunaviy. `reskin` config'da `legal:` yoki admin'da
`Sayt sozlamalari` → litsenziya/yuridik shaxs qatorlarini haqiqiysiga oʻzgartiring.

### 1.4 Demo admin akkauntni oʻchirish  ⚠️ XAVFSIZLIK
Demo koʻrsatish uchun `demo` nomli zaif parolli admin bor. Ishga tushirishdan oldin:
- `/admin/` → Foydalanuvchilar → `demo` ni **oʻchiring**.
- Oʻzingizga **kuchli parolli** yangi admin yarating: `python manage.py createsuperuser`.

---

## 2. Kundalik foydalanish (admin panel)

`/admin/` ga oʻz login/parolingiz bilan kiring.

| Boʻlim | Nima qilasiz |
|---|---|
| **Qabullar** | Yangi/kutilayotgan qabullarni koʻrish, tasdiqlash, bekor qilish |
| **Murojaatlar (Lead)** | Qoʻngʻiroq/narx soʻrovlari — bogʻlanish |
| **Xizmatlar / Narxlar** | Xizmat matni, narxlarni yangilash (narxni yashirish ham mumkin) |
| **Shifokorlar** | Yangi shifokor, bio, jadval (qabul vaqtlari shundan hisoblanadi) |
| **Ish vaqti** | Klinika ish soatlari — boʻsh vaqt slotlari shundan chiqadi |
| **Blog / Sharhlar / Galereya** | Kontent qoʻshish |

## 3. Telegram xabarnoma

Klinika Telegram'iga xabar kelishi uchun bir marta sozlanadi (bot token + chat id — backend
`.env`). Buni oʻrnatuvchi mutaxassis bajaradi; tekshirish: `python manage.py test_telegram`.

## 4. Nusxa (backup) va yangilanish

- Ma'lumotlar bazasi (qabullar/murojaatlar) muntazam **backup** qilinishi shart — deploy skriptida.
- Kontent oʻzgarishlari darhol saytda koʻrinadi (ISR, ~5 daqiqagacha kesh).

## 5. Deploy (texnik)

Server, domen, HTTPS, backup — `deploy/` katalogi va oʻrnatuvchi mutaxassis zimmasida.
Muhim: rasm/API host **HTTPS** boʻlishi shart (prod CSP `upgrade-insecure-requests`, ADR-019).

---

**Savol?** Sizga saytni sotgan mutaxassisga murojaat qiling — texnik jurnal `PROJECT_HISTORY.md`da.
