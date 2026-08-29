#!/usr/bin/env bash
# Backend konteyner start — migratsiya (idempotent), keyin CMD (gunicorn).
# Seed/reskin ATAYLAB bu yerda EMAS: har restartda content'ni qayta yozib yubormaslik uchun.
# Ularni birinchi deploy'da qo'lda ishga tushirasiz (DEPLOY.md).
set -euo pipefail

echo "→ migrate…"
python manage.py migrate --noinput

exec "$@"
