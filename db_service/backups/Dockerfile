FROM alpine:3.19

RUN apk add --no-cache bash curl zip docker-cli

WORKDIR /backups

COPY backup_db.sh /backups/backup_db.sh
COPY crontab.txt /etc/crontabs/root

RUN chmod +x /backups/backup_db.sh

CMD ["crond", "-f", "-d", "8"] 