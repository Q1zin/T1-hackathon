"""Сборщики данных из API (SOLID: Single Responsibility)."""

from typing import Any

from src.core.exceptions import DataCollectionError
from src.core.interfaces import IAPIClient, IDataCollector
from src.core.logging import get_logger

logger = get_logger(__name__)


class SferaDataCollector(IDataCollector):
    """Сборщик данных из T1 Сфера.Код API."""

    def __init__(self, api_client: IAPIClient) -> None:
        """
        Инициализация сборщика.

        Args:
            api_client: Клиент для работы с API
        """
        self.api_client = api_client

    async def collect_projects(
        self, limit: int = 100, cursor: str | None = None, sort: str = "name", order: str = "asc"
    ) -> dict[str, Any]:
        """
        Собрать данные о всех проектах.

        Args:
            limit: Размер страницы (по умолчанию 100)
            cursor: Курсор для пагинации
            sort: Поле для сортировки (name, created_at, updated_at)
            order: Порядок сортировки (asc, desc)

        Returns:
            Словарь с данными: {"projects": [...], "page_info": {...}}

        Raises:
            DataCollectionError: При ошибке сбора данных
        """
        try:
            logger.info("Collecting projects data")

            params: dict[str, Any] = {"limit": limit, "sort": sort, "order": order}
            if cursor:
                params["cursor"] = cursor

            response = await self.api_client.get("projects", **params)

            projects = response.get("data", [])
            page_info = response.get("page", {})

            logger.info(f"Collected {len(projects)} projects")
            return {"projects": projects, "page_info": page_info}

        except Exception as e:
            logger.error(f"Failed to collect projects: {str(e)}")
            raise DataCollectionError(f"Failed to collect projects: {str(e)}")

    async def collect_repositories(
        self, project_key: str, limit: int = 100, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Собрать данные о репозиториях проекта.

        Args:
            project_key: Ключ проекта (projectKey)
            limit: Размер страницы
            cursor: Курсор для пагинации

        Returns:
            Словарь с данными: {"repositories": [...], "page_info": {...}}

        Raises:
            DataCollectionError: При ошибке сбора данных
        """
        try:
            logger.info(f"Collecting repositories for project {project_key}")

            params: dict[str, Any] = {"limit": limit}
            if cursor:
                params["cursor"] = cursor

            response = await self.api_client.get(f"projects/{project_key}/repos", **params)

            repositories = response.get("data", [])
            page_info = response.get("page", {})

            logger.info(f"Collected {len(repositories)} repositories")
            return {"repositories": repositories, "page_info": page_info}

        except Exception as e:
            logger.error(f"Failed to collect repositories: {str(e)}")
            raise DataCollectionError(f"Failed to collect repositories: {str(e)}")

    async def collect_commits(
        self,
        project_key: str,
        repo_name: str,
        ref_name: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Собрать данные о коммитах.

        Args:
            project_key: Ключ проекта
            repo_name: Имя репозитория
            ref_name: Имя ветки (опционально)
            limit: Размер страницы
            cursor: Курсор для пагинации

        Returns:
            Словарь с данными: {"commits": [...], "page_info": {...}}

        Raises:
            DataCollectionError: При ошибке сбора данных
        """
        try:
            logger.info(
                f"Collecting commits for project {project_key}, "
                f"repository {repo_name}, ref {ref_name or 'default'}"
            )

            params: dict[str, Any] = {"limit": limit}
            if cursor:
                params["cursor"] = cursor
            if ref_name:
                params["rev"] = ref_name  # Используем 'rev' согласно Swagger API

            response = await self.api_client.get(
                f"projects/{project_key}/repos/{repo_name}/commits", **params
            )

            commits = response.get("data", [])
            page_info = response.get("page", {})

            logger.info(f"Collected {len(commits)} commits")
            return {"commits": commits, "page_info": page_info}

        except Exception as e:
            logger.error(f"Failed to collect commits: {str(e)}")
            raise DataCollectionError(f"Failed to collect commits: {str(e)}")

    async def collect_commit_diff(
        self, project_key: str, repo_name: str, commit_sha: str
    ) -> dict[str, Any]:
        """
        Собрать diff коммита.

        Args:
            project_key: Ключ проекта
            repo_name: Имя репозитория
            commit_sha: SHA коммита

        Returns:
            Diff коммита с детальной информацией

        Raises:
            DataCollectionError: При ошибке сбора данных
        """
        try:
            logger.info(
                f"Collecting commit diff for project {project_key}, "
                f"repository {repo_name}, commit {commit_sha}"
            )

            response = await self.api_client.get(
                f"projects/{project_key}/repos/{repo_name}/commits/{commit_sha}"
            )

            logger.info("Collected commit diff")
            return response

        except Exception as e:
            logger.error(f"Failed to collect commit diff: {str(e)}")
            raise DataCollectionError(f"Failed to collect commit diff: {str(e)}")

    async def collect_project_info(self, project_key: str) -> dict[str, Any]:
        """
        Получить информацию о проекте.

        Args:
            project_key: Ключ проекта

        Returns:
            Информация о проекте

        Raises:
            DataCollectionError: При ошибке сбора данных
        """
        try:
            logger.info(f"Collecting project info for {project_key}")
            response = await self.api_client.get(f"projects/{project_key}")
            logger.info(f"Collected info for project {project_key}")
            return response

        except Exception as e:
            logger.error(f"Failed to collect project info: {str(e)}")
            raise DataCollectionError(f"Failed to collect project info: {str(e)}")

    async def collect_repository_info(
        self, project_key: str, repo_name: str
    ) -> dict[str, Any]:
        """
        Получить информацию о репозитории.

        Args:
            project_key: Ключ проекта
            repo_name: Имя репозитория

        Returns:
            Информация о репозитории

        Raises:
            DataCollectionError: При ошибке сбора данных
        """
        try:
            logger.info(f"Collecting repository info for {project_key}/{repo_name}")
            response = await self.api_client.get(f"projects/{project_key}/repos/{repo_name}")
            logger.info(f"Collected info for repository {repo_name}")
            return response

        except Exception as e:
            logger.error(f"Failed to collect repository info: {str(e)}")
            raise DataCollectionError(f"Failed to collect repository info: {str(e)}")


class BranchCollector:
    """Сборщик данных о ветках."""

    def __init__(self, api_client: IAPIClient) -> None:
        """
        Инициализация сборщика.

        Args:
            api_client: Клиент для работы с API
        """
        self.api_client = api_client

    async def collect_branches(
        self, project_key: str, repo_name: str, limit: int = 100, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Собрать данные о ветках репозитория.

        Args:
            project_key: Ключ проекта
            repo_name: Имя репозитория
            limit: Размер страницы
            cursor: Курсор для пагинации

        Returns:
            Словарь с данными: {"branches": [...], "page_info": {...}}

        Raises:
            DataCollectionError: При ошибке сбора данных
        """
        try:
            logger.info(f"Collecting branches for project {project_key}, repository {repo_name}")

            params: dict[str, Any] = {"limit": limit}
            if cursor:
                params["cursor"] = cursor

            response = await self.api_client.get(
                f"projects/{project_key}/repos/{repo_name}/branches", **params
            )

            branches = response.get("data", [])
            page_info = response.get("page", {})

            logger.info(f"Collected {len(branches)} branches")
            return {"branches": branches, "page_info": page_info}

        except Exception as e:
            logger.error(f"Failed to collect branches: {str(e)}")
            raise DataCollectionError(f"Failed to collect branches: {str(e)}")
