#!/usr/bin/env bash
# Run WMS locally: backend (http://localhost:8000) + frontend (http://localhost:5173)
# in one terminal. Ctrl+C stops both.
#
#   ./run-local.sh            start (installs dependencies when they changed)
#   ./run-local.sh --test     run backend tests + frontend type-check, then exit
#   ./run-local.sh --migrate  apply pending database migrations, then start
#
# Note: local and production use the same Supabase project unless backend/.env
# points elsewhere — be careful with data you create while testing.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
BACKEND="$ROOT/wms/backend"
FRONTEND="$ROOT/wms/frontend/ui"
API_PORT=${API_PORT:-8000}
WEB_PORT=${WEB_PORT:-5173}

say()  { printf '\033[36m▸\033[0m %s\n' "$*"; }
fail() { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; exit 1; }
hash_of() { shasum "$1" | cut -d' ' -f1; }

# ── Prerequisites ─────────────────────────────────────────────────────────────
PYTHON=$(command -v python3.12 || command -v python3 || true)
[[ -n "$PYTHON" ]] || fail "Python 3.12 not found (brew install python@3.12)"
command -v npm >/dev/null || fail "Node.js not found (brew install node)"
[[ -f "$BACKEND/.env" ]] || fail "Missing wms/backend/.env — copy wms/backend/.env.example and fill it in"

# ── Backend dependencies ──────────────────────────────────────────────────────
if [[ ! -x "$BACKEND/venv/bin/python" ]]; then
  say "Creating Python virtualenv (wms/backend/venv)"
  "$PYTHON" -m venv "$BACKEND/venv"
fi
REQ_HASH="$(cat "$BACKEND/requirements.txt" "$BACKEND/requirements-dev.txt" | shasum | cut -d' ' -f1)"
if [[ "$(cat "$BACKEND/venv/.req-hash" 2>/dev/null)" != "$REQ_HASH" ]]; then
  say "Installing Python packages"
  "$BACKEND/venv/bin/python" -m pip install -q --upgrade pip
  "$BACKEND/venv/bin/python" -m pip install -q -r "$BACKEND/requirements-dev.txt"
  echo "$REQ_HASH" > "$BACKEND/venv/.req-hash"
fi

# ── Frontend dependencies ─────────────────────────────────────────────────────
LOCK_HASH=$(hash_of "$FRONTEND/package-lock.json")
if [[ "$(cat "$FRONTEND/node_modules/.lock-hash" 2>/dev/null)" != "$LOCK_HASH" ]]; then
  say "Installing npm packages"
  (cd "$FRONTEND" && npm ci --silent)
  echo "$LOCK_HASH" > "$FRONTEND/node_modules/.lock-hash"
fi
grep -q "^VITE_API_URL=http://localhost:$API_PORT/api$" "$FRONTEND/.env.local" 2>/dev/null \
  || echo "VITE_API_URL=http://localhost:$API_PORT/api" > "$FRONTEND/.env.local"

# ── Modes ─────────────────────────────────────────────────────────────────────
case "${1:-}" in
  --test)
    say "Backend tests";  (cd "$BACKEND" && venv/bin/python -m pytest -q)
    say "Frontend types"; (cd "$FRONTEND" && npx vue-tsc --build)
    say "All good"; exit 0 ;;
  --migrate)
    say "Database migrations"; "$BACKEND/scripts/migrate.sh" ;;
  "") ;;
  *) fail "Unknown option $1 (use --test or --migrate)" ;;
esac

# ── Run both, with prefixed output ────────────────────────────────────────────
prefix() { awk -v p="$1" '{ print p $0; fflush() }'; }
# Stop every process this script started (uvicorn's reloader and vite spawn children)
kill_tree() { local c; for c in $(pgrep -P "$1" 2>/dev/null); do kill_tree "$c"; done; kill "$1" 2>/dev/null || true; }
cleanup() { trap - INT TERM EXIT; for c in $(pgrep -P $$ 2>/dev/null); do kill_tree "$c"; done; }
trap cleanup INT TERM EXIT

say "API  → http://localhost:$API_PORT/docs"
say "App  → http://localhost:$WEB_PORT"
(cd "$BACKEND" && exec venv/bin/uvicorn main:app --reload --port "$API_PORT" 2>&1) | prefix $'\033[35mapi │\033[0m ' &
(cd "$FRONTEND" && exec npx vite --port "$WEB_PORT" --strictPort 2>&1) | prefix $'\033[32mweb │\033[0m ' &

# Exit as soon as either side stops (bash 3.2 on macOS has no `wait -n`)
while sleep 1; do
  [[ $(jobs -r | wc -l) -ge 2 ]] || { say "A process stopped — shutting down"; break; }
done
