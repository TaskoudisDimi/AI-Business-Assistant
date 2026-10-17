#!/usr/bin/env bash
# Nightly backup: database (public + auth schemas) and uploaded dataset files.
# Keeps BACKUP_KEEP_DAYS (default 14) days of backups in BACKUP_DIR (default /var/backups/wms).
# Needs DATABASE_URL in backend/.env and a pg_dump at least as new as the Supabase
# Postgres major version (check: pg_dump --version vs Supabase → Settings → Infrastructure).
set -euo pipefail
cd "$(dirname "$0")/.."

BACKUP_DIR=${BACKUP_DIR:-/var/backups/wms}
KEEP=${BACKUP_KEEP_DAYS:-14}
if [[ -z "${DATABASE_URL:-}" && -f .env ]]; then
  DATABASE_URL=$(grep -E '^DATABASE_URL=' .env | head -1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
fi
[[ -n "${DATABASE_URL:-}" ]] || { echo "DATABASE_URL is not set" >&2; exit 1; }

stamp=$(date -u +%Y%m%d-%H%M)
mkdir -p "$BACKUP_DIR"
umask 077   # backups contain personal data: owner-only

echo "→ database"
pg_dump "$DATABASE_URL" --format=custom --no-owner --no-privileges \
  --schema=public --schema=auth --file="$BACKUP_DIR/db-$stamp.dump"

echo "→ dataset files"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
PY=venv/bin/python; [[ -x $PY ]] || PY=python3
"$PY" scripts/backup_storage.py "$tmp/storage"
tar -czf "$BACKUP_DIR/storage-$stamp.tar.gz" -C "$tmp" storage

echo "→ removing backups older than $KEEP days"
find "$BACKUP_DIR" -maxdepth 1 -type f \( -name 'db-*.dump' -o -name 'storage-*.tar.gz' \) -mtime "+$KEEP" -delete

ls -lh "$BACKUP_DIR" | tail -n 4
echo "Backup done: $BACKUP_DIR/*-$stamp.*"
# Restore (into an empty project): pg_restore --no-owner --dbname "$DATABASE_URL" db-<stamp>.dump
