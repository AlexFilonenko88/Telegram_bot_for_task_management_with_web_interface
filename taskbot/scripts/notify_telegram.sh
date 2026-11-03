#!/bin/bash
# =============================================================================
# notify_telegram.sh — отправка алерт-сообщения в Telegram (п.20).
#
# Используется backup.sh для уведомлений о сбоях, годится и для других
# скриптов:  notify_telegram.sh "текст сообщения"
#
# Настройка (через окружение или .env проекта):
#   TELEGRAM_ALERT_BOT_TOKEN — токен ОТДЕЛЬНОГО бота для алертов (создать
#                              через @BotFather; не использовать токен
#                              боевого TaskBot — алерты не должны зависеть
#                              от продуктивного бота);
#   TELEGRAM_ALERT_CHAT_ID   — id чата, куда слать алерты. Узнать: написать
#                              боту, затем открыть
#                              https://api.telegram.org/bot<TOKEN>/getUpdates
# Если переменные не заданы — скрипт тихо завершается (код 0): отсутствие
# алертов не должно ломать вызвавший скрипт.
# =============================================================================

set -euo pipefail

read_env() {
    grep -E "^$1=" "$ENV_FILE" 2>/dev/null | tail -n1 | cut -d= -f2- | tr -d '"' || true
}

ENV_FILE="${ENV_FILE:-$(cd "$(dirname "$0")/../.." && pwd)/.env}"

TOKEN="${TELEGRAM_ALERT_BOT_TOKEN:-$(read_env TELEGRAM_ALERT_BOT_TOKEN)}"
CHAT_ID="${TELEGRAM_ALERT_CHAT_ID:-$(read_env TELEGRAM_ALERT_CHAT_ID)}"

MESSAGE="${1:-(пустое уведомление)}"

# Не настроено — не падаем: хост-скрипт (бэкап) важнее уведомления.
if [ -z "$TOKEN" ] || [ -z "$CHAT_ID" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') WARNING — Telegram-алерты не настроены" \
         "(TELEGRAM_ALERT_BOT_TOKEN / TELEGRAM_ALERT_CHAT_ID), сообщение не отправлено" >&2
    exit 0
fi

# Bot API: sendMessage с parse_mode=HTML (<b>/<code> в тексте уместны).
# --max-time 10: зависший курл не должен блокировать ночные скрипты.
curl -fsS --max-time 10 \
     "https://api.telegram.org/bot${TOKEN}/sendMessage" \
     --data-urlencode "chat_id=${CHAT_ID}" \
     --data-urlencode "text=${MESSAGE}" \
     --data-urlencode "parse_mode=HTML" > /dev/null
