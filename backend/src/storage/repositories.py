from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import StorageError
from src.core.interfaces import IRepository
from src.core.logging import get_logger
from src.storage.models import Commit, Metric, Project, Repository
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
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity: ProjectCreate) -> ProjectResponse:
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
        try:
            result = await self.session.execute(select(Project).where(Project.id == id))
            project = result.scalar_one_or_none()
            return ProjectResponse.model_validate(project) if project else None
        except Exception as e:
            logger.error(f"Failed to get project: {str(e)}")
            raise StorageError(f"Failed to get project: {str(e)}")

    async def update(self, id: int, entity: ProjectCreate) -> ProjectResponse | None:
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
        try:
            query = select(Project)

            if "is_public" in filters:
                query = query.where(Project.is_public == filters["is_public"])
            if "limit" in filters:
                query = query.limit(filters["limit"])
            if "offset" in filters:
                query = query.offset(filters["offset"])

            result = await self.session.execute(query)
            projects = result.scalars().all()
            return [ProjectResponse.model_validate(p) for p in projects]
        except Exception as e:
            logger.error(f"Failed to list projects: {str(e)}")
            raise StorageError(f"Failed to list projects: {str(e)}")


class RepositoryRepository(IRepository[RepositoryResponse, int]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity: RepositoryCreate) -> RepositoryResponse:
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
        try:
            result = await self.session.execute(select(Repository).where(Repository.id == id))
            repository = result.scalar_one_or_none()
            return RepositoryResponse.model_validate(repository) if repository else None
        except Exception as e:
            logger.error(f"Failed to get repository: {str(e)}")
            raise StorageError(f"Failed to get repository: {str(e)}")

    async def update(self, id: int, entity: RepositoryCreate) -> RepositoryResponse | None:
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
        try:
            query = select(Repository)

            if "project_id" in filters:
                query = query.where(Repository.project_id == filters["project_id"])
            if "is_fork" in filters:
                query = query.where(Repository.is_fork == filters["is_fork"])
            if "limit" in filters:
                query = query.limit(filters["limit"])
            if "offset" in filters:
                query = query.offset(filters["offset"])

            result = await self.session.execute(query)
            repositories = result.scalars().all()
            return [RepositoryResponse.model_validate(r) for r in repositories]
        except Exception as e:
            logger.error(f"Failed to list repositories: {str(e)}")
            raise StorageError(f"Failed to list repositories: {str(e)}")


class CommitRepository(IRepository[CommitResponse, int]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity: CommitCreate) -> CommitResponse:
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
        try:
            result = await self.session.execute(select(Commit).where(Commit.id == id))
            commit = result.scalar_one_or_none()
            return CommitResponse.model_validate(commit) if commit else None
        except Exception as e:
            logger.error(f"Failed to get commit: {str(e)}")
            raise StorageError(f"Failed to get commit: {str(e)}")

    async def update(self, id: int, entity: CommitCreate) -> CommitResponse | None:
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
        try:
            query = select(Commit)

            if "repository_id" in filters:
                query = query.where(Commit.repository_id == filters["repository_id"])
            if "author_email" in filters:
                query = query.where(Commit.author_email == filters["author_email"])
            if "since" in filters:
                query = query.where(Commit.committed_at >= filters["since"])
            if "until" in filters:
                query = query.where(Commit.committed_at <= filters["until"])
            if "limit" in filters:
                query = query.limit(filters["limit"])
            if "offset" in filters:
                query = query.offset(filters["offset"])

            query = query.order_by(Commit.committed_at.desc())

            result = await self.session.execute(query)
            commits = result.scalars().all()
            return [CommitResponse.model_validate(c) for c in commits]
        except Exception as e:
            logger.error(f"Failed to list commits: {str(e)}")
            raise StorageError(f"Failed to list commits: {str(e)}")


class MetricRepository(IRepository[MetricResponse, int]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity: MetricCreate) -> MetricResponse:
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
        try:
            result = await self.session.execute(select(Metric).where(Metric.id == id))
            metric = result.scalar_one_or_none()
            return MetricResponse.model_validate(metric) if metric else None
        except Exception as e:
            logger.error(f"Failed to get metric: {str(e)}")
            raise StorageError(f"Failed to get metric: {str(e)}")

    async def update(self, id: int, entity: MetricCreate) -> MetricResponse | None:
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
        try:
            query = select(Metric)

            if "repository_id" in filters:
                query = query.where(Metric.repository_id == filters["repository_id"])
            if "metric_type" in filters:
                query = query.where(Metric.metric_type == filters["metric_type"])
            if "metric_name" in filters:
                query = query.where(Metric.metric_name == filters["metric_name"])
            if "since" in filters:
                query = query.where(Metric.calculated_at >= filters["since"])
            if "until" in filters:
                query = query.where(Metric.calculated_at <= filters["until"])
            if "limit" in filters:
                query = query.limit(filters["limit"])
            if "offset" in filters:
                query = query.offset(filters["offset"])

            query = query.order_by(Metric.calculated_at.desc())

            result = await self.session.execute(query)
            metrics = result.scalars().all()
            return [MetricResponse.model_validate(m) for m in metrics]
        except Exception as e:
            logger.error(f"Failed to list metrics: {str(e)}")
            raise StorageError(f"Failed to list metrics: {str(e)}")
