"""Схемы для аналитических API endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# Персональные метрики
# ============================================================================

class YearActivityResponse(BaseModel):
    """Активность за год (количество коммитов в день)."""
    data: dict[str, int] = Field(
        ...,
        description="Мапа: дата (YYYY-MM-DD) -> количество коммитов",
        examples=[{"2024-01-15": 5, "2024-01-16": 3}]
    )


class LanguageStatsResponse(BaseModel):
    """Статистика по языкам программирования."""
    data: dict[str, float] = Field(
        ...,
        description="Мапа: язык -> процент использования",
        examples=[{"JavaScript": 50.0, "TypeScript": 30.0, "Python": 20.0}]
    )


class PersonalRecommendationsResponse(BaseModel):
    """Личные рекомендации."""
    recommendations: list[str] = Field(
        ...,
        description="Список текстовых рекомендаций",
        examples=[["Попробуйте улучшить качество commit messages", "Рассмотрите возможность рефакторинга кода"]]
    )


class Achievement(BaseModel):
    """Достижение пользователя."""
    img: str = Field(..., description="URL изображения достижения")
    title: str = Field(..., description="Название достижения")


class PersonalAchievementsResponse(BaseModel):
    """Личные достижения."""
    achievements: list[Achievement]


class DiffItem(BaseModel):
    """Один diff из списка."""
    file_name: str = Field(..., description="Имя файла")
    diff: str = Field(..., description="Текст diff")


class DiffsListResponse(BaseModel):
    """Список diff'ов с пагинацией."""
    items: list[DiffItem]
    total: int = Field(..., description="Общее количество diff'ов")
    start: int = Field(..., description="Начальная позиция")
    limit: int = Field(..., description="Лимит на страницу")


class MonthlyStats(BaseModel):
    """Статистика за один месяц."""
    index: int = Field(..., description="Индекс месяца (1-12)")
    count_commits: int = Field(..., description="Количество коммитов")
    count_lines: int = Field(..., description="Количество строк кода")
    kpi: float = Field(..., description="KPI")


class GeneralStatsResponse(BaseModel):
    """Общая статистика по месяцам."""
    year: int
    month: int
    stats: list[MonthlyStats] = Field(
        ...,
        description="Статистика за последние N месяцев"
    )


class SquareStatsResponse(BaseModel):
    """Координаты для визуализации в квадрате."""
    x: float = Field(..., description="Координата X")
    y: float = Field(..., description="Координата Y")


class WeekdayActivity(BaseModel):
    """Активность по дню недели."""
    day: str = Field(..., description="День недели (пн, вт, ср, чт, пт, сб, вс)")
    count: int = Field(..., description="Количество коммитов")


class WeekdayActivityResponse(BaseModel):
    """Активность по дням недели за всё время."""
    data: list[WeekdayActivity]


class WeekdayComparison(BaseModel):
    """Сравнение активности с командой по дню недели."""
    day: str = Field(..., description="День недели (пн, вт, ср, чт, пт, сб, вс)")
    my_count: int = Field(..., description="Личное количество коммитов")
    avg_team: float = Field(..., description="Среднее по команде")


class WeekdayComparisonResponse(BaseModel):
    """Сравнение активности с командой по дням недели."""
    data: list[WeekdayComparison]


class QualityScoreResponse(BaseModel):
    """Коэффициент качества (сообщений или кода)."""
    score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Оценка качества (0-100)"
    )


class MetricGrowthData(BaseModel):
    """Данные роста метрики по месяцам."""
    month: str = Field(..., description="Месяц (YYYY-MM)")
    value: float = Field(..., description="Значение метрики")


class MetricGrowth(BaseModel):
    """Рост одной метрики."""
    metric_name: str = Field(..., description="Название метрики")
    data: list[MetricGrowthData]


class GrowthMetricsResponse(BaseModel):
    """Рост по параметрам по месяцам."""
    metrics: list[MetricGrowth]


# ============================================================================
# Общие метрики команды
# ============================================================================

class DeadZonesResponse(BaseModel):
    """Мертвые зоны (периоды низкой активности)."""
    dead_zones: list[int] = Field(
        ...,
        max_length=10,
        description="Список индексов мертвых зон (топ 10)"
    )


class TeamMemberSquare(BaseModel):
    """Координаты члена команды в квадрате."""
    name: str = Field(..., description="Имя участника")
    img: str | None = Field(None, description="URL аватара")
    x: float
    y: float


class TeamSquareStatsResponse(BaseModel):
    """Статистика команды в квадрате."""
    members: list[TeamMemberSquare]


class MostChangedFile(BaseModel):
    """Информация о часто изменяемом файле."""
    position: int = Field(..., description="Позиция в топе")
    name: str = Field(..., description="Имя файла")
    count_lines: int = Field(..., description="Количество строк")
    count_rewrites: int = Field(..., description="Количество переписываний")


class MostChangedFilesResponse(BaseModel):
    """Топ самых изменяемых файлов."""
    files: list[MostChangedFile] = Field(
        ...,
        max_length=10,
        description="Топ 10 файлов"
    )


class TeamWeekdayActivity(BaseModel):
    """Средняя активность команды по дню недели."""
    day: str = Field(..., description="День недели")
    avg_team: float = Field(..., description="Среднее по команде")


class TeamWeekdayActivityResponse(BaseModel):
    """Средняя активность команды по дням недели."""
    data: list[TeamWeekdayActivity]


class RatingEntry(BaseModel):
    """Запись в рейтинге."""
    name: str = Field(..., description="Имя участника")
    value: float = Field(..., description="Значение метрики")


class KPIRatingResponse(BaseModel):
    """Рейтинг KPI (топ 5)."""
    rating: list[RatingEntry] = Field(
        ...,
        max_length=5,
        description="Топ 5 участников по KPI"
    )


class CommitQualityRatingResponse(BaseModel):
    """Рейтинг качества коммитов (топ 5)."""
    rating: list[RatingEntry] = Field(
        ...,
        max_length=5,
        description="Топ 5 участников по качеству коммитов"
    )


class CodeQualityRatingResponse(BaseModel):
    """Рейтинг качества кода (топ 5)."""
    rating: list[RatingEntry] = Field(
        ...,
        max_length=5,
        description="Топ 5 участников по качеству кода"
    )


class RepositoryLanguagesResponse(BaseModel):
    """Языки программирования репозитория."""
    languages: dict[str, float] = Field(
        ...,
        description="Мапа: язык -> процент",
        examples=[{"JavaScript": 50.0, "TypeScript": 30.0, "Rust": 20.0}]
    )


class Contributor(BaseModel):
    """Информация о контрибьюторе."""
    name: str = Field(..., description="Имя")
    email: EmailStr = Field(..., description="Email")
    img: str | None = Field(None, description="URL аватара")


class ContributorsResponse(BaseModel):
    """Список контрибьюторов."""
    contributors: list[Contributor]


class ContributorImpact(BaseModel):
    """Вклад контрибьютора за период."""
    index: int = Field(..., description="Индекс (порядковый номер)")
    email: EmailStr = Field(..., description="Email контрибьютора")
    impact: float = Field(..., description="Показатель вклада")


class MonthlyContributionResponse(BaseModel):
    """Статистика вклада за месяц."""
    year: int
    month: int
    contributions: list[ContributorImpact] = Field(
        ...,
        max_length=5,
        description="Топ 5 контрибьюторов"
    )
