# CodeMetrics

Платформа для анализа метрик Git-репозиториев из T1 Сфера.Код API.

## Описание

Система автоматизированного сбора и анализа данных о коммитах, разработчиках и репозиториях для выявления аномалий и формирования рекомендаций по оптимизации процессов разработки.

## Технологии

- **Backend**: Python 3.11, FastAPI
- **Database**: PostgreSQL, Redis
- **Task Queue**: Celery
- **Deployment**: Docker Compose

## Команда

- Ланин Даниил (d.lanin@g.nsu.ru)
- Шарапов Владимир (q1zin@mail.ru)
- Агафонов Григорий (g.agafonov@g.nsu.ru)
- Гридин Денис (den.gridin5@gmail.com)
- Атрощенко Денис (d.atroshchenko@g.nsu.ru)

## Быстрый старт

См. [QUICK_START.md](backend/QUICK_START.md)

## API Endpoints

- **GET** `/api/v1/data/projects` - Список проектов
- **GET** `/api/v1/data/projects/{key}/repos` - Репозитории проекта
- **GET** `/api/v1/data/projects/{key}/repos/{name}/commits` - Коммиты
- **GET** `/docs` - Swagger UI

## T1 Сфера.Код Hackathon 2025

Проект создан в рамках хакатона T1 Сфера.Код.
