# 🚀 Покрокова інструкція: від GitHub до працюючого сервера

## 📋 Що маємо:
- ✅ Готовий код в `g:\Моделювання\R1`
- ✅ GitHub repository: https://github.com/sydorm/ERP-System.git

## 🎯 Що зробимо:
1. Завантажимо код на GitHub
2. Створимо Vultr VPS
3. Запустимо ERP на сервері
4. Отримаємо працюючу систему на IP/домені

---

# ЕТАП 1: Завантаження на GitHub ⬆️

## Крок 1.1: Ініціалізація Git

```powershell
# Перейти в директорію проекту
cd g:\Моделювання\R1

# Перевірити чи є git (якщо ні - встановити з git-scm.com)
git --version

# Ініціалізувати (якщо не було)
git init
```

## Крок 1.2: Додати файли

```powershell
# Додати всі файли
git add .

# Перевірити що додалось (зелені - добре, червоні - ігноруються)
git status
```

## Крок 1.3: Зробити commit

```powershell
git commit -m "Initial commit: ERP system with database, auth API, and AI assistant"
```

## Крок 1.4: Підключити GitHub

```powershell
# Підключити ваш repository
git remote add origin https://github.com/sydorm/ERP-System.git

# Перевірити
git remote -v
```

## Крок 1.5: Push на GitHub

```powershell
# Створити main гілку і завантажити
git branch -M main
git push -u origin main
```

**Якщо попросить авторизацію:**
- Username: sydorm
- Password: **GitHub Personal Access Token** (не пароль!)
  - Створити тут: https://github.com/settings/tokens
  - Permissions: repo (full control)

✅ **Перевірка:** Відкрийте https://github.com/sydorm/ERP-System - має з'явитись код!

---

# ЕТАП 2: Створення Vultr VPS ☁️

## Крок 2.1: Реєстрація на Vultr

1. Перейти: https://www.vultr.com/
2. Sign Up або Login
3. Add Funds (мінімум $10)

## Крок 2.2: Створити VPS

**Deploy New Server:**
- **Type**: Cloud Compute
- **Location**: Amsterdam / Frankfurt (ближче до України)
- **Server Type**: Ubuntu 22.04 LTS
- **Server Size**: 
  - **Мінімум**: $6/міс (2GB RAM, 55GB SSD) ← рекомендую
  - Бюджет: $12/міс (4GB RAM, 80GB SSD)
- **SSH Key**: (опціонально, але рекомендую)
  - Створити: `ssh-keygen -t rsa -b 4096`
  - Додати публічний ключ (~/.ssh/id_rsa.pub)
- **Server Hostname**: erp-production

**Deploy Now!**

⏳ Зачекайте 2-3 хв поки сервер створюється

## Крок 2.3: Записати дані

```
IP Address: _______________________
Username: root
Password: _________________________ (якщо без SSH key)
```

✅ **Перевірка:** Status: Running

---

# ЕТАП 3: Налаштування VPS 🛠️

## Крок 3.1: Підключення до сервера

**Через SSH (Windows PowerShell):**

```powershell
# З паролем:
ssh root@YOUR_SERVER_IP

# З SSH ключем:
ssh -i ~/.ssh/id_rsa root@YOUR_SERVER_IP
```

**При першому підключенні:**
```
The authenticity of host... Are you sure? → yes
```

✅ **Ви на сервері!** Побачите: `root@erp-production:~#`

---

## Крок 3.2: Оновлення системи

```bash
apt update && apt upgrade -y
```

⏳ 2-3 хвилини

---

## Крок 3.3: Встановлення Docker

```bash
# Встановити Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Встановити Docker Compose
apt install docker-compose -y

# Перевірити
docker --version
docker-compose --version
```

✅ **Має показати версії** (наприклад: Docker version 24.0.7)

---

## Крок 3.4: Встановлення Git

```bash
apt install git -y

# Перевірити
git --version
```

---

# ЕТАП 4: Клонування проекту 📦

## Крок 4.1: Створити директорію

```bash
mkdir -p /var/www
cd /var/www
```

## Крок 4.2: Клонувати з GitHub

```bash
git clone https://github.com/sydorm/ERP-System.git
cd ERP-System

# Перевірити
ls -la
```

✅ **Має показати:** backend/, frontend/, docs/, docker-compose.yml і т.д.

---

# ЕТАП 5: Налаштування Environment 🔧

## Крок 5.1: Backend .env

```bash
cd /var/www/ERP-System/backend
cp .env.example .env
nano .env
```

**Змінити наступні рядки:**

