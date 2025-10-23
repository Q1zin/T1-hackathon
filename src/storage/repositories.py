"""Репозитории для работы с данными (SOLID: Single Responsibility)."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError, StorageError
from src.core.interfaces import IRepository
from src.core.logging import get_logger
from src.storage.models import Anomaly, Commit, Metric, Project, Recommendation, Repository
from src.storage.schemas import (
    CommitCreate,
    CommitResponse,
    MetricCreate,
    MetricResponse,
    ProjectCreate,
    ProjectResponse,
    RepositoryCreate,
    RepositoryResponse,
)

logger = get_logger(__name__)


class ProjectRepository(IRepository[ProjectResponse, int]):
    """Репозиторий для работы с проектами."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        self.session = session

    async def create(self, entity: ProjectCreate) -> ProjectResponse:
        """Создать проект."""
        try:
            project = Project(**entity.model_dump())
            self.session.add(project)
            await self.session.flush()
            await self.session.refresh(project)
            return ProjectResponse.model_validate(project)
        except Exception as e:
            logger.error(f"Failed to create project: {str(e)}")
            raise StorageError(f"Failed to create project: {str(e)}")

    async def get(self, id: int) -> ProjectResponse | None:
        """Получить проект по ID."""
        try:
            result = await self.session.execute(select(Project).where(Project.id == id))
            project = result.scalar_one_or_none()
            return ProjectResponse.model_validate(project) if project else None
        except Exception as e:
            logger.error(f"Failed to get project: {str(e)}")
            raise StorageError(f"Failed to get project: {str(e)}")

    async def update(self, id: int, entity: ProjectCreate) -> ProjectResponse | None:
        """Обновить проект."""
        try:
            result = await self.session.execute(select(Project).where(Project.id == id))
            project = result.scalar_one_or_none()
            if not project:
                return None

            for key, value in entity.model_dump(exclude_unset=True).items():
                setattr(project, key, value)

            await self.session.flush()
            await self.session.refresh(project)
            return ProjectResponse.model_validate(project)
        except Exception as e:
            logger.error(f"Failed to update project: {str(e)}")
            raise StorageError(f"Failed to update project: {str(e)}")

    async def delete(self, id: int) -> bool:
        """Удалить проект."""
        try:
            result = await self.session.execute(select(Project).where(Project.id == id))
            project = result.scalar_one_or_none()
            if not project:
                return False

            await self.session.delete(project)
            await self.session.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to delete project: {str(e)}")
            raise StorageError(f"Failed to delete project: {str(e)}")

    async def list(self, **filters: Any) -> list[ProjectResponse]:
        """Получить список проектов."""
        try:
            query = select(Project)
            # TODO: Добавить фильтрацию
            result = await self.session.execute(query)
            projects = result.scalars().all()
            return [ProjectResponse.model_validate(p) for p in projects]
        except Exception as e:
            logger.error(f"Failed to list projects: {str(e)}")
            raise StorageError(f"Failed to list projects: {str(e)}")


