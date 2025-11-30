# Руководство по развертыванию

## Подготовка к продакшену

### 1. Настройка сервера

#### Требования к серверу

- **CPU**: 2+ ядра
- **RAM**: 4+ GB
- **Диск**: 20+ GB SSD
- **ОС**: Ubuntu 20.04+ или CentOS 8+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

#### Установка Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Настройка домена и SSL

#### DNS настройки

```bash
# A-запись для основного домена
yourdomain.com -> YOUR_SERVER_IP

# CNAME для API (опционально)
api.yourdomain.com -> yourdomain.com
```

#### SSL сертификаты

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d yourdomain.com

# Автообновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Настройка переменных окружения

Создайте `.env` файл для продакшена:

```bash
# ====== APP ======
DEBUG=false
LOG_LEVEL=INFO

# ====== TELEGRAM ======
TELEGRAM_BOT_TOKEN=your_production_bot_token
TELEGRAM_BOT_WEBHOOK_SECRET=your_secure_webhook_secret

# ====== AI ======
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

# ====== SUNO ======
USE_SUNO=true
SUNO_API_KEY=your_suno_key
SUNO_API_BASE=https://api.sunoapi.org

# ====== DATABASE ======
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=sunog_prod
POSTGRES_USER=sunog_prod
POSTGRES_PASSWORD=your_secure_password

# ====== REDIS ======
REDIS_URL=redis://redis:6379/0

# ====== S3 STORAGE ======
S3_ENDPOINT_URL=https://your-s3-endpoint.com
S3_ACCESS_KEY_ID=your_s3_key
S3_SECRET_ACCESS_KEY=your_s3_secret
S3_BUCKET_NAME=sunog-assets-prod
S3_REGION=us-east-1

# ====== PAYMENTS ======
PAYMENT_PROVIDER=stripe
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# ====== SECURITY ======
JWT_SECRET=your_very_secure_jwt_secret_here
CORS_ORIGINS=https://yourdomain.com

# ====== OBSERVABILITY ======
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
PROMETHEUS_ENABLED=true

# ====== URLS ======
BASE_URL=https://yourdomain.com
FRONTEND_URL=https://yourdomain.com
PUBLIC_BASE_URL=https://yourdomain.com

# ====== BUSINESS RULES ======
MAX_FREE_REGENERATIONS=3
ASSET_RETENTION_DAYS=180
RATE_LIMIT_PER_MINUTE=30
```

### 4. Развертывание

#### Клонирование и настройка

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/sunog.git
cd sunog

# Копирование конфигурации
cp env.example .env
# Отредактируйте .env файл

# Создание SSL директории
mkdir -p infra/ssl
```

#### Запуск в продакшене

```bash
# Запуск с продакшен конфигурацией
docker-compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Выполнение миграций
docker-compose -f docker-compose.prod.yml exec server alembic upgrade head
```

### 5. Настройка Telegram бота

#### Установка webhook

```bash
# Установка webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourdomain.com/bot/webhook"}'

# Проверка webhook
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

#### Настройка Mini App

1. Откройте [@BotFather](https://t.me/botfather)
2. Отправьте `/newapp`
3. Выберите вашего бота
4. Укажите URL: `https://yourdomain.com`

### 6. Мониторинг и логирование

#### Настройка Sentry

1. Создайте проект в [Sentry](https://sentry.io)
2. Получите DSN
3. Добавьте в `.env` файл

#### Настройка Prometheus и Grafana

```bash
# Проверка метрик
curl http://localhost:9090/metrics

# Доступ к Grafana
# URL: https://yourdomain.com:3001
# Логин: admin
# Пароль: admin (измените в .env)
```

### 7. Backup и восстановление

#### Backup базы данных

```bash
# Создание backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U sunog_prod sunog_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Автоматический backup (crontab)
0 2 * * * cd /path/to/sunog && docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U sunog_prod sunog_prod > backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

#### Восстановление

```bash
# Восстановление из backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U sunog_prod sunog_prod < backup_file.sql
```

### 8. Масштабирование

#### Горизонтальное масштабирование

```bash
# Увеличение количества worker'ов
docker-compose -f docker-compose.prod.yml up -d --scale worker=3

# Увеличение количества API серверов
docker-compose -f docker-compose.prod.yml up -d --scale server=2
```

#### Настройка load balancer

```nginx
# nginx.conf
upstream backend {
    server server1:8000;
    server server2:8000;
    server server3:8000;
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

### 9. Обновление

#### Обновление кода

```bash
# Получение обновлений
git pull origin main

# Пересборка и перезапуск
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Выполнение миграций
docker-compose -f docker-compose.prod.yml exec server alembic upgrade head
```

#### Откат изменений

```bash
# Откат к предыдущей версии
git checkout previous_commit_hash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### 10. Безопасность

#### Firewall настройки

```bash
# UFW настройки
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### Регулярные обновления

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 11. Troubleshooting

#### Проверка логов

```bash
# Логи всех сервисов
docker-compose -f docker-compose.prod.yml logs -f

# Логи конкретного сервиса
docker-compose -f docker-compose.prod.yml logs -f server
```

#### Проверка ресурсов

```bash
# Использование ресурсов
docker stats

# Дисковое пространство
df -h

# Память
free -h
```

#### Перезапуск сервисов

```bash
# Перезапуск всех сервисов
docker-compose -f docker-compose.prod.yml restart

# Перезапуск конкретного сервиса
docker-compose -f docker-compose.prod.yml restart server
```

