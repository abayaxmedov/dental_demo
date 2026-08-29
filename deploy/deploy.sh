#!/usr/bin/env bash
# dental_demo — bir buyruqli deploy (ADR-021). Idempotent: build + up + migrate(entrypoint) + warm.
# Content'ni ATAYLAB seed QILMAYDI (ma'lumotni qayta yozmaslik uchun) — birinchi deploy'da
# DEPLOY.md dagi seed qadamini QO'LDA bajaring.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE="deploy/.env.prod"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml)

[ -f "$ENV_FILE" ] || {
  echo "✗ $ENV_FILE topilmadi."
  echo "  cp deploy/.env.prod.example $ENV_FILE   # so'ng haqiqiy qiymatlar bilan to'ldiring"
  exit 1
}
# Placeholder qolib ketmasin (jimgina buzuq deploy oldini olish).
if grep -qE 'REPLACE_' "$ENV_FILE"; then
  echo "✗ $ENV_FILE hali REPLACE_… placeholder'lar bilan. Haqiqiy sirlarni yozing:"
  grep -nE 'REPLACE_' "$ENV_FILE" | sed 's/^/    /'
  exit 1
fi

echo "→ build + up…"
"${COMPOSE[@]}" up -d --build

echo "→ backend 'healthy' bo'lishini kutish…"
status=starting
for _ in $(seq 1 40); do
  cid="$("${COMPOSE[@]}" ps -q backend || true)"
  [ -n "$cid" ] && status="$(docker inspect -f '{{.State.Health.Status}}' "$cid" 2>/dev/null || echo starting)"
  [ "$status" = "healthy" ] && break
  sleep 3
done
echo "  backend: $status"
[ "$status" = "healthy" ] || { echo "⚠ backend healthy emas — loglar: ${COMPOSE[*]} logs backend"; }

echo "→ ISR keshini tozalash + qizdirish…"
SECRET="$(grep -E '^REVALIDATE_SECRET=' "$ENV_FILE" | cut -d= -f2- || true)"
BASE="http://localhost"
if [ -n "$SECRET" ]; then
  code="$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/api/revalidate" \
    -H "x-revalidate-secret: $SECRET" --max-time 20 || echo 000)"
  echo "  purge: HTTP $code"
fi
for path in /uz /uz/narxlar /uz/xizmatlar /uz/haqimizda /uz/aloqa /uz/galereya /uz/blog /ru /en; do
  curl -s -o /dev/null "$BASE$path" --max-time 25 || true
done

echo "✓ Deploy tugadi. Ochish: http://<server-ip>/"
echo "  Loglar:   ${COMPOSE[*]} logs -f"
echo "  Holat:    ${COMPOSE[*]} ps"
