import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import get_settings
from src.core.logging import get_logger
from src.data_collection.api_client import SferaAPIClient
from src.data_collection.collectors import SferaDataCollector
from src.storage.models import Commit, Project, Repository
from src.storage.repositories import CommitRepository, ProjectRepository, RepositoryRepository
from src.storage.schemas import CommitCreate, ProjectCreate, RepositoryCreate
from src.tasks.celery_app import celery_app

logger = get_logger(__name__)

_engine = None
_async_session_maker = None


def get_async_session_maker():
    global _engine, _async_session_maker
    if _async_session_maker is None:
        settings = get_settings()
        _engine = create_async_engine(
            str(settings.database_url),
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        _async_session_maker = async_sessionmaker(_engine, expire_on_commit=False)
    return _async_session_maker


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        try:
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
    logger.info("Starting projects collection task")
    return run_async(_collect_all_projects_async())


async def _collect_all_projects_async() -> dict[str, int]:
    api_client = SferaAPIClient()
    collector = SferaDataCollector(api_client)

    session_maker = get_async_session_maker()
    async with session_maker() as session:
        project_repo = ProjectRepository(session)
        repo_repo = RepositoryRepository(session)

        projects_count = 0
        repos_count = 0

        try:
            logger.info("Fetching projects from Sfera API")
            projects_data = await collector.collect_projects()
            projects = projects_data["projects"]
            logger.info(f"Found {len(projects)} projects")

            for project in projects:
                project_key = project["name"]
                result = await session.execute(
                    select(Project).where(Project.external_id == project_key)
                )
                existing_project = result.scalar_one_or_none()

                if existing_project:
                    db_project_id = existing_project.id
                else:
                    project_create = ProjectCreate(
                        external_id=project_key,
                        name=project.get("full_name", project_key),
                        description=project.get("description"),
                        is_public=project.get("public", False),
                        extra_data={"links": project.get("links")}
                    )
                    db_project = await project_repo.create(project_create)
                    db_project_id = db_project.id
                    projects_count += 1
                    logger.info(f"Created project: {project.get('full_name', project_key)}")

                repos_data = await collector.collect_repositories(project_key)
                repositories = repos_data["repositories"]

                for repo in repositories:
                    repo_slug = repo.get("slug") or repo.get("name")
                    result = await session.execute(
                        select(Repository).where(
                            Repository.project_id == db_project_id,
                            Repository.external_id == repo_slug
                        )
                    )
                    existing_repo = result.scalar_one_or_none()

                    if not existing_repo:
                        repo_create = RepositoryCreate(
                            external_id=repo_slug,
                            project_id=db_project_id,
                            name=repo.get("name", repo_slug),
                            description=repo.get("description"),
                            default_branch=repo.get("default_branch"),
                            clone_url=repo.get("links", {}).get("clone", [{}])[0].get("href"),
                            is_fork=repo.get("is_fork", False),
                            extra_data={"forkable": repo.get("forkable"), "links": repo.get("links")}
                        )
                        await repo_repo.create(repo_create)
                        repos_count += 1

            await session.commit()
            logger.info(f"Projects collection completed: {projects_count} projects, {repos_count} repos")
            return {"projects": projects_count, "repositories": repos_count}

        except Exception as e:
            logger.error(f"Error during projects collection: {str(e)}")
            await session.rollback()
            raise


@celery_app.task(name="collect_repository_commits")
def collect_repository_commits(project_key: str, repo_slug: str) -> dict[str, int]:
    logger.info(f"Starting commits collection for {project_key}/{repo_slug}")
    return run_async(_collect_repository_commits_async(project_key, repo_slug))


async def _collect_repository_commits_async(project_key: str, repo_slug: str) -> dict[str, int]:
    api_client = SferaAPIClient()
    collector = SferaDataCollector(api_client)

    session_maker = get_async_session_maker()
    async with session_maker() as session:
        commit_repo = CommitRepository(session)
        commits_count = 0

        try:
            project_result = await session.execute(
                select(Project).where(Project.external_id == project_key)
            )
            project = project_result.scalar_one_or_none()
            if not project:
                logger.error(f"Project {project_key} not found")
                return {"collected": 0, "error": "Project not found"}

            result = await session.execute(
                select(Repository).where(
                    Repository.project_id == project.id,
                    Repository.external_id == repo_slug
                )
            )
            repository = result.scalar_one_or_none()
            if not repository:
                logger.error(f"Repository {project_key}/{repo_slug} not found")
                return {"collected": 0, "error": "Repository not found"}

            commits_data = await collector.collect_commits(project_key, repo_slug)
            all_commits = commits_data["commits"]
            logger.info(f"Found {len(all_commits)} commits")

            for commit in all_commits:
                commit_id = commit.get("id") or commit.get("sha") or commit.get("hash")
                result = await session.execute(
                    select(Commit).where(
                        Commit.external_id == commit_id,
                        Commit.repository_id == repository.id
                    )
                )
                if result.scalar_one_or_none():
                    continue

                diff_base64 = None
                try:
                    diff_data = await collector.collect_commit_diff(project_key, repo_slug, commit_id)
                    if "data" in diff_data and "content" in diff_data["data"]:
                        diff_base64 = diff_data["data"]["content"]
                except Exception as e:
                    logger.warning(f"Failed to collect diff for {commit_id}: {str(e)}")

                author = commit.get("author", {})
                committer = commit.get("committer", {})

                committer_timestamp = commit.get("committer_timestamp")
                author_timestamp = commit.get("author_timestamp")

                if committer_timestamp:
                    committed_at = datetime.fromtimestamp(committer_timestamp / 1000, tz=timezone.utc)
                elif "created_at" in commit:
                    from dateutil import parser
                    committed_at = parser.parse(commit["created_at"])
                else:
                    committed_at = datetime.now(timezone.utc)

                if author_timestamp:
                    authored_at = datetime.fromtimestamp(author_timestamp / 1000, tz=timezone.utc)
                else:
                    authored_at = committed_at

                commit_create = CommitCreate(
                    external_id=commit_id,
                    repository_id=repository.id,
                    author_name=author.get("name", "Unknown"),
                    author_email=author.get("email_address") or author.get("email", "unknown@example.com"),
                    committer_name=committer.get("name", "Unknown"),
                    committer_email=committer.get("email_address") or committer.get("email", "unknown@example.com"),
                    message=commit.get("message", ""),
                    authored_date=authored_at,
                    committed_at=committed_at,
                    diff_base64=diff_base64,
                    branch_names=commit.get("branch_names"),
                    parent_shas=commit.get("parents"),
                    extra_data={
                        "display_id": commit.get("display_id"),
                        "tag_names": commit.get("tag_names"),
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
