"""Задачи для сбора данных."""

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import get_settings
from src.core.logging import get_logger
from src.data_collection.api_client import SferaAPIClient
from src.data_collection.collectors import SferaDataCollector
from src.storage.models import Commit, Project, Repository
from src.storage.repositories import CommitRepository, ProjectRepository, RepositoryRepository
from src.storage.schemas import CommitCreate, ProjectCreate, RepositoryCreate
from src.tasks.celery_app import celery_app

logger = get_logger(__name__)


def get_async_session():
    """Создать новую async session для текущего event loop."""
    settings = get_settings()
    engine = create_async_engine(
        str(settings.database_url),
        echo=False,
        pool_pre_ping=True,
    )
    return async_sessionmaker(engine, expire_on_commit=False)()


def run_async(coro):
    """Запустить async корутину в синхронном контексте."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        try:
            # Cleanup pending tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            pass
        finally:
            asyncio.set_event_loop(None)
            loop.close()


@celery_app.task(name="collect_all_projects")
def collect_all_projects() -> dict[str, int]:
    """
    Собрать данные обо всех проектах.

    Returns:
        Статистика сбора
    """
    logger.info("Starting projects collection task")
    return run_async(_collect_all_projects_async())


async def _collect_all_projects_async() -> dict[str, int]:
    """Асинхронная реализация сбора проектов."""
    api_client = SferaAPIClient()
    collector = SferaDataCollector(api_client)

    session = get_async_session()
    async with session:
        project_repo = ProjectRepository(session)
        repo_repo = RepositoryRepository(session)

        projects_count = 0
        repos_count = 0

        try:
            # Собираем проекты из API
            logger.info("Fetching projects from Sfera API")
            projects_data = await collector.collect_projects()
            projects = projects_data["projects"]
            logger.info(f"Found {len(projects)} projects")

            for project in projects:
                # Проверяем, есть ли проект в БД
                project_key = project["name"]
                result = await session.execute(
                    select(Project).where(Project.external_id == project_key)
                )
                existing_project = result.scalar_one_or_none()

                if existing_project:
                    logger.debug(f"Project {project.get('full_name', project_key)} already exists, skipping")
                    db_project_id = existing_project.id
                else:
                    # Создаём проект
                    project_create = ProjectCreate(
                        external_id=project_key,
                        name=project.get("full_name", project_key),
                        description=project.get("description"),
                        extra_data={"public": project.get("public"), "links": project.get("links")}
                    )
                    db_project = await project_repo.create(project_create)
                    db_project_id = db_project.id
                    projects_count += 1
                    logger.info(f"Created project: {project.get('full_name', project_key)}")

                # Собираем репозитории проекта
                logger.info(f"Fetching repositories for project {project_key}")
                repos_data = await collector.collect_repositories(project_key)
                repositories = repos_data["repositories"]
                logger.info(f"Found {len(repositories)} repositories in {project_key}")

                for repo in repositories:
                    # Проверяем, есть ли репозиторий в БД
                    # Slug может быть в поле "slug" или "name"
                    repo_slug = repo.get("slug") or repo.get("name")
                    result = await session.execute(
                        select(Repository).where(
                            Repository.project_id == db_project_id,
                            Repository.external_id == repo_slug
                        )
                    )
                    existing_repo = result.scalar_one_or_none()

                    if existing_repo:
                        logger.debug(f"Repository {repo.get('name', repo_slug)} already exists, skipping")
                    else:
                        # Создаём репозиторий
                        repo_create = RepositoryCreate(
                            external_id=repo_slug,
                            project_id=db_project_id,
                            name=repo.get("name", repo_slug),
                            default_branch=repo.get("default_branch"),
                            extra_data={
                                "description": repo.get("description"),
                                "public": repo.get("public"),
                                "forkable": repo.get("forkable"),
                                "links": repo.get("links")
                            }
                        )
                        await repo_repo.create(repo_create)
                        repos_count += 1
                        logger.info(f"Created repository: {repo.get('name', repo_slug)}")

            await session.commit()
            logger.info(f"Projects collection completed: {projects_count} projects, {repos_count} repos")
            return {"projects": projects_count, "repositories": repos_count}

        except Exception as e:
            logger.error(f"Error during projects collection: {str(e)}")
            await session.rollback()
            raise


@celery_app.task(name="collect_repository_commits")
def collect_repository_commits(project_key: str, repo_slug: str) -> dict[str, int]:
    """
    Собрать коммиты для репозитория.

    Args:
        project_key: Key проекта
        repo_slug: Slug репозитория

    Returns:
        Статистика сбора
    """
    logger.info(f"Starting commits collection for {project_key}/{repo_slug}")
    return run_async(_collect_repository_commits_async(project_key, repo_slug))


async def _collect_repository_commits_async(project_key: str, repo_slug: str) -> dict[str, int]:
    """Асинхронная реализация сбора коммитов."""
    api_client = SferaAPIClient()
    collector = SferaDataCollector(api_client)

    session = get_async_session()
    async with session:
        commit_repo = CommitRepository(session)
        commits_count = 0

        try:
            # Находим проект в БД
            project_result = await session.execute(
                select(Project).where(Project.external_id == project_key)
            )
            project = project_result.scalar_one_or_none()

            if not project:
                logger.error(f"Project {project_key} not found in database")
                return {"collected": 0, "error": "Project not found"}

            # Находим репозиторий в БД
            result = await session.execute(
                select(Repository).where(
                    Repository.project_id == project.id,
                    Repository.external_id == repo_slug
                )
            )
            repository = result.scalar_one_or_none()

            if not repository:
                logger.error(f"Repository {project_key}/{repo_slug} not found in database")
                return {"collected": 0, "error": "Repository not found"}

            # ИНКРЕМЕНТАЛЬНАЯ ЗАГРУЗКА: Получаем последний коммит из БД
            last_commit_result = await session.execute(
                select(Commit)
                .where(Commit.repository_id == repository.id)
                .order_by(Commit.committed_at.desc())
                .limit(1)
            )
            last_commit = last_commit_result.scalar_one_or_none()

            if last_commit:
                logger.info(f"Incremental load: fetching commits after last commit at {last_commit.committed_at}")
            else:
                logger.info("Full load: fetching all commits")

            # Собираем коммиты из API (пока без фильтра по дате - API может не поддерживать)
            commits_data = await collector.collect_commits(
                project_key,
                repo_slug
            )
            all_commits = commits_data["commits"]
            logger.info(f"Found {len(all_commits)} commits for {project_key}/{repo_slug}")

            for commit in all_commits:
                # Проверяем, есть ли коммит в БД
                # API возвращает SHA коммита (может быть "id", "sha", или "hash")
                commit_id = commit.get("id") or commit.get("sha") or commit.get("hash")
                result = await session.execute(
                    select(Commit).where(
                        Commit.external_id == commit_id,
                        Commit.repository_id == repository.id
                    )
                )
                existing_commit = result.scalar_one_or_none()

                if existing_commit:
                    logger.debug(f"Commit {commit_id} already exists, skipping")
                    continue

                # Получаем diff для коммита
                diff_base64 = None
                try:
                    diff_data = await collector.collect_commit_diff(project_key, repo_slug, commit_id)
                    # API возвращает структуру с data.content в base64
                    if "data" in diff_data and "content" in diff_data["data"]:
                        diff_base64 = diff_data["data"]["content"]
                        logger.debug(f"Collected diff for commit {commit_id} ({len(diff_base64)} chars)")
                except Exception as e:
                    logger.warning(f"Failed to collect diff for commit {commit_id}: {str(e)}")

                # Создаём коммит
                author = commit.get("author", {})
                committer = commit.get("committer", {})

                # Получаем timestamp из разных возможных полей
                committer_timestamp = commit.get("committer_timestamp")
                if not committer_timestamp and "created_at" in commit:
                    # Парсим ISO формат даты
                    from dateutil import parser
                    committed_at = parser.parse(commit["created_at"])
                else:
                    committed_at = datetime.fromtimestamp(committer_timestamp / 1000, tz=timezone.utc) if committer_timestamp else datetime.now(timezone.utc)

                commit_create = CommitCreate(
                    external_id=commit_id,
                    repository_id=repository.id,
                    author_name=author.get("name", "Unknown"),
                    author_email=author.get("email_address") or author.get("email", "unknown@example.com"),
                    message=commit.get("message", ""),
                    committed_at=committed_at,
                    diff_base64=diff_base64,
                    branch_names=commit.get("branch_names"),
                    parent_shas=commit.get("parents"),
                    extra_data={
                        "display_id": commit.get("display_id"),
                        "tag_names": commit.get("tag_names"),
                        "committer": {
                            "name": committer.get("name"),
                            "email": committer.get("email_address") or committer.get("email")
                        }
                    }
                )
                await commit_repo.create(commit_create)
                commits_count += 1

            await session.commit()
            logger.info(f"Commits collection completed: {commits_count} new commits")
            return {"collected": commits_count}

        except Exception as e:
            logger.error(f"Error during commits collection: {str(e)}")
            await session.rollback()
            raise


@celery_app.task(name="periodic_data_collection")
def periodic_data_collection() -> dict[str, int]:
    """
    Периодический сбор данных (запускается по расписанию).

    Returns:
        Статистика сбора
    """
    logger.info("Starting periodic data collection")
    return run_async(_periodic_data_collection_async())


async def _periodic_data_collection_async() -> dict[str, int]:
    """Асинхронная реализация периодического сбора."""
    logger.info("Running full data collection cycle")

    # Сначала собираем проекты и репозитории
    projects_stats = await _collect_all_projects_async()

    # Затем собираем коммиты для всех репозиториев
    session = get_async_session()
    async with session:
        # Получаем репозитории с информацией о проекте
        result = await session.execute(
            select(Repository, Project).join(Project, Repository.project_id == Project.id)
        )
        repo_project_pairs = result.all()

        total_commits = 0
        for repo, project in repo_project_pairs:
            project_key = project.external_id
            repo_slug = repo.external_id

            try:
                commits_stats = await _collect_repository_commits_async(project_key, repo_slug)
                total_commits += commits_stats.get("collected", 0)
            except Exception as e:
                logger.error(f"Failed to collect commits for {project_key}/{repo_slug}: {str(e)}")

    result = {
        "projects": projects_stats.get("projects", 0),
        "repositories": projects_stats.get("repositories", 0),
        "commits": total_commits
    }
    logger.info(f"Periodic collection completed: {result}")
    return result
