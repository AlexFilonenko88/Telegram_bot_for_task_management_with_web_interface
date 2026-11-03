# Мониторинг: логи (Loki) и метрики сервера (Prometheus) в Grafana

Все контейнеры проекта (app, db, loki, promtail, grafana...) пишут логи в
Loki (п.17); метрики сервера (CPU/RAM/диск/сеть) собирает Prometheus через
node-exporter (п.18). Смотреть и то и другое — в Grafana:
**http://localhost:3000** (порт 3000 — Grafana из п.17, переиспользуется).

Как это работает:

```
контейнеры (docker logs) ──> Promtail (docker service discovery)
                                  │  push
                                  v
                              Loki (хранение, retention 7 дней) ──┐
                                                                  ├──> Grafana :3000
сервер /proc /sys ──> node-exporter (:9100/metrics)               │
                        │ scrape каждые 15с                       │
                        v                                         │
                     Prometheus (volume prometheus-data) ─────────┘
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

## Метрики сервера: Prometheus + node-exporter (п.18)

Datasource Prometheus подключается автоматически так же, как Loki
(`monitoring/grafana/provisioning/datasources/prometheus.yml`).

Проверка вручную: Grafana → **Connections → Data sources → Prometheus →
Save & test**. Проверка самого Prometheus: http://localhost:9090/targets —
здесь его смотреть можно, но на проде порт 9090 наружу не публикуется.

node-exporter монтирует `/proc`, `/sys` и `/` хоста **только на чтение** —
иначе из контейнера не видно реальные ресурсы машины. Это официальный
способ запуска node-exporter (см. комментарии в docker-compose.yml).

### Полезные PromQL-запросы (Grafana → Explore → Prometheus)

```promql
# Загрузка CPU в процентах (усреднённо по всем ядрам)
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Занятая RAM в процентах
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Свободное место на диске (корень)
node_filesystem_avail_bytes{mountpoint="/", fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes{mountpoint="/"} * 100

# Сетевой трафик (байт/сек)
rate(node_network_receive_bytes_total{device="eth0"}[5m])
```

Готовый дашборд: в Grafana → Dashboards → Import, ID **1860**
(Node Exporter Full) — самый популярный дашборд для node-exporter.

## Полезные команды

```bash
docker compose logs loki promtail   # статус самого стека логирования
docker compose logs -f app          # обычный docker logs продолжает работать
```

Заметки:
- Loki (3100) и Prometheus (9090) не публикуют порты наружу — доступ только
  из сети tasknet, данные смотрим через Grafana :3000.
- Логи хранятся 7 дней (`retention_period: 168h` в loki-config.yml).
- Метрики Prometheus и дашборды Grafana живут в volume `prometheus-data`
  и `grafana-data` — переживают перезапуск контейнеров.
