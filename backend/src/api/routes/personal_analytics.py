"""API эндпоинты для персональной аналитики пользователей."""

from fastapi import APIRouter, Depends, Query
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.analytics.personal_analytics_service import PersonalAnalyticsService
from src.core.logging import get_logger
from src.storage.database import get_db
from src.storage.analytics_schemas import (
    Achievement,
    DiffItem,
    DiffsListResponse,
    GeneralStatsResponse,
    GrowthMetricsResponse,
    LanguageStatsResponse,
    MetricGrowth,
    MetricGrowthData,
    MonthlyStats,
    PersonalAchievementsResponse,
    PersonalRecommendationsResponse,
    QualityScoreResponse,
    SquareStatsResponse,
    WeekdayActivity,
    WeekdayActivityResponse,
    WeekdayComparison,
    WeekdayComparisonResponse,
    YearActivityResponse,
)

logger = get_logger(__name__)
router = APIRouter()


@router.get("/year-activity", response_model=YearActivityResponse)
async def get_year_activity(
    email: EmailStr = Query(..., description="Email пользователя"),
    db: AsyncSession = Depends(get_db)
) -> YearActivityResponse:
    """
    Активность за год (количество коммитов в день).

    Args:
        email: Email пользователя
        db: Сессия базы данных

    Returns:
        Мапа: дата -> количество коммитов
    """
    logger.info(f"Getting year activity for {email}")

    service = PersonalAnalyticsService(db)
    activity_data = await service.get_year_activity(email)

    return YearActivityResponse(data=activity_data)


@router.get("/language-stats", response_model=LanguageStatsResponse)
async def get_language_stats(
    email: EmailStr = Query(..., description="Email пользователя")
) -> LanguageStatsResponse:
    """
    Статистика по языкам программирования.

    Args:
        email: Email пользователя

    Returns:
        Мапа: язык -> процент использования
    """
    # TODO: Реализовать логику анализа языков
    logger.info(f"Getting language stats for {email}")

    # Заглушка
    return LanguageStatsResponse(
        data={
            "JavaScript": 50.0,
            "TypeScript": 20.0,
            "Rust": 30.0,
        }
    )


@router.get("/recommendations", response_model=PersonalRecommendationsResponse)
async def get_personal_recommendations(
    email: EmailStr = Query(..., description="Email пользователя")
) -> PersonalRecommendationsResponse:
    """
    Личные рекомендации для улучшения работы.

    Args:
        email: Email пользователя

    Returns:
        Список текстовых рекомендаций
    """
    # TODO: Реализовать логику генерации рекомендаций на основе метрик
    logger.info(f"Getting recommendations for {email}")

    # Заглушка
    return PersonalRecommendationsResponse(
        recommendations=[
            "Улучшите качество commit messages - добавьте больше деталей",
            "Рассмотрите возможность рефакторинга файла main.py",
            "Попробуйте увеличить покрытие тестами - текущее покрытие 45%",
        ]
    )


@router.get("/achievements", response_model=PersonalAchievementsResponse)
async def get_personal_achievements(
    email: EmailStr = Query(..., description="Email пользователя")
) -> PersonalAchievementsResponse:
    """
    Личные достижения пользователя.

    Args:
        email: Email пользователя

    Returns:
        Список достижений с изображениями
    """
    # TODO: Реализовать систему достижений
    logger.info(f"Getting achievements for {email}")

    # Заглушка
    return PersonalAchievementsResponse(
        achievements=[
            Achievement(
                img="https://example.com/badges/100-commits.png",
                title="100 коммитов"
            ),
            Achievement(
                img="https://example.com/badges/code-quality.png",
                title="Мастер качества кода"
            ),
            Achievement(
                img="https://example.com/badges/early-bird.png",
                title="Ранняя пташка"
            ),
        ]
    )


@router.get("/diffs", response_model=DiffsListResponse)
async def get_diffs_list(
    email: EmailStr = Query(..., description="Email пользователя"),
    start: int = Query(default=0, ge=0, description="Начальная позиция"),
    limit: int = Query(default=10, ge=1, le=100, description="Количество элементов"),
) -> DiffsListResponse:
    """
    Список diff'ов пользователя с пагинацией (backlog).

    Args:
        email: Email пользователя
        start: Начальная позиция
        limit: Количество элементов на страницу

    Returns:
        Список diff'ов с пагинацией
    """
    # TODO: Реализовать получение diff'ов из БД
    logger.info(f"Getting diffs for {email} (start={start}, limit={limit})")

    # Заглушка
    return DiffsListResponse(
        items=[
            DiffItem(
                file_name="src/main.py",
                diff="@@ -1,5 +1,6 @@\n def main():\n-    print('Hello')\n+    print('Hello World')\n"
            ),
            DiffItem(
                file_name="src/utils.py",
                diff="@@ -10,3 +10,7 @@\n def helper():\n     pass\n+\n+def new_function():\n+    return True\n"
            ),
        ],
        total=150,
        start=start,
        limit=limit
    )


@router.get("/general-stats", response_model=GeneralStatsResponse)
async def get_general_stats(
    email: EmailStr = Query(..., description="Email пользователя"),
    year: int = Query(..., description="Год"),
    month: int = Query(..., ge=1, le=12, description="Месяц (1-12)"),
) -> GeneralStatsResponse:
    """
    Общая статистика (коммиты, строки, KPI) за последние 5 месяцев.

    Args:
        email: Email пользователя
        year: Год
        month: Месяц (1-12)

    Returns:
        Статистика за 5 месяцев начиная с указанного
    """
    # TODO: Реализовать расчет статистики из БД
    logger.info(f"Getting general stats for {email} ({year}-{month})")

    # Заглушка - 5 месяцев статистики
    return GeneralStatsResponse(
        year=year,
        month=month,
        stats=[
            MonthlyStats(index=1, count_commits=45, count_lines=1200, kpi=8.5),
            MonthlyStats(index=2, count_commits=52, count_lines=1450, kpi=9.1),
            MonthlyStats(index=3, count_commits=38, count_lines=980, kpi=7.8),
            MonthlyStats(index=4, count_commits=61, count_lines=1680, kpi=9.8),
            MonthlyStats(index=5, count_commits=47, count_lines=1320, kpi=8.9),
        ]
    )


