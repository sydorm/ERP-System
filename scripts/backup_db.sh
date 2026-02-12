#!/bin/bash

# Configuration
CONTAINER_NAME="erp_postgres"
DB_USER="erp_user"
DB_NAME="erp_db"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup
echo "Creating backup of $DB_NAME to $BACKUP_FILE..."
docker exec -t $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "✅ Backup created successfully: $BACKUP_FILE"
else
  echo "❌ Backup failed!"
  exit 1
fi
