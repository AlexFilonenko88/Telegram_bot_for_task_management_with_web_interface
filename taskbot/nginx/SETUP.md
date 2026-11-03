# Настройка Nginx + HTTPS (Certbot) для TaskBot

Домен в примерах: `myapp.com` — заменить на свой. DNS A-запись домена должна
указывать на IP сервера **до** выпуска сертификата.

## 1. Установка пакетов

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

## 2. Каталог для webroot Certbot

```bash
sudo mkdir -p /var/www/certbot
```

Каталог используется блоком `location ^~ /.well-known/acme-challenge/` из
`myapp.conf`: Let's Encrypt запрашивает
`http://myapp.com/.well-known/acme-challenge/<token>`, и nginx отдаёт
валидационный файл прямо с диска, не заходя в приложение.

## 3. Первый выпуск сертификата (только HTTP)

Пока сертификата нет, https-блок в конфиге закомментирован (nginx не
стартует с `ssl_certificate`, указывающим на несуществующий файл).

```bash
# включаем сайт (в конфиге активен только http-блок)
sudo cp nginx/myapp.conf /etc/nginx/sites-available/myapp.conf
sudo ln -s /etc/nginx/sites-available/myapp.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# выпускаем сертификат режимом webroot
sudo certbot certonly --webroot -w /var/www/certbot -d myapp.com -d www.myapp.com
```

- `certonly` — certbot только получает и обновляет сертификаты, сам конфиг
  nginx мы контролируем руками (не даём certbot переписывать наш файл).
- `--webroot -w /var/www/certbot` — валидация через файлы в нашем location.
- Сертификаты появятся в `/etc/letsencrypt/live/myapp.com/`.

Проверка: `sudo certbot certificates`.

## 4. Включаем HTTPS-блок

Раскомментировать второй `server { listen 443 ... }` в
`/etc/nginx/sites-available/myapp.conf` (или повторно скопировать файл с
раскомментированным блоком), затем:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

Проверка: `curl -I https://myapp.com` — статус 200, заголовки безопасности,
редирект `curl -I http://myapp.com` → `301`.

## 5. Автопродление

Certbot при установке ставит systemd-таймер. Проверка:

```bash
systemctl list-timers | grep certbot        # таймер продления
sudo certbot renew --dry-run                # репетиция продления
```

После каждого продления nginx должен перечитать сертификаты. Добавляем
reload-хук:

```bash
sudo sh -c 'printf "#!/bin/sh\nsystemctl reload nginx\n" > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh'
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

Сертификаты Let's Encrypt действительны 90 дней, продлеваются автоматически
начиная с 60-го дня.

## 6. Что уже настроено в myapp.conf

| Требование | Где |
|---|---|
| Редирект HTTP → HTTPS (301) | `location / { return 301 ... }` в http-блоке |
| HSTS | `add_header Strict-Transport-Security ... always` |
| X-Frame-Options / X-Content-Type-Options | `add_header ... always` в 443-блоке |
| Gzip | `gzip on; gzip_types ...` (JSON/CSS/JS; картинки не сжимаем) |
| WebSocket | `map $http_upgrade $connection_upgrade` + `Upgrade/Connection` headers |
| Заголовки proxy | `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`, `Host` |
| Лимиты запросов | `limit_req_zone` 10 r/s на IP + burst 20 (отдельная зона 1 r/s для секретных эндпоинтов) |
| Место под сертификаты | `location /.well-known/acme-challenge/` + `ssl_certificate` в `/etc/letsencrypt/live/` |

## Порядок запуска всей связки на сервере

```bash
# 1. приложение
cd taskbot && docker compose up -d --build
# 2. nginx + сертификат (шаги 1-4 выше)
```
