#!/usr/bin/env bash
# dental_demo — DB + media zaxira nusxasi. Cron'ga qo'yish mumkin (DEPLOY.md).
#   bash deploy/backup.sh            # → deploy/backups/ ga yozadi
#   BACKUP_DIR=/mnt/backups bash deploy/backup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE="deploy/.env.prod"
COMPOSE=(docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml)
BACKUP_DIR="${BACKUP_DIR:-deploy/backups}"
mkdir -p "$BACKUP_DIR"

# Timestamp'ni HOST beradi (skript ichida date OK — bu shell, workflow emas).
STAMP="$(date +%Y%m%d-%H%M%S)"
DB_USER="$(grep -E '^POSTGRES_USER=' "$ENV_FILE" | cut -d= -f2- || echo dental)"
DB_NAME="$(grep -E '^POSTGRES_DB=' "$ENV_FILE" | cut -d= -f2- || echo dental)"

echo "→ DB dump…"
"${COMPOSE[@]}" exec -T db pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_DIR/db-$STAMP.sql.gz"

echo "→ media arxiv…"
"${COMPOSE[@]}" run --rm --no-deps -T -v "$(pwd)/$BACKUP_DIR:/backup" backend \
  tar czf "/backup/media-$STAMP.tar.gz" -C /app media 2>/dev/null || \
  echo "  (media bo'sh yoki hali seed qilinmagan — o'tkazib yuborildi)"

echo "✓ Zaxira: $BACKUP_DIR/db-$STAMP.sql.gz"
# 14 kundan eski zaxiralarni tozalash
find "$BACKUP_DIR" -name 'db-*.sql.gz' -mtime +14 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name 'media-*.tar.gz' -mtime +14 -delete 2>/dev/null || true
