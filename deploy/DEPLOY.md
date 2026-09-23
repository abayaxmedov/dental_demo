# dental_demo — Deploy qo'llanmasi (ADR-021)

Bitta Linux VPS'da Docker Compose bilan: **PostgreSQL + Django (gunicorn) + Next.js (standalone) + nginx**.
Barchasi `docker-compose.prod.yml` da. Demo **https://dentist.onesystem.uz** da, TLS host nginx +
certbot'da tugaydi (§6b — JORIY, REAL setup).

| | |
|---|---|
| Server | **38.242.255.34** (Contabo VPS, `vmi2867712`) · Ubuntu 24.04 · 6 vCPU / 11 GB |
| Kirish | `ssh root@38.242.255.34` (kalit `~/.ssh/id_ed25519`) |
| Loyiha yo'li | **`/root/abay/dental_demo`** |
| Domen | `dentist.onesystem.uz` → A-record shu IP'ga |
| Stack porti | `127.0.0.1:8090` (faqat localhost; :80/:443 ni HOST nginx egallagan) |

> **DIQQAT — umumiy server.** Bu VPS'da o'nlab boshqa loyiha ishlaydi (`~/abay/*`, 30+ konteyner,
> `/etc/nginx/conf.d/*.conf` da boshqa saytlar). Faqat `~/abay/dental_demo` va bizning nginx
> vhost'imizga tegiladi. `docker system prune`, umumiy `docker compose down`, host nginx'ning
> boshqa fayllari — **MUTLAQO YO'Q**.
>
> **Eski AWS EC2 (`3.227.184.179`) endi bizniki EMAS** — Elastic IP biriktirilmagani uchun
> instance IP'ni yo'qotdi, AWS uni boshqa mijozning ALB'siga berdi (ADR-022). Eski IP'ga
> murojaat qilmang.

---

## 0. Nega bunday arxitektura (muhim eslatmalar)

