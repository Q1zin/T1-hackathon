from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    external_id: str
    name: str
    description: str | None = None
    is_public: bool = False
    extra_data: dict[str, Any] | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_public: bool | None = None
    extra_data: dict[str, Any] | None = None


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RepositoryBase(BaseModel):
    external_id: str
    project_id: int
    name: str
    description: str | None = None
    default_branch: str | None = None
    clone_url: str | None = None
    is_fork: bool = False
    last_commit_at: datetime | None = None
    extra_data: dict[str, Any] | None = None


class RepositoryCreate(RepositoryBase):
    pass


class RepositoryResponse(RepositoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CommitBase(BaseModel):
    external_id: str
    repository_id: int
    message: str
    author_name: str
    author_email: str
    committer_name: str
    committer_email: str
    authored_date: datetime
    committed_at: datetime
    diff_base64: str | None = None
    branch_names: list[str] | None = None
    parent_shas: list[str] | None = None
    extra_data: dict[str, Any] | None = None


class CommitCreate(CommitBase):
    pass


class CommitResponse(CommitBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class MetricBase(BaseModel):
    repository_id: int | None = None
    metric_type: str
    metric_name: str
    value: float
    period_start: datetime | None = None
    period_end: datetime | None = None
    extra_data: dict[str, Any] | None = None


class MetricCreate(MetricBase):
    pass


class MetricResponse(MetricBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    calculated_at: datetime


class AnomalyBase(BaseModel):
    metric_id: int | None = None
    repository_id: int | None = None
    anomaly_type: str
    severity: str = Field(..., pattern="^(low|medium|high)$")
    description: str
    value: float | None = None
    threshold: float | None = None
    z_score: float | None = None
    resolved_at: datetime | None = None
    extra_data: dict[str, Any] | None = None


class AnomalyCreate(AnomalyBase):
    pass


class AnomalyResponse(AnomalyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    detected_at: datetime


class RecommendationBase(BaseModel):
    repository_id: int | None = None
    anomaly_id: int | None = None
    recommendation_type: str
    title: str
    description: str
    priority: str = Field(..., pattern="^(low|medium|high)$")
    status: str = "pending"
    extra_data: dict[str, Any] | None = None


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationResponse(RecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    applied_at: datetime | None = None
