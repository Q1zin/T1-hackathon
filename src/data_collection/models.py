"""Pydantic модели для данных из T1 Сфера.Код API (согласно Swagger)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# БАЗОВЫЕ МОДЕЛИ
# ============================================================================


class ResponsePageMeta(BaseModel):
    """Метаданные пагинации."""

    next_cursor: str | None = None
    prev_cursor: str | None = None


class ErrorScopeElement(BaseModel):
    """Элемент области ошибки."""

    element: str


class Error(BaseModel):
    """Ошибка API."""

    message: str
    metadata: dict[str, Any] | None = None
    scope: list[ErrorScopeElement] | None = None
    type: str  # internal, auth, bad_input, not_found, already_exists, not_allowed, conflict


class ErrorResponse(BaseModel):
    """Ответ с ошибкой."""

    errors: list[Error]
    request_id: str
    status: str


# ============================================================================
# GIT МОДЕЛИ
# ============================================================================


class GitUser(BaseModel):
    """Git автор/коммитер."""

    name: str
    email: str


class RepoTag(BaseModel):
    """Тег репозитория."""

    name: str
    message: str | None = None
    commit: str  # SHA1


class RepoCommit(BaseModel):
    """Коммит репозитория."""

    hash: str  # SHA1
    message: str
    author: GitUser
    committer: GitUser
    created_at: datetime
    parents: list[str] = Field(default_factory=list)  # SHA1
    tag_names: list[str] = Field(default_factory=list)
    Tags: list[RepoTag] = Field(default_factory=list)  # Deprecated
    branch_names: list[str] = Field(default_factory=list)
    issues: dict[str, str] | None = None


class RepoBranch(BaseModel):
    """Ветка репозитория."""

    name: str
    is_protected: bool
    last_commit: RepoCommit


# ============================================================================
# PROJECT МОДЕЛИ
# ============================================================================


class ProjectPermissions(BaseModel):
    """Права доступа к проекту."""

    can_view_settings: bool = False
    can_edit_settings: bool = False
    can_edit_advanced: bool = False
    can_edit_advanced_settings: bool = False
    can_create_repository: bool = False
    can_import_repository: bool = False
    can_view_quality_gate: bool = False
    can_edit_quality_gate: bool = False
    can_edit_advanced_quality_gate: bool = False
    can_view_quality_plugin: bool = False
    can_edit_quality_plugin: bool = False
    can_edit_advanced_quality_plugin: bool = False
    can_view_roles: bool = False
    can_edit_roles: bool = False
    can_view_teams: bool = False
    can_edit_teams: bool = False


class Project(BaseModel):
    """Проект (согласно Swagger Definition: Project)."""

    id: int
    name: str  # Unique project key (в swagger это Key)
    full_name: str  # Name (в swagger это Name)
    description: str | None = None
    is_public: bool
    is_favorite: bool = False
    lfs_allow: bool = False
    created_at: datetime
    updated_at: datetime
    parent_id: int | None = None
    permissions: ProjectPermissions
    groups: list["Project"] = Field(default_factory=list)  # SubProjects


# ============================================================================
# REPOSITORY МОДЕЛИ
# ============================================================================


class CloneLinks(BaseModel):
    """Ссылки для клонирования репозитория."""

    https: str | None = None
    ssh: str | None = None


class RepoSlug(BaseModel):
    """Идентификатор репозитория."""

    owner: str
    name: str


class RepositoryPermissions(BaseModel):
    """Права доступа к репозиторию."""

    can_view_content: bool = False
    can_edit_content: bool = False
    can_write_advanced: bool = False
    can_create_branch: bool = False
    can_delete_branch: bool = False
    can_view_settings: bool = False
    can_edit_settings: bool = False
    can_edit_advanced_settings: bool = False
    can_edit_pr_settings: bool = False
    can_view_issues: bool = False
    can_edit_issues: bool = False
    can_view_pr: bool = False
    can_create_pr: bool = False


class RepositoryListItem(BaseModel):
    """Элемент списка репозиториев."""

    name: str
    owner_name: str  # Project key
    description: str | None = None
    default_branch: str | None = None
    topics: list[str] = Field(default_factory=list)
    clone_links: CloneLinks
    permissions: RepositoryPermissions
    created_at: datetime
    updated_at: datetime
    is_fork: bool = False
    fork_slug: RepoSlug | None = None


class RepoStructure(BaseModel):
    """Структура репозитория (фильтры веток/путей)."""

    id: int
    name: str
    description: str | None = None
    mask: str  # Regular expression
    is_default: bool = False


class Repository(BaseModel):
    """Полная информация о репозитории."""

    name: str
    owner_name: str  # Project key
    description: str | None = None
    default_branch: str | None = None
    topics: list[str] = Field(default_factory=list)
    clone_links: CloneLinks
    permissions: RepositoryPermissions
    created_at: datetime
    updated_at: datetime
    is_fork: bool = False
    fork_slug: RepoSlug | None = None
    enable_paths_restrictions: bool = False
    repo_structure_paths_include: list[RepoStructure] = Field(default_factory=list)
    repo_structure_paths_exclude: list[RepoStructure] = Field(default_factory=list)


# ============================================================================
# API RESPONSES
# ============================================================================


class ProjectsListResponse(BaseModel):
    """Ответ со списком проектов."""

    data: list[Project]
    page: ResponsePageMeta = Field(default_factory=ResponsePageMeta)
    request_id: str
    status: str


class ProjectResponse(BaseModel):
    """Ответ с одним проектом."""

    data: Project
    page: ResponsePageMeta | None = None
    request_id: str
    status: str


class ListOrgReposResponse(BaseModel):
    """Ответ со списком репозиториев."""

    data: list[RepositoryListItem]
    page: ResponsePageMeta = Field(default_factory=ResponsePageMeta)
    request_id: str
    status: str


class RepoResponse(BaseModel):
    """Ответ с информацией о репозитории."""

    data: Repository
    page: ResponsePageMeta | None = None
    request_id: str
    status: str


class ListRepoBranchesResponse(BaseModel):
    """Ответ со списком веток."""

    data: list[RepoBranch]
    page: ResponsePageMeta = Field(default_factory=ResponsePageMeta)
    request_id: str
    status: str


class ListRepoCommitsResponse(BaseModel):
    """Ответ со списком коммитов."""

    data: list[RepoCommit]
    page: ResponsePageMeta = Field(default_factory=ResponsePageMeta)
    request_id: str
    status: str


class RepoCommitResponse(BaseModel):
    """Ответ с информацией о коммите."""

    data: RepoCommit
    page: ResponsePageMeta | None = None
    request_id: str
    status: str


# ============================================================================
# DIFF МОДЕЛИ
# ============================================================================


class DiffData(BaseModel):
    """
    Данные diff между ревизиями.

    ВАЖНО: Поле 'content' содержит BASE64-encoded строку с полным diff!
    Декодируйте его с помощью base64.b64decode() для получения текста diff.
    """

    source_head_id: str | None = None  # SHA коммита (для commit diff)
    content: str  # BASE64-encoded diff content
    large_files: list[str] = Field(default_factory=list)  # Список больших файлов
    excluded_files: list[str] = Field(default_factory=list)  # Исключенные файлы


class DiffResponse(BaseModel):
    """
    Ответ с diff данными.

    Использование:
        import base64

        response = await get_commit_diff(...)
        diff_text = base64.b64decode(response.data.content).decode('utf-8')
        print(diff_text)
    """

    data: DiffData
    request_id: str
    status: str
