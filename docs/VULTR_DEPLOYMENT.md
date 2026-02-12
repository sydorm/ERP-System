# Deployment на Vultr Server

Повна інструкція для розгортання ERP системи на Vultr VPS.

## 1. Створення Vultr VPS

### Рекомендовані specs для MVP:
- **Plan**: Cloud Compute - Regular Performance
- **CPU**: 2 vCPU
- **RAM**: 4 GB
- **Storage**: 80 GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Location**: Обрати найближчу до користувачів (Frankfurt для України)

**Вартість**: ~$12/місяць

---

## 2. Початкове налаштування сервера

### 2.1 Підключення через SSH

```bash
ssh root@your_server_ip
```

### 2.2 Оновлення системи

```bash
apt update && apt upgrade -y
```

### 2.3 Створення нового користувача (безпека)

```bash
adduser deploy
usermod -aG sudo deploy
```

### 2.4 Налаштування SSH для нового користувача

```bash
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

Тепер підключайтеся як deploy:
```bash
ssh deploy@your_server_ip
```

---

## 3. Встановлення Docker

```bash
# Видалити старі версії (якщо є)
sudo apt-get remove docker docker-engine docker.io containerd runc

# Встановити залежності
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Додати Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Додати Docker repository
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Встановити Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Додати користувача до групи docker
sudo usermod -aG docker deploy
newgrp docker

# Перевірити установку
docker --version
docker compose version
```

---

## 4. Встановлення Git

```bash
sudo apt install -y git
git --version
```

---

## 5. Клонування проекту

```bash
# Створити директорію для проектів
mkdir -p ~/projects
cd ~/projects

# Клонувати репозиторій (коли буде Git repo)
# git clone https://github.com/your-username/erp-system.git
# cd erp-system

# Або завантажити файли вручну
mkdir erp-system
cd erp-system

# Завантажити файли через scp з локальної машини:
# scp -r g:\Моделювання\R1\* deploy@your_server_ip:~/projects/erp-system/
```

---

## 6. Налаштування Environment файлів

### 6.1 Backend .env

```bash
cd ~/projects/erp-system/backend
nano .env
```

Додайте:
```env
DATABASE_URL=postgresql://erp_user:STRONG_PASSWORD_HERE@postgres:5432/erp_db
REDIS_URL=redis://redis:6379
SECRET_KEY=generate-random-256-bit-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
ALLOWED_ORIGINS=["https://your-domain.com"]
```

**Згенерувати SECRET_KEY:**
```bash
openssl rand -hex 32
```

### 6.2 Frontend .env

```bash
cd ~/projects/erp-system/frontend
nano .env
```

Додайте:
```env
VITE_API_URL=https://api.your-domain.com
```

---

## 7. Production Docker Compose

Створіть `docker-compose.prod.yml`:

```bash
cd ~/projects/erp-system
nano docker-compose.prod.yml
```

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: erp_postgres
    restart: always
    environment:
      POSTGRES_DB: erp_db
      POSTGRES_USER: erp_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - erp_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U erp_user -d erp_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: erp_redis
    restart: always
    networks:
      - erp_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: erp_backend
    restart: always
    environment:
      DATABASE_URL: postgresql://erp_user:${POSTGRES_PASSWORD}@postgres:5432/erp_db
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - erp_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: erp_frontend
    restart: always
    networks:
      - erp_network

  nginx:
    image: nginx:alpine
    container_name: erp_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
      - frontend
    networks:
      - erp_network

volumes:
  postgres_data:

networks:
  erp_network:
    driver: bridge
```

---

## 8. Production Dockerfiles

### 8.1 Backend Dockerfile.prod

```bash
nano backend/Dockerfile.prod
```

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run with gunicorn for production
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

Додайте gunicorn до requirements.txt:
```bash
echo "gunicorn==21.2.0" >> backend/requirements.txt
```

### 8.2 Frontend Dockerfile.prod

```bash
nano frontend/Dockerfile.prod
```

```dockerfile
FROM node:20-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## 9. Nginx Configuration

### 9.1 Створити директорію

```bash
mkdir -p nginx
```

### 9.2 Main Nginx config

```bash
nano nginx/nginx.conf
```

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

        # SSL Configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket support (for future features)
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### 9.3 Frontend Nginx config

```bash
nano nginx/frontend.conf
```

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/javascript application/xml+rss application/json;
}
```

---

## 10. SSL Certificate (Let's Encrypt)

```bash
# Встановити Certbot
sudo apt install -y certbot python3-certbot-nginx

# Отримати сертифікат
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Автоматичне оновлення (crontab)
sudo crontab -e
# Додати:
0 0 * * * certbot renew --quiet
```

---

## 11. Запуск Production

```bash
cd ~/projects/erp-system

# Створити .env файл з паролями
nano .env
```

Додайте:
```env
POSTGRES_PASSWORD=your_strong_password
SECRET_KEY=your_generated_secret_key
```

```bash
# Build і запуск
docker compose -f docker-compose.prod.yml up -d --build

# Перевірити логи
docker compose -f docker-compose.prod.yml logs -f

# Перевірити статус
docker compose -f docker-compose.prod.yml ps
```

---

## 12. Firewall (UFW)

```bash
# Увімкнути firewall
sudo ufw enable

# Дозволити SSH
sudo ufw allow 22/tcp

# Дозволити HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Перевірити статус
sudo ufw status
```

---

## 13. Моніторинг і Backup

### 13.1 Автоматичний backup бази даних

```bash
nano ~/backup-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker exec erp_postgres pg_dump -U erp_user erp_db > $BACKUP_DIR/erp_db_$TIMESTAMP.sql

# Видалити бекапи старші 7 днів
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

```bash
chmod +x ~/backup-db.sh

# Додати в crontab (щодня о 2 ночі)
crontab -e
# Додати:
0 2 * * * /home/deploy/backup-db.sh
```

### 13.2 Моніторинг ресурсів

```bash
# Встановити htop
sudo apt install -y htop

# Перегляд ресурсів
htop
```

---

## 14. Оновлення Production

```bash
cd ~/projects/erp-system

# Pull нових змін
git pull origin main

# Rebuild і restart
docker compose -f docker-compose.prod.yml up -d --build

# Перевірити логи
docker compose -f docker-compose.prod.yml logs -f backend frontend
```

---

## 15. Troubleshooting

### Переглянути логи
```bash
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
docker compose -f docker-compose.prod.yml logs postgres
```

### Перезапустити сервіс
```bash
docker compose -f docker-compose.prod.yml restart backend
```

### Зайти в контейнер
```bash
docker exec -it erp_backend /bin/bash
docker exec -it erp_postgres psql -U erp_user -d erp_db
```

### Очистити Docker
```bash
docker system prune -a
```

---

## 16. Checklist перед запуском

- [ ] Доменне ім'я налаштовано (A record → IP сервера)
- [ ] SSL сертифікат отримано
- [ ] .env файли з production налаштуваннями
- [ ] Firewall налаштовано
- [ ] Backup скрипт працює
- [ ] Nginx правильно проксує запити
- [ ] База даних працює
- [ ] Backend API відповідає (https://your-domain.com/api/health)
- [ ] Frontend завантажується (https://your-domain.com)

---

## Вартість

**Місячна вартість:**
- Vultr VPS (4GB): $12
- Домен (.com): ~$12/рік = $1/місяць
- **Загалом**: ~$13/місяць для MVP

**При масштабуванні (100+ користувачів):**
- Vultr VPS (8GB): $24/місяць
- Managed PostgreSQL: $15/місяць
- Backups: $5/місяць
- **Загалом**: ~$44/місяць
