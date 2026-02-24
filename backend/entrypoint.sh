#!/bin/bash
set -e

# Wait for database to be ready (optional but recommended)
echo "Waiting for database..."
# Use postgres-client to check connectivity if needed
# while ! pg_isready -h postgres -p 5432 -U erp_user; do
#   sleep 1
# done

# Run migrations (auto-merge heads if multiple exist)
echo "Running migrations..."
HEADS=$(alembic heads 2>&1 | grep -c "(head)")
if [ "$HEADS" -gt "1" ]; then
  echo "Multiple heads detected ($HEADS), merging..."
  alembic merge heads -m "auto_merge" --rev-id "auto_merge_$(date +%s)"
fi
alembic upgrade head

# Create sample data (if needed and tables are empty)
# python app/db/create_sample_data.py

# Start application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
