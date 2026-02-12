#!/bin/bash

# Configuration
CONTAINER_NAME="erp_postgres"
DB_USER="erp_user"
DB_NAME="erp_db"

if [ -z "$1" ]; then
  echo "Usage: ./restore_db.sh <backup_file.sql>"
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "❌ File not found: $BACKUP_FILE"
  exit 1
fi

echo "⚠️  WARNING: This will overwrite the current database '$DB_NAME'."
read -p "Are you sure? (y/N): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Operation cancelled."
  exit 0
fi

echo "Restoring $DB_NAME from $BACKUP_FILE..."

# Drop and recreate (optional, or just pass to psql)
# Usually pg_restore is for binary format, psql for sql format
cat "$BACKUP_FILE" | docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME

if [ $? -eq 0 ]; then
  echo "✅ Restore completed successfully."
else
  echo "❌ Restore failed!"
  exit 1
fi
