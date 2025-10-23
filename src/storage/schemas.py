"""Pydantic схемы для валидации и сериализации."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProjectBase(BaseModel):
    """Базовая схема проекта."""

    external_id: str
    name: str
    description: str | None = None
    metadata: dict[str, Any] | None = None


class ProjectCreate(ProjectBase):
    """Схема создания проекта."""

    pass


class ProjectUpdate(BaseModel):
    """Схема обновления проекта."""

    name: str | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None


class ProjectResponse(ProjectBase):
    """Схема ответа проекта."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RepositoryBase(BaseModel):
    """Базовая схема репозитория."""

    external_id: str
    project_id: int
    name: str
    default_branch: str | None = None
    metadata: dict[str, Any] | None = None


class RepositoryCreate(RepositoryBase):
    """Схема создания репозитория."""

    pass


class RepositoryResponse(RepositoryBase):
    """Схема ответа репозитория."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CommitBase(BaseModel):
    """Базовая схема коммита."""

    external_id: str
    repository_id: int
    author_name: str
    author_email: EmailStr
    message: str
    branch: str | None = None
    committed_at: datetime
    additions: int | None = None
    deletions: int | None = None
    total_changes: int | None = None
    files_changed: int | None = None
    metadata: dict[str, Any] | None = None


class CommitCreate(CommitBase):
    """Схема создания коммита."""

    pass


class CommitResponse(CommitBase):
    """Схема ответа коммита."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class MetricBase(BaseModel):
    """Базовая схема метрики."""

    metric_type: str
    entity_type: str
    entity_id: str
    metric_name: str
    value: float
    period_start: datetime
    period_end: datetime
    metadata: dict[str, Any] | None = None


class MetricCreate(MetricBase):
    """Схема создания метрики."""

    pass


class MetricResponse(MetricBase):
    """Схема ответа метрики."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class AnomalyBase(BaseModel):
    """Базовая схема аномалии."""

    entity_type: str
    entity_id: str
    anomaly_type: str
    severity: str = Field(..., pattern="^(low|medium|high)$")
    description: str
    detected_at: datetime
    metadata: dict[str, Any] | None = None


class AnomalyCreate(AnomalyBase):
    """Схема создания аномалии."""

    pass


class AnomalyResponse(AnomalyBase):
    """Схема ответа аномалии."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class RecommendationBase(BaseModel):
    """Базовая схема рекомендации."""

    entity_type: str
    entity_id: str
    category: str
    title: str
    description: str
    priority: str = Field(..., pattern="^(low|medium|high)$")
    impact: str | None = None
    metadata: dict[str, Any] | None = None


class RecommendationCreate(RecommendationBase):
    """Схема создания рекомендации."""

    pass


class RecommendationResponse(RecommendationBase):
    """Схема ответа рекомендации."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
