#!/usr/bin/env bash
# ISR keshini tozalab, asosiy sahifalarni oldindan qizdiradi (AUDIT-2026-08-29 / T-FIX-02).
#
# Nega: barcha server fetch'lar `revalidate: 300` bilan keshlanadi. Deploy yoki `reskin`
# dan keyin birinchi tashrifchi (koʻpincha prospektning oʻzi, QR orqali) sovuq render
# kutadi. Bu skript avval purge qiladi, soʻng sahifalarni chaqirib keshni toʻldiradi.
#
# Ishlatish:  make warm
# Muhit:      FRONTEND_BASE_URL (default http://127.0.0.1:3000), REVALIDATE_SECRET
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# backend/.env dan qiymatlarni olamiz (muhitda boʻlsa — muhit ustun).
if [ -f "$ROOT/backend/.env" ]; then
  while IFS='=' read -r key val; do
    case "$key" in
      FRONTEND_BASE_URL) [ -z "${FRONTEND_BASE_URL:-}" ] && FRONTEND_BASE_URL="$val" ;;
      REVALIDATE_SECRET) [ -z "${REVALIDATE_SECRET:-}" ] && REVALIDATE_SECRET="$val" ;;
    esac
  done < <(grep -E '^(FRONTEND_BASE_URL|REVALIDATE_SECRET)=' "$ROOT/backend/.env" 2>/dev/null || true)
fi

BASE="${FRONTEND_BASE_URL:-http://127.0.0.1:3000}"
BASE="${BASE%/}"
SECRET="${REVALIDATE_SECRET:-}"

if [ -n "$SECRET" ]; then
  code=$(curl -s -o /tmp/warm-revalidate.json -w '%{http_code}' --max-time 10 \
    -X POST "$BASE/api/revalidate" -H "x-revalidate-secret: $SECRET" || echo 000)
  if [ "$code" = "200" ]; then
    echo "✓ ISR keshi tozalandi"
  else
    echo "⚠ Purge ishlamadi (HTTP $code) — faqat qizdirish bilan davom etamiz"
  fi
else
  echo "⚠ REVALIDATE_SECRET yoʻq — purge oʻtkazib yuborildi, faqat qizdiramiz"
fi

# Uch tilda eng koʻp ochiladigan yoʻllar (bosh sahifa + pul yoʻli + sotuv sahifalari).
PATHS_UZ="/uz /uz/xizmatlar /uz/narxlar /uz/shifokorlar /uz/ishlarimiz /uz/sharhlar /uz/aloqa"
PATHS_RU="/ru /ru/uslugi /ru/tseny /ru/vrachi"
PATHS_EN="/en /en/services /en/prices /en/doctors"

fail=0
for p in $PATHS_UZ $PATHS_RU $PATHS_EN; do
  start=$(date +%s%N 2>/dev/null || echo 0)
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 25 "$BASE$p" || echo 000)
  end=$(date +%s%N 2>/dev/null || echo 0)
  ms=$(( (end - start) / 1000000 ))
  if [ "$code" = "200" ]; then
    printf '  ✓ %-22s %sms\n' "$p" "$ms"
  else
    printf '  ✗ %-22s HTTP %s\n' "$p" "$code"
    fail=1
  fi
done

[ "$fail" = "0" ] && echo "✓ Qizdirish tugadi — birinchi tashrif issiq keshdan keladi" \
                  || { echo "✗ Baʼzi sahifalar qizimadi"; exit 1; }
