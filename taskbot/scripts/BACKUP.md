# Бэкап PostgreSQL: скрипт + cron (п.19)

`backup.sh` — nightly-бэкап базы TaskBot. PostgreSQL живёт в контейнере
`taskbot-db` (docker-compose из п.13), поэтому pg_dump запускается через
`docker exec` — по аналогии со скриптом из задания, но под наш проект.

Что делает скрипт (по шагам в самом файле, с комментариями):

1. читает `POSTGRES_DB` / `POSTGRES_USER` из `.env` проекта (grep-парсингом,
   без `source` — в .env есть и другие переменные);
2. `docker exec taskbot-db pg_dump ... | gzip > /var/backups/postgres/<db>_<дата>.sql.gz`;
3. проверяет, что файл не пустой (pg_dump может «успешно» вернуть 0 байт);
4. опционально копирует бэкап в облако через rclone;
5. удаляет бэкапы старше 7 дней (`find -mtime +7 -delete`).

`set -euo pipefail` — ключевое: без `pipefail` код ошибки pg_dump теряется
за gzip, и битый бэкап считался бы успешным.

## Установка на сервер

```bash
# из корня репозитория
sudo cp taskbot/scripts/backup.sh /opt/backup.sh
sudo chmod +x /opt/backup.sh
```

Скрипт сам находит `.env` проекта по своему пути (`taskbot/scripts/../../.env`),
поэтому при копировании в `/opt` задай `ENV_FILE` явно (см. cron ниже) или
переопредели креды: `POSTGRES_DB`/`POSTGRES_USER` в окружении имеют приоритет.

## Проверка вручную (обязательный шаг)

```bash
sudo /opt/backup.sh

# файл создался и не пустой?
ls -lh /var/backups/postgres/
```

### Проверка восстановления (на тестовой БД!)

Бэкап, который ни разу не восстанавливали, — это не бэкап. Проверяем в
тестовую базу, не в боевую:

```bash
# создаём тестовую базу внутри контейнера
docker exec taskbot-db psql -U taskbot -c "CREATE DATABASE taskbot_restore_test;"

# заливаем последний бэкап (zcat распаковывает, psql принимает поток)
ls -t /var/backups/postgres/*.sql.gz | head -1 | \
    xargs -I{} zcat {} | docker exec -i taskbot-db psql -U taskbot -d taskbot_restore_test

# смотрим, что данные на месте (кол-во задач/юзеров)
docker exec taskbot-db psql -U taskbot -d taskbot_restore_test -c "\dt"
docker exec taskbot-db psql -U taskbot -d taskbot_restore_test \
    -c "SELECT count(*) FROM tasks;"

# чистим тестовую базу
docker exec taskbot-db psql -U taskbot -c "DROP DATABASE taskbot_restore_test;"
```

## Cron: запуск каждую ночь в 3:00

```bash
sudo chmod +x /opt/backup.sh     # если ещё не делали
crontab -e
```

Строка (для root, чтобы был доступ к docker; лог — в файл, stderr тоже):

```
0 3 * * * ENV_FILE=/home/deploy/myapp/.env /opt/backup.sh >> /var/log/backup.log 2>&1
```

Проверка после первой ночи: `tail /var/log/backup.log` — строка `OK — ...`
и `Готово.`, в `/var/backups/postgres/` — свежий файл.

## Выгрузка в облачное хранилище (rclone, опционально)

Правило 3-2-1 (см. п.20): минимум одна копия вне сервера.

```bash
# установка
curl https://rclone.org/install.sh | sudo bash

# интерактивная настройка провайдера (S3 / Yandex Object Storage / B2 ...)
rclone config

# проверка вручную
RCLONE_REMOTE=remote:my-backups-bucket/postgres /opt/backup.sh
```

В cron — тем же способом:

```
0 3 * * * ENV_FILE=/home/deploy/myapp/.env RCLONE_REMOTE=remote:my-backups-bucket/postgres /opt/backup.sh >> /var/log/backup.log 2>&1
```

Используется `rclone copy` (не `sync`): sync после локальной чистки удалил бы
старые копии и из облака — облако хранит историю дольше, чем сервер.

## Настройки скрипта (переменные окружения)

| Переменная | По умолчанию | Что делает |
|---|---|---|
| `CONTAINER` | `taskbot-db` | имя контейнера PostgreSQL |
| `BACKUP_DIR` | `/var/backups/postgres` | куда класть бэкапы |
| `KEEP_DAYS` | `7` | срок хранения локальных бэкапов |
| `ENV_FILE` | `<repo>/.env` (по пути скрипта) | где брать креды БД |
| `RCLONE_REMOTE` | пусто | `remote:bucket/path` — включает копию в облако |
| `POSTGRES_DB` / `POSTGRES_USER` | из `.env` | креды БД (фолбэк: `taskbot`) |
