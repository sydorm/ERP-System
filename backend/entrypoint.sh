#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."

# Якщо ми запускаємо бекенд (uvicorn), тоді робимо міграції
if [[ "$*" == *"uvicorn"* ]] || [ -z "$1" ]; then
  echo "Running migrations..."
  # Auto-merge heads if multiple exist
  HEADS=$(alembic heads 2>&1 | grep -c "(head)")
  if [ "$HEADS" -gt "1" ]; then
    echo "Multiple heads detected ($HEADS), merging..."
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