@router.get("/square-stats", response_model=SquareStatsResponse)
async def get_square_stats(
    email: EmailStr = Query(..., description="Email пользователя")
) -> SquareStatsResponse:
    """
    Координаты в квадрате для визуализации (статистика в двух измерениях).

    Args:
        email: Email пользователя

    Returns:
        Координаты X и Y для позиционирования
    """
    # TODO: Реализовать расчет координат на основе метрик
    logger.info(f"Getting square stats for {email}")

    # Заглушка
    return SquareStatsResponse(
        x=0.75,
        y=0.62
    )


@router.get("/weekday-activity", response_model=WeekdayActivityResponse)
async def get_weekday_activity(
    email: EmailStr = Query(..., description="Email пользователя")
) -> WeekdayActivityResponse:
    """
    Активность по дням недели (коммиты) за всё время.

    Args:
        email: Email пользователя

    Returns:
        Количество коммитов по дням недели
    """
    # TODO: Реализовать агрегацию по дням недели
    logger.info(f"Getting weekday activity for {email}")

    # Заглушка
    return WeekdayActivityResponse(
        data=[
            WeekdayActivity(day="пн", count=45),
            WeekdayActivity(day="вт", count=52),
            WeekdayActivity(day="ср", count=48),
            WeekdayActivity(day="чт", count=56),
            WeekdayActivity(day="пт", count=38),
            WeekdayActivity(day="сб", count=12),
            WeekdayActivity(day="вс", count=8),
        ]
    )


@router.get("/weekday-comparison", response_model=WeekdayComparisonResponse)
async def get_weekday_comparison(
    email: EmailStr = Query(..., description="Email пользователя")
) -> WeekdayComparisonResponse:
    """
    Сравнение активности с командой по дням недели за всё время.

    Args:
        email: Email пользователя

    Returns:
        Сравнение личной активности со средней по команде
    """
    # TODO: Реализовать расчет среднего по команде и сравнение
    logger.info(f"Getting weekday comparison for {email}")

    # Заглушка
    return WeekdayComparisonResponse(
        data=[
            WeekdayComparison(day="пн", my_count=45, avg_team=38.5),
            WeekdayComparison(day="вт", my_count=52, avg_team=42.3),
            WeekdayComparison(day="ср", my_count=48, avg_team=44.1),
            WeekdayComparison(day="чт", my_count=56, avg_team=41.7),
            WeekdayComparison(day="пт", my_count=38, avg_team=36.2),
            WeekdayComparison(day="сб", my_count=12, avg_team=15.8),
            WeekdayComparison(day="вс", my_count=8, avg_team=11.3),
        ]
    )


@router.get("/commit-quality", response_model=QualityScoreResponse)
async def get_commit_message_quality(
    email: EmailStr = Query(..., description="Email пользователя")
) -> QualityScoreResponse:
    """
    Коэффициент качества сообщений в коммитах (0-100).

    Args:
        email: Email пользователя

    Returns:
        Оценка качества commit messages
    """
    # TODO: Реализовать анализ качества commit messages
    logger.info(f"Getting commit quality for {email}")

    # Заглушка
    return QualityScoreResponse(score=78.5)


@router.get("/code-quality", response_model=QualityScoreResponse)
async def get_code_quality(
    email: EmailStr = Query(..., description="Email пользователя")
) -> QualityScoreResponse:
    """
    Коэффициент качества кода (0-100).

    Args:
        email: Email пользователя

    Returns:
        Оценка качества кода
    """
    # TODO: Реализовать анализ качества кода
    logger.info(f"Getting code quality for {email}")

    # Заглушка
    return QualityScoreResponse(score=85.2)


@router.get("/growth-metrics", response_model=GrowthMetricsResponse)
async def get_growth_metrics(
    email: EmailStr = Query(..., description="Email пользователя")
) -> GrowthMetricsResponse:
    """
    Рост по параметрам (количество коммитов, KPI) по месяцам.

    Args:
        email: Email пользователя

    Returns:
        Динамика метрик по месяцам
    """
    # TODO: Реализовать расчет динамики роста метрик
    logger.info(f"Getting growth metrics for {email}")

    # Заглушка
    return GrowthMetricsResponse(
        metrics=[
            MetricGrowth(
                metric_name="Количество коммитов",
                data=[
                    MetricGrowthData(month="2024-06", value=35.0),
                    MetricGrowthData(month="2024-07", value=42.0),
                    MetricGrowthData(month="2024-08", value=38.0),
                    MetricGrowthData(month="2024-09", value=51.0),
                    MetricGrowthData(month="2024-10", value=47.0),
                ]
            ),
            MetricGrowth(
                metric_name="KPI",
                data=[
                    MetricGrowthData(month="2024-06", value=7.2),
                    MetricGrowthData(month="2024-07", value=8.1),
                    MetricGrowthData(month="2024-08", value=7.8),
                    MetricGrowthData(month="2024-09", value=9.2),
                    MetricGrowthData(month="2024-10", value=8.9),
                ]
            ),
        ]
    )
