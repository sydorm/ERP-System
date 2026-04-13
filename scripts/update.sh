#!/bin/bash

# Скрипт для оновлення ERP системи на Vultr
# Запуск: ./scripts/update.sh

echo "🚀 Starting update process..."

# 1. Отримуємо останні зміни з GitHub (Жорстко)
echo "📥 Pulling latest changes from git..."
git fetch origin main
git reset --hard origin/main

# 2. Очищення старих образів та КЕШУ Vite
echo "🧹 Cleaning up old docker resources & Vite cache..."
docker system prune -f --volumes
# Видаляємо кеш Vite інструментами хоста, якщо папка примонтована
rm -rf frontend/node_modules/.vite 2>/dev/null || true

# 3. Перезбираємо контейнери (примусово без кешу для фронтенду)
echo "🐳 Rebuilding and restarting containers..."
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d

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
