#!/bin/bash
set -e

# Configuration
BACKUP_DIR="$(dirname "$0")"
CONTAINER_NAME="deal_app_db"
DB_USER="deals_user"
RETENTION_DAYS=30  # Keep backups for 30 days
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"
ZIP_FILE="$BACKUP_DIR/db_backup_$DATE.zip"
LOG_FILE="$BACKUP_DIR/backup.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log "ERROR: $1"
    exit 1
}

# Check if container exists
if ! docker ps -a | grep -q $CONTAINER_NAME; then
    handle_error "Container $CONTAINER_NAME not found"
fi

# Check if container is running
if ! docker ps | grep -q $CONTAINER_NAME; then
    handle_error "Container $CONTAINER_NAME is not running"
fi

log "Starting database backup..."

# Run pg_dumpall inside the container
if ! docker exec $CONTAINER_NAME pg_dumpall -U $DB_USER > "$BACKUP_FILE"; then
    handle_error "Failed to create database dump"
fi

# Check if dump file was created and has content
if [ ! -s "$BACKUP_FILE" ]; then
    handle_error "Backup file is empty"
fi

# Zip the backup
if ! zip -j "$ZIP_FILE" "$BACKUP_FILE"; then
    handle_error "Failed to compress backup file"
fi

# Remove the SQL file after successful compression
rm "$BACKUP_FILE"

# Cleanup old backups
find "$BACKUP_DIR" -name "db_backup_*.zip" -type f -mtime +$RETENTION_DAYS -delete

log "Backup completed successfully: $ZIP_FILE"
log "Backup size: $(du -h "$ZIP_FILE" | cut -f1)" 