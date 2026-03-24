#!/bin/bash

# Скрипт для перезавантаження бази даних калькулятора на Vultr
# Запуск: ./scripts/restart_calculator_db.sh

echo "🔄 Restarting Calculator Database..."

# Переходимо в директорію калькулятора
cd "$(dirname "$0")/../calculator-app" || exit

# Перезавантажуємо тільки контейнер бази даних
docker-compose restart calc_postgres

echo "✅ Calculator Database (calc_postgres) restarted!"

# Перевіряємо статус
docker-compose ps calc_postgres
