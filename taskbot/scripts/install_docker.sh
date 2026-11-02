#!/usr/bin/env bash
#
# Установка Docker и Docker Compose на Ubuntu 22.04.
#
# Что делает скрипт:
#   1. Проверяет окружение (не root, наличие sudo, Ubuntu 22.04).
#   2. Устанавливает пакеты, необходимые для подключения репозитория.
#   3. Добавляет официальный GPG-ключ и репозиторий Docker.
#   4. Устанавливает docker-ce и docker-compose-plugin.
#   5. Добавляет текущего пользователя в группу docker (без sudo).
#   6. Проверяет установку командой docker --version.
#
# Запуск:  ./install_docker.sh
# После выполнения перезапустите сессию (или выполните `newgrp docker`),
# чтобы группа docker применилась.

set -euo pipefail

# --- Шаг 1. Проверка окружения -------------------------------------------------

# Под root работать нельзя: usermod применяется к "текущему пользователю",
# а sudo для выполнения привилегированных команд нужен только обычному юзеру.
if [[ $EUID -eq 0 ]]; then
  echo "Ошибка: не запускайте скрипт от root. Запустите от обычного пользователя (sudo спросится сам)." >&2
  exit 1
fi

# Все привилегированные действия выполняются через sudo — проверяем, что он есть.
if ! command -v sudo >/dev/null 2>&1; then
  echo "Ошибка: sudo не найден. Установите его: apt install sudo" >&2
  exit 1
fi

# Скрипт написан под Ubuntu 22.04 (jammy) — убеждаемся, что запустили именно на ней.
if ! grep -qE 'Ubuntu 22\.04' /etc/os-release; then
  echo "Предупреждение: скрипт тестировался на Ubuntu 22.04, текущая ОС может отличаться." >&2
  grep -E '^(PRETTY_NAME)=' /etc/os-release >&2 || true
  read -rp "Продолжить установку? [y/N] " answer
  [[ ${answer:-N} =~ ^[Yy]$ ]] || exit 1
fi

echo "==> Окружение проверено: пользователь $(whoami), sudo доступен."

# --- Шаг 2. Подготовка: пакеты для добавления репозитория -----------------------

# ca-certificates — HTTPS для apt; curl — скачивание GPG-ключа;
# gnupg — работа с ключами apt.
echo "==> Устанавливаю пакеты, необходимые для подключения репозитория Docker..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# --- Шаг 3. Официальный репозиторий Docker --------------------------------------

# Каталог, где apt хранит ключи репозиториев.
echo "==> Добавляю официальный GPG-ключ Docker..."
sudo install -m 0755 -d /etc/apt/keyrings

# Скачиваем ключ Docker в деграгментированном (ASCII) виде и даём права на чтение.
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Добавляем сам репозиторий: приоритет apt-источников в формате deb822.
echo "==> Подключаю репозиторий Docker (download.docker.com)..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# --- Шаг 4. Установка docker-ce и docker-compose-plugin -------------------------

# docker-ce            — сам Docker Engine
# docker-ce-cli        — CLI-клиент docker
# containerd.io        — рантайм контейнеров
# docker-buildx-plugin — расширенный сборщик образов
# docker-compose-plugin— подкоманда `docker compose`
echo "==> Устанавливаю docker-ce и docker-compose-plugin..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# --- Шаг 5. Текущий пользователь в группу docker --------------------------------

# Членство в группе docker позволяет запускать docker без sudo.
# Изменение вступит в силу после перезапуска сессии.
echo "==> Добавляю пользователя $(whoami) в группу docker..."
sudo usermod -aG docker "$(whoami)"

# --- Шаг 6. Проверка установки ----------------------------------------------------

echo "==> Проверяю установку..."
docker --version
sudo docker compose version

echo ""
echo "Готово! Docker и Docker Compose установлены."
echo "Чтобы запускать docker без sudo, перезапустите сессию или выполните: newgrp docker"
