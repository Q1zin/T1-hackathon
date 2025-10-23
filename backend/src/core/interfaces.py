"""Интерфейсы и абстрактные базовые классы (SOLID: Dependency Inversion)."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
K = TypeVar("K")


class IRepository(ABC, Generic[T, K]):
    """Интерфейс репозитория для работы с данными."""

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Создать сущность."""
        pass

    @abstractmethod
    async def get(self, id: K) -> T | None:
        """Получить сущность по ID."""
        pass

    @abstractmethod
    async def update(self, id: K, entity: T) -> T | None:
        """Обновить сущность."""
        pass

    @abstractmethod
    async def delete(self, id: K) -> bool:
        """Удалить сущность."""
        pass

    @abstractmethod
    async def list(self, **filters: Any) -> list[T]:
        """Получить список сущностей с фильтрами."""
        pass


class IAPIClient(ABC):
    """Интерфейс клиента для работы с внешним API."""

    @abstractmethod
    async def get(self, endpoint: str, **params: Any) -> dict[str, Any]:
        """GET запрос."""
        pass

    @abstractmethod
    async def post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """POST запрос."""
        pass


class IDataCollector(ABC):
    """Интерфейс сборщика данных из репозиториев."""

    @abstractmethod
    async def collect_projects(self) -> list[dict[str, Any]]:
        """Собрать данные о проектах."""
        pass

    @abstractmethod
    async def collect_repositories(self, project_id: str) -> list[dict[str, Any]]:
        """Собрать данные о репозиториях проекта."""
        pass

    @abstractmethod
    async def collect_commits(
        self, project_id: str, repository_id: str, branch: str = "master"
    ) -> list[dict[str, Any]]:
        """Собрать данные о коммитах."""
        pass

    @abstractmethod
    async def collect_commit_diff(
        self, project_id: str, repository_id: str, commit_id: str
    ) -> dict[str, Any]:
        """Собрать diff коммита."""
        pass


class IMetricsCalculator(ABC):
    """Интерфейс для расчета метрик."""

    @abstractmethod
    async def calculate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Рассчитать метрики на основе данных."""
        pass


class IAnalyzer(ABC):
    """Интерфейс анализатора для выявления трендов и аномалий."""

    @abstractmethod
    async def analyze(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """Провести анализ метрик."""
        pass

    @abstractmethod
    async def detect_anomalies(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Обнаружить аномалии."""
        pass

    @abstractmethod
    async def generate_recommendations(
        self, analysis: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Сгенерировать рекомендации."""
        pass


class ICacheService(ABC):
    """Интерфейс сервиса кеширования."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Получить значение из кеша."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Установить значение в кеш."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Удалить значение из кеша."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Очистить весь кеш."""
        pass
