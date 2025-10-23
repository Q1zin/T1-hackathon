"""Celery приложение для фоновых задач."""

from celery import Celery

from src.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "codemetrics",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Расписание для Celery Beat (каждые 10 минут)
celery_app.conf.beat_schedule = {
    "periodic-data-collection": {
        "task": "periodic_data_collection",
        "schedule": 600.0,  # 10 минут в секундах
        "options": {
            "expires": 540.0,  # Истекает через 9 минут, чтобы не накапливались задачи
        }
    },
}

# Импортируем задачи явно, чтобы они зарегистрировались
from src.tasks import collection_tasks  # noqa: F401
