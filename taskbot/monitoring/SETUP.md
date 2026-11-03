# Централизованный сбор логов: Loki + Promtail + Grafana (п.17)

Все контейнеры проекта (app, db, loki, promtail, grafana...) пишут логи в
Loki; смотреть их в одном месте — в Grafana: **http://localhost:3000**.

Как это работает:

```
контейнеры (docker logs) ──> Promtail (docker service discovery)
                                  │  push
                                  v
                              Loki (хранение, retention 7 дней)
                                  │  query
                                  v
                              Grafana (Explore, дашборды)
```

## Запуск

```bash
cd taskbot
docker compose up -d
docker compose ps          # все 5 сервисов должны быть Up (loki — healthy/started)
```

## Подключение Loki к Grafana

### Вариант 1 — автоматически (уже настроено)

Datasource подключается при первом старте через provisioning:
`monitoring/grafana/provisioning/datasources/loki.yml` монтируется в
`/etc/grafana/provisioning/datasources/`, и Grafana сама регистрирует
Loki (`http://loki:3100`) как datasource по умолчанию.

Проверка: Grafana → **Connections → Data sources** — должен быть Loki
со статусом зелёной галочкой.

### Вариант 2 — вручную через UI (если provisioning не используется)

1. Открой http://localhost:3000, войди `admin` / `admin` (сменить пароль).
2. **Connections → Data sources → Add data source → Loki**.
3. URL: `http://loki:3100` — имя сервиса из docker-compose, не localhost
   (Grafana живёт в сети tasknet и ходит в Loki по имени сервиса).
4. **Save & test** — должно появиться «Successfully queried the Loki API».

## Просмотр логов

Grafana → **Explore → Loki**. Примеры LogQL:

```logql
# Все логи всех контейнеров
{compose_project="taskbot"}

# Логи конкретного сервиса (метки из relabel_configs в promtail-config.yml)
{service="app"}

# Только ошибки stderr
{service="app", stream="stderr"}

# Строки с ошибками за последние 2 часа
{service="app"} |= "ERROR"

# Частота ошибок по минутам (для графика)
rate({service="app"} |= "ERROR" [1m])
```

## Ротация файлов логов на хосте

Promtail читает файлы из `/var/lib/docker/containers` — без ротации они
растут бесконечно. Docker сам ограничивает их через драйвер json-file.
Чтобы не добавлять `logging:` в каждый сервис, можно задать дефолт в
`/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```

После изменения: `sudo systemctl restart docker` (действует на НОВЫЕ
контейнеры — пересоздать через `docker compose up -d --force-recreate`).

## Полезные команды

```bash
docker compose logs loki promtail   # статус самого стека логирования
docker compose logs -f app          # обычный docker logs продолжает работать
```

Заметки:
- Loki не публикует порт 3100 наружу — доступ только из сети tasknet.
- Логи хранятся 7 дней (`retention_period: 168h` в loki-config.yml).
- Дашборды и настройки Grafana живут в volume `grafana-data`.