- **Ichki trafik hech qachon ommaviy origin'ga chiqmaydi.** (Tarixan sabab EC2 hairpin NAT edi;
  hozirgi VPS'da sabab boshqa — tashqi chiqish TLS/host nginx orqali behuda aylanma bo'lardi va
  `SECURE_SSL_REDIRECT`/certbot bilan mo'rt zanjir hosil qilardi.) Qoida o'sha:
  - SSR/ISR fetch → `API_URL_INTERNAL=http://backend:8000` (ichki, nginx'ni chetlab).
  - next/image optimizer media'ni `MEDIA_REWRITE_TARGET=http://nginx` orqali (ichki) oladi.
  - Backend media URL'lari **root-relative** (`MEDIA_PUBLIC_BASE=/`); brauzerdagi `og:image`ni
    `metadataBase` mutlaq ommaviy qiladi. Natijada rasm optimizatsiyasi **saqlanadi**.
- **Build vaqtida QOTADIGAN** qiymatlar: `NEXT_PUBLIC_*`, `SITE_HTTPS`, `MEDIA_REWRITE_TARGET`.
  Ularni o'zgartirsangiz frontend'ni **qayta build** qiling (`--build`).
- Sirlar faqat `deploy/.env.prod` da (git ignore). `deploy/.env.prod.example` — namuna (commit qilinadi).

---

## 1. Serverni tayyorlash (bir marta)

SSH:

```bash
ssh root@38.242.255.34
```

Joriy serverda Docker (v29) + Compose (v5) **allaqachon o'rnatilgan** — quyidagi blok faqat
NOLDAN yangi server uchun. Docker + Compose plugin (Ubuntu):

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER && newgrp docker   # sudo'siz docker
```

**Firewall:** `22` (SSH), `80` va `443` ochiq bo'lsin. Bizning stack `127.0.0.1:8090` da —
u tashqaridan KO'RINMAYDI va ko'rinmasligi ham kerak (kirish faqat host nginx orqali).

---

## 2. Kod + env (bir marta)

Joriy serverda kod **`/root/abay/dental_demo`** da turibdi (eski EC2'dan ko'chirilgan, git
metadata'siz — `git pull` ISHLAMAYDI, yangilash uchun §7 ga qarang).

Noldan:
```bash
mkdir -p ~/abay && cd ~/abay
git clone git@github.com:abayaxmedov/dental_demo.git
cd dental_demo
cp deploy/.env.prod.example deploy/.env.prod
```

`deploy/.env.prod` ni tahrirlang — kamida quyidagilar:

| O'zgaruvchi | Qiymat |
|---|---|
| `SECRET_KEY` | `openssl rand -hex 32` |
| `REVALIDATE_SECRET` | `openssl rand -hex 32` (frontend va backend'da BIR XIL) |
| `POSTGRES_PASSWORD` va `DATABASE_URL` dagi parol | bir xil kuchli parol |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | klinika bot/chat (sotiladigan xususiyat) |

`.env.prod.example` **joriy setup** bilan to'ldirilgan (domen + `HTTP_BIND=127.0.0.1:8090` +
`SITE_HTTPS=true`). Boshqa domen uchun `dentist.onesystem.uz` ni hamma joyda almashtiring —
`ALLOWED_HOSTS`, `CORS/CSRF_TRUSTED_ORIGINS`, `NEXT_PUBLIC_*`, `PUBLIC_BASE_URL`.

---

## 3. Deploy

```bash
bash deploy/deploy.sh
```

Bu: image build → `up -d` → migrate (entrypoint) → backend *healthy* kutish → ISR purge + qizdirish.
`deploy.sh` `REPLACE_…` placeholder qolsa **to'xtaydi** (jimgina buzuq deploy bo'lmasin).

Qo'lda muqobil:
```bash
docker compose --env-file deploy/.env.prod -f docker-compose.prod.yml up -d --build
```

---

## 4. Birinchi deploy'dan keyin — content seed (bir marta)

`deploy.sh` content'ni **ataylab** seed qilmaydi (restartda ma'lumot yo'qolmasin). Birinchi marta:

```bash
C="docker compose --env-file deploy/.env.prod -f docker-compose.prod.yml"
# 1) Demo rasmlar (CC0, Openverse'dan) — internet egress kerak:
$C exec backend python manage.py fetch_seed_images
# 2) Demo content (uz/ru/en):
$C exec backend python manage.py seed_demo --reset
# 3) Admin (prod'da --force shart, T-FIX-16 guard):
$C exec backend python manage.py create_demo_admin --username admin --password 'KUCHLI_PAROL' --force
# 4) (ixtiyoriy) Admin TIRIK ko'rinishi uchun ko'p tasodifiy qabul + murojaat (additive):
$C exec backend python manage.py seed_random --appointments 60 --leads 25
# 5) ISR keshini yangilash:
bash deploy/deploy.sh   # yoki faqat warm qismi
```

Admin: `https://<domen>/admin/` · Sayt: `https://<domen>/`. `seed_random` xohlagancha qayta
ishga tushiriladi (o'chirmaydi, qo'shadi) — kalendar/inbox to'lasin.

---

## 5. Sotilgan klinikaga rebrand (reskin)

`deploy/reskin/prospect.example.yml` dan nusxa oling, to'ldiring, so'ng:

```bash
docker compose --env-file deploy/.env.prod -f docker-compose.prod.yml \
  exec backend python manage.py reskin --config deploy/reskin/<mijoz>.yml
```

Reskin uch tilni ham yozadi va ISR'ni tozalaydi (`FRONTEND_BASE_URL=http://frontend:3000`).

---

## 6. TLS / domen (HTTP → HTTPS)

1. Domenning A-record'ini **38.242.255.34** ga yo'naltiring (`dig +short <domen>` bilan tekshiring).
2. `deploy/.env.prod` da barcha IP'ni domenga almashtiring; **`SITE_HTTPS=true`**.
3. `deploy/nginx/dental.conf` ga `443` server bloki + certbot (yoki Caddy) qo'shing, `80`→`443` redirect.
   Certbot uchun `certbot/certbot` konteyner yoki host'da certbot; sertifikatni nginx'ga mount qiling.
4. **Qayta build** (SITE_HTTPS/NEXT_PUBLIC build vaqtida qotadi):
   ```bash
   docker compose --env-file deploy/.env.prod -f docker-compose.prod.yml up -d --build
   ```
   `SITE_HTTPS=true` bo'lgach backend HSTS + secure-cookie + SSL-redirect, frontend
   `upgrade-insecure-requests` + HSTS'ni yoqadi.

---

## 6b. Umumiy server (host nginx :80/:443 ni egallagan) — REAL setup

**Bu — joriy, ishlab turgan setup.** Serverda host nginx o'nlab saytga xizmat qiladi
(`/etc/nginx/conf.d/*.conf` + `/etc/nginx/sites-enabled/*`: `crm.onesystem.uz`, `24.procleaning.uz`,
`airium.uz`, `metro.onesystem.uz` va h.k.), certbot sertifikatlari `/etc/letsencrypt/live/` da.
Shuning uchun dental stack o'z nginx'ini **`127.0.0.1:8090`** ga bog'laydi (boshqa hech bir port
band qilinmaydi), host nginx esa `dentist.onesystem.uz` ni unga proxy qiladi + TLS'ni tugatadi.
Bizning vhost — **alohida fayl**, `server_name` ham alohida: qo'shni saytlarga ta'sir qilmaydi.

