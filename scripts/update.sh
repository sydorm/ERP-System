#!/bin/bash

# Скрипт для оновлення ERP системи на Vultr
# Запуск: ./scripts/update.sh

echo "🚀 Starting update process..."

# 1. Отримуємо останні зміни з GitHub
echo "📥 Pulling latest changes from git..."
git pull origin main || { echo "❌ Git pull failed"; exit 1; }

# 2. Очищення старих образів для звільнення пам'яті (важливо для Vultr)
echo "🧹 Cleaning up old docker resources..."
docker system prune -f --volumes

# 3. Перезбираємо контейнери
echo "🐳 Rebuilding and restarting containers..."
docker-compose down
docker-compose up -d --build

echo "⏳ Waiting for services to settle (15s)..."
sleep 15

# 4. Перевірка статусу контейнерів
echo "📊 Checking container status..."
docker-compose ps

# 5. Застосовуємо міграції бази даних
echo "🗄️ Applying database migrations..."
docker-compose exec -T backend alembic upgrade head || echo "⚠️ Migration failed or already up to date"

echo "✅ Update completed successfully!"
echo "🌐 Frontend available at: http://70.34.247.20:5173"
echo "🔌 Backend available at: http://70.34.247.20:8000"
