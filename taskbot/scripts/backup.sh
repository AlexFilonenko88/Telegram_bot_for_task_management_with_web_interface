#!/bin/bash
# =============================================================================
# backup.sh — автоматический бэкап PostgreSQL из Docker-контейнера (п.19).
#
# Проект: TaskBot (docker-compose из п.13), база — контейнер taskbot-db.
# pg_dump запускается ВНУТРИ контейнера, пароль не нужен: локальные
# подключения в postgres-контейнере доверенные (trust) по умолчанию.
#
# Установка на сервер (подробности — scripts/BACKUP.md):
#   sudo cp backup.sh /opt/backup.sh && sudo chmod +x /opt/backup.sh
#   sudo /opt/backup.sh                      # проверить вручную
#   crontab -e                               # каждая ночь в 3:00
#     0 3 * * * /opt/backup.sh >> /var/log/backup.log 2>&1
#
# Все настройки можно переопределить переменными окружения:
#   CONTAINER, BACKUP_DIR, KEEP_DAYS, ENV_FILE, RCLONE_REMOTE
#   POSTGRES_DB, POSTGRES_USER (по умолчанию читаются из .env проекта)
# =============================================================================

# -e: падать при первой ошибке; -u: необъявленная переменная — ошибка;
# -o pipefail: если pg_dump упал, а gzip "проглотил" — скрипт всё равно упадёт
# (без pipefail $? в конвейере = код ПОСЛЕДНЕЙ команды, и битый бэкап
# считался бы успешным).
set -euo pipefail

# --- Настройки -----------------------------------------------------------------

# Имя контейнера с PostgreSQL (container_name в docker-compose.yml).
CONTAINER="${CONTAINER:-taskbot-db}"

# Куда класть бэкапы (создаётся при отсутствии).
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgres}"

# Сколько дней хранить бэкапы (старше — удаляются).
KEEP_DAYS="${KEEP_DAYS:-7}"

# .env проекта с POSTGRES_DB / POSTGRES_USER (docker-compose читает его же).
# По умолчанию — .env рядом с docker-compose: <repo>/.env (скрипт в taskbot/scripts/).
ENV_FILE="${ENV_FILE:-$(cd "$(dirname "$0")/../.." && pwd)/.env}"

# Каталог в облачном хранилище для rclone (п.19, "если есть внешнее хранилище").
# Пусто — выгрузка в облако отключена. Пример: RCLONE_REMOTE=remote:my-backups/postgres
RCLONE_REMOTE="${RCLONE_REMOTE:-}"

# --- Чтение кредов из .env (без source: .env может содержать постороннее) -------

# grep-парсинг KEY=VALUE; `|| true` — отсутствие файла/ключа не роняет скрипт.
read_env() {
    grep -E "^$1=" "$ENV_FILE" 2>/dev/null | tail -n1 | cut -d= -f2- | tr -d '"' || true
}

DB_NAME="${POSTGRES_DB:-$(read_env POSTGRES_DB)}"
DB_USER="${POSTGRES_USER:-$(read_env POSTGRES_USER)}"
# Fallback, если .env не найден (креды по умолчанию из .env.example).
DB_NAME="${DB_NAME:-taskbot}"
DB_USER="${DB_USER:-taskbot}"

DATE="$(date +"%Y-%m-%d_%H-%M-%S")"
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz"

log()  { echo "$(date '+%Y-%m-%d %H:%M:%S') $*"; }
fail() {
    log "ERROR — $*" >&2
    # Алерт в Telegram (п.20): о сбое бэкапа надо узнать утром, а не когда
    # понадобится восстановление. Не настроен/упал — молча: backup важнее.
    "$(dirname "$0")/notify_telegram.sh" \
        "<b>TaskBot backup FAILED</b> на $(hostname): $*" > /dev/null 2>&1 || true
    exit 1
}

# --- Шаг 1: бэкап ----------------------------------------------------------------

mkdir -p "$BACKUP_DIR"

log "Бэкап $DB_NAME из контейнера $CONTAINER -> $BACKUP_FILE"

# docker exec: pg_dump внутри контейнера, вывод по конвейеру в gzip НА ХОСТЕ.
# pipefail гарантирует: код ошибки pg_dump не потеряется за gzip.
if ! docker exec "$CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    # Удаляем частичный/пустой файл, чтобы он не копился и не попал в облако.
    rm -f "$BACKUP_FILE"
    fail "бэкап не создан (pg_dump или gzip). Провери: docker ps, контейнер $CONTAINER, креды $ENV_FILE"
fi

# Пустой файл = битый бэкап: pg_dump может "успешно" вернуть 0 байт.
[ -s "$BACKUP_FILE" ] || fail "файл бэкапа пуст: $BACKUP_FILE"

log "OK — $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"

# --- Шаг 2: копия в облако (опционально, rclone) ---------------------------------

if [ -n "$RCLONE_REMOTE" ] && command -v rclone >/dev/null 2>&1; then
    # copy, а не sync: sync мог бы УДАЛИТЬ файлы в облаке, которых нет локально
    # (после чистки старых бэкапов облако лишилось бы и их).
    if rclone copy "$BACKUP_FILE" "$RCLONE_REMOTE"; then
        log "OK — копия в облако: $RCLONE_REMOTE"
    else
        # Облачная копия не удалась — это не повод ронять ночной бэкап:
        # локальная копия уже сохранена. Ошибка уйдёт в лог для разбора.
        log "WARNING — rclone copy не удался (локальный бэкап сохранён)" >&2
    fi
elif [ -n "$RCLONE_REMOTE" ]; then
    log "WARNING — RCLONE_REMOTE задан, но rclone не установлен" >&2
fi

# --- Шаг 3: ротация — удалить бэкапы старше KEEP_DAYS ----------------------------

# -mtime +7 = старше 7*24 часов; -name ограничивает только нашими файлами.
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime "+$KEEP_DAYS" -delete
log "OK — старые бэкапы (старше $KEEP_DAYS дней) удалены"

log "Готово."
