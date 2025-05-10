#!/bin/bash
set -e

# This script should be run from the host, not inside the container.
# It will exec into the db container and run pg_dumpall, then zip the output.

BACKUP_DIR="$(dirname "$0")"
CONTAINER_NAME="deal_app_db"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"
ZIP_FILE="$BACKUP_DIR/db_backup_$DATE.zip"

# Run pg_dumpall inside the container
# You may need to adjust -U user if you change the DB user

docker exec $CONTAINER_NAME pg_dumpall -U deals_user > "$BACKUP_FILE"

# Zip the backup
zip -j "$ZIP_FILE" "$BACKUP_FILE"
rm "$BACKUP_FILE"

echo "Backup complete: $ZIP_FILE" 