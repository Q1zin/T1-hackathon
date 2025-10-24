"""Сервис для персональной аналитики пользователей."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.storage.models import Commit

logger = get_logger(__name__)


class PersonalAnalyticsService:
    """Сервис для работы с персональной аналитикой."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_year_activity(self, author_email: str) -> dict[str, int]:
        """
        Получить активность пользователя за текущий год (количество коммитов в день).

        Args:
            author_email: Email автора коммитов

        Returns:
            Словарь вида {"2024-10-24": 5, "2024-10-25": 3, ...}
        """
        try:
            current_year = datetime.now(timezone.utc).year
            logger.info(f"Getting year activity for {author_email} (year: {current_year})")

            # Получаем дату начала и конца текущего года
            year_start = datetime(current_year, 1, 1, tzinfo=timezone.utc)
            year_end = datetime(current_year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

            # SQL запрос для группировки по дате (без времени)
            # Используем func.date() для извлечения только даты из committed_at
            query = (
                select(
                    func.date(Commit.committed_at).label("commit_date"),
                    func.count(Commit.id).label("commit_count")
                )
                .where(Commit.author_email == author_email)
                .where(Commit.committed_at >= year_start)
                .where(Commit.committed_at <= year_end)
                .group_by(func.date(Commit.committed_at))
                .order_by(func.date(Commit.committed_at))
            )

            result = await self.session.execute(query)
            rows = result.all()

            # Преобразуем результат в словарь {дата: количество}
            activity_data: dict[str, int] = {}
            for row in rows:
                # row.commit_date может быть datetime.date или datetime
                commit_date = row.commit_date
                if isinstance(commit_date, datetime):
                    date_str = commit_date.strftime("%Y-%m-%d")
                else:
                    date_str = commit_date.isoformat()

                activity_data[date_str] = row.commit_count

            logger.info(f"Found {len(activity_data)} active days for {author_email}")
            return activity_data

        except Exception as e:
            logger.error(f"Failed to get year activity for {author_email}: {str(e)}")
            raise
