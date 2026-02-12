# ERP System - MVP

Сучасна ERP система для малого та середнього бізнесу з AI асистентом.

## 🚀 Швидкий старт

### Локально (з Docker)
```bash
docker-compose up -d
cd backend && alembic upgrade head
```
Детальніше: [docs/LOCAL_RUN.md](docs/LOCAL_RUN.md)

### Production (Vultr VPS)
```bash
git clone https://github.com/YOUR_USERNAME/R1.git
cd R1
# Див. docs/VULTR_DEPLOY.md
```

---

## 📋 Що готово

### ✅ Backend (FastAPI)
- 🗄️ **Database**: PostgreSQL з 7 таблицями (Company, User, Warehouse, Product, Counterparty, Order, OrderLine)
- 🔄 **Migrations**: Alembic для міграцій
- 🔐 **Authentication**: JWT токени (bcrypt + jose)
- 📝 **API**: 4 auth endpoints (register, login, profile)
- 🤖 **AI Integration**: Kimi AI assistant endpoints

### ✅ Frontend (Vue 3)
- 🎨 **UI**: Element Plus components
- 🔐 **Auth**: Login/Signup pages (DEMO режим)
- 📊 **Dashboard**: Sidebar navigation
- 🤖 **AI Assistant**: Floating chat panel з Kimi AI

### ✅ Features
- Multi-company support (ФОП/ТОВ)
- User management з ролями
- Warehouse management
- Product catalog (номенклатура)
- Counterparty management (клієнти/постачальники)
- Order processing

---

## 🛠 Tech Stack

**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0
- PostgreSQL 15+
- Alembic 1.12+
- JWT (python-jose)
- Bcrypt (passlib)

**Frontend:**
- Vue 3.3+
- Vite 5+
- Element Plus 2.4+
- Pinia
- Vue Router

**Infrastructure:**
- Docker + Docker Compose
- Redis 7+
- Nginx (production)

---

## 📁 Структура проекту

```
R1/
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Config, security
│   │   ├── db/            # Database session
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── alembic/           # Database migrations
│   └── requirements.txt
│
├── frontend/              # Vue 3 frontend
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── composables/   # Composables
│   │   ├── layouts/       # Layouts
│   │   ├── router/        # Vue Router
│   │   ├── stores/        # Pinia stores
│   │   └── views/         # Pages
│   └── package.json
│
├── docs/                  # Documentation
│   ├── LOCAL_RUN.md      # Local setup
│   ├── VULTR_DEPLOY.md   # Production deployment
│   └── DATABASE_SETUP.md # Database guide
│
└── docker-compose.yml
```

---

## 📚 Документація

- [Локальний запуск](docs/LOCAL_RUN.md)
- [Vultr Deployment](docs/VULTR_DEPLOY.md)
- [Database Setup](docs/DATABASE_SETUP.md)
- [Kimi AI Guide](docs/KIMI_USER_GUIDE.md) (в artifacts)

---

## 🔐 Default Credentials

**Admin (після sample data):**
- Email: admin@demo.com
- Password: admin123

**DEMO режим (frontend без backend):**
- Будь-які credentials

---

## 🌐 URLs

**Локально:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Production:**
- https://your-domain.com

---

## 🔄 Development Workflow

```bash
# 1. Створити нову гілку
git checkout -b feature/new-feature

# 2. Зробити зміни
# ...

# 3. Commit
git add .
git commit -m "feat: add new feature"

# 4. Push
git push origin feature/new-feature

# 5. Create Pull Request на GitHub

# 6. Після merge - deploy
ssh user@server
cd /var/www/R1
git pull
docker-compose restart
```

---

## 🐛 Troubleshooting

### Порт зайнятий
```bash
docker-compose down
# Змінити порт в docker-compose.yml
docker-compose up -d
```

### Міграції не застосовуються
```bash
docker-compose exec backend alembic current
docker-compose exec backend alembic upgrade head
```

### Frontend не бачить backend
Перевірити `VITE_API_URL` в `frontend/.env`

---

## 🎯 Roadmap

### MVP (Завершено)
- [x] Database models
- [x] Authentication API
- [x] Basic frontend
- [x] AI Assistant

### Phase 2 (В розробці)
- [ ] Products CRUD API
- [ ] Orders API
- [ ] Real-time updates (WebSockets)
- [ ] Reports module

### Phase 3 (Планується)
- [ ] Multi-warehouse inventory
- [ ] Invoicing
- [ ] Payment processing
- [ ] Mobile app

---

## 📄 License

MIT License - використовуйте як хочете!

---

## 👨‍💻 Credits

Розроблено з ❤️ для малого бізнесу України 🇺🇦
