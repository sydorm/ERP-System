# 🚀 Локальний запуск ERP системи

## Крок 1: Перевірка Docker

```powershell
# Перевірити чи запущений Docker Desktop
docker ps
```

Якщо помилка → запустіть Docker Desktop

---

## Крок 2: Створити .env файли

```powershell
# Backend .env
cd g:\Моделювання\R1\backend
copy .env.example .env

# Frontend .env (якщо потрібно)
cd ..\frontend
copy .env.example .env
```

---

## Крок 3: Запустити все через Docker

```powershell
cd g:\Моделювання\R1

# Запустити всі сервіси
docker-compose up -d

# Переглянути логи (щоб побачити чи все ОК)
docker-compose logs -f
```

**Що запуститься:**
- ✅ PostgreSQL на порту 5432
- ✅ Redis на порту 6379
- ✅ Backend API на порту 8000
- ✅ Frontend на порту 5173

---

## Крок 4: Застосувати міграції БД

```powershell
# Увійти в backend контейнер
docker-compose exec backend bash

# Всередині контейнера:
alembic upgrade head
python -m app.db.create_sample_data
exit
```

**Або напряму з Windows:**

```powershell
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m app.db.create_sample_data
```

---

## Крок 5: Відкрити в браузері

### Frontend (Vue 3)
```
http://localhost:5173
```

Login credentials (DEMO режим):
- Email: будь-який
- Password: будь-який

### Backend API Documentation
```
http://localhost:8000/docs
```

Тут можна тестувати API endpoints!

### Kimi AI Assistant
На сторінці Dashboard - фіолетова кнопка справа внизу 🤖

---

## Крок 6: Тестування Authentication API

### Через Swagger UI (рекомендовано)
1. Відкрити http://localhost:8000/docs
2. Знайти `/auth/register`
3. Натиснути "Try it out"
4. Ввести дані
5. Execute

### Через curl

```powershell
# 1. Отримати company_id
docker exec -it erp_postgres psql -U erp_user -d erp_db -c "SELECT id FROM companies LIMIT 1;"

# 2. Зареєструвати користувача (замінити COMPANY_ID)
curl -X POST http://localhost:8000/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@test.com\",\"password\":\"testpass123\",\"first_name\":\"Тест\",\"last_name\":\"Юзер\",\"company_id\":\"COMPANY_ID\"}'

# 3. Login
curl -X POST http://localhost:8000/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@test.com\",\"password\":\"testpass123\"}'
```

---

## ⚠️ Troubleshooting

### Порт зайнятий
```powershell
# Змінити порт у docker-compose.yml
# Наприклад: "5174:5173" замість "5173:5173"
```

### Backend не підключається до БД
```powershell
# Перезапустити все
docker-compose down
docker-compose up -d

# Зачекати 10 секунд і перевірити
docker-compose ps
```

### Frontend показує помилку
```powershell
# Подивитись логи
docker-compose logs frontend

# Або запустити без Docker
cd frontend
npm install
npm run dev
```

---

## 🎯 Що перевірити

- [ ] Frontend відкривається на localhost:5173
- [ ] Можна зайти в систему (DEMO режим)
- [ ] Dashboard відображається
- [ ] AI Assistant button з'являється
- [ ] API docs на localhost:8000/docs
- [ ] Можна зареєструвати користувача через `/auth/register`
- [ ] Можна увійти через `/auth/login`

---

## 🔄 Команди для управління

```powershell
# Зупинити все
docker-compose down

# Запустити знову
docker-compose up -d

# Переглянути логи
docker-compose logs -f backend
docker-compose logs -f frontend

# Перезапустити один сервіс
docker-compose restart backend

# Видалити все (включно з даними БД)
docker-compose down -v
```

---

## 💾 Після тестування - Git commit

```powershell
cd g:\Моделювання\R1

git add .
git commit -m "feat: add database models and authentication API"
git push
```

**Тепер все збережено в Git і можна безпечно деплоїти на сервер!** ✅
