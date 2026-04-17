#!/bin/bash

# Скрипт для виправлення конфліктів міграцій та перезапуску бекенду на сервері
# Автор: Antigravity AI

echo "🚀 Починаємо процес відновлення..."

# 1. Видаляємо проблемний контейнер ТА ОБРАЗ (обходимо баг docker-compose 1.29.2)
echo "📦 Видаляємо контейнер та старі образи..."
# Шукаємо будь-який контейнер, що містить 'erp_backend' у назві
docker rm -f $(docker ps -a -q -f "name=erp_backend") 2>/dev/null || true
docker rmi erp-system_backend 2>/dev/null || true
docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true

# 2. Очищуємо файли міграцій від "фантомних" файлів та кешу
echo "🧹 Очищуємо папку міграцій та кеш..."
git clean -fd backend/alembic/versions/
find . -name "__pycache__" -type d -exec rm -rf {} +

# 3. Оновлюємо код до останньої версії з GitHub
echo "🔄 Оновлюємо код з GitHub..."
git pull origin main
git reset --hard origin/main

# 4. Запускаємо бекенд заново
echo "🔨 Запускаємо бекенд..."
# Спробуємо використати 'docker compose' (V2) якщо він є, інакше старий 'docker-compose'
if docker compose version >/dev/null 2>&1; then
    docker compose up -d --build backend
else
    echo "⚠️ У вас стара версія docker-compose. Спробуйте оновити: apt install docker-compose-plugin"
    docker-compose up -d --build backend
fi

# 5. Синхронізуємо стан бази даних (Alembic Stamp)
echo "⚙️ Синхронізуємо стан міграцій у базі..."
# Даємо контейнеру час запуститися
sleep 5
docker-compose exec -T backend alembic stamp head

echo "✅ Відновлення завершено! Спробуйте створити характеристику в браузері."
