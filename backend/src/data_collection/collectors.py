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

    async def collect_all_commits(
        self,
        project_key: str,
        repo_name: str,
        ref_name: str | None = None,
        max_commits: int | None = None,
        after_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Собрать ВСЕ коммиты репозитория с пагинацией.

        Args:
            project_key: Ключ проекта
            repo_name: Имя репозитория
            ref_name: Имя ветки (опционально)
            max_commits: Максимальное количество коммитов (None = все)
            after_date: Фильтр - только коммиты после этой даты (ISO format: "2024-01-01T00:00:00Z")

        Returns:
            Список всех коммитов

        Raises:
            DataCollectionError: При ошибке сбора данных
        """
        try:
            logger.info(
                f"Starting FULL commits collection for {project_key}/{repo_name}, "
                f"ref: {ref_name or 'default'}, after_date: {after_date or 'all time'}"
            )

            all_commits: list[dict[str, Any]] = []
            cursor: str | None = None
            page_num = 1

            # Парсим дату для фильтрации
            from datetime import datetime
            filter_date = None
            if after_date:
                try:
                    from dateutil import parser
                    filter_date = parser.parse(after_date)
                    logger.info(f"Will filter commits after {filter_date}")
                except Exception as e:
                    logger.warning(f"Failed to parse after_date {after_date}: {e}")

            while True:
                # Собираем страницу коммитов
                commits_data = await self.collect_commits(
                    project_key=project_key,
                    repo_name=repo_name,
                    ref_name=ref_name,
                    limit=1000,
                    cursor=cursor
                )

                commits = commits_data["commits"]
                page_info = commits_data["page_info"]

                # Фильтруем по дате если задан фильтр
                if filter_date:
                    filtered_commits = []
                    stop_collection = False

                    for commit in commits:
                        # Получаем дату коммита
                        commit_date_str = commit.get("created_at")
                        if commit_date_str:
                            try:
                                from dateutil import parser
                                commit_date = parser.parse(commit_date_str)

                                # Если коммит старше фильтра - останавливаем сбор
                                if commit_date < filter_date:
                                    stop_collection = True
                                    logger.info(
                                        f"Reached commits older than {after_date}, "
                                        f"stopping collection"
                                    )
                                    break

                                filtered_commits.append(commit)
                            except Exception as e:
                                logger.warning(f"Failed to parse commit date: {e}")
                                filtered_commits.append(commit)
                        else:
                            filtered_commits.append(commit)

                    commits = filtered_commits

                    if stop_collection:
                        all_commits.extend(commits)
                        logger.info(
                            f"Page {page_num}: collected {len(commits)} commits "
                            f"(total: {len(all_commits)}) - STOPPED by date filter"
                        )
                        break

                all_commits.extend(commits)
                logger.info(
                    f"Page {page_num}: collected {len(commits)} commits "
                    f"(total: {len(all_commits)})"
                )

                # Проверяем лимит
                if max_commits and len(all_commits) >= max_commits:
                    all_commits = all_commits[:max_commits]
                    logger.info(f"Reached max_commits limit: {max_commits}")
                    break

                # Проверяем есть ли следующая страница
                next_cursor = page_info.get("next_cursor")
                if not next_cursor:
                    logger.info("No more pages, collection complete")
                    break

                cursor = next_cursor
                page_num += 1

            logger.info(f"FULL collection completed: {len(all_commits)} total commits")
            return all_commits

        except Exception as e:
            logger.error(f"Failed to collect all commits: {str(e)}")
            raise DataCollectionError(f"Failed to collect all commits: {str(e)}")

    async def collect_commit_details(
        self, project_key: str, repo_name: str, commit_sha: str
    ) -> dict[str, Any]:
        """
        Собрать детали коммита.

        Args:
            project_key: Ключ проекта
            repo_name: Имя репозитория
            commit_sha: SHA коммита

        Returns:
            Детали коммита

        Raises:
            DataCollectionError: При ошибке сбора данных
        """
        try:
            logger.info(
                f"Collecting commit details for project {project_key}, "
                f"repository {repo_name}, commit {commit_sha}"
            )

            response = await self.api_client.get(
                f"projects/{project_key}/repos/{repo_name}/commits/{commit_sha}"
            )

            logger.info("Collected commit details")
            return response

        except Exception as e:
            logger.error(f"Failed to collect commit details: {str(e)}")
            raise DataCollectionError(f"Failed to collect commit details: {str(e)}")

    async def collect_commit_diff(
        self, project_key: str, repo_name: str, commit_sha: str, binary: bool = False
    ) -> dict[str, Any]:
        """
        Получить diff коммита (изменения) в base64.

        Args:
            project_key: Ключ проекта
            repo_name: Имя репозитория
            commit_sha: SHA коммита
            binary: Включить бинарные файлы

        Returns:
            Diff коммита с полем content в base64

        Raises:
            DataCollectionError: При ошибке сбора данных
        """
        try:
            logger.info(
                f"Collecting commit diff (base64) for project {project_key}, "
                f"repository {repo_name}, commit {commit_sha}"
            )

            params = {}
            if binary:
                params["binary"] = "true"

            response = await self.api_client.get(
                f"projects/{project_key}/repos/{repo_name}/commits/{commit_sha}/diff",
                **params
            )

            logger.info("Collected commit diff in base64")
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
