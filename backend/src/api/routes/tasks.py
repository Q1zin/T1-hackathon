from fastapi import APIRouter
from pydantic import BaseModel

from src.core.logging import get_logger
from src.tasks.collection_tasks import (
    collect_all_projects,
    collect_repository_commits,
)

logger = get_logger(__name__)

router = APIRouter()


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None


@router.post("/collect/projects", response_model=TaskResponse)
async def trigger_projects_collection() -> TaskResponse:
    logger.info("Projects collection triggered")
    task = collect_all_projects.delay()
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message="Projects collection queued"
    )


@router.post("/collect/commits/{project_key}/{repo_slug}", response_model=TaskResponse)
async def trigger_commits_collection(project_key: str, repo_slug: str) -> TaskResponse:
    logger.info(f"Commits collection triggered for {project_key}/{repo_slug}")
    task = collect_repository_commits.delay(project_key, repo_slug)
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message=f"Commits collection for {project_key}/{repo_slug} queued"
    )


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    from celery.result import AsyncResult
    from src.tasks.celery_app import celery_app

    task_result = AsyncResult(task_id, app=celery_app)
    return TaskStatusResponse(
        task_id=task_id,
        status=task_result.status,
        result=task_result.result if task_result.ready() else None
    )


class DBStatsResponse(BaseModel):
    projects_count: int
    repositories_count: int
    commits_count: int
    commits_by_email: dict[str, int]


@router.get("/db-stats", response_model=DBStatsResponse)
async def get_db_stats() -> DBStatsResponse:
    """
    Получить статистику по данным в БД (для диагностики).

    Returns:
        Статистика: количество проектов, репозиториев, коммитов
    """
    from sqlalchemy import func, select
    from src.storage.database import get_db
    from src.storage.models import Commit, Project, Repository

    async for db in get_db():
        # Подсчет проектов
        projects_result = await db.execute(select(func.count(Project.id)))
        projects_count = projects_result.scalar() or 0

        # Подсчет репозиториев
        repos_result = await db.execute(select(func.count(Repository.id)))
        repos_count = repos_result.scalar() or 0

        # Подсчет коммитов
        commits_result = await db.execute(select(func.count(Commit.id)))
        commits_count = commits_result.scalar() or 0

        # Подсчет коммитов по email
        commits_by_email_result = await db.execute(
            select(
                Commit.author_email,
                func.count(Commit.id).label("count")
            )
            .group_by(Commit.author_email)
            .order_by(func.count(Commit.id).desc())
            .limit(10)
        )
        commits_by_email = {
            row.author_email: row.count
            for row in commits_by_email_result.all()
        }

        return DBStatsResponse(
            projects_count=projects_count,
            repositories_count=repos_count,
            commits_count=commits_count,
            commits_by_email=commits_by_email
        )
