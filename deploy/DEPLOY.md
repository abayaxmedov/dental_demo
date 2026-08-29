# dental_demo — Deploy qo'llanmasi (ADR-021)

Bitta Linux VPS'da Docker Compose bilan: **PostgreSQL + Django (gunicorn) + Next.js (standalone) + nginx**.
Barchasi `docker-compose.prod.yml` da. Demo hozircha **IP orqali, HTTP** (TLS yo'q) — domen olgach
pastdagi *TLS* bo'limi bilan HTTPS'ga o'tiladi.

Server: **3.227.184.179** · SSH kaliti: `aws-key_kz.pem` (repo ildizida, **git ignore**da — hech qachon commit qilinmaydi).

---

## 0. Nega bunday arxitektura (muhim eslatmalar)

- **EC2 hairpin NAT:** instance (va uning konteynerlari) o'zining **ommaviy IP**'siga ura olmaydi.
  Shuning uchun:
  - SSR/ISR fetch → `API_URL_INTERNAL=http://backend:8000` (ichki, nginx'ni chetlab).
  - next/image optimizer media'ni `MEDIA_REWRITE_TARGET=http://nginx` orqali (ichki) oladi.
  - Backend media URL'lari **root-relative** (`MEDIA_PUBLIC_BASE=/`); brauzerdagi `og:image`ni
    `metadataBase` mutlaq ommaviy qiladi. Natijada rasm optimizatsiyasi **saqlanadi**.
- **Build vaqtida QOTADIGAN** qiymatlar: `NEXT_PUBLIC_*`, `SITE_HTTPS`, `MEDIA_REWRITE_TARGET`.
  Ularni o'zgartirsangiz frontend'ni **qayta build** qiling (`--build`).
- Sirlar faqat `deploy/.env.prod` da (git ignore). `deploy/.env.prod.example` — namuna (commit qilinadi).

---

## 1. Serverni tayyorlash (bir marta)

SSH (repo ildizidan, kalit huquqi 400 bo'lsin):

```bash
chmod 400 aws-key_kz.pem
ssh -i aws-key_kz.pem ubuntu@3.227.184.179
```

Docker + Compose plugin (Ubuntu):

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER && newgrp docker   # sudo'siz docker
```

**Security Group / firewall:** `22` (SSH) va `80` (HTTP) ochiq bo'lsin. TLS qo'shilganda `443`.

---

## 2. Kod + env (bir marta)

```bash
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

IP o'rniga domen ishlatsangiz, `ALLOWED_HOSTS` / `*_ORIGINS` / `NEXT_PUBLIC_*` / `PUBLIC_BASE_URL`
larni domenga o'zgartiring.

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

1. Domenning A-record'ini `3.227.184.179` ga yo'naltiring.
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

Bu serverda host nginx allaqachon boshqa saytlarni (`mebel.onesystem.uz` → :3000, `sqb.onesystem.uz`)
xizmat qiladi. Shuning uchun dental stack o'z nginx'ini **`127.0.0.1:8090`** ga bog'laydi, host nginx
esa `dentist.onesystem.uz` ni unga proxy qiladi + TLS'ni tugatadi.

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
git pull && bash deploy/deploy.sh   # yangilanish
```

**Zaxira (cron tavsiya):**
```bash
bash deploy/backup.sh                       # deploy/backups/ ga DB + media
# crontab -e:  0 3 * * *  cd /home/ubuntu/dental_demo && bash deploy/backup.sh
```

**Rollback:** oldingi commit'ga qayting va qayta deploy:
```bash
git checkout <oldingi-sha> && bash deploy/deploy.sh
# DB'ni tiklash: gunzip < deploy/backups/db-XXddd.sql.gz | $C exec -T db psql -U dental dental
```

---

## 8. Nosozliklarni bartaraf etish

| Alomat | Sabab / yechim |
|---|---|
| Sayt ochilmaydi, https'ga o'tib ketadi | `SITE_HTTPS=true` bo'lib qolgan-u TLS yo'q. `false` qiling, qayta build. |
| Admin login 403 (CSRF) | `CSRF_TRUSTED_ORIGINS` da to'liq origin (`http://IP`) yo'q. |
| Rasm 404 / optimizatsiya xato | `MEDIA_REWRITE_TARGET=http://nginx` va media volume tekshiring: `$C exec nginx ls /var/www/media`. |
| SSR bo'sh/eski content | backend healthy emas yoki seed qilinmagan (4-bo'lim). `$C logs backend`. |
| `DisallowedHost` | `ALLOWED_HOSTS` ga `backend`, `localhost`, IP kirganini tekshiring. |
| 400/500 booking/appointment | frontend build'da `NEXT_PUBLIC_API_URL` noto'g'ri (browser origin). Qayta build. |