class RepositoryRepository(IRepository[RepositoryResponse, int]):
    """Репозиторий для работы с репозиториями."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        self.session = session

    async def create(self, entity: RepositoryCreate) -> RepositoryResponse:
        """Создать репозиторий."""
        try:
            repository = Repository(**entity.model_dump())
            self.session.add(repository)
            await self.session.flush()
            await self.session.refresh(repository)
            return RepositoryResponse.model_validate(repository)
        except Exception as e:
            logger.error(f"Failed to create repository: {str(e)}")
            raise StorageError(f"Failed to create repository: {str(e)}")

    async def get(self, id: int) -> RepositoryResponse | None:
        """Получить репозиторий по ID."""
        try:
            result = await self.session.execute(select(Repository).where(Repository.id == id))
            repository = result.scalar_one_or_none()
            return RepositoryResponse.model_validate(repository) if repository else None
        except Exception as e:
            logger.error(f"Failed to get repository: {str(e)}")
            raise StorageError(f"Failed to get repository: {str(e)}")

    async def update(self, id: int, entity: RepositoryCreate) -> RepositoryResponse | None:
        """Обновить репозиторий."""
        try:
            result = await self.session.execute(select(Repository).where(Repository.id == id))
            repository = result.scalar_one_or_none()
            if not repository:
                return None

            for key, value in entity.model_dump(exclude_unset=True).items():
                setattr(repository, key, value)

            await self.session.flush()
            await self.session.refresh(repository)
            return RepositoryResponse.model_validate(repository)
        except Exception as e:
            logger.error(f"Failed to update repository: {str(e)}")
            raise StorageError(f"Failed to update repository: {str(e)}")

    async def delete(self, id: int) -> bool:
        """Удалить репозиторий."""
        try:
            result = await self.session.execute(select(Repository).where(Repository.id == id))
            repository = result.scalar_one_or_none()
            if not repository:
                return False

            await self.session.delete(repository)
            await self.session.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to delete repository: {str(e)}")
            raise StorageError(f"Failed to delete repository: {str(e)}")

    async def list(self, **filters: Any) -> list[RepositoryResponse]:
        """Получить список репозиториев."""
        try:
            query = select(Repository)
            # TODO: Добавить фильтрацию по project_id и другим полям
            result = await self.session.execute(query)
            repositories = result.scalars().all()
            return [RepositoryResponse.model_validate(r) for r in repositories]
        except Exception as e:
            logger.error(f"Failed to list repositories: {str(e)}")
            raise StorageError(f"Failed to list repositories: {str(e)}")


class CommitRepository(IRepository[CommitResponse, int]):
    """Репозиторий для работы с коммитами."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        self.session = session

    async def create(self, entity: CommitCreate) -> CommitResponse:
        """Создать коммит."""
        try:
            commit = Commit(**entity.model_dump())
            self.session.add(commit)
            await self.session.flush()
            await self.session.refresh(commit)
            return CommitResponse.model_validate(commit)
        except Exception as e:
            logger.error(f"Failed to create commit: {str(e)}")
            raise StorageError(f"Failed to create commit: {str(e)}")

    async def get(self, id: int) -> CommitResponse | None:
        """Получить коммит по ID."""
        try:
            result = await self.session.execute(select(Commit).where(Commit.id == id))
            commit = result.scalar_one_or_none()
            return CommitResponse.model_validate(commit) if commit else None
        except Exception as e:
            logger.error(f"Failed to get commit: {str(e)}")
            raise StorageError(f"Failed to get commit: {str(e)}")

    async def update(self, id: int, entity: CommitCreate) -> CommitResponse | None:
        """Обновить коммит."""
        try:
            result = await self.session.execute(select(Commit).where(Commit.id == id))
            commit = result.scalar_one_or_none()
            if not commit:
                return None

            for key, value in entity.model_dump(exclude_unset=True).items():
                setattr(commit, key, value)

            await self.session.flush()
            await self.session.refresh(commit)
            return CommitResponse.model_validate(commit)
        except Exception as e:
            logger.error(f"Failed to update commit: {str(e)}")
            raise StorageError(f"Failed to update commit: {str(e)}")

    async def delete(self, id: int) -> bool:
        """Удалить коммит."""
        try:
            result = await self.session.execute(select(Commit).where(Commit.id == id))
            commit = result.scalar_one_or_none()
            if not commit:
                return False

            await self.session.delete(commit)
            await self.session.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to delete commit: {str(e)}")
            raise StorageError(f"Failed to delete commit: {str(e)}")

    async def list(self, **filters: Any) -> list[CommitResponse]:
        """Получить список коммитов."""
        try:
            query = select(Commit)
            # TODO: Добавить фильтрацию
            result = await self.session.execute(query)
            commits = result.scalars().all()
            return [CommitResponse.model_validate(c) for c in commits]
        except Exception as e:
            logger.error(f"Failed to list commits: {str(e)}")
            raise StorageError(f"Failed to list commits: {str(e)}")


class MetricRepository(IRepository[MetricResponse, int]):
    """Репозиторий для работы с метриками."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория."""
        self.session = session

    async def create(self, entity: MetricCreate) -> MetricResponse:
        """Создать метрику."""
        try:
            metric = Metric(**entity.model_dump())
            self.session.add(metric)
            await self.session.flush()
            await self.session.refresh(metric)
            return MetricResponse.model_validate(metric)
        except Exception as e:
            logger.error(f"Failed to create metric: {str(e)}")
            raise StorageError(f"Failed to create metric: {str(e)}")

    async def get(self, id: int) -> MetricResponse | None:
        """Получить метрику по ID."""
        try:
            result = await self.session.execute(select(Metric).where(Metric.id == id))
            metric = result.scalar_one_or_none()
            return MetricResponse.model_validate(metric) if metric else None
        except Exception as e:
            logger.error(f"Failed to get metric: {str(e)}")
            raise StorageError(f"Failed to get metric: {str(e)}")

    async def update(self, id: int, entity: MetricCreate) -> MetricResponse | None:
        """Обновить метрику."""
        try:
            result = await self.session.execute(select(Metric).where(Metric.id == id))
            metric = result.scalar_one_or_none()
            if not metric:
                return None

            for key, value in entity.model_dump(exclude_unset=True).items():
                setattr(metric, key, value)

            await self.session.flush()
            await self.session.refresh(metric)
            return MetricResponse.model_validate(metric)
        except Exception as e:
            logger.error(f"Failed to update metric: {str(e)}")
            raise StorageError(f"Failed to update metric: {str(e)}")

    async def delete(self, id: int) -> bool:
        """Удалить метрику."""
        try:
            result = await self.session.execute(select(Metric).where(Metric.id == id))
            metric = result.scalar_one_or_none()
            if not metric:
                return False

            await self.session.delete(metric)
            await self.session.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to delete metric: {str(e)}")
            raise StorageError(f"Failed to delete metric: {str(e)}")

    async def list(self, **filters: Any) -> list[MetricResponse]:
        """Получить список метрик."""
        try:
            query = select(Metric)
            # TODO: Добавить фильтрацию
            result = await self.session.execute(query)
            metrics = result.scalars().all()
            return [MetricResponse.model_validate(m) for m in metrics]
        except Exception as e:
            logger.error(f"Failed to list metrics: {str(e)}")
            raise StorageError(f"Failed to list metrics: {str(e)}")
