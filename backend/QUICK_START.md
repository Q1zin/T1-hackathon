# Быстрый старт

## Требования

- Docker и Docker Compose
- Git

## Запуск

### 1. Клонировать репозиторий

```bash
git clone <repository-url>
cd T1-hackathon
```

### 2. Настроить переменные окружения

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Отредактировать `.env`:
```env
SFERA_API_USERNAME=ваш-email@example.com
SFERA_API_PASSWORD=ваш-api-token
```

### 3. Запустить Docker

```bash
docker-compose up -d
```

### 4. Проверить работу

**Health check:**
```bash
curl http://localhost:8000/health
```

**Swagger UI:**
```
http://localhost:8000/docs
```

**Тест API:**
```bash
curl http://localhost:8000/api/v1/data/test-auth
curl http://localhost:8000/api/v1/data/projects?limit=5
```

## Остановка

```bash
docker-compose down
```

## Логи

```bash
# Все сервисы
docker-compose logs -f

# Только API
docker-compose logs -f api

# Только Celery worker
docker-compose logs -f celery_worker
```

## Порты

- **8000** - FastAPI
- **5432** - PostgreSQL
- **6379** - Redis
