# API для IoT-моніторингу

Django REST Framework проєкт для прийому телеметрії від IoT-пристроїв, зберігання часових рядів, перегляду даних через REST API та створення алертів за порогами.

> Важливо: у цьому варіанті використовується SQLite, бо це задано окремою умовою. Це свідоме відхилення від загальної вимоги про PostgreSQL/MySQL/MariaDB для production.

## Основні можливості

- реєстрація користувача;
- токен-логін через DRF token auth;
- CRUD для пристроїв;
- прийом телеметрії через `X-DEVICE-KEY`;
- зберігання часових рядів;
- фільтрація телеметрії за пристроєм, метрикою і періодом;
- пороги алертів;
- автоматичне створення алертів при перевищенні порогів;
- асинхронна AI-аналітика телеметрії через Celery + OpenAI API;
- Docker/Gunicorn/Nginx конфігурація.

## Локальний запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Запуск через Docker

```bash
cp .env.example .env
docker compose up --build
```

API буде доступне на `http://localhost`.

## Основні endpoints

### Accounts

```http
POST /api/accounts/register/
POST /api/accounts/login/
GET  /api/accounts/me/
```

### Devices

```http
GET    /api/devices/
POST   /api/devices/
GET    /api/devices/{id}/
PATCH  /api/devices/{id}/
DELETE /api/devices/{id}/
POST   /api/devices/{id}/rotate-key/
```

### Telemetry

```http
POST /api/telemetry/ingest/
GET  /api/telemetry/points/
GET  /api/telemetry/points/?device=1&metric=temperature&start=2026-01-01T00:00:00Z&end=2026-01-02T00:00:00Z
```

Приклад прийому телеметрії:

```bash
curl -X POST http://127.0.0.1:8000/api/telemetry/ingest/ \
  -H "Content-Type: application/json" \
  -H "X-DEVICE-KEY: DEVICE_API_KEY" \
  -d '{"metric":"temperature","value":31.5,"unit":"C"}'
```

Також підтримується batch-формат:

```json
[
  {"metric": "temperature", "value": 31.5, "unit": "C"},
  {"metric": "humidity", "value": 75.2, "unit": "%"}
]
```

### Alerts

```http
GET    /api/alerts/thresholds/
POST   /api/alerts/thresholds/
GET    /api/alerts/events/
POST   /api/alerts/events/{id}/acknowledge/
POST   /api/alerts/events/{id}/close/
```

Приклад порогу:

```json
{
  "device": 1,
  "metric": "temperature",
  "min_value": null,
  "max_value": 30,
  "enabled": true
}
```

### AI

```http
POST /api/ai/insights/generate/
GET  /api/ai/insights/
GET  /api/ai/insights/{id}/
```

Приклад:

```json
{
  "device_id": 1,
  "metric": "temperature",
  "hours": 24
}
```

## Тести

```bash
pytest
```
