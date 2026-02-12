# Database Setup - Quick Start Commands

## 🚀 Запуск PostgreSQL

```bash
# Запустити тільки PostgreSQL
docker-compose up postgres -d

# Або запустити всі сервіси
docker-compose up -d
```

## 📊 Створення таблиць

### Варіант 1: Через Alembic (рекомендовано)

```bash
cd backend

# Застосувати міграції
alembic upgrade head

# Перевірити статус
alembic current

# Історія міграцій
alembic history
```

### Варіант 2: Напряму через Python (якщо Alembic не працює)

```bash
cd backend
python -m app.db.init_db
```

## 🎲 Створення тестових даних

```bash
cd backend
python -m app.db.create_sample_data
```

**Це створить:**
- ✅ Компанію "Демо ФОП"
- ✅ Адміна (admin@demo.com / admin123)
- ✅ Головний склад
- ✅ 3 товари
- ✅ 2 контрагенти

## 🔍 Перевірка БД

### Підключення до PostgreSQL

```bash
# Через Docker
docker exec -it erp_postgres psql -U erp_user -d erp_db

# Команди в psql:
\dt          # Список таблиць
\d users     # Опис таблиці users
SELECT * FROM companies;
\q           # Вихід
```

### Перевірка даних

```sql
-- Список компаній
SELECT id, name, company_type FROM companies;

-- Список користувачів
SELECT email, first_name, last_name FROM users;

-- Список товарів
SELECT code, name, price FROM products;
```

## 🛠️ Корисні команди

### Скинути базу (ОБЕРЕЖНО!)

```bash
# Зупинити і видалити дані
docker-compose down -v

# Піднятися знову
docker-compose up -d

# Застосувати міграції
cd backend
alembic upgrade head
python -m app.db.create_sample_data
```

### Створити нову міграцію

```bash
cd backend
alembic revision --autogenerate -m "Опис змін"
```

### Відкотити міграцію

```bash
# На один крок назад
alembic downgrade -1

# До конкретної версії
alembic downgrade 001_initial
```

## 📝 Структура таблиць

```
companies (FOP/TOV)
  └─ users (співробітники)
  └─ warehouses (склади)
  └─ products (товари)
  └─ counterparties (контрагенти)
  └─ orders (замовлення)
       └─ order_lines (позиції замовлення)
```

## ✅ Перевірка готовності

- [ ] PostgreSQL запущений: `docker ps | grep postgres`
- [ ] База створена: `docker exec -it erp_postgres psql -U erp_user -d erp_db -c "\dt"`
- [ ] Таблиці створені: має бути 7 таблиць
- [ ] Тестові дані є: `SELECT count(*) FROM companies;` → має бути 1
