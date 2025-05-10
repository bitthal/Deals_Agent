# Database Backup System

This directory contains the automated database backup system for the Deals Agent application.

## Components

- `backup_db.sh`: Main backup script that creates SQL dumps and compresses them
- `Dockerfile`: Container configuration for the backup service
- `crontab.txt`: Cron schedule configuration for automated backups

## Backup Schedule

- Backups run automatically every Sunday at 3:00 AM
- Each backup is stored as a compressed ZIP file
- Backup files are named with timestamp: `db_backup_YYYY-MM-DD_HH-MM-SS.zip`

## Manual Backup

To create a manual backup:

```bash
./backup_db.sh
```

## Backup Retention

- Backups are stored in the `./backups` directory
- It's recommended to implement a retention policy to manage disk space
- Consider moving older backups to long-term storage

## Configuration

The backup system uses the following environment variables:
- `CONTAINER_NAME`: Name of the PostgreSQL container (default: deal_app_db)
- `POSTGRES_USER`: Database user (default: deals_user)

## Logs

- Backup logs are stored in `/backups/cron.log`
- Each backup operation is logged with timestamp and status 