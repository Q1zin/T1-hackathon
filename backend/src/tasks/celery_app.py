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
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

from src.tasks import collection_tasks  # noqa: F401
