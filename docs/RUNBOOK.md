# Antigravity ERP Runbook (Diagnostics / Recovery / Deployment)

## 1. Purpose
Цей runbook використовується для:
- швидкої діагностики проблем
- відновлення роботи сервісів
- перевірки міграцій
- перевірки backend/frontend після змін

---

## 2. Standard Commands (Use only Docker Compose V2)

### Перевірка версій
```bash
docker --version
docker compose version
```

### Статус сервісів
```bash
docker compose ps
docker compose stats
```

### Логи
```bash
# Всі сервіси
docker compose logs -f --tail=100

# Конкретний сервіс
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

---

## 3. Database & Migrations

### Перевірка бази (PostgreSQL)
```bash
# Перевірити наявність таблиць
docker compose exec postgres psql -U erp_user -d erp_db -c "\dt"

# Перевірити конкретну таблицю (наприклад, document_sequences)
docker compose exec postgres psql -U erp_user -d erp_db -c "select * from document_sequences;"
```

### Управління міграціями (Alembic)
```bash
# Застосувати всі міграції
docker compose exec backend alembic upgrade head

# Перевірити поточну версію міграції
docker compose exec backend alembic current

# Відкотити останню міграцію
docker compose exec backend alembic downgrade -1

# Створити нову міграцію (автоматично на основі моделей)
docker compose exec backend alembic revision --autogenerate -m "description_of_change"
```

---

## 4. Recovery (Відновлення)

### Перезапуск сервісів
```bash
# Повний перезапуск (іноді вирішує проблеми з кешем)
docker compose restart

# Перезапуск зі збіркою (якщо змінилися Dockerfile або залежності)
docker compose up -d --build
```

### Очищення (Use with caution!)
```bash
# Видалити всі контейнери, мережі
docker compose down

# Видалити разом з даними (Volumes!) — УВАГА: видалить базу!
# docker compose down -v
```

---

## 5. Backend Diagnostics (FastAPI)

### Перевірка API
```bash
# Перевірити здоров'я API
curl http://localhost:8000/health

# Доступ до автоматичної документації
# http://[IP_OR_DOMAIN]:8000/docs
```

---

## 6. Frontend Diagnostics (Vue)

### Перевірка збірки
```bash
# Якщо фронтенд не стартує після git pull (оновлення пакетів)
docker compose exec frontend npm install
```

---

## 7. Workflow Checklist

1. **Pull code:** `git pull origin main`
2. **Apply migrations:** `docker compose exec backend alembic upgrade head`
3. **Restart if needed:** `docker compose restart`
4. **Check logs:** `docker compose logs --tail=50 backend`
