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
