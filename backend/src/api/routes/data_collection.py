"""API эндпоинты для сбора данных из Сфера.Код."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from src.core.logging import get_logger
from src.data_collection.api_client import SferaAPIClient
from src.data_collection.collectors import BranchCollector, SferaDataCollector
from src.data_collection.models import (
    DiffResponse,
    ListOrgReposResponse,
    ListRepoBranchesResponse,
    ListRepoCommitsResponse,
    ProjectResponse,
    ProjectsListResponse,
    RepoCommitResponse,
    RepoResponse,
)

logger = get_logger(__name__)
router = APIRouter()


@router.get("/test-auth")
async def test_authentication() -> dict[str, str]:
    """
    Протестировать авторизацию в API Сфера.Код.

    Returns:
        Статус авторизации
    """
    try:
        client = SferaAPIClient()
        # Проверяем Basic Auth, делая простой запрос
        result = await client.get("projects", limit=1)
        return {
            "status": "success",
            "message": "Successfully authenticated with Sfera.Kod API using Basic Auth",
            "api_url": client.base_url,
        }
    except Exception as e:
        logger.error(f"Authentication test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/projects", response_model=ProjectsListResponse)
async def get_projects(
    limit: int = Query(default=10, ge=1, le=100),
    cursor: str | None = Query(default=None),
    sort: str = Query(default="name", pattern="^(name|created_at|updated_at)$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
    q: str | None = Query(default=None),
) -> ProjectsListResponse:
    """
    Получить список проектов из Сфера.Код.

    Args:
        limit: Количество проектов (1-100)
        cursor: Курсор пагинации
        sort: Поле для сортировки (name, created_at, updated_at)
        order: Порядок сортировки (asc, desc)
        q: Фильтр по имени

    Returns:
        Список проектов в формате Swagger
    """
    try:
        client = SferaAPIClient()
        params: dict[str, Any] = {"limit": limit, "sort": sort, "order": order}
        if cursor:
            params["cursor"] = cursor
        if q:
            params["q"] = q

        response = await client.get("projects", **params)
        return ProjectsListResponse(**response)

    except Exception as e:
        logger.error(f"Failed to collect projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to collect projects: {str(e)}")


@router.get("/projects/{project_key}", response_model=ProjectResponse)
async def get_project_info(project_key: str) -> ProjectResponse:
    """
    Получить информацию о проекте.

    Args:
        project_key: Ключ проекта

    Returns:
        Информация о проекте
    """
    try:
        client = SferaAPIClient()
        response = await client.get(f"projects/{project_key}")
        return ProjectResponse(**response)

    except Exception as e:
        logger.error(f"Failed to get project info: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Project not found: {str(e)}")


@router.get("/projects/{project_key}/repos", response_model=ListOrgReposResponse)
async def get_repositories(
    project_key: str,
    limit: int = Query(default=10, ge=1, le=100),
    cursor: str | None = Query(default=None),
    sort: str = Query(default="name", pattern="^(name|created_at|updated_at)$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
    q: str | None = Query(default=None),
) -> ListOrgReposResponse:
    """
    Получить список репозиториев проекта.

    Args:
        project_key: Ключ проекта
        limit: Количество репозиториев (1-100)
        cursor: Курсор пагинации
        sort: Поле сортировки
        order: Порядок сортировки
        q: Фильтр по имени

    Returns:
        Список репозиториев
    """
    try:
        client = SferaAPIClient()
        params: dict[str, Any] = {"limit": limit, "sort": sort, "order": order}
        if cursor:
            params["cursor"] = cursor
        if q:
            params["q"] = q

        response = await client.get(f"projects/{project_key}/repos", **params)
        return ListOrgReposResponse(**response)

    except Exception as e:
        logger.error(f"Failed to collect repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to collect repositories: {str(e)}")


@router.get("/projects/{project_key}/repos/{repo_name}", response_model=RepoResponse)
async def get_repository_info(project_key: str, repo_name: str) -> RepoResponse:
    """
    Получить информацию о репозитории.

    Args:
        project_key: Ключ проекта
        repo_name: Имя репозитория

    Returns:
        Информация о репозитории
    """
    try:
        client = SferaAPIClient()
        response = await client.get(f"projects/{project_key}/repos/{repo_name}")
        return RepoResponse(**response)

    except Exception as e:
        logger.error(f"Failed to get repository info: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Repository not found: {str(e)}")


@router.get(
    "/projects/{project_key}/repos/{repo_name}/branches", response_model=ListRepoBranchesResponse
)
async def get_branches(
    project_key: str,
    repo_name: str,
    limit: int = Query(default=10, ge=1, le=100),
    cursor: str | None = Query(default=None),
    sort: str = Query(default="name", pattern="^(name|committed_at)$"),
    order: str = Query(default="asc", pattern="^(asc|desc)$"),
    q: str | None = Query(default=None),
    merged: bool | None = Query(default=None),
) -> ListRepoBranchesResponse:
    """
    Получить список веток репозитория.

    Args:
        project_key: Ключ проекта
        repo_name: Имя репозитория
        limit: Количество веток (1-100)
        cursor: Курсор пагинации
        sort: Поле сортировки (name, committed_at)
        order: Порядок сортировки
        q: Фильтр по имени
        merged: Только слитые ветки

    Returns:
        Список веток
    """
    try:
        client = SferaAPIClient()
        params: dict[str, Any] = {"limit": limit, "sort": sort, "order": order}
        if cursor:
            params["cursor"] = cursor
        if q:
            params["q"] = q
        if merged is not None:
            params["merged"] = merged

        response = await client.get(f"projects/{project_key}/repos/{repo_name}/branches", **params)
        return ListRepoBranchesResponse(**response)

    except Exception as e:
        logger.error(f"Failed to collect branches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to collect branches: {str(e)}")


@router.get(
    "/projects/{project_key}/repos/{repo_name}/commits", response_model=ListRepoCommitsResponse
)
async def get_commits(
    project_key: str,
    repo_name: str,
    rev: str | None = Query(default=None, description="Git revision (branch/tag/commit)"),
    limit: int = Query(default=10, ge=1, le=100),
    cursor: str | None = Query(default=None),
    author: str | None = Query(default=None),
    committer: str | None = Query(default=None),
    before: str | None = Query(default=None, description="ISO datetime"),
    after: str | None = Query(default=None, description="ISO datetime"),
) -> ListRepoCommitsResponse:
    """
    Получить список коммитов.

    Args:
        project_key: Ключ проекта
        repo_name: Имя репозитория
        rev: Git revision (ветка/тег/коммит)
        limit: Количество коммитов (1-100)
        cursor: Курсор пагинации
        author: Фильтр по автору
        committer: Фильтр по коммитеру
        before: Старше указанной даты
        after: Новее указанной даты

    Returns:
        Список коммитов
    """
    try:
        client = SferaAPIClient()
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if rev:
            params["rev"] = rev
        if author:
            params["author"] = author
        if committer:
            params["committer"] = committer
        if before:
            params["before"] = before
        if after:
            params["after"] = after

        response = await client.get(
            f"projects/{project_key}/repos/{repo_name}/commits", **params
        )
        return ListRepoCommitsResponse(**response)

    except Exception as e:
        logger.error(f"Failed to collect commits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to collect commits: {str(e)}")


@router.get(
    "/projects/{project_key}/repos/{repo_name}/commits/{commit_sha}",
    response_model=RepoCommitResponse,
)
async def get_commit_info(
    project_key: str,
    repo_name: str,
    commit_sha: str,
) -> RepoCommitResponse:
    """
    Получить информацию о коммите.

    Args:
        project_key: Ключ проекта
        repo_name: Имя репозитория
        commit_sha: SHA коммита

    Returns:
        Информация о коммите
    """
    try:
        client = SferaAPIClient()
        response = await client.get(
            f"projects/{project_key}/repos/{repo_name}/commits/{commit_sha}"
        )
        return RepoCommitResponse(**response)

    except Exception as e:
        logger.error(f"Failed to get commit info: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Commit not found: {str(e)}")


@router.get(
    "/projects/{project_key}/repos/{repo_name}/commits/diff",
    response_model=DiffResponse,
)
async def get_commits_diff(
    project_key: str,
    repo_name: str,
    rev: str = Query(..., description="Git revision (from)"),
    until: str | None = Query(default=None, description="Git revision (to)"),
    binary: bool = Query(default=False, description="Include binary file changes"),
    path: str | None = Query(default=None, description="File or directory path"),
) -> DiffResponse:
    """
    Получить diff между двумя ревизиями (commits).

    **ВАЖНО**: response.data.content содержит BASE64-encoded строку!

    Для получения текста diff используйте:
    ```python
    import base64
    diff_text = base64.b64decode(response.data.content).decode('utf-8')
    ```

    Args:
        project_key: Ключ проекта
        repo_name: Имя репозитория
        rev: Git revision (from) - обязательный
        until: Git revision (to) - опционально
        binary: Включить бинарные изменения
        path: Путь к файлу/директории

    Returns:
        Diff между ревизиями (content в base64)
    """
    try:
        client = SferaAPIClient()
        params: dict[str, Any] = {"rev": rev, "binary": binary}
        if until:
            params["until"] = until
        if path:
            params["path"] = path

        response = await client.get(
            f"projects/{project_key}/repos/{repo_name}/commits/diff", **params
        )
        return DiffResponse(**response)

    except Exception as e:
        logger.error(f"Failed to get commits diff: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get commits diff: {str(e)}")


@router.get(
    "/projects/{project_key}/repos/{repo_name}/commits/{commit_sha}/diff",
    response_model=DiffResponse,
)
async def get_commit_diff(
    project_key: str,
    repo_name: str,
    commit_sha: str,
    binary: bool = Query(default=False, description="Include binary file changes"),
) -> DiffResponse:
    """
    Получить diff конкретного коммита.

    **ВАЖНО**: response.data.content содержит BASE64-encoded строку!

    Для получения текста diff используйте:
    ```python
    import base64
    diff_text = base64.b64decode(response.data.content).decode('utf-8')
    ```

    Args:
        project_key: Ключ проекта
        repo_name: Имя репозитория
        commit_sha: SHA коммита
        binary: Включить бинарные изменения

    Returns:
        Diff коммита (content в base64)
    """
    try:
        client = SferaAPIClient()
        params: dict[str, Any] = {"binary": binary}

        response = await client.get(
            f"projects/{project_key}/repos/{repo_name}/commits/{commit_sha}/diff", **params
        )
        return DiffResponse(**response)

    except Exception as e:
        logger.error(f"Failed to get commit diff: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Commit diff not found: {str(e)}")
