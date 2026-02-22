# 🚀 Deployment на Vultr VPS

## Передумови

- ✅ Vultr VPS (Ubuntu 22.04)
- ✅ Domain (опціонально, але рекомендовано)
- ✅ SSH доступ до сервера

---

## Крок 1: Підготовка VPS

### Підключення до сервера

```bash
ssh root@your-server-ip
```

### Оновлення системи

```bash
apt update && apt upgrade -y
```

### Встановлення Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Перевірити
docker --version
docker-compose --version
```

### Встановлення Git

```bash
apt install git -y
```

---

## Крок 2: Клонування проекту

```bash
# Створити директорію для проектів
mkdir -p /var/www
cd /var/www

# Клонувати з GitHub
git clone https://github.com/YOUR_USERNAME/R1.git
cd R1
```

---

## Крок 3: Налаштування Environment

### Backend .env

```bash
cd /var/www/R1/backend
cp .env.example .env
nano .env
```

**Змінити:**
```env
DATABASE_URL=postgresql://erp_user:STRONG_PASSWORD_HERE@postgres:5432/erp_db
SECRET_KEY=GENERATE_RANDOM_SECRET_KEY_HERE
ENVIRONMENT=production

# Kimi AI (якщо потрібно)
KIMI_API_KEY=your-actual-kimi-key
```

**Згенерувати SECRET_KEY:**
```bash
openssl rand -hex 32
```

### Frontend .env

```bash
cd /var/www/R1/frontend
cp .env.example .env
nano .env
```

```env
VITE_API_URL=http://your-domain.com
# Або якщо без domain:
VITE_API_URL=http://YOUR_SERVER_IP:8000
```

---

## Крок 4: Налаштування Docker Compose для Production

```bash
cd /var/www/R1
nano docker-compose.yml
```

**Змінити в postgres service:**
```yaml
environment:
  POSTGRES_PASSWORD: STRONG_PASSWORD_HERE  # Той самий як в .env
```

---

## Крок 5: Запуск

```bash
cd /var/www/R1

# Запустити все
docker-compose up -d

# Перевірити статус
docker-compose ps

# Подивитись логи
docker-compose logs -f
```

### Застосувати міграції

```bash
# Увійти в backend container
docker-compose exec backend bash

# Застосувати міграції
alembic upgrade head

# Створити тестові дані (опціонально)
python -m app.db.create_sample_data

exit
```

---

## Крок 6: Налаштування Nginx (рекомендовано)

### Встановлення

```bash
apt install nginx -y
```

### Конфігурація

```bash
nano /etc/nginx/sites-available/erp
```

**Вміст:**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /auth {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /docs {
        proxy_pass http://localhost:8000;
    }
}
```

**Активувати:**
```bash
ln -s /etc/nginx/sites-available/erp /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

---

## Крок 7: SSL Certificate (Let's Encrypt)

```bash
# Встановити Certbot
apt install certbot python3-certbot-nginx -y

# Отримати сертифікат
certbot --nginx -d your-domain.com -d www.your-domain.com

# Автоматичне оновлення
certbot renew --dry-run
```

---

## Крок 8: Firewall

```bash
# Встановити UFW
apt install ufw -y

# Дозволити потрібні порти
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# Увімкнути
ufw enable

# Перевірити
ufw status
```

---

## 🔄 Оновлення коду

```bash
cd /var/www/R1

# Отримати останні зміни
git pull origin main

# Перезапустити
docker-compose down
docker-compose up -d

# Застосувати нові міграції (якщо є)
docker-compose exec backend alembic upgrade head
```

---

## 📊 Моніторинг

### Перегляд логів

```bash
# Всі сервіси
docker-compose logs -f

# Тільки backend
docker-compose logs -f backend

# Тільки frontend
docker-compose logs -f frontend
```

### Статус контейнерів

```bash
docker-compose ps
```

### Використання ресурсів

```bash
docker stats
```

---

## ⚠️ Troubleshooting

### Контейнер не стартує

```bash
docker-compose logs backend
docker-compose restart backend
```

### БД не підключається

```bash
# Перевірити чи працює postgres
docker-compose ps postgres

# Перевірити credentials в .env
cat backend/.env
```

### Nginx помилки

```bash
# Перевірити конфігурацію
nginx -t

# Подивитись логи
tail -f /var/log/nginx/error.log
```

---

## 🎯 Готово!

Ваш ERP працює на:
- **HTTP**: http://your-domain.com
- **HTTPS**: https://your-domain.com (якщо налаштували SSL)
- **API Docs**: https://your-domain.com/docs

**Login:**
- Email: admin@demo.com
- Password: <YOUR_PASSWORD>

(з sample data)

---

## 📝 Checklist

- [ ] VPS створено
- [ ] Docker встановлено
- [ ] Проект клоновано
- [ ] .env налаштовано
- [ ] Docker containers запущені
- [ ] Міграції застосовані
- [ ] Nginx налаштовано
- [ ] SSL certificate встановлено
- [ ] Firewall налаштовано
- [ ] Все працює ✅
