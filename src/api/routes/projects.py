"""API эндпоинты для работы с проектами."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.database import get_db
from src.storage.repositories import ProjectRepository
from src.storage.schemas import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)) -> list[ProjectResponse]:
    """Получить список всех проектов."""
    repo = ProjectRepository(db)
    return await repo.list()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)) -> ProjectResponse:
    """Получить проект по ID."""
    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate, db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Создать новый проект."""
    repo = ProjectRepository(db)
    return await repo.create(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int, project: ProjectCreate, db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Обновить проект."""
    repo = ProjectRepository(db)
    updated = await repo.update(project_id, project)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Удалить проект."""
    repo = ProjectRepository(db)
    deleted = await repo.delete(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
