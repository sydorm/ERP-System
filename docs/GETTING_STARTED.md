# Початок роботи з ERP System

## Швидкий старт

### 1. Перевірте встановлені залежності

Переконайтеся, що у вас встановлено:
- Docker Desktop (з Docker Compose)
- Git

### 2. Клонуйте репозиторій

```bash
cd g:\Моделювання\R1
```

### 3. Налаштуйте environment файли

```bash
# Backend
copy backend\.env.example backend\.env

# Frontend  
copy frontend\.env.example frontend\.env
```

### 4. Запустіть через Docker Compose

```bash
docker-compose up --build
```

Це запустить:
- PostgreSQL на порту 5432
- Redis на порту 6379
- Backend API на порту 8000
- Frontend на порту 5173

### 5. Відкрийте у браузері

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health

## Розробка без Docker

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Структура проекту

```
R1/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # Головний файл FastAPI
│   │   ├── core/        # Налаштування, config
│   │   ├── db/          # Database session
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── api/         # API endpoints
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/            # Vue 3 frontend
│   ├── src/
│   │   ├── main.js     # Головний файл Vue
│   │   ├── App.vue     # Root component
│   │   ├── router/     #Vue Router
│   │   ├── stores/     # Pinia stores
│   │   ├── views/      # Pages
│   │   └── components/ # Components
│   ├── package.json
│   └── Dockerfile
│
└── docker-compose.yml
```

## Наступні кроки

1. ✅ Базова структура створена
2. ⏳ Налаштувати Alembic для міграцій
3. ⏳ Створити моделі бази даних (User, Company)
4. ⏳ Додати JWT аутентифікацію
5. ⏳ Створити реєстрацію компанії (multi-step)

## Корисні команди

```bash
# Перезапустити тільки backend
docker-compose restart backend

# Перезапустити тільки frontend
docker-compose restart frontend

# Переглянути логи
docker-compose logs -f backend
docker-compose logs -f frontend

# Зупинити все
docker-compose down

# Зупинити та видалити volumes
docker-compose down -v
```

## Troubleshooting

### Порт вже зайнятий
Якщо порти 5173 або 8000 зайняті, змініть їх у `docker-compose.yml`

### Backend не може підключитися до PostgreSQL
Зачекайте 10-15 секунд після запуску docker-compose

### Frontend не бачить backend API
Перевірте, що backend запущений: http://localhost:8000/health
