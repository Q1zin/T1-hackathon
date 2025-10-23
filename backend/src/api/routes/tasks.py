"""API endpoints для управления задачами."""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from src.core.logging import get_logger
from src.tasks.collection_tasks import (
    collect_all_projects,
    collect_repository_commits,
    periodic_data_collection,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskResponse(BaseModel):
    """Ответ о запуске задачи."""

    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Статус задачи."""

    task_id: str
    status: str
    result: dict | None = None


@router.post("/collect/trigger", response_model=TaskResponse)
async def trigger_data_collection() -> TaskResponse:
    """
    Запустить полный сбор данных вручную.

    Эндпоинт запускает задачу сбора всех проектов, репозиториев и коммитов.
    Задача выполняется асинхронно в Celery.

    Returns:
        Информация о запущенной задаче
    """
    logger.info("Manual data collection triggered via API")

    # Запускаем задачу через Celery
    task = periodic_data_collection.delay()

    return TaskResponse(
        task_id=task.id,
        status="queued",
        message="Data collection task has been queued for execution"
    )


@router.post("/collect/projects", response_model=TaskResponse)
async def trigger_projects_collection() -> TaskResponse:
    """
    Запустить сбор проектов и репозиториев вручную.

    Собирает только проекты и репозитории, без коммитов.

    Returns:
        Информация о запущенной задаче
    """
    logger.info("Manual projects collection triggered via API")

    task = collect_all_projects.delay()

    return TaskResponse(
        task_id=task.id,
        status="queued",
        message="Projects collection task has been queued for execution"
    )


@router.post("/collect/commits/{project_key}/{repo_slug}", response_model=TaskResponse)
async def trigger_commits_collection(project_key: str, repo_slug: str) -> TaskResponse:
    """
    Запустить сбор коммитов для конкретного репозитория.

    Args:
        project_key: Ключ проекта
        repo_slug: Slug репозитория

    Returns:
        Информация о запущенной задаче
    """
    logger.info(f"Manual commits collection triggered for {project_key}/{repo_slug}")

    task = collect_repository_commits.delay(project_key, repo_slug)

    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Commits collection task for {project_key}/{repo_slug} has been queued"
    )


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Получить статус задачи по ID.

    Args:
        task_id: ID задачи Celery

    Returns:
        Статус задачи и результат (если доступен)
    """
    from celery.result import AsyncResult
    from src.tasks.celery_app import celery_app

    task_result = AsyncResult(task_id, app=celery_app)

    response = TaskStatusResponse(
        task_id=task_id,
        status=task_result.status,
        result=task_result.result if task_result.ready() else None
    )

    return response
