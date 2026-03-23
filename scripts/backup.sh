#!/bin/bash
# Daily backup script for Odoo production
# Add to cron: 0 2 * * * /path/to/scripts/backup.sh

COMPOSE_FILE="$(dirname "$0")/../docker-compose.prod.yml"
BACKUP_DIR="/backups/odoo"
KEEP_DAYS=7

mkdir -p "$BACKUP_DIR"

DATE=$(date +%F)

# Backup database
docker compose -f "$COMPOSE_FILE" exec -T db \
  pg_dump -U odoo production | gzip > "$BACKUP_DIR/db_${DATE}.sql.gz"

# Backup filestore
docker compose -f "$COMPOSE_FILE" exec -T odoo \
  tar czf - /var/lib/odoo/filestore > "$BACKUP_DIR/filestore_${DATE}.tar.gz"

# Remove old backups
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR" -name "filestore_*.tar.gz" -mtime +$KEEP_DAYS -delete

echo "Backup completed: $DATE"
