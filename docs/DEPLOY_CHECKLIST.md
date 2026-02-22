# DEPLOY_CHECKLIST.md
# Deployment Checklist (Vultr / Docker Compose / ERP)

## 1. Before Deploy (локально / перед пушем)
- [ ] Задача має чіткий scope
- [ ] Зміни перевірені локально/в dev
- [ ] Якщо змінювалась БД — є Alembic migration
- [ ] Немає випадкових змін/рефакторингів
- [ ] Коміт має зрозумілу назву

---

## 2. Pull / Update Code on Server
```bash
cd /var/www/ERP-System
git pull
```

## 3. Database Sync (Migrations)
```bash
# Обов'язково після зміни моделей
docker compose exec backend alembic upgrade head
```

## 4. Rebuild / Restart Services
```bash
# Якщо змінився Dockerfile, конфігурація або залежності (pip/npm)
docker compose up -d --build

# Якщо просто оновився код
docker compose restart
```

## 5. Post-Deploy Verification (на сервері)
- [ ] Контейнери в статусі Up (`docker compose ps`)
- [ ] Бекенд логи без traceback (`docker compose logs --tail=50 backend`)
- [ ] Сторінка UI відкривається
- [ ] Цільова функція працює
