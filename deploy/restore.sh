#!/usr/bin/env bash
# dental_demo — zaxiradan tiklash (DB + media). `backup.sh` ning teskarisi; server ko'chirishda
# ham shu ishlatiladi (ADR-022).
#
#   bash deploy/restore.sh deploy/backups/db-20260923-030000.sql.gz \
#                          deploy/backups/media-20260923-030000.tar.gz
#   bash deploy/restore.sh _migration/db_dental.sql       # faqat DB (xom .sql ham bo'ladi)
#
# MUHIM: DB BO'SH bo'lishi kerak (yangi volume). Ustidan tiklash uchun avval:
#   $C down && docker volume rm dental_demo_pgdata     # ← MA'LUMOT O'CHADI
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DB_FILE="${1:-}"
MEDIA_FILE="${2:-}"
[ -n "$DB_FILE" ] || { echo "✗ Foydalanish: bash deploy/restore.sh <db.sql[.gz]> [media.tar.gz]"; exit 1; }
[ -f "$DB_FILE" ] || { echo "✗ topilmadi: $DB_FILE"; exit 1; }

ENV_FILE="deploy/.env.prod"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml)
DB_USER="$(grep -E '^POSTGRES_USER=' "$ENV_FILE" | cut -d= -f2- || echo dental)"
DB_NAME="$(grep -E '^POSTGRES_DB=' "$ENV_FILE" | cut -d= -f2- || echo dental)"

echo "→ db konteyneri…"
"${COMPOSE[@]}" up -d db
for _ in $(seq 1 40); do
  cid="$("${COMPOSE[@]}" ps -q db || true)"
  st="$(docker inspect -f '{{.State.Health.Status}}' "$cid" 2>/dev/null || echo starting)"
  [ "$st" = healthy ] && break
  sleep 2
done
sleep 3   # healthcheck o'tgach ham initdb qayta ishga tushadi — socket tayyor bo'lsin
echo "  db: ${st:-?}"

existing="$("${COMPOSE[@]}" exec -T db psql -U "$DB_USER" -d "$DB_NAME" -Atc \
  "select count(*) from information_schema.tables where table_schema='public'" 2>/dev/null || echo 0)"
if [ "${existing:-0}" -gt 0 ]; then
  echo "✗ '$DB_NAME' bo'sh emas ($existing jadval). Ustidan tiklash ma'lumotni buzadi."
  echo "  Ataylab qilmoqchi bo'lsangiz: ${COMPOSE[*]} down && docker volume rm dental_demo_pgdata"
  exit 1
fi

echo "→ DB tiklash: $DB_FILE"
case "$DB_FILE" in
  *.gz) gunzip -c "$DB_FILE" ;;
  *)    cat "$DB_FILE" ;;
esac | "${COMPOSE[@]}" exec -T db psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" >/dev/null
echo "  ✓ $("${COMPOSE[@]}" exec -T db psql -U "$DB_USER" -d "$DB_NAME" -Atc \
      "select count(*) from information_schema.tables where table_schema='public'") jadval tiklandi"

if [ -n "$MEDIA_FILE" ]; then
  [ -f "$MEDIA_FILE" ] || { echo "✗ topilmadi: $MEDIA_FILE"; exit 1; }
  echo "→ media tiklash: $MEDIA_FILE"
  # Arxiv ikki xil bo'lishi mumkin: ichida "media/" papkasi (backup.sh) yoki to'g'ridan-to'g'ri
  # fayllar (volume'dan olingan). Ikkalasini ham to'g'ri joyga yoyamiz.
  vol="$(docker volume ls -q | grep -E '(^|_)media$' | head -1)"
  [ -n "$vol" ] || { echo "✗ media volume topilmadi — avval '${COMPOSE[*]} up -d' qiling"; exit 1; }
  if tar tzf "$MEDIA_FILE" | head -1 | grep -q '^media/'; then STRIP=1; else STRIP=0; fi
  docker run --rm -v "$vol:/m" -v "$(cd "$(dirname "$MEDIA_FILE")" && pwd):/b:ro" alpine \
    tar xzf "/b/$(basename "$MEDIA_FILE")" -C /m --strip-components="$STRIP"
  echo "  ✓ $(docker run --rm -v "$vol:/m" alpine sh -c 'find /m -type f | wc -l') fayl"
fi

echo "✓ Tiklandi. Endi: bash deploy/deploy.sh"
