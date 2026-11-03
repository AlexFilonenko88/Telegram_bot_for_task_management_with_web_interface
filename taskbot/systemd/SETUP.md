# Автозапуск docker compose через systemd

Юнит: `taskbot.service` (рядом с этим файлом). Приложение — в
`/home/deploy/myapp` (docker-compose.yml из п.13 + .env).

> Предусловие: на сервере должны быть установлены docker и docker compose
> плагин (п.11) и проект разложен по пути `/home/deploy/myapp`.

## 1. Установка юнита

```bash
# копируем юнит в каталог systemd
sudo cp systemd/taskbot.service /etc/systemd/system/taskbot.service

# перечитываем юниты после добавления нового файла
sudo systemctl daemon-reload
```

## 2. Включение автозапуска и старт сейчас

```bash
# enable — автозапуск при загрузке; --now — запустить сразу, не дожидаясь ребута
sudo systemctl enable --now taskbot.service
```

## 3. Проверка

```bash
# статус: active (exited) — норма для Type=oneshot с RemainAfterExit
systemctl status taskbot.service

# контейнеры подняты и healthy?
docker compose -f /home/deploy/myapp/docker-compose.yml ps

# логи запуска через journald
journalctl -u taskbot.service          # все записи
journalctl -u taskbot.service -b       # только с текущей загрузки
journalctl -u taskbot.service -f       # следить в реальном времени
```

## 4. Управление

```bash
sudo systemctl stop taskbot.service     # docker compose down (данные в volume остаются)
sudo systemctl start taskbot.service    # docker compose up -d --wait
sudo systemctl restart taskbot.service  # stop + start
sudo systemctl disable taskbot.service  # убрать из автозагрузки (сервис не останавливается)
```

## 5. Тест автозапуска (ребут)

```bash
sudo reboot
# после загрузки сервера:
systemctl status taskbot.service
docker compose -f /home/deploy/myapp/docker-compose.yml ps
```

## Почему юнит, а не только restart: always

У сервисов в docker-compose.yml (п.13) уже стоит `restart: always` — Docker
демон сам перезапускает упавшие контейнеры и поднимает их при загрузке.
Юнит добавляет то, что restart: always не даёт:

1. **Явный порядок** — старт строго после `docker.service` (`After` + `Requires`).
2. **Восстановление compose-проекта целиком** — если проект был остановлен
   (`docker compose down`) или не поднялся при загрузке, systemd повторит
   попытку (`Restart=on-failure`, каждые 10 секунд).
3. **Единая точка управления** — `systemctl stop taskbot` = штатный
   `compose down`, удобно для деплоя и не надо помнить пути.
4. **Логи в journald** — `journalctl -u taskbot`.
