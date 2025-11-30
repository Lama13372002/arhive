# API Examples

## Аутентификация

### Верификация Telegram WebApp

```bash
curl -X POST "http://localhost:8000/api/v1/auth/telegram/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "init_data": "query_id=AAHdF6IQAAAAAN0XohDhrOrc&user=%7B%22id%22%3A279058397%2C%22first_name%22%3A%22Vladislav%22%2C%22last_name%22%3A%22Kibenko%22%2C%22username%22%3A%22vdkfrost%22%2C%22language_code%22%3A%22ru%22%7D&auth_date=1662771648&hash=c501b71e775f74ce10e377dea85a7ea24ecd640b223ea86dfe453e0eaed2e2b2"
  }'
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "telegram_id": 279058397,
    "username": "vdkfrost",
    "first_name": "Vladislav",
    "last_name": "Kibenko",
    "locale": "ru",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

## Заказы

### Создание заказа

```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "ru",
    "genre": "pop",
    "mood": "romantic",
    "tempo": "medium",
    "occasion": "birthday",
    "recipient": "Анна",
    "notes": "Любит цветы и кофе"
  }'
```

### Получение списка заказов

```bash
curl -X GET "http://localhost:8000/api/v1/orders?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Получение заказа по ID

```bash
curl -X GET "http://localhost:8000/api/v1/orders/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Обновление заказа

```bash
curl -X PATCH "http://localhost:8000/api/v1/orders/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Добавить упоминание о путешествиях"
  }'
```

## Генерация текста

### Запуск генерации текста

```bash
curl -X POST "http://localhost:8000/api/v1/orders/1/lyrics/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "regenerate": false
  }'
```

Ответ:
```json
{
  "task_id": "lyrics_task_1_1234567890",
  "message": "Lyrics generation started"
}
```

### Получение последней версии текста

```bash
curl -X GET "http://localhost:8000/api/v1/orders/1/lyrics/latest" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Редактирование текста

```bash
curl -X POST "http://localhost:8000/api/v1/orders/1/lyrics/submit_edit" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "[Verse 1]\nТвои глаза как звезды в небе\nТвоя улыбка - солнца свет\n\n[Chorus]\nС днем рождения, Анна!\nПусть счастье будет с тобой\nС днем рождения, Анна!\nТы лучшая на свете такой"
  }'
```

### Утверждение заказа

```bash
curl -X POST "http://localhost:8000/api/v1/orders/1/approve" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Генерация аудио

### Запуск генерации аудио

```bash
curl -X POST "http://localhost:8000/api/v1/orders/1/generate_audio" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Ответ:
```json
{
  "task_id": "audio_task_1_1234567890",
  "message": "Audio generation started"
}
```

## Платежи

### Создание платежа

```bash
curl -X POST "http://localhost:8000/api/v1/orders/1/pay" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Ответ:
```json
{
  "id": 1,
  "provider": "stripe",
  "amount": 9.99,
  "currency": "USD",
  "status": "pending",
  "external_id": "pi_1234567890",
  "created_at": "2024-01-01T00:00:00"
}
```

## Health Check

### Базовая проверка

```bash
curl -X GET "http://localhost:8000/health"
```

Ответ:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### Детальная проверка

```bash
curl -X GET "http://localhost:8000/api/v1/health/detailed"
```

Ответ:
```json
{
  "status": "ok",
  "services": {
    "database": "ok",
    "redis": "ok"
  }
}
```

## Webhook для Suno

### Обработка callback от Suno

```bash
curl -X POST "http://localhost:8000/api/v1/audio/callback" \
  -H "Content-Type: application/json" \
  -d '{
    "taskId": "suno_task_123",
    "status": "completed",
    "data": {
      "audioUrl": "https://example.com/audio.mp3",
      "downloadUrl": "https://example.com/download.mp3"
    }
  }'
```

## Обработка ошибок

### Пример ошибки валидации

```json
{
  "detail": [
    {
      "loc": ["body", "language"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Пример ошибки авторизации

```json
{
  "detail": "Invalid authentication credentials"
}
```

### Пример ошибки ресурса

```json
{
  "detail": "Order not found"
}
```

## Статусы заказов

- `draft` - Черновик
- `pending_lyrics` - Генерация текста
- `lyrics_ready` - Текст готов
- `user_editing` - Редактирование пользователем
- `approved` - Утверждено
- `generating` - Генерация аудио
- `delivered` - Готово
- `canceled` - Отменено

## Статусы платежей

- `none` - Без платежа
- `pending` - Ожидает оплаты
- `paid` - Оплачено
- `failed` - Ошибка оплаты
- `refunded` - Возврат

