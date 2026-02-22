# Розробка ERP System (Technical Docs)

Цей документ містить технічну інформацію про проект, стеку технологій та плани розвитку.

---

## 🛠 Tech Stack

**Backend:**
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 15+
- **Migrations**: Alembic
- **Security**: JWT (Jose), Bcrypt

**Frontend:**
- **Framework**: Vue 3 (Vite)
- **UI Library**: Element Plus
- **State Management**: Pinia
- **Icons**: @element-plus/icons-vue

**Infrastructure:**
- **Deployment**: Docker + Docker Compose V2
- **Cache**: Redis

---

## 📁 Структура проекту

```
R1/
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints (versioned)
│   │   ├── core/          # Security, configuration, constants
│   │   ├── db/            # Session Management
│   │   ├── models/        # SQLAlchemy database models
│   │   ├── schemas/       # Pydantic schemas (request/response models)
│   │   └── services/      # Business logic & services
│   ├── alembic/           # Migrations versions
│   └── requirements.txt
│
├── frontend/              # Vue 3 frontend
│   ├── src/
│   │   ├── api/           # API service clients
│   │   ├── components/    # Reusable UI components
│   │   ├── layouts/       # Dashboard and Auth layouts
│   │   ├── stores/        # Pinia state stores
│   │   └── views/         # Page components
│   └── package.json
│
└── docker-compose.yml
```

---

## 🔄 Процес розробки (Workflow)

Ми дотримуємося стабільного процесу впровадження змін:

1.  **Локальні зміни**: Розробка та тестування в Docker-контейнерах.
2.  **Git Commit**: Чіткий опис змін.
3.  **GitHub Push**: `git push origin main`.
4.  **Vultr Sync**: `git pull` на сервері та перезапуск контейнерів за потреби.

---

## 🎯 План розвитку (Roadmap)

### Завершено (MVP)
- [x] Базова архітектура та DB моделі
- [x] Система авторизації та ролей
- [x] Інтеграція AI асистента
- [x] Управління компаніями та користувачами

### В розробці
- [ ] Повна реалізація замовлень (Orders CRUD)
- [ ] Система статусів та довідників
- [ ] Оптимізація нумерації документів за `document_sequences`

### Планується
- [ ] Модуль звітів та аналітики
- [ ] Інтеграція з платіжними сервісами
- [ ] Розширене управління складами
