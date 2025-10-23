"""Задачи для сбора данных."""

from src.core.logging import get_logger
from src.data_collection.api_client import SferaAPIClient
from src.data_collection.collectors import SferaDataCollector
from src.tasks.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="collect_all_projects")
def collect_all_projects() -> dict[str, int]:
    """
    Собрать данные обо всех проектах.

    Returns:
        Статистика сбора
    """
    logger.info("Starting projects collection task")

    # TODO: Реализовать асинхронный запуск
    # api_client = SferaAPIClient()
    # collector = SferaDataCollector(api_client)
    # projects = await collector.collect_projects()

    logger.info("Projects collection task completed")
    return {"collected": 0}


@celery_app.task(name="collect_repository_commits")
def collect_repository_commits(project_id: str, repository_id: str) -> dict[str, int]:
    """
    Собрать коммиты для репозитория.

    Args:
        project_id: ID проекта
        repository_id: ID репозитория

    Returns:
        Статистика сбора
    """
    logger.info(f"Starting commits collection for {project_id}/{repository_id}")

    # TODO: Реализовать сбор коммитов

    logger.info("Commits collection task completed")
    return {"collected": 0}


@celery_app.task(name="periodic_data_collection")
def periodic_data_collection() -> dict[str, int]:
    """
    Периодический сбор данных (запускается по расписанию).

    Returns:
        Статистика сбора
    """
    logger.info("Starting periodic data collection")

    # TODO: Реализовать периодический сбор всех данных

    logger.info("Periodic data collection completed")
    return {"projects": 0, "repositories": 0, "commits": 0}
