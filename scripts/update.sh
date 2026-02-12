#!/bin/bash

# Скрипт для оновлення ERP системи на Vultr
# Запуск: ./scripts/update.sh

echo "🚀 Starting update process..."

# 1. Отримуємо останні зміни з GitHub
echo "📥 Pulling latest changes from git..."
git pull origin main

# 2. Перезбираємо контейнери (якщо змінились залежності або Dockerfile)
echo "🐳 Rebuilding and restarting containers..."
docker-compose down
docker-compose up -d --build

# 3. Застосовуємо міграції бази даних
echo "🗄️ Applying database migrations..."
docker-compose exec backend alembic upgrade head

echo "✅ Update completed successfully!"
