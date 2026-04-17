#!/bin/bash

# Скрипт для виправлення конфліктів міграцій та перезапуску бекенду на сервері
# Автор: Antigravity AI

echo "🚀 Починаємо процес відновлення..."

# 1. Видаляємо проблемний контейнер (обходимо баг docker-compose 1.29.2)
echo "📦 Видаляємо контейнер erp_backend..."
docker rm -f erp_backend 2>/dev/null || true

# 2. Очищуємо файли міграцій від "фантомних" файлів та кешу
echo "🧹 Очищуємо папку міграцій та кеш..."
git clean -fd backend/alembic/versions/
find . -name "__pycache__" -type d -exec rm -rf {} +

# 3. Оновлюємо код до останньої версії з GitHub
echo "🔄 Оновлюємо код з GitHub..."
git pull origin main
git reset --hard origin/main

# 4. Запускаємо бекенд заново (з перезбіркою для впевненості)
echo "🔨 Перезбираємо та запускаємо бекенд..."
docker-compose up -d --build backend

# 5. Синхронізуємо стан бази даних (Alembic Stamp)
echo "⚙️ Синхронізуємо стан міграцій у базі..."
# Даємо контейнеру час запуститися
sleep 5
docker-compose exec -T backend alembic stamp head

echo "✅ Відновлення завершено! Спробуйте створити характеристику в браузері."
