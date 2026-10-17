#!/usr/bin/env bash
# Apply pending SQL migrations from migrations/*.sql, in name order, once each.
# Needs DATABASE_URL (Supabase → Project Settings → Database → Connection string,
# "Session pooler", port 5432) in the environment or in backend/.env, and psql.
#
#   scripts/migrate.sh            apply pending migrations
#   scripts/migrate.sh --status   list applied / pending
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ -z "${DATABASE_URL:-}" && -f .env ]]; then
  DATABASE_URL=$(grep -E '^DATABASE_URL=' .env | head -1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//')
fi
[[ -n "${DATABASE_URL:-}" ]] || { echo "DATABASE_URL is not set (env or backend/.env)" >&2; exit 1; }
command -v psql >/dev/null || { echo "psql not found. Install: apt install postgresql-client (or brew install libpq)" >&2; exit 1; }

PSQL=(psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -X)
"${PSQL[@]}" -c "create table if not exists schema_migrations (name text primary key, applied_at timestamptz not null default now())"
applied=$("${PSQL[@]}" -t -A -c "select name from schema_migrations")

pending=0
for file in migrations/*.sql; do
  name=$(basename "$file")
  if grep -qx "$name" <<<"$applied"; then
    [[ "${1:-}" == "--status" ]] && echo "  applied  $name"
    continue
  fi
  pending=$((pending + 1))
  if [[ "${1:-}" == "--status" ]]; then
    echo "  pending  $name"
    continue
  fi
  echo "→ applying $name"
  "${PSQL[@]}" --single-transaction -f "$file" \
    -c "insert into schema_migrations (name) values ('$name')"
done

if [[ "${1:-}" != "--status" ]]; then
  [[ $pending -eq 0 ]] && echo "Database is up to date." || echo "Applied $pending migration(s)."
fi
