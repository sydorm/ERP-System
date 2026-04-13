#!/bin/bash
set -e

# Wait for database to be ready with timeout
echo "Waiting for database (postgres:5432)..."
MAX_RETRIES=30
RETRY_COUNT=0

until pg_isready -h postgres -p 5432 -U erp_user || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
  echo "Postgres is unavailable - sleeping ($RETRY_COUNT/$MAX_RETRIES)"
  RETRY_COUNT=$((RETRY_COUNT + 1))
  sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "❌ Error: Could not connect to Postgres after $MAX_RETRIES seconds. Exiting."
  exit 1
fi

echo "✅ Database is ready!"

# Якщо ми запускаємо бекенд (uvicorn), тоді робимо міграції
if [[ "$*" == *"uvicorn"* ]] || [ -z "$1" ]; then
  echo "Running migrations..."
  # Auto-merge heads if multiple exist
  HEAD_COUNT=$(alembic heads 2>&1 | grep -c "(head)")
  if [ "$HEAD_COUNT" -gt "1" ]; then
    echo "Multiple heads detected ($HEAD_COUNT), merging..."
    alembic merge heads -m "auto_merge" --rev-id "auto_merge_$(date +%s)" || true
  fi
  alembic upgrade head || echo "Migration failed, but trying to start app anyway..."
fi

# Виконати передану команду (наприклад, alembic stamp)
if [ -n "$1" ]; then
  echo "Executing command: $@"
  exec "$@"
else
  echo "Starting application..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi
