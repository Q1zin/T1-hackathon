"""Калькуляторы метрик (SOLID: Single Responsibility, Open/Closed)."""

from abc import ABC, abstractmethod
from typing import Any

from src.core.exceptions import MetricsCalculationError
from src.core.interfaces import IMetricsCalculator
from src.core.logging import get_logger

logger = get_logger(__name__)


class BaseMetricsCalculator(IMetricsCalculator, ABC):
    """Базовый класс для калькуляторов метрик."""

    @abstractmethod
    async def calculate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Рассчитать метрики."""
        pass


class CommitMetricsCalculator(BaseMetricsCalculator):
    """Калькулятор метрик коммитов."""

    async def calculate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Рассчитать метрики на основе коммитов.

        Args:
            data: Данные о коммитах

        Returns:
            Рассчитанные метрики

        Raises:
            MetricsCalculationError: При ошибке расчета
        """
        try:
            commits = data.get("commits", [])

            if not commits:
                return {
                    "total_commits": 0,
                    "average_commit_size": 0,
                    "total_additions": 0,
                    "total_deletions": 0,
                    "total_files_changed": 0,
                }

            total_commits = len(commits)
            total_additions = sum(c.get("additions", 0) for c in commits)
            total_deletions = sum(c.get("deletions", 0) for c in commits)
            total_files = sum(c.get("files_changed", 0) for c in commits)

            return {
                "total_commits": total_commits,
                "average_commit_size": (total_additions + total_deletions) / total_commits,
                "total_additions": total_additions,
                "total_deletions": total_deletions,
                "total_files_changed": total_files,
                "average_files_per_commit": total_files / total_commits if total_commits else 0,
            }

        except Exception as e:
            logger.error(f"Failed to calculate commit metrics: {str(e)}")
            raise MetricsCalculationError(f"Failed to calculate commit metrics: {str(e)}")


class DeveloperMetricsCalculator(BaseMetricsCalculator):
    """Калькулятор метрик разработчиков."""

    async def calculate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Рассчитать метрики разработчиков.

        Args:
            data: Данные о коммитах разработчиков

        Returns:
            Метрики по разработчикам

        Raises:
            MetricsCalculationError: При ошибке расчета
        """
        try:
            commits = data.get("commits", [])

            # Группировка по авторам
            authors_stats: dict[str, Any] = {}

            for commit in commits:
                author = commit.get("author_email", "unknown")

                if author not in authors_stats:
                    authors_stats[author] = {
                        "name": commit.get("author_name", "Unknown"),
                        "email": author,
                        "commits": 0,
                        "additions": 0,
                        "deletions": 0,
                        "files_changed": 0,
                    }

                authors_stats[author]["commits"] += 1
                authors_stats[author]["additions"] += commit.get("additions", 0)
                authors_stats[author]["deletions"] += commit.get("deletions", 0)
                authors_stats[author]["files_changed"] += commit.get("files_changed", 0)

            # TODO: Добавить расчет продуктивности, качества кода и т.д.

            return {
                "total_developers": len(authors_stats),
                "developers": list(authors_stats.values()),
            }

        except Exception as e:
            logger.error(f"Failed to calculate developer metrics: {str(e)}")
            raise MetricsCalculationError(f"Failed to calculate developer metrics: {str(e)}")


class RepositoryMetricsCalculator(BaseMetricsCalculator):
    """Калькулятор метрик репозиториев."""

    async def calculate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Рассчитать метрики репозитория.

        Args:
            data: Данные о репозитории

        Returns:
            Метрики репозитория

        Raises:
            MetricsCalculationError: При ошибке расчета
        """
        try:
            # TODO: Реализовать расчет:
            # - Частота мержей
            # - Количество активных веток
            # - Горячие точки в коде
            # - Паттерны рефакторинга

            return {
                "active_branches": data.get("branches", []),
                "merge_frequency": 0,  # TODO
                "hotspots": [],  # TODO
            }

        except Exception as e:
            logger.error(f"Failed to calculate repository metrics: {str(e)}")
            raise MetricsCalculationError(
                f"Failed to calculate repository metrics: {str(e)}"
            )


class TimePatternCalculator(BaseMetricsCalculator):
    """Калькулятор временных паттернов активности."""

    async def calculate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Рассчитать временные паттерны.

        Args:
            data: Данные о коммитах с временными метками

        Returns:
            Временные паттерны

        Raises:
            MetricsCalculationError: При ошибке расчета
        """
        try:
            commits = data.get("commits", [])

            # TODO: Реализовать анализ:
            # - Распределение по дням недели
            # - Распределение по часам
            # - Пиковые периоды активности
            # - Нерабочее время

            return {
                "hourly_distribution": {},  # TODO
                "daily_distribution": {},  # TODO
                "peak_hours": [],  # TODO
            }

        except Exception as e:
            logger.error(f"Failed to calculate time patterns: {str(e)}")
            raise MetricsCalculationError(f"Failed to calculate time patterns: {str(e)}")