```env
# ⚠️ ОБОВ'ЯЗКОВО змінити:
DATABASE_URL=postgresql://erp_user:STRONG_PASS_123@postgres:5432/erp_db
SECRET_KEY=<згенеруйте-нижче>
ENVIRONMENT=production

# Опціонально (якщо є Kimi AI key):
KIMI_API_KEY=your-actual-kimi-key-here
```

**Згенерувати SECRET_KEY:**
```bash
# Вийти з nano: Ctrl+X → N
openssl rand -hex 32

# Скопіювати результат і вставити в .env як SECRET_KEY
nano .env
# Вставити після SECRET_KEY=
```

**Зберегти:** Ctrl+X → Y → Enter

---

## Крок 5.2: Змінити пароль БД в docker-compose.yml

```bash
cd /var/www/ERP-System
nano docker-compose.yml
```

**Знайти секцію postgres і змінити:**

```yaml
environment:
  POSTGRES_PASSWORD: STRONG_PASS_123  # Той самий як в .env вище!
```

**Зберегти:** Ctrl+X → Y → Enter

---

## Крок 5.3: Frontend .env

```bash
cd /var/www/ERP-System/frontend
cp .env.example .env
nano .env
```

**Вміст:**
```env
VITE_API_URL=http://YOUR_SERVER_IP
```

Замініть YOUR_SERVER_IP на ваш реальний IP (наприклад: http://45.76.123.45)

**Зберегти:** Ctrl+X → Y → Enter

---

# ЕТАП 6: Запуск системи 🚀

## Крок 6.1: Запустити Docker

```bash
cd /var/www/ERP-System

# Запустити всі сервіси
docker-compose up -d
```

⏳ **Перший раз:** 5-10 хвилин (завантажує образи)

**Перевірити:**
```bash
docker-compose ps
```

✅ **Всі повинні бути State: Up:**
- erp_postgres
- erp_redis
- erp_backend
- erp_frontend

---

## Крок 6.2: Застосувати міграції БД

```bash
# Увійти в backend контейнер
docker-compose exec backend bash

# Застосувати міграції
alembic upgrade head

# Створити тестові дані (admin, товари, склад)
python -m app.db.create_sample_data

# Вийти
exit
```

✅ **Має показати:** "✓ Sample data created successfully!"

---

# ЕТАП 7: Відкрити firewall 🔥

```bash
# Встановити UFW
apt install ufw -y

# Дозволити порти
ufw allow 22/tcp     # SSH (важливо!)
ufw allow 5173/tcp   # Frontend
ufw allow 8000/tcp   # Backend API

# Увімкнути
ufw --force enable

# Перевірити
ufw status
```

---

# ЕТАП 8: Перевірка 🎉

## Відкрийте в браузері:

### Frontend:
```
http://YOUR_SERVER_IP:5173
```

**Login (DEMO режим):**
- Email: будь-який
- Password: будь-який

**Або з реальним backend:**
- Email: admin@demo.com
- Password: admin123

### API Documentation:
```
http://YOUR_SERVER_IP:8000/docs
```

### Kimi AI Assistant:
Після входу на Dashboard → фіолетова кнопка справа внизу 🤖

---

# ✅ ГОТОВО!

Ваша ERP система працює на:
- 🌐 Frontend: http://YOUR_IP:5173
- 🔌 Backend: http://YOUR_IP:8000
- 📖 Docs: http://YOUR_IP:8000/docs

---

# 📝 Додатково (опціонально)

## Налаштувати domain (замість IP)

1. Купити domain (наприклад на namecheap.com)
2. Додати A record: `@` → `YOUR_SERVER_IP`
3. Встановити Nginx + SSL:

```bash
apt install nginx certbot python3-certbot-nginx -y

# Створити конфіг
nano /etc/nginx/sites-available/erp

# Див. VULTR_DEPLOY.md для повного конфігу

# Отримати SSL
certbot --nginx -d yourdomain.com
```

Тоді доступ буде: **https://yourdomain.com** ✨

---

# 🔄 Оновлення коду (після змін)

```bash
# На сервері:
cd /var/www/ERP-System
git pull origin main
docker-compose down
docker-compose up -d

# Якщо були зміни в моделях:
docker-compose exec backend alembic upgrade head
```

---

# ⚠️ Якщо щось не працює

## Frontend не відкривається:
```bash
docker-compose logs frontend
docker-compose restart frontend
```

## Backend помилки:
```bash
docker-compose logs backend
```

## БД не підключається:
```bash
# Перевірити credentials
cat backend/.env
nano docker-compose.yml  #Password має співпадати
```

## Загальна перезагрузка:
```bash
docker-compose down
docker-compose up -d
```

---

**Готово! Будь-які питання - питайте! 🚀**