1. `deploy/.env.prod` da: `HTTP_BIND=127.0.0.1:8090`, `SITE_HTTPS=true`, barcha URL'lar
   `https://dentist.onesystem.uz`, `ALLOWED_HOSTS=dentist.onesystem.uz,localhost,127.0.0.1,backend`.
2. Stack'ni ko'taring: `bash deploy/deploy.sh` (nginx faqat localhost:8090 da).
3. Host nginx server bloki + TLS: [`deploy/nginx/host-site.conf.example`](nginx/host-site.conf.example)
   izohidagi buyruqlar (cp → sed → symlink → `nginx -t` → reload → `certbot --nginx`).
4. Chain nozikligi: compose nginx `X-Forwarded-Proto` ni host nginx'dan **saqlaydi** (`$fwd_proto` map),
   aks holda `SITE_HTTPS=true` da Django cheksiz https-redirect qiladi.

---

## 7. Kundalik ishlar

```bash
C="docker compose --env-file deploy/.env.prod -f docker-compose.prod.yml"
$C ps                 # holat
$C logs -f backend    # loglar
$C restart backend    # xizmatni qayta ishga tushirish
$C down               # to'xtatish (volume'lar saqlanadi)
```

**Yangilash.** Serverdagi nusxada `.git` YO'Q (ko'chirishda tushib qolgan), shuning uchun
`git pull` emas — lokal mashinadan kodni uzatib, qayta deploy qilamiz (`.env.prod` va
`_migration/` TEGILMAYDI):

```bash
# LOKAL (repo ildizida):
git archive --format=tar HEAD | ssh root@38.242.255.34 \
  'tar xf - -C /root/abay/dental_demo'
ssh root@38.242.255.34 'cd /root/abay/dental_demo && bash deploy/deploy.sh'
```

**Zaxira (cron tavsiya):**
```bash
bash deploy/backup.sh                       # deploy/backups/ ga DB + media
# crontab -e:  0 3 * * *  cd /root/abay/dental_demo && bash deploy/backup.sh >> /root/abay/dental_demo/deploy/backups/cron.log 2>&1
```

**Rollback:** lokalda oldingi commit'ga o'ting va yuqoridagi `git archive` bilan qayta uzating.
```bash
# DB'ni tiklash: gunzip < deploy/backups/db-XXXX.sql.gz | $C exec -T db psql -U dental dental
```

---

## 8. Nosozliklarni bartaraf etish

| Alomat | Sabab / yechim |
|---|---|
| Brauzer "sertifikat mos emas" deydi (boshqa domen nomi) | DNS bizning serverga qaramayapti, YOKI host nginx'da bizning `server_name` bloki yo'q → so'rov default vhost'ga tushib, begona sertifikat beriladi. `dig +short dentist.onesystem.uz` = `38.242.255.34` va `nginx -T \| grep dentist` bilan tekshiring. |
| Nginx "Welcome to nginx!" chiqadi | Xuddi shu sabab — vhost yo'q yoki `nginx -t` xato berib reload bo'lmagan. |
| 502 Bad Gateway | Stack tushgan. `$C ps`, `$C logs -f frontend backend`. Host nginx `127.0.0.1:8090` ga uradi. |
| Cheksiz https redirect sikli | `SECURE_SSL_REDIRECT` yoqilgan (yoqilmasligi kerak — ADR-022) yoki compose nginx `X-Forwarded-Proto`ni yo'qotgan (`$fwd_proto` map). |
| Sayt ochilmaydi, https'ga o'tib ketadi | `SITE_HTTPS=true` bo'lib qolgan-u TLS yo'q. `false` qiling, qayta build. |
| Admin login 403 (CSRF) | `CSRF_TRUSTED_ORIGINS` da to'liq origin (`https://domen`) yo'q. |
| Rasm 404 / optimizatsiya xato | `MEDIA_REWRITE_TARGET=http://nginx` va media volume tekshiring: `$C exec nginx ls /var/www/media`. |
| SSR bo'sh/eski content | backend healthy emas yoki seed qilinmagan (4-bo'lim). `$C logs backend`. |
| `DisallowedHost` | `ALLOWED_HOSTS` ga `backend`, `localhost`, IP kirganini tekshiring. |
| 400/500 booking/appointment | frontend build'da `NEXT_PUBLIC_API_URL` noto'g'ri (browser origin). Qayta build. |
