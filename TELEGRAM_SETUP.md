# Настройка Telegram бота

## 1. Создание бота

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен в `.env` файл:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

## 2. Настройка Mini App

1. Отправьте команду `/newapp` боту [@BotFather](https://t.me/botfather)
2. Выберите вашего бота
3. Укажите название приложения: `Sunog`
4. Укажите описание: `AI генератор персональных песен`
5. Загрузите иконку (512x512px)
6. Укажите URL приложения: `https://yourdomain.com`
7. Сохраните полученную ссылку

## 3. Настройка webhook (для продакшена)

### Автоматическая настройка

```bash
# Установите webhook URL
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourdomain.com/bot/webhook"}'
```

### Проверка webhook

```bash
# Проверьте статус webhook
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

## 4. Настройка переменных окружения

Обновите `.env` файл:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_WEBHOOK_SECRET=your_webhook_secret_here

# URLs (замените на ваши домены)
BASE_URL=https://yourdomain.com
FRONTEND_URL=https://yourdomain.com
PUBLIC_BASE_URL=https://yourdomain.com
```

## 5. Тестирование

1. Запустите проект: `docker compose up -d`
2. Найдите вашего бота в Telegram
3. Отправьте команду `/start`
4. Нажмите кнопку "Создать песню"
5. Проверьте, что Mini App открывается

## 6. Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку
- `/orders` - Открыть список заказов
- `/new` - Создать новый заказ

## 7. Troubleshooting

### Бот не отвечает

1. Проверьте токен бота в `.env`
2. Убедитесь, что сервисы запущены: `docker compose ps`
3. Проверьте логи: `docker compose logs -f server`

### Mini App не открывается

1. Проверьте URL в настройках бота
2. Убедитесь, что фронтенд доступен по HTTPS
3. Проверьте CORS настройки

### Webhook не работает

1. Проверьте, что домен доступен из интернета
2. Убедитесь, что SSL сертификат валиден
3. Проверьте логи Nginx: `docker compose logs -f nginx`

## 8. Продакшен настройки

### SSL сертификаты

```bash
# Используйте Let's Encrypt
certbot --nginx -d yourdomain.com
```

### Домен и DNS

1. Настройте A-запись для вашего домена
2. Убедитесь, что порты 80 и 443 открыты
3. Настройте firewall

### Мониторинг

- Prometheus: `https://yourdomain.com:9090`
- Grafana: `https://yourdomain.com:3001`
- API Docs: `https://yourdomain.com/docs`

