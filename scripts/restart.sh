#!/bin/bash

# Скрипт для швидкого перезапуску бекенду та бази даних
# Запуск: ./scripts/restart.sh

echo "🔄 Restarting ERP System services..."

# Перезавантажуємо тільки бекенд та базу (решта підтягнеться)
docker-compose restart erp_postgres erp_backend

echo "⏳ Waiting for stability (5s)..."
sleep 5

echo "📊 Current Status:"
docker-compose ps

echo "✅ Restart command sent!"
