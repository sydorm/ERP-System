#!/bin/bash
set -e

# Скрипт для оновлення ERP системи на Vultr
# Запуск: ./scripts/update.sh

echo "♦ Починаємо процес відновлення..."

# 1. Отримуємо останні зміни з GitHub
echo "♦ Оновлюємо код з GitHub..."
git fetch origin main
git reset --hard origin/main

# 2. Зупиняємо контейнери ПЕРЕД очищенням образів
echo "♦ Зупиняємо контейнери..."
docker compose down

# 3. Видаляємо старі образи та кеш (БЕЗ --volumes щоб не зачепити дані)
echo "♦ Видаляємо контейнери та старі образи..."
docker system prune -f
rm -rf frontend/node_modules/.vite 2>/dev/null || true

# 4. Перезбираємо та запускаємо (--force-recreate гарантує свіжі контейнери)
echo "♦ Запускаємо бекенд..."
docker compose build --no-cache frontend
docker compose up -d --force-recreate

echo "⏳ Waiting for services to settle (15s)..."
sleep 15

# 5. Перевірка статусу
echo "♦ Перевіряємо статус контейнерів..."
docker compose ps

# 6. Застосовуємо міграції
echo "♦ Синхронізуємо стан міграцій у базі..."
docker compose exec -T backend alembic upgrade head || echo "⚠️ Migration failed or already up to date"

echo "♦ Відновлення завершено! Спробуйте створити характеристику в браузері."
echo "🌐 Frontend: http://70.34.247.20:5173"
echo "🔌 Backend:  http://70.34.247.20:8000"
